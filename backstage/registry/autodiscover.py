from __future__ import annotations

from django.apps import apps
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission

from backstage.conf import get_skip_app_labels
from backstage.models import BackstageSettings
from backstage.registry.factory import _is_inline_only_model, build_admin_class


def should_skip_model(model: type) -> bool:
    if model._meta.abstract or not model._meta.managed:
        return True
    if model is BackstageSettings:
        return True
    if model is Permission:
        return True
    if model._meta.app_label in get_skip_app_labels():
        return True
    if model._meta.proxy:
        return True
    if _is_inline_only_model(model):
        return True
    return False


def register_all_models() -> None:
    user_model = get_user_model()
    for model in apps.get_models():
        if should_skip_model(model):
            if _is_inline_only_model(model) and model in admin.site._registry:
                admin.site.unregister(model)
            continue
        if model in admin.site._registry:
            continue
        if model is user_model or model is Group:
            admin_class = build_admin_class(model)
            admin.site.register(model, admin_class)
            continue
        admin_class = build_admin_class(model)
        admin.site.register(model, admin_class)
