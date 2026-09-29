from __future__ import annotations

from django.db import models

from backstage.draft.conf import resolve_draft_copy_field_names


class DraftPublishDuplicateRowMixin(models.Model):
    """Duplicate-row draft: live row (live_version null); draft row points at live via FK."""

    live_version = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="draft_copies",
    )

    class Meta:
        abstract = True

    @property
    def is_draft_copy(self) -> bool:
        return self.live_version_id is not None

    @property
    def is_live_row(self) -> bool:
        return self.live_version_id is None

    def preview_slug(self) -> str:
        if self.is_draft_copy and self.live_version_id:
            return self.live_version.slug
        return self.slug

    def get_or_create_draft(self) -> models.Model:
        if not self.is_live_row:
            raise ValueError("Only live rows can spawn a draft copy.")
        existing = self.draft_copies.first()
        if existing:
            return existing
        return self._create_draft_copy()

    def _create_draft_copy(self) -> models.Model:
        model_class = self.__class__
        copy_fields = resolve_draft_copy_field_names(model_class)
        if not copy_fields:
            raise ValueError(
                f"No draft copy fields for {model_class._meta.label_lower} — "
                f"set DRAFT_PUBLISH copy_fields or draft_copy_field_names() on the model."
            )
        kwargs = {name: getattr(self, name) for name in copy_fields}
        draft = model_class(
            live_version=self,
            is_published=False,
            **kwargs,
        )
        if hasattr(draft, "slug") and hasattr(self, "slug"):
            draft.slug = self.slug
        draft.save()
        return draft
