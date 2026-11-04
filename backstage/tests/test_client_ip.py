from django.test import RequestFactory, TestCase, override_settings

from backstage.client_ip import client_ip_from, trusted_proxy_count
from backstage.middleware import AdminRequestMiddleware, get_current_request


class ClientIpTests(TestCase):
    def test_first_hop_when_proxies_unset(self):
        self.assertEqual(
            client_ip_from("203.0.113.1, 10.0.0.1", "127.0.0.1", None),
            "203.0.113.1",
        )

    def test_remote_only_when_proxies_zero(self):
        self.assertEqual(client_ip_from("203.0.113.1, 10.0.0.1", "127.0.0.1", 0), "127.0.0.1")

    def test_trusted_proxy_from_right(self):
        self.assertEqual(
            client_ip_from("spoof, 203.0.113.5, 10.0.0.2", "127.0.0.1", 2),
            "203.0.113.5",
        )

    @override_settings(BACKSTAGE={"TRUSTED_PROXY_COUNT": 1})
    def test_trusted_proxy_count_from_settings(self):
        self.assertEqual(trusted_proxy_count(), 1)


class AdminRequestMiddlewareTests(TestCase):
    def test_sets_and_clears_request(self):
        factory = RequestFactory()
        request = factory.get("/admin/")
        seen = []

        def get_response(req):
            seen.append(get_current_request())
            return None

        middleware = AdminRequestMiddleware(get_response)
        middleware(request)
        self.assertIs(seen[0], request)
        self.assertIsNone(get_current_request())
