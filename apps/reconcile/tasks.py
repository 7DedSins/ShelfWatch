from celery import shared_task

from apps.libraries.models import Library

from .engine import reconcile_library as run_reconcile


@shared_task(soft_time_limit=600, time_limit=660)
def reconcile_library(library_id: int) -> int:
    library = Library.objects.select_related("service").get(pk=library_id)
    return run_reconcile(library)
