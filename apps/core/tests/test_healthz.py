from unittest.mock import patch

import pytest
from django.db.utils import OperationalError


@pytest.mark.django_db
def test_healthz_ok(client):
    response = client.get("/healthz/")
    assert response.status_code == 200
    assert response["Content-Type"].startswith("application/json")
    body = response.json()
    assert body == {"status": "ok"}


@pytest.mark.django_db
def test_healthz_without_trailing_slash_redirects(client):
    response = client.get("/healthz", follow=False)
    assert response.status_code in (301, 302)
    assert response["Location"].endswith("/healthz/")


@pytest.mark.django_db
def test_healthz_accepts_head(client):
    response = client.head("/healthz/")
    assert response.status_code == 200
    assert response.content == b""


@pytest.mark.django_db
def test_healthz_post_hits_the_same_view(client):
    # Current view does not check HTTP method; document that until we lock it down.
    response = client.post("/healthz/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.django_db
@patch(
    "apps.core.views.connection.ensure_connection",
    side_effect=OperationalError("database is locked"),
)
def test_healthz_returns_503_when_db_fails(_mock_connect, client):
    response = client.get("/healthz/")
    assert response.status_code == 503
    body = response.json()
    assert body["status"] == "error"
    assert "database is locked" in body["detail"]
    assert set(body) == {"status", "detail"}


def test_unknown_path_is_404(client):
    response = client.get("/does-not-exist/")
    assert response.status_code == 404


def test_healthz_view_does_not_import_services():
    import apps.core.views as core_views

    assert "apps.services" not in getattr(core_views, "__dict__", {})
    source = core_views.__file__
    with open(source, encoding="utf-8") as fh:
        text = fh.read()
    assert "apps.services" not in text
    assert "from apps.services" not in text
