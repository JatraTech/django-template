from django.urls import re_path, include

urlpatterns = [
    re_path(r"^v1/user/", include("user.urls", namespace="v1:users")),
]
