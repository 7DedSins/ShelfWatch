"""Scan tasks go on the scans queue so a long walk cannot starve poll_service."""

from datetime import timedelta

from celery import chain, shared_task
from django.utils import timezone

from apps.reconcile.tasks import reconcile_library

from .models import Library
from .scan import scan_library


@shared_task(
    soft_time_limit=3600,
    time_limit=3660,
)
def scan_library_task(library_id: int) -> int:
    library = Library.objects.get(pk=library_id)
    return scan_library(library)


@shared_task
def schedule_scans() -> int:
    """Fan-out due libraries. Cheap; lives on default. Walks run on scans."""
    now = timezone.now()
    count = 0
    rows = Library.objects.values_list("pk", "last_scanned_at", "scan_interval_seconds")
    for library_id, last_scanned_at, interval in rows:
        due = last_scanned_at is None or (
            last_scanned_at + timedelta(seconds=interval) <= now
        )
        if due:
            # .s = signature (mutable): next task gets previous return as 1st arg.
            # .si = immutable: args stay exactly what we pass. scan returns int count;
            # reconcile_library(library_id) must not become (count, library_id).
            # Pylance types @shared_task as a plain function (no .s / .si / .delay).
            chain(
                scan_library_task.s(library_id),  # type: ignore[attr-defined]
                reconcile_library.si(library_id),  # type: ignore[attr-defined]
            ).delay()
            count += 1
    return count
