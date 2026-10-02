# Host project contract

Backstage auto-admin is **convention-driven**. These patterns are not enforced by migrations but determine tabs, widgets, navigation, and preview behavior.

## Two integration patterns

| Pattern | When | Where |
|---------|------|--------|
| **A — Copy examples** | New client projects | [examples/host_singleton.py](examples/host_singleton.py), [examples/host_seo_mixin.py](examples/host_seo_mixin.py), [examples/host_cms_api_utils.py](examples/host_cms_api_utils.py), [examples/host_singleton_viewset.py](examples/host_singleton_viewset.py) |
| **B — Shared host mixins** | Larger monorepos | Shared `models/base.py` + audit mixins in your project |

Backstage does not ship Django models for SEO/singleton in v1; the **host owns the schema**.

## Singleton pages (`SingletonModel`)

**Signal:** any base class named exactly `SingletonModel` in the model MRO (`factory._inherits_singleton`).

**Behavior:**

- Admin class: `SingletonAdmin` (no delete permission, changelist redirects to `pk=1` change view).
- Sidebar links directly to the change form.
- `get_or_create(pk=1)` on first edit.

**Model contract:**

```python
class AboutPage(SEOMixin, SingletonModel, ModelMixin):
    class Meta:
        verbose_name = "About page"
        verbose_name_plural = "About page"  # singular label in nav
```

See [examples/host_singleton.py](examples/host_singleton.py).

## Public API (DRF)

Admin singletons and public APIs both use `pk=1`, but the API layer should load rows via **`get_singleton(ModelClass)`**, not by passing a queryset into helpers that expect a model class.

Copy [examples/host_cms_api_utils.py](examples/host_cms_api_utils.py) into your CMS app. Use optional `prefetch_related=(...)` when serializers call `.all()` on related managers in `to_representation`.

Copy [examples/host_singleton_viewset.py](examples/host_singleton_viewset.py) for a minimal read-only `ViewSet.list` pattern (`AllowAny`, `GET` only).

## SEO tab (`SEOMixin` / field names)

**Signal:** editable fields whose names appear in `SEO_FIELD_NAMES` (default set in `backstage/conf.py`):

`seo_title`, `seo_description`, `canonical_url`, `og_title`, `og_description`, `og_image`

Override via `BACKSTAGE["SEO_FIELD_NAMES"]`.

**Behavior:** auto fieldsets place those fields on the **SEO** tab; remaining editable fields go to **Content** (and **Publishing** if applicable).

Use the same field names as [examples/host_seo_mixin.py](examples/host_seo_mixin.py) unless you customize `SEO_FIELD_NAMES`.

## Rich text (TinyMCE)

**Signals:**

- Field name in `RICH_TEXT_FIELD_NAMES` (default: `content`, `description`, `requirements`), **or**
- `TextField` whose name ends with a suffix in `RICH_TEXT_SUFFIXES` (default: `_body`).

**Host requirements:**

- `django-tinymce` installed and configured.
- Upload endpoint wired in your project (e.g. `admin/tinymce/upload/`).
- Slim toolbar recommended — see [../features/editor-ux.md](../features/editor-ux.md).

## Publishing tab

Fields moved to **Publishing** tab (when present on model):

`is_published`, `published_at`, `is_read`, `status`

Example: `BlogPost` uses `is_published` / `published_at`; `ModelMixin` uses `is_active` on **Content** tab (not in publishing set).

## Inline-only models

**Signal:** exactly one non-auto `ForeignKey` to a model in the **same app**.

**Behavior:** not registered in sidebar; only appears as stacked inline on the parent with tabbed inlines.

## Reverse FK children

Any reverse relation from parent → child generates a **stacked inline** with `extra=0`, optional `order` ordering, and per-inline tab slug.

## Audit / visibility (optional)

`ModelMixin` adds `created_at`, `updated_at`, `created_by`, `updated_by`, `is_active` (`verbose_name="Visible on website"`). Auto fieldsets exclude audit FKs from list display priority but include them on forms unless you override fieldsets.

## Preview eligibility

Implement `resolve_preview_route` in **`yourapp/backstage_host.py`**. Set `PREVIEW_ROUTE_CALLBACK` to `"yourapp.backstage_host.resolve_preview_route"`.

## Slug prepopulation

If model has both `slug` and `title` fields, factory sets `prepopulated_fields = {"slug": ("title",)}`.

## What Backstage skips registering

See [reference/auto-admin.md](reference/auto-admin.md): abstract, unmanaged, proxy, inline-only, `BackstageSettings`, `Permission`, apps in `SKIP_APP_LABELS`.

## Editor copy (optional but recommended)

Plain-language labels in admin come from `FIELD_EDITOR_META` / `TAB_DESCRIPTIONS` in host settings — not from this contract. See [../features/editor-ux.md](../features/editor-ux.md).
