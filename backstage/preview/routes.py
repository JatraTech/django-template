from __future__ import annotations

from typing import Any

from django.utils.module_loading import import_string

from backstage.settings import get_config


def resolve_preview_route(obj: Any) -> str | None:
    callback_path = get_config().get("PREVIEW_ROUTE_CALLBACK")
    if not callback_path:
        return None

    callback = import_string(callback_path)
    return callback(obj)
