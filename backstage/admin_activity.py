from __future__ import annotations

from django.contrib import admin
from django.contrib.admin.models import ADDITION, CHANGE, DELETION, LogEntry
from django.http import HttpRequest
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from backstage.admin import ModelAdmin
from backstage.dashboard.activity_labels import (
    activity_action_label,
    activity_change_detail,
    activity_log_entry_ip,
    activity_log_queryset,
)


class LogEntryActionFilter(admin.SimpleListFilter):
    title = _("Action")
    parameter_name = "action_flag"

    def lookups(self, request, model_admin):
        return (
            (str(ADDITION), _("Added")),
            (str(CHANGE), _("Changed")),
            (str(DELETION), _("Deleted")),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value is None:
            return queryset
        return queryset.filter(action_flag=int(value))


class AdminActivityLogAdmin(ModelAdmin):
    changelist_row_edit = False
    changelist_row_delete = False

    list_display = (
        "action_time",
        "user",
        "action_display",
        "content_type",
        "object_repr",
        "object_link_display",
        "change_detail_display",
        "ip_display",
    )
    list_filter = ("action_time", LogEntryActionFilter, "content_type")
    search_fields = ("object_repr", "change_message")
    ordering = ("-action_time",)
    list_select_related = ("user", "content_type", "backstage_meta")

    def has_module_permission(self, request: HttpRequest) -> bool:
        return bool(request.user.is_active and request.user.is_staff)

    def has_view_permission(self, request: HttpRequest, obj=None) -> bool:
        return self.has_module_permission(request)

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def has_change_permission(self, request: HttpRequest, obj=None) -> bool:
        return False

    def has_delete_permission(self, request: HttpRequest, obj=None) -> bool:
        return False

    def change_view(self, request, object_id, form_url="", extra_context=None):
        from django.shortcuts import redirect

        return redirect("admin:backstage_adminactivitylog_changelist")

    def get_queryset(self, request: HttpRequest):
        return activity_log_queryset(request)

    def get_list_filter(self, request: HttpRequest):
        if request.user.is_superuser:
            return ("action_time", LogEntryActionFilter, "user", "content_type")
        return self.list_filter

    @admin.display(description=_("Action"))
    def action_display(self, obj: LogEntry) -> str:
        return activity_action_label(obj)

    @admin.display(description=_("Object link"))
    def object_link_display(self, obj: LogEntry):
        url = obj.get_admin_url()
        if url:
            return format_html('<a href="{}">{}</a>', url, _("Open"))
        return "—"

    @admin.display(description=_("Changes"))
    def change_detail_display(self, obj: LogEntry) -> str:
        return activity_change_detail(obj)

    @admin.display(description=_("IP address"))
    def ip_display(self, obj: LogEntry) -> str:
        ip = activity_log_entry_ip(obj)
        if ip:
            return ip
        return "—"
