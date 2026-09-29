from django.db.models import F
from django.db.models.functions import Concat
from django.db.models.functions.text import Value
from rest_framework import decorators, parsers, response

from app.utils.mixins.views import BaseModelViewSet
from user.filters import UserFilterSet
from user.models import User
from user.serializers import (
    PartialUserCreationSerializer,
    UserImageUploadSerializer,
    UserSerializer,
)


class UserViewSet(BaseModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    serializers = {
        "upload_image": UserImageUploadSerializer,
        "create_partial_user": PartialUserCreationSerializer,
    }
    filterset_class = UserFilterSet
    ordering_fields = [
        "username",
        "user_full_name",
        "phone",
        "email",
        "dob",
        "image",
        "user_role",
        "last_login",
        "date_joined",
    ]
    ordering_field_map = {"full_name": "user_full_name", "user_role_display": "user_role"}

    def get_queryset(self):
        return super().get_queryset().annotate(user_full_name=Concat(F("first_name"), Value(" "), F("last_name")))

    @decorators.action(
        methods=["put"],
        detail=True,
        url_name="upload_image",
        url_path="upload-image",
        parser_classes=[
            parsers.MultiPartParser,
        ],
    )
    def upload_image(self, request, pk):
        serializer = self.get_serializer(data={"image": request.data.get("image"), "user": self.get_object()})
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return response.Response(
            serializer.data,
        )

    @decorators.action(
        methods=["get"],
        detail=False,
        url_name="me",
        url_path="me",
    )
    def me(self, request, *args, **kwargs):
        serializer = self.get_serializer(request.user)
        return response.Response(serializer.data)

    @decorators.action(
        methods=["post"],
        detail=False,
        url_path="partial-registration",
        permission_classes=[],
        authentication_classes=[],
    )
    def create_partial_user(self, request, *args, **kwargs):
        return super().create(request)
