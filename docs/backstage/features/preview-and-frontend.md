# Preview and frontend integration

Split-pane preview shows the public frontend in an iframe beside the change form. For models in `DRAFT_PUBLISH`, preview reads **draft** content; otherwise preview shows **saved** DB state (see [draft-publish.md](draft-publish.md)).

## Enable preview for a model

1. Implement **`resolve_preview_route(obj)`** in **`yourapp/backstage_host.py`** (return path only, or `None`).
2. Set `BACKSTAGE["PREVIEW_ROUTE_CALLBACK"]` to `"yourapp.backstage_host.resolve_preview_route"`.

```python
def resolve_preview_route(obj):
    if obj.__class__.__name__ == "BlogPost" and getattr(obj, "slug", None):
        return f"/blog/{obj.slug}"
    return None
```

3. Add the model to `BACKSTAGE["DRAFT_PUBLISH"]["models"]` with duplicate-row draft fields (`DraftPublishDuplicateRowMixin`). Split-pane preview is enabled only for allowlisted models when step 1 returns a route.

See [draft-publish.md](draft-publish.md) and [examples/backstage_host.example.py](examples/backstage_host.example.py).

When preview paths are tied to **model-owned slugs** (e.g. marketing pages), prefer a class-level `PREVIEW_PATH_BY_SLUG` on the model and read it from `resolve_preview_route` instead of duplicating slug→path maps in the host file.

## Preview URL construction

1. Callback route
2. Signed token (`PreviewTokenService`, 15-minute TTL)
3. Base URL from Admin appearance / `SITE_URL` / env

Final URL: `{frontend_url}{route}?preview={token}`

## CORS (SPA frontend)

Greenfield projects using this template already configure this in **`app/settings.py`**. When merging Backstage into an existing Django project, add the same block from [examples/settings_snippet.py](../examples/settings_snippet.py).

```python
from corsheaders.defaults import default_headers

CORS_ALLOW_HEADERS = (*default_headers, "x-preview-token")
```

## API: draft content with token

Use `PreviewQuerysetMixin` on DRF viewsets (`backstage/preview/mixins.py`):

```python
def get_queryset(self):
    if self.get_preview_context():
        return self.get_unfiltered_queryset()
    return super().get_queryset().filter(is_published=True)
```

## Troubleshooting

[../operations/troubleshooting.md](../operations/troubleshooting.md)
