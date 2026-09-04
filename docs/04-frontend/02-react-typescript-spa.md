# 02 — The React + TypeScript SPA

**Status:** contract — expand when taught
**Prereqs:** [01-django-templates-and-htmx.md](01-django-templates-and-htmx.md) ·
**[Ferryman's frontend track](../../../Ferryman/docs/09-frontend/README.md)** (lessons 01–05 at minimum)
**Time:** 2–3 weeks

> **This lesson does not teach React.** If you have not done Ferryman's track, stop and do it —
> it teaches TypeScript, React, Vite, and TanStack Query properly against a simpler UI. Coming
> back here, this is application rather than learning, and it goes fast.

---

## Why this lesson exists

The same four screens, as a typed SPA. The goal is not to prove React is better — it is to
build the identical thing so the comparison in lesson 04 is honest, and to find out where the
API you designed in m06 turns out to be inadequate.

---

## What you should be able to say afterwards

- What the SPA genuinely does better, with evidence
- What it costs, with evidence
- Which screens justify it and which do not
- How much of the "React is complicated" reputation is the ecosystem rather than React

---

## Concepts to cover

1. **Repo layout.** `frontend/` inside the ShelfWatch repo. One PR can change a serializer and
   its consumer together — which matters because of the generated types.
2. **The stack.** Vite, React Router, TanStack Query, Tailwind, React Hook Form + Zod. Same as
   Ferryman; deliberately, so it is muscle memory rather than a new decision.
3. **Dev proxy** to Django, so no CORS in development. Understand what you are deferring to
   production.
4. **Generated types from `drf-spectacular`.** Point `openapi-typescript` at `/api/schema/`.
   **This is where m06's schema quality gets audited** — every place the generated type is
   wrong or `unknown` is a serializer you under-annotated. Fix the backend, not the frontend.
5. **Query keys for these resources.** A `queryKeys` factory. Services, libraries,
   discrepancies with filters, health history.
6. **The four screens.**
   - Overview: parallel queries, one loading state, the chart from JSON
   - Library detail: paginated table, nested routing
   - Discrepancies: URL-driven filters, optimistic bulk-acknowledge with rollback
   - Settings: forms with Zod, and test-connection as a mutation with a pending state
7. **The chart.** Recharts or Chart.js via a React wrapper. Compare the effort against lesson
   01's server-rendered version — **be honest**, including the bundle cost.
8. **Auto-refresh.** `refetchInterval` on service cards. Compare with HTMX polling; it is the
   same idea in a different place.
9. **Optimistic updates.** Bulk-acknowledge is the right candidate — immediate feedback, low
   cost if it fails, easy rollback.
10. **Loading and error states.** The SPA must build every state that Django gave you for free.
    **Count them.** This is one of the real costs and it is easy to under-report.

---

## Exercise

1. Scaffold `frontend/`, wire the dev proxy, generate types from the schema.
2. **Log every place the generated type is `unknown` or wrong.** Fix the serializers. Keep the
   list — it is a finding for lesson 04.
3. Build all four screens with identical functionality to lesson 01. **No shortcuts** — if the
   Django version had a spinner, this one has a spinner.
4. Auth: JWT login, refresh interceptor, protected routes. (Storage: Ferryman lesson 07.)
5. Optimistic bulk-acknowledge with rollback. Make the server fail and watch it revert.
6. **Measure everything in the [README's table](README.md#what-to-measure).**
7. **Add the same one field you added in lesson 01.** Count the files. Compare directly.
8. Throttle the network to slow 3G. Load both versions. **Record both.** This is the number
   people argue about without evidence.
9. Count your dependencies (`npm ls --depth=0`, and then the full tree). Compare with the
   Django version's.

---

## Done when

- [ ] All four screens match lesson 01's functionality exactly
- [ ] Types generated from the schema; serializer gaps fixed and **logged**
- [ ] Auth with refresh works
- [ ] One optimistic update with tested rollback
- [ ] Every metric recorded
- [ ] The "add one field" file count recorded and compared
- [ ] Slow-3G numbers for both versions
- [ ] Committed: `feat(frontend): React + TypeScript SPA against the DRF API`

---

## Interview questions this unlocks

- "How do you keep frontend and backend types in sync?"
- "What did building the same UI twice teach you?"
- "How do you handle loading and error states?"
- "When is an optimistic update appropriate?"

---

**Next:** [03-consuming-drf-from-react.md](03-consuming-drf-from-react.md)
