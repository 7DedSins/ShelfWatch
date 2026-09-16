"""Write DiscrepancyDrafts to rows. Reopen resolved; auto-resolve vanished."""

from django.utils import timezone

from .diff import DiscrepancyDraft
from .models import Discrepancy


def apply_drafts(library, drafts: list[DiscrepancyDraft], *, now=None) -> int:
    now = now or timezone.now()
    incoming = {(d.kind.value, d.key) for d in drafts}
    existing = {
        (row.kind, row.key): row
        for row in Discrepancy.objects.filter(library=library)
    }
    written = 0
    for draft in drafts:
        ident = (draft.kind.value, draft.key)
        row = existing.get(ident)
        if row is None:
            Discrepancy.objects.create(
                library=library,
                kind=draft.kind.value,
                key=draft.key,
                status=Discrepancy.Status.OPEN,
            )
            written += 1
            continue
        if row.status == Discrepancy.Status.RESOLVED:
            row.status = Discrepancy.Status.OPEN
            row.resolved_at = None
            row.save(update_fields=["status", "resolved_at", "updated_at"])
            written += 1
    for ident, row in existing.items():
        if ident in incoming:
            continue
        if row.status == Discrepancy.Status.RESOLVED:
            continue
        row.status = Discrepancy.Status.RESOLVED
        row.resolved_at = now
        row.save(update_fields=["status", "resolved_at", "updated_at"])
        written += 1
    return written
