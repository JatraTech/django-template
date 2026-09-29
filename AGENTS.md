# AGENTS.md — django_template (reference host)

Guidance for Cursor agents working on this Django starter / Backstage reference repo.

## Backstage admin

**Documentation:** [`docs/backstage/integration.md`](docs/backstage/integration.md) + [`docs/backstage/examples/backstage_host.example.py`](docs/backstage/examples/backstage_host.example.py).

**Host file:** [`app/backstage_host.py`](app/backstage_host.py) (nav, overrides, editor meta, preview for **`sample`** models).

Wire `PREVIEW_ROUTE_CALLBACK`: `"app.backstage_host.resolve_preview_route"` in [`app/settings.py`](app/settings.py).

Editor copy: model-first; use `backstage_host.py` for jargon, inlines, and rich-text hints.

## Commands

```bash
cd django_template
uv run python manage.py check_backstage_integration
uv run pytest app/tests -q
```

Package development source: sibling [`bpi-backend/backstage/`](../bpi/bpi-backend/backstage/).

## Preview API

[`docs/backstage/features/preview-and-frontend.md`](docs/backstage/features/preview-and-frontend.md).
