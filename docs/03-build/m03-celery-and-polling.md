# Milestone 03 — Celery and polling

**Goal:** every enabled service is polled on its own interval by a scheduled task, health is
recorded, and slow work can never block fast work.

**Detours first:** **[django/07 Celery and Beat](../02-django/07-celery-and-beat.md)** ·
[concepts/02 Scheduled work and idempotency](../01-concepts/02-scheduled-work-and-idempotency.md)

**Sessions:** 3–4

> **The distributed-systems milestone.** Everything here is asked about in interviews, and most
> candidates who list Celery on a CV cannot explain any of it.

---

## Design decisions to make and write down

1. **Two queues.** `default` and `scans`, with separate worker containers.
   **Experience the starvation before you fix it** — the fix means nothing otherwise.
   Note the cost: an extra container against your m00 RAM budget. Is it worth it? (Yes, and you
   should be able to say why in one sentence.)
2. **Fan-out scheduling.** Beat runs `schedule_polls()` every 60s, which queries for *due*
   services and dispatches. One Beat entry regardless of how many services exist. **Due-ness is
   data, not configuration** — that is the design idea worth naming.
3. **Per-service intervals.** `poll_interval_seconds` on the model. What is a sensible default,
   and what is the minimum you allow? Someone will set it to 1.
4. **Locking.** Per-service lock so a slow poll is not double-launched. Timeout longer than
   your worst poll. **Released in `finally`.**
5. **Retry policy.** Retry on timeout and `5xx` with backoff and jitter. **Do not retry
   `ServiceAuthFailed`** — the credentials will not fix themselves.
6. **Flapping.** N consecutive failures before declaring a service down. Pick N, and pick the
   recovery threshold separately (they need not match).
7. **Results backend.** Do you need one? Health results go to the database, so probably not —
   one less thing to run. Decide deliberately.

---

## Build

- `config/celery.py`; Celery wired into Django settings.
- Compose: `worker-default`, `worker-scans`, `beat` as separate containers.
- `worker_prefetch_multiplier=1` and `task_acks_late=True` on the scans queue.
- `poll_service(service_id)` — thin task calling a `services.py` function.
- `schedule_polls()` — Beat entry, fans out to due services.
- Redis locking per service.
- Retries with backoff and jitter; non-retryable errors excepted.
- Denormalised `Service.last_health_ok` updated by the poll (from m01's decision).
- Task tests with `ALWAYS_EAGER`.

---

## Break it

**Do all of these. This is the richest "Break it" in the project.**

1. **Cause starvation.** One queue, one worker. A 5-minute task and a 1-second task. Watch the
   fast one wait. **Screenshot the timeline.** Then split the queues and confirm it clears.
2. Leave `prefetch_multiplier` at the default. Queue five long tasks across two workers. Watch
   tasks sit unstarted while a worker idles. Set it to 1. Compare.
3. Kill a worker mid-task **without** `acks_late`. Confirm the task is lost silently. Enable it,
   repeat, confirm redelivery. **Then confirm redelivery causes no damage**, because the task is
   idempotent. That two-step is the lesson.
4. Make a poll take longer than its interval. Watch overlapping executions. Add the lock.
   Confirm one runs.
5. **Break the lock two ways:** no timeout plus a killed worker → that service never polls
   again, silently. Then a timeout shorter than the poll → overlap returns.
6. Remove the lock entirely and confirm the data is **still correct** because of idempotency.
   *The lock is an optimisation; the idempotency is the guarantee.*
7. Point a service at a dead host. Confirm backoff intervals grow and jitter is present.
8. Use a wrong API key. Confirm zero retries.
9. Kill Beat. Confirm nothing schedules. **Work out how you would have noticed** — then build
   that detection.
10. Set a service's interval to 1 second. Watch what it does to the queue. Add a minimum.

---

## Done when

- [ ] Starvation caused, screenshotted, and fixed with two queues
- [ ] `prefetch_multiplier=1` justified by an observed difference
- [ ] `acks_late` on; redelivery proven safe
- [ ] Locking works; broken deliberately in both directions
- [ ] **Correct without the lock**, proven
- [ ] Backoff with jitter; auth failures do not retry
- [ ] Beat failure is detectable
- [ ] Health history accumulating for real services
- [ ] Committed: `feat(m03): two-queue Celery polling with locking and backoff`

---

## Interview connection

**The densest milestone for interview material in this project.**

- *"Why two Celery queues?"* — with a screenshot of the starvation.
- *"What does `task_acks_late` do, and what does it require of your task?"*
- *"What's `worker_prefetch_multiplier`?"*
- *"How do you stop a scheduled task double-firing?"*
- *"Is a distributed lock enough?"* — no, and this is the answer that shows depth.
- *"What happens when your scheduler dies?"*
- *"Tell me about a bug in your own design."* — the lock without a timeout is a good one.

---

**Next:** [m04 — Library scanning](m04-library-scanning.md)
