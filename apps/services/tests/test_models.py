import pytest
from django.db import IntegrityError

from apps.services.models import Service


@pytest.mark.django_db
def test_service_name_must_be_unique():
    Service.objects.create(name="Kavita", url="https://example.com")
    with pytest.raises(IntegrityError):
        Service.objects.create(name="Kavita", url="https://another-example.com")
