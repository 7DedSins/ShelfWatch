"""poll_service + schedule_polls. AI-written [!]. Eager: no Redis.

Explain: never-polled is due (NULL ≠ old timestamp); fan-out is .delay(id).
"""

from datetime import timedelta
from unittest.mock import patch

import pytest
from django.utils import timezone

from apps.services.connectors.base import HealthResult, ServiceUnavailable
from apps.services.models import Service
from apps.services.tasks import poll_service, schedule_polls


@pytest.mark.django_db
def test_poll_service_loads_row_and_calls_poll_health():
    service = Service.objects.create(
        name="Kavita",
        url="http://kavita.test",
        kind=Service.Kind.KAVITA,
    )
    with patch(
        "apps.services.tasks.poll_health",
        return_value=HealthResult(ok=True),
    ) as mock_poll:
        poll_service(service.pk)
    mock_poll.assert_called_once()
    assert mock_poll.call_args[0][0].pk == service.pk


@pytest.mark.django_db
def test_poll_service_propagates_unavailable():
    service = Service.objects.create(
        name="Kavita",
        url="http://kavita.test",
        kind=Service.Kind.KAVITA,
    )
    with patch(
        "apps.services.tasks.poll_health",
        side_effect=ServiceUnavailable("timed out"),
    ):
        with pytest.raises(ServiceUnavailable):
            poll_service(service.pk)


def _service(**kwargs) -> Service:
    defaults = {
        "name": "Kavita",
        "url": "http://kavita.test",
        "kind": Service.Kind.KAVITA,
    }
    defaults.update(kwargs)
    return Service.objects.create(**defaults)


@pytest.mark.django_db
def test_poll_interval_defaults_to_sixty():
    service = _service()
    assert service.poll_interval_seconds == 60


@pytest.mark.django_db
def test_schedule_polls_empty_table_enqueues_nothing():
    with patch("apps.services.tasks.poll_service.delay") as delay:
        count = schedule_polls()
    assert count == 0
    delay.assert_not_called()


@pytest.mark.django_db
def test_never_polled_is_due():
    service = _service()
    assert service.last_polled_at is None
    with patch("apps.services.tasks.poll_service.delay") as delay:
        count = schedule_polls()
    assert count == 1
    delay.assert_called_once_with(service.pk)


@pytest.mark.django_db
def test_recently_polled_within_interval_is_not_due():
    now = timezone.now()
    _service(last_polled_at=now - timedelta(seconds=10), poll_interval_seconds=60)
    with patch("apps.services.tasks.timezone.now", return_value=now):
        with patch("apps.services.tasks.poll_service.delay") as delay:
            count = schedule_polls()
    assert count == 0
    delay.assert_not_called()


@pytest.mark.django_db
def test_stale_poll_beyond_interval_is_due():
    now = timezone.now()
    service = _service(
        last_polled_at=now - timedelta(seconds=120),
        poll_interval_seconds=60,
    )
    with patch("apps.services.tasks.timezone.now", return_value=now):
        with patch("apps.services.tasks.poll_service.delay") as delay:
            count = schedule_polls()
    assert count == 1
    delay.assert_called_once_with(service.pk)


@pytest.mark.django_db
def test_exactly_at_interval_boundary_is_due():
    now = timezone.now()
    service = _service(
        last_polled_at=now - timedelta(seconds=60),
        poll_interval_seconds=60,
    )
    with patch("apps.services.tasks.timezone.now", return_value=now):
        with patch("apps.services.tasks.poll_service.delay") as delay:
            count = schedule_polls()
    assert count == 1
    delay.assert_called_once_with(service.pk)


@pytest.mark.django_db
def test_just_inside_interval_is_not_due():
    now = timezone.now()
    _service(
        last_polled_at=now - timedelta(seconds=59),
        poll_interval_seconds=60,
    )
    with patch("apps.services.tasks.timezone.now", return_value=now):
        with patch("apps.services.tasks.poll_service.delay") as delay:
            count = schedule_polls()
    assert count == 0
    delay.assert_not_called()


@pytest.mark.django_db
def test_due_ness_uses_per_row_interval():
    now = timezone.now()
    stale_fast = _service(
        name="Fast",
        last_polled_at=now - timedelta(seconds=30),
        poll_interval_seconds=10,
    )
    _service(
        name="Slow",
        url="http://slow.test",
        last_polled_at=now - timedelta(seconds=30),
        poll_interval_seconds=60,
    )
    never = _service(name="New", url="http://new.test")
    with patch("apps.services.tasks.timezone.now", return_value=now):
        with patch("apps.services.tasks.poll_service.delay") as delay:
            count = schedule_polls()
    assert count == 2
    enqueued = {call.args[0] for call in delay.call_args_list}
    assert enqueued == {stale_fast.pk, never.pk}


@pytest.mark.django_db
def test_schedule_polls_does_not_call_poll_health_itself():
    _service()
    with patch("apps.services.tasks.poll_service.delay") as delay:
        with patch("apps.services.tasks.poll_health") as health:
            schedule_polls()
    delay.assert_called_once()
    health.assert_not_called()
