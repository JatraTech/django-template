from __future__ import annotations

from backstage.admin import ModelAdmin
from backstage.branding import resolve_site_url
from backstage.contrib.inlines.admin import StackedInline, TabularInline
from backstage.contrib.inlines.hub import HubInlineMixin
from backstage.mixins.rich_text import RichTextAdminMixin, RichTextInlineMixin
from backstage.preview.routes import resolve_preview_route
from backstage.preview.service import PreviewTokenService
from backstage.registry.editor_meta import EditorMetadataMixin


class BackstageModelAdmin(EditorMetadataMixin, RichTextAdminMixin, ModelAdmin):
    show_full_result_count = False
    preview_enabled = False
    preview_split_pane = True
    changelist_row_edit = True
    changelist_row_delete = True
    changelist_editable_ux = True

    def preview_route(self, obj) -> str | None:
        return resolve_preview_route(obj)

    def get_preview_url(self, request, obj) -> str | None:
        route = self.preview_route(obj)
        if not route:
            return None
        token = PreviewTokenService().generate(request.user.pk, obj)
        frontend_url = resolve_site_url()
        return f"{frontend_url}{route}?preview={token}"

    def change_view(self, request, object_id, form_url="", extra_context=None):
        extra_context = extra_context or {}
        obj = self.get_object(request, object_id)
        if self.preview_enabled and self.preview_split_pane and obj and request.user.is_staff:
            extra_context["preview_url"] = self.get_preview_url(request, obj)
            extra_context["preview_split_pane"] = True
        return super().change_view(request, object_id, form_url, extra_context=extra_context)


class BackstageTabularInline(EditorMetadataMixin, RichTextInlineMixin, TabularInline):
    pass


class BackstageStackedInline(EditorMetadataMixin, RichTextInlineMixin, StackedInline):
    collapsible = True


class BackstageHubTabularInline(HubInlineMixin, BackstageTabularInline):
    hub_show_title = False
    show_title = False


class BackstageHubStackedInline(HubInlineMixin, BackstageStackedInline):
    hub_show_title = True
    show_title = True
    collapsible = True


class SingletonAdmin(BackstageModelAdmin):
    def has_delete_permission(self, request, obj=None):
        return False

    def _ensure_singleton(self):
        return self.model.objects.get_or_create(pk=1)[0]

    def has_add_permission(self, request):
        if hasattr(self.model, "_default_manager"):
            return not self.model._default_manager.exists()
        return True

    def changelist_view(self, request, extra_context=None):
        from django.shortcuts import redirect

        obj = self._ensure_singleton()
        return redirect(f"{obj.pk}/change/")

    def change_view(self, request, object_id, form_url="", extra_context=None):
        if str(object_id) == "1":
            self._ensure_singleton()
        return super().change_view(request, object_id, form_url, extra_context=extra_context)
