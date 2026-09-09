"""poll_health + manage.py poll_health.

AI-written 2026-09-09. Explain: this layer does not swallow ConnectorError
into an empty/ok result. Command tests mock poll_health — no live VPS.
"""

from io import StringIO
from unittest.mock import MagicMock, patch

import pytest
from django.core.management import call_command

from apps.services.connectors.base import (
    HealthResult,
    ServiceUnavailable,
)
from apps.services.health import poll_health
from apps.services.models import Service


def test_poll_health_calls_registry_and_health():
    service = Service(
        name="Kavita",
        url="http://kavita.test",
        kind=Service.Kind.KAVITA,
        api_key="secret",
    )
    connector = MagicMock()
    connector.health.return_value = HealthResult(ok=True, detail="up")

    with patch("apps.services.health.get_connector", return_value=connector) as mock_get:
        result = poll_health(service)

    mock_get.assert_called_once_with("kavita", "http://kavita.test", "secret")
    connector.health.assert_called_once_with()
    assert result.ok is True
    assert result.detail == "up"


def test_poll_health_does_not_swallow_unavailable():
    service = Service(
        name="Kavita",
        url="http://kavita.test",
        kind=Service.Kind.KAVITA,
        api_key="secret",
    )
    connector = MagicMock()
    connector.health.side_effect = ServiceUnavailable("timed out")

    with patch("apps.services.health.get_connector", return_value=connector):
        with pytest.raises(ServiceUnavailable, match="timed out"):
            poll_health(service)


@pytest.mark.django_db
def test_command_no_services_prints_message():
    out = StringIO()
    call_command("poll_health", stdout=out)
    assert "No services." in out.getvalue()


@pytest.mark.django_db
def test_command_prints_success_with_service_name():
    Service.objects.create(
        name="Kavita",
        url="http://kavita.test",
        kind=Service.Kind.KAVITA,
    )
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
    Service.objects.create(
        name="Kavita",
        url="http://down.test",
        kind=Service.Kind.KAVITA,
    )
    err = StringIO()
    with patch(
        "apps.services.management.commands.poll_health.poll_health",
        side_effect=ServiceUnavailable("timed out"),
    ):
        call_command("poll_health", stderr=err)
    text = err.getvalue()
    assert "Kavita" in text
    assert "timed out" in text
