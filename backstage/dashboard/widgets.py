from __future__ import annotations

import json
from typing import Any

from django.contrib.admin.models import LogEntry
from django.contrib.admin.sites import AdminSite
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from backstage.branding import resolve_text
from backstage.conf import get_model_label
from backstage.dashboard.activity_labels import (
    activity_context_label,
    human_activity_title,
    parse_inline_objects,
)
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

CHART_ACCENT_VARS: dict[str, str] = {
    "blue": "var(--backstage-accent-blue)",
    "green": "var(--backstage-accent-green)",
    "amber": "var(--backstage-accent-amber)",
    "purple": "var(--backstage-accent-purple)",
    "slate": "var(--backstage-accent-slate)",
}

CHART_FILL_VARS: dict[str, str] = {
    "blue": "var(--backstage-chart-fill-blue)",
    "green": "var(--backstage-chart-fill-green)",
    "amber": "var(--backstage-chart-fill-amber)",
    "purple": "var(--backstage-chart-fill-purple)",
    "slate": "var(--backstage-chart-fill-slate)",
}


def build_welcome(request: HttpRequest, admin_site: AdminSite, dashboard_config: dict[str, Any]) -> dict[str, Any]:
    welcome_cfg = dashboard_config.get("welcome") or {}
    title = welcome_cfg.get("title") or resolve_text("site_header", "SITE_HEADER") or _("Dashboard")
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
        if spec.get("if_draft_publish") and not is_draft_publish_enabled():
            continue

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

        link = spec.get("link", "changelist") if link_model else spec.get("link")
        url = resolve_stat_link_url(
            admin_site,
            link_model,
            link,
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


def build_charts(request: HttpRequest, admin_site: AdminSite, dashboard_config: dict[str, Any]) -> list[dict[str, Any]]:
    specs = dashboard_config.get("charts") or []
    charts: list[dict[str, Any]] = []

    for spec in specs:
        segment_specs = spec.get("segments") or []
        ring_labels: list[str] = []
        ring_data: list[int] = []
        ring_colors: list[str] = []
        legend: list[dict[str, Any]] = []
        segment_counts: list[int] = []

        for segment in segment_specs:
            if segment.get("if_draft_publish") and not is_draft_publish_enabled():
                continue

            callback_path = segment.get("count_callback")
            model_label = segment.get("model")
            model = None
            count: int | None = None

            if callback_path:
                try:
                    count = resolve_count_callback(callback_path, request, admin_site)
                except (ImportError, TypeError, ValueError):
                    continue
            elif model_label:
                try:
                    model = parse_model_label(str(model_label))
                except LookupError:
                    continue
                if not user_can_view_model(request, admin_site, model):
                    continue
                count = safe_filter_count(model, segment.get("filter") or {})
            else:
                continue

            accent = str(segment.get("accent") or "blue")
            fill_color = CHART_FILL_VARS.get(accent, CHART_FILL_VARS["blue"])
            label = str(resolve_stat_label(model, segment.get("label")))

            segment_counts.append(count)
            legend.append({"label": label, "count": count, "accent": accent})
            if count > 0:
                ring_labels.append(label)
                ring_data.append(count)
                ring_colors.append(fill_color)

        if not legend:
            continue

        total = sum(segment_counts)
        if total == 0:
            continue

        if not ring_labels:
            continue

        chart_data = {
            "labels": ring_labels,
            "datasets": [
                {
                    "data": ring_data,
                    "backgroundColor": ring_colors,
                    "borderWidth": 2,
                    "borderColor": "var(--backstage-surface)",
                }
            ],
        }
        charts.append(
            {
                "id": spec.get("id") or f"chart_{len(charts)}",
                "title": str(spec.get("title") or _("Chart")),
                "type": spec.get("type") or "doughnut",
                "height": int(spec.get("height") or 220),
                "total": total,
                "data_json": json.dumps(chart_data),
                "legend": legend,
            }
        )

    return charts


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
        inline_objects = parse_inline_objects(entry.change_message or "")
        title = human_activity_title(entry)
        context_label = activity_context_label(entry, inline_objects)
        activity.append(
            {
                "title": title,
                "context_label": context_label,
                "admin_url": admin_url,
                "action_time": entry.action_time,
                "user_repr": str(entry.user) if entry.user_id else "",
                "user_initials": _user_initials(str(entry.user) if entry.user_id else ""),
            }
        )

    return activity
