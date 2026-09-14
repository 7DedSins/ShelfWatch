"""poll_health + manage.py poll_health.

AI-written. Explain: ConnectorError is re-raised after last_health_ok=False.
Command tests mock poll_health — no live VPS.
"""

from io import StringIO
from unittest.mock import MagicMock, patch

import pytest
from django.core.management import call_command

from apps.services.connectors.base import (
    HealthResult,
    ServiceAuthFailed,
    ServiceUnavailable,
)
from apps.services.health import poll_health
from apps.services.models import Service


def _row(**kwargs) -> Service:
    defaults = {
        "name": "Kavita",
        "url": "http://kavita.test",
        "kind": Service.Kind.KAVITA,
        "api_key": "secret",
    }
    defaults.update(kwargs)
    return Service.objects.create(**defaults)


@pytest.mark.django_db
def test_new_service_has_unknown_health():
    service = _row()
    assert service.last_health_ok is None
    assert service.last_polled_at is None


@pytest.mark.django_db
def test_poll_health_calls_registry_and_writes_success():
    service = _row()
    connector = MagicMock()
    connector.health.return_value = HealthResult(ok=True, detail="up")

    with patch("apps.services.health.get_connector", return_value=connector) as mock_get:
        result = poll_health(service)

    mock_get.assert_called_once_with("kavita", "http://kavita.test", "secret")
    assert result.ok is True
    service.refresh_from_db()
    assert service.last_health_ok is True
    assert service.last_polled_at is not None


@pytest.mark.django_db
def test_poll_health_ok_false_without_raise_still_persists():
    service = _row()
    connector = MagicMock()
    connector.health.return_value = HealthResult(ok=False, detail="degraded")

    result = None
    with patch("apps.services.health.get_connector", return_value=connector):
        result = poll_health(service)

    assert result.ok is False
    service.refresh_from_db()
    assert service.last_health_ok is False
    assert service.last_polled_at is not None


@pytest.mark.django_db
def test_poll_health_unavailable_persists_false_then_raises():
    service = _row()
    connector = MagicMock()
    connector.health.side_effect = ServiceUnavailable("timed out")

    with patch("apps.services.health.get_connector", return_value=connector):
        with pytest.raises(ServiceUnavailable, match="timed out"):
            poll_health(service)

    service.refresh_from_db()
    assert service.last_health_ok is False
    assert service.last_polled_at is not None


@pytest.mark.django_db
def test_poll_health_auth_failed_persists_false_then_raises():
    service = _row(name="LRR", url="http://lrr.test", kind=Service.Kind.LANRARAGI)
    connector = MagicMock()
    connector.health.side_effect = ServiceAuthFailed("bad key")

    with patch("apps.services.health.get_connector", return_value=connector):
        with pytest.raises(ServiceAuthFailed):
            poll_health(service)

    service.refresh_from_db()
    assert service.last_health_ok is False


@pytest.mark.django_db
def test_command_no_services_prints_message():
    out = StringIO()
    call_command("poll_health", stdout=out)
    assert "No services." in out.getvalue()


@pytest.mark.django_db
def test_command_prints_success_with_service_name():
    _row()
    out = StringIO()
    with patch(
        "apps.services.management.commands.poll_health.poll_health",
        return_value=HealthResult(ok=True, detail="pong"),
    ):
        call_command("poll_health", stdout=out)
    text = out.getvalue()
    assert "Kavita" in text
    assert "ok=True" in text
    assert "pong" in text


@pytest.mark.django_db
def test_command_prints_connector_error_on_stderr():
    _row(url="http://down.test")
    err = StringIO()
    with patch(
        "apps.services.management.commands.poll_health.poll_health",
        side_effect=ServiceUnavailable("timed out"),
    ):
        call_command("poll_health", stderr=err)
    text = err.getvalue()
    assert "Kavita" in text
    assert "timed out" in text
