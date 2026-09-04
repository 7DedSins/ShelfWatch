# 07 — Celery and Beat

**Status:** contract — expand when taught
**Prereqs:** [concepts/02 Scheduled work and idempotency](../01-concepts/02-scheduled-work-and-idempotency.md)
**Used by:** [m03](../03-build/m03-celery-and-polling.md), [m04](../03-build/m04-library-scanning.md)
**Time:** 2 sessions

> **The most interview-dense lesson in this project.** Two queues, `.s` vs `.si`,
> `acks_late`, prefetch, and locking are all things candidates claim on a CV and cannot explain.

---

## Why this lesson exists

ShelfWatch has two completely different kinds of work: health polls that take 200ms and must
run every minute, and filesystem walks that take six hours. Running them on the same worker
means the polls stop for six hours. The architecture that fixes it is the lesson.

---

## What you should be able to say afterwards

- Why two queues, and what breaks with one
- What `acks_late` and `prefetch_multiplier` actually do
- The difference between `.s` and `.si`, and when it bites
- Where Celery's reliability guarantees end

---

## Concepts to cover

1. **The pieces.** Your Django code → broker (Redis) → worker process. Beat is a separate
   process that publishes on a schedule. **Four containers total** — budget the RAM.
2. **⚠️ The two-queue design — the central decision.** `default` for fast work, `scans` for
   slow. **Separate worker containers**, each consuming one queue. With a single queue, one
   six-hour scan occupies a worker slot and health polls queue behind it. Have them
   *experience* this before fixing it.
3. **`worker_prefetch_multiplier=1`** on the scans worker. By default a worker grabs a batch of
   tasks and holds them while running the first. With hour-long tasks that means several
   libraries sit unstarted for hours while another worker idles. **A genuinely non-obvious
   setting with a dramatic effect.**
4. **`task_acks_late=True`.** Acknowledge after completion, so a worker that dies mid-scan
   causes redelivery rather than silent loss. **This is precisely why the task must be
   idempotent** — the two settings are a pair, and knowing that is the sign you understand
   both.
5. **`.s` vs `.si` — the classic bug.** In `chain(scan_library.s(id), reconcile_library.si(id))`,
   `.s` would pass `scan_library`'s return value as an extra positional argument to
   `reconcile_library`, causing a signature error or, worse, a silently wrong argument. `.si`
   (immutable) does not. **Make them hit it**, then fix it.
6. **Fan-out scheduling.** Beat runs cheap `schedule_polls()` / `schedule_scans()` tasks that
   query for *due* work and dispatch it. One Beat entry, any number of services. Due-ness is
   data, not configuration.
7. **Locking.** A Redis lock per library so a slow scan is not double-launched by the next tick.
   Release in `finally`. Timeout longer than the worst scan. Covered in
   [concepts/02](../01-concepts/02-scheduled-work-and-idempotency.md) — here you implement it.
8. **Retries.** `autoretry_for`, `retry_backoff`, `retry_jitter`, `max_retries`. Which
   exceptions retry and which do not.
9. **Results backend.** Do you need one? For fire-and-forget tasks whose output goes to the
   database, **no** — and not configuring one is one less thing to operate. Decide deliberately.
10. **Testing.** `CELERY_TASK_ALWAYS_EAGER=True` in test settings runs tasks synchronously.
    Fast and deterministic — **but it bypasses serialisation**, so it will not catch a task
    argument that is not JSON-serialisable. Know that gap.
11. **Time limits.** `soft_time_limit` raises inside the task so you can clean up;
    `time_limit` kills it. Set both on scans, or a hung FUSE call blocks a worker forever —
    which is a real failure mode on your box.

---

## Exercise

1. Wire Celery into Django. One worker, one queue. Run a task.
2. **Cause the starvation.** A 5-minute task and a 1-second task on one queue. Watch the fast
   one wait. Screenshot the timeline.
3. Split into two queues and two worker containers. Confirm the fast task is unaffected.
4. Set `prefetch_multiplier` to the default and queue five long tasks across two workers.
   Watch tasks sit unstarted. Set it to 1 and compare.
5. Kill a worker mid-task without `acks_late`. Confirm the task is lost. Enable it and confirm
   redelivery. **Then confirm redelivery is harmless** because the task is idempotent.
6. Build the chain with `.s`. Read the error. Switch to `.si`.
7. Add the Redis lock. Break it both ways (no timeout, too-short timeout).
8. Add `soft_time_limit`. Make a task hang and confirm it is interrupted.
9. Kill Beat. Confirm nothing schedules, and design how you would detect that.

---

## Done when

- [ ] You caused and fixed queue starvation, with evidence
- [ ] `prefetch_multiplier=1` justified by an observed difference
- [ ] `acks_late` on, and you have proven redelivery is safe
- [ ] You hit the `.s`/`.si` bug and can explain it
- [ ] Locking works and you have broken it deliberately
- [ ] Time limits stop a hung task
- [ ] Beat failure is detectable

---

## Interview questions this unlocks

- "**Why two Celery queues?**"
- "What does `task_acks_late` do? What does it require of your task?"
- "What's `worker_prefetch_multiplier` and why change it?"
- "**What's the difference between `.s` and `.si`?**"
- "How do you stop a scheduled task double-firing?"
- "How do you test Celery tasks? What does `ALWAYS_EAGER` miss?"
- "What happens when Beat dies?"
