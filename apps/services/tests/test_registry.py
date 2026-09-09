"""Registry tests. AI-written 2026-09-09 — explain: unknown kind raises, not None."""

import pytest

from apps.services.connectors.kavita import KavitaConnector
from apps.services.connectors.lanraragi import LanraragiConnector
from apps.services.connectors.registry import CONNECTORS, get_connector
from apps.services.models import Service


def test_get_connector_returns_kavita_instance():
    connector = get_connector("kavita", "http://kavita.test", "key")
    assert isinstance(connector, KavitaConnector)


def test_get_connector_returns_lanraragi_instance():
    connector = get_connector("lanraragi", "http://lrr.test", "key")
    assert isinstance(connector, LanraragiConnector)


def test_unknown_kind_raises_value_error():
    with pytest.raises(ValueError, match="stash"):
        get_connector("stash", "http://stash.test", "key")


def test_registry_keys_match_service_kind_values():
    assert set(CONNECTORS) == {
        Service.Kind.KAVITA.value,
        Service.Kind.LANRARAGI.value,
    }
