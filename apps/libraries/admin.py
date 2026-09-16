from django.contrib import admin

from .models import DiskItem, Library, StorageSnapshot


@admin.register(Library)
class LibraryAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "service",
        "remote_id",
        "root_path",
        "last_scanned_at",
        "scan_interval_seconds",
        "created_at",
    )
    search_fields = ("name",)
    readonly_fields = ("created_at", "last_scanned_at")


@admin.register(DiskItem)
class DiskItemAdmin(admin.ModelAdmin):
    list_display = (
        "relative_path",
        "library",
        "file_count",
        "total_bytes",
        "seen_at",
    )
    search_fields = ("relative_path",)
    list_filter = ("library",)
    readonly_fields = ("seen_at",)


@admin.register(StorageSnapshot)
class StorageSnapshotAdmin(admin.ModelAdmin):
    list_display = ("library", "captured_at", "item_count", "total_bytes")
    list_filter = ("library",)
    readonly_fields = ("library", "captured_at", "item_count", "total_bytes")
