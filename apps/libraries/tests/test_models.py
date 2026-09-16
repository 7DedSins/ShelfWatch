"""Library / DiskItem uniqueness. AI-written [!]."""

import pytest
from django.db import IntegrityError
from django.utils import timezone

from apps.libraries.models import DiskItem, Library
from apps.services.models import Service


@pytest.fixture
def service(db):
    return Service.objects.create(name="Kavita", url="http://kavita.test")


@pytest.mark.django_db
def test_library_unique_per_service_name(service):
    Library.objects.create(service=service, name="Manga", root_path="/mnt/a")
    with pytest.raises(IntegrityError):
        Library.objects.create(service=service, name="Manga", root_path="/mnt/b")


@pytest.mark.django_db
def test_same_library_name_allowed_on_different_services(service):
    other = Service.objects.create(
        name="LRR",
        url="http://lrr.test",
        kind=Service.Kind.LANRARAGI,
    )
    Library.objects.create(service=service, name="Manga", root_path="/mnt/a")
    Library.objects.create(service=other, name="Manga", root_path="/mnt/b")
    assert Library.objects.filter(name="Manga").count() == 2


@pytest.mark.django_db
def test_diskitem_unique_per_library_path(service):
    library = Library.objects.create(service=service, name="Manga", root_path="/tmp")
    now = timezone.now()
    DiskItem.objects.create(
        library=library,
        relative_path="One Piece",
        seen_at=now,
    )
    with pytest.raises(IntegrityError):
        DiskItem.objects.create(
            library=library,
            relative_path="One Piece",
            seen_at=now,
        )


@pytest.mark.django_db
def test_same_relative_path_allowed_in_different_libraries(service):
    a = Library.objects.create(service=service, name="A", root_path="/a")
    b = Library.objects.create(service=service, name="B", root_path="/b")
    now = timezone.now()
    DiskItem.objects.create(library=a, relative_path="Solo", seen_at=now)
    DiskItem.objects.create(library=b, relative_path="Solo", seen_at=now)
    assert DiskItem.objects.filter(relative_path="Solo").count() == 2
