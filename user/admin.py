from django.contrib import admin
from .models import User
from django.contrib.auth.admin import UserAdmin as _UserAdmin
from django.utils.translation import gettext_lazy as _


@admin.register(User)
class UserAdmin(_UserAdmin):
    list_filter = ("is_staff", "is_superuser", "user_role")
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            _("Personal info"),
            {"fields": ("first_name", "last_name", "email", "image", "dob")},
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "user_role",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                    "notify_on_user_reg",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    search_fields = ["id", "first_name", "last_name"]
