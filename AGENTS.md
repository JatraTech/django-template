# AGENTS.md — django_template (reference host)

Guidance for Cursor agents working on this Django starter / Backstage reference repo.

This repo is the **reference host** for [django-backstage](https://github.com/JatraTech/django-backstage) and [django-jt](https://github.com/JatraTech/django-jt) (DRF utilities, optional Gmail/Graph mail) plus the shared **env/Docker contract**. Product backends copy [CONFIGURATION.md](docs/CONFIGURATION.md) and maintain their own `AGENTS.md`.

## Documentation

| Topic | Document |
|-------|----------|
| Doc index + read order | [`docs/README.md`](docs/README.md) |
| Architecture hub | [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) |
| Env, settings, Docker | [`docs/CONFIGURATION.md`](docs/CONFIGURATION.md) |
| Backstage CMS (topic) | [`docs/architecture/BACKSTAGE.md`](docs/architecture/BACKSTAGE.md) |
| Backstage CMS (detail) | [django-backstage integration](https://github.com/JatraTech/django-backstage/blob/main/docs/integration.md) |
| Backstage QA (this host) | [`docs/backstage/reference-host.md`](docs/backstage/reference-host.md) |
| Analytics / export (reference only; not in template) | [`docs/architecture/product_api_patterns.md`](docs/architecture/product_api_patterns.md) |

## Backstage admin

**Documentation:** [integration.md](https://github.com/JatraTech/django-backstage/blob/main/docs/integration.md) + [backstage_host.example.py](https://github.com/JatraTech/django-backstage/blob/main/docs/examples/backstage_host.example.py).

**Host file:** [`app/backstage_host.py`](app/backstage_host.py) (nav, overrides, editor meta, preview for **`sample`** models).

Wire `PREVIEW_ROUTE_CALLBACK`: `"app.backstage_host.resolve_preview_route"` in [`app/settings.py`](app/settings.py).

Editor copy: model-first; use `backstage_host.py` for jargon, inlines, and rich-text hints.

## Commands

```bash
uv run python manage.py check
uv run python manage.py check_backstage_integration
uv run pytest app/tests -q
```

## Verification

```bash
uv sync
uv run python manage.py check
uv run python manage.py check_backstage_integration
uv run pytest app/tests -q
uv run python -c "from django_jt.health import liveness; from django_jt.drf.spectacular import SpectacularRapiDocView"
```

**Shared utilities:** DRF/auth/email from `django_jt`; Backstage rich text + TinyMCE upload from `django-backstage` (`backstage.views.tinymce_upload`, `backstage.mixins.rich_text`). This template has no `app/utils/` or `app/admin/` trees.

## Preview API

[preview and frontend](https://github.com/JatraTech/django-backstage/blob/main/docs/features/preview-and-frontend.md).
