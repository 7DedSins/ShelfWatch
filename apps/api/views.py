"""ViewSets: auth + queryset scoping. Views must not call Kavita or os.walk.

Security: get_queryset() is the tenancy filter. get_object() uses it, so
detail/poll/scan/acknowledge on another user's id is 404, not 403.
"""

from celery import chain
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.throttling import SimpleRateThrottle
from rest_framework.viewsets import ReadOnlyModelViewSet

from apps.libraries.models import DiskItem, Library
from apps.libraries.tasks import scan_library_task
from apps.reconcile.models import Discrepancy
from apps.reconcile.tasks import reconcile_library
from apps.services.models import Service
from apps.services.tasks import poll_service

from .serializers import (
    DiscrepancySerializer,
    DiskItemSerializer,
    LibrarySerializer,
    ServiceSerializer,
)


class PollThrottle(SimpleRateThrottle):
    """Per-user cap on POST /services/{id}/poll/ (DEFAULT_THROTTLE_RATES['poll'])."""

    scope = "poll"

    def get_cache_key(self, request, view):
        if not request.user.is_authenticated:
            return None
        return self.cache_format % {"scope": self.scope, "ident": request.user.pk}


class ScanThrottle(SimpleRateThrottle):
    """Per-user cap on POST /libraries/{id}/scan/."""

    scope = "scan"

    def get_cache_key(self, request, view):
        if not request.user.is_authenticated:
            return None
        return self.cache_format % {"scope": self.scope, "ident": request.user.pk}


class ServiceViewSet(ReadOnlyModelViewSet):
    """List/retrieve the caller's services. Writes stay in admin this milestone."""

    serializer_class = ServiceSerializer

    def get_queryset(self):
        return Service.objects.filter(owner=self.request.user)

    @action(detail=True, methods=["post"], throttle_classes=[PollThrottle])
    def poll(self, request, pk=None):
        """Enqueue poll_health. 202 = queued, not 'Kavita is up'."""
        service = self.get_object()
        poll_service.delay(service.pk)  # type: ignore[attr-defined]
        return Response({"queued": True}, status=202)


class LibraryViewSet(ReadOnlyModelViewSet):
    """Libraries whose parent Service.owner is the caller."""

    serializer_class = LibrarySerializer

    def get_queryset(self):
        return Library.objects.filter(service__owner=self.request.user).select_related(
            "service"
        )

    @action(detail=True, methods=["post"], throttle_classes=[ScanThrottle])
    def scan(self, request, pk=None):
        """Enqueue walk then reconcile. .si so scan's int return is not an extra arg."""
        library = self.get_object()
        chain(
            scan_library_task.s(library.pk),  # type: ignore[attr-defined]
            reconcile_library.si(library.pk),  # type: ignore[attr-defined]
        ).delay()
        return Response({"queued": True}, status=202)


class DiskItemViewSet(ReadOnlyModelViewSet):
    """Per-folder scan rows. Nothing should POST these by hand."""

    serializer_class = DiskItemSerializer

    def get_queryset(self):
        return DiskItem.objects.filter(
            library__service__owner=self.request.user
        ).select_related("library")


class DiscrepancyViewSet(ReadOnlyModelViewSet):
    """Diff rows. Create/resolve is the engine; clients may acknowledge."""

    serializer_class = DiscrepancySerializer

    def get_queryset(self):
        return Discrepancy.objects.filter(
            library__service__owner=self.request.user
        ).select_related("library")

    @action(detail=True, methods=["post"])
    def acknowledge(self, request, pk=None):
        """Mark open → acknowledged. Resolved stays resolved (engine owns that)."""
        row = self.get_object()
        if row.status != Discrepancy.Status.RESOLVED:
            row.status = Discrepancy.Status.ACKNOWLEDGED
            row.save(update_fields=["status", "updated_at"])
        return Response(DiscrepancySerializer(row).data)
