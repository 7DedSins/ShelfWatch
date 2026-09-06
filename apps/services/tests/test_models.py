import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import CharField

from apps.services.models import Service


@pytest.mark.django_db
def test_service_name_must_be_unique():
    Service.objects.create(name="Kavita", url="https://example.com")
    with pytest.raises(IntegrityError):
        Service.objects.create(name="Kavita", url="https://other.example.com")


@pytest.mark.django_db
def test_different_names_are_allowed():
    Service.objects.create(name="Kavita", url="https://kavita.example.com")
    Service.objects.create(name="Komga", url="https://komga.example.com")
    assert Service.objects.count() == 2


@pytest.mark.django_db
def test_str_returns_name():
    service = Service.objects.create(name="LANraragi", url="https://lrr.example.com")
    assert str(service) == "LANraragi"


@pytest.mark.django_db
def test_default_ordering_is_by_name():
    Service.objects.create(name="Zebra", url="https://z.example.com")
    Service.objects.create(name="Alpha", url="https://a.example.com")
    assert list(Service.objects.values_list("name", flat=True)) == ["Alpha", "Zebra"]


@pytest.mark.django_db
def test_timestamps_set_on_create_and_update():
    service = Service.objects.create(name="Kavita", url="https://example.com")
    assert service.created_at is not None
    assert service.updated_at is not None
    assert service.updated_at >= service.created_at

    created = service.created_at
    service.url = "https://kavita.example.com"
    service.save()
    service.refresh_from_db()
    assert service.created_at == created
    assert service.updated_at >= created


def test_name_field_is_unique_in_schema():
    # No database: this only reads model._meta.
    # type ignore: Pylance's Django types omit Field.unique / max_length.
    # Do not wrap in getattr — Ruff B009 rewrites that to field.unique on save.
    field = Service._meta.get_field("name")
    assert isinstance(field, CharField)
    assert field.unique is True  # type: ignore[attr-defined]
    assert field.max_length == 200  # type: ignore[attr-defined]


@pytest.mark.django_db
def test_full_clean_rejects_blank_name():
    service = Service(name="", url="https://example.com")
    with pytest.raises(ValidationError) as exc:
        service.full_clean()
    assert "name" in exc.value.message_dict


@pytest.mark.django_db
def test_full_clean_rejects_invalid_url():
    service = Service(name="Kavita", url="not-a-url")
    with pytest.raises(ValidationError) as exc:
        service.full_clean()
    assert "url" in exc.value.message_dict


@pytest.mark.django_db
def test_full_clean_rejects_name_longer_than_max_length():
    service = Service(name="k" * 201, url="https://example.com")
    with pytest.raises(ValidationError) as exc:
        service.full_clean()
    assert "name" in exc.value.message_dict


@pytest.mark.django_db
def test_save_does_not_run_full_clean():
    # Characterization: ORM save() does not call full_clean(). Empty name
    # is invalid for forms/admin but currently allowed at the SQL layer
    # because CharField stores "" not NULL. Do not "fix" this in tests.
    service = Service.objects.create(name="", url="https://example.com")
    assert service.pk is not None
