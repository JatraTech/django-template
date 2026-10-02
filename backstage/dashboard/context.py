from __future__ import annotations

from typing import Any

from django.contrib.admin.sites import AdminSite
from django.http import HttpRequest

from backstage.dashboard.widgets import (
    build_charts,
    build_my_drafts,
    build_quick_actions,
    build_recent_activity,
    build_stats,
    build_welcome,
)
from backstage.draft.conf import is_draft_publish_enabled
from backstage.settings import get_config

DEFAULT_LAYOUT = ["welcome", "recent_activity"]

WIDGET_BUILDERS = {
    "welcome": lambda request, admin_site, cfg: build_welcome(request, admin_site, cfg),
    "stats": lambda request, admin_site, cfg: build_stats(request, admin_site, cfg),
    "quick_actions": lambda request, admin_site, cfg: build_quick_actions(request, admin_site, cfg),
    "my_drafts": lambda request, admin_site, cfg: build_my_drafts(request, admin_site, cfg),
    "recent_activity": lambda request, admin_site, cfg: build_recent_activity(request, cfg),
    "charts": lambda request, admin_site, cfg: build_charts(request, admin_site, cfg),
}


def get_dashboard_config() -> dict[str, Any]:
    return get_config().get("DASHBOARD") or {}


def is_dashboard_enabled() -> bool:
    config = get_dashboard_config()
    return config.get("enabled", True)


def build_dashboard_context(
    request: HttpRequest,
    admin_site: AdminSite,
    base_context: dict[str, Any],
) -> dict[str, Any]:
    config = get_dashboard_config()
    layout = list(config.get("layout") or DEFAULT_LAYOUT)
    if is_draft_publish_enabled() and "my_drafts" not in layout:
        insert_at = len(layout)
        if "charts" in layout:
            insert_at = layout.index("charts") + 1
        elif "quick_actions" in layout:
            insert_at = layout.index("quick_actions") + 1
        layout.insert(insert_at, "my_drafts")
    widgets: dict[str, Any] = {}

    for widget_id in layout:
        builder = WIDGET_BUILDERS.get(widget_id)
        if builder is None:
            continue
        widgets[widget_id] = builder(request, admin_site, config)

    base_context.update(
        {
            "dashboard_enabled": True,
            "dashboard_layout": layout,
            "dashboard_widgets": widgets,
            "dashboard_show_app_list": bool(config.get("show_app_list", False)),
        }
    )
    return base_context
