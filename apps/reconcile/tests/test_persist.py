"""Reopen vs auto-resolve. AI-written [!]."""

import pytest

from apps.libraries.models import Library
from apps.reconcile.diff import DiscrepancyDraft, DiscrepancyKind
from apps.reconcile.models import Discrepancy
from apps.reconcile.persist import apply_drafts
from apps.services.models import Service


@pytest.fixture
def library(db) -> Library:
    service = Service.objects.create(name="Kavita", url="http://kavita.test")
    return Library.objects.create(service=service, name="Manga", root_path="/tmp")


def _draft(key="solo leveling"):
    return DiscrepancyDraft(DiscrepancyKind.MISSING_IN_SERVICE, key)


@pytest.mark.django_db
def test_create_then_auto_resolve(library):
    apply_drafts(library, [_draft()])
    row = Discrepancy.objects.get()
    assert row.status == Discrepancy.Status.OPEN
    apply_drafts(library, [])
    row.refresh_from_db()
    assert row.status == Discrepancy.Status.RESOLVED
    assert row.resolved_at is not None


@pytest.mark.django_db
def test_resolved_reopens_on_recurrence(library):
    apply_drafts(library, [_draft()])
    apply_drafts(library, [])
    apply_drafts(library, [_draft()])
    row = Discrepancy.objects.get()
    assert row.status == Discrepancy.Status.OPEN
    assert row.resolved_at is None
    assert Discrepancy.objects.count() == 1
