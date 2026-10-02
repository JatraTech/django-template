from django.contrib.auth import get_user_model
from django.test import SimpleTestCase, TestCase

from backstage.templatetags.backstage import _initials_from_display_name, user_initials


class InitialsFromDisplayNameTests(SimpleTestCase):
    def test_two_word_name(self):
        self.assertEqual(_initials_from_display_name("Admin User"), "AU")

    def test_single_word(self):
        self.assertEqual(_initials_from_display_name("admin"), "AD")

    def test_empty(self):
        self.assertEqual(_initials_from_display_name(""), "Y")


class UserInitialsFilterTests(TestCase):
    def test_full_name(self):
        User = get_user_model()
        user = User(username="jdoe", first_name="Jane", last_name="Doe")
        self.assertEqual(user_initials(user), "JD")

    def test_username_fallback(self):
        User = get_user_model()
        user = User(username="admin")
        self.assertEqual(user_initials(user), "AD")

    def test_none_user(self):
        self.assertEqual(user_initials(None), "Y")
