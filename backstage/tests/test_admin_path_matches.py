from django.test import RequestFactory, SimpleTestCase

from backstage.sites import BackstageAdminSite


class AdminPathMatchesTabQueryTests(SimpleTestCase):
    def setUp(self):
        self.site = BackstageAdminSite()
        self.factory = RequestFactory()

    def _matches(self, request_path: str, query_string: str, link_path: str, link_query: str) -> bool:
        url = f"{request_path}?{query_string}" if query_string else request_path
        request = self.factory.get(url)
        return self.site._admin_path_matches(
            request.path,
            link_path,
            is_tab=True,
            link_query=link_query,
            request_query=request.GET.urlencode(),
        )

    def test_tab_query_matches(self):
        self.assertTrue(
            self._matches(
                "/admin/pages/homepage/1/change/",
                "tab=seo",
                "/admin/pages/homepage/1/change/",
                "tab=seo",
            )
        )

    def test_tab_query_missing_on_request(self):
        self.assertFalse(
            self._matches(
                "/admin/pages/homepage/1/change/",
                "",
                "/admin/pages/homepage/1/change/",
                "tab=seo",
            )
        )

    def test_tab_query_wrong_value(self):
        self.assertFalse(
            self._matches(
                "/admin/pages/homepage/1/change/",
                "tab=general",
                "/admin/pages/homepage/1/change/",
                "tab=seo",
            )
        )
