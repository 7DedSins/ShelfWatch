"""kind string → connector class. Views/tasks call get_connector, never if/elif.

Adding a vendor: new file + one CONNECTORS line + a Service.Kind value.
Keys must match Service.Kind values (kavita, lanraragi).
"""

from collections.abc import Callable

from .base import BaseConnector
from .kavita import KavitaConnector
from .lanraragi import LanraragiConnector

# Callable, not type[BaseConnector]: Pylance will not construct an ABC
# with (url, api_key). Each vendor class is a factory of that shape.
CONNECTORS: dict[str, Callable[[str, str], BaseConnector]] = {
    "kavita": KavitaConnector,
    "lanraragi": LanraragiConnector,
}


def get_connector(kind: str, url: str, api_key: str) -> BaseConnector:
    try:
        cls = CONNECTORS[kind]
    except KeyError as extra:
        raise ValueError(f"Unknown service kind: {kind!r}") from extra
    return cls(url, api_key)
