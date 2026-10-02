from unittest.mock import patch

from django.test import TestCase, override_settings

from backstage.branding import resolve_sidebar_text, resolve_text
from backstage.models import BackstageSettings
from backstage.services import clear_backstage_settings_cache, ensure_backstage_settings


class ResolveSidebarTextTests(TestCase):
    def setUp(self):
        clear_backstage_settings_cache()

    def _update_settings(self, **fields) -> BackstageSettings:
        obj = BackstageSettings.objects.get(pk=1)
        for name, value in fields.items():
            setattr(obj, name, value)
        obj.save(update_fields=list(fields.keys()))
        clear_backstage_settings_cache()
        return obj

    @override_settings(
        BACKSTAGE={
            "SITE_HEADER": "Config Header",
            "SITE_SUBHEADER": "Config Subheader",
        }
    )
    def test_empty_db_fields_return_empty_without_config_fallback(self):
        self._update_settings(site_header="", site_subheader="")
        self.assertEqual(resolve_sidebar_text("site_header", "SITE_HEADER"), "")
        self.assertEqual(resolve_sidebar_text("site_subheader", "SITE_SUBHEADER"), "")

    @override_settings(
        BACKSTAGE={
            "SITE_HEADER": "Config Header",
            "SITE_SUBHEADER": "Config Subheader",
        }
    )
    def test_db_values_used_when_set(self):
        self._update_settings(site_header="My Header", site_subheader="My Subheader")
        self.assertEqual(resolve_sidebar_text("site_header", "SITE_HEADER"), "My Header")
        self.assertEqual(resolve_sidebar_text("site_subheader", "SITE_SUBHEADER"), "My Subheader")

    @override_settings(
        BACKSTAGE={
            "SITE_HEADER": "Config Header",
            "SITE_SUBHEADER": "Config Subheader",
        }
    )
    @patch("backstage.branding.get_backstage_settings_or_none", return_value=None)
    def test_no_settings_row_falls_back_to_config(self, _mock_settings):
        self.assertEqual(resolve_sidebar_text("site_header", "SITE_HEADER"), "Config Header")
        self.assertEqual(resolve_sidebar_text("site_subheader", "SITE_SUBHEADER"), "Config Subheader")

    @patch("backstage.branding.get_backstage_settings_or_none", return_value=None)
    @patch("backstage.branding._backstage_value", return_value=None)
    def test_no_settings_and_no_config_falls_back_to_defaults(self, _mock_config, _mock_settings):
        self.assertEqual(resolve_sidebar_text("site_header", "SITE_HEADER"), "Admin")
        self.assertEqual(resolve_sidebar_text("site_subheader", "SITE_SUBHEADER"), "Content management")

    @override_settings(
        BACKSTAGE={
            "SITE_TITLE": "Config Title",
            "SITE_HEADER": "Config Header",
        }
    )
    def test_empty_db_site_title_returns_empty_without_config_fallback(self):
        self._update_settings(site_title="")
        self.assertEqual(resolve_text("site_title", "SITE_TITLE"), "")

    @override_settings(
        BACKSTAGE={
            "SITE_TITLE": "Seeded Title",
            "SITE_HEADER": "Seeded Header",
            "SITE_SUBHEADER": "Seeded Subheader",
        }
    )
    def test_ensure_backstage_settings_seeds_branding_on_create(self):
        BackstageSettings.objects.filter(pk=1).delete()
        clear_backstage_settings_cache()
        obj = ensure_backstage_settings()
        self.assertEqual(obj.site_title, "Seeded Title")
        self.assertEqual(obj.site_header, "Seeded Header")
        self.assertEqual(obj.site_subheader, "Seeded Subheader")


class ResolveFaviconsTests(TestCase):
    def setUp(self):
        clear_backstage_settings_cache()
        ensure_backstage_settings()

    def test_resolve_favicons_uses_letterboxed_favicon_not_full_logo(self):
        from io import BytesIO

        from django.core.files.uploadedfile import SimpleUploadedFile
        from PIL import Image

        from backstage.branding import resolve_favicons

        png = BytesIO()
        Image.new("RGBA", (200, 50), color=(0, 128, 255, 255)).save(png, format="PNG")
        logo_file = SimpleUploadedFile("wide-logo.png", png.getvalue(), content_type="image/png")

        obj = BackstageSettings.objects.get(pk=1)
        if obj.favicon_light:
            obj.favicon_light.delete(save=False)
        obj.logo_light = logo_file
        obj.save()
        obj.refresh_from_db()
        clear_backstage_settings_cache()

        self.assertTrue(obj.favicon_light.name)
        favicons = resolve_favicons()
        self.assertIsNotNone(favicons)
        self.assertEqual(len(favicons), 1)
        self.assertEqual(favicons[0]["type"], "image/png")
        self.assertEqual(favicons[0]["sizes"], "32x32")
        self.assertEqual(favicons[0]["href"], obj.favicon_light.url)
        self.assertNotEqual(favicons[0]["href"], obj.logo_light.url)
