from io import BytesIO

from django.core.files.base import ContentFile
from PIL import Image


def test_generate_square_favicon_png_preserves_aspect_ratio():
    from app.utils.images import generate_square_favicon_png

    wide = BytesIO()
    Image.new("RGBA", (160, 40), color=(255, 0, 0, 255)).save(wide, format="PNG")
    wide.seek(0)

    png_bytes, filename = generate_square_favicon_png(wide, size=32)
    assert filename == "favicon.png"

    with Image.open(ContentFile(png_bytes)) as result:
        assert result.size == (32, 32)
        assert result.mode == "RGBA"
        assert result.getpixel((16, 0))[3] == 0
        assert result.getpixel((16, 31))[3] == 0
        assert result.getpixel((16, 16))[0] == 255
