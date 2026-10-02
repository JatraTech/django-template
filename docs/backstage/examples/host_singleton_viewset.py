"""Copy into your CMS app views. Not imported by Backstage.

Pair with [host_cms_api_utils.py](host_cms_api_utils.py) and [host_singleton.py](host_singleton.py).
"""

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

# from yourapp.models import AboutPage, SiteSettings
# from yourapp.serializers import AboutPageSerializer, SiteSettingsSerializer
# from yourapp.utils import get_singleton


class AboutPageViewSet(ViewSet):
    permission_classes = [AllowAny]
    http_method_names = ["get"]

    def list(self, request, *args, **kwargs):
        page = get_singleton(AboutPage)
        serializer = AboutPageSerializer(page, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class SiteSettingsViewSet(ViewSet):
    """Prefetch when ``to_representation`` calls ``instance.related_set.all()``."""

    permission_classes = [AllowAny]
    http_method_names = ["get"]

    def list(self, request, *args, **kwargs):
        settings_obj = get_singleton(
            SiteSettings,
            prefetch_related=("social_links", "nav_items"),
        )
        serializer = SiteSettingsSerializer(settings_obj, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)
