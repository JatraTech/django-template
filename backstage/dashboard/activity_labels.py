from __future__ import annotations

import json

from django.contrib.admin.models import LogEntry
from django.utils.translation import gettext_lazy as _


def parse_inline_objects(change_message: str) -> list[str]:
    if not change_message or not change_message.startswith("["):
        return []
    try:
        payload = json.loads(change_message)
    except json.JSONDecodeError:
        return []
    if not isinstance(payload, list):
        return []
    objects: list[str] = []
    for sub_message in payload:
        if not isinstance(sub_message, dict):
            continue
        for key in ("added", "changed", "deleted"):
            block = sub_message.get(key)
            if not isinstance(block, dict):
                continue
            obj = block.get("object")
            if obj:
                objects.append(str(obj))
    return objects


def human_activity_title(entry: LogEntry) -> str:
    parent_repr = entry.object_repr or ""
    inline_objects = parse_inline_objects(entry.change_message or "")

    if inline_objects:
        unique = list(dict.fromkeys(inline_objects))
        if len(unique) == 1:
            return _("Updated {name}").format(name=unique[0])
        if parent_repr:
            return _("Updated {count} items on {parent}").format(
                count=len(unique),
                parent=parent_repr,
            )
        return _("Updated {count} items").format(count=len(unique))

    if entry.is_addition():
        return _("Added {name}").format(name=parent_repr)
    if entry.is_deletion():
        return _("Removed {name}").format(name=parent_repr)
    return _("Updated {name}").format(name=parent_repr)


def activity_context_label(entry: LogEntry, inline_objects: list[str]) -> str:
    if not inline_objects:
        return ""
    parent_repr = (entry.object_repr or "").strip()
    if not parent_repr:
        return ""
    unique = list(dict.fromkeys(inline_objects))
    if len(unique) == 1 and unique[0] == parent_repr:
        return ""
    return parent_repr
