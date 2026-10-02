from datetime import timedelta
from pathlib import Path
from urllib.parse import urlparse

from corsheaders.defaults import default_headers
from environs import Env

# =============================================================================
# Bootstrap & helpers
# =============================================================================
env = Env()
env.read_env()

BASE_DIR = Path(__file__).resolve().parent.parent

_aws_secret = BASE_DIR / ".secrets" / "aws.secret"
if _aws_secret.exists():
    env.read_env(path=str(_aws_secret))

BACKEND_URL = env("BACKEND_URL", default="http://localhost:8000")
BACKEND_DOMAIN = urlparse(BACKEND_URL).netloc
FRONTEND_URL = env("FRONTEND_URL", default="http://localhost:3000")

# =============================================================================
# Project defaults
# =============================================================================
DEFAULT_ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "0.0.0.0",
]
DEFAULT_CORS_ALLOWED_ORIGINS = [
    "http://127.0.0.1:3000",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://localhost:5173",
    "http://127.0.0.1:8000",
    "http://localhost:8000",
]
DEFAULT_CSRF_TRUSTED_ORIGINS = [
    "http://127.0.0.1:3000",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://localhost:5173",
    "http://127.0.0.1:8000",
    "http://localhost:8000",
]


# =============================================================================
# Core Django
# =============================================================================
SECRET_KEY = env("SECRET_KEY", default="django-insecure-change-this-in-production")
DEBUG = env.bool("DEBUG", default=False)
ALLOWED_HOSTS = ["*"] if DEBUG else env.list("ALLOWED_HOSTS", default=DEFAULT_ALLOWED_HOSTS)

ROOT_URLCONF = "app.urls"
# Docker: Gunicorn → app.wsgi (default); optional Uvicorn → app.asgi (see docker-compose.yml web command).
WSGI_APPLICATION = "app.wsgi.application"
ASGI_APPLICATION = "app.asgi.application"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# =============================================================================
# Applications
# =============================================================================
DJANGO_APPS = [
    "backstage",
    "backstage.contrib.forms",
    "backstage.contrib.inlines",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
]
THIRD_PARTY_APPS = [
    "tinymce",
    "rest_framework",
    "django_userforeignkey",
    "drf_standardized_errors",
    "drf_spectacular",
    "django_filters",
    "corsheaders",
    "django_extensions",
    "django_celery_beat",
    "django_celery_results",
    "storages",
]
LOCAL_APPS = [
    "user",
    "sample",
]

INSTALLED_APPS = (
    DJANGO_APPS
    + THIRD_PARTY_APPS
    + LOCAL_APPS
    + [
        # Must be last so file-deletion signals run after other app handlers.
        "django_cleanup.apps.CleanupConfig",
    ]
)


# =============================================================================
# Middleware & templates
# =============================================================================
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    # "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_userforeignkey.middleware.UserForeignKeyMiddleware",
    "app.middlewares.OverrideContentTypeMiddleware",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


# =============================================================================
# Database
# =============================================================================
DATABASES = {
    "default": {
        "ENGINE": env("DB_ENGINE", default="django.db.backends.postgresql"),
        "NAME": env("DB_NAME", default="myproject"),
        "USER": env("DB_USER", default="postgres"),
        "PASSWORD": env("DB_PASSWORD", default="postgres"),
        "HOST": env("DB_HOST", default="localhost"),
        "PORT": env("DB_PORT", default="5432"),
        "CONN_MAX_AGE": env.int("DB_CONN_MAX_AGE", default=600),
    }
}


# =============================================================================
# Internationalization & localization
# =============================================================================
LANGUAGE_CODE = "en-us"
TIME_ZONE = env("TIME_ZONE", default="America/Chicago")
USE_I18N = True
USE_TZ = True


# =============================================================================
# Authentication
# =============================================================================
AUTH_USER_MODEL = "user.User"
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
AUTHENTICATION_BACKENDS = [
    "app.utils.backends.authentication.StatusBackend",
]


