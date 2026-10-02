from __future__ import annotations

from typing import Any

from django.db import models

from backstage.conf import get_inline_hub_options
from backstage.contrib.inlines.hub import HUB_INLINE_AFTER_TEMPLATE, HubInlineMixin


def apply_inline_hub_config(inline_cls: type, parent_model: type[models.Model]) -> type:
    """Merge BACKSTAGE INLINE_HUB options onto an inline class (returns same class, mutated)."""
    child_model = getattr(inline_cls, "model", None)
    if child_model is None:
        return inline_cls

    options = get_inline_hub_options(parent_model, child_model)
    is_hub = getattr(inline_cls, "inline_mode", "default") == "hub"

    if not options and not is_hub:
        return inline_cls

    if not is_hub and not issubclass(inline_cls, HubInlineMixin):
        return inline_cls

    fields = options.get("fields")
    if fields:
        inline_cls.hub_fields = tuple(fields)
        if not getattr(inline_cls, "fields", None):
            inline_cls.fields = tuple(fields)

    if options.get("help_text"):
        inline_cls.hub_help_text = options["help_text"]
    if options.get("add_label"):
        inline_cls.hub_add_label = options["add_label"]
    if options.get("changelist_label"):
        inline_cls.hub_changelist_label = options["changelist_label"]
    if options.get("template_after"):
        inline_cls.template_after = options["template_after"]
    elif getattr(inline_cls, "inline_mode", "default") == "hub" and not getattr(inline_cls, "template_after", None):
        inline_cls.template_after = HUB_INLINE_AFTER_TEMPLATE

    if inline_cls.inline_mode == "hub" and issubclass(inline_cls, HubInlineMixin):
        if hasattr(inline_cls, "hub_show_title"):
            inline_cls.show_title = inline_cls.hub_show_title

    return inline_cls


def finalize_parent_inlines(admin_class: type, parent_model: type[models.Model]) -> None:
    inlines = list(getattr(admin_class, "inlines", []) or [])
    if not inlines:
        return
    admin_class.inlines = [apply_inline_hub_config(inline, parent_model) for inline in inlines]
