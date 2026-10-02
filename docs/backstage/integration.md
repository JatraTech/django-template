# Backstage integration (human path)

Single onboarding guide for developers. For exhaustive reference, see [README.md](README.md).

## 1. Install the package

Copy `backstage/` into your Django project. In `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    "backstage",
    "backstage.contrib.forms",
    "backstage.contrib.inlines",
    "django.contrib.admin",  # after backstage
    # your apps
]
```

URLs:

```python
path("backstage/", include("backstage.urls")),
path("admin/", admin.site.urls),
```

```bash
python manage.py migrate backstage
```

Details: [guides/quickstart.md](guides/quickstart.md).

## 2. Host config (one file)

Copy the template:

```bash
cp docs/backstage/examples/backstage_host.example.py yourapp/backstage_host.py
```

Customize navigation, overrides, editor meta, and **`resolve_preview_route`** in **`yourapp/backstage_host.py`**.

If `settings.py` imports from `backstage_host` at module level, **import Django models inside `resolve_preview_route`**, not at the top of `backstage_host.py`.

Wire `settings.py`:

```python
from yourapp.backstage_host import (
    ADMIN_OVERRIDES,
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
    "SITE_URL": FRONTEND_URL,
    "NAV_GROUPS": NAV_GROUPS,
    "MODEL_ICONS": MODEL_ICONS,
    "MODEL_LABELS": MODEL_LABELS,
    "PREVIEW_ROUTE_CALLBACK": "yourapp.backstage_host.resolve_preview_route",
    "ADMIN_OVERRIDES": ADMIN_OVERRIDES,
    "INLINE_RELATIONS": INLINE_RELATIONS,
    "FIELD_EDITOR_META": FIELD_EDITOR_META,
    "TAB_DESCRIPTIONS": TAB_DESCRIPTIONS,
}
```

See [examples/settings_snippet.py](examples/settings_snippet.py).

## 3. Model conventions

Auto-admin detects `SingletonModel`, SEO field names, and rich-text field names. Copy abstract bases from [examples/host_singleton.py](examples/host_singleton.py) and [examples/host_seo_mixin.py](examples/host_seo_mixin.py).

For headless/public APIs, copy [examples/host_cms_api_utils.py](examples/host_cms_api_utils.py) and [examples/host_singleton_viewset.py](examples/host_singleton_viewset.py).

Full contract: [guides/host-contract.md](guides/host-contract.md).

**Page-child models (sidebar):** If a model has a single foreign key to a parent page in the same app (ignoring audit fields like `created_by` / `updated_by`), Backstage treats it as inline-only: it is not registered as a standalone admin and does not appear in the auto-built sidebar. Edit those rows on the parent change form tabs instead. To order and allowlist sidebar items, set optional `models` on each entry in `NAV_GROUPS` (e.g. `"website.HomePage"`).

### Inline relations (`INLINE_RELATIONS`)

Use one list in `backstage_host.py` instead of juggling `ADMIN_OVERRIDES.inlines`, `STANDALONE_CHILD_MODELS`, `INLINE_HUB`, and a custom inline class.

| Field | Purpose |
|--------|---------|
| `parent` / `child` | Model class names |
| `mode` | `default_stacked` \| `default_tabular` \| `hub_tabular` \| `hub_stacked` |
| `fk` | Optional; inferred when only one FK to parent |
| `fields`, `ordering` | Inline columns |
| `standalone_child` | Child keeps full admin (changelist + change) |
| `hide_parent_fk_on_child` | `exclude` parent FK on child admin |
| `help_text`, `add_label`, `changelist_label` | Hub footer copy |
| `primary_tab` | Hub only: `false` keeps the legacy block below fieldsets; default `true` adds a tab next to Page/SEO fieldset tabs |
| `inline_class` | Optional dotted path to override generated inline |

Unconfigured reverse FKs still get **default stacked** editable inlines.

Example (hub summary on a singleton page; child edited on standalone screens):

```python
INLINE_RELATIONS = [
    {
        "parent": "PressReleasesPage",
        "child": "PressRelease",
        "mode": "hub_tabular",
        "fk": "press_page",
        "fields": ("date", "title", "category"),
        "ordering": ("-date",),
        "standalone_child": True,
        "hide_parent_fk_on_child": True,
        "help_text": _("Summary only. Use Edit for full body, Add for a new release."),
    },
]
```

