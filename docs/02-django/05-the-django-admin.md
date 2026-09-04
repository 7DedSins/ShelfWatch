# 05 — The Django admin

**Status:** contract — expand when taught
**Prereqs:** [03-models-and-migrations.md](03-models-and-migrations.md)
**Used by:** [m01](../03-build/m01-services-and-health.md)
**Time:** ~50 min

> **The most underrated demo in a Django portfolio.** Almost everyone ships the default and it
> shows. A properly customised admin takes an afternoon and looks like a product.

---

## Why this lesson exists

You get a working CRUD interface for free, which means you have a usable internal tool before
you write a single template. It is also the fastest way to make ShelfWatch genuinely useful to
yourself — and a tool you actually use gets finished.

---

## What you should be able to say afterwards

- What the admin is for and, importantly, what it is not for
- How to customise it enough to be genuinely useful
- Why the default admin is a performance problem at scale
- How to stop it leaking secrets

---

## Concepts to cover

1. **What it is for.** An internal staff tool over your models. **Not** a customer-facing UI,
   not an API, not a substitute for your dashboard. Knowing where the line is matters — people
   ship admins to end users and regret it.
2. **`list_display`, and computed columns.** Methods on the `ModelAdmin` become columns.
   `@admin.display(boolean=True)` renders a green tick or red cross — a status column that is
   instantly readable.
3. **`list_filter`, `search_fields`, `date_hierarchy`.** Three lines that turn a table into
   something navigable. `list_filter` on a high-cardinality field is a trap; know why.
4. **`readonly_fields`.** Anything written by a task — `last_scanned_at`, health results —
   must not be hand-editable. Read-only, or you will "fix" a value and confuse yourself later.
5. **⚠️ Secrets.** An encrypted `api_key` displayed in `list_display` or the change form has
   just been **decrypted onto a web page**. Exclude it, or show a masked prefix only. Check
   this deliberately — see [concepts/03](../01-concepts/03-secrets-at-rest.md).
6. **Admin actions.** "Poll now", "Scan now", "Acknowledge selected". A dropdown over selected
   rows. **This is what makes the admin genuinely useful** rather than merely present.
7. **Performance.** The default changelist does one query per row per related field. Override
   `get_queryset()` with `select_related`. **A 200-row changelist doing 600 queries is normal
   and nobody notices** — measure it with debug-toolbar, then fix it.
8. **Inlines.** `Library` inline on `Service`. Convenient, and a performance trap on large
   sets — cap or paginate.
9. **`raw_id_fields` / `autocomplete_fields`.** A `ForeignKey` to a table with 100,000 rows
   renders a `<select>` with 100,000 options. Genuinely breaks the page. Know the fix.

---

## Exercise

1. Register every model with the default admin. Note how much works for free.
2. Customise `ServiceAdmin`: `list_display` with a coloured status column, `list_filter` by
   kind and enabled, `search_fields` on name.
3. **Check whether the API key is visible anywhere.** Fix it. Verify by viewing the page.
4. Make task-written fields read-only.
5. Add the three admin actions. Confirm "Poll now" actually dispatches the Celery task.
6. Load 500 services with health checks. **Measure the changelist query count.** Fix it with
   `select_related`. Measure again. Record both.
7. Add a `ForeignKey` to `DiskItem` (100,000 rows) somewhere and load the change form. Watch
   the page struggle. Fix with `autocomplete_fields`.
8. `date_hierarchy` on `HealthCheck`. Navigate by day.

---

## Done when

- [ ] The admin is genuinely usable, not the default
- [ ] Secrets are not visible anywhere in it
- [ ] Task-written fields are read-only
- [ ] Three working admin actions
- [ ] Changelist query counts measured and fixed
- [ ] No unbounded `<select>` anywhere

---

## Interview questions this unlocks

- "What's the Django admin for? What isn't it for?"
- "How would you customise it?"
- "Why is the default admin slow on large tables?"
- "How do you stop the admin leaking sensitive fields?"
