from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from app.utils.mixins.serializers import BaseModelSerializer
from user.constants import UserRoleChoices
from user.models import User


class TeamSerializer(serializers.ModelSerializer):
    size = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = ["id", "full_name", "size"]


class TeamMemberSerializer(BaseModelSerializer):
    allowed_user_roles = [
        UserRoleChoices.PROPERTY_MANAGER
    ]  # user_role allowed to create from this API. Should be restricted to roles lower than host

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "full_name",
            "email",
            "phone",
            "user_role",
            "superior",
            "password",
        ]
        extra_kwargs = {
            "password": {"write_only": True},
            "user_role": {
                "required": False,
                "default": UserRoleChoices.PROPERTY_MANAGER,
            },
            "superior": {"write_only": True},
        }

    def validate_user_role(self, value):
        if value not in self.allowed_user_roles:
            raise ValidationError("User Role not allowed")
        return value
