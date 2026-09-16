from django.contrib import admin

from .models import Discrepancy


@admin.register(Discrepancy)
class DiscrepancyAdmin(admin.ModelAdmin):
    list_display = ("library", "kind", "key", "status", "opened_at", "resolved_at")
    list_filter = ("status", "kind", "library")
    search_fields = ("key",)
    readonly_fields = ("opened_at", "updated_at", "resolved_at")
    actions = ("acknowledge",)

    @admin.action(description="Acknowledge selected")
    def acknowledge(self, request, queryset):
        queryset.exclude(status=Discrepancy.Status.RESOLVED).update(
            status=Discrepancy.Status.ACKNOWLEDGED,
        )

