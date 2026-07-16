# Django Startup Template

A production-ready Django REST API template with modern best practices, pre-configured authentication, async task processing, and Docker support.

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

## Quick Start

### Docker (Recommended)

```bash
git clone <your-repo-url>
cd django_template
cp .env.example .env   # Configure your environment
docker compose up --build
```

Access at:

- API: http://localhost:8050
- Health: http://localhost:8050/healthz
- Docs: http://localhost:8050/api/schema/docs/
- Admin: http://localhost:8050/admin/

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
HOST_FORWARD_APP_PORT=8050
```

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

Compose uses shared anchors — customize via `.env`:

```env
COMPOSE_PROJECT_NAME=your_project_name
DB_NAME=your_db_name
DB_PASSWORD=your_password
HOST_FORWARD_APP_PORT=8050
```

Inside Docker, `DB_HOST=db` and `REDIS_URL=redis://redis:6379` are set automatically.

### Optional: Django Channels

1. Install dependencies:

```bash
uv add channels channels-redis daphne
```

2. Add `"channels"` to `INSTALLED_APPS` in `app/settings.py`
3. Set `CHANNELS_ENABLED=true` in `.env`
4. Configure ASGI routing in `app/asgi.py`

Redis DB `/3` is reserved for the channel layer when enabled.

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

1. Configure production environment variables
2. Build and push Docker image
3. Run `docker compose up` (migrations and collectstatic run on web startup)
4. Optionally front with `nginx.conf` as a reverse proxy

## License

MIT License - feel free to use this template for your projects.