# =============================================================================
# API (DRF, JWT, Spectacular)
# =============================================================================
REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "EXCEPTION_HANDLER": "drf_standardized_errors.handler.exception_handler",
    "DEFAULT_VERSIONING_CLASS": "rest_framework.versioning.NamespaceVersioning",
    "DEFAULT_PAGINATION_CLASS": "app.utils.pagination.StandardPagination",
    "DEFAULT_RENDERER_CLASSES": ("app.utils.renderers.SuccessJsonResponse",),
    "DEFAULT_AUTHENTICATION_CLASSES": ("rest_framework_simplejwt.authentication.JWTAuthentication",),
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
        "app.utils.filters.ExtendedSearchFilter",
        "app.utils.filters.AudienceFilter",
        "app.utils.ordering.CustomOrderingFilter",
    ),
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}

DRF_STANDARDIZED_ERRORS = {
    "EXCEPTION_FORMATTER_CLASS": "app.utils.exceptions.ExceptionFormatter",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Django REST API",
    "DESCRIPTION": """1. Make sure to set content-type to: `multipart/form-data` if you are uploading an image or a file.\n 2. For unsafe methods [POST/PATCH/PUT/DELETE], always append `/` if not told otherwise.""",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "SCHEMA_PATH_PREFIX": "/api/v[0-9]",
    "SERVE_AUTHENTICATION": ["rest_framework.authentication.SessionAuthentication"],
    "COMPONENT_SPLIT_REQUEST": True,
    "SWAGGER_UI_SETTINGS": {"deepLinking": True, "persistAuthorization": True},
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=7),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=15),
}


# =============================================================================
# Security & CORS
# =============================================================================
USE_X_FORWARDED_HOST = True
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = env.list(
    "CORS_ALLOWED_ORIGINS",
    default=DEFAULT_CORS_ALLOWED_ORIGINS,
)
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = (
    *default_headers,
    "x-preview-token",
)
CORS_EXPOSE_HEADERS = [
    "Content-Disposition",
]
CSRF_TRUSTED_ORIGINS = env.list(
    "CSRF_TRUSTED_ORIGINS",
    default=DEFAULT_CSRF_TRUSTED_ORIGINS,
)
X_FRAME_OPTIONS = "DENY"

if not DEBUG:
    # HTTPS
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = True
    # HSTS
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = False
    # Browser security
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_REFERRER_POLICY = "same-origin"
    # Cookies
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SAMESITE = "Lax"
    CSRF_COOKIE_SAMESITE = "Lax"


# =============================================================================
# Async tasks (Celery, Redis cache, optional Channels)
# =============================================================================
def normalize_redis_base(url: str) -> str:
    url = url.rstrip("/")
    parsed = urlparse(url)
    if parsed.path and parsed.path != "/":
        raise ValueError("REDIS_URL must not include DB index")
    return url


REDIS_URL = normalize_redis_base(env("REDIS_URL", default="redis://localhost:6379"))


def redis_url(db: int, override: str) -> str:
    return env(override, default=f"{REDIS_URL}/{db}")


CELERY_BROKER_URL = redis_url(0, "CELERY_BROKER_URL")
CELERY_RESULT_BACKEND = redis_url(1, "CELERY_RESULT_BACKEND")
CELERY_TASK_IGNORE_RESULT = env.bool("CELERY_TASK_IGNORE_RESULT", default=True)
CELERY_ACCEPT_CONTENT = ["json", "pickle"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"
CELERY_BEAT_SCHEDULE = {}

CACHE_REDIS_URL = redis_url(2, "CACHE_REDIS_URL")
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": CACHE_REDIS_URL,
        "TIMEOUT": 120,
    }
}

CHANNELS_ENABLED = env.bool("CHANNELS_ENABLED", default=False)
if CHANNELS_ENABLED:
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {
                "hosts": [redis_url(3, "CHANNELS_REDIS_URL")],
            },
        },
    }


# =============================================================================
# Static, media & storage
# =============================================================================
STATIC_ROOT = BASE_DIR / "staticfiles"
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

USE_S3_STORAGE = env.bool("USE_S3_STORAGE", default=False)

