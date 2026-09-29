# Quickstart — integrate Backstage into a Django project

## 1. Copy the package

Copy the entire `backstage/` directory into your Django project root (same level as `manage.py`).

## 2. `INSTALLED_APPS` order

**`backstage` must be first.** Contrib sub-apps:

```python
INSTALLED_APPS = [
    "backstage",
    "backstage.contrib.forms",
    "backstage.contrib.inlines",
    "django.contrib.admin",  # after backstage — see reference/auto-admin.md
    "django.contrib.auth",
    # ...
    "your_app",
]
```

Why `django.contrib.admin` comes after Backstage: `BackstageConfig.ready()` replaces `admin.site` and registers all models first; your `admin.py` loads later for unregister/re-register overrides.

## 3. Host config file

```bash
cp docs/backstage/examples/backstage_host.example.py yourapp/backstage_host.py
```

## 4. Settings

```python
# settings.py
FRONTEND_URL = "http://localhost:5173"

from yourapp.backstage_host import (
    ADMIN_OVERRIDES,
    FIELD_EDITOR_META,
    MODEL_ICONS,
    MODEL_LABELS,
    NAV_GROUPS,
    TAB_DESCRIPTIONS,
)

BACKSTAGE = {
    "SITE_TITLE": "Acme Admin",
    "SITE_HEADER": "Acme Corp",
    "SITE_SUBHEADER": "Content management",
    "SITE_URL": FRONTEND_URL,
    "NAV_GROUPS": NAV_GROUPS,
    "MODEL_ICONS": MODEL_ICONS,
    "MODEL_LABELS": MODEL_LABELS,
    "PREVIEW_ROUTE_CALLBACK": "yourapp.backstage_host.resolve_preview_route",
    "ADMIN_OVERRIDES": ADMIN_OVERRIDES,
    "FIELD_EDITOR_META": FIELD_EDITOR_META,
    "TAB_DESCRIPTIONS": TAB_DESCRIPTIONS,
}
```

See [examples/settings_snippet.py](examples/settings_snippet.py) and [../reference/configuration.md](../reference/configuration.md).

## 5. URLs

```python
urlpatterns = [
    path("backstage/", include("backstage.urls")),
    path("admin/", admin.site.urls),
]
```

For rich text, add a TinyMCE upload route and `django-tinymce`. See [../features/editor-ux.md](../features/editor-ux.md).

## 6. Migrate

```bash
python manage.py migrate backstage
python manage.py migrate
```

## 7. Superuser and smoke test

```bash
python manage.py createsuperuser
python manage.py runserver
```

Open `/admin/`. Confirm **System → Admin appearance** opens.

## 8. Models

Follow [host-contract.md](host-contract.md). Copy [examples/host_singleton.py](examples/host_singleton.py) and [examples/host_seo_mixin.py](examples/host_seo_mixin.py) if needed.

No per-app `admin.py` required — Backstage autodiscovers on startup.

## 9. Integration check

```bash
python manage.py check_backstage_integration
```

## 10. New project checklist

1. Copy `backstage/` into the project.
2. `INSTALLED_APPS` order + `migrate backstage`.
3. Copy `backstage_host.example.py` → `yourapp/backstage_host.py` and customize.
4. Wire `BACKSTAGE` + URLs in `settings.py`.
5. Use `SingletonModel` for one-row CMS pages.
6. Configure **Admin appearance** per environment.
7. Run `check_backstage_integration`.

See [../integration.md](../integration.md).
