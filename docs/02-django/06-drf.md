# 06 — Django REST Framework

**Status:** contract — expand when taught
**Prereqs:** [04-orm-and-query-optimization.md](04-orm-and-query-optimization.md), [concepts/04](../01-concepts/04-authorization-and-tenancy.md)
**Used by:** [m06](../03-build/m06-drf-api.md)
**Time:** ~90 min

---

## Why this lesson exists

DRF is in almost every Python backend job description. It is also easy to use in a way that
works and is quietly insecure — see the list-endpoint trap in
[concepts/04](../01-concepts/04-authorization-and-tenancy.md).

---

## What you should be able to say afterwards

- How serializers validate and transform, and where custom validation belongs
- Why `get_queryset()` is the security boundary
- Which pagination style suits which data
- How the OpenAPI schema becomes your frontend's types

---

## Concepts to cover

1. **Serializers.** `ModelSerializer` for the common case, plain `Serializer` when the shape
   diverges from the model. `read_only`, `write_only`, `SerializerMethodField`. **`write_only`
   is how the API key enters and never leaves.**
2. **Validation layers.** Field-level `validate_<field>`, object-level `validate()`, and model
   `clean()`. Know which runs when — **DRF does not call model `clean()` by default**, which
   surprises people and silently skips rules you thought were enforced.
3. **ViewSets and routers.** `ModelViewSet` for full CRUD, `ReadOnlyModelViewSet` for
   `HealthCheck` and `DiskItem` (which nothing should create by hand). The router generates
   URLs; know what it generated.
4. **`get_queryset()` is the security boundary.** Filter by `request.user` here. Object
   permissions are defence in depth. Re-read
   [concepts/04](../01-concepts/04-authorization-and-tenancy.md) — this is the one thing in
   DRF that is genuinely dangerous to get wrong.
5. **Permissions.** Global `IsAuthenticated` default plus a custom `IsOwner`. New viewsets
   closed by default.
6. **Filtering, ordering, search.** `django-filter` for `?kind=`, `?resolved=`, `?library=`.
   `OrderingFilter`. Declared, not hand-rolled per view.
7. **Pagination.** Page-number for stable lists. **Cursor for `HealthCheck`** — an append-only
   log where offset pagination skips and duplicates rows as new ones arrive. Same reasoning as
   [Ferryman's delivery log](../../../Ferryman/docs/09-frontend/05-the-delivery-log-table.md).
8. **Custom actions.** `@action(detail=True, methods=["post"])` for `poll/`, `scan/`,
   `acknowledge/`. **Throttle them** — they dispatch real work and are trivially abusable.
9. **Throttling.** `ScopedRateThrottle` on the manual-trigger actions specifically.
10. **`drf-spectacular`.** Generates OpenAPI from your serializers → Swagger UI at `/api/docs/`
    → **TypeScript types for the React frontend** in Phase 4. The quality of your serializer
    annotations directly determines the quality of your frontend types.
11. **JWT with `simplejwt`.** Access and refresh tokens. Browser storage is
    [Ferryman frontend 07](../../../Ferryman/docs/09-frontend/07-auth-in-the-browser.md).
12. **N+1 in serializers.** A nested serializer over a related set is an N+1 per row. Fix it in
    `get_queryset()`, not in the serializer.

---

## Exercise

1. Build serializers and viewsets for Service, Library, Discrepancy; read-only for HealthCheck
   and DiskItem.
2. **Write the authorization matrix test first** (owner/other/anonymous × list/detail). Watch
   the list case fail with only `IsOwner`. Fix it in `get_queryset()`.
3. Add the test asserting the API key value appears in **no** response body.
4. Add filtering and ordering. Cursor pagination on `HealthCheck` — then insert rows while
   paging and confirm no duplicates or skips.
5. Add the three custom actions with throttling. Exceed a throttle and confirm `429`.
6. Nest libraries inside the service serializer. **Measure the query count.** Fix it in
   `get_queryset()`. Measure again.
7. Wire `drf-spectacular`. Open Swagger. **Screenshot for the README.** Confirm the schema is
   accurate — a wrong schema is worse than none, because the frontend will trust it.
8. Add JWT auth and get a token with `curl`.

---

## Done when

- [ ] Full authz matrix tested and passing, list included
- [ ] Automated proof that secrets never serialize out
- [ ] Cursor pagination proven correct under concurrent inserts
- [ ] Custom actions throttled
- [ ] Serializer N+1 found and fixed with counts
- [ ] Swagger accurate and screenshotted
- [ ] JWT working

---

## Interview questions this unlocks

- "How do you scope API data to the current user?"
- "Do object permissions protect list endpoints?"
- "When would you use cursor pagination?"
- "How do you stop a field being returned in a response?"
- "How do you avoid N+1s in a nested serializer?"
- "How do you document a REST API?"
