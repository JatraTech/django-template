from __future__ import annotations

from typing import Any
from urllib.parse import urlparse

from django.contrib.admin.sites import AdminSite
from django.db import models
from django.http import HttpRequest
from django.urls import NoReverseMatch, reverse

from backstage.dashboard.resolvers import user_can_view_model


def _normalize_admin_path(path: str) -> str:
    normalized = urlparse(str(path)).path or "/"
    if not normalized.endswith("/"):
        normalized = f"{normalized}/"
    return normalized


def model_for_admin_link(admin_site: AdminSite, link: str) -> type[models.Model] | None:
    if not link or not isinstance(link, str):
        return None

    target = _normalize_admin_path(link)
    try:
        index_path = _normalize_admin_path(reverse(f"{admin_site.name}:index", current_app=admin_site.name))
    except NoReverseMatch:
        index_path = _normalize_admin_path(reverse("admin:index"))

    if target == index_path:
        return None

    best_match: type[models.Model] | None = None
    best_prefix_len = -1

    for model in admin_site._registry:
        meta = model._meta
        candidates: list[str] = []
        for url_name, args in (
            (f"admin:{meta.app_label}_{meta.model_name}_changelist", ()),
            (f"admin:{meta.app_label}_{meta.model_name}_change", (1,)),
            (f"admin:{meta.app_label}_{meta.model_name}_add", ()),
        ):
            try:
                candidates.append(
                    _normalize_admin_path(
                        reverse(url_name, args=args, current_app=admin_site.name),
                    )
                )
            except NoReverseMatch:
                continue

        for prefix in candidates:
            if target == prefix or target.startswith(prefix):
                if len(prefix) > best_prefix_len:
                    best_prefix_len = len(prefix)
                    best_match = model

    return best_match


def nav_item_allowed(
    request: HttpRequest,
    admin_site: AdminSite,
    item: dict[str, Any],
    permission_callback_ok: bool,
) -> bool:
    if not permission_callback_ok:
        return False

    model = item.get("model")
    if model is None:
        link = item.get("link_callback") or item.get("link")
        if isinstance(link, str):
            model = model_for_admin_link(admin_site, link)

    if model is not None:
        return user_can_view_model(request, admin_site, model)

    return True


def nav_items_any_allowed(items: list[dict[str, Any]]) -> bool:
    for item in items:
        if item.get("has_permission"):
            return True
        nested = item.get("items")
        if isinstance(nested, list) and nav_items_any_allowed(nested):
            return True
    return False
