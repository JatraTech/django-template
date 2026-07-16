from pathlib import Path
from datetime import timedelta
from urllib.parse import urlparse

from environs import Env

env = Env()
env.read_env()
env.read_env(path=".secrets/aws.secret")

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY", default="django-insecure-change-this-in-production")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("DEBUG", False)
ALLOWED_HOSTS = ["*"] if DEBUG else env.list("ALLOWED_HOSTS", "localhost,127.0.0.1")

# Application definition

CORE_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
]
THIRD_PARTY_APPS = [
    "rest_framework",
    "django_userforeignkey",
    "drf_standardized_errors",
    "drf_spectacular",
    "django_filters",
    "corsheaders",
    "django_extensions",
    "django_celery_beat",
    "storages",
    "django_celery_results",
]

APPS = [
    "user",
]

INSTALLED_APPS = (
    CORE_APPS
    + THIRD_PARTY_APPS
    + APPS
    + [
        # Must be last — deletes FileField/ImageField files on model delete and replace.
        "django_cleanup.apps.CleanupConfig",
    ]
)

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

ROOT_URLCONF = "app.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": ["templates"],
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

WSGI_APPLICATION = "app.wsgi.application"

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

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

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-us"
TIME_ZONE = "America/Chicago"
USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = "user.User"

AUTHENTICATION_BACKENDS = [
    "app.utils.backends.authentication.StatusBackend",
]

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "EXCEPTION_HANDLER": "drf_standardized_errors.handler.exception_handler",
    "DEFAULT_VERSIONING_CLASS": "rest_framework.versioning.NamespaceVersioning",
    "DEFAULT_PAGINATION_CLASS": "app.utils.pagination.StandardPagination",
    "DEFAULT_RENDERER_CLASSES": ("app.utils.renderers.SuccessJsonResponse",),
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
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

# CORS Settings
if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True
else:
    # CORS_ALLOWED_ORIGINS = [

    # ] #TODO: !IMPORTANT: Update this list with actual origins before deployment

    CORS_ALLOW_ALL_ORIGINS = True

# CSRF Trusted Origins
CSRF_TRUSTED_ORIGINS = env.list(
    "CSRF_TRUSTED_ORIGINS",
    default="http://localhost:8000,http://localhost:8080,http://127.0.0.1:8000,http://127.0.0.1:8080",
)

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=7),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=15),
}

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


# LOGGING = {
#     "version": 1,
#     "disable_existing_loggers": False,
#     "handlers": {
#         "file": {
#             "level": "DEBUG",
#             "class": "logging.FileHandler",
#             "filename": "logs/django.log",
#             "formatter": "verbose",
#         },
#     },
#     "formatters": {
#         "verbose": {
#             "format": "[{asctime}] {levelname} {name}: {message}",
#             "style": "{",
#         },
#     },
#     "loggers": {
#         "django": {
#             "handlers": ["file"],
#             "level": "INFO",
#             "propagate": False,
#         },
#     },
# }



SECURE_PROXY_SSL_HEADER = (
    "HTTP_X_FORWARDED_PROTO",
    env("SECURE_PROXY_SSL_HEADER", default="https"),
)

# Storage Settings
if not DEBUG:
    STORAGES = {
        "default": {
            "BACKEND": "storages.backends.s3.S3Storage",
            "OPTIONS": {
                "file_overwrite": False,
                "location": "media",
            },
        },
        "staticfiles": {
            "BACKEND": "storages.backends.s3.S3Storage",
            "OPTIONS": {
                # "file_overwrite": True,
                "location": "static",
            },
        },
    }
    AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME", default="")
    AWS_S3_REGION_NAME = env("AWS_S3_REGION_NAME", default="us-east-2")
    AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com"
    STATIC_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/static/"
else:
    STATIC_URL = "static/"
    MEDIA_URL = "media/"
    MEDIA_ROOT = "media"
    STATIC_ROOT = "staticfiles"

# Email Configuration
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="noreply@example.com")
