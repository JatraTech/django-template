"""Letterboxed PNG favicons for Backstage admin branding."""

from __future__ import annotations

import io
from pathlib import Path
from typing import BinaryIO

from PIL import Image, ImageOps

FileSource = Path | str | BinaryIO


def _normalize_mode(img: Image.Image) -> Image.Image:
    """Convert to RGB or RGBA, preserving alpha for logos/transparent assets."""
    if img.mode in ("RGBA", "LA"):
        return img.convert("RGBA")
    if img.mode == "P":
        return img.convert("RGBA") if "transparency" in img.info else img.convert("RGB")
    if img.mode != "RGB":
        return img.convert("RGB")
    return img


def generate_square_favicon_png(
    source: FileSource,
    *,
    size: int = 32,
) -> tuple[bytes, str]:
    """
    Letterbox source image into a square PNG (aspect ratio preserved).

    Scales down to fit within size×size, centers on a transparent canvas.
    """
    if hasattr(source, "seek"):
        try:
            source.seek(0)
        except (OSError, io.UnsupportedOperation):
            pass

    with Image.open(source) as img:
        img = ImageOps.exif_transpose(img)
        img = _normalize_mode(img)
        img.thumbnail((size, size), Image.Resampling.LANCZOS)

        canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        offset_x = (size - img.width) // 2
        offset_y = (size - img.height) // 2
        if img.mode == "RGBA":
            canvas.paste(img, (offset_x, offset_y), img)
        else:
            canvas.paste(img, (offset_x, offset_y))

        buffer = io.BytesIO()
        canvas.save(buffer, format="PNG")
        return buffer.getvalue(), "favicon.png"
