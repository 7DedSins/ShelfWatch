"""scan_library_task. AI-written [!]. Eager: no Redis."""

from datetime import timedelta
from pathlib import Path
from unittest.mock import patch

import pytest
from django.utils import timezone

from apps.libraries.models import Library
from apps.libraries.tasks import scan_library_task, schedule_scans
from apps.services.models import Service


@pytest.mark.django_db
def test_scan_task_loads_library_and_calls_scan(tmp_path: Path):
    service = Service.objects.create(name="Kavita", url="http://kavita.test")
    library = Library.objects.create(
        service=service, name="Manga", root_path=str(tmp_path)
    )
    with patch("apps.libraries.tasks.scan_library", return_value=3) as scan:
        assert scan_library_task(library.pk) == 3
    scan.assert_called_once()
    assert scan.call_args[0][0].pk == library.pk


def test_scan_task_name_and_time_limits():
    assert scan_library_task.name == "apps.libraries.tasks.scan_library_task"
    assert scan_library_task.soft_time_limit == 3600
    assert scan_library_task.time_limit == 3660
    assert schedule_scans.name == "apps.libraries.tasks.schedule_scans"


@pytest.mark.django_db
def test_never_scanned_is_due():
    service = Service.objects.create(name="Kavita", url="http://kavita.test")
    library = Library.objects.create(
        service=service, name="Manga", root_path="/tmp"
    )
    with patch("apps.libraries.tasks.scan_library_task.delay") as delay:
        assert schedule_scans() == 1
    delay.assert_called_once_with(library.pk)


@pytest.mark.django_db
def test_recent_scan_within_interval_is_not_due():
    now = timezone.now()
    service = Service.objects.create(name="Kavita", url="http://kavita.test")
    Library.objects.create(
        service=service,
        name="Manga",
        root_path="/tmp",
        last_scanned_at=now - timedelta(minutes=10),
        scan_interval_seconds=3600,
    )
    with patch("apps.libraries.tasks.timezone.now", return_value=now):
        with patch("apps.libraries.tasks.scan_library_task.delay") as delay:
            assert schedule_scans() == 0
    delay.assert_not_called()


@pytest.mark.django_db
def test_stale_scan_is_due():
    now = timezone.now()
    service = Service.objects.create(name="Kavita", url="http://kavita.test")
    library = Library.objects.create(
        service=service,
        name="Manga",
        root_path="/tmp",
        last_scanned_at=now - timedelta(hours=2),
        scan_interval_seconds=3600,
    )
    with patch("apps.libraries.tasks.timezone.now", return_value=now):
        with patch("apps.libraries.tasks.scan_library_task.delay") as delay:
            assert schedule_scans() == 1
    delay.assert_called_once_with(library.pk)
