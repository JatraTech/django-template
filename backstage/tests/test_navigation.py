from django.test import RequestFactory, TestCase, override_settings

from backstage.registry.navigation import get_dashboard_nav_group


class DashboardNavGroupTests(TestCase):
    def test_dashboard_nav_group_has_home_section_shape(self):
        request = RequestFactory().get("/admin/")
        group = get_dashboard_nav_group(request)
        assert group is not None
        self.assertEqual(group["id"], "dashboard")
        self.assertTrue(group["separator"])
        self.assertTrue(group["collapsible"])
        self.assertEqual(str(group["title"]), "Home")
        self.assertEqual(len(group["items"]), 1)
        self.assertEqual(str(group["items"][0]["title"]), "Dashboard")

    @override_settings(BACKSTAGE={"DASHBOARD": {"enabled": False}})
    def test_dashboard_disabled_returns_none(self):
        request = RequestFactory().get("/admin/")
        self.assertIsNone(get_dashboard_nav_group(request))
