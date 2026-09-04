# Milestone 06 — DRF API

**Goal:** a complete, documented, correctly-authorised REST API — the contract the React
frontend will consume in Phase 4.

**Detours first:** [django/06 DRF](../02-django/06-drf.md) ·
[concepts/04 Authorization and tenancy](../01-concepts/04-authorization-and-tenancy.md)

**Sessions:** 3

---

## Design decisions to make and write down

1. **What is writable.** Service, Library, Discrepancy (acknowledge only) — CRUD.
   HealthCheck and DiskItem — **read-only**, because nothing should create them by hand.
   Use `ReadOnlyModelViewSet` so this is structural rather than a convention.
2. **⚠️ `get_queryset()` is the security boundary.** Filter by `request.user` there.
   `IsOwner` is defence in depth. **Build the bug first** (see "Break it") — it is invisible in
   code review and obvious in a test.
3. **404, not 403,** for another user's object. Falls out naturally from filtering in
   `get_queryset`. Notice the secure design is also the simpler one.
4. **Pagination per resource.** Page-number for services and libraries; **cursor for
   `HealthCheck`**, because it is append-only and offset pagination duplicates and skips rows
   as new ones arrive.
5. **Custom actions.** `POST /services/{id}/poll/`, `/libraries/{id}/scan/`,
   `/discrepancies/{id}/acknowledge/`. **Throttle the first two** — they dispatch real work
   onto your queues and are trivially abusable.
6. **The API key never leaves.** `write_only=True`. Plus **a test asserting the value appears
   in no response body anywhere.**
7. **Schema quality.** `drf-spectacular` output becomes the React frontend's TypeScript types
   in Phase 4. **A sloppy schema costs you later** — the frontend will trust it and be wrong.

---

## Build

- `apps/api/` — serializers, viewsets, router, permissions.
- Global `DEFAULT_PERMISSION_CLASSES = [IsAuthenticated]`.
- `get_queryset()` scoping on every viewset, including nested resources.
- `django-filter` for `?kind=`, `?resolved=`, `?library=`; `OrderingFilter`.
- Cursor pagination on `HealthCheck`.
- The three custom actions with `ScopedRateThrottle`.
- JWT via `simplejwt`.
- `drf-spectacular` → `/api/schema/` and Swagger at `/api/docs/`.
- The full authorization matrix test.

---

## Break it

1. **Build the leak.** Use only `IsOwner`, no `get_queryset` filtering. Create two users with
   data. `GET /api/services/` as user A. **See user B's services.** Then write the matrix test
   and watch it fail. Fix it. *The code looked correct the whole time.*
2. Verify cross-user detail access returns **404**, not 403. Explain why.
3. Check the **nested second level**: `Discrepancy` → `Library` → `Service` → `owner`. Easy to
   forget. Test it.
4. Write the test that greps every response body for an API key value. Remove `write_only` and
   watch it fail.
5. Cursor-paginate `HealthCheck` while polls are actively inserting rows. Confirm no duplicates
   and no skips. Then switch to offset pagination and **watch both happen.**
6. Hammer `POST /services/{id}/poll/`. Confirm `429` and that you have not filled your Celery
   queue.
7. Add a new viewset with no permission classes. Confirm it is **closed** by default.
8. Nest libraries in the service serializer. **Measure the query count.** Fix in
   `get_queryset()`. Measure again. Record both.
9. Open Swagger. Check every endpoint's schema is actually correct — try a request from the UI.
   A wrong schema is worse than none.

---

## Done when

- [ ] You built the list-endpoint leak and caught it with a test
- [ ] Full authz matrix: owner/other/anonymous × list/detail, every endpoint
- [ ] Cross-user access returns 404
- [ ] Automated proof secrets never serialize out
- [ ] Cursor pagination proven correct under concurrent inserts
- [ ] Trigger actions throttled
- [ ] New viewsets closed by default
- [ ] Serializer N+1 found and fixed with counts
- [ ] Swagger accurate and screenshotted for the README
- [ ] Committed: `feat(m06): DRF API with scoped querysets and OpenAPI schema`

---

## Interview connection

- *"**Do object-level permissions protect a list endpoint?**"* — with the story of building
  the bug.
- *"Why 404 instead of 403?"*
- *"When would you use cursor pagination?"* — you have seen offset fail.
- *"How do you stop a field being returned?"*
- *"How do you keep an API and its client in sync?"*

---

**Next:** [m07 — Alerts](m07-alerts.md)
