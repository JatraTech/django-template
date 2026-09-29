from decimal import Decimal
from pathlib import Path
from typing import Any

from django.db.models import DecimalField, ImageField
from django.db.models.fields.files import ImageFieldFile

from app.utils.images import optimize_image_content


class OptimizedImageFieldFile(ImageFieldFile):
    """ImageFieldFile that converts uploads to optimized WebP on save."""

    def save(self, name, content, save=True):
        if name and not str(name).lower().endswith(".webp"):
            content, name = optimize_image_content(content, Path(str(name)).name)
        return super().save(name, content, save=save)


class OptimizedImageField(ImageField):
    """ImageField that auto-optimizes uploads to WebP (skips existing .webp)."""

    attr_class = OptimizedImageFieldFile

    def deconstruct(self):
        name, _path, args, kwargs = super().deconstruct()
        # Report as ImageField so no AlterField migrations are needed.
        return name, "django.db.models.ImageField", args, kwargs


class MoneyField(DecimalField):
    def __init__(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        kwargs["decimal_places"] = kwargs.pop("decimal_places", 2)
        kwargs["max_digits"] = kwargs.pop("max_digits", 10)
        kwargs["default"] = kwargs.pop("default", Decimal(0))
        super().__init__(*args, **kwargs)
