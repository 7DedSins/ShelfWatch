# 08 — Testing Django

**Status:** contract — expand when taught
**Prereqs:** [06-drf.md](06-drf.md), [07-celery-and-beat.md](07-celery-and-beat.md)
**Used by:** [m05](../03-build/m05-reconciliation.md), [m08](../03-build/m08-performance-pass.md)
**Time:** ~90 min

---

## Why this lesson exists

ShelfWatch's most valuable logic — the reconciliation diff — is pure and therefore perfectly
testable. Its most dangerous behaviour — a connector failure looking like an empty library — is
only caught by a test you thought to write.

---

## What you should be able to say afterwards

- How to test HTTP integrations without network access
- How to test Celery tasks without a broker
- Why the reconciliation tests should be written before the engine
- What the authorization matrix is and why every API needs one

---

## Concepts to cover

1. **The stack.** `pytest` + `pytest-django` + `factory_boy` + `respx`. Prefer pytest style
   over Django's `TestCase` classes — fixtures compose better than inheritance.
2. **`factory_boy`.** Factories for every model, with `SubFactory` for relationships. A test
   that needs a Discrepancy should not have to construct a User, Service, and Library by hand.
3. **Database.** `pytest-django` wraps each test in a transaction and rolls back. `--reuse-db`
   for speed locally, fresh in CI. Know when you need `django_db(transaction=True)` and what it
   costs.
4. **`respx` for connectors.** Record real responses from your actual Kavita instance once,
   commit them as fixtures, and test against those. **CI must be hermetic** — a test suite that
   needs your VPS is a suite that fails on someone else's machine.
   Cases that matter: success, 401-then-retry, malformed JSON, timeout, a paginated response.
5. **⚠️ The most important connector test.** A timeout must raise, **not** return an empty
   inventory. Write the test that proves conflating them would mark every series as missing.
   This is the bug with the largest blast radius in the project.
6. **Celery tests.** `CELERY_TASK_ALWAYS_EAGER=True` in test settings. Fast and deterministic.
   **Know what it skips**: serialisation, so a non-JSON-serialisable argument passes tests and
   fails in production. Add one test that exercises real serialisation.
7. **Reconciliation tests — write these first.** Construct a disk inventory and a service
   inventory, assert the exact discrepancy set. **Table-driven**, one row per scenario. This is
   the specification of the product; writing it before the code is the right order and one of
   the few places where TDD is unambiguously correct.
8. **The authorization matrix.** For every endpoint: owner → 200, other user → **404**,
   anonymous → 401, for **list and detail**. Parametrized so adding an endpoint adds a row.
9. **Scan tests.** `tmp_path` with a real synthetic directory tree. Do not mock the filesystem —
   you would be testing your mock.
10. **What not to test.** Django's ORM, DRF's routing, third-party libraries. Test *your* logic.
11. **Coverage.** 80%+ overall, higher on `reconcile/` and `connectors/`. The ratio is
    deliberate; be able to explain it.
12. **CI.** GitHub Actions with Postgres and Redis service containers. Green on every push.

---

## Exercise

1. Set up the stack. Factories for every model.
2. **Write the reconciliation test table before the engine exists.** Every discrepancy kind,
   plus the empty and identical cases. All red.
3. Connector tests with `respx`: success, 401-then-retry-once-then-fail, malformed JSON,
   timeout, pagination.
4. **The timeout test**: assert it raises rather than returning `[]`. Then deliberately make it
   return `[]` and watch the reconciliation test produce hundreds of false discrepancies.
   **That contrast is the lesson.**
5. Task tests with `ALWAYS_EAGER`. Then one test that passes a non-serialisable argument and
   confirm eager mode does not catch it.
6. The parametrized authorization matrix across every endpoint.
7. Scan test against a real `tmp_path` tree, including a deleted-file case via `seen_at`.
8. Wire CI with service containers. Make it fail, then pass.
9. Run the suite twice. Identical results, or your isolation is broken.

---

## Done when

- [ ] Reconciliation tests were written before the engine
- [ ] Connector tests are hermetic — CI needs no VPS
- [ ] The timeout-vs-empty distinction is tested, and you have seen the damage without it
- [ ] Authorization matrix covers list and detail for every endpoint
- [ ] Scans tested against a real temp tree
- [ ] 80%+ coverage, higher where it matters
- [ ] CI green with Postgres and Redis

---

## Interview questions this unlocks

- "How do you test code that calls an external API?"
- "How do you test Celery tasks? What does eager mode miss?"
- "What's an authorization matrix?"
- "What would you write tests for first?"
- "How do you keep CI from depending on external services?"
