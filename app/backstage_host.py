"""
Backstage host configuration for django_template (nav, overrides, editor meta, preview).

Demonstrates themed admin with sample models.

Editor copy policy:
- Model verbose_name / help_text are the default (especially SEO mixin and field help on models).
- FIELD_EDITOR_META only for jargon fields, inlines, rich-text hints, and models without model help.
- TAB_DESCRIPTIONS stay here (not on models).
"""

from __future__ import annotations

from typing import Any

from django.utils.translation import gettext_lazy as _

NAV_GROUPS = {
    "sample_pages": {
        "title": _("Sample pages"),
        "icon": "web",
        "apps": ["sample"],
        "models": [
            "sample.SampleHomePage",
            "sample.SampleSitePage",
            "sample.SampleArticle",
            "sample.SampleInquiry",
        ],
    },
    "system": {
        "title": _("System"),
        "icon": "settings",
        "apps": ["backstage", "user", "auth"],
    },
}

MODEL_ICONS = {
    "samplearticle": "newspaper",
    "samplehomepage": "home",
    "samplesitepage": "info",
    "sampleinquiry": "mail",
    "sampleinlinefact": "fact_check",
    "backstagesettings": "palette",
}

MODEL_LABELS: dict[str, str] = {
    "sampleinquiry": _("Contact submissions"),
}

ADMIN_OVERRIDES = {
    "SampleInquiry": {
        "readonly_fields": ["name", "email", "message", "created_at"],
        "list_display": ["name", "email", "is_read", "created_at"],
        "list_filter": ["is_read"],
    },
    "SampleArticle": {
        "list_display": ["title", "is_published", "published_at"],
        "list_display_links": ["title"],
    },
}

_RICH_HELP = _("Use simple formatting only (bold, lists, links). Headings match the public site design.")


def _rich_body(label: str) -> dict[str, Any]:
    return {"label": label, "help_text": _RICH_HELP}


TAB_DESCRIPTIONS = {
    "samplearticle": {
        "Content": _("Title, excerpt, and body."),
        "Publishing": _("Visibility and publish date."),
    },
    "samplesitepage": {
        "Content": _("Hero and introduction."),
        "SEO": _("Optional search and social previews."),
    },
}

FIELD_EDITOR_META = {
    "samplesitepage": {
        "hero_title": {
            "label": _("Main headline"),
            "help_text": _("Large title at the top of the page."),
        },
        "intro_body": _rich_body(_("Introduction")),
    },
}

PREVIEW_PATH_BY_MODEL: dict[str, str] = {
    "SampleHomePage": "/",
    "SampleSitePage": "/about",
}


def dashboard_sample_pages_count(request, admin_site) -> int:
    from sample.models import SampleHomePage, SampleSitePage

    count = 0
    if SampleHomePage.objects.filter(pk=1).exists():
        count += 1
    if SampleSitePage.objects.filter(pk=1).exists():
        count += 1
    return count


DASHBOARD = {
    "layout": ["welcome", "stats", "quick_actions", "my_drafts", "recent_activity"],
    "welcome": {
        "body": _("Reference host for Backstage: sample content, draft/publish, navigation, and appearance."),
        "links": [
            {
                "label": _("View live site"),
                "url_key": "frontend",
                "icon": "open_in_new",
            },
            {
                "label": _("Edit home page"),
                "model": "sample.samplehomepage",
                "action": "change",
                "singleton": True,
                "icon": "home",
            },
        ],
    },
    "stats": [
        {
            "id": "unread_inquiries",
            "label": _("Unread submissions"),
            "model": "sample.sampleinquiry",
            "filter": {"is_read": False},
            "icon": "mail",
            "accent": "blue",
            "link": "changelist",
        },
        {
            "id": "sample_articles",
            "label": _("Sample articles"),
            "model": "sample.samplearticle",
            "icon": "edit_note",
            "accent": "green",
            "link": "changelist",
        },
        {
            "id": "sample_pages",
            "label": _("Sample pages"),
            "model": "sample.samplesitepage",
            "count_callback": "app.backstage_host.dashboard_sample_pages_count",
            "icon": "language",
            "accent": "purple",
            "link": "changelist",
        },
    ],
    "quick_actions": [
        {
            "label": _("New sample article"),
            "model": "sample.samplearticle",
            "action": "add",
            "icon": "edit_square",
        },
        {
            "label": _("Contact submissions"),
            "model": "sample.sampleinquiry",
            "action": "changelist",
            "icon": "mail",
        },
        {
            "label": _("About page"),
            "model": "sample.samplesitepage",
            "action": "change",
            "singleton": True,
            "icon": "info",
        },
    ],
    "my_drafts": {"limit": 6},
    "recent_activity": {"limit": 8},
}


def resolve_preview_route(obj: Any) -> str | None:
    model_name = obj.__class__.__name__

    if model_name in PREVIEW_PATH_BY_MODEL:
        return PREVIEW_PATH_BY_MODEL[model_name]

    if model_name == "SampleArticle":
        slug = getattr(obj, "slug", None)
        if slug:
            return f"/articles/{slug}"

    return None
