"""API URL conf. Included from config.urls at ``/api/``.

DefaultRouter emits list/detail plus ``@action`` routes
(``/services/{id}/poll/``, ``/libraries/{id}/scan/``,
``/discrepancies/{id}/acknowledge/``).
"""

from rest_framework.routers import DefaultRouter

from .views import (
    DiskItemViewSet,
    DiscrepancyViewSet,
    LibraryViewSet,
    ServiceViewSet,
)

router = DefaultRouter()
router.register("services", ServiceViewSet, basename="service")
router.register("libraries", LibraryViewSet, basename="library")
router.register("disk-items", DiskItemViewSet, basename="diskitem")
router.register("discrepancies", DiscrepancyViewSet, basename="discrepancy")
urlpatterns = router.urls
