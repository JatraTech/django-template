from __future__ import annotations

from django.db import models

from backstage.settings import get_config

DRAFT_PUBLISH_DUPLICATE_ROW = "duplicate_row"


def _draft_publish_config() -> dict:
    return get_config().get("DRAFT_PUBLISH") or {}


def is_draft_publish_enabled() -> bool:
    return bool(_draft_publish_config().get("enabled"))


def _model_registry_key(model: type[models.Model]) -> str:
    return f"{model._meta.app_label}.{model._meta.model_name}"


def is_draft_publish_model(model: type[models.Model]) -> bool:
    if not is_draft_publish_enabled():
        return False
    allowed = _draft_publish_config().get("models") or []
    if _model_registry_key(model) not in allowed:
        return False
    return hasattr(model, "live_version")


def resolve_draft_copy_field_names(model: type[models.Model]) -> tuple[str, ...] | None:
    """Copy fields for duplicate-row draft/publish (config, then model classmethod)."""
    config = _draft_publish_config()
    copy_fields = config.get("copy_fields") or {}
    key = _model_registry_key(model)
    configured = copy_fields.get(key)
    if configured is not None:
        if isinstance(configured, (list, tuple)) and configured:
            return tuple(str(name) for name in configured)
        return None

    classmethod = getattr(model, "draft_copy_field_names", None)
    if callable(classmethod):
        result = classmethod()
        if result:
            return tuple(str(name) for name in result)
    return None
