from rest_framework import decorators, response
from rest_framework.viewsets import GenericViewSet

from user.serializers.auth import (
    ResetPasswordSerializer,
    SendResetPasswordEmailSerializer,
)


class AuthViewSet(GenericViewSet):
    @decorators.action(
        methods=["post"],
        detail=False,
        url_path="send-reset-password-email",
        url_name="send-reset-password-email",
        serializer_class=SendResetPasswordEmailSerializer,
        permission_classes=[],
        authentication_classes=[],
    )
    def send_reset_password_email(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response({"message": "Reset password email request received successfully."})

    @decorators.action(
        methods=["post"],
        detail=False,
        url_path="reset-password",
        url_name="reset-password",
        serializer_class=ResetPasswordSerializer,
        permission_classes=[],
        authentication_classes=[],
    )
    def reset_password(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response({"message": "Password reset successfully."})
