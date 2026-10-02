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
