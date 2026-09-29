from __future__ import annotations

from django.db.models import Field

from backstage.conf import get_field_editor_meta


class EditorMetadataMixin:
    """Apply host FIELD_EDITOR_META labels and help_text to admin and inline fields."""

    def formfield_for_dbfield(self, db_field: Field, request, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
        if formfield is None:
            return None
        meta = get_field_editor_meta(self.model).get(db_field.name, {})
        if label := meta.get("label"):
            formfield.label = label
        if help_text := meta.get("help_text"):
            formfield.help_text = help_text
        return formfield
