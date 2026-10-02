from __future__ import annotations

from django.core.files.base import ContentFile

from app.utils.images import generate_square_favicon_png


def regenerate_favicon_light(settings_obj) -> bool:
    """
    Rebuild favicon_light from logo_light (letterboxed square PNG).

    Returns True when favicon_light was changed.
    """
    previous_name = settings_obj.favicon_light.name if settings_obj.favicon_light else ""

    if settings_obj.favicon_light:
        settings_obj.favicon_light.delete(save=False)
        settings_obj.favicon_light = None

    if not settings_obj.logo_light:
        return previous_name != ""

    if hasattr(settings_obj.logo_light, "open"):
        with settings_obj.logo_light.open("rb") as handle:
            png_bytes, filename = generate_square_favicon_png(handle)
    else:
        png_bytes, filename = generate_square_favicon_png(settings_obj.logo_light)

    settings_obj.favicon_light.save(filename, ContentFile(png_bytes), save=False)
    new_name = settings_obj.favicon_light.name if settings_obj.favicon_light else ""
    return new_name != previous_name
