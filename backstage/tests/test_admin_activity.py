from django.contrib.admin.models import ADDITION, CHANGE, DELETION, LogEntry
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.test import RequestFactory, TestCase

from django.contrib import admin

from backstage.admin_activity import AdminActivityLogAdmin, LogEntryActionFilter
from backstage.dashboard.activity_labels import activity_action_label
from backstage.models import AdminActivityLog

User = get_user_model()


class ActivityActionLabelTests(TestCase):
    def test_labels_for_flags(self):
        self.assertEqual(str(activity_action_label(LogEntry(action_flag=ADDITION))), "Added")
        self.assertEqual(str(activity_action_label(LogEntry(action_flag=CHANGE))), "Changed")
        self.assertEqual(str(activity_action_label(LogEntry(action_flag=DELETION))), "Deleted")


class AdminActivityLogAdminTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.admin = AdminActivityLogAdmin(AdminActivityLog, admin.site)
        self.staff = User.objects.create_user(username="staff", password="pass", is_staff=True)
        self.other = User.objects.create_user(username="other", password="pass", is_staff=True)
        ct = ContentType.objects.get_for_model(User)
        self.own = LogEntry.objects.create(
            user_id=self.staff.pk,
            content_type=ct,
            object_id="1",
            object_repr="mine",
            action_flag=1,
        )
        self.foreign = LogEntry.objects.create(
            user_id=self.other.pk,
            content_type=ct,
            object_id="2",
            object_repr="theirs",
            action_flag=1,
        )

    def test_read_only_permissions(self):
        request = self.factory.get("/admin/")
        request.user = self.staff
        self.assertFalse(self.admin.has_add_permission(request))
        self.assertFalse(self.admin.has_change_permission(request))
        self.assertFalse(self.admin.has_delete_permission(request))

    def test_queryset_scoped_for_staff(self):
        request = self.factory.get("/admin/")
        request.user = self.staff
        qs = self.admin.get_queryset(request)
        self.assertEqual(list(qs), [self.own])

    def test_superuser_list_filter_includes_user(self):
        request = self.factory.get("/admin/")
        request.user = User.objects.create_superuser(username="root", password="pass")
        filters = self.admin.get_list_filter(request)
        self.assertIn("user", filters)
        self.assertIn(LogEntryActionFilter, filters)

    def test_object_link_display_when_admin_url_exists(self):
        request = self.factory.get("/admin/")
        request.user = self.staff
        html = self.admin.object_link_display(self.own)
        self.assertIn("Open", str(html))
        self.assertIn(f"/admin/user/user/{self.own.object_id}/change/", str(html))

    def test_action_filter_narrows_queryset(self):
        request = self.factory.get("/admin/")
        request.user = self.staff
        change_entry = LogEntry.objects.create(
            user_id=self.staff.pk,
            content_type=ContentType.objects.get_for_model(User),
            object_id="3",
            object_repr="changed",
            action_flag=CHANGE,
        )
        base_qs = self.admin.get_queryset(request)
        filt = LogEntryActionFilter(request, {"action_flag": str(CHANGE)}, AdminActivityLog, self.admin)
        filtered = filt.queryset(request, base_qs)
        self.assertEqual(list(filtered), [change_entry])
