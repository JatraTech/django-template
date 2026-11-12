# Product API patterns (analytics / export)

This starter is a **minimal reference host**: JWT auth, `user`, `sample`, and Backstage. DRF plumbing comes from **django-jt** (`BaseModelViewSet`, filters, pagination, optional mail). It does not ship sample analytics URLs.

## django-jt (preferred)

Install **`django-jt[all]`** (includes the `analytics` extra: pydantic, polars, styleframe). Import from the package:

| Piece | Module |
|-------|--------|
| `AnalyticsData`, `DataType` | `django_jt.analytics` |
| `AnalyticsDataViewMixin`, `AnalyticsGraphViewMixin` | `django_jt.mixins.analytics` |
| `ExportMixin` (`export/xlsx`) | `django_jt.mixins.export` |
| `AdminOnly` | `django_jt.permissions` (`DJANGO_JT_ADMIN_ROLES`, default `admin`) |
| Audience-scoped lists | `django_jt.filters.AudienceFilter` + `audience_lookups` on views |

See [django-jt README](https://github.com/JatraTech/django-jt/blob/main/README.md) and [CHANGELOG](https://github.com/JatraTech/django-jt/blob/main/CHANGELOG.md) (0.3.0).

## Product repos

Older APIs may still duplicate code under `app/utils/`. When migrating, switch imports to django-jt and delete local copies. Domain-specific RBAC and example analytics URL wiring remain in product repos until migrated.

## Related

- Optional QA stub: [`examples/qa_accounts_stub.py`](examples/qa_accounts_stub.py)
- Architecture hub: [ARCHITECTURE.md](../ARCHITECTURE.md)
