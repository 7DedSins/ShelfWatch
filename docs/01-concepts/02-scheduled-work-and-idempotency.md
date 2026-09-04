# 02 — Scheduled work and idempotency

**Status:** contract — expand when taught
**Prereqs:** [01-polling-and-reconciliation.md](01-polling-and-reconciliation.md)
**Used by:** [m03](../03-build/m03-celery-and-polling.md), [m04](../03-build/m04-library-scanning.md)
**Time:** ~75 min

> The distributed-systems core of this project. Everything here is asked about in interviews.

---

## Why this lesson exists

Beat fires `scan_library` every 15 minutes. A scan takes 45 minutes. By the third tick you have
three copies of the same scan writing to the same rows. Nothing warned you; the data is just
quietly wrong.

---

## What you should be able to say afterwards

- Why any scheduled task can and will run twice
- What a distributed lock is, and the two ways it goes wrong
- Why a task must be safe to re-run rather than merely unlikely to
- How to retry without making an outage worse

---

## Concepts to cover

1. **Every reason a task runs twice.** Beat fires again before the last finished. `acks_late`
   redelivers after a worker dies. A network blip makes the broker redeliver. Someone clicks
   "Scan now". **You cannot prevent this — you design for it.**
2. **Idempotency.** Same input, same end state, however many times it runs. `bulk_create` with
   `update_conflicts=True` on a unique key is idempotent; a plain `create` is not. **The
   database constraint is what makes it true**, not your code being careful.
3. **Distributed locks.** `cache.add(key, "1", timeout=N)` — atomic set-if-absent in Redis.
   Claim before starting, release in a `finally`.
   Two failure modes, both real:
   - **No timeout** → a crashed worker holds the lock forever and that library never scans
     again, silently.
   - **Timeout too short** → the lock expires mid-scan and a second scan starts anyway, which
     is the exact thing you were preventing.
   There is no perfect value. **Pick one longer than your worst observed scan, and monitor
   for scans that exceed it.**
4. **Locks are not a correctness guarantee.** They reduce the chance of concurrent runs. Your
   task must *still* be idempotent, because the lock can expire. Belt and braces — and being
   able to say why the lock alone is insufficient is a strong signal.
5. **Retries with backoff and jitter.** `autoretry_for`, `retry_backoff`, `retry_jitter`,
   `max_retries`. Retrying a down service every second makes its recovery harder.
6. **Which failures to retry.** A timeout or `5xx` — yes. A `401` — no, the credentials are
   wrong and will still be wrong in ten seconds. Classify deliberately.
7. **Chunking long work.** A 45-minute task holding one transaction is a problem. Commit in
   chunks so partial progress survives, and design so a resumed scan does not double-count.
8. **Beat's own reliability.** Beat is a single process. If it dies, nothing schedules. It is a
   single point of failure — know it, monitor it, and do not be surprised by it.
9. **Fan-out scheduling.** Beat runs a cheap `schedule_scans()` every 15 minutes that finds
   *due* libraries and dispatches them, rather than Beat holding a per-library schedule. One
   scheduler entry, arbitrary libraries, and due-ness is data rather than configuration.

---

## Exercise

1. **Cause the overlap.** Make a task sleep 60s, schedule it every 20s. Watch three run at
   once. Look at the resulting rows.
2. Add a Redis lock. Confirm one runs and the others exit cleanly.
3. **Break the lock two ways:** remove the timeout and kill the worker mid-task — confirm it
   never runs again. Then set the timeout shorter than the task and confirm overlap returns.
4. Make the task idempotent with a unique constraint and upserts. **Now remove the lock
   entirely and confirm the data is still correct.** That is the point: the lock is an
   optimisation, the constraint is the guarantee.
5. Add retries with backoff and jitter. Make a connector fail. Watch the intervals grow.
6. Make it fail with `401`. Confirm no retry.
7. Kill Beat. Confirm nothing schedules and work out how you would have noticed.

---

## Done when

- [ ] You caused overlapping tasks and saw the damage
- [ ] The lock works, and you have broken it in both directions
- [ ] **The task is correct without the lock**, proven
- [ ] Retries back off with jitter; non-retryable errors do not retry
- [ ] Beat's single-point-of-failure status is understood and monitored

---

## Interview questions this unlocks

- "How do you stop a scheduled task from running twice?"
- "What's a distributed lock? How does it fail?"
- "Is a lock enough to guarantee correctness?" — no, and this is the good answer.
- "How do you make a task idempotent?"
- "What happens if your worker dies mid-task?"
- "Which errors would you retry?"
