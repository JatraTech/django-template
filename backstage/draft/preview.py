from __future__ import annotations

from django.db import models

from backstage.draft.conf import is_draft_publish_model
from backstage.preview.routes import resolve_preview_route


def preview_enabled_for_model(model: type[models.Model]) -> bool:
    if not is_draft_publish_model(model):
        return False
    try:
        instance = model()
        if hasattr(instance, "slug") and not getattr(instance, "slug", None):
            instance.slug = "preview-route-check"
        return resolve_preview_route(instance) is not None
    except Exception:
        return False
