from datetime import UTC, datetime
from pathlib import Path

from django.db import transaction
from django.db.models import Count, Sum
from django.utils import timezone

from .models import DiskItem, Library, StorageSnapshot

CHUNK = 1000


def _as_utc(dt):
    """Store and compare only UTC-aware datetimes (USE_TZ=True, TIME_ZONE=UTC)."""
    if timezone.is_naive(dt):
        return dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)


def scan_library(library: Library, *, now=None) -> int:
    """Walk root_path: one DiskItem per immediate child dir; chunked bulk upsert.

    DiskItem() takes field kwargs — not defaults= (that is update_or_create only).
    atomic() is per chunk, not around the walk.
    """
    scan_started = _as_utc(now or timezone.now())
    root = Path(library.root_path)

    if not root.is_dir():
        # Advance due-ness so Beat does not enqueue every 60s on a missing path.
        library.last_scanned_at = scan_started
        library.save(update_fields=["last_scanned_at"])
        return 0

    pending: list[DiskItem] = []
    for child in root.iterdir():
        if not child.is_dir():
            continue
        file_count = 0
        total_bytes = 0
        newest = None

        for path in child.rglob("*"):
            if not path.is_file():
                continue
            file_count += 1
            stat = path.stat()
            total_bytes += stat.st_size
            mtime = datetime.fromtimestamp(stat.st_mtime, tz=UTC)
            if newest is None or mtime > newest:
                newest = mtime

        pending.append(
            DiskItem(
                library=library,
                relative_path=child.name,
                file_count=file_count,
                total_bytes=total_bytes,
                newest_mtime=newest,
                seen_at=scan_started,
            )
        )
        if len(pending) >= CHUNK:
            _upsert_chunk(pending)
            pending = []
    if pending:
        _upsert_chunk(pending)

    seen = DiskItem.objects.filter(library=library, seen_at=scan_started)
    totals = seen.aggregate(n=Count("id"), b=Sum("total_bytes"))
    StorageSnapshot.objects.create(
        library=library,
        captured_at=scan_started,
        item_count=totals["n"] or 0,
        total_bytes=totals["b"] or 0,
    )
    library.last_scanned_at = scan_started
    library.save(update_fields=["last_scanned_at"])
    return totals["n"] or 0


def _upsert_chunk(rows: list[DiskItem]) -> None:
    with transaction.atomic():
        DiskItem.objects.bulk_create(
            rows,
            update_conflicts=True,
            unique_fields=["library", "relative_path"],
            update_fields=["file_count", "total_bytes", "newest_mtime", "seen_at"],
        )
