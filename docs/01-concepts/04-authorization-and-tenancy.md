# 04 — Authorization and tenancy

**Status:** contract — expand when taught
**Prereqs:** [03-secrets-at-rest.md](03-secrets-at-rest.md)
**Used by:** [m06](../03-build/m06-drf-api.md)
**Time:** ~60 min

---

## Why this lesson exists

ShelfWatch is multi-user. Each user's services, libraries, and discrepancies are theirs alone.
Broken object-level authorization is **the** most common serious API vulnerability, and DRF
makes it particularly easy to get wrong in a way that passes every test you thought to write.

---

## What you should be able to say afterwards

- The difference between authentication and authorization
- **Why object permissions do not protect list endpoints**
- Why another user's object should return 404, not 403
- How to make the safe thing the default

---

## Concepts to cover

1. **AuthN vs. AuthZ.** Who you are, versus what you may do. Two layers; conflating them is
   where broken access control starts.
2. **The DRF trap — the important part of this lesson.** A custom `IsOwner` permission with
   `has_object_permission` **only runs on detail views.** DRF calls it when it fetches a single
   object. On a **list** endpoint there is no single object, so it never runs, and
   `/api/services/` happily returns every service belonging to every user.

   Have them build exactly this bug and then find it with a test. **It is invisible in the
   code and obvious in the test**, which is precisely why it ships so often.
3. **`get_queryset()` is the real control.** Filter by `request.user` there. Then every action —
   list, retrieve, update, delete — is scoped, because they all start from the queryset. Object
   permissions become defence in depth rather than the only line.
4. **404, not 403.** Requesting another user's object returns `404`. A `403` confirms the
   object exists, which is an enumeration oracle. Filtering in `get_queryset` gives you this
   behaviour for free — notice that the secure design is also the simpler one.
5. **Safe by default.** Set `DEFAULT_PERMISSION_CLASSES` to `IsAuthenticated` globally, then
   open up specific endpoints deliberately. A new viewset should be **closed** unless someone
   opened it. Design so forgetting fails closed.
6. **Nested resources.** A Library belongs to a Service belongs to a User. Scoping Libraries
   means traversing the relationship — `Library.objects.filter(service__owner=user)`. Easy to
   forget on the second level, so test it.
7. **Background tasks have no user.** A Celery task has no `request`. It must be given the
   scope explicitly. **This is where multi-tenancy is most often forgotten**, because there is
   no request object to remind you.
8. **Token auth.** JWT via `simplejwt` for the React frontend. Where the token lives in the
   browser is [Ferryman's frontend lesson 07](../../../Ferryman/docs/09-frontend/07-auth-in-the-browser.md) —
   the same problem, and the answer does not change.

---

## Exercise

1. Build the viewset with `IsOwner` as the *only* control. Create two users with data.
2. **Write the authorization matrix test**: owner → 200, other user → 404, anonymous → 401,
   for **list and detail**. Watch the list test fail. Sit with that — the code looked right.
3. Fix it in `get_queryset()`. Re-run. Keep `IsOwner` as well and explain why.
4. Verify the response is `404` and not `403`, and articulate why that matters.
5. Do the same for the nested Library and Discrepancy endpoints. **Check the second level of
   nesting specifically.**
6. Set global `IsAuthenticated`. Add a new viewset with no permission classes and confirm it is
   closed by default.
7. Write a Celery task that touches user-scoped data. Confirm it needs explicit scoping.
   Deliberately omit it and see what leaks.

---

## Done when

- [ ] You built the list-endpoint leak and found it with a test
- [ ] `get_queryset()` filters by user everywhere, including nested resources
- [ ] The full authz matrix is tested for list *and* detail
- [ ] Cross-user access returns 404
- [ ] New endpoints are closed by default
- [ ] Tasks are explicitly scoped

---

## Interview questions this unlocks

- "How do you scope API data to the current user?"
- "**Do object-level permissions protect a list endpoint?**" — no, and this is the question.
- "Why 404 instead of 403?"
- "How do you make sure a new endpoint isn't accidentally public?"
- "How does a background job know which user it's acting for?"
