from __future__ import annotations

from typing import Any

from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin, UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from django.db import models

from backstage.conf import (
    get_rich_text_field_names,
    get_rich_text_suffixes,
    get_seo_field_names,
    get_tab_descriptions,
)
from backstage.draft.admin import DraftPublishAdminMixin
from backstage.draft.conf import is_draft_publish_model
from backstage.draft.preview import preview_enabled_for_model
from backstage.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm
from backstage.registry.base import BackstageModelAdmin, BackstageStackedInline, SingletonAdmin
from backstage.settings import get_config

AUTO_FIELD_NAMES = frozenset({"id", "created_at", "updated_at", "created_by", "updated_by"})

LIST_DISPLAY_LINK_PRIORITY = ("title", "name", "text", "label", "heading", "slug")
LIST_DISPLAY_DEPRIORITIZE = frozenset(
    {
        "is_active",
        "order",
        "page",
        "slug",
        "image",
        "image_url",
        "external_image_url",
        "logo",
        "custom_image_url",
    }
)


def _make_admin_class(name: str, bases: tuple[type, ...], attrs: dict[str, Any]) -> type:
    admin_class = type(name, bases, attrs)
    admin_class.__module__ = __name__
    return admin_class


def _inherits_singleton(model: type[models.Model]) -> bool:
    return any(base.__name__ == "SingletonModel" for base in model.__mro__)


def _has_seo_fields(model: type[models.Model]) -> bool:
    return get_seo_field_names().issubset({f.name for f in model._meta.get_fields() if hasattr(f, "name")})


def _is_rich_text_field(field: models.Field) -> bool:
    if not isinstance(field, models.TextField):
        return False
    if field.name in get_rich_text_field_names():
        return True
    return any(field.name.endswith(suffix) for suffix in get_rich_text_suffixes())


def _rich_text_fields(model: type[models.Model]) -> tuple[str, ...]:
    return tuple(
        field.name for field in model._meta.get_fields() if hasattr(field, "name") and _is_rich_text_field(field)
    )


INLINE_ONLY_IGNORED_FK_NAMES = frozenset({"created_by", "updated_by"})


def _is_inline_only_model(model: type[models.Model]) -> bool:
    foreign_keys = [
        field
        for field in model._meta.get_fields()
        if isinstance(field, models.ForeignKey)
        and not field.auto_created
        and field.name not in INLINE_ONLY_IGNORED_FK_NAMES
    ]
    if len(foreign_keys) != 1:
        return False
    parent = foreign_keys[0].remote_field.model
    if parent is model:
        return False
    return parent._meta.app_label == model._meta.app_label


def _editable_fields(model: type[models.Model]) -> list[str]:
    names = [
        field.name
        for field in model._meta.get_fields()
        if getattr(field, "editable", False) and field.name not in AUTO_FIELD_NAMES
    ]
    if is_draft_publish_model(model):
        names = [name for name in names if name not in {"live_version", "is_published"}]
    return names


def _build_fieldsets(model: type[models.Model]) -> tuple[tuple[str | None, dict[str, Any]], ...]:
    editable = _editable_fields(model)
    if not editable:
        return ((None, {"fields": ()}),)

    seo_field_names = get_seo_field_names()
    seo_fields = [name for name in editable if name in seo_field_names]
    non_seo = [name for name in editable if name not in seo_field_names]
    tab_descriptions = get_tab_descriptions(model)

    fieldsets: list[tuple[str | None, dict[str, Any]]] = []
    publishing_fields = [name for name in non_seo if name in {"is_published", "published_at", "is_read", "status"}]
    if is_draft_publish_model(model):
        publishing_fields = [name for name in publishing_fields if name != "is_published"]
    content_fields = [name for name in non_seo if name not in publishing_fields]

    def _tab_options(tab_name: str, fields: tuple[str, ...]) -> dict[str, Any]:
        options: dict[str, Any] = {"classes": ["tab"], "fields": fields}
        description = tab_descriptions.get(tab_name)
        if description:
            options["description"] = description
        return options

    if content_fields:
        fieldsets.append(("Content", _tab_options("Content", tuple(content_fields))))
    if publishing_fields:
        fieldsets.append(("Publishing", _tab_options("Publishing", tuple(publishing_fields))))
    if seo_fields:
        fieldsets.append(("SEO", _tab_options("SEO", tuple(seo_fields))))

    if not fieldsets:
        fieldsets.append((None, {"fields": tuple(editable)}))
    return tuple(fieldsets)


