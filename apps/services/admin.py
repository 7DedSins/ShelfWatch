from django.contrib import admin

from .models import Service


# Register your models here.
@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("name", "url", "created_at", "updated_at", "kind")
    search_fields = ("name",)
    readonly_fields = ("created_at", "updated_at")

    def get_readonly_fields(self, request, obj=None):
        # Add form: obj is None → kind is a dropdown.
        # Change form: lock kind so Kavita/LANraragi are not swapped on a live row.
        fields = list(super().get_readonly_fields(request, obj))
        if obj is not None:
            fields.append("kind")
        return fields
