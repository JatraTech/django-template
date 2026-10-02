# Backstage Admin Panel

Internal Django admin UI for reference hosts. Host projects define models; Backstage auto-registers them with shared changelist, change forms, navigation, preview, and editor metadata.

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

## Package layout

```
backstage/
  apps.py              # Admin site + autodiscover
  registry/            # factory, navigation, editor meta
  preview/             # tokens, routes, DRF mixin
  templates/           # Admin UI
  static/backstage/    # CSS, JS, preview
```
