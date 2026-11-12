# Backstage reference host (django-template)

Use this project for **manual QA** after installing [django-backstage](https://github.com/JatraTech/django-backstage). Generic integration steps are in [package integration.md](https://github.com/JatraTech/django-backstage/blob/main/docs/integration.md).

## Wiring in this repo

| Piece | Location |
|-------|----------|
| `BACKSTAGE` + imports | [`app/settings.py`](../../app/settings.py) |
| Nav, overrides, editor meta, preview | [`app/backstage_host.py`](../../app/backstage_host.py) |
| Demo CMS models | [`sample/`](../../sample/) |
| Package dependency | [`django-backstage`](https://github.com/JatraTech/django-backstage) in [`pyproject.toml`](../../pyproject.toml) (git URL or local path for dev) |

`PREVIEW_ROUTE_CALLBACK`: `"app.backstage_host.resolve_preview_route"`.

## Verify

```bash
uv run python manage.py check_backstage_integration
uv run python manage.py migrate backstage
```

Then open **http://localhost:8000/admin/** (after `createsuperuser`).

## Smoke checklist

1. **Dashboard** — sidebar entry, welcome/stats/quick actions, drafts and recent activity widgets
2. **Sample pages → Sample articles** — changelist, change form, draft/publish flow
3. **Sample site page** — inline facts on the parent form only (not a separate sidebar model)
4. **System → Admin appearance** — accent palette and theme presets
5. Changelist link colors (default text, accent on hover), empty-state **Add** button, filters, dark mode

Exercise changelist, draft/publish on **sample** articles, preview split pane, and **Admin appearance**.

## Preview + frontend

This template pairs with [reactjs-ts-template](https://github.com/JatraTech/reactjs-ts-template). CORS and preview headers are set in `app/settings.py` — see [preview and frontend](https://github.com/JatraTech/django-backstage/blob/main/docs/features/preview-and-frontend.md).

## Customize admins

Do not add `@admin.register` in app `admin.py` for models Backstage autodiscovers; use `ADMIN_OVERRIDES` in `backstage_host.py` (see [`user/admin.py`](../../user/admin.py)).

Example patterns: [docs/examples on django-backstage](https://github.com/JatraTech/django-backstage/tree/main/docs/examples).
