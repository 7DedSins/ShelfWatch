"""IsOwner vs list leak. AI-written [!]."""

from types import SimpleNamespace

import pytest
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated

from apps.api.permissions import IsOwner
from apps.api.views import ServiceViewSet
from apps.services.models import Service

User = get_user_model()


@pytest.mark.django_db
def test_is_owner_object_permission_only():
    alice = User.objects.create_user("alice", password="x")
    bob = User.objects.create_user("bob", password="x")
    own = Service.objects.create(name="A", url="http://a.test", owner=alice)
    other = Service.objects.create(name="B", url="http://b.test", owner=bob)
    orphan = Service.objects.create(name="O", url="http://o.test")
    perm = IsOwner()
    req = SimpleNamespace(user=alice)
    assert perm.has_object_permission(req, None, own) is True
    assert perm.has_object_permission(req, None, other) is False
    assert perm.has_object_permission(req, None, orphan) is False
    # List trap: default has_permission is True, so IsOwner never hides rows.
    assert perm.has_permission(req, None) is True


def test_service_viewset_wires_is_owner_plural_attribute():
    # DRF reads permission_classes, not permission_class. A typo is a silent no-op.
    classes = ServiceViewSet.permission_classes
    assert IsAuthenticated in classes
    assert IsOwner in classes
