from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from django.apps import apps
from django.db import models
from django.utils.module_loading import import_string

RELATION_MODES = frozenset(
    {
        "default_stacked",
        "default_tabular",
        "hub_tabular",
        "hub_stacked",
    }
)

MODE_BASE_CLASS = {
    "default_stacked": "backstage.registry.base.BackstageStackedInline",
    "default_tabular": "backstage.registry.base.BackstageTabularInline",
    "hub_tabular": "backstage.registry.base.BackstageHubTabularInline",
    "hub_stacked": "backstage.registry.base.BackstageHubStackedInline",
}


@dataclass
class CompiledRelations:
    standalone_child_models: list[str] = field(default_factory=list)
    admin_overrides_patch: dict[str, dict[str, Any]] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)


def _model_by_name(name: str) -> type[models.Model] | None:
    name = str(name).strip()
    if not name:
        return None
    if "." in name:
        app_label, model_name = name.split(".", 1)
        try:
            return apps.get_model(app_label, model_name)
        except LookupError:
            return None
    for model in apps.get_models():
        if model.__name__ == name:
            return model
    return None


def _fk_to_parent(child_model: type[models.Model], parent_model: type[models.Model], fk_name: str | None) -> str:
    if fk_name:
        return fk_name
    matches: list[str] = []
    for field in child_model._meta.get_fields():
        if not isinstance(field, models.ForeignKey) or field.auto_created:
            continue
        if field.remote_field.model is parent_model:
            matches.append(field.name)
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        raise ValueError(
            f"Ambiguous FK from {child_model.__name__} to {parent_model.__name__}: {matches}. Set 'fk' in INLINE_RELATIONS."
        )
    raise ValueError(f"No FK from {child_model.__name__} to {parent_model.__name__}.")


