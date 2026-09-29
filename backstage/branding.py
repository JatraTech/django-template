from __future__ import annotations

from typing import Any

from django.conf import settings
from django.templatetags.static import static
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from backstage.defaults import BRANDING_DEFAULTS
from backstage.services import get_backstage_settings_or_none
from backstage.settings import get_config
from backstage.theme_presets import DEFAULT_THEME_PRESET
from backstage.theme_tokens import build_theme_css, build_theme_tokens


def _is_nonempty(value: Any) -> bool:
    return value is not None and value != ""


def _backstage_value(key: str) -> Any:
    return get_config("BACKSTAGE").get(key)


def resolve_text(db_attr: str, backstage_key: str) -> str:
    settings_obj = get_backstage_settings_or_none()
    if settings_obj is not None:
        db_value = getattr(settings_obj, db_attr, None)
        if _is_nonempty(db_value):
            return str(db_value)

    config_value = _backstage_value(backstage_key)
    if _is_nonempty(config_value) and not isinstance(config_value, dict):
        return str(config_value)

    default = BRANDING_DEFAULTS.get(backstage_key, "")
    return str(default) if default is not None else ""


def resolve_site_url() -> str:
    settings_obj = get_backstage_settings_or_none()
    if settings_obj is not None and _is_nonempty(settings_obj.frontend_url):
        return settings_obj.frontend_url.rstrip("/")

    config_value = _backstage_value("SITE_URL")
    if _is_nonempty(config_value):
        return str(config_value).rstrip("/")

    frontend_url = getattr(settings, "FRONTEND_URL", None)
    if _is_nonempty(frontend_url):
        return str(frontend_url).rstrip("/")

    return BRANDING_DEFAULTS["SITE_URL"].rstrip("/")


def resolve_api_docs_url() -> str:
    config_value = _backstage_value("API_DOCS_URL")
    if _is_nonempty(config_value):
        return str(config_value).rstrip("/")

    backend_url = getattr(settings, "BACKEND_URL", "http://localhost:8000")
    return f"{str(backend_url).rstrip('/')}/schema/rapidoc/"


def resolve_logo() -> dict[str, str] | None:
    settings_obj = get_backstage_settings_or_none()
    if settings_obj is not None and (settings_obj.logo_light or settings_obj.logo_dark):
        logo: dict[str, str] = {}
        if settings_obj.logo_light:
            logo["light"] = settings_obj.logo_light.url
        if settings_obj.logo_dark:
            logo["dark"] = settings_obj.logo_dark.url
        elif settings_obj.logo_light:
            logo["dark"] = settings_obj.logo_light.url
        return logo or None

    config_logo = _backstage_value("SITE_LOGO")
    if isinstance(config_logo, dict) and config_logo:
        return config_logo

    return None


def resolve_favicons() -> list[dict[str, str]] | None:
    settings_obj = get_backstage_settings_or_none()
    if settings_obj is not None and settings_obj.logo_light:
        return [
            {
                "rel": "icon",
                "sizes": "32x32",
                "type": "image/webp",
                "href": settings_obj.logo_light.url,
            },
        ]

    config_favicons = _backstage_value("SITE_FAVICONS")
    if isinstance(config_favicons, list) and config_favicons:
        return config_favicons

    return None


def resolve_site_dropdown(request: Any) -> list[dict[str, Any]]:
    config_dropdown = _backstage_value("SITE_DROPDOWN")
    if isinstance(config_dropdown, list) and config_dropdown:
        return config_dropdown

    return [
        {
            "icon": "public",
            "title": _("Public website"),
            "link": resolve_site_url(),
            "attrs": {"target": "_blank"},
        },
        {
            "icon": "code",
            "title": _("API docs"),
            "link": resolve_api_docs_url(),
            "attrs": {"target": "_blank"},
        },
    ]


def resolve_default_styles(request: Any) -> list[str]:
    return [
        reverse("backstage-theme-css"),
        static("backstage/preview.css"),
    ]


def resolve_theme_tokens() -> dict[str, Any]:
    settings_obj = get_backstage_settings_or_none()
    return build_theme_tokens(settings_obj)


def resolve_theme_css() -> str:
    return build_theme_css(resolve_theme_tokens())


def resolve_appearance_classes() -> str:
    settings_obj = get_backstage_settings_or_none()
    theme_preset = DEFAULT_THEME_PRESET
    font_family = "inter"
    sidebar_density = "comfortable"

    if settings_obj is not None:
        theme_preset = getattr(settings_obj, "theme_preset", None) or DEFAULT_THEME_PRESET
        font_family = getattr(settings_obj, "font_family", None) or "inter"
        sidebar_density = getattr(settings_obj, "sidebar_density", None) or "comfortable"

    return " ".join(
        [
            f"backstage-preset-{theme_preset}",
            f"backstage-density-{sidebar_density}",
            f"backstage-font-{font_family}",
        ]
    )
