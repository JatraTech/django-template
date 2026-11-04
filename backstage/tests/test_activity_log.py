import json

from django.contrib.admin.models import ADDITION, CHANGE, LogEntry
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.test import RequestFactory, TestCase

from backstage.dashboard.activity_labels import (
    activity_change_detail,
    activity_log_queryset,
)
from backstage.dashboard.widgets import build_recent_activity
from backstage.middleware import AdminRequestMiddleware
from backstage.models import AdminLogEntryMeta

User = get_user_model()


class ActivityLogQuerysetTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.staff = User.objects.create_user(username="staff", password="pass", is_staff=True)
        self.other = User.objects.create_user(username="other", password="pass", is_staff=True)
        self.superuser = User.objects.create_user(
            username="super",
            password="pass",
            is_staff=True,
            is_superuser=True,
        )
        ct = ContentType.objects.get_for_model(User)

        self.staff_entry = LogEntry.objects.create(
            user_id=self.staff.pk,
            content_type=ct,
            object_id=str(self.staff.pk),
            object_repr="staff row",
            action_flag=CHANGE,
            change_message=json.dumps([{"changed": {"fields": ["Email"]}}]),
        )
        self.other_entry = LogEntry.objects.create(
            user_id=self.other.pk,
            content_type=ct,
            object_id=str(self.other.pk),
            object_repr="other row",
            action_flag=CHANGE,
            change_message="Changed username.",
        )

    def _request(self, user):
        request = self.factory.get("/admin/")
        request.user = user
        return request

    def test_staff_sees_only_own_entries(self):
        qs = activity_log_queryset(self._request(self.staff))
        self.assertEqual(list(qs), [self.staff_entry])

    def test_superuser_sees_all_entries(self):
        qs = activity_log_queryset(self._request(self.superuser))
        self.assertEqual(set(qs), {self.staff_entry, self.other_entry})


class ActivityChangeDetailTests(TestCase):
    def test_uses_get_change_message(self):
        entry = LogEntry(
            change_message=json.dumps([{"changed": {"fields": ["Hero image"]}}]),
        )
        detail = activity_change_detail(entry)
        self.assertIn("Hero", detail)

    def test_plain_message_fallback(self):
        entry = LogEntry(change_message="Changed hero image.")
        self.assertEqual(activity_change_detail(entry), "Changed hero image.")


class AdminLogMetaSignalTests(TestCase):
    def test_creates_sidecar_with_ip(self):
        user = User.objects.create_user(username="editor", password="pass", is_staff=True)
        ct = ContentType.objects.get_for_model(User)
        factory = RequestFactory()
        request = factory.post("/admin/user/user/1/change/")
        request.META["REMOTE_ADDR"] = "203.0.113.10"
        request.user = user

        def create_entry(req):
            return LogEntry.objects.create(
                user_id=user.pk,
                content_type=ct,
                object_id="1",
                object_repr="User",
                action_flag=ADDITION,
            )

        middleware = AdminRequestMiddleware(create_entry)
        middleware(request)
        meta = AdminLogEntryMeta.objects.get(log_entry__user_id=user.pk)
        self.assertEqual(str(meta.ip_address), "203.0.113.10")


class BuildRecentActivityTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username="solo", password="pass", is_staff=True)
        ct = ContentType.objects.get_for_model(User)
        LogEntry.objects.create(
            user_id=self.user.pk,
            content_type=ct,
            object_id="1",
            object_repr="solo",
            action_flag=CHANGE,
            change_message=json.dumps([{"changed": {"fields": ["Title"]}}]),
        )

    def test_payload_includes_detail_and_url_name(self):
        request = self.factory.get("/admin/")
        request.user = self.user
        payload = build_recent_activity(
            request,
            {
                "recent_activity": {
                    "limit": 5,
                    "show_change_detail": True,
                    "show_ip": True,
                    "full_list_url_name": "admin:backstage_adminactivitylog_changelist",
                }
            },
        )
        self.assertEqual(len(payload["entries"]), 1)
        self.assertTrue(payload["entries"][0]["change_detail"])
        self.assertEqual(
            payload["full_list_url_name"],
            "admin:backstage_adminactivitylog_changelist",
        )
