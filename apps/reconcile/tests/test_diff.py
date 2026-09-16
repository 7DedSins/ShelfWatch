"""Table-driven diff spec. Engine is pure: no DB, no HTTP."""

from apps.reconcile.diff import (
    DiscrepancyKind,
    DiskEntry,
    RemoteEntry,
    diff_inventories,
)


def _kinds(disk, remote):
    return {(d.kind, d.key) for d in diff_inventories(disk, remote)}


def test_identical_inventories_no_discrepancies():
    disk = [DiskEntry("Solo Leveling")]
    remote = [RemoteEntry("Solo Leveling")]
    assert diff_inventories(disk, remote) == []


def test_both_empty():
    assert diff_inventories([], []) == []


def test_missing_in_service():
    disk = [DiskEntry("Solo Leveling")]
    assert _kinds(disk, []) == {
        (DiscrepancyKind.MISSING_IN_SERVICE, "solo leveling"),
    }


def test_missing_on_disk():
    remote = [RemoteEntry("Solo Leveling")]
    assert _kinds([], remote) == {
        (DiscrepancyKind.MISSING_ON_DISK, "solo leveling"),
    }


def test_disk_empty_service_full():
    remote = [RemoteEntry("A"), RemoteEntry("B")]
    kinds = _kinds([], remote)
    assert kinds == {
        (DiscrepancyKind.MISSING_ON_DISK, "a"),
        (DiscrepancyKind.MISSING_ON_DISK, "b"),
    }


def test_service_empty_disk_full():
    disk = [DiskEntry("A"), DiskEntry("B")]
    kinds = _kinds(disk, [])
    assert kinds == {
        (DiscrepancyKind.MISSING_IN_SERVICE, "a"),
        (DiscrepancyKind.MISSING_IN_SERVICE, "b"),
    }


def test_case_and_space_normalize_match():
    disk = [DiskEntry("  Solo Leveling ")]
    remote = [RemoteEntry("solo leveling")]
    assert diff_inventories(disk, remote) == []


def test_official_suffix_does_not_match_yet():
    """Conservative: visible pair of misses, not a silent wrong merge."""
    disk = [DiskEntry("Solo Leveling (Official)")]
    remote = [RemoteEntry("Solo Leveling")]
    assert _kinds(disk, remote) == {
        (DiscrepancyKind.MISSING_IN_SERVICE, "solo leveling (official)"),
        (DiscrepancyKind.MISSING_ON_DISK, "solo leveling"),
    }
