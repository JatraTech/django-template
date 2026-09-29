from __future__ import annotations

from typing import TYPE_CHECKING, Any
from urllib.parse import urlencode

from django.apps import apps
from django.contrib.admin.sites import AdminSite
from django.core.exceptions import FieldError
from django.db import models
from django.http import HttpRequest
from django.urls import reverse
from django.utils.module_loading import import_string

from backstage.conf import get_model_label
from backstage.settings import get_config

if TYPE_CHECKING:
    from django.contrib.admin import ModelAdmin


def parse_model_label(model_label: str) -> type[models.Model]:
    app_label, model_name = model_label.split(".", 1)
    return apps.get_model(app_label, model_name)


def get_model_admin(admin_site: AdminSite, model: type[models.Model]) -> ModelAdmin | None:
    return admin_site._registry.get(model)


def user_can_view_model(request: HttpRequest, admin_site: AdminSite, model: type[models.Model]) -> bool:
    model_admin = get_model_admin(admin_site, model)
    if model_admin is None:
        return False
    return model_admin.has_view_permission(request)


def user_can_add_model(request: HttpRequest, admin_site: AdminSite, model: type[models.Model]) -> bool:
    model_admin = get_model_admin(admin_site, model)
    if model_admin is None:
        return False
    return model_admin.has_add_permission(request)


def user_can_change_model(request: HttpRequest, admin_site: AdminSite, model: type[models.Model]) -> bool:
    model_admin = get_model_admin(admin_site, model)
    if model_admin is None:
        return False
    return model_admin.has_change_permission(request)


def resolve_model_icon(model: type[models.Model], override: str | None = None) -> str:
    if override:
        return override
    key = model._meta.model_name
    icons = get_config().get("MODEL_ICONS") or {}
    return icons.get(key, "dataset")


def resolve_stat_label(model: type[models.Model] | None, override: str | None = None) -> str:
    if override:
        return str(override)
    if model is None:
        return ""
    return get_model_label(model, plural=True)


def admin_changelist_url(admin_site: AdminSite, model: type[models.Model], query: dict | None = None) -> str:
    url = reverse(
        f"admin:{model._meta.app_label}_{model._meta.model_name}_changelist",
        current_app=admin_site.name,
    )
    if query:
        url = f"{url}?{urlencode(query, doseq=True)}"
    return url


def admin_add_url(admin_site: AdminSite, model: type[models.Model]) -> str:
    return reverse(
        f"admin:{model._meta.app_label}_{model._meta.model_name}_add",
        current_app=admin_site.name,
    )


def admin_change_url(admin_site: AdminSite, model: type[models.Model], object_id: int | str) -> str:
    return reverse(
        f"admin:{model._meta.app_label}_{model._meta.model_name}_change",
        args=[object_id],
        current_app=admin_site.name,
    )


def resolve_singleton_change_url(request: HttpRequest, admin_site: AdminSite, model: type[models.Model]) -> str | None:
    if not user_can_change_model(request, admin_site, model):
        return None
    instance = model.objects.first()
    if instance is None:
        instance = model.objects.create()
    return admin_change_url(admin_site, model, instance.pk)


def resolve_stat_link_url(
    admin_site: AdminSite,
    model: type[models.Model] | None,
    link: str | None,
    link_query: dict | None,
) -> str | None:
    if model is None or not link:
        return None
    if link == "changelist":
        return admin_changelist_url(admin_site, model, link_query)
    if link == "add":
        return admin_add_url(admin_site, model)
    return reverse(link, current_app=admin_site.name)


def resolve_count_callback(callback_path: str, request: HttpRequest, admin_site: AdminSite) -> int:
    callback = import_string(callback_path)
    return int(callback(request, admin_site))


def safe_filter_count(model: type[models.Model], filters: dict[str, Any]) -> int:
    if not filters:
        return model.objects.count()
    try:
        return model.objects.filter(**filters).count()
    except FieldError:
        return 0


def resolve_preview_url(request: HttpRequest, admin_site: AdminSite, obj: models.Model) -> str | None:
    model_admin = get_model_admin(admin_site, obj.__class__)
    if model_admin is None or not getattr(model_admin, "preview_enabled", False):
        return None
    get_preview_url = getattr(model_admin, "get_preview_url", None)
    if not callable(get_preview_url):
        return None
    return get_preview_url(request, obj)


def resolve_welcome_link(request: HttpRequest, admin_site: AdminSite, spec: dict[str, Any]) -> dict[str, str] | None:
    label = spec.get("label")
    if not label:
        return None

    explicit_url = spec.get("url")
    if explicit_url:
        link = {"label": str(label), "url": str(explicit_url)}
        if spec.get("icon"):
            link["icon"] = str(spec["icon"])
        return link

    if spec.get("url_key") == "frontend":
        from backstage.branding import resolve_site_url

        link = {"label": str(label), "url": resolve_site_url(), "external": True}
        if spec.get("icon"):
            link["icon"] = str(spec["icon"])
        return link

    model_label = spec.get("model")
    if not model_label:
        return None

    try:
        model = parse_model_label(model_label)
    except LookupError:
        return None

    action = spec.get("action", "changelist")
    url: str | None = None

    if spec.get("singleton") or action == "change":
        url = resolve_singleton_change_url(request, admin_site, model)
    elif action == "add":
        if not user_can_add_model(request, admin_site, model):
            return None
        url = admin_add_url(admin_site, model)
    else:
        if not user_can_view_model(request, admin_site, model):
            return None
        url = admin_changelist_url(admin_site, model)

    if not url:
        return None
    link = {"label": str(label), "url": url}
    if spec.get("icon"):
        link["icon"] = str(spec["icon"])
    return link


def build_welcome_links(
    request: HttpRequest, admin_site: AdminSite, link_specs: list[dict[str, Any]]
) -> list[dict[str, str]]:
    links: list[dict[str, str]] = []
    for spec in link_specs:
        resolved = resolve_welcome_link(request, admin_site, spec)
        if resolved is not None:
            links.append(resolved)
    return links
