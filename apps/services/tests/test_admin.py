from unittest.mock import patch

import pytest
from django.contrib import admin, messages
from django.contrib.auth import get_user_model
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import RequestFactory
from django.urls import reverse

from apps.services.admin import ServiceAdmin
from apps.services.connectors.base import HealthResult, ServiceUnavailable
from apps.services.models import Service


def test_service_is_registered_with_service_admin():
    assert Service in admin.site._registry
    assert isinstance(admin.site._registry[Service], ServiceAdmin)


def test_kind_readonly_on_change_not_on_add():
    admin_instance = ServiceAdmin(Service, admin.site)
    request = RequestFactory().get("/admin/")
    add_fields = admin_instance.get_readonly_fields(request, obj=None)
    assert "kind" not in add_fields
    change_fields = admin_instance.get_readonly_fields(request, obj=Service())
    assert "kind" in change_fields


def test_service_admin_list_and_search_config():
    assert ServiceAdmin.list_display == (
        "name",
        "url",
        "created_at",
        "updated_at",
        "kind",
        "last_health_ok",
        "last_polled_at",
        "poll_interval_seconds",
    )
    assert "api_key" not in ServiceAdmin.list_display
    assert ServiceAdmin.search_fields == ("name",)
    assert ServiceAdmin.readonly_fields == (
        "created_at",
        "updated_at",
        "last_health_ok",
        "last_polled_at",
    )
    assert "test_connection" in ServiceAdmin.actions


def _admin_request():
    request = RequestFactory().post("/admin/")
    request.session = {}
    request._messages = FallbackStorage(request)
    return request


@pytest.mark.django_db
def test_test_connection_action_success_message():
    service = Service.objects.create(name="Kavita", url="http://kavita.test")
    admin_instance = ServiceAdmin(Service, admin.site)
    request = _admin_request()
    with patch(
        "apps.services.admin.poll_health",
        return_value=HealthResult(ok=True, detail="up"),
    ):
        admin_instance.test_connection(request, Service.objects.filter(pk=service.pk))
    stored = list(request._messages)
    assert any("Kavita" in str(m) and "ok=True" in str(m) for m in stored)


@pytest.mark.django_db
def test_test_connection_action_error_message():
    service = Service.objects.create(name="Kavita", url="http://down.test")
    admin_instance = ServiceAdmin(Service, admin.site)
    request = _admin_request()
    with patch(
        "apps.services.admin.poll_health",
        side_effect=ServiceUnavailable("timed out"),
    ):
        admin_instance.test_connection(request, Service.objects.filter(pk=service.pk))
    stored = list(request._messages)
    assert any(m.level == messages.ERROR and "timed out" in str(m) for m in stored)


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
