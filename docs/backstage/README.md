# Backstage documentation

Backstage is a self-contained Django admin package. Host projects add models; Backstage auto-registers them with shared changelist, change forms, navigation, preview, and editor metadata.

**Start here:** **[integration.md](integration.md)** — single onboarding path (`backstage_host.py`).

**This repo:** live reference host — vendored [`backstage/`](../../backstage/), demo [`sample/`](../../sample/) app, [`app/backstage_host.py`](../../app/backstage_host.py). Run `python manage.py check_backstage_integration` from the project root.

## Reading order

| Step | Document | When to read |
|------|----------|--------------|
| 1 | [guides/quickstart.md](guides/quickstart.md) | Step-by-step install |
| 2 | [guides/host-contract.md](guides/host-contract.md) | CMS model conventions |
| 3 | [reference/configuration.md](reference/configuration.md) | Every `BACKSTAGE` key |
| 4 | [reference/auto-admin.md](reference/auto-admin.md) | Autodiscover and factory |
| 5 | [features/customization.md](features/customization.md) | Overrides |
| 6 | [features/preview-and-frontend.md](features/preview-and-frontend.md) | Preview + API |
| 7 | [features/editor-ux.md](features/editor-ux.md) | Editor meta policy |
| 8 | [operations/troubleshooting.md](operations/troubleshooting.md) | Failures and manual QA |
| 9 | [features/draft-publish.md](features/draft-publish.md) | Draft rows + preview |
| 10 | [guides/copy-to-new-project.md](guides/copy-to-new-project.md) | Copy `backstage/` to another project |

Host config template:

```bash
cp docs/backstage/examples/backstage_host.example.py yourapp/backstage_host.py
```

## Verification

```bash
python manage.py check_backstage_integration
```

| Term | Meaning |
|------|---------|
| **Backstage** | The `backstage/` Python package |
| **Host project** | Your Django project apps |
| **`backstage_host.py`** | Single host config module (nav, overrides, editor meta, preview) |
| **`BACKSTAGE`** | Settings dict merged with package defaults |
| **Admin appearance** | DB-backed branding singleton |

## Host module checklist

| Export | Purpose |
|--------|---------|
| `NAV_GROUPS`, `MODEL_ICONS`, `MODEL_LABELS` | Sidebar |
| `ADMIN_OVERRIDES` | Per-model admin attrs |
| `FIELD_EDITOR_META`, `TAB_DESCRIPTIONS` | Editor UX |
| `resolve_preview_route` | Preview iframe paths |

Wire in `settings.py`; set `PREVIEW_ROUTE_CALLBACK` to `"yourapp.backstage_host.resolve_preview_route"`.

## Verification

```bash
python manage.py check_backstage_integration
```
