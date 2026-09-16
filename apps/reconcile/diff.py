from dataclasses import dataclass
from enum import StrEnum


class DiscrepancyKind(StrEnum):
    MISSING_IN_SERVICE = "missing_in_service"
    MISSING_ON_DISK = "missing_on_disk"


@dataclass(frozen=True)
class DiskEntry:
    relative_path: str
    file_count: int = 0


@dataclass(frozen=True)
class RemoteEntry:
    name: str
    remote_id: str = ""


@dataclass(frozen=True)
class DiscrepancyDraft:
    kind: DiscrepancyKind
    key: str


def normalize(name: str) -> str:
    return name.casefold().strip()


def diff_inventories(
    disk: list[DiskEntry], remote: list[RemoteEntry]
) -> list[DiscrepancyDraft]:
    """Set difference on normalize(name). Conservative: no fuzzy / suffix strip."""
    disk_keys = {normalize(d.relative_path) for d in disk}
    remote_keys = {normalize(r.name) for r in remote}
    out: list[DiscrepancyDraft] = []
    for key in sorted(disk_keys - remote_keys):
        out.append(DiscrepancyDraft(DiscrepancyKind.MISSING_IN_SERVICE, key))
    for key in sorted(remote_keys - disk_keys):
        out.append(DiscrepancyDraft(DiscrepancyKind.MISSING_ON_DISK, key))
    return out
