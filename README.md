# Django Startup Template 🚀

A production-ready Django REST API template with modern best practices, pre-configured authentication, async task processing, and Docker support.

## ✨ Features

- Django 5.2 + Django REST Framework + JWT Authentication
- Celery + Redis for async tasks and scheduled jobs
- PostgreSQL 17 database
- Docker & Docker Compose ready
- uv for fast package management
- API Documentation (drf-spectacular)
- AWS S3 integration, Google OAuth support
- Production-ready with Gunicorn & Nginx

## 🚀 Quick Start

### Docker (Recommended)

```bash
git clone <your-repo-url>
cd rox_backend
cp .env.example .env  # Configure your environment
docker-compose up --build
```

Access at:
- API: http://localhost:8080
- Docs: http://localhost:8080/api/schema/docs/
- Admin: http://localhost:8080/admin/

### Local Development

```bash
git clone <your-repo-url>
cd rox_backend

# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Setup
uv sync
cp .env.example .env  # Configure your environment
uv run python manage.py migrate
uv run python manage.py createsuperuser

# Run services (separate terminals)
uv run python manage.py runserver 7000
uv run celery -A app worker --loglevel=INFO
uv run celery -A app beat --loglevel=INFO
```

## 🎨 Customizing Project Name

This template uses "rox" as default. Replace it with your project name:

| File | What to Change |
|------|----------------|
| `docker-compose.yml` | `project_name`, container names, network name |
| `pyproject.toml` | `name = "rox-backend"` |
| `.env` | `DEF_DB_NAME=rox` |
| `user/templates/user/email/on_active_password_reset.html` | "Welcome to Rox", "The Rox Team" |
| Root directory | Rename `rox_backend/` folder |

**💡 Tip:** Use find & replace to search "rox" (case-insensitive) throughout the project.

## ⚙️ Configuration

### Environment Variables

Create a `.env` file:

```env
# Django
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DEF_DB_ENGINE=django.db.backends.postgresql
DEF_DB_NAME=your_db_name
DEF_DB_USER=postgres
DEF_DB_PASSWORD=postgres
DEF_DB_HOST=localhost
DEF_DB_PORT=5432

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0

# AWS S3 (Optional)
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AWS_STORAGE_BUCKET_NAME=your-bucket

# Google OAuth (Optional)
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-secret
```

### Docker Compose

Update `docker-compose.yml`:

```yaml
x-variables:
  project_name: &project_name your_project_name
  postgres_user: &postgres_user postgres
  postgres_password: &postgres_password your_password
```

## 📁 Project Structure

```
.
├── app/                # Django project settings
├── user/               # User app with authentication
├── templates/          # HTML templates
├── staticfiles/        # Static files
├── media/             # Media uploads
├── docker-compose.yml
├── Dockerfile
└── pyproject.toml
```

## 🔧 Common Commands

```bash
# Django
uv run python manage.py startapp <app_name>
uv run python manage.py makemigrations
uv run python manage.py migrate
uv run python manage.py collectstatic

# Dependencies
uv add <package-name>

# Docker
docker-compose up -d
docker-compose logs -f
docker-compose exec web python manage.py shell
docker-compose down
```

## 📚 API Documentation

- **Swagger UI**: `/api/schema/docs/`
- **ReDoc**: `/api/schema/redoc/`
- **OpenAPI Schema**: `/api/schema/`

## 🎯 Key Features

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
    # Your async task logic
    pass
```

## 🚢 Deployment

1. Configure production environment variables
2. Build and push Docker image
3. Run migrations and collect static files
4. Start services with docker-compose

## 📝 License

MIT License - feel free to use this template for your projects.

---

**Happy Coding!** 🎉