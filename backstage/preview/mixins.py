from __future__ import annotations

from django.db import models
from rest_framework.request import Request

from backstage.preview.service import get_preview_from_request


class PreviewQuerysetMixin:
    """Bypass publish/active filters when a valid preview token is present."""

    preview_model: type[models.Model] | None = None

    def get_preview_context(self) -> dict | None:
        request: Request = self.request
        preview = get_preview_from_request(request)
        if not preview:
            return None
        model = self.preview_model or self.queryset.model
        if preview["app_label"] == model._meta.app_label and preview["model_name"] == model._meta.model_name:
            return preview
        return None

    def get_unfiltered_queryset(self):
        model = self.preview_model or self.queryset.model
        return model._default_manager.all()
