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

Apply migrations after upgrading the package (includes `0002_backfill_branding_from_config` for existing Admin appearance rows).

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

For extra inline classes, fieldsets, or ordering on a parent, use `ADMIN_OVERRIDES` in `backstage_host.py` (e.g. `"inlines"`, `"fieldsets"`). See [features/customization.md](features/customization.md).

### Inline relations (`INLINE_RELATIONS`)

Declare parent → child edges in `BACKSTAGE["INLINE_RELATIONS"]` (export a list from `backstage_host.py`). At startup the package compiles them into inlines, `STANDALONE_CHILD_MODELS`, and child `exclude` as needed:

| `mode` | Behavior |
|--------|----------|
| `default_stacked` | Editable stacked inline (factory default if omitted) |
| `default_tabular` | Editable tabular inline |
| `hub_tabular` / `hub_stacked` | Read-only summary + Edit/Delete + Add/View all footer |

Set **`primary_tab_slug`** on a hub entry to anchor the hub panel on a parent fieldset tab (same tab bar as `classes: ["tab"]` fieldsets). See [reference/configuration.md](reference/configuration.md).

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

Implement `resolve_preview_route` in **`backstage_host.py`**. The SPA sends preview tokens on API requests; whitelist **`x-preview-token`** in `CORS_ALLOW_HEADERS` (see [features/preview-and-frontend.md](features/preview-and-frontend.md)). Greenfield projects: this is already set in template **`app/settings.py`**. Brownfield merges: copy the Security & CORS block from [examples/settings_snippet.py](examples/settings_snippet.py).

## Verify in your project

```bash
python manage.py check_backstage_integration
```

The integration check prints **warnings** when `FIELD_EDITOR_META` repeats a model field’s `verbose_name` or `help_text` — remove those entries from host meta. It also validates `DRAFT_PUBLISH` models have `live_version` and a preview route mapping.

Draft/publish: [features/draft-publish.md](features/draft-publish.md).

Branding: **System → Admin appearance**. Text fields (title, header, subheader) are stored in the DB; `BACKSTAGE` SITE_* seed new or empty rows via migration/create only — see [reference/configuration.md](reference/configuration.md).

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
