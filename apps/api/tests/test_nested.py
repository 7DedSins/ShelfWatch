"""Nested tenancy + trigger actions. AI-written [!]."""

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient
from unittest.mock import patch

from apps.libraries.models import DiskItem, Library
from apps.reconcile.models import Discrepancy
from apps.services.models import Service

User = get_user_model()


@pytest.fixture
def api():
    return APIClient()


@pytest.fixture
def world(db):
    a = User.objects.create_user("alice", password="x")
    b = User.objects.create_user("bob", password="x")
    sa = Service.objects.create(name="Alice", url="http://a.test", owner=a)
    sb = Service.objects.create(name="Bob", url="http://b.test", owner=b)
    now = timezone.now()
    la = Library.objects.create(
        service=sa, name="Manga", root_path="/a", remote_id="1"
    )
    lb = Library.objects.create(
        service=sb, name="Manga", root_path="/b", remote_id="2"
    )
    da = DiskItem.objects.create(
        library=la, relative_path="Solo", seen_at=now, file_count=1
    )
    db_item = DiskItem.objects.create(
        library=lb, relative_path="Secret", seen_at=now, file_count=1
    )
    disc_a = Discrepancy.objects.create(
        library=la, kind="missing_in_service", key="solo"
    )
    disc_b = Discrepancy.objects.create(
        library=lb, kind="missing_in_service", key="secret"
    )
    return {
        "a": a,
        "b": b,
        "sa": sa,
        "sb": sb,
        "la": la,
        "lb": lb,
        "da": da,
        "db_item": db_item,
        "disc_a": disc_a,
        "disc_b": disc_b,
    }


@pytest.mark.django_db
def test_library_list_scoped(api, world):
    api.force_authenticate(world["a"])
    ids = {row["id"] for row in api.get("/api/libraries/").json()}
    assert ids == {world["la"].pk}


@pytest.mark.django_db
def test_other_library_detail_404(api, world):
    api.force_authenticate(world["a"])
    assert api.get(f"/api/libraries/{world['lb'].pk}/").status_code == 404


@pytest.mark.django_db
def test_disk_items_scoped(api, world):
    api.force_authenticate(world["a"])
    ids = {row["id"] for row in api.get("/api/disk-items/").json()}
    assert ids == {world["da"].pk}
    assert api.get(f"/api/disk-items/{world['db_item'].pk}/").status_code == 404


@pytest.mark.django_db
def test_discrepancies_scoped(api, world):
    api.force_authenticate(world["a"])
    ids = {row["id"] for row in api.get("/api/discrepancies/").json()}
    assert ids == {world["disc_a"].pk}
    assert api.get(f"/api/discrepancies/{world['disc_b'].pk}/").status_code == 404


@pytest.mark.django_db
def test_acknowledge_own_not_others(api, world):
    api.force_authenticate(world["a"])
    response = api.post(f"/api/discrepancies/{world['disc_a'].pk}/acknowledge/")
    assert response.status_code == 200
    assert response.json()["status"] == "acknowledged"
    world["disc_a"].refresh_from_db()
    assert world["disc_a"].status == Discrepancy.Status.ACKNOWLEDGED
    assert (
        api.post(f"/api/discrepancies/{world['disc_b'].pk}/acknowledge/").status_code
        == 404
    )


@pytest.mark.django_db
def test_poll_queues_own_service_only(api, world):
    api.force_authenticate(world["a"])
    with patch("apps.api.views.poll_service.delay") as delay:
        response = api.post(f"/api/services/{world['sa'].pk}/poll/")
    assert response.status_code == 202
    delay.assert_called_once_with(world["sa"].pk)
    with patch("apps.api.views.poll_service.delay") as delay:
        assert api.post(f"/api/services/{world['sb'].pk}/poll/").status_code == 404
        delay.assert_not_called()


@pytest.mark.django_db
def test_scan_chains_own_library_only(api, world):
    api.force_authenticate(world["a"])
    with patch("apps.api.views.chain") as chain_fn:
        response = api.post(f"/api/libraries/{world['la'].pk}/scan/")
    assert response.status_code == 202
    chain_fn.assert_called_once()
    with patch("apps.api.views.chain") as chain_fn:
        assert api.post(f"/api/libraries/{world['lb'].pk}/scan/").status_code == 404
        chain_fn.assert_not_called()
