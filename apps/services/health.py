"""Turn a Service row into a health check. No HTTP here — the connector owns that.

Callers (management command, admin) catch ConnectorError. This function must
not convert a timeout into HealthResult(ok=False) if that would later be
confused with inventory; health is a boolean, but we still re-raise so the
caller decides how to display it.
"""

from django.utils import timezone

from apps.services.connectors.base import ConnectorError, HealthResult
from apps.services.connectors.registry import get_connector
from apps.services.models import Service


def poll_health(service: Service) -> HealthResult:
    connector = get_connector(service.kind, service.url, service.api_key)
    try:
        result = connector.health()
    except ConnectorError:
        # Persist-then-raise: admin shows last failure; caller still sees the error.
        # Do not return HealthResult(ok=False) — that would look like a successful poll.
        service.last_health_ok = False
        service.last_polled_at = timezone.now()
        service.save(update_fields=["last_health_ok", "last_polled_at"])
        raise
    service.last_health_ok = result.ok
    service.last_polled_at = timezone.now()
    service.save(update_fields=["last_health_ok", "last_polled_at"])
    return result