def _make_inline_admin(inline_model: type[models.Model], fk_name: str) -> type:
    inline_fields = [
        field.name
        for field in inline_model._meta.get_fields()
        if getattr(field, "editable", False) and field.name not in AUTO_FIELD_NAMES and field.name != fk_name
    ]
    rich_fields = _rich_text_fields(inline_model)
    tab_slug = inline_model._meta.model_name
    ordering = ["order", "id"] if any(f.name == "order" for f in inline_model._meta.get_fields()) else ["id"]

    return _make_admin_class(
        f"{inline_model.__name__}Inline",
        (BackstageStackedInline,),
        {
            "model": inline_model,
            "fk_name": fk_name,
            "extra": 0,
            "tab": True,
            "verbose_name": tab_slug,
            "verbose_name_plural": inline_model._meta.verbose_name_plural,
            "fields": inline_fields or None,
            "rich_text_fields": rich_fields,
            "ordering": ordering,
        },
    )


def _build_inlines(model: type[models.Model]) -> list[type]:
    inlines: list[type] = []
    for relation in model._meta.get_fields():
        if not (relation.one_to_many and relation.auto_created and not relation.concrete):
            continue
        inline_model = relation.related_model
        if not inline_model._meta.managed or inline_model._meta.abstract:
            continue
        fk_name = relation.field.name
        if is_draft_publish_model(model) and relation.get_accessor_name() == "draft_copies":
            continue
        inlines.append(_make_inline_admin(inline_model, fk_name))
    return inlines


def _is_list_display_candidate(field: models.Field) -> bool:
    if not getattr(field, "concrete", False):
        return False
    if field.many_to_many or field.one_to_many:
        return False
    if field.name in AUTO_FIELD_NAMES:
        return False
    if isinstance(field, models.TextField):
        return False
    if isinstance(field, models.BooleanField):
        return False
    if isinstance(field, (models.FileField, models.ImageField)):
        return False
    return True


def _list_display_candidate_names(model: type[models.Model]) -> list[str]:
    names = [field.name for field in model._meta.get_fields() if _is_list_display_candidate(field)]
    if is_draft_publish_model(model):
        names = [name for name in names if name != "live_version"]
    return names


def _pick_list_display_link_field(model: type[models.Model], candidate_names: list[str]) -> str:
    name_set = set(candidate_names)
    for name in LIST_DISPLAY_LINK_PRIORITY:
        if name in name_set:
            return name
    field_by_name = {field.name: field for field in model._meta.get_fields() if hasattr(field, "name")}
    for name in candidate_names:
        field = field_by_name.get(name)
        if field and isinstance(field, (models.CharField, models.SlugField)):
            return name
    return "__str__"


def _build_list_display_config(
    model: type[models.Model],
) -> tuple[list[str], tuple[str, ...] | None]:
    candidates = _list_display_candidate_names(model)
    if not candidates:
        return (["__str__"], ("__str__",))

    link_field = _pick_list_display_link_field(model, candidates)
    deprioritized = {name for name in LIST_DISPLAY_DEPRIORITIZE if name in candidates and name != link_field}
    prioritized = [name for name in candidates if name not in deprioritized and name != link_field]

    display: list[str] = []
    if link_field == "__str__":
        display.append("__str__")
    else:
        display.append(link_field)

    for name in prioritized:
        if len(display) >= 5:
            break
        if name not in display:
            display.append(name)

    for name in candidates:
        if len(display) >= 5:
            break
        if name in deprioritized and name not in display:
            display.append(name)

    link_target = link_field if link_field in display else display[0]
    return (display, (link_target,))


def _build_list_display(model: type[models.Model]) -> list[str]:
    return _build_list_display_config(model)[0]


