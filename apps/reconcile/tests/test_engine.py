"""reconcile_library skips ConnectorError. AI-written [!]."""

from unittest.mock import MagicMock, patch

import pytest
from django.utils import timezone

from apps.libraries.models import DiskItem, Library
from apps.reconcile.engine import reconcile_library
from apps.reconcile.models import Discrepancy
from apps.services.connectors.base import RemoteSeries, ServiceUnavailable
from apps.services.models import Service


@pytest.fixture
def library(db) -> Library:
    service = Service.objects.create(name="Kavita", url="http://kavita.test")
    return Library.objects.create(
        service=service,
        name="Manga",
        root_path="/tmp",
        remote_id="1",
        last_scanned_at=timezone.now(),
    )


def _disk(library: Library, name: str) -> None:
    DiskItem.objects.create(
        library=library,
        relative_path=name,
        file_count=1,
        seen_at=library.last_scanned_at,
    )


@pytest.mark.django_db
def test_connector_error_skips_and_writes_nothing(library):
    _disk(library, "Solo Leveling")
    connector = MagicMock()
    connector.list_series.side_effect = ServiceUnavailable("timeout")
    with patch(
        "apps.reconcile.engine.get_connector",
        return_value=connector,
    ):
        assert reconcile_library(library) == 0
    assert Discrepancy.objects.count() == 0


@pytest.mark.django_db
def test_empty_remote_is_inventory_and_flags_disk(library):
    _disk(library, "Solo Leveling")
    connector = MagicMock()
    connector.list_series.return_value = iter([])
    with patch(
        "apps.reconcile.engine.get_connector",
        return_value=connector,
    ):
        assert reconcile_library(library) == 1
    row = Discrepancy.objects.get()
    assert row.kind == "missing_in_service"
    assert row.key == "solo leveling"
    assert row.status == Discrepancy.Status.OPEN


@pytest.mark.django_db
def test_successful_match_writes_nothing(library):
    _disk(library, "Solo Leveling")
    connector = MagicMock()
    connector.list_series.return_value = iter(
        [RemoteSeries(id="9", name="Solo Leveling", library_id="1")]
    )
    with patch(
        "apps.reconcile.engine.get_connector",
        return_value=connector,
    ):
        assert reconcile_library(library) == 0
    assert Discrepancy.objects.count() == 0


@pytest.mark.django_db
def test_skip_without_remote_id_or_scan(library):
    library.remote_id = ""
    library.save()
    assert reconcile_library(library) == 0
    library.remote_id = "1"
    library.last_scanned_at = None
    library.save()
    assert reconcile_library(library) == 0
