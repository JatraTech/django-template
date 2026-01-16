from rest_framework import routers
from django.urls import path, include
from user.views import UserViewSet
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from user.views.auth import AuthViewSet

router = routers.SimpleRouter()
router.register(r"users", UserViewSet)
router.register(r"auth", AuthViewSet, basename="auth")

app_name = "user"
urlpatterns = [
    path("", include(router.urls)),
    path(
        "auth/token/",
        TokenObtainPairView.as_view(
            permission_classes=[],
            authentication_classes=[],
        ),
        name="token_obtain_pair",
    ),
    path(
        "auth/token/refresh/",
        TokenRefreshView.as_view(),
        name="token_refresh",
    ),
]
