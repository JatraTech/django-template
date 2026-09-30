import logging
import os

from celery import Celery, current_app
from celery.signals import setup_logging, worker_process_init, worker_ready

# set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")

logger = logging.getLogger(__name__)

app = Celery("app")
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

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
