from django.contrib import admin
from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase, override_settings

from backstage.dashboard.context import build_dashboard_context
from backstage.dashboard.draft_counts import count_unpublished_drafts
from backstage.dashboard.widgets import build_charts, build_stats


class DraftCountsTests(TestCase):
    def setUp(self):
        self.request = RequestFactory().get("/admin/")
        User = get_user_model()
        self.request.user = User.objects.create_superuser(
            username="draftadmin",
            email="draft@example.com",
            password="testpass123",
        )

    def test_count_unpublished_drafts_disabled(self):
        self.assertEqual(count_unpublished_drafts(self.request, admin.site), 0)

    @override_settings(
        BACKSTAGE={
            "DRAFT_PUBLISH": {"enabled": True, "models": []},
        }
    )
    def test_count_unpublished_drafts_enabled_no_models(self):
        self.assertEqual(count_unpublished_drafts(self.request, admin.site), 0)


class DashboardDraftPublishSpecTests(TestCase):
    def setUp(self):
        self.request = RequestFactory().get("/admin/")
        User = get_user_model()
        self.request.user = User.objects.create_superuser(
            username="dashadmin",
            email="dash@example.com",
            password="testpass123",
        )

    @override_settings(
        BACKSTAGE={
            "DRAFT_PUBLISH": {"enabled": False, "models": []},
        }
    )
    def test_build_stats_skips_if_draft_publish_when_disabled(self):
        config = {
            "stats": [
                {
                    "id": "drafts",
                    "label": "Drafts",
                    "count_callback": "backstage.dashboard.draft_counts.count_unpublished_drafts",
                    "if_draft_publish": True,
                }
            ]
        }
        cards = build_stats(self.request, admin.site, config)
        self.assertEqual(cards, [])

    @override_settings(
        BACKSTAGE={
            "DRAFT_PUBLISH": {"enabled": True, "models": []},
        }
    )
    def test_build_stats_includes_if_draft_publish_when_enabled(self):
        config = {
            "stats": [
                {
                    "id": "drafts",
                    "label": "Drafts",
                    "icon": "edit_note",
                    "count_callback": "backstage.dashboard.draft_counts.count_unpublished_drafts",
                    "if_draft_publish": True,
                }
            ]
        }
        cards = build_stats(self.request, admin.site, config)
        self.assertEqual(len(cards), 1)
        self.assertEqual(cards[0]["count"], 0)
        self.assertEqual(cards[0]["label"], "Drafts")

    def test_build_charts_skips_draft_segment_when_disabled(self):
        from website.models import NewsletterSubscription

        NewsletterSubscription.objects.create(email="chart@example.com", source="test")
        config = {
            "charts": [
                {
                    "id": "mix",
                    "title": "Mix",
                    "segments": [
                        {
                            "label": "Newsletter",
                            "model": "website.newslettersubscription",
                            "accent": "green",
                        },
                        {
                            "label": "Drafts",
                            "count_callback": "backstage.dashboard.draft_counts.count_unpublished_drafts",
                            "accent": "slate",
                            "if_draft_publish": True,
                        },
                    ],
                }
            ]
        }
        charts = build_charts(self.request, admin.site, config)
        self.assertEqual(len(charts), 1)
        import json

        payload = json.loads(charts[0]["data_json"])
        self.assertEqual(payload["labels"], ["Newsletter"])

    @override_settings(
        BACKSTAGE={
            "DRAFT_PUBLISH": {"enabled": True, "models": []},
        }
    )
    def test_build_charts_includes_draft_segment_when_enabled(self):
        from website.models import NewsletterSubscription

        NewsletterSubscription.objects.create(email="chart2@example.com", source="test")
        config = {
            "charts": [
                {
                    "id": "mix",
                    "title": "Mix",
                    "segments": [
                        {
                            "label": "Newsletter",
                            "model": "website.newslettersubscription",
                            "accent": "green",
                        },
                        {
                            "label": "Drafts",
                            "count_callback": "backstage.dashboard.draft_counts.count_unpublished_drafts",
                            "accent": "slate",
                            "if_draft_publish": True,
                        },
                    ],
                }
            ]
        }
        charts = build_charts(self.request, admin.site, config)
        self.assertEqual(len(charts), 1)
        import json

        chart = charts[0]
        self.assertEqual(chart["total"], 1)
        self.assertEqual(len(chart["legend"]), 2)
        self.assertEqual(chart["legend"][1]["label"], "Drafts")
        self.assertEqual(chart["legend"][1]["count"], 0)
        payload = json.loads(chart["data_json"])
        self.assertEqual(payload["labels"], ["Newsletter"])
        self.assertEqual(payload["datasets"][0]["data"], [1])


class DashboardLayoutDraftTests(TestCase):
    @override_settings(
        BACKSTAGE={
            "DRAFT_PUBLISH": {"enabled": True, "models": []},
            "DASHBOARD": {"layout": ["quick_actions", "charts", "recent_activity"]},
        }
    )
    def test_my_drafts_inserted_after_charts_when_draft_enabled(self):
        request = RequestFactory().get("/admin/")
        User = get_user_model()
        request.user = User.objects.create_superuser(
            username="layoutadmin",
            email="layout@example.com",
            password="testpass123",
        )
        ctx = build_dashboard_context(request, admin.site, {})
        layout = ctx["dashboard_layout"]
        self.assertEqual(layout[layout.index("charts") + 1], "my_drafts")
