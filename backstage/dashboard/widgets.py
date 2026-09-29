from __future__ import annotations

from typing import Any

from django.contrib.admin.models import LogEntry
from django.contrib.admin.sites import AdminSite
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from backstage.conf import get_model_label
from backstage.dashboard.resolvers import (
    admin_add_url,
    admin_change_url,
    admin_changelist_url,
    build_welcome_links,
    parse_model_label,
    resolve_count_callback,
    resolve_model_icon,
    resolve_preview_url,
    resolve_singleton_change_url,
    resolve_stat_label,
    resolve_stat_link_url,
    safe_filter_count,
    user_can_add_model,
    user_can_change_model,
    user_can_view_model,
)
from backstage.draft.conf import is_draft_publish_enabled
from backstage.settings import get_config


def build_welcome(request: HttpRequest, admin_site: AdminSite, dashboard_config: dict[str, Any]) -> dict[str, Any]:
    welcome_cfg = dashboard_config.get("welcome") or {}
    config = get_config()
    title = welcome_cfg.get("title") or config.get("SITE_HEADER") or _("Dashboard")
    body = welcome_cfg.get("body") or _("Use the sidebar to find content, or the shortcuts below when configured.")
    link_specs = welcome_cfg.get("links") or []
    links = build_welcome_links(request, admin_site, link_specs)
    return {
        "title": str(title),
        "body": str(body),
        "links": links,
    }


def _user_initials(user_repr: str) -> str:
    cleaned = (user_repr or "").strip()
    if not cleaned:
        return "Y"
    parts = cleaned.split()
    if len(parts) >= 2:
        return f"{parts[0][0]}{parts[1][0]}".upper()
    return cleaned[:2].upper()


def build_stats(request: HttpRequest, admin_site: AdminSite, dashboard_config: dict[str, Any]) -> list[dict[str, Any]]:
    specs = dashboard_config.get("stats") or []
    cards: list[dict[str, Any]] = []

    for spec in specs:
        model_label = spec.get("model")
        model = None
        if model_label:
            try:
                model = parse_model_label(model_label)
            except LookupError:
                continue
            if not user_can_view_model(request, admin_site, model):
                continue

        callback_path = spec.get("count_callback")
        if callback_path:
            try:
                count = resolve_count_callback(callback_path, request, admin_site)
            except (ImportError, TypeError, ValueError):
                continue
        elif model is not None:
            count = safe_filter_count(model, spec.get("filter") or {})
        else:
            continue

        link_model = model
        if link_model is None and model_label:
            try:
                link_model = parse_model_label(model_label)
            except LookupError:
                link_model = None

        url = resolve_stat_link_url(
            admin_site,
            link_model,
            spec.get("link", "changelist"),
            spec.get("link_query"),
        )
        icon = resolve_model_icon(link_model, spec.get("icon")) if link_model else spec.get("icon", "analytics")
        cards.append(
            {
                "id": spec.get("id") or f"stat_{len(cards)}",
                "label": resolve_stat_label(link_model, spec.get("label")),
                "count": count,
                "icon": icon,
                "accent": spec.get("accent", "blue"),
                "url": url,
            }
        )

    return cards


def build_quick_actions(
    request: HttpRequest, admin_site: AdminSite, dashboard_config: dict[str, Any]
) -> list[dict[str, Any]]:
    specs = dashboard_config.get("quick_actions") or []
    actions: list[dict[str, Any]] = []

    for spec in specs:
        model_label = spec.get("model")
        if not model_label:
            continue
        try:
            model = parse_model_label(model_label)
        except LookupError:
            continue

        action = spec.get("action", "changelist")
        url: str | None = None

        if spec.get("singleton") or action == "change":
            url = resolve_singleton_change_url(request, admin_site, model)
        elif action == "add":
            if not user_can_add_model(request, admin_site, model):
                continue
            url = admin_add_url(admin_site, model)
        else:
            if not user_can_view_model(request, admin_site, model):
                continue
            url = admin_changelist_url(admin_site, model)

        if not url:
            continue

        actions.append(
            {
                "label": str(spec.get("label") or get_model_label(model, plural=False)),
                "url": url,
                "icon": resolve_model_icon(model, spec.get("icon")),
            }
        )

    return actions


def build_my_drafts(request: HttpRequest, admin_site: AdminSite, dashboard_config: dict[str, Any]) -> dict[str, Any]:
    limit = int((dashboard_config.get("my_drafts") or {}).get("limit") or 10)
    rows: list[dict[str, Any]] = []

    if not is_draft_publish_enabled():
        return {"rows": rows, "limit": limit}

    draft_config = get_config().get("DRAFT_PUBLISH") or {}
    model_keys = draft_config.get("models") or []

    for model_key in model_keys:
        try:
            model = parse_model_label(model_key)
        except LookupError:
            continue
        if not hasattr(model, "live_version"):
            continue
        if not user_can_change_model(request, admin_site, model):
            continue

        qs = model.objects.filter(live_version__isnull=False).select_related("live_version")[:limit]

        for obj in qs:
            title = getattr(obj, "title", None) or str(obj)
            rows.append(
                {
                    "title": str(title),
                    "model_label": get_model_label(model, plural=False),
                    "edit_url": admin_change_url(admin_site, model, obj.pk),
                    "preview_url": resolve_preview_url(request, admin_site, obj),
                }
            )
            if len(rows) >= limit:
                break
        if len(rows) >= limit:
            break

    return {"rows": rows[:limit], "limit": limit}


def build_recent_activity(request: HttpRequest, dashboard_config: dict[str, Any]) -> list[dict[str, Any]]:
    limit = int((dashboard_config.get("recent_activity") or {}).get("limit") or 10)
    entries = (
        LogEntry.objects.select_related("content_type", "user")
        .filter(user_id=request.user.pk)
        .order_by("-action_time")[:limit]
    )

    activity: list[dict[str, Any]] = []
    for entry in entries:
        admin_url = entry.get_admin_url()
        content_type_name = ""
        if entry.content_type_id:
            content_type_name = str(entry.content_type.name)
        activity.append(
            {
                "object_repr": entry.object_repr,
                "admin_url": admin_url,
                "content_type_name": content_type_name,
                "action_time": entry.action_time,
                "is_addition": entry.is_addition,
                "is_change": entry.is_change,
                "is_deletion": entry.is_deletion,
                "user_repr": str(entry.user) if entry.user_id else "",
                "user_initials": _user_initials(str(entry.user) if entry.user_id else ""),
            }
        )

    return activity
