from __future__ import annotations

from django.apps import apps
from django.contrib import admin
from django.urls import reverse
from django.utils.translation import gettext

from backstage.conf import get_model_label, get_skip_app_labels
from backstage.settings import get_config

GENERIC_MODEL_ICONS = {
    "user": "people",
    "group": "group",
    "backstagesettings": "palette",
}


def _inherits_singleton(model: type) -> bool:
    return any(base.__name__ == "SingletonModel" for base in model.__mro__)


def _model_admin_link(model: type) -> str:
    meta = model._meta
    if _inherits_singleton(model):
        return reverse(f"admin:{meta.app_label}_{meta.model_name}_change", args=[1])
    return reverse(f"admin:{meta.app_label}_{meta.model_name}_changelist")


def _icon_for_model(model: type) -> str:
    name = model.__name__.lower()
    icons = {**GENERIC_MODEL_ICONS, **get_config().get("MODEL_ICONS", {})}
    return icons.get(name, "draft")


def _build_fallback_nav_groups() -> dict:
    app_labels: set[str] = set()
    for model in admin.site._registry:
        label = model._meta.app_label
        if label not in get_skip_app_labels():
            app_labels.add(label)

    groups: dict[str, dict] = {}
    for app_label in sorted(app_labels):
        try:
            title = apps.get_app_config(app_label).verbose_name
        except LookupError:
            title = app_label.replace("_", " ").title()
        groups[app_label] = {
            "title": title,
            "icon": "folder",
            "apps": [app_label],
        }
    return groups


def _get_nav_groups() -> dict:
    groups = get_config().get("NAV_GROUPS") or {}
    if groups:
        return groups
    return _build_fallback_nav_groups()


def _resolve_nav_model(spec: str) -> type | None:
    spec = spec.strip()
    if not spec:
        return None
    if "." in spec:
        app_label, model_name = spec.split(".", 1)
        try:
            model = apps.get_model(app_label, model_name)
        except LookupError:
            return None
    else:
        model = None
        needle = spec.lower()
        for registered in admin.site._registry:
            if registered.__name__.lower() == needle:
                model = registered
                break
        if model is None:
            return None
    if model not in admin.site._registry:
        return None
    return model


def _models_for_nav_group(group_key: str, group: dict, grouped_models: dict[str, list[type]]) -> list[type]:
    allowlist = group.get("models")
    if allowlist:
        models: list[type] = []
        for spec in allowlist:
            model = _resolve_nav_model(str(spec))
            if model is not None:
                models.append(model)
        return models
    return sorted(grouped_models.get(group_key, []), key=lambda m: get_model_label(m))


def get_sidebar_navigation(request) -> list[dict]:
    nav_groups = _get_nav_groups()
    app_to_group: dict[str, str] = {}
    for group_key, group in nav_groups.items():
        for app_label in group["apps"]:
            app_to_group[app_label] = group_key

    grouped_models: dict[str, list[type]] = {key: [] for key in nav_groups}
    for model in admin.site._registry:
        group_key = app_to_group.get(model._meta.app_label)
        if group_key:
            grouped_models[group_key].append(model)

    navigation: list[dict] = []
    for group_key, group in nav_groups.items():
        models = _models_for_nav_group(group_key, group, grouped_models)
        if not models:
            continue
        navigation.append(
            {
                "id": group_key,
                "title": group["title"],
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": get_model_label(model),
                        "icon": _icon_for_model(model),
                        "link": _model_admin_link(model),
                    }
                    for model in models
                ],
            }
        )
    return navigation


def get_dashboard_nav_group(request) -> dict | None:
    dashboard = get_config().get("DASHBOARD") or {}
    if dashboard.get("enabled") is False:
        return None
    nav_group_title = dashboard.get("nav_group_title") or gettext("Home")
    return {
        "id": "dashboard",
        "title": nav_group_title,
        "separator": True,
        "collapsible": True,
        "items": [
            {
                "title": gettext("Dashboard"),
                "icon": "dashboard",
                "link": reverse("admin:index"),
            }
        ],
    }


def get_backstage_sidebar(request) -> dict:
    navigation = get_sidebar_navigation(request)
    dashboard_group = get_dashboard_nav_group(request)
    if dashboard_group:
        navigation.insert(0, dashboard_group)
    return {
        "show_search": True,
        "show_all_applications": False,
        "navigation": navigation,
    }
