# Backstage Admin Panel

Internal Django admin UI for BPI and reference hosts. Host projects define models; Backstage auto-registers them with shared changelist, change forms, navigation, preview, and editor metadata.

Copyright © Building Plastics, Inc.

## Documentation

**Documentation:** [`docs/backstage/README.md`](../docs/backstage/README.md) — start with [integration.md](../docs/backstage/integration.md).

## Install (minimal)

```python
INSTALLED_APPS = [
    "backstage",
    "backstage.contrib.forms",
    "backstage.contrib.inlines",
    "django.contrib.admin",  # after backstage
    # ... your apps
]
```

```bash
python manage.py migrate backstage
python manage.py check_backstage_integration
```

Branding: **System → Admin appearance** (DB overrides `BACKSTAGE`).

## Inline relations (host config)

Canonical host guide: [integration.md](../docs/backstage/integration.md).

Declare parent → child edges in `BACKSTAGE["INLINE_RELATIONS"]` (compiled at startup into inlines, `STANDALONE_CHILD_MODELS`, and child `exclude` as needed):

| `mode` | Behavior |
|--------|----------|
| `default_stacked` | Editable stacked inline (factory default if omitted) |
| `default_tabular` | Editable tabular inline |
| `hub_tabular` / `hub_stacked` | Read-only summary + Edit/Delete + Add/View all footer; default **primary tab** with parent fieldset tabs |

Legacy `INLINE_HUB` + manual `ADMIN_OVERRIDES.inlines` still work; prefer `INLINE_RELATIONS` for new hosts. Escape hatch: `inline_class` dotted path on a relation entry.

## Package layout

```
backstage/
  apps.py              # Admin site + autodiscover
  registry/            # factory, navigation, editor meta
  preview/             # tokens, routes, DRF mixin
  templates/           # Admin UI
  static/backstage/    # CSS, JS, preview
```
