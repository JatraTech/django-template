# Django Startup Template

A production-ready Django REST API template with modern best practices, pre-configured authentication, async task processing, and Docker support.

**Frontend counterpart:** [`../react-marketing-template`](../react-marketing-template) — Vite + React marketing SPA (SEO prerender, RTK Query, Backstage preview).

## Features

- Django 5.2 + Django REST Framework + JWT Authentication
- Celery + Redis for async tasks and scheduled jobs
- PostgreSQL 17 database
- Docker & Docker Compose ready (multi-stage, non-root)
- uv for fast package management
- API Documentation (drf-spectacular)
- AWS S3 integration, Google OAuth support
- Universal Redis DB-index convention (broker /0, results /1, cache /2, channels /3)
- Production-ready with Gunicorn & optional Nginx
- **Backstage admin** — vendored themed CMS UI (`backstage/`) with a **`sample`** app for draft/publish, navigation, and appearance settings

## Backstage admin (reference host)

This template includes a **vendored copy** of the Backstage package from the BPI repo (`backstage/` at project root). It is wired via [`app/backstage_host.py`](app/backstage_host.py) and the [`sample`](sample/) app (demo articles, singleton pages, inquiries).

After `migrate` and `createsuperuser`, open **http://localhost:8000/admin/** and exercise:

1. **Dashboard** — sidebar entry, welcome/stats/quick actions, drafts and recent activity widgets
2. **Sample pages → Sample articles** — changelist, change form, draft/publish flow
3. **Sample site page** — inline facts on the parent form only (not a separate sidebar model)
4. **System → Admin appearance** — accent palette and theme presets
5. Changelist link colors (default text, accent on hover), empty-state **Add** button, filters, dark mode

Verify wiring:

```bash
uv run python manage.py check_backstage_integration
```

**Documentation:** [`docs/backstage/README.md`](docs/backstage/README.md) — start with [`integration.md`](docs/backstage/integration.md).

Do not add custom `@admin.register` in app `admin.py` files for models Backstage autodiscovers; use `ADMIN_OVERRIDES` in `backstage_host.py` instead (see `user/admin.py`).

## Quick Start

### Docker (Recommended)

```bash
git clone <your-repo-url>
cd django_template
cp .env.example .env   # Configure your environment
docker compose up --build
```

Access at:

- API: http://localhost:8000
- Health: http://localhost:8000/healthz
- Docs: http://localhost:8000/api/schema/docs/
- Admin: http://localhost:8000/admin/

### Local Development

```bash
git clone <your-repo-url>
cd django_template

# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Setup
uv sync
cp .env.example .env   # Configure your environment
uv run python manage.py migrate
uv run python manage.py createsuperuser

# Run services (separate terminals)
uv run python manage.py runserver 8000
uv run celery -A app worker --loglevel=INFO
uv run celery -A app beat --loglevel=INFO
```

## Customizing for a New Project

Replace `myproject` with your project name:

| File | What to Change |
|------|----------------|
| `.env` | `COMPOSE_PROJECT_NAME`, `DB_NAME` |
| `pyproject.toml` | `name = "myproject-backend"` |
| `user/templates/user/email/*.html` | Branding text |
| Root directory | Rename folder if desired |

**Tip:** Search for `myproject` (case-insensitive) throughout the project.

## Configuration

### Storage and CORS (production)

- **Local dev:** `USE_S3_STORAGE=False` (default) — static and media files on disk under `staticfiles/` and `media/`.
- **Production:** set `USE_S3_STORAGE=True` and configure `AWS_*` variables in `.env` (see `.env.example`). Do not rely on `DEBUG` to toggle S3.
- **CORS:** production uses an explicit allowlist (`CORS_ALLOWED_ORIGINS` in `.env`). Defaults include common local frontend ports (3000, 5173) and the API (8000). Backstage split-pane preview sends `x-preview-token`; that header is allowed in settings.

### Environment Variables

Create a `.env` file from `.env.example`:

