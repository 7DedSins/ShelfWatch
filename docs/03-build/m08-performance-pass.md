# Milestone 08 — Performance pass

**Goal:** find every N+1 and slow query, fix them, and **record the numbers** — because the
numbers are the portfolio artifact, not the fixes.

**Detours first:** [django/04 The ORM](../02-django/04-orm-and-query-optimization.md) ·
[django/08 Testing Django](../02-django/08-testing-django.md)

**Sessions:** 2–3

> **"Tell me about a performance problem you solved" is asked in almost every interview.**
> Most candidates answer with vocabulary. You are going to answer with a screenshot.

---

## Design decisions to make and write down

1. **Measure before optimising.** Every change in this milestone must have a before and an
   after. **An optimisation you cannot quantify is a guess** — and possibly a pessimisation.
2. **What "slow" means here.** Set targets: dashboard under 300ms, API list endpoints under
   200ms, admin changelists under 500ms. Numbers, so "done" is a fact rather than a feeling.
3. **Where to denormalise.** `Service.last_health_ok` was one call. Are there others? The rule:
   denormalise when reads massively outnumber writes and the join is expensive. **Every
   denormalisation is a consistency risk** — name the risk and who updates the field.
4. **Indexes are not free.** Each one costs write performance, and your scans write in bulk.
   Add from evidence, not from intuition.
5. **Caching — and whether you need it.** Redis caching for the dashboard? **Probably not**, if
   the queries are fast. Caching a slow query is hiding it. Fix the query first; consider cache
   after. Be able to say that.

---

## Build

- `django-debug-toolbar` in local settings.
- A query-count regression test: `assertNumQueries` on the dashboard and key API endpoints,
  so an N+1 reintroduced later **fails CI**. This is the part that makes the fix permanent.
- Fixes for everything found.
- Indexes justified by `EXPLAIN ANALYZE`.
- A seeding management command: realistic volumes (50 services, 200 libraries, 200,000
  DiskItems, 500,000 HealthChecks) so measurements mean something.

---

## Break it

1. **Seed realistic data first.** Ten rows hides every problem you are looking for.
2. Load the dashboard. **Screenshot the debug-toolbar query count.** It will be shocking.
3. Fix with `select_related` / `prefetch_related` / denormalisation. **Screenshot again.**
   **Both screenshots go in the README** — this is the single most persuasive artifact in the
   project.
4. Do the same for every API list endpoint, the admin changelists, and the discrepancy feed.
5. Find your slowest query. `EXPLAIN ANALYZE`. Add an index. Compare **plans**, not just times
   — you want to see the sequential scan become an index scan.
6. **Measure the write cost** of your new indexes: time a bulk scan before and after. If a
   read optimisation halved your scan speed, that is a trade you should make knowingly.
7. Add `assertNumQueries` tests. **Reintroduce an N+1 deliberately and confirm CI goes red.**
8. Load the storage chart with a year of snapshots. Fix whatever that reveals.
9. Run everything with the whole stack under load — a scan running, polls firing — and measure
   again. **Numbers on an idle system are not numbers.**

---

## Done when

- [ ] Realistic seed data exists as a command
- [ ] Before/after query counts recorded for **every** major view
- [ ] Both screenshots in the README
- [ ] At least one index justified by a query plan
- [ ] The write cost of new indexes is measured
- [ ] `assertNumQueries` regression tests, proven to catch a reintroduced N+1
- [ ] All targets met **under load**, not idle
- [ ] Every number in [PROGRESS.md](../PROGRESS.md)'s table filled in
- [ ] Committed: `perf(m08): eliminate N+1s and add query-count regression tests`

---

## Interview connection

**The most reusable material in the project.**

- *"**Tell me about a performance problem you solved.**"* — with two screenshots.
- *"What's an N+1 and how did you find yours?"*
- *"How do you stop a performance regression coming back?"* — `assertNumQueries` in CI is a
  better answer than most people give.
- *"When would you denormalise? What does it cost?"*
- *"When would you add a cache?"* — after fixing the query, not instead of.
- *"How do you know your optimisation worked?"*

---

**Backend complete.** Now the dashboard: [04-frontend/README.md](../04-frontend/README.md).
