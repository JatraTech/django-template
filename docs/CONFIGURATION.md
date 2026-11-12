# Configuration contract

Documentation index and layout: [README.md](README.md).

How environment variables, `app/settings.py`, and Docker Compose fit together. New projects should follow this layout; production apps (Boss, Homesteadr, memblue) use external Postgres with a single compose file (or `docker-compose.external-db.yml` in django-template).

## Flow

- **`.env.example`** — committed contract for all profiles (local active values; **staging:** / **production:** hints on each line). Copy to `.env` and adjust per [architecture/DEPLOYMENT_ENVIRONMENTS.md](architecture/DEPLOYMENT_ENVIRONMENTS.md).
- **`.env.server`** — optional gitignored copy with production values (same keys as `.env.example`).
- **`.env`** — on the machine or server; loaded by `environs` in settings.
- **`app/settings.py`** — local-safe defaults; production comes from `.env`.

`FRONTEND_URL` and `BACKEND_URL` are set once in the Bootstrap section of settings. Application code should use `settings.FRONTEND_URL`, not hardcoded production URLs.

## Rules

| Layer | Rule |
|-------|------|
| `settings.py` defaults | Local-safe only (`localhost`, `http://localhost:…`). No production hostnames in `DEFAULT_*` lists. |
| Compose `environment:` | Do not set `DB_*` when using external RDS (overrides `env_file`). Pin `REDIS_URL=redis://redis:6379` for app containers. |
| Redis | Single base `REDIS_URL` without a `/0` suffix; settings assign DB indexes in code (Homesteadr/CondHOA: `/0` broker, `/1` results, `/2` cache; MemBlue: `/0` broker, `/1` cache). |
| Compose `environment:` (MemBlue) | May inject `PLATFORM_DOMAIN`, `ADMIN_*` defaults; still pin **base** `REDIS_URL=redis://redis:6379` only — do not set `CELERY_BROKER_URL` / `CACHE_URL` / `DB_*` in compose. |

## `.env` section order

1. Core Django (`TIME_ZONE` here)
2. Database
3. Security & CORS
4. Static, media & storage
5. URLs & email
6. Redis / Celery / cache / Channels
7. Logging
8. Integrations (AWS, ecosystem, payments, monitoring, AI — use sub-comments)
9. Optional / QA
10. App-specific sections (see below)
11. Docker / runtime

CondHOA, Homesteadr, and MemBlue backends follow this skeleton in `.env.example`, `.env`, and `.env.server`.

### App-specific env sections

| App | Extra sections (after Optional / QA, before Docker) |
|-----|-----------------------------------------------------|
| CondHOA | **Application business rules**, **Ops** (`AUDIT_DOCS_DIR`) |
| Homesteadr | (none — AWS and product keys live under Integrations) |
| MemBlue | **Optional / QA:** `DEMO_*`, `LOGIN_DEMO_CODE`, `LOGIN_SKIP_MFA`. Production `FIELD_ENCRYPTION_KEYS` under Security; `ADMIN_*` under URLs & email. Trim rare keys to `docs/DEPLOYMENT.md`. |

### Ecosystem env comments (all three products)

Use the same sub-blocks under **Integrations**:

1. **RPC** — Bearer tokens inbound callers present to this API.
2. **Inbound HMAC** — verify `POST /api/v1/integrations/ecosystem/inbound/`.
3. **Outbound events** — `name|consumer|event_type_prefix|url|hmac-secret` (semicolon-separated). After changes: `python manage.py seed_outbound_subscriptions` (+ Celery worker).

## `settings.py` section order

Bootstrap → Project defaults → Core Django → Applications → Middleware → Database → Internationalization → Authentication → API → Security & CORS → Async tasks → Static, media & storage → URLs & email → Logging → Integrations → app-specific (Backstage, business rules, QA).

## Docker Compose

| File | Postgres | Use case |
|------|----------|----------|
| `docker-compose.yml` | In compose (`DB_HOST=db`) | Local development |
| `docker-compose.external-db.yml` | External / RDS (`DB_*` in `.env` only) | Production |
| `docker-compose.staging.yml` | In compose | Optional second stack on same host |
| Homesteadr / Boss / CondHOA / MemBlue `docker-compose.yml` | External / RDS (`DB_*` in `.env` only) | Production (no bundled `db`) |

**Local:**

```bash
cp .env.example .env
docker compose up -d --build
```

**Production (RDS):**

```bash
cp .env.example .env   # apply production: hints; set DB_HOST to RDS endpoint
docker compose -f docker-compose.external-db.yml up -d --build
```

**Staging (bundled Postgres):**

```bash
cp .env.example .env   # apply staging: hints (COMPOSE_PROJECT_NAME=myproject-staging, etc.)
docker compose -f docker-compose.staging.yml up -d --build
```

**Web healthcheck:** the `web` service probes `/healthz` with a **5-minute `start_period`** so migrate, collectstatic, and Gunicorn worker boot on a cold start do not fail `depends_on: service_healthy` before HTTP is ready. Probe history: `docker inspect <project>_web --format '{{json .State.Health}}' | jq`.

**Verifying deploy health:** `docker compose up -d` should exit **0**; `docker inspect <project>_web --format '{{.State.Health.Status}}'` should be `healthy`. If deploy fails while Gunicorn logs look normal, use `docker inspect … --format '{{json .State.Health.Log}}' | jq '.[-5:]'`.

Optional AWS credentials can live in `.secrets/aws.secret` (loaded at startup).
