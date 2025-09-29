from rest_framework.permissions import BasePermission

from user.constants import UserRoleChoices


class CleanersNotAllowed(BasePermission):
    def has_permission(self, request, view):
        return not request.user.user_role == UserRoleChoices.CLEANER