```env
# Django
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_ENGINE=django.db.backends.postgresql
DB_NAME=your_db_name
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432

# Redis (base URL only — settings assign DB indexes)
REDIS_URL=redis://localhost:6379

# Docker
COMPOSE_PROJECT_NAME=your_project_name
HOST_FORWARD_APP_PORT=8000
```

If `HOST_FORWARD_APP_PORT` is not `8000`, update `CORS_ALLOWED_ORIGINS`, `CSRF_TRUSTED_ORIGINS`, and `BACKEND_URL` in `.env` to match the published API URL. See [`.env.example`](.env.example) (Docker / runtime and Celery sections) for `CELERY_WORKER_PREFETCH_MULTIPLIER`, optional `HOST_FORWARD_DB_PORT`, and `APP_UID` / `APP_GID`.

### Redis DB Registry

One Redis instance, logical separation by DB index:

| DB | Purpose |
|----|---------|
| `/0` | Celery broker |
| `/1` | Celery results (ignored by default) |
| `/2` | Django cache |
| `/3` | Channels layer (when enabled) |

Set `REDIS_URL` without a DB suffix. Override individual roles if needed:

```env
CELERY_BROKER_URL=redis://localhost:6379/0
CACHE_REDIS_URL=redis://localhost:6379/2
CHANNELS_REDIS_URL=redis://localhost:6379/3
```

### Docker Compose

Compose uses shared anchors (`x-common-env`, `x-common-runtime`, `x-common-service`) — customize via `.env`:

```env
COMPOSE_PROJECT_NAME=your_project_name
DB_NAME=your_db_name
DB_PASSWORD=your_password
HOST_FORWARD_APP_PORT=8000
HOST_BIND_ADDRESS=127.0.0.1
```

Inside Docker, `DB_HOST=db` and `REDIS_URL=redis://redis:6379` are set automatically.

**Compose conventions**

| Piece | Pattern |
|-------|---------|
| Compose project | `COMPOSE_PROJECT_NAME` (staging file uses `{name}-staging`) |
| Containers | `{COMPOSE_PROJECT_NAME}_{role}` (staging: `{name}_staging_{role}`) |
| Image | `{COMPOSE_PROJECT_NAME}-backend:latest` (staging: `:staging`) |
| Network (Docker name) | `{COMPOSE_PROJECT_NAME}_net` (staging: `{name}_staging_net`) |
| Media volume | `media_data` → `/app/media` |

Only **`web`** declares `build`; worker and beat reuse the same image (avoids parallel build/tag races). `HOST_BIND_ADDRESS` defaults to `127.0.0.1`; set `0.0.0.0` when you need LAN access to the published port. Optional `DB_MEM_LIMIT`, `REDIS_MEM_LIMIT`, `WEB_MEM_LIMIT`, `WORKER_MEM_LIMIT`, and `BEAT_MEM_LIMIT` set per-service `mem_limit`.

**HTTP server (Gunicorn vs Uvicorn)**

