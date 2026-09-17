"""Object-level owner check. Does not protect list endpoints."""

from rest_framework.permissions import BasePermission


class IsOwner(BasePermission):
    """True when ``obj.owner`` is the caller. Unused on list views.

    DRF never calls ``has_object_permission`` for ``GET /api/services/``.
    Tenancy is ``get_queryset()``; this class is defence in depth on detail.
    """

    def has_object_permission(self, request, view, obj):
        return getattr(obj, "owner", None) == request.user

