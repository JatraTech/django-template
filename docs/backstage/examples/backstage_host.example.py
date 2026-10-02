"""
Backstage host configuration — copy this file into your Django project.

  cp docs/backstage/examples/backstage_host.example.py yourapp/backstage_host.py

Then wire exports in settings.py (see settings_snippet.py in this folder).

Editor copy policy:
- Model verbose_name / help_text are the default (SEO mixin, field help on models).
- FIELD_EDITOR_META only for jargon fields, inlines, rich-text hints, and models without model help.
- TAB_DESCRIPTIONS stay here (not on models).

Preview: implement resolve_preview_route below; point PREVIEW_ROUTE_CALLBACK at this module.
Import models inside that function if settings imports this module at startup.
See docs/backstage/reference/configuration.md for all BACKSTAGE keys.
"""

from __future__ import annotations

from typing import Any

from django.utils.translation import gettext_lazy as _

# --- Navigation ---

NAV_GROUPS = {
    "website": {
        "title": _("Website"),
        "icon": "web",
        "apps": ["pages", "blog"],
        # Optional allowlist — order and visibility in sidebar (page-child FK models stay inline-only):
        "models": [
            "pages.HomePage",
            "pages.AboutPage",
            "blog.BlogPost",
            "blog.ContactMessage",
        ],
    },
    "system": {
        "title": _("System"),
        "icon": "settings",
        "apps": ["backstage", "auth"],
    },
}

MODEL_ICONS = {
    "homepage": "home",
    "aboutpage": "info",
    "blogpost": "newspaper",
    "backstagesettings": "palette",
}

MODEL_LABELS: dict[str, str] = {}

# --- Dashboard (optional; see configuration.md) ---

DASHBOARD = {
    "layout": ["welcome", "stats", "quick_actions", "my_drafts", "recent_activity"],
    "welcome": {
        "body": _("Your admin home for content and settings."),
        "links": [
            {"label": _("View live site"), "url_key": "frontend", "icon": "open_in_new"},
            {
                "label": _("Edit home page"),
                "model": "pages.homepage",
                "action": "change",
                "singleton": True,
                "icon": "home",
            },
        ],
    },
    "stats": [
        {
            "id": "unread_messages",
            "label": _("Unread messages"),
            "model": "blog.contactmessage",
            "filter": {"is_read": False},
            "icon": "mail",
            "accent": "blue",
            "link": "changelist",
        },
    ],
    "quick_actions": [
        {"label": _("New post"), "model": "blog.blogpost", "action": "add", "icon": "edit_square"},
    ],
    "my_drafts": {"limit": 6},
    "recent_activity": {"limit": 8},
}

ADMIN_OVERRIDES = {
    "BlogPost": {
        "list_display": ["title", "is_published", "published_at"],
        "list_display_links": ["title"],
    },
    "ContactMessage": {
        "readonly_fields": ["name", "email", "message", "created_at"],
    },
}

# --- Editor UX ---

_RICH_HELP = _("Use simple formatting only (bold, lists, links). Headings match the website design.")


def _order(help_text: str | None = None) -> dict[str, Any]:
    meta: dict[str, Any] = {"label": _("Sort order")}
    if help_text is not None:
        meta["help_text"] = help_text
    return meta


def _rich_body(label: str) -> dict[str, Any]:
    return {"label": label, "help_text": _RICH_HELP}


TAB_DESCRIPTIONS = {
    "homepage": {
        "Content": _("Sections shown on the home page."),
        "SEO": _("Optional. Controls search and social link previews."),
    },
    "blogpost": {
        "Content": _("Article title, body, and featured image."),
        "Publishing": _("Control visibility and publish date."),
    },
}

FIELD_EDITOR_META = {
    "homepage": {
        "hero_title": {
            "label": _("Main headline"),
            "help_text": _("Large title at the top of the home page."),
        },
        "intro_body": _rich_body(_("Introduction")),
    },
    # Catalog models (BlogPost, Product, …): set verbose_name / help_text on the model,
    # not here — see 07-editor-ux.md.
}

# --- Preview routes (public site paths, no domain) ---

# Static path per model class name:
PREVIEW_PATH_BY_MODEL: dict[str, str] = {
    "HomePage": "/",
    "AboutPage": "/about",
}

# Optional slug → path for marketing-style pages (slug field on model):
PREVIEW_PATH_BY_SLUG: dict[str, str] = {
    "contact": "/contact",
    "pricing": "/pricing",
}


def resolve_preview_route(obj: Any) -> str | None:
    """Map admin object → frontend path for split-pane preview. Return None to disable."""
    model_name = obj.__class__.__name__

    if model_name in PREVIEW_PATH_BY_MODEL:
        return PREVIEW_PATH_BY_MODEL[model_name]

    slug = getattr(obj, "slug", None)
    if slug and slug in PREVIEW_PATH_BY_SLUG:
        return PREVIEW_PATH_BY_SLUG[slug]

    if model_name == "BlogPost" and slug:
        return f"/blog/{slug}"

    return None


# Optional: convention overrides (None = package defaults in backstage/conf.py)
# SEO_FIELD_NAMES = None
# RICH_TEXT_FIELD_NAMES = None
# RICH_TEXT_SUFFIXES = None
# SKIP_APP_LABELS = None

# settings.py:
# PREVIEW_ROUTE_CALLBACK = "yourapp.backstage_host.resolve_preview_route"
