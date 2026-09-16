from django.db import models

from .diff import DiscrepancyKind


class Discrepancy(models.Model):
    class Status(models.TextChoices):
        OPEN = "open", "Open"
        ACKNOWLEDGED = "acknowledged", "Acknowledged"
        RESOLVED = "resolved", "Resolved"

    library = models.ForeignKey(
        "libraries.Library",
        on_delete=models.CASCADE,
        related_name="discrepancies",
    )
    kind = models.CharField(
        max_length=32,
        choices=[(k.value, k.value) for k in DiscrepancyKind],
    )
    key = models.CharField(max_length=1024)
    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.OPEN,
    )
    opened_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["library", "kind", "key"],
                name="uniq_discrepancy_library_kind_key",
            ),
        ]
        ordering = ["-opened_at"]

    def __str__(self) -> str:
        return f"{self.kind}:{self.key}"

