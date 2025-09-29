from django.contrib import admin

from app.utils.mixins.models.constants import ActivityStatusChoices


class StatusAdminSite(admin.AdminSite):
    def has_permission(self, request) -> bool:
        return (
            hasattr(request.user, "status")
            and request.user.status == ActivityStatusChoices.ACTIVE
            and request.user.is_staff
        )
