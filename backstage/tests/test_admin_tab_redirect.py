from django.test import RequestFactory, SimpleTestCase

from backstage.admin import _backstage_tab_fragment_from_request


class BackstageTabFragmentTests(SimpleTestCase):
    def _fragment(self, data: dict[str, str]) -> str:
        request = RequestFactory().post("/", data)
        return _backstage_tab_fragment_from_request(request)

    def test_inline_tab_slug(self):
        self.assertEqual(
            self._fragment(
                {
                    "_backstage_active_tab": "website-teammembercredentialline-2",
                }
            ),
            "website-teammembercredentialline-2",
        )

    def test_general_fieldset_subtab(self):
        self.assertEqual(
            self._fragment(
                {
                    "_backstage_active_tab": "general",
                    "_backstage_active_fieldset_tab": "bio",
                    "_backstage_first_fieldset_tab": "profile",
                }
            ),
            "general--bio",
        )

    def test_general_first_fieldset_omits_hash(self):
        self.assertEqual(
            self._fragment(
                {
                    "_backstage_active_tab": "general",
                    "_backstage_active_fieldset_tab": "profile",
                    "_backstage_first_fieldset_tab": "profile",
                }
            ),
            "",
        )

    def test_rejects_unsafe_slug(self):
        self.assertEqual(
            self._fragment(
                {
                    "_backstage_active_tab": "general",
                    "_backstage_active_fieldset_tab": "bio<script>",
                }
            ),
            "",
        )