Docker **`web`** defaults to **Gunicorn** on `app.wsgi` (typical REST + Celery). A commented **Uvicorn** block on `app.asgi` is in `docker-compose.yml` (and `docker-compose.staging.yml` if you use staging)—uncomment it and comment out the Gunicorn `command` when you need ASGI in Docker (for example after enabling [Django Channels](#optional-django-channels)). `WEB_CONCURRENCY` sets `--workers` for either server. Uvicorn options use `UVICORN_KEEPALIVE_TIMEOUT` in `.env` (see `.env.example`).

**Upgrading from older template compose**

Older forks used volume key `media` and network name `{name}_network`. After pulling this template, Compose creates new resources unless you migrate: copy data from the old volume (e.g. `docker run --rm -v old_media:/from -v new_media_data:/to alpine cp -a /from/. /to/`) or accept a fresh dev volume. Rename or recreate external networks if other stacks referenced the old network name.

### Optional: Django Channels

1. Install dependencies:

```bash
uv add channels channels-redis daphne
```

2. Add `"channels"` to `INSTALLED_APPS` in `app/settings.py`
3. Set `CHANNELS_ENABLED=true` in `.env`
4. Configure ASGI routing in `app/asgi.py`

Redis DB `/3` is reserved for the channel layer when enabled.

## Production deploy (GitHub Actions)

This repo includes [`.github/workflows/deploy-production.yml`](.github/workflows/deploy-production.yml) (same pattern as BPI): SSH to your server, `git pull`, `docker compose build`, `docker compose up -d`.

1. Create a GitHub **Environment** named `Production`.
2. Add repository secrets (or environment secrets):
   - `REMOTE_HOST` — server hostname or IP
   - `REMOTE_USER` — SSH user
   - `REMOTE_SSH_KEY` — private key (PEM)
   - `REMOTE_PATH` — absolute path to the project on the server (contains `docker-compose.yml`)
3. Push to `main` or run the workflow manually (**workflow_dispatch**).

The workflow does **not** run tests; run `pytest` and `check_backstage_integration` in CI or locally before deploy. On the server, set `USE_S3_STORAGE=True` and AWS vars in `.env` when using object storage.

## Project Structure

```
.
├── app/                # Django project settings
├── user/               # User app with authentication
├── templates/          # HTML templates
├── staticfiles/        # Collected static files
├── media/              # Media uploads
├── docker-compose.yml
├── Dockerfile
├── entrypoint.sh
└── pyproject.toml
```

## Common Commands

```bash
# Django
uv run python manage.py startapp <app_name>
uv run python manage.py makemigrations
uv run python manage.py migrate
uv run python manage.py collectstatic

# Dependencies
uv add <package-name>

# Docker
docker compose up -d
docker compose logs -f
docker compose exec web python manage.py shell
docker compose down
```

## API Documentation

- **Swagger UI**: `/api/schema/docs/`
- **ReDoc**: `/api/schema/redoc/`
- **OpenAPI Schema**: `/api/schema/`

## Key Features

**JWT Authentication**

```python
# Endpoints
POST /api/auth/login/      # Get tokens
POST /api/auth/refresh/    # Refresh token
POST /api/auth/register/   # Register user
```

**Celery Tasks**

```python
from celery import shared_task

@shared_task
def your_task():
    pass
```

## Deployment

### Local / manual

1. Configure environment variables (`.env`)
2. Run `docker compose up --build` (migrations and collectstatic run on web startup)
3. Optionally front with `nginx.conf` as a reverse proxy

### GitHub Actions (SSH + Docker on server)

| Branch | Workflow | GitHub environment |
|--------|----------|----------------------|
| `main` | [deploy-production.yml](.github/workflows/deploy-production.yml) | **Production** |
| `staging` | [deploy-staging.yml](.github/workflows/deploy-staging.yml) | **Staging** |

**Production secrets:** `REMOTE_HOST`, `REMOTE_USER`, `REMOTE_SSH_KEY`, `REMOTE_PATH` (git checkout on server).

**Staging secrets:** `STAGING_REMOTE_HOST`, `STAGING_REMOTE_USER`, `STAGING_REMOTE_SSH_KEY`, `STAGING_REMOTE_PATH`.

Staging uses [`docker-compose.staging.yml`](docker-compose.staging.yml) (separate Compose project, `:staging` image tag, `{name}_staging_net` network, isolated volumes). It mirrors `docker-compose.yml` for services, limits, and HTTP server blocks—when you change production compose, apply the same edit to staging except for the staging `name`, image tag, container names, and network name. Set `COMPOSE_PROJECT_NAME`, `DB_NAME`, `HOST_FORWARD_APP_PORT`, and `HOST_BIND_ADDRESS` in staging `.env` so staging does not collide with production on the same host (use a different host port than prod, e.g. `8001`).

**Frontend:** pair with [`../react-marketing-template`](../react-marketing-template) — use its `deploy-production.yml` / `deploy-staging.yml` (static `dist/` rsync) for the React site.

## License

MIT License - feel free to use this template for your projects.
