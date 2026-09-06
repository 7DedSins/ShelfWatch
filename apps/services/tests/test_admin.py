import pytest
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.urls import reverse

from apps.services.admin import ServiceAdmin
from apps.services.models import Service


def test_service_is_registered_with_service_admin():
    assert Service in admin.site._registry
    assert isinstance(admin.site._registry[Service], ServiceAdmin)


def test_service_admin_list_and_search_config():
    assert ServiceAdmin.list_display == ("name", "url", "created_at", "updated_at")
    assert ServiceAdmin.search_fields == ("name",)
    assert ServiceAdmin.readonly_fields == ("created_at", "updated_at")


@pytest.mark.django_db
def test_staff_can_open_service_changelist(client):
    User = get_user_model()
    user = User.objects.create_superuser("admin", "admin@example.com", "password")
    client.force_login(user)
    url = reverse("admin:services_service_changelist")
    Service.objects.create(name="Kavita", url="https://example.com")
    response = client.get(url)
    assert response.status_code == 200
    content = response.content.decode()
    assert "Kavita" in content
    assert "https://example.com" in content
