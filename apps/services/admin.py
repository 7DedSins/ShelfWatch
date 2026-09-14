from django.contrib import admin, messages

from apps.services.connectors.base import ConnectorError
from apps.services.health import poll_health

from .models import Service


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "url",
        "created_at",
        "updated_at",
        "kind",
        "last_health_ok",
        "last_polled_at",
        "poll_interval_seconds",
    )
    search_fields = ("name",)
    # Health timestamps are written by poll_health; interval stays editable.
    readonly_fields = ("created_at", "updated_at", "last_health_ok", "last_polled_at")
    actions = ("test_connection",)

    def get_readonly_fields(self, request, obj=None):
        # Add form: obj is None → kind is a dropdown.
        # Change form: lock kind so Kavita/LANraragi are not swapped on a live row.
        fields = list(super().get_readonly_fields(request, obj))
        if obj is not None:
            fields.append("kind")
        return fields

    @admin.action(description="Test connection")
    def test_connection(self, request, queryset):
        for service in queryset:
            try:
                result = poll_health(service)
                detail = f" {result.detail}" if result.detail else ""
                self.message_user(request, f"{service.name}: ok={result.ok}{detail}")
            except ConnectorError as extra:
                self.message_user(
                    request, f"{service.name}: {extra}", level=messages.ERROR
                )
