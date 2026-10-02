import copy
import hashlib
import re
import time
from collections.abc import Callable
from typing import Any
from urllib.parse import parse_qs, urlparse

from django.contrib.admin import AdminSite
from django.core.cache import cache
from django.core.paginator import Paginator
from django.core.validators import EMPTY_VALUES
from django.http import HttpRequest, HttpResponse
from django.template.response import TemplateResponse
from django.urls import URLPattern, URLResolver, path, reverse, reverse_lazy
from django.utils.encoding import force_bytes
from django.utils.functional import lazy
from django.utils.module_loading import import_string

from backstage import branding
from backstage.conf import get_sidebar_group_collapse
from backstage.dataclasses import DropdownItem, Favicon, SearchResult
from backstage.registry.navigation import get_backstage_sidebar
from backstage.settings import get_config

_BRANDING_KEYS = frozenset(
    {
        "SITE_TITLE",
        "SITE_HEADER",
        "SITE_SUBHEADER",
        "SITE_URL",
        "SITE_LOGO",
        "SITE_FAVICONS",
        "SITE_DROPDOWN",
    }
)


class BackstageAdminSite(AdminSite):
    default_site = "backstage.sites.BackstageAdminSite"
    settings_name = "BACKSTAGE"

    def __init__(self, name: str = "admin") -> None:
        from backstage.forms import AuthenticationForm

        super().__init__(name)

        custom_login_form = get_config(self.settings_name)["LOGIN"]["form"]

        if custom_login_form is not None:
            self.login_form = import_string(custom_login_form)
        elif self.login_form is None:
            self.login_form = AuthenticationForm

    def get_urls(self) -> list[URLResolver | URLPattern]:
        return (
            [
                path("search/", self.admin_view(self.search), name="search"),
            ]
            + self._get_extra_urls()
            + super().get_urls()
        )

    def each_context(self, request: HttpRequest) -> dict[str, Any]:
        context = super().each_context(request)

        sidebar_config = self._get_config("SIDEBAR", request)
        data = {
            "form_classes": self._get_config("FORMS", request).get("classes"),
            "site_title": self._get_config("SITE_TITLE", request),
            "site_header": self._get_config("SITE_HEADER", request),
            "site_subheader": self._get_config("SITE_SUBHEADER", request),
            "site_version": self._get_config("SITE_VERSION", request),
            "site_url": self._get_config("SITE_URL", request),
            "site_dropdown": self._get_site_dropdown_items("SITE_DROPDOWN", request),
            "site_logo": self._get_theme_images("SITE_LOGO", request),
            "site_icon": self._get_theme_images("SITE_ICON", request),
            "site_symbol": self._get_config("SITE_SYMBOL", request),
            "site_favicons": self._get_favicons("SITE_FAVICONS", request),
            "login_image": self._get_value(get_config(self.settings_name)["LOGIN"].get("image"), request),
            "show_history": self._get_config("SHOW_HISTORY", request),
            "show_view_on_site": self._get_config("SHOW_VIEW_ON_SITE", request),
            "show_languages": self._get_config("SHOW_LANGUAGES", request),
            "language_flags": self._get_config("LANGUAGE_FLAGS", request),
            "show_back_button": self._get_config("SHOW_BACK_BUTTON", request),
            "theme": self._get_config("THEME", request),
            "environment": self._get_config("ENVIRONMENT", request),
            "environment_title_prefix": self._get_config("ENVIRONMENT_TITLE_PREFIX", request),
            "languages_list": self._get_value(self._get_config("LANGUAGES", request).get("navigation"), request),
            "languages_action": self._get_value(self._get_config("LANGUAGES", request).get("action"), request),
            "account_links": self._get_account_links(request),
            "tab_list": self.get_tabs_list(request),
            "styles": self._get_list("STYLES", request),
            "scripts": self._get_list("SCRIPTS", request),
            "command_show_history": self._get_config("COMMAND", request).get("show_history"),
            "sidebar_show_all_applications": self._get_value(sidebar_config.get("show_all_applications"), request),
            "sidebar_show_search": self._get_value(sidebar_config.get("show_search"), request),
            "sidebar_navigation": self.get_sidebar_list(request) if self.has_permission(request) else [],
            "sidebar_group_collapse": get_sidebar_group_collapse(),
            "appearance_classes": branding.resolve_appearance_classes(),
        }

        context.update(data)

        global_callback = get_config(self.settings_name)["GLOBAL_CALLBACK"]

        if isinstance(global_callback, str):
            global_context = import_string(global_callback)(request)

            if isinstance(global_context, dict):
                context.update(global_context)

        if hasattr(self, "extra_context") and callable(self.extra_context):
            return self.extra_context(context, request)

        return context

    def index(self, request: HttpRequest, extra_context: dict[str, Any] | None = None) -> TemplateResponse:
        app_list = self.get_app_list(request)

        context = {
            **self.each_context(request),
            "title": self.index_title,
            "subtitle": None,
            "app_list": app_list,
            "index": True,
            **(extra_context or {}),
        }

        dashboard_callback = get_config(self.settings_name)["DASHBOARD_CALLBACK"]
        dashboard_config = get_config(self.settings_name).get("DASHBOARD") or {}
        dashboard_enabled = dashboard_config.get("enabled", True)

        if dashboard_enabled:
            from backstage.dashboard import build_dashboard_context

            context = build_dashboard_context(request, self, context)

        if isinstance(dashboard_callback, str):
            context = import_string(dashboard_callback)(request, context)

        request.current_app = self.name

        if dashboard_enabled:
            template_name = get_config(self.settings_name).get("DASHBOARD_TEMPLATE") or (
                "backstage/dashboard/index.html"
            )
        else:
            template_name = self.index_template or "admin/index.html"

        return TemplateResponse(request, template_name, context)

    def _search_apps(self, app_list: list[dict[str, Any]], search_term: str) -> list[SearchResult]:
        results = []
        apps = []

        for app in app_list:
            if search_term in app["name"].lower():
                apps.append(app)
                continue

            models = []

            for model in app["models"]:
                if search_term in model["name"].lower():
                    models.append(model)

            if len(models) > 0:
                app["models"] = models
                apps.append(app)

        for app in apps:
            for model in app["models"]:
                results.append(
                    SearchResult(
                        title=str(model["name"]),
                        description=app["name"],
                        link=model["admin_url"],
                        icon="tag",
                    )
                )

        return results

    def _search_models(
        self,
        request: HttpRequest,
        app_list: list[dict[str, Any]],
        search_term: str,
        allowed_models: list[str] | None = None,
    ) -> list[SearchResult]:
        results = []

        for app in app_list:
            for model in app["models"]:
                # Skip models which are not allowed
                if isinstance(allowed_models, list | tuple):
                    if model["model"]._meta.label.lower() not in [m.lower() for m in allowed_models]:
                        continue

                admin_instance = self._registry.get(model["model"])
                search_fields = admin_instance.get_search_fields(request)

                if not search_fields:
                    continue

                pks = []

                qs = admin_instance.get_queryset(request)
                search_results, _has_duplicates = admin_instance.get_search_results(request, qs, search_term)

                for item in search_results:
                    if item.pk in pks:
                        continue

                    pks.append(item.pk)

                    link = reverse_lazy(
                        f"{self.name}:{admin_instance.model._meta.app_label}_{admin_instance.model._meta.model_name}_change",
                        args=(item.pk,),
                    )

                    results.append(
                        SearchResult(
                            title=str(item),
                            description=f"{item._meta.app_label.capitalize()} - {item._meta.verbose_name.capitalize()}",
                            link=link,
                            icon="data_object",
                        )
                    )

        return results

    def search(
        self, request: HttpRequest, extra_context: dict[str, Any] | None = None
    ) -> TemplateResponse | HttpResponse:
        start_time = time.time()

        CACHE_TIMEOUT = 5 * 60
        PER_PAGE = 100

        search_term = request.GET.get("s")
        app_list = super().get_app_list(request)

        if search_term in EMPTY_VALUES:
            return HttpResponse()

        search_term = search_term.lower()

        search_key_base = f"{request.user.pk}_{search_term}"
        cache_key = f"backstage_search_{hashlib.sha256(force_bytes(search_key_base)).hexdigest()}"
        cache_results = cache.get(cache_key)

        if cache_results:
            results = cache_results
        else:
            results = self._search_apps(app_list, search_term)

            if search_callback := self._get_config("COMMAND", request).get("search_callback"):
                results.extend(self._get_value(search_callback, request, search_term))

            search_models = self._get_value(self._get_config("COMMAND", request).get("search_models"), request)

            if search_models is True or isinstance(search_models, list | tuple):
                allowed_models = search_models if isinstance(search_models, list | tuple) else None

                results.extend(self._search_models(request, app_list, search_term, allowed_models))

            cache.set(cache_key, results, timeout=CACHE_TIMEOUT)

        execution_time = time.time() - start_time
        paginator = Paginator(results, PER_PAGE)

        show_history = self._get_value(self._get_config("COMMAND", request).get("show_history"), request)

        return TemplateResponse(
            request,
            template="backstage/helpers/command_results.html",
            context={
                "search_term": search_term,
                "page_obj": paginator,
                "results": paginator.page(request.GET.get("page", 1)),
                "page_counter": (int(request.GET.get("page", 1)) - 1) * PER_PAGE,
                "execution_time": execution_time,
                "command_show_history": show_history,
            },
            headers={
                "HX-Trigger": "search",
            },
        )

    def password_change(self, request: HttpRequest, extra_context: dict[str, Any] | None = None) -> TemplateResponse:
        from django.contrib.auth.views import PasswordChangeView

        from backstage.forms import AdminOwnPasswordChangeForm

        url = reverse(f"{self.name}:password_change_done", current_app=self.name)
        defaults = {
            "form_class": AdminOwnPasswordChangeForm,
            "success_url": url,
            "extra_context": {**self.each_context(request), **(extra_context or {})},
        }
        if self.password_change_template is not None:
            defaults["template_name"] = self.password_change_template
        request.current_app = self.name
        return PasswordChangeView.as_view(**defaults)(request)

    def get_sidebar_list(self, request: HttpRequest) -> list[dict[str, Any]]:
        navigation = self._get_value(self._get_config("SIDEBAR", request).get("navigation"), request)
        tabs = self._get_value(self._get_config("TABS", request), request) or []
        results = []

        for group in copy.deepcopy(navigation):
            if not group.get("id"):
                group["id"] = self._slugify_nav_group_id(group.get("title", "group"))

            group["items"] = self._get_navigation_items(request, group["items"], tabs)

            # Badge callbacks
            if "badge" in group and isinstance(group["badge"], str):
                try:
                    callback = import_string(group["badge"])
                    group["badge_callback"] = lazy(callback)(request)
                except (ImportError, ValueError):
                    pass

            results.append(group)

        self._resolve_exclusive_active_items(results)

        return results

    @staticmethod
    def _normalize_admin_path(path: str) -> str:
        normalized = urlparse(str(path)).path or "/"
        if not normalized.endswith("/"):
            normalized = f"{normalized}/"
        return normalized

    def _admin_path_matches(
        self,
        request_path: str,
        link_path: str,
        *,
        is_tab: bool = False,
        link_query: str = "",
    ) -> bool:
        request_path = self._normalize_admin_path(request_path)
        link_path = self._normalize_admin_path(link_path)
        index_path = self._normalize_admin_path(reverse(f"{self.name}:index"))

        if link_path == index_path:
            return request_path == index_path

        if request_path == link_path or request_path.startswith(link_path):
            if is_tab and link_query:
                query_params = parse_qs(link_query)
                request_params = parse_qs(request.GET.urlencode())
                if not all(request_params.get(k) == v for k, v in query_params.items()):
                    return False
            return True

        return False

    def _resolve_exclusive_active_items(self, groups: list[dict[str, Any]]) -> None:
        candidates: list[tuple[int, dict[str, Any]]] = []

        for group in groups:
            for item in group.get("items", []):
                if not item.get("active"):
                    continue
                link = str(item.get("link_callback") or item.get("link", ""))
                link_path = self._normalize_admin_path(urlparse(link).path)
                candidates.append((len(link_path), item))

        if len(candidates) <= 1:
            return

        longest = max(length for length, _ in candidates)
        for group in groups:
            for item in group.get("items", []):
                if not item.get("active"):
                    continue
                link = str(item.get("link_callback") or item.get("link", ""))
                link_path = self._normalize_admin_path(urlparse(link).path)
                if len(link_path) != longest:
                    item["active"] = False

    @staticmethod
    def _slugify_nav_group_id(title: str) -> str:
        slug = re.sub(r"[^a-z0-9]+", "-", str(title).lower()).strip("-")
        return slug or "group"

    def _get_navigation_items(self, request: HttpRequest, items: list[dict], tabs: list[dict] | None = None) -> list:
        allowed_items = []

        for item in items:
            link = item.get("link")

            if not link:
                continue

            if "active" in item:
                item["active"] = self._get_value(item["active"], request)
            else:
                item["active"] = self._get_is_active(request, item.get("link_callback") or link)

            # Checks if any tab item is active and then marks the sidebar link as active
            if tabs and self._get_is_tab_active(request, tabs, link):
                item["active"] = True

            # Link callback
            if isinstance(link, Callable):
                item["link_callback"] = lazy(link)(request)

            # Permission callback
            item["has_permission"] = self._call_permission_callback(item.get("permission"), request)

            # Badge callbacks
            if "badge" in item and isinstance(item["badge"], str):
                try:
                    callback = import_string(item["badge"])
                    item["badge_callback"] = lazy(callback)(request)
                except (ImportError, ValueError):
                    pass

            # Process nested items
            if "items" in item:
                item["items"] = self._get_navigation_items(request, item["items"])

            allowed_items.append(item)

        return allowed_items

    def _get_account_links(self, request: HttpRequest) -> list[dict[str, Any]]:
        links = []

        navigation = self._get_value(get_config(self.settings_name)["ACCOUNT"].get("navigation"), request)

        for item in navigation:
            links.append(
                {
                    "title": self._get_value(item["title"], request),
                    "link": self._get_value(item["link"], request),
                }
            )

        return links

    def get_tabs_list(self, request: HttpRequest) -> list[dict[str, Any]]:
        tabs = copy.deepcopy(self._get_config("TABS", request))

        if not tabs:
            return []

        for tab in tabs:
            allowed_items = []

            for item in tab["items"]:
                item["has_permission"] = self._call_permission_callback(item.get("permission"), request)

                if isinstance(item["link"], Callable):
                    item["link_callback"] = lazy(item["link"])(request)

                if "active" not in item:
                    item["active"] = self._get_is_active(request, item.get("link_callback") or item["link"], True)
                else:
                    item["active"] = self._get_value(item["active"], request)

                allowed_items.append(item)

            tab["items"] = allowed_items

        return tabs

    def _call_permission_callback(self, callback: str | Callable | None, request: HttpRequest) -> bool:
        if callback is None:
            return True

        if isinstance(callback, str):
            try:
                callback = import_string(callback)
            except (ImportError, ValueError):
                pass

        if isinstance(callback, str) or isinstance(callback, Callable):
            # We are not able to use here "is" because type is lazy loaded function
            if lazy(callback)(request) == True:  # noqa: E712
                return True

        return False

    def _replace_values(self, target: dict, source: dict, request: HttpRequest):
        for key, value in source.items():
            if value is not None and callable(value):
                target[key] = value(request)
            else:
                target[key] = value

        return target

    def _get_is_active(self, request: HttpRequest, link: str | Callable, is_tab: bool = False) -> bool:
        if not isinstance(link, str):
            link = str(link)

        parsed = urlparse(link)
        return self._admin_path_matches(
            request.path,
            parsed.path,
            is_tab=is_tab,
            link_query=parsed.query,
        )

    def _get_is_tab_active(self, request: HttpRequest, tabs: list[dict], nav_link: str) -> bool:
        for tab_opts in tabs:
            has_primary_link = False
            has_tab_link_active = False

            for tab_item in tab_opts["items"]:
                if nav_link == tab_item["link"]:
                    has_primary_link = True
                    continue

                if self._get_is_active(request, tab_item.get("link_callback") or tab_item["link"]):
                    has_tab_link_active = True
                    continue

            if has_primary_link and has_tab_link_active:
                return True

        return False

    def _resolve_branding(self, key: str, request: HttpRequest | None) -> Any:
        if key == "SITE_TITLE":
            return branding.resolve_text("site_title", "SITE_TITLE")
        if key == "SITE_HEADER":
            return branding.resolve_sidebar_text("site_header", "SITE_HEADER")
        if key == "SITE_SUBHEADER":
            return branding.resolve_sidebar_text("site_subheader", "SITE_SUBHEADER")
        if key == "SITE_URL":
            return branding.resolve_site_url()
        if key == "SITE_LOGO":
            return branding.resolve_logo()
        if key == "SITE_FAVICONS":
            return branding.resolve_favicons()
        if key == "SITE_DROPDOWN":
            return branding.resolve_site_dropdown(request)
        return None

    def _get_config(self, key: str, *args: Any) -> Any:
        config = get_config(self.settings_name)
        request = args[0] if args else None

        if key in _BRANDING_KEYS:
            return self._resolve_branding(key, request)

        if key == "SIDEBAR":
            sidebar = config.get(key) or {}
            if not sidebar.get("navigation"):
                return get_backstage_sidebar(request) if request else {}
            return self._get_value(sidebar, *args)

        if key in config and config[key]:
            return self._get_value(config[key], *args)

    def _get_theme_images(self, key: str, *args: Any) -> dict[str, str] | str | None:
        images = self._get_config(key, *args)

        if isinstance(images, dict):
            if "light" in images and "dark" in images:
                return {
                    "light": self._get_value(images["light"], *args),
                    "dark": self._get_value(images["dark"], *args),
                }

            return None

        return images

    def _get_list(self, key: str, *args: Any) -> list[Any]:
        config = get_config(self.settings_name)
        request = args[0] if args else None

        if key == "STYLES" and not config.get(key):
            return branding.resolve_default_styles(request) if request else []

        items = config.get(key)
        if isinstance(items, list):
            return [self._get_value(item, *args) for item in items]

        return []

    def _get_favicons(self, key: str, *args: Any) -> list[Favicon]:
        favicons = self._get_config(key, *args)

        if not favicons:
            return []

        return [
            Favicon(
                href=self._get_value(item["href"], *args),
                rel=item.get("rel"),
                sizes=item.get("sizes"),
                type=item.get("type"),
            )
            for item in favicons
        ]

    def _get_site_dropdown_items(self, key: str, *args: Any) -> list[DropdownItem]:
        items = self._get_config(key, *args)

        if not items:
            return []

        return [
            DropdownItem(
                title=item.get("title"),
                link=self._get_value(item["link"], *args),
                icon=item.get("icon"),
                attrs=item.get("attrs"),
            )
            for item in items
        ]

    def _get_value(self, value: str | Callable | None, *args: Any) -> Any:
        if value is None:
            return None

        if isinstance(value, str):
            try:
                callback = import_string(value)
                return callback(*args)
            except (ImportError, ValueError):
                pass

            return value

        if isinstance(value, Callable):
            return value(*args)

        return value

    def _get_extra_urls(self) -> list[URLResolver | URLPattern]:
        extra_urls: list[URLResolver | URLPattern] = []

        if hasattr(self, "extra_urls") and callable(self.extra_urls):
            extra_urls = self.extra_urls()

        site_views = self._get_config("SITE_VIEWS")

        if site_views is None:
            return extra_urls

        for url_conf in site_views:
            url, name, path_to_view = url_conf

            if not isinstance(path_to_view, str):
                continue

            view = import_string(path_to_view).as_view(admin_site=self)

            extra_urls.append(
                path(
                    url,
                    self.admin_view(view),
                    name=name,
                )
            )

        return extra_urls