def _build_list_filter(model: type[models.Model]) -> list[str]:
    filters: list[str] = []
    for field in model._meta.get_fields():
        if not getattr(field, "concrete", False):
            continue
        if isinstance(field, models.BooleanField):
            filters.append(field.name)
        elif isinstance(field, models.CharField) and getattr(field, "choices", None):
            filters.append(field.name)
    return filters[:4]


def _build_search_fields(model: type[models.Model]) -> list[str]:
    return [
        field.name
        for field in model._meta.get_fields()
        if isinstance(field, (models.CharField, models.TextField)) and field.name not in AUTO_FIELD_NAMES
    ][:5]


def _apply_admin_overrides(admin_class: type, model_name: str) -> type:
    overrides = get_config().get("ADMIN_OVERRIDES", {}).get(model_name, {})
    if overrides:
        for key, value in overrides.items():
            setattr(admin_class, key, value)
    return admin_class


def _filter_model_field_names(model: type[models.Model], names: tuple[str, ...]) -> tuple[str, ...]:
    available = {f.name for f in model._meta.get_fields() if hasattr(f, "name")}
    return tuple(name for name in names if name in available)


def build_admin_class(model: type[models.Model]) -> type:
    from django.contrib.auth import get_user_model

    User = get_user_model()

    if model is Group:
        return _apply_admin_overrides(
            _make_admin_class("BackstageGroupAdmin", (BaseGroupAdmin, BackstageModelAdmin), {}),
            model.__name__,
        )

    if model is User:
        personal_fields = _filter_model_field_names(User, ("first_name", "last_name", "email", "image", "dob", "phone"))
        permission_fields = _filter_model_field_names(
            User,
            (
                "is_active",
                "user_role",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
                "notify_on_user_reg",
            ),
        )
        date_fields = _filter_model_field_names(User, ("last_login", "date_joined"))
        return _apply_admin_overrides(
            _make_admin_class(
                "BackstageUserAdmin",
                (BaseUserAdmin, BackstageModelAdmin),
                {
                    "form": UserChangeForm,
                    "add_form": UserCreationForm,
                    "change_password_form": AdminPasswordChangeForm,
                    "list_filter": _filter_model_field_names(User, ("is_staff", "is_superuser", "user_role")),
                    "search_fields": list(
                        _filter_model_field_names(User, ("id", "first_name", "last_name", "email", "username"))
                    ),
                    "fieldsets": (
                        (None, {"fields": ("username", "password")}),
                        ("Personal info", {"classes": ["tab"], "fields": personal_fields}),
                        (
                            "Permissions",
                            {"classes": ["tab"], "fields": permission_fields},
                        ),
                        ("Important dates", {"classes": ["tab"], "fields": date_fields}),
                    ),
                },
            ),
            model.__name__,
        )

    if _inherits_singleton(model):
        base: type = SingletonAdmin
    elif is_draft_publish_model(model):
        base = _make_admin_class(
            f"DraftPublish{model.__name__}Admin",
            (DraftPublishAdminMixin, BackstageModelAdmin),
            {},
        )
    else:
        base = BackstageModelAdmin
    list_display, list_display_links = _build_list_display_config(model)
    attrs: dict[str, Any] = {
        "show_full_result_count": False,
        "list_display": list_display,
        "list_display_links": list_display_links,
        "list_filter": _build_list_filter(model),
        "search_fields": _build_search_fields(model),
        "fieldsets": _build_fieldsets(model),
        "inlines": _build_inlines(model),
    }

    rich_fields = _rich_text_fields(model)
    if rich_fields:
        attrs["rich_text_fields"] = rich_fields

    if preview_enabled_for_model(model):
        attrs["preview_enabled"] = True

    if any(field.name == "slug" for field in model._meta.get_fields() if hasattr(field, "name")):
        if any(field.name == "title" for field in model._meta.get_fields() if hasattr(field, "name")):
            attrs["prepopulated_fields"] = {"slug": ("title",)}

    fk_names = [field.name for field in model._meta.get_fields() if isinstance(field, models.ForeignKey)]
    if "product" in fk_names:
        attrs["autocomplete_fields"] = ["product"]

    return _apply_admin_overrides(
        _make_admin_class(f"{model.__name__}Admin", (base,), attrs),
        model.__name__,
    )
