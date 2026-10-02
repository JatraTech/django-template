from __future__ import annotations

from backstage.settings import get_config

DEFAULT_SKIP_APP_LABELS = ("contenttypes", "sessions", "admin")

DEFAULT_SEO_FIELD_NAMES = (
    "seo_title",
    "seo_description",
    "canonical_url",
    "og_title",
    "og_description",
    "og_image",
)

DEFAULT_RICH_TEXT_FIELD_NAMES = ("content", "description", "requirements")
DEFAULT_RICH_TEXT_SUFFIXES = ("_body",)

DEFAULT_SIDEBAR_GROUP_COLLAPSE = "dynamic"
SIDEBAR_GROUP_COLLAPSE_CHOICES = frozenset({"open", "collapsed", "dynamic"})


def get_skip_app_labels() -> frozenset[str]:
    configured = get_config().get("SKIP_APP_LABELS")
    if configured is None:
        return frozenset(DEFAULT_SKIP_APP_LABELS)
    return frozenset(configured)


def get_seo_field_names() -> frozenset[str]:
    configured = get_config().get("SEO_FIELD_NAMES")
    if configured is None:
        return frozenset(DEFAULT_SEO_FIELD_NAMES)
    return frozenset(configured)


def get_rich_text_field_names() -> frozenset[str]:
    configured = get_config().get("RICH_TEXT_FIELD_NAMES")
    if configured is None:
        return frozenset(DEFAULT_RICH_TEXT_FIELD_NAMES)
    return frozenset(configured)


def get_rich_text_suffixes() -> tuple[str, ...]:
    configured = get_config().get("RICH_TEXT_SUFFIXES")
    if configured is None:
        return DEFAULT_RICH_TEXT_SUFFIXES
    return tuple(configured)


def get_sidebar_group_collapse() -> str:
    configured = get_config().get("SIDEBAR", {}).get("group_collapse")
    if configured is None:
        return DEFAULT_SIDEBAR_GROUP_COLLAPSE
    value = str(configured).lower()
    if value not in SIDEBAR_GROUP_COLLAPSE_CHOICES:
        return DEFAULT_SIDEBAR_GROUP_COLLAPSE
    return value


def get_field_editor_meta(model: type) -> dict[str, dict[str, str]]:
    key = model.__name__.lower()
    configured = get_config().get("FIELD_EDITOR_META") or {}
    raw = configured.get(key)
    if not raw:
        return {}
    return {str(field): dict(options) for field, options in raw.items()}


def get_tab_descriptions(model: type) -> dict[str, str]:
    key = model.__name__.lower()
    configured = get_config().get("TAB_DESCRIPTIONS") or {}
    raw = configured.get(key)
    if not raw:
        return {}
    return {str(tab): str(text) for tab, text in raw.items()}


def get_inline_hub_options(parent_model: type, child_model: type) -> dict:
    configured = get_config().get("INLINE_HUB") or {}
    parent_key = parent_model.__name__
    child_key = child_model.__name__
    raw = configured.get(parent_key) or configured.get(parent_key.lower())
    if not isinstance(raw, dict):
        return {}
    options = raw.get(child_key) or raw.get(child_key.lower())
    if not isinstance(options, dict):
        return {}
    return dict(options)


def get_model_label(model: type, *, plural: bool = True) -> str:
    key = model.__name__.lower()
    override = get_config().get("MODEL_LABELS", {}).get(key)
    if override:
        return str(override)
    meta = model._meta
    return str(meta.verbose_name_plural if plural else meta.verbose_name)
