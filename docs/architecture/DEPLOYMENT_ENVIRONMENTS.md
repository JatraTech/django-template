# Deployment environments

Reference contract for local, staging, and production. **Filled example:** [CondHOA](../../../condhoa/condhoa-backend/docs/architecture/DEPLOYMENT_ENVIRONMENTS.md).

## Variables

| Variable | Values | Role |
|----------|--------|------|
| `APP_ENV` | `local` \| `staging` \| `production` | Which deploy this is |
| `DEBUG` | `1` local, `0` deployed | Django dev behavior only |
| `DEMO_ENABLED` | `true` / `false` | Demo seed, QA catalog API, SPA quick login (if applicable) |

Defaults in `app/settings.py`: `DEMO_ENABLED` defaults to on when `APP_ENV` is not `production`.

## Invariants

| `APP_ENV` | `DEBUG` | `DEMO_ENABLED` |
|-----------|---------|----------------|
| `local` | `1` | optional (default on) |
| `staging` | `0` | `1` (typical) |
| `production` | `0` | `0` |

Startup check `validate_app_env` (see `app/utils/checks.py`): production refuses `DEMO_ENABLED` or `DEBUG`.

## Env files

| File | Use |
|------|-----|
| `.env.example` | All keys; local defaults with inline **staging:** / **production:** hints — copy to `.env` |

See [CONFIGURATION.md](../CONFIGURATION.md) for compose file choices.

## Profile checklist (template)

| | Local | Staging | Production |
|---|--------|---------|------------|
| `APP_ENV` | `local` | `staging` | `production` |
| `DEBUG` | `1` | `0` | `0` |
| `DEMO_ENABLED` | `true` (typical) | `true` | `false` |
| Compose | `docker compose up` | `docker-compose.staging.yml` | `docker-compose.external-db.yml` |
| Postgres | bundled `db` in compose | bundled `db` | RDS in `.env` |

Replace example hostnames in `.env.example` hints with your product domains.

## Commands (product-specific)

| Kind | When | Example |
|------|------|---------|
| Bootstrap / real data | Production | `python manage.py seed_*` (your product command) |
| Demo / QA fixture | Staging + local when demo on | `python manage.py seed_demo_data` — must refuse when `DEMO_ENABLED=0` |

## Frontend (if SPA)

- Staging build: `VITE_DEMO_ENABLED=true` + shared QA password when using quick login
- Production build: demo flags off

## Optional staging safety

`EMAIL_RECIPIENTS_OVERRIDE` / SMS overrides redirect outbound messages; optional, not tied to `DEMO_ENABLED`.

## Related

- [QA_DEMO.md](QA_DEMO.md)
- [CONFIGURATION.md](../CONFIGURATION.md)
- [examples/qa_accounts_stub.py](examples/qa_accounts_stub.py)
