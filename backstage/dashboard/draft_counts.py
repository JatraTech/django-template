from __future__ import annotations

from django.contrib.admin.sites import AdminSite
from django.http import HttpRequest

from backstage.dashboard.resolvers import parse_model_label, user_can_change_model
from backstage.draft.conf import is_draft_publish_enabled
from backstage.settings import get_config


def count_unpublished_drafts(request: HttpRequest, admin_site: AdminSite) -> int:
    if not is_draft_publish_enabled():
        return 0

    draft_config = get_config().get("DRAFT_PUBLISH") or {}
    model_keys = draft_config.get("models") or []
    total = 0

    for model_key in model_keys:
        try:
            model = parse_model_label(model_key)
        except LookupError:
            continue
        if not hasattr(model, "live_version"):
            continue
        if not user_can_change_model(request, admin_site, model):
            continue
        total += model.objects.filter(live_version__isnull=False).count()

    return total
