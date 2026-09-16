from django.core.validators import MinValueValidator
from django.db import models


class Library(models.Model):
    service = models.ForeignKey(
        "services.Service",
        on_delete=models.CASCADE,
        related_name="libraries",
    )
    name = models.CharField(max_length=200)
    # VPS mount path; not a laptop FilePathField.
    root_path = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    # NULL = never scanned. Scans are expensive; default 1h not 60s.
    last_scanned_at = models.DateTimeField(null=True, blank=True)
    scan_interval_seconds = models.PositiveIntegerField(
        default=3600,
        validators=[MinValueValidator(1)],
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["service", "name"],
                name="uniq_library_service_name",
            ),
        ]
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.service}: {self.name}"


class DiskItem(models.Model):
    library = models.ForeignKey(
        Library,
        on_delete=models.CASCADE,
        related_name="disk_items",
    )
    # Series folder relative to root_path — not a chapter file.
    relative_path = models.CharField(max_length=1024)
    file_count = models.PositiveIntegerField(default=0)
    total_bytes = models.PositiveBigIntegerField(default=0)
    newest_mtime = models.DateTimeField(null=True, blank=True)
    # Scan stamp (UTC). Stale if older than the current scan_started.
    seen_at = models.DateTimeField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["library", "relative_path"],
                name="uniq_diskitem_library_path",
            ),
        ]
        indexes = [
            models.Index(fields=["library", "seen_at"]),
        ]

    def __str__(self) -> str:
        return self.relative_path


class StorageSnapshot(models.Model):
    """Append-only chart point. Not derived from DiskItem history."""

    library = models.ForeignKey(
        Library,
        on_delete=models.CASCADE,
        related_name="snapshots",
    )
    captured_at = models.DateTimeField()  # UTC; append-only, not updated in place.
    item_count = models.PositiveIntegerField()
    total_bytes = models.PositiveBigIntegerField()

    class Meta:
        ordering = ["-captured_at"]
