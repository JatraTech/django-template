from django.urls import include, re_path

urlpatterns = [
    re_path(r"^v1/user/", include("user.urls", namespace="v1:users")),
]
