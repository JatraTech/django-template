"""Copy into your CMS app (e.g. cms/utils.py). Not imported by Backstage.

For routine FileField/ImageField output in serializers, prefer ``get_image_url`` from
``app.utils.mixins.serializers``. Use the helpers below when you need ``BACKEND_URL``
fallbacks without a request (management commands, seeds) or CharField seed paths.
"""

from django.conf import settings
from django.db import models


def get_singleton(
    model_class: type[models.Model],
    *,
    prefetch_related: tuple[str, ...] = (),
) -> models.Model:
    """Load or create the singleton row (pk=1) for a ``SingletonModel`` page.

    Pass the **model class** (e.g. ``AboutPage``), not a queryset. Wrong::

        get_singleton(AboutPage.objects.prefetch_related("items"))  # AttributeError

    Right::

        get_singleton(AboutPage, prefetch_related=("items",))
    """
    obj, _ = model_class.objects.get_or_create(pk=1)
    if prefetch_related:
        return model_class.objects.prefetch_related(*prefetch_related).get(pk=obj.pk)
    return obj


def absolute_file_url(request, field) -> str | None:
    """Absolute URL for a Django FileField/ImageField value."""
    if not field:
        return None
    name = getattr(field, "name", None)
    if not name:
        return None
    url = field.url
    if request is not None:
        return request.build_absolute_uri(url)
    base = settings.BACKEND_URL.rstrip("/")
    return f"{base}{url}" if url.startswith("/") else url


def public_media_url(request, relative_path: str | None) -> str | None:
    """Turn a seed-relative image path into a public media URL on the API host."""
    if not relative_path:
        return None
    if relative_path.startswith(("http://", "https://")):
        return relative_path
    path = relative_path.replace("assets/images/", "").lstrip("/")
    if request is not None:
        return request.build_absolute_uri(f"/media/images/{path}")
    base = settings.BACKEND_URL.rstrip("/")
    return f"{base}/media/images/{path}"