def validate_relation_entry(entry: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not isinstance(entry, dict):
        return ["INLINE_RELATIONS entry must be a dict."]
    parent_name = entry.get("parent")
    child_name = entry.get("child")
    mode = entry.get("mode", "default_stacked")
    if not parent_name or not child_name:
        errors.append("INLINE_RELATIONS entry requires 'parent' and 'child'.")
        return errors
    if mode not in RELATION_MODES:
        errors.append(f"Invalid mode '{mode}' for {parent_name} → {child_name}.")
    parent = _model_by_name(str(parent_name))
    child = _model_by_name(str(child_name))
    if parent is None:
        errors.append(f"Unknown parent model '{parent_name}'.")
    if child is None:
        errors.append(f"Unknown child model '{child_name}'.")
    if parent is not None and child is not None:
        try:
            _fk_to_parent(child, parent, entry.get("fk"))
        except ValueError as exc:
            errors.append(str(exc))
    return errors


def build_inline_class(
    parent_model: type[models.Model],
    child_model: type[models.Model],
    entry: dict[str, Any],
) -> type:
    inline_path = entry.get("inline_class")
    if inline_path:
        return import_string(str(inline_path))

    mode = str(entry.get("mode", "default_stacked"))
    base = import_string(MODE_BASE_CLASS[mode])
    fk_name = _fk_to_parent(child_model, parent_model, entry.get("fk"))
    class_name = f"{child_model.__name__}{parent_model.__name__}RelationInline"

    attrs: dict[str, Any] = {
        "model": child_model,
        "fk_name": fk_name,
        "extra": 0,
    }
    if entry.get("fields"):
        attrs["fields"] = tuple(entry["fields"])
    if entry.get("ordering"):
        attrs["ordering"] = tuple(entry["ordering"])
    if mode.startswith("hub"):
        if entry.get("help_text"):
            attrs["hub_help_text"] = entry["help_text"]
        if entry.get("add_label"):
            attrs["hub_add_label"] = entry["add_label"]
        if entry.get("changelist_label"):
            attrs["hub_changelist_label"] = entry["changelist_label"]
        if entry.get("primary_tab") is False:
            attrs["hub_primary_tab"] = False

    return type(class_name, (base,), attrs)


def _default_inlines_for_parent(
    parent_model: type[models.Model],
    skip_child_names: frozenset[str],
) -> list[type]:
    from backstage.draft.conf import is_draft_publish_model
    from backstage.registry.factory import _make_inline_admin

    inlines: list[type] = []
    for relation in parent_model._meta.get_fields():
        if not (relation.one_to_many and relation.auto_created and not relation.concrete):
            continue
        inline_model = relation.related_model
        if not inline_model._meta.managed or inline_model._meta.abstract:
            continue
        if inline_model.__name__ in skip_child_names:
            continue
        fk_name = relation.field.name
        if is_draft_publish_model(parent_model) and relation.get_accessor_name() == "draft_copies":
            continue
        inlines.append(_make_inline_admin(inline_model, fk_name))
    return inlines


def _relation_key(parent_name: str, child_name: str) -> tuple[str, str]:
    return (str(parent_name), str(child_name))


def compile_inline_relations(
    entries: list[dict[str, Any]],
    backstage_config: dict[str, Any] | None = None,
) -> CompiledRelations:
    backstage_config = backstage_config or {}
    result = CompiledRelations()
    inline_hub = backstage_config.get("INLINE_HUB") or {}
    hub_keys = {
        _relation_key(parent, child)
        for parent, children in inline_hub.items()
        if isinstance(children, dict)
        for child in children
    }

    by_parent: dict[str, list[dict[str, Any]]] = {}
    for entry in entries:
        errors = validate_relation_entry(entry)
        if errors:
            result.warnings.extend(errors)
            continue
        parent_name = str(entry["parent"])
        child_name = str(entry["child"])
        key = _relation_key(parent_name, child_name)
        if key in hub_keys:
            result.warnings.append(
                f'INLINE_RELATIONS {parent_name} → {child_name} shadows INLINE_HUB; prefer INLINE_RELATIONS only.',
            )
        by_parent.setdefault(parent_name, []).append(entry)

    for parent_name, parent_entries in by_parent.items():
        parent_model = _model_by_name(parent_name)
        if parent_model is None:
            continue
        configured_children = frozenset(str(e["child"]) for e in parent_entries)
        inline_classes: list[type] = []
        for entry in parent_entries:
            child_model = _model_by_name(str(entry["child"]))
            if child_model is None:
                continue
            inline_classes.append(build_inline_class(parent_model, child_model, entry))
            if entry.get("standalone_child"):
                if child_model.__name__ not in result.standalone_child_models:
                    result.standalone_child_models.append(child_model.__name__)
            if entry.get("hide_parent_fk_on_child"):
                fk = _fk_to_parent(child_model, parent_model, entry.get("fk"))
                child_patch = result.admin_overrides_patch.setdefault(child_model.__name__, {})
                exclude = child_patch.get("exclude") or ()
                if isinstance(exclude, str):
                    exclude = (exclude,)
                child_patch["exclude"] = tuple(dict.fromkeys((*exclude, fk)))

        inline_classes.extend(_default_inlines_for_parent(parent_model, configured_children))
        parent_patch = result.admin_overrides_patch.setdefault(parent_model.__name__, {})
        parent_patch["inlines"] = inline_classes

    return result


def apply_compiled_relations_to_settings(settings: Any) -> list[str]:
    backstage = getattr(settings, "BACKSTAGE", None)
    if not isinstance(backstage, dict):
        return []

    entries = backstage.get("INLINE_RELATIONS") or []
    if not entries:
        return []

    compiled = compile_inline_relations(entries, backstage)

    standalone = list(backstage.get("STANDALONE_CHILD_MODELS") or [])
    for name in compiled.standalone_child_models:
        if name not in standalone:
            standalone.append(name)
    backstage["STANDALONE_CHILD_MODELS"] = standalone

    admin_overrides = backstage.setdefault("ADMIN_OVERRIDES", {})
    for model_name, patch in compiled.admin_overrides_patch.items():
        target = admin_overrides.setdefault(model_name, {})
        for key, value in patch.items():
            target[key] = value

    return compiled.warnings
