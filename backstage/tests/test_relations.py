from django.test import SimpleTestCase

from backstage.registry.relations import RELATION_MODES, compile_inline_relations, validate_relation_entry


class InlineRelationsValidationTests(SimpleTestCase):
    def test_invalid_mode(self):
        errors = validate_relation_entry(
            {"parent": "PressReleasesPage", "child": "PressRelease", "mode": "invalid"},
        )
        self.assertTrue(any("Invalid mode" in e for e in errors))

    def test_requires_parent_child(self):
        errors = validate_relation_entry({"mode": "hub_tabular"})
        self.assertTrue(any("parent" in e for e in errors))

    def test_relation_modes_frozen(self):
        self.assertIn("hub_tabular", RELATION_MODES)


class CompileInlineRelationsTests(SimpleTestCase):
    def test_empty_entries(self):
        compiled = compile_inline_relations([])
        self.assertEqual(compiled.standalone_child_models, [])
        self.assertEqual(compiled.admin_overrides_patch, {})
