"""
URL configuration for app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path, re_path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from app.views import SpectacularElementsView, SpectacularRapiDocView
from .urls_api import urlpatterns as api_urls
from django.conf import settings
from django.conf.urls.static import static

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
urls = [
    path("admin/", admin.site.urls),
    re_path(r"^api/", include(api_urls)),
]

urlpatterns = schema_urls + urls
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