Wire in `settings.py`: `"INLINE_RELATIONS": INLINE_RELATIONS`. See [features/hub-inlines.md](features/hub-inlines.md).

**Hub primary tabs:** When the parent uses tabbed fieldsets (`classes: ["tab"]` on fieldsets), each `hub_*` relation with `primary_tab` enabled (default) appears as an extra tab in the same strip (e.g. Page | SEO | Press releases). The table and Add/View-all footer live inside that tab panel—not a separate card below the page.

Legacy `INLINE_HUB` remains supported; do not duplicate the same parent/child in both.

## 4. Editor copy policy

| Put copy on… | When |
|--------------|------|
| **Model** | Default labels and help (SEO, limits) |
| **`FIELD_EDITOR_META` in `backstage_host.py`** | Jargon, inlines, rich-text hints |
| **`TAB_DESCRIPTIONS`** | Tab intro paragraphs |

Do not duplicate the same text on model and meta.

## 5. Customize admin

1. `ADMIN_OVERRIDES` in `backstage_host.py`
2. Editor meta / tab descriptions in the same file
3. Unregister + custom `ModelAdmin` only when needed — [features/customization.md](features/customization.md)

## 6. Preview (optional)

Implement `resolve_preview_route` in **`backstage_host.py`**. Enable CORS header `x-preview-token`. See [features/preview-and-frontend.md](features/preview-and-frontend.md).

## Verify in your project

```bash
python manage.py check_backstage_integration
```

The integration check prints **warnings** when `FIELD_EDITOR_META` repeats a model field’s `verbose_name` or `help_text` — remove those entries from host meta. It also validates `DRAFT_PUBLISH` models have `live_version` and a preview route mapping.

Draft/publish: [features/draft-publish.md](features/draft-publish.md).

Branding: **System → Admin appearance** (DB overrides `BACKSTAGE`).

## Layer boundaries

Keep host-specific code out of the package when possible:

| Layer | Package | Host |
|-------|---------|------|
| Config | `BACKSTAGE` defaults, merge in `get_config()` | `backstage_host.py`, `settings.BACKSTAGE` |
| Registration | `registry/autodiscover`, `factory.build_admin_class` | `ADMIN_OVERRIDES`, unregister/custom admins |
| Domain | Draft mixin, preview callback **path**, dashboard widget builders | Models, `resolve_preview_route`, TinyMCE upload URL |
| UI | Templates, `admin-theme.css`, widgets | Optional `DASHBOARD_TEMPLATE`, `STYLES` / logos |

`backstage` must be **first** in `INSTALLED_APPS`; it installs `BackstageAdminSite` as `admin.site` during `AppConfig.ready()`.

Rich text: mixins in `backstage/mixins/rich_text.py`; host still serves `admin/tinymce_upload.js` — see [features/editor-ux.md](features/editor-ux.md).

## Reference host (this repo)

Use this **`django_template`** project for manual QA: changelist, draft/publish on **sample** articles, preview split pane, and **System → Admin appearance**.

## Troubleshooting

[operations/troubleshooting.md](operations/troubleshooting.md)

## Optional contrib apps

The package ships optional Django apps under `backstage/contrib/`. Enable only what you need in `INSTALLED_APPS` (after `backstage`, before or with your apps):

| App | Purpose |
|-----|---------|
| `backstage.contrib.forms` | Rich text / array form widgets |
| `backstage.contrib.inlines` | Nested inline admin |
| `backstage.contrib.filters` | Advanced admin list filters |
| `backstage.contrib.simple_history` | History templates + submit line |
| `backstage.contrib.constance` | Constance config UI |
| `backstage.contrib.guardian` | Object permissions forms |
| `backstage.contrib.import_export` | Import/export preview tables |
| `backstage.contrib.waffle`, `hijack`, `location_field` | Feature flags, hijack, geo fields |

BPI uses **forms** and **inlines** only; other contrib code remains for reuse in other host projects and is not dead code.
