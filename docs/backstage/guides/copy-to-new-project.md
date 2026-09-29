# Universal copy checklist

Use this when copying [`backstage/`](../../backstage/) into a **new** Django project (not the BPI monorepo). For day-to-day BPI development, see [../integration.md](../integration.md).

## 1. Copy the package

Copy the entire `backstage/` directory into your project root (sibling to your settings module). Do **not** copy BPI apps (`app/`, `core/`, `website/`) or `app.utils.admin.rich_text` shims—use [`backstage/mixins/rich_text.py`](../../backstage/mixins/rich_text.py) directly.

## 2. Install and wire Django

```python
INSTALLED_APPS = [
    "backstage",
    "backstage.contrib.forms",
    "backstage.contrib.inlines",
    "django.contrib.admin",  # after backstage
    # your apps
]

urlpatterns = [
    path("backstage/", include("backstage.urls")),
    path("admin/", admin.site.urls),
]
```

```bash
python manage.py migrate backstage
python manage.py check_backstage_integration
```

`backstage` must be **first** in `INSTALLED_APPS` (it installs `BackstageAdminSite` on startup).

## 3. Host configuration

```bash
cp docs/backstage/examples/backstage_host.example.py yourapp/backstage_host.py
```

Wire in `settings.py` — see [examples/settings_snippet.py](examples/settings_snippet.py):

- `BACKSTAGE` dict (`NAV_GROUPS`, `ADMIN_OVERRIDES`, `PREVIEW_ROUTE_CALLBACK`, optional `DRAFT_PUBLISH`, `DASHBOARD`)
- Import model metadata from `yourapp/backstage_host.py` only (not from product models at module top level unless lazy)

## 4. Host-owned pieces

| Piece | Owner |
|-------|--------|
| CMS / catalog models | Your apps (singleton + SEO: [examples/host_singleton.py](examples/host_singleton.py), [host_seo_mixin.py](examples/host_seo_mixin.py)) |
| TinyMCE upload JS | Your static (`admin/tinymce_upload.js`) — [../features/editor-ux.md](../features/editor-ux.md) |
| Preview URLs | `resolve_preview_route` in `backstage_host.py` — [../features/preview-and-frontend.md](../features/preview-and-frontend.md) |
| Optional image optimization | Your fields (e.g. custom `ImageField` subclass)—**not** required on `BackstageSettings` |

## 5. Draft/publish (optional)

Enable in settings:

```python
"DRAFT_PUBLISH": {
    "enabled": True,
    "models": ["yourapp.blogpost"],
    # optional: "copy_fields": {"yourapp.blogpost": ["title", "slug", "content", ...]},
},
```

Each listed model needs `DraftPublishDuplicateRowMixin` and either `copy_fields` or `draft_copy_field_names()` on the model.

## 6. Verify

From your project root (with venv active):

```bash
python manage.py check_backstage_integration
```

Manual QA with sample models: use this **`django_template`** reference host (vendored `backstage/` + `sample` app) and run `/admin/` locally.

## 7. Do not copy from BPI

- `app/backstage_host.py` business config (use as **reference**, not verbatim)
- `core`, `website`, `app.utils.fields.OptimizedImageField` (host-only optimizations)
- BPI-specific `INSTALLED_APPS` and API apps unless your project needs them
