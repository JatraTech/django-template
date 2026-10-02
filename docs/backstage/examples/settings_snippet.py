# Paste into settings.py (replace yourapp with your Django app label).

FRONTEND_URL = "http://localhost:5173"

from yourapp.backstage_host import (
    ADMIN_OVERRIDES,
    DASHBOARD,
    FIELD_EDITOR_META,
    INLINE_RELATIONS,
    MODEL_ICONS,
    MODEL_LABELS,
    NAV_GROUPS,
    TAB_DESCRIPTIONS,
)

BACKSTAGE = {
    "SITE_TITLE": "Acme Admin",
    "SITE_HEADER": "Acme Corp",
    "SITE_SUBHEADER": "Content management",
    "SITE_URL": FRONTEND_URL,
    "NAV_GROUPS": NAV_GROUPS,
    "MODEL_ICONS": MODEL_ICONS,
    "MODEL_LABELS": MODEL_LABELS,
    "PREVIEW_ROUTE_CALLBACK": "yourapp.backstage_host.resolve_preview_route",
    "DRAFT_PUBLISH": {
        "enabled": True,
        "models": ["blog.blogpost"],
    },
    "INLINE_RELATIONS": INLINE_RELATIONS,
    "ADMIN_OVERRIDES": ADMIN_OVERRIDES,
    "FIELD_EDITOR_META": FIELD_EDITOR_META,
    "TAB_DESCRIPTIONS": TAB_DESCRIPTIONS,
    "DASHBOARD": DASHBOARD,
}

# Preview API from iframe / SPA:
# from corsheaders.defaults import default_headers
# CORS_ALLOW_HEADERS = (*default_headers, "x-preview-token")

# TinyMCE — see docs/07-editor-ux.md
# TINYMCE_DEFAULT_CONFIG = { ... }
