import os

from celery import Celery

# Worker process is not manage.py — it still needs Django settings.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
app = Celery("config")
# Only settings named CELERY_* (broker URL, eager flags).
app.config_from_object("django.conf:settings", namespace="CELERY")
# Load @shared_task from installed apps (apps.services.tasks).
app.autodiscover_tasks()
