"""Page-number envelope. AI-written [!]."""

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.api.tests.conftest import results
from apps.services.models import Service

User = get_user_model()


@pytest.fixture
def api():
    return APIClient()


@pytest.mark.django_db
def test_list_is_paginated_envelope_detail_is_not(api, db):
    user = User.objects.create_user("alice", password="x")
    one = Service.objects.create(name="Alpha", url="http://a.test", owner=user)
    Service.objects.create(name="Beta", url="http://b.test", owner=user)
    api.force_authenticate(user)

    listing = api.get("/api/services/")
    assert listing.status_code == 200
    body = listing.json()
    assert body["count"] == 2
    assert body["next"] is None
    assert body["previous"] is None
    assert {row["name"] for row in body["results"]} == {"Alpha", "Beta"}

    detail = api.get(f"/api/services/{one.pk}/")
    assert detail.status_code == 200
    assert "results" not in detail.json()
    assert detail.json()["name"] == "Alpha"


@pytest.mark.django_db
def test_page_size_splits_and_page_two_has_the_rest(api, db):
    user = User.objects.create_user("alice", password="x")
    Service.objects.create(name="Alpha", url="http://a.test", owner=user)
    Service.objects.create(name="Beta", url="http://b.test", owner=user)
    api.force_authenticate(user)

    page1 = api.get("/api/services/?page_size=1")
    assert page1.status_code == 200
    body = page1.json()
    assert body["count"] == 2
    assert body["next"] is not None
    assert "page=2" in body["next"]
    assert len(body["results"]) == 1
    first_name = body["results"][0]["name"]

    page2 = api.get("/api/services/?page_size=1&page=2")
    assert page2.status_code == 200
    assert len(results(page2)) == 1
    assert results(page2)[0]["name"] != first_name
    assert {first_name, results(page2)[0]["name"]} == {"Alpha", "Beta"}
