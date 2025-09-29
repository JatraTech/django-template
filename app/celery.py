from __future__ import absolute_import, unicode_literals
import logging
import os
from celery import Celery
from celery.signals import setup_logging, worker_ready

# set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")

logger = logging.getLogger(__name__)

app = Celery("app")
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()
