# Milestone 05 — Reconciliation

**Goal:** diff what each service thinks it has against what is actually on disk, and turn the
difference into `Discrepancy` rows.

**Detours first:** [concepts/01 Polling and reconciliation](../01-concepts/01-polling-and-reconciliation.md) ·
[django/08 Testing Django](../02-django/08-testing-django.md)

**Sessions:** 3–4

> **This milestone is the product.** Everything before it was plumbing. **Write the tests
> first** — the test table *is* the specification, and this is one of the few places where TDD
> is unambiguously the right order.

---

## Design decisions to make and write down

1. **The taxonomy — derive it from real incidents on your own box.** `MISSING_IN_SERVICE`,
   `MISSING_ON_DISK`, `COUNT_MISMATCH`, `NO_COVER`, `STALLED_SCAN`, `EMPTY_SERIES`. Each one
   should map to something that has actually happened to you. **If you cannot name the
   incident, do not add the category.**
2. **Matching.** Disk folder `Solo Leveling (Official)` vs. service series `Solo Leveling`.
   Normalise how? **Be conservative** — an unmatched pair is a *visible* discrepancy; a wrongly
   matched pair is invisible. Find two real folder names that a naive rule would wrongly match.
3. **⚠️ Never reconcile against a failed fetch.** If the connector raised, **skip the
   reconciliation entirely.** Do not diff against a partial or empty inventory. This is the
   most dangerous possible bug here: it would report your entire library as deleted, and if
   alerts are on, it would tell you so at 3am.
4. **Discrepancy lifecycle.** Created, acknowledged, resolved. Does a resolved discrepancy that
   recurs create a new row or reopen the old one? **Reopen** — otherwise the history of a
   recurring problem is scattered. Justify it.
5. **Auto-resolution.** A discrepancy that no longer holds should resolve itself on the next
   reconcile. Otherwise the user is manually clearing a list forever and stops looking at it.
6. **Thresholds.** Is a count mismatch of 1 worth reporting? Of 10? Configurable per library,
   with a sensible default — otherwise the signal drowns in noise.
7. **`STALLED_SCAN`.** A service reporting a scan running for longer than N hours. **Nothing
   else detects this**, it has happened to you twice via FUSE hangs, and it is the single most
   distinctive feature in the product. What is N?

---

## Build

- `apps/reconcile/models.py` — `Discrepancy`, `DiscrepancyKind`, lifecycle fields.
- **`apps/reconcile/tests/test_diff.py` first** — table-driven, one row per scenario, all red.
- `apps/reconcile/services.py` — the diff engine. **Pure functions**: two inventories in,
  a discrepancy set out. No database, no HTTP, no Celery.
- `reconcile_library(library_id)` — a thin task calling it, chained after `scan_library` with
  `.si`.
- Auto-resolution of discrepancies that no longer hold.
- Admin for discrepancies with a bulk-acknowledge action.

---

## Break it

1. **Write the test table before the engine.** Every kind, plus: identical inventories,
   both empty, disk empty but service full, service empty but disk full.
2. **The critical test:** make the connector raise and confirm reconciliation is **skipped**,
   not run against an empty inventory. Then deliberately let it run against the empty result
   and watch it generate a discrepancy for every series you own. **Sit with that output.**
3. Rename a folder on disk. Confirm you get one `MISSING_IN_SERVICE` and one
   `MISSING_ON_DISK` — and consider whether you would rather detect it as a rename.
4. Add a chapter on disk without rescanning the service. Confirm `COUNT_MISMATCH`.
5. Resolve a discrepancy manually, then recreate the condition. Confirm your reopen-vs-new
   decision behaves as designed.
6. Fix a condition and rescan. Confirm auto-resolution.
7. Run reconciliation over 8,000 series. **Time it.** If it is slow, is it the diff or the
   queries? Measure before optimising.
8. Find two real folder names in your library that your matching rule wrongly pairs. Tighten it.
9. **Point it at your real Contabo services.** Look at what it finds. **You will learn something
   about your own libraries** — write it in the session log. That is the moment this project
   becomes real.

---

## Done when

- [ ] Tests were written before the engine
- [ ] The diff engine is pure — no DB, no HTTP, no Celery imports
- [ ] **Failed fetches skip reconciliation**, tested, and you have seen the alternative
- [ ] Auto-resolution works
- [ ] The taxonomy maps to real incidents
- [ ] Matching is conservative and its false-positive case is known
- [ ] Reconciliation timed over a realistic library
- [ ] **It has told you something true about your own setup**
- [ ] Committed: `feat(m05): reconciliation engine with discrepancy lifecycle`

---

## Interview connection

**Your best system-design story in this project.**

- *"What does your system actually do?"* — and now the answer is interesting.
- *"How do you diff two sources of truth?"*
- *"What happens if one source fails to respond?"* — the answer is "nothing", and the reason
  is that the alternative is catastrophic.
- *"How do you keep an alert list from becoming noise?"* — auto-resolution and thresholds.
- *"How do you decide what to alert on?"*
- *"Tell me about testing something complex."* — the table-driven spec, written first.

---

**Checkpoint reached.** Do the system-design drill in the
[question bank](../06-interview/question-bank.md) for the first time.

**Next:** [m06 — DRF API](m06-drf-api.md)
