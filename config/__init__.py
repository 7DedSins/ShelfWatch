# Importing Django loads the Celery app so @shared_task binds to this instance,
# not a leftover default app. `celery -A config` uses the same object.
from .celery import app as celery_app

__all__ = ("celery_app",)
