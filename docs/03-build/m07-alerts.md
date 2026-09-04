# Milestone 07 — Alerts

**Goal:** when something breaks, you find out — without being told the same thing forty times.

**Detours first:** none new. Reuse [concepts/02](../01-concepts/02-scheduled-work-and-idempotency.md).

**Sessions:** 2

> The hard part is not sending a webhook. It is **not sending forty of them.**

---

## Design decisions to make and write down

1. **What is alert-worthy.** A service down, a new discrepancy, a stalled scan. **Not** every
   discrepancy — a full library scan can produce hundreds at once and forty notifications is
   the same as none, because you turn them off.
2. **Deduplication.** The same discrepancy recurring must not re-alert. Key on
   `(library, kind, subject)` with a cooldown window. **Same idempotency discipline as
   everywhere else in this project** — notice the pattern recurring.
3. **Batching.** A scan generating 200 discrepancies sends **one** notification saying "200 new
   discrepancies in Manhwa" with a link, not 200 messages. Design the batch window.
4. **Flapping.** From [concepts/01](../01-concepts/01-polling-and-reconciliation.md): N
   consecutive failures before "down", M consecutive successes before "recovered". Without
   this, a service on a flaky network alerts all night.
5. **⚠️ The self-inflicted 3am problem.** Your own bug — a connector regression that makes
   every fetch fail — would alert you for every service, every interval, all night. **A global
   rate cap on notifications is not optional.** Decide the number.
6. **Delivery failures.** The webhook endpoint (Discord, ntfy, Gotify) can be down. Retry with
   backoff, then give up and record it. **An alert about failing alerts is a loop** — do not
   build one.
7. **Channels.** Start with one generic webhook. `AlertRule` and `channels/` structured so
   adding email later is one file — the same shape as connectors, deliberately.

---

## Build

- `apps/alerts/models.py` — `AlertRule`, `Notification` (with delivery status and attempts).
- `channels/base.py` plus `webhook.py`.
- `dispatch_alerts(discrepancy_ids)` on the `default` queue.
- Dedup keyed on the discrepancy identity with a cooldown.
- Batching within a window.
- Flapping thresholds for service up/down.
- A global notification rate cap.
- Retry with backoff on delivery; give up and record.
- A "test alert" button in the admin and the API.

---

## Break it

1. Trigger 200 discrepancies at once. Confirm **one** notification, not 200.
2. Recreate the same discrepancy repeatedly. Confirm the cooldown holds.
3. Flap a service up and down five times quickly. Confirm the thresholds suppress it.
4. **Simulate your own bug**: make every connector fail simultaneously. Confirm the global rate
   cap stops the flood. **Without the cap first**, so you see what you are preventing.
5. Point the webhook at a dead URL. Confirm retries with backoff, then a clean give-up recorded
   in `Notification`.
6. Point it at a URL returning `429`. Confirm you honour `Retry-After` rather than your own
   schedule.
7. Confirm a delivery failure does **not** generate an alert about the failure. Check for the
   loop deliberately.
8. Send a test alert to a real Discord webhook. Read it on your phone. **Is it actually
   useful?** Does it say what broke, where, and what to do? Rewrite the message until it is.

Exercise 8 is the one people skip. An alert that does not tell you what to do is noise with
extra steps.

---

## Done when

- [ ] Bulk discrepancies produce one batched notification
- [ ] Dedup and cooldown work
- [ ] Flapping suppressed
- [ ] A global rate cap exists and you have seen why
- [ ] Delivery retries, backs off, and gives up cleanly
- [ ] No alert-about-alerts loop
- [ ] A real notification arrives on your phone and is genuinely useful
- [ ] Committed: `feat(m07): batched, deduplicated alerting with rate limits`

---

## Interview connection

- *"How do you avoid alert fatigue?"*
- *"How do you stop a monitoring system from spamming during a large-scale failure?"*
- *"What happens when your notification channel is down?"*
- *"How do you decide what's worth alerting on?"* — symptoms, batched, actionable.

---

**Next:** [m08 — Performance pass](m08-performance-pass.md)
