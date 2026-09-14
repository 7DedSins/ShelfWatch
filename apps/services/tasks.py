"""Celery tasks. Thin: load a Service by id, then poll_health.

Pass service_id (int), never a model instance — workers JSON-serialize arguments.
"""

from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from .health import poll_health
from .models import Service


@shared_task
def poll_service(service_id: int) -> None:
    # Load inside the worker. Do not pass a Service — JSON cannot pickle the row.
    service = Service.objects.get(pk=service_id)
    poll_health(service)


@shared_task
def schedule_polls() -> int:
    """Fan-out: enqueue poll_service for every due row. Naive loop — SQLite cannot
    multiply timedelta by an integer F(); N services is tiny. NULL last_polled_at
    is due (never polled ≠ old timestamp).
    """
    now = timezone.now()
    count = 0
    rows = Service.objects.values_list("pk", "last_polled_at", "poll_interval_seconds")
    for service_id, last_polled_at, interval in rows:
        if last_polled_at is None or last_polled_at + timedelta(seconds=interval) <= now:
            # .delay fans out; calling poll_service() would HTTP inside the scheduler.
            poll_service.delay(service_id)
            count += 1
    return count
