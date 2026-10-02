import logging
import os

from celery import Celery, current_app

# set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")

logger = logging.getLogger(__name__)

celery_app = Celery("app")
celery_app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django app configs.
celery_app.autodiscover_tasks()

import app.tasks  # noqa: E402, F401 — project tasks live outside INSTALLED_APPS

extra_task_modules = []

for module in extra_task_modules:
    try:
        __import__(module)
    except ImportError:
        logger.warning(f"Could not import {module}")


def is_celery_running():
    try:
        i = current_app.control.inspect()
        ping_result = i.ping()  # Returns dict if workers alive
        return bool(ping_result)
    except Exception:
        return False


def queue_email_tasks() -> bool:
    """Whether outbound email should be handed off to Celery tasks."""
    from django.conf import settings

    if getattr(settings, "CELERY_TASK_ALWAYS_EAGER", False):
        return True
    return is_celery_running()
