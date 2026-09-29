# Backstage Admin Panel

Internal Django admin UI for BPI and reference hosts. Host projects define models; Backstage auto-registers them with shared changelist, change forms, navigation, preview, and editor metadata.

Copyright © Building Plastics, Inc.

## Documentation

**Canonical docs** live in the reference host repo:

**[`django_template/docs/backstage/README.md`](../../django_template/docs/backstage/README.md)**

Start with [`integration.md`](../../django_template/docs/backstage/integration.md). Copy [`backstage_host.example.py`](../../django_template/docs/backstage/examples/backstage_host.example.py) into your project as `yourapp/backstage_host.py`.

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
