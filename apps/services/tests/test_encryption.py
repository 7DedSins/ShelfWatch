import pytest
from django.contrib.auth import get_user_model
from django.db import connection
from django.urls import reverse

from apps.services.models import Service

PLAINTEXT = "kavita-test-token-not-real"


def _raw_api_key(service_id):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT api_key FROM services_service WHERE id = %s",
            [service_id],
        )
        row = cursor.fetchone()
    return row[0] if row else None


@pytest.mark.django_db
def test_api_key_round_trips_in_python():
    service = Service.objects.create(
        name="Kavita",
        url="https://example.com",
        api_key=PLAINTEXT,
    )
    service.refresh_from_db()
    assert service.api_key == PLAINTEXT


@pytest.mark.django_db
def test_api_key_is_ciphertext_in_sqlite():
    service = Service.objects.create(
        name="Kavita",
        url="https://example.com",
        api_key=PLAINTEXT,
    )
    raw = _raw_api_key(service.pk)
    assert raw
    assert raw != PLAINTEXT
    assert PLAINTEXT not in raw
    assert raw.startswith("gAAAA")


@pytest.mark.django_db
def test_blank_api_key_does_not_go_through_fernet():
    service = Service.objects.create(name="Komga", url="https://komga.example.com")
    service.refresh_from_db()
    assert service.api_key in ("", None)
    raw = _raw_api_key(service.pk)
    assert raw in ("", None)


@pytest.mark.django_db
def test_str_does_not_include_api_key():
    service = Service.objects.create(
        name="Kavita",
        url="https://example.com",
        api_key=PLAINTEXT,
    )
    assert PLAINTEXT not in str(service)
    assert str(service) == "Kavita"


@pytest.mark.django_db
def test_admin_changelist_does_not_show_api_key(client):
    User = get_user_model()
    user = User.objects.create_superuser("admin", "admin@example.com", "password")
    client.force_login(user)
    Service.objects.create(
        name="Kavita",
        url="https://example.com",
        api_key=PLAINTEXT,
    )
    response = client.get(reverse("admin:services_service_changelist"))
    assert response.status_code == 200
    body = response.content.decode()
    assert PLAINTEXT not in body
    assert "Kavita" in body
