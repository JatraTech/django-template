from __future__ import annotations

from django.db import models, transaction
from django.utils import timezone

from backstage.draft.conf import resolve_draft_copy_field_names


class DraftPublishService:
    @staticmethod
    def _copy_field_names(model: type[models.Model]) -> tuple[str, ...]:
        names = resolve_draft_copy_field_names(model)
        if not names:
            raise ValueError(
                f"No draft copy fields for {model._meta.label_lower} — "
                f"set DRAFT_PUBLISH copy_fields or draft_copy_field_names() on the model."
            )
        return names

    @staticmethod
    @transaction.atomic
    def publish(instance: models.Model) -> models.Model:
        model = type(instance)
        if instance.is_draft_copy:
            live = instance.live_version
            if live is None:
                raise ValueError("Draft copy missing live_version.")
            for name in DraftPublishService._copy_field_names(model):
                setattr(live, name, getattr(instance, name))
            live.is_published = True
            if live.published_at is None:
                live.published_at = timezone.now()
            live.save()
            instance.delete()
            return live

        instance.is_published = True
        if instance.published_at is None:
            instance.published_at = timezone.now()
        instance.save()
        return instance

    @staticmethod
    @transaction.atomic
    def discard_draft(instance: models.Model) -> models.Model | None:
        if not instance.is_draft_copy:
            raise ValueError("Only draft copies can be discarded.")
        live = instance.live_version
        instance.delete()
        return live

    @staticmethod
    @transaction.atomic
    def discard_pending_drafts_for_live(live: models.Model) -> int:
        if not live.is_live_row:
            raise ValueError("discard_pending_drafts_for_live requires a live row.")
        count = 0
        for draft in list(live.draft_copies.all()):
            DraftPublishService.discard_draft(draft)
            count += 1
        return count

    @staticmethod
    @transaction.atomic
    def create_draft_from_live_form(live: models.Model, form) -> models.Model:
        if not live.is_live_row or not live.is_published:
            raise ValueError("Lazy draft creation requires a published live row.")
        if live.draft_copies.exists():
            raise ValueError("A draft copy already exists for this live row.")
        draft = live.get_or_create_draft()
        for name in DraftPublishService._copy_field_names(type(live)):
            if name in form.cleaned_data:
                setattr(draft, name, form.cleaned_data[name])
        draft.save()
        return draft
