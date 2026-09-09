"""Turn a Service row into a health check. No HTTP here — the connector owns that.

Callers (management command, admin) catch ConnectorError. This function must
not convert a timeout into HealthResult(ok=False) if that would later be
confused with inventory; health is a boolean, but we still re-raise so the
caller decides how to display it.
"""

from apps.services.connectors.base import HealthResult
from apps.services.connectors.registry import get_connector
from apps.services.models import Service


def poll_health(service: Service) -> HealthResult:
    connector = get_connector(service.kind, service.url, service.api_key)
    return connector.health()