if USE_S3_STORAGE:
    AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME")
    AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY")

    AWS_S3_ENDPOINT_URL = env("AWS_S3_ENDPOINT_URL", default="").strip() or None
    AWS_S3_CUSTOM_DOMAIN = env("AWS_S3_CUSTOM_DOMAIN", default="").strip() or None

    AWS_S3_FILE_OVERWRITE = False
    AWS_QUERYSTRING_AUTH = True
    AWS_QUERYSTRING_EXPIRE = 86400

    STORAGES = {
        "default": {
            "BACKEND": "storages.backends.s3.S3Storage",
            "OPTIONS": {"location": "media"},
        },
        "staticfiles": {
            "BACKEND": "storages.backends.s3.S3Storage",
            "OPTIONS": {"location": "static"},
        },
    }

    if AWS_S3_CUSTOM_DOMAIN:
        STATIC_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/static/"
        MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/media/"


# =============================================================================
# Communications
# =============================================================================
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="noreply@example.com")
EMAIL_RECIPIENTS_OVERRIDE = env.list("EMAIL_RECIPIENTS_OVERRIDE", default=[])

GOOGLE_CLIENT_ID = env("GOOGLE_CLIENT_ID", default="")
GOOGLE_CLIENT_SECRET = env("GOOGLE_CLIENT_SECRET", default="")

OPENAI_API_KEY = env("OPENAI_API_KEY", default="")
OPENAI_MODEL = env("OPENAI_MODEL", default="gpt-4o-mini")
OPENAI_EMBEDDING_MODEL = env("OPENAI_EMBEDDING_MODEL", default="text-embedding-3-small")


# =============================================================================
# Backstage (admin UI)
# =============================================================================
from app.backstage_host import (  # noqa: E402
    ADMIN_OVERRIDES,
    DASHBOARD,
    FIELD_EDITOR_META,
    MODEL_ICONS,
    MODEL_LABELS,
    NAV_GROUPS,
    TAB_DESCRIPTIONS,
)

BACKSTAGE = {
    "SITE_TITLE": "Template Admin",
    "SITE_HEADER": "Django Template",
    "SITE_SUBHEADER": "Backstage reference host",
    "SITE_URL": FRONTEND_URL,
    "NAV_GROUPS": NAV_GROUPS,
    "MODEL_ICONS": MODEL_ICONS,
    "MODEL_LABELS": MODEL_LABELS,
    "PREVIEW_ROUTE_CALLBACK": "app.backstage_host.resolve_preview_route",
    "DRAFT_PUBLISH": {
        "enabled": True,
        "models": ["sample.samplearticle"],
    },
    "ADMIN_OVERRIDES": ADMIN_OVERRIDES,
    "FIELD_EDITOR_META": FIELD_EDITOR_META,
    "TAB_DESCRIPTIONS": TAB_DESCRIPTIONS,
    "DASHBOARD": DASHBOARD,
    "SKIP_APP_LABELS": [
        "contenttypes",
        "sessions",
        "admin",
        "django_celery_beat",
        "django_celery_results",
    ],
}


# =============================================================================
# Logging
# =============================================================================
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {"verbose": {"format": "{asctime} [{levelname}] {name}: {message}", "style": "{"}},
    "handlers": {"console": {"class": "logging.StreamHandler", "formatter": "verbose"}},
    "loggers": {
        "django": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "django.server": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "gunicorn": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "uvicorn": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "daphne": {"handlers": ["console"], "level": "INFO", "propagate": False},
    },
    "root": {"handlers": ["console"], "level": "INFO"},
}


# =============================================================================
# TinyMCE (admin rich text)
# =============================================================================
TINYMCE_DEFAULT_CONFIG = {
    "height": 400,
    "menubar": False,
    "plugins": "link image lists advlist",
    "toolbar": "undo redo | bold italic underline | bullist numlist | link image",
    "automatic_uploads": True,
    "images_upload_handler": "tinymceImageUploadHandler",
    "relative_urls": False,
    "remove_script_host": False,
    "content_style": (
        "body { font-family: system-ui, sans-serif; font-size: 14px; "
        "background-color: transparent; margin: 0.5rem; } "
        "a, a:visited { color: var(--color-primary-600); text-decoration: underline; } "
        "a:hover { color: var(--color-primary-700); }"
    ),
}
