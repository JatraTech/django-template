from __future__ import annotations

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from django.urls import NoReverseMatch, reverse
from django.utils.translation import gettext

from backstage.branding import resolve_site_url
from backstage.settings import get_config


class Command(BaseCommand):
    help = "Verify Backstage is wired correctly in the host project."

    def handle(self, *args, **options):
        errors: list[str] = []
        warnings: list[str] = []

        installed = list(settings.INSTALLED_APPS)
        if not installed or installed[0] != "backstage":
            errors.append(
                '"backstage" must be the first entry in INSTALLED_APPS '
                f"(currently first: {installed[0] if installed else 'none'})."
            )

        if "django.contrib.admin" in installed:
            admin_index = installed.index("django.contrib.admin")
            backstage_index = installed.index("backstage")
            if admin_index < backstage_index:
                errors.append('"django.contrib.admin" must be listed after "backstage".')

        if not hasattr(settings, "BACKSTAGE"):
            errors.append("settings.BACKSTAGE dict is missing.")
        else:
            get_config()  # merge sanity check

        try:
            reverse("backstage-theme-css")
        except NoReverseMatch:
            warnings.append(
                'URL name "backstage-theme-css" not found — include path("backstage/", include("backstage.urls")).'
            )

        if not self._backstage_migrations_applied():
            errors.append('Run "python manage.py migrate backstage" — backstage tables missing.')

        config = get_config()
        callback_path = config.get("PREVIEW_ROUTE_CALLBACK")
        if callback_path:
            from django.utils.module_loading import import_string

            try:
                import_string(callback_path)
            except Exception as exc:
                warnings.append(f"PREVIEW_ROUTE_CALLBACK cannot be imported ({callback_path}): {exc}")
            site_url = resolve_site_url()
            if not site_url or site_url in {"/", ""}:
                warnings.append(
                    "PREVIEW_ROUTE_CALLBACK is set but public site URL looks empty — "
                    "set FRONTEND_URL, BACKSTAGE['SITE_URL'], or Admin appearance → frontend URL."
                )

        warnings.extend(self._duplicate_field_editor_meta_warnings())
        warnings.extend(self._draft_publish_config_warnings())
        warnings.extend(self._admin_theme_css_warnings())
        warnings.extend(self._hide_title_warnings())
        warnings.extend(self._dashboard_config_warnings())
        warnings.extend(self._host_package_import_warnings())
        warnings.extend(self._inline_hub_config_warnings())
        warnings.extend(self._inline_relations_config_warnings())

        for message in warnings:
            self.stdout.write(self.style.WARNING(f"Warning: {message}"))

        if errors:
            for message in errors:
                self.stderr.write(self.style.ERROR(message))
            raise CommandError(f"Backstage integration check failed ({len(errors)} error(s)).")

        self.stdout.write(self.style.SUCCESS("Backstage integration check passed."))

    def _backstage_migrations_applied(self) -> bool:
        table_names = connection.introspection.table_names()
        # BackstageSettings model table from initial migration
        expected = "backstage_backstagesettings"
        return expected in table_names

    def _duplicate_field_editor_meta_warnings(self) -> list[str]:
        from django.apps import apps

        meta = get_config().get("FIELD_EDITOR_META") or {}
        warnings: list[str] = []
        max_show = 10

        def norm(value: object) -> str:
            if value is None:
                return ""
            return str(gettext(value)).strip()

        for model_key, fields in meta.items():
            if not isinstance(fields, dict):
                continue
            model = None
            key_lower = str(model_key).lower()
            for app_config in apps.get_app_configs():
                for candidate in app_config.get_models():
                    if candidate.__name__.lower() == key_lower:
                        model = candidate
                        break
                if model is not None:
                    break
            if model is None:
                continue
            for field_name, field_meta in fields.items():
                if not isinstance(field_meta, dict):
                    continue
                try:
                    db_field = model._meta.get_field(field_name)
                except Exception:
                    continue
                meta_help = field_meta.get("help_text")
                if meta_help is not None:
                    model_help = getattr(db_field, "help_text", None) or ""
                    if norm(meta_help) == norm(model_help) and norm(model_help):
                        warnings.append(
                            f"Duplicate FIELD_EDITOR_META help_text for "
                            f"{model._meta.label_lower}.{field_name} "
                            f"(matches model field — remove from host meta)."
                        )
                meta_label = field_meta.get("label")
                if meta_label is not None:
                    verbose = getattr(db_field, "verbose_name", None)
                    if norm(meta_label) == norm(verbose):
                        warnings.append(
                            f"Duplicate FIELD_EDITOR_META label for "
                            f"{model._meta.label_lower}.{field_name} "
                            f"(matches model verbose_name — remove from host meta)."
                        )

        if len(warnings) > max_show:
            extra = len(warnings) - max_show
            return warnings[:max_show] + [f"... and {extra} more duplicate meta warning(s)."]
        return warnings

    def _draft_publish_config_warnings(self) -> list[str]:
        from django.apps import apps

        from backstage.draft.conf import is_draft_publish_enabled
        from backstage.preview.routes import resolve_preview_route

        if not is_draft_publish_enabled():
            return []

        config = get_config().get("DRAFT_PUBLISH") or {}
        warnings: list[str] = []
        for key in config.get("models") or []:
            if "." not in key:
                warnings.append(f"DRAFT_PUBLISH model key {key!r} should be app_label.modelname.")
                continue
            app_label, model_name = key.split(".", 1)
            try:
                model = apps.get_model(app_label, model_name)
            except LookupError:
                warnings.append(f"DRAFT_PUBLISH lists unknown model {key!r}.")
                continue
            if not hasattr(model, "live_version"):
                warnings.append(
                    f"DRAFT_PUBLISH model {key} has no live_version field — "
                    f"add DraftPublishDuplicateRowMixin (or snapshot mixin)."
                )
            from backstage.draft.conf import resolve_draft_copy_field_names

            if not resolve_draft_copy_field_names(model):
                warnings.append(
                    f"DRAFT_PUBLISH model {key} has no copy fields — "
                    f"set DRAFT_PUBLISH['copy_fields']['{key}'] or "
                    f"draft_copy_field_names() on the model."
                )
            try:
                sample = model()
                if hasattr(sample, "slug") and not getattr(sample, "slug", None):
                    sample.slug = "preview-route-check"
                if resolve_preview_route(sample) is None:
                    warnings.append(
                        f"DRAFT_PUBLISH model {key} has no preview route — add mapping in resolve_preview_route."
                    )
            except Exception as exc:
                warnings.append(f"DRAFT_PUBLISH preview route check failed for {key}: {exc}")
        return warnings

    def _admin_theme_css_warnings(self) -> list[str]:
        from pathlib import Path

        import backstage

        package_root = Path(backstage.__file__).resolve().parent
        css_path = package_root / "static" / "backstage" / "admin-theme.css"
        warnings: list[str] = []
        if not css_path.is_file():
            warnings.append(f"Missing admin theme CSS at {css_path.relative_to(package_root)}.")
            return warnings
        css = css_path.read_text()
        required_tokens = (
            "--backstage-control-min-height",
            "--backstage-table-cell-padding-x",
            "--backstage-table-cell-padding-y",
            "--backstage-border",
            "--backstage-row-action-size",
        )
        missing = [token for token in required_tokens if token not in css]
        if missing:
            warnings.append("admin-theme.css is missing expected design tokens: " + ", ".join(missing) + ".")
        try:
            reverse("backstage-theme-css")
        except NoReverseMatch:
            pass  # handled in handle()
        return warnings

    def _hide_title_warnings(self) -> list[str]:
        warnings: list[str] = []
        overrides = get_config().get("ADMIN_OVERRIDES") or {}

        def walk(obj: object, path: str) -> None:
            if isinstance(obj, dict):
                if "hide_title" in obj:
                    warnings.append(
                        f"Deprecated hide_title in BACKSTAGE ADMIN_OVERRIDES at {path} — use show_title instead."
                    )
                for key, value in obj.items():
                    walk(value, f"{path}.{key}" if path else str(key))

        walk(overrides, "ADMIN_OVERRIDES")
        warnings.extend(self._scan_host_modules_for_hide_title())
        return warnings

    def _scan_host_modules_for_hide_title(self) -> list[str]:
        from importlib import import_module
        from pathlib import Path

        warnings: list[str] = []
        for dotted in self._guess_host_backstage_modules():
            try:
                mod = import_module(dotted)
            except Exception:
                continue
            mod_path = getattr(mod, "__file__", None)
            if not mod_path:
                continue
            source = Path(mod_path).read_text()
            if "hide_title" not in source:
                continue
            if any("hide_title" in w for w in warnings):
                continue
            warnings.append(f"Host module {dotted} references deprecated hide_title — use show_title on ModelAdmin.")
        return warnings

    def _guess_host_backstage_modules(self) -> list[str]:
        from pathlib import Path

        candidates: list[str] = []
        settings_module = getattr(settings, "SETTINGS_MODULE", "")
        if settings_module:
            app_label = settings_module.split(".", 1)[0]
            candidates.append(f"{app_label}.backstage_host")
        for path in Path(settings.BASE_DIR).glob("**/backstage_host.py"):
            rel = path.relative_to(settings.BASE_DIR)
            if rel.parts[0] == "backstage":
                continue
            module = ".".join(rel.with_suffix("").parts)
            if module not in candidates:
                candidates.append(module)
        return candidates

    def _inline_hub_config_warnings(self) -> list[str]:
        from django.contrib import admin

        configured = get_config().get("INLINE_HUB") or {}
        if not configured:
            return []

        def model_by_name(name: str):
            for model in admin.site._registry:
                if model.__name__ == name:
                    return model
            return None

        standalone = {str(n).split(".")[-1] for n in (get_config().get("STANDALONE_CHILD_MODELS") or [])}
        warnings: list[str] = []

        for parent_name, children in configured.items():
            parent = model_by_name(str(parent_name))
            if parent is None:
                warnings.append(f'INLINE_HUB: unknown parent model "{parent_name}" (not registered on admin site).')
                continue
            if not isinstance(children, dict):
                continue
            for child_name in children:
                child = model_by_name(str(child_name))
                if child is None:
                    warnings.append(
                        f'INLINE_HUB: unknown child model "{child_name}" under "{parent_name}".',
                    )
                    continue
                if child.__name__ not in standalone:
                    warnings.append(
                        f'INLINE_HUB: "{parent_name}" → "{child_name}" — add "{child.__name__}" to '
                        "STANDALONE_CHILD_MODELS if the child should have its own changelist outside the hub.",
                    )
        return warnings

    def _inline_relations_config_warnings(self) -> list[str]:
        from backstage.registry.relations import validate_relation_entry

        warnings: list[str] = []
        relations = get_config().get("INLINE_RELATIONS") or []
        inline_hub = get_config().get("INLINE_HUB") or {}
        relation_keys = set()
        for entry in relations:
            if not isinstance(entry, dict):
                warnings.append("INLINE_RELATIONS: entry must be a dict.")
                continue
            warnings.extend(validate_relation_entry(entry))
            parent = entry.get("parent")
            child = entry.get("child")
            if parent and child:
                relation_keys.add((str(parent), str(child)))
        for parent_name, children in inline_hub.items():
            if not isinstance(children, dict):
                continue
            for child_name in children:
                key = (str(parent_name), str(child_name))
                if key in relation_keys:
                    warnings.append(
                        f'INLINE_HUB and INLINE_RELATIONS both define "{parent_name}" → "{child_name}"; '
                        "use INLINE_RELATIONS only.",
                    )
        return warnings

    def _dashboard_config_warnings(self) -> list[str]:
        config = get_config().get("DASHBOARD") or {}
        if not config.get("enabled", True):
            return []
        layout = list(config.get("layout") or [])
        if not layout:
            return [
                'BACKSTAGE["DASHBOARD"] is enabled but layout is empty — '
                "add widget ids (welcome, stats, quick_actions, my_drafts, recent_activity, charts)."
            ]
        known = {"welcome", "stats", "quick_actions", "my_drafts", "recent_activity", "charts"}
        unknown = [wid for wid in layout if wid not in known]
        if unknown:
            return [f"BACKSTAGE DASHBOARD layout contains unknown widget id(s): {', '.join(unknown)}."]
        return []

    def _host_package_import_warnings(self) -> list[str]:
        import re
        from pathlib import Path

        import backstage

        host_import = re.compile(r"^\s*(from\s+(app|core)\.|import\s+(app|core)\.)")
        package_root = Path(backstage.__file__).resolve().parent
        offenders: list[str] = []
        for path in package_root.rglob("*.py"):
            if "tests" in path.parts:
                continue
            rel = path.relative_to(package_root)
            for line in path.read_text().splitlines():
                stripped = line.strip()
                if stripped.startswith("#"):
                    continue
                if host_import.match(stripped):
                    offenders.append(str(rel))
                    break
        if not offenders:
            return []
        unique = sorted(set(offenders))
        preview = ", ".join(unique[:5])
        extra = len(unique) - min(5, len(unique))
        suffix = f" (and {extra} more)" if extra > 0 else ""
        return [
            f"Backstage package imports host modules (app/core) in: {preview}{suffix} — "
            f"move logic into backstage or accept as host coupling."
        ]
