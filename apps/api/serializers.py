"""JSON shape for API resources. Validation and field visibility live here.

ModelSerializer maps model fields; Meta.extra_kwargs / read_only_fields
are the leak/write controls. DRF does not call model.full_clean() by default.
"""

from rest_framework import serializers

from apps.libraries.models import DiskItem, Library
from apps.reconcile.models import Discrepancy
from apps.services.models import Service


class ServiceSerializer(serializers.ModelSerializer):
    """Public service fields. ``api_key`` is write-only (never in responses)."""

    class Meta:
        model = Service
        fields = (
            "id",
            "name",
            "url",
            "kind",
            "last_health_ok",
            "last_polled_at",
            "poll_interval_seconds",
            "api_key",
        )
        extra_kwargs = {"api_key": {"write_only": True}}
        read_only_fields = ("last_health_ok", "last_polled_at")


class LibrarySerializer(serializers.ModelSerializer):
    """Library row. Scan stamp is engine-owned, not client-writable."""

    class Meta:
        model = Library
        fields = (
            "id",
            "service",
            "name",
            "remote_id",
            "root_path",
            "last_scanned_at",
            "scan_interval_seconds",
        )
        read_only_fields = ("last_scanned_at",)


class DiskItemSerializer(serializers.ModelSerializer):
    """Scan snapshot of a series folder. Created only by scan_library."""

    class Meta:
        model = DiskItem
        fields = (
            "id",
            "library",
            "relative_path",
            "file_count",
            "total_bytes",
            "newest_mtime",
            "seen_at",
        )


class DiscrepancySerializer(serializers.ModelSerializer):
    """Diff result. All fields read-only; status changes via acknowledge action."""

    class Meta:
        model = Discrepancy
        fields = (
            "id",
            "library",
            "kind",
            "key",
            "status",
            "opened_at",
            "resolved_at",
        )
        read_only_fields = fields
