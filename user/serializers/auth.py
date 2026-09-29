from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from rest_framework import serializers

from user.utils import (
    get_password_reset_token_for_email_or_username,
    reset_password_for_token,
)


class SendResetPasswordEmailSerializer(serializers.Serializer):
    email_or_username = serializers.CharField()
    template_name = serializers.ChoiceField(
        choices=["password_reset", "on_active_password_reset"],
        default="password_reset",
        required=False,
    )

    def create(self, validated_data):
        template_name = validated_data.get("template_name", "password_reset")
        reset_email_template = f"user/email/{template_name}.html"

        user, uidb64, token = get_password_reset_token_for_email_or_username(validated_data["email_or_username"])
        context = {
            "user": user,
            "uidb64": uidb64,
            "token": token,
            "domain": settings.APP_FRONTEND_BASE_URL,
        }
        template_to_str = render_to_string(reset_email_template, context)

        send_mail(
            subject="Password Reset",
            message=template_to_str,
            recipient_list=[user.email],
            html_message=template_to_str,
            from_email=settings.DEFAULT_FROM_EMAIL,
        )
        return user


class ResetPasswordSerializer(serializers.Serializer):
    password = serializers.CharField()
    token = serializers.CharField()
    uid = serializers.CharField()

    def create(self, validated_data):
        return reset_password_for_token(
            validated_data["uid"],
            validated_data["token"],
            validated_data["password"],
        )
