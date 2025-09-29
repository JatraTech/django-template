import re
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail, send_mass_mail
from django.db.models import Q
from rest_framework import serializers

from app import settings
from app.utils.mixins.serializers import (
    BaseModelSerializer,
    ExtendableModelSerializer,
)
from user.constants import UserRoleChoices
from user.models import AccessHaltReasonChoices, User
from django.contrib.auth.models import Permission

from user.utils import generate_username


class UserPermissionSerializer(BaseModelSerializer):
    app = serializers.CharField(source="content_type.app_label")

    class Meta:
        model = Permission
        fields = ["id", "app", "name", "codename"]


class UserLiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "full_name", "image"]


class MiniUserSerializer(BaseModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "phone",
            "full_name",
            "email",
            "dob",
            "image",
            "user_role",
            "is_active",
        ]
        ignore_always_exclude_fields = ["is_active"]


class UserSerializer(ExtendableModelSerializer):
    extend_field_serializers = {
        "permissions": UserPermissionSerializer(
            many=True,
            source="user_permissions",
        ),
    }

    class Meta:
        model = User
        exclude = [
            "user_permissions",
            "groups",
        ]
        extra_kwargs = {"password": {"write_only": True}}
        ignore_always_exclude_fields = ["is_active"]

    def validate(self, attrs):
        valid_data = super().validate(attrs)
        if "password" in valid_data:
            valid_data["password"] = make_password(valid_data.get("password"))
        return valid_data


class UserImageUploadSerializer(serializers.Serializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    image = serializers.ImageField(allow_null=True)

    def save(self, **kwargs):
        if user := self.validated_data.get("user"):
            user.image = self.validated_data.get("image", None)
            user.save()
            return {"image": user.image.url, "id": user.id}

    def to_representation(self, instance):
        request = self.context.get("request")
        return {
            "user": instance.get("user").id,
            "image": request.build_absolute_uri(instance.get("user").image.url)
            if request and instance.get("user").image
            else None,
        }


class PartialUserCreationSerializer(BaseModelSerializer):
    """
    A serializer to create user (Generally Users who show interest in using the app).
    """

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "dob",
            "phone",
            "address",
            "email",
        ]
        extra_kwargs = {"address": {"required": False, "allow_blank": True}}

    def create(self, validated_data):
        validated_data["is_active"] = False
        validated_data["access_halt_reason"] = (
            AccessHaltReasonChoices.APPLICATION_PENDING
        )
        validated_data["username"] = generate_username(
            validated_data["first_name"],
            validated_data["last_name"],
        )
        user: User = super().create(validated_data)

        # notify admins about the new registration
        admin_emails = (
            User.objects.filter(notify_on_user_reg=True, is_active=True)
            .filter(
                Q(user_role__in=[UserRoleChoices.ADMIN, UserRoleChoices.SUPER_ADMIN])
                | Q(is_superuser=True)
                | Q(is_staff=True)
            )
            .values_list("email", flat=True)
        )
        send_mail(
            subject="New User Registration",
            message=f"A new user by the username {user.username} has been registered on the platform. Please review and activate their account.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=list(admin_emails),
        )
        return user


class UserBasicInfoSerializer(BaseModelSerializer):
    class Meta:
        model = User
        fields = ["id", "full_name", "image"]
