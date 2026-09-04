# Question bank

**How to use:** after each milestone, answer that milestone's questions **out loud, without
notes.** Under two minutes each, or you do not know it yet.

---

## Section A — Django and data

*Available after m01.*

1. When would you use Django over Flask or FastAPI?
2. How do you structure a large Django project? Where does business logic go?
3. How do you manage settings across environments? Why not `if DEBUG`?
4. How do you enforce an architectural boundary between apps?
5. Why are querysets lazy? When does that bite you?
6. **Where should a uniqueness rule live — model `clean()` or a database constraint?**
   *(And what does `bulk_create` do to `clean()`?)*
7. How would you add a `NOT NULL` column to a 50-million-row table?
8. What does Django's migration autogenerate miss?
9. How do you write a reversible data migration?
10. When would you use a `JSONField`? When is it laziness?
11. How do you store an API key you need to replay? Why not hash it?
12. What does encryption at rest actually protect against — and what doesn't it?
13. What's the Django admin for, and what isn't it for?
14. Why is the default admin slow on large tables?

---

## Section B — Async work and the ORM

*Available after m05. The strongest section.*

**Celery**
1. **Why two Celery queues?** What breaks with one?
2. What does `task_acks_late` do? What does it require of your task?
3. What's `worker_prefetch_multiplier` and why change it for long tasks?
4. **What's the difference between `.s` and `.si` in a chain?**
5. How do you stop a scheduled task double-firing?
6. **Is a distributed lock enough to guarantee correctness?** *(No — and this is the answer that shows depth.)*
7. How does a lock fail? *(Both directions.)*
8. Which errors do you retry? Which don't you?
9. What happens when Beat dies? How would you know?
10. How do you test Celery tasks? What does `ALWAYS_EAGER` miss?
11. What happens if a task hangs?

**The ORM**
12. **What's an N+1 query? How did you find yours?** *(With numbers.)*
13. `select_related` or `prefetch_related` — when each?
14. How do you get the latest related row per parent?
15. When would you denormalise? What does it cost?
16. How do you insert 10,000 rows efficiently?
17. How do you detect deletions without storing a diff? *(`seen_at`.)*
18. Why not wrap a long job in one transaction?
19. How do you stop a performance regression coming back?

**Design**
20. How would you detect changes in a system with no webhooks?
21. What's the difference between event-driven and reconciliation-based design?
22. **Your API call times out. How do you make sure that doesn't look like deleted data?**
23. How would you support a new service type? *(One file, one line — then show it.)*
24. Where does retry logic belong — the client or the caller?
25. How do you avoid alert fatigue?

---

## Section C — API, frontend, and operations

*Available after the frontend and ops phases.*

**API**
1. **Do object-level permissions protect a list endpoint?**
2. Why return 404 instead of 403 for another user's object?
3. When would you use cursor pagination? What can't you build with it?
4. How do you stop a field being returned in a response?
5. How do you keep an API and its client in sync?
6. **How did building a real client change your API design?**
7. REST or GraphQL? *(With a specific reason from your own experience.)*
8. How do you evolve an API with a live consumer?

**Frontend**
9. **Server-rendered or SPA — how do you choose?** *(You have numbers.)*
10. What's the difference between server state and client state?
11. What's wrong with fetching in `useEffect`?
12. Where do you store a JWT in a browser?
13. How many loading states does a SPA need that a server-rendered page doesn't?

**Operations**
14. How much memory does your system use? Where does it go?
15. **How do you monitor a monitoring system?**
16. How would you detect that your scheduler silently stopped?
17. How do you deploy without interrupting running jobs?
18. How do you stop one service affecting others on the same host?
19. How do you guarantee a monitoring tool can't damage what it monitors? *(`:ro` mounts.)*
20. Have you ever restored from a backup?

**Judgment**
21. What would you do differently if you started over?
22. What are the limitations of your design?
23. **Tell me about a performance problem you solved.**
24. Tell me about a bug in your own design.
25. What did you deliberately not build, and why?
26. If this had 100× the services, what breaks first?

---

## The system-design drill

Run at each checkpoint. Same prompt, keep every attempt.

> **"Design a system that monitors several third-party services, reconciles their reported
> state against ground truth, and alerts on discrepancies."**

**Structure (45 min):** clarify (how many services, poll frequency, data volume, who uses it) →
requirements → data model → the polling architecture → **failure modes** → scale.

**The failure-modes section decides the interview.** Volunteer these:
- A service times out → **must not look like deleted data**
- A scan overruns its schedule → locking plus idempotency
- A worker dies mid-scan → `acks_late`, redelivery, idempotent upserts
- Beat dies → nothing schedules, everything looks fine, staleness metric catches it
- A large-scale failure → alert batching and a global rate cap
- One slow service → separate queues so it cannot starve the others

**Attempt log:**

### Attempt 1 — after m05
Date: · Missed: · Weakest section: · To fix:

### Attempt 2 — after ops
Date: · Missed: · Improvement:

---

## The four stories worth rehearsing

**1. The failure that looked like deletion.** A connector timeout returning `[]` instead of
raising would have marked every series in every library as deleted — and with alerts on, told
me so at 3am. Fixed with a typed exception hierarchy and a reconciliation step that skips
entirely when the fetch failed. **The general lesson: absence and failure are different states
and conflating them is how monitoring systems lie.**

**2. The scan that starved the polls.** One Celery queue, a six-hour filesystem walk, and
health checks queued behind it. Split into two queues with separate workers, set
`prefetch_multiplier=1` and `acks_late=True` on the slow one — which then forced every scan
task to be genuinely idempotent, because `acks_late` means redelivery.

**3. The N+1 nobody would have noticed.** The dashboard did 1,200 queries and rendered in
under a second on ten rows of test data. On real data it took nine. Found it with
debug-toolbar, fixed it with a `Prefetch` and one denormalised column, and added
`assertNumQueries` so it cannot come back.

**4. The dashboard I built twice.** Same four screens, Django+HTMX and React+TS, against the
same API. *(See [04-frontend/04](../04-frontend/04-comparing-the-two.md) for the numbers.)*
The surprise was not which won — it was how many holes a real client exposed in an API I
thought was finished.

Story 4 is your differentiator. Almost nobody has done it.
