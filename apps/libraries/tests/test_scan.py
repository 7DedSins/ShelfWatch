"""Naive scan_library. AI-written [!]."""

from datetime import timedelta
from pathlib import Path

import pytest
from django.utils import timezone

from apps.libraries.models import DiskItem, Library, StorageSnapshot
from apps.libraries.scan import CHUNK, scan_library
from apps.services.models import Service


@pytest.fixture
def library(db, tmp_path: Path) -> Library:
    service = Service.objects.create(name="Kavita", url="http://kavita.test")
    return Library.objects.create(
        service=service,
        name="Manga",
        root_path=str(tmp_path),
    )


def _series(root: Path, name: str, filename: str = "ch1.cbz") -> Path:
    folder = root / name
    folder.mkdir()
    (folder / filename).write_bytes(b"cbz")
    return folder


@pytest.mark.django_db
def test_missing_root_returns_zero(library):
    library.root_path = "/no/such/shelfwatch-scan"
    library.save()
    assert scan_library(library) == 0
    assert DiskItem.objects.count() == 0
    library.refresh_from_db()
    assert library.last_scanned_at is not None


@pytest.mark.django_db
def test_one_series_folder_one_row(library, tmp_path: Path):
    _series(tmp_path, "One Piece")
    assert scan_library(library) == 1
    item = DiskItem.objects.get()
    assert item.relative_path == "One Piece"
    assert item.file_count == 1
    assert item.total_bytes == 3
    assert item.newest_mtime is not None
    assert item.newest_mtime.tzinfo is not None
    assert item.seen_at.tzinfo is not None


@pytest.mark.django_db
def test_second_scan_does_not_duplicate(library, tmp_path: Path):
    _series(tmp_path, "One Piece")
    scan_library(library)
    scan_library(library)
    assert DiskItem.objects.count() == 1


@pytest.mark.django_db
def test_second_folder_adds_a_row(library, tmp_path: Path):
    _series(tmp_path, "One Piece")
    scan_library(library)
    _series(tmp_path, "Naruto")
    assert scan_library(library) == 2
    assert DiskItem.objects.count() == 2


@pytest.mark.django_db
def test_removed_folder_keeps_stale_row_with_old_seen_at(library, tmp_path: Path):
    first = timezone.now()
    later = first + timedelta(minutes=5)
    one = _series(tmp_path, "One Piece")
    _series(tmp_path, "Naruto")
    scan_library(library, now=first)
    for child in one.iterdir():
        child.unlink()
    one.rmdir()
    scan_library(library, now=later)
    gone = DiskItem.objects.get(relative_path="One Piece")
    stay = DiskItem.objects.get(relative_path="Naruto")
    assert gone.seen_at == first
    assert stay.seen_at == later
    assert DiskItem.objects.count() == 2


@pytest.mark.django_db
def test_naive_now_is_stored_utc(library, tmp_path: Path):
    _series(tmp_path, "One Piece")
    naive = timezone.now().replace(tzinfo=None)
    scan_library(library, now=naive)
    seen = DiskItem.objects.get().seen_at
    assert timezone.is_aware(seen)
    assert seen.utcoffset() == timedelta(0)


@pytest.mark.django_db
def test_scan_appends_storage_snapshot(library, tmp_path: Path):
    _series(tmp_path, "One Piece")
    scan_library(library)
    snap = StorageSnapshot.objects.get()
    assert snap.item_count == 1
    assert snap.total_bytes == 3
    scan_library(library)
    assert StorageSnapshot.objects.count() == 2


@pytest.mark.django_db
def test_missing_root_does_not_write_snapshot(library):
    library.root_path = "/no/such/shelfwatch-scan"
    library.save()
    scan_library(library)
    assert StorageSnapshot.objects.count() == 0


@pytest.mark.django_db
def test_chunked_upsert_still_idempotent(library, tmp_path: Path, monkeypatch):
    monkeypatch.setattr("apps.libraries.scan.CHUNK", 1)
    _series(tmp_path, "One Piece")
    _series(tmp_path, "Naruto")
    assert scan_library(library) == 2
    assert scan_library(library) == 2
    assert DiskItem.objects.count() == 2
    assert CHUNK == 1000
