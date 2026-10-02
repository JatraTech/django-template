from __future__ import annotations

from typing import Any

from django.http import HttpRequest

HUB_INLINE_AFTER_TEMPLATE = "backstage/helpers/edit_inline/hub_inline_after.html"


class HubInlineMixin:
    """
    Read-only child summary on a parent change form: Edit/Delete open standalone admin;
    footer Add + View all. Set inline_mode = "hub" or use BackstageHub* inline bases.
    """

    inline_mode = "hub"
    hub_fields: tuple[str, ...] | None = None
    hub_help_text: str | None = None
    hub_add_label: str | None = None
    hub_changelist_label: str | None = None
    hub_show_title: bool = False
    hub_primary_tab: bool = True
    hub_anchor_fieldset_tab: str | None = None
    show_change_link = True
    can_delete = False
    extra = 0
    template_after = HUB_INLINE_AFTER_TEMPLATE

    def __init__(self, parent_model, admin_site) -> None:
        from backstage.registry.inline_hub import apply_inline_hub_config

        apply_inline_hub_config(self.__class__, parent_model)
        super().__init__(parent_model, admin_site)

    def get_hub_fields(self, request: HttpRequest, obj=None) -> tuple[str, ...]:
        if self.hub_fields:
            return self.hub_fields
        fields = self.fields
        if fields:
            if isinstance(fields, (list, tuple)):
                return tuple(fields)
            return (fields,)
        return ()

    def get_readonly_fields(self, request: HttpRequest, obj=None):
        if self.inline_mode == "hub":
            return self.get_hub_fields(request, obj)
        return super().get_readonly_fields(request, obj)

    def has_add_permission(self, request: HttpRequest, obj=None) -> bool:
        if self.inline_mode == "hub":
            return False
        return super().has_add_permission(request, obj)

    def has_change_permission(self, request: HttpRequest, obj=None) -> bool:
        if self.inline_mode == "hub":
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request: HttpRequest, obj=None) -> bool:
        if self.inline_mode == "hub":
            return False
        return super().has_delete_permission(request, obj)

    def get_hub_template_context(self, request: HttpRequest) -> dict[str, Any]:
        """Extension point for django-template universal admin panels."""
        return {}
