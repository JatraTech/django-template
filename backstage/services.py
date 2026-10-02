from __future__ import annotations

from typing import Any

from django.conf import settings as django_settings

from backstage.models import BackstageSettings

_settings_cache: BackstageSettings | None = None
_settings_cache_loaded = False


class BackstageSettingsNotConfiguredError(Exception):
    """Raised when the BackstageSettings singleton has not been created yet."""


def _is_nonempty_config_value(value: Any) -> bool:
    return value is not None and value != ""


def branding_defaults_from_config() -> dict[str, str]:
    from backstage.settings import get_config

    cfg = get_config() or {}
    defaults: dict[str, str] = {}
    for db_field, cfg_key in (
        ("site_title", "SITE_TITLE"),
        ("site_header", "SITE_HEADER"),
        ("site_subheader", "SITE_SUBHEADER"),
    ):
        value = cfg.get(cfg_key)
        if _is_nonempty_config_value(value) and not isinstance(value, dict):
            defaults[db_field] = str(value)
    return defaults


def ensure_backstage_settings() -> BackstageSettings:
    global _settings_cache, _settings_cache_loaded

    defaults: dict[str, str] = {}
    if not BackstageSettings.objects.filter(pk=1).exists():
        frontend_url = getattr(django_settings, "FRONTEND_URL", "")
        if frontend_url:
            defaults["frontend_url"] = frontend_url
        defaults.update(branding_defaults_from_config())

    obj, _ = BackstageSettings.objects.get_or_create(pk=1, defaults=defaults)
    _settings_cache = obj
    _settings_cache_loaded = True
    return obj


def get_backstage_settings_or_none() -> BackstageSettings | None:
    global _settings_cache, _settings_cache_loaded

    if _settings_cache_loaded:
        return _settings_cache

    try:
        _settings_cache = BackstageSettings.objects.get(pk=1)
    except BackstageSettings.DoesNotExist:
        return ensure_backstage_settings()

    _settings_cache_loaded = True
    return _settings_cache


def get_backstage_settings() -> BackstageSettings:
    settings_obj = get_backstage_settings_or_none()
    if settings_obj is None:
        raise BackstageSettingsNotConfiguredError(
            "Admin appearance is not configured. Create it under System → Admin appearance in admin."
        )
    return settings_obj


def clear_backstage_settings_cache() -> None:
    global _settings_cache, _settings_cache_loaded

    _settings_cache = None
    _settings_cache_loaded = False
