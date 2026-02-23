"""
Celery configuration for agentbloom project.
"""

import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "agentbloom.settings")

app = Celery("agentbloom")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
