import json

from django.contrib.admin.models import ADDITION, CHANGE, DELETION, LogEntry
from django.test import TestCase

from backstage.dashboard.activity_labels import (
    human_activity_title,
    parse_inline_objects,
)


class ParseInlineObjectsTests(TestCase):
    def test_parses_changed_inline_object(self):
        message = json.dumps(
            [
                {
                    "changed": {
                        "name": "webcast",
                        "object": "Q3 earnings webcast",
                        "fields": ["Title"],
                    }
                }
            ]
        )
        self.assertEqual(parse_inline_objects(message), ["Q3 earnings webcast"])

    def test_non_json_returns_empty(self):
        self.assertEqual(parse_inline_objects("Changed title."), [])


class HumanActivityTitleTests(TestCase):
    def _entry(self, **kwargs) -> LogEntry:
        defaults = {
            "object_repr": "Investors page",
            "action_flag": CHANGE,
            "change_message": "",
        }
        defaults.update(kwargs)
        return LogEntry(**defaults)

    def test_inline_change_uses_child_object_name(self):
        message = json.dumps(
            [
                {
                    "changed": {
                        "name": "webcast",
                        "object": "Q3 earnings webcast",
                        "fields": ["Title"],
                    }
                }
            ]
        )
        entry = self._entry(change_message=message)
        self.assertEqual(str(human_activity_title(entry)), "Updated Q3 earnings webcast")

    def test_parent_only_change(self):
        message = json.dumps([{"changed": {"fields": ["Hero image"]}}])
        entry = self._entry(change_message=message)
        self.assertEqual(str(human_activity_title(entry)), "Updated Investors page")

    def test_plain_change_message_fallback(self):
        entry = self._entry(change_message="Changed hero image.")
        self.assertEqual(str(human_activity_title(entry)), "Updated Investors page")

    def test_addition_and_deletion(self):
        add = self._entry(object_repr="Press release", action_flag=ADDITION)
        delete = self._entry(object_repr="Press release", action_flag=DELETION)
        self.assertEqual(str(human_activity_title(add)), "Added Press release")
        self.assertEqual(str(human_activity_title(delete)), "Removed Press release")
