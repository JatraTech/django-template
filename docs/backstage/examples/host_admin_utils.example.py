"""
Shared helpers for custom ModelAdmins that replace Backstage autodiscovered classes.

Copy into your Django project (e.g. yourapp/admin_utils.py) and import from app admin modules.

See docs/backstage/integration.md § Customize admin.
"""

from __future__ import annotations

from typing import Any

from django.contrib import admin

from backstage.settings import get_config


def replace_admin(model: type, admin_class: type[admin.ModelAdmin]) -> None:
    try:
        admin.site.unregister(model)
    except admin.sites.NotRegistered:
        pass
    admin.site.register(model, admin_class)


def host_inlines(model_name: str) -> list[Any]:
    return list(get_config().get("ADMIN_OVERRIDES", {}).get(model_name, {}).get("inlines") or [])


def hub_relation_inlines(model_name: str, *, extra: list[Any] | None = None) -> list[Any]:
    """INLINE_RELATIONS hub classes only (exclude autodiscovered reverse-FK inlines)."""
    hubs = [inline for inline in host_inlines(model_name) if inline.__name__.endswith("RelationInline")]
    return hubs + list(extra or [])


def hub_relation_inlines_for_child(
    model_name: str,
    child_model: type,
    *,
    extra: list[Any] | None = None,
) -> list[Any]:
    hubs = [
        inline
        for inline in host_inlines(model_name)
        if inline.__name__.endswith("RelationInline") and getattr(inline, "model", None) is child_model
    ]
    return hubs + list(extra or [])


def apply_host_overrides(admin_class: type, model_name: str) -> type:
    """Copy declarative ADMIN_OVERRIDES onto a custom admin class (excludes compiled inlines)."""
    overrides = dict(get_config().get("ADMIN_OVERRIDES", {}).get(model_name) or {})
    overrides.pop("inlines", None)
    for key, value in overrides.items():
        setattr(admin_class, key, value)
    return admin_class
