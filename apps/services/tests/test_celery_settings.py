"""Celery policy in Django settings. AI-written [!].

No broker, no Beat process. These tests would have caught the typos
(service vs services, tasks vs task, scehdule).
"""

from django.conf import settings

from apps.services.connectors.base import (
    ServiceAuthFailed,
    ServiceBadResponse,
    ServiceUnavailable,
)
from apps.services.tasks import poll_service, schedule_polls


def test_no_result_backend():
    assert getattr(settings, "CELERY_RESULT_BACKEND", None) is None


def test_acks_late_and_prefetch_for_long_tasks_later():
    assert settings.CELERY_TASK_ACKS_LATE is True
    assert settings.CELERY_WORKER_PREFETCH_MULTIPLIER == 1


def test_default_and_scans_queues_exist():
    queues = settings.CELERY_TASK_QUEUES
    assert set(queues) == {"default", "scans"}
    assert queues["default"]["routing_key"] == "default"
    assert queues["scans"]["routing_key"] == "scans"
    assert queues["scans"]["exchange"] == "scans"
    assert settings.CELERY_TASK_DEFAULT_QUEUE == "default"


def test_health_tasks_route_to_default_not_scans():
    from apps.libraries.tasks import scan_library_task, schedule_scans
    from apps.reconcile.tasks import reconcile_library

    routes = settings.CELERY_TASK_ROUTES
    assert routes[schedule_polls.name]["queue"] == "default"
    assert routes[poll_service.name]["queue"] == "default"
    assert routes[schedule_scans.name]["queue"] == "default"
    assert routes[scan_library_task.name]["queue"] == "scans"
    assert routes[reconcile_library.name]["queue"] == "scans"


def test_task_names_match_autodiscover():
    assert schedule_polls.name == "apps.services.tasks.schedule_polls"
    assert poll_service.name == "apps.services.tasks.poll_service"


def test_beat_wakes_schedule_polls_every_60s():
    from apps.libraries.tasks import schedule_scans

    entry = settings.CELERY_BEAT_SCHEDULE["schedule-polls-every-60s"]
    assert "tasks" not in entry
    assert entry["task"] == schedule_polls.name
    assert entry["schedule"] == 60.0
    scans = settings.CELERY_BEAT_SCHEDULE["schedule-scans-every-60s"]
    assert scans["task"] == schedule_scans.name
    assert scans["schedule"] == 60.0


def test_poll_service_retries_unavailable_only():
    assert poll_service.max_retries == 5
    assert poll_service.autoretry_for == (ServiceUnavailable,)
    assert poll_service.retry_backoff is True
    assert poll_service.retry_jitter is True
    assert ServiceAuthFailed not in poll_service.autoretry_for
    assert ServiceBadResponse not in poll_service.autoretry_for


def test_schedule_polls_does_not_autoretry():
    assert getattr(schedule_polls, "autoretry_for", ()) in ((), None)


def test_eager_test_settings_do_not_drop_beat_or_routes():
    assert settings.CELERY_TASK_ALWAYS_EAGER is True
    assert settings.CELERY_TASK_EAGER_PROPAGATES is True
    assert settings.CELERY_BROKER_URL == "memory://"
    assert "schedule-polls-every-60s" in settings.CELERY_BEAT_SCHEDULE
    assert poll_service.name in settings.CELERY_TASK_ROUTES
