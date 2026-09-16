"""Load disk + remote, diff, persist. Skip on ConnectorError — never diff []."""

from apps.libraries.models import DiskItem, Library
from apps.services.connectors.base import ConnectorError, RemoteSeries
from apps.services.connectors.registry import get_connector

from .diff import DiskEntry, RemoteEntry, diff_inventories
from .persist import apply_drafts


def reconcile_library(library: Library) -> int:
    if not library.remote_id or library.last_scanned_at is None:
        return 0

    disk = [
        DiskEntry(relative_path=path, file_count=count)
        for path, count in DiskItem.objects.filter(
            library=library,
            seen_at=library.last_scanned_at,
        ).values_list("relative_path", "file_count")
    ]

    service = library.service
    connector = get_connector(service.kind, service.url, service.api_key)
    try:
        series: list[RemoteSeries] = list(connector.list_series(library.remote_id))
    except ConnectorError:
        # Do not treat timeout as empty inventory.
        return 0

    remote = [RemoteEntry(name=s.name, remote_id=s.id) for s in series]
    drafts = diff_inventories(disk, remote)
    return apply_drafts(library, drafts)
