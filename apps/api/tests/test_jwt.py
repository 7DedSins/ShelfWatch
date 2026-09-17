"""JWT obtain/refresh and public schema. AI-written [!]."""

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.api.tests.conftest import results
from apps.services.models import Service

User = get_user_model()


@pytest.fixture
def api():
    return APIClient()


@pytest.fixture
def alice(db):
    user = User.objects.create_user("alice", password="x")
    Service.objects.create(name="Alice Kavita", url="http://a.test", owner=user)
    return user


@pytest.mark.django_db
def test_anonymous_services_is_401_bearer_challenge(api):
    response = api.get("/api/services/")
    assert response.status_code == 401
    assert "Bearer" in response.headers.get("WWW-Authenticate", "")


@pytest.mark.django_db
def test_token_pair_then_bearer_list(api, alice):
    pair = api.post(
        "/api/token/",
        {"username": "alice", "password": "x"},
        format="json",
    )
    assert pair.status_code == 200
    access = pair.json()["access"]
    refresh = pair.json()["refresh"]
    api.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
    listing = api.get("/api/services/")
    assert listing.status_code == 200
    assert {row["name"] for row in results(listing)} == {"Alice Kavita"}

    api.credentials()
    rotated = api.post("/api/token/refresh/", {"refresh": refresh}, format="json")
    assert rotated.status_code == 200
    assert "access" in rotated.json()


@pytest.mark.django_db
def test_schema_public_api_key_write_only(api):
    response = api.get("/api/schema/", HTTP_ACCEPT="application/json")
    assert response.status_code == 200
    schema = response.json()
    paths = schema["paths"]
    assert "/api/token/" in paths
    assert "/api/services/" in paths
    api_key = schema["components"]["schemas"]["Service"]["properties"]["api_key"]
    assert api_key.get("writeOnly") is True
