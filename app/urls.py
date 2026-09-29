import re
from urllib.parse import urlsplit

from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from app.admin.tinymce_upload import tinymce_upload
from app.health import liveness
from app.views import SpectacularElementsView, SpectacularRapiDocView

from .urls_api import urlpatterns as api_urls

schema_urls = [
    path(
        "api/schema/",
        SpectacularAPIView.as_view(api_version="v1"),
        name="schema",
    ),
    path(
        "",
        SpectacularRapiDocView.as_view(url_name="schema"),
        name="rapidoc-ui",
    ),
    path(
        "schema/elements/",
        SpectacularElementsView.as_view(url_name="schema"),
        name="elements",
    ),
    path(
        "schema/rapidoc/",
        SpectacularRapiDocView.as_view(url_name="schema"),
        name="rapidoc-ui",
    ),
    path(
        "schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "schema/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
]

health_urls = [
    path("healthz", liveness, name="liveness"),
]

urlpatterns = [
    *schema_urls,
    *health_urls,
    path("backstage/", include("backstage.urls")),
    path("admin/tinymce/upload/", tinymce_upload, name="tinymce_upload"),
    path("admin/", admin.site.urls),
    path("tinymce/", include("tinymce.urls")),
    path("api/", include(api_urls)),
]

if not getattr(settings, "USE_S3_STORAGE", False) and not urlsplit(settings.MEDIA_URL).netloc:
    urlpatterns += [
        re_path(
            rf"^{re.escape(settings.MEDIA_URL.lstrip('/'))}(?P<path>.*)$",
            serve,
            {"document_root": settings.MEDIA_ROOT},
        ),
    ]
