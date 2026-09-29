from __future__ import annotations

from tinymce.widgets import AdminTinyMCE


class RichTextAdminMixin:
    """Apply TinyMCE to selected TextField columns in Django admin."""

    rich_text_fields: tuple[str, ...] = ()

    class Media:
        js = ("admin/tinymce_upload.js",)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        for name in self.rich_text_fields:
            if name in form.base_fields:
                form.base_fields[name].widget = AdminTinyMCE()
        return form


class RichTextInlineMixin:
    """Apply TinyMCE to selected inline TextField columns."""

    rich_text_fields: tuple[str, ...] = ()

    class Media:
        js = ("admin/tinymce_upload.js",)

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name in self.rich_text_fields:
            kwargs["widget"] = AdminTinyMCE()
        return super().formfield_for_dbfield(db_field, request, **kwargs)
