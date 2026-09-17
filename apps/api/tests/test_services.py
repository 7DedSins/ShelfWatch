"""Service list/detail tenancy. AI-written [!]."""

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.services.models import Service

User = get_user_model()


@pytest.fixture
def api():
    return APIClient()


@pytest.fixture
def users(db):
    a = User.objects.create_user("alice", password="x")
    b = User.objects.create_user("bob", password="x")
    return a, b


@pytest.fixture
def services(users):
    a, b = users
    sa = Service.objects.create(
        name="Alice Kavita",
        url="http://a.test",
        owner=a,
        api_key="secret-alice",
    )
    sb = Service.objects.create(
        name="Bob LRR",
        url="http://b.test",
        owner=b,
        kind=Service.Kind.LANRARAGI,
        api_key="secret-bob",
    )
    orphan = Service.objects.create(name="Orphan", url="http://o.test")
    return sa, sb, orphan


def _assert_unauthenticated(response):
    # SessionAuthentication: no login → 403. Token/JWT later → 401.
    assert response.status_code in (401, 403)


@pytest.mark.django_db
def test_anonymous_list_is_rejected(api):
    _assert_unauthenticated(api.get("/api/services/"))


@pytest.mark.django_db
def test_anonymous_detail_is_rejected(api, services):
    sa, _sb, _orphan = services
    _assert_unauthenticated(api.get(f"/api/services/{sa.pk}/"))


@pytest.mark.django_db
def test_list_only_own_services(api, users, services):
    a, _b = users
    sa, _sb, _orphan = services
    api.force_authenticate(a)
    response = api.get("/api/services/")
    assert response.status_code == 200
    names = {row["name"] for row in response.json()}
    assert names == {sa.name}


@pytest.mark.django_db
def test_unowned_and_other_user_hidden(api, users, services):
    a, _b = users
    _sa, sb, orphan = services
    api.force_authenticate(a)
    ids = {row["id"] for row in api.get("/api/services/").json()}
    assert sb.pk not in ids
    assert orphan.pk not in ids


@pytest.mark.django_db
def test_other_user_detail_is_404_not_403(api, users, services):
    a, _b = users
    _sa, sb, _orphan = services
    api.force_authenticate(a)
    response = api.get(f"/api/services/{sb.pk}/")
    assert response.status_code == 404


@pytest.mark.django_db
def test_unowned_detail_is_404(api, users, services):
    a, _b = users
    _sa, _sb, orphan = services
    api.force_authenticate(a)
    assert api.get(f"/api/services/{orphan.pk}/").status_code == 404


@pytest.mark.django_db
def test_own_detail_ok_and_api_key_absent(api, users, services):
    a, _b = users
    sa, _sb, _orphan = services
    api.force_authenticate(a)
    response = api.get(f"/api/services/{sa.pk}/")
    assert response.status_code == 200
    body = response.json()
    assert "api_key" not in body
    assert "secret-alice" not in str(body)
    assert body["name"] == sa.name
    assert body["kind"] == Service.Kind.KAVITA


@pytest.mark.django_db
def test_list_does_not_serialize_api_key(api, users, services):
    a, _b = users
    api.force_authenticate(a)
    body = api.get("/api/services/").json()
    assert all("api_key" not in row for row in body)
    assert "secret-alice" not in str(body)


@pytest.mark.django_db
def test_readonly_rejects_writes(api, users, services):
    a, _b = users
    sa, _sb, _orphan = services
    api.force_authenticate(a)
    assert api.post("/api/services/", {"name": "X", "url": "http://x.test"}).status_code == 405
    assert api.put(f"/api/services/{sa.pk}/", {"name": "Z"}).status_code == 405
    assert api.patch(f"/api/services/{sa.pk}/", {"name": "Z"}).status_code == 405
    assert api.delete(f"/api/services/{sa.pk}/").status_code == 405


@pytest.mark.django_db
def test_user_with_no_services_gets_empty_list(api, db):
    lone = User.objects.create_user("carol", password="x")
    api.force_authenticate(lone)
    response = api.get("/api/services/")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.django_db
def test_healthz_still_public():
    from django.test import Client

    assert Client().get("/healthz/").status_code == 200
