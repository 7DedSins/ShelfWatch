# 02 — Monitoring and the public demo

**Status:** contract — expand when taught
**Prereqs:** [01-production-deployment.md](01-production-deployment.md)
**Time:** 1–2 sessions

---

## Why this lesson exists

Two separate problems that happen to land together. **Who watches the watcher** — ShelfWatch
can fail silently, which is a particularly embarrassing failure for a monitoring tool. And
**how do you demo it** without exposing your actual media library to the internet.

---

## What you should be able to say afterwards

- What to monitor in a system whose whole job is monitoring
- How to detect that Beat has stopped, which is the silent killer here
- How to give reviewers something clickable without exposing private data
- Why a seeded demo is a design problem, not just a fixture

---

## Concepts to cover

1. **The recursive problem.** If Beat dies, nothing schedules, no polls happen, no
   discrepancies appear — and the dashboard shows a **calm, green, entirely stale screen.**
   Silence looks identical to health. This is the most important failure mode in the project
   and it needs external detection.
2. **Staleness as the key metric.** Not "is the service up" but **"when did the last successful
   poll complete?"** A `last_successful_poll_age` metric that grows unboundedly is the signal.
   Alert on the age, not on an error — errors are not being generated, that is the problem.
3. **`/healthz` that means something.** Database, Redis, a Celery ping, **and Beat liveness**
   (Beat writes a heartbeat key; healthz checks its age). Different failures, different
   responses.
4. **External uptime check.** Something outside the box hitting `/healthz` every minute. A free
   tier is fine. **This is the only thing that catches "the whole VPS is gone"** — internal
   monitoring cannot, by definition.
5. **Sentry.** Free tier, about five lines, and it will show you exceptions you never knew
   about. Genuine credibility for very little work.
6. **Monitoring on a full box.** A Prometheus + Grafana stack is heavy on a VPS already running
   nine containers. Options: skip it and rely on structured logs plus external checks;
   a very small Prometheus with short retention; or a hosted free tier. **Choose deliberately
   and be able to justify it** — "I didn't run Grafana because it would have cost 15% of my RAM
   to watch a system doing 50 requests a minute" is a good answer.
7. **⚠️ The demo instance.** **Do not expose your real library.** Deploy a separate instance
   with a stub connector backed by fixture data, seeded to look plausible, behind `demo/demo`
   credentials. Reviewers get something clickable; your media stays private.
8. **The demo is a design problem.** It needs enough discrepancies to be interesting, health
   history so the charts are not empty, and a stalled scan so the distinctive feature is
   visible. **A demo with no data teaches a visitor nothing** and is worse than a screenshot.
9. **Read-only demo.** The demo user can browse and acknowledge, not create or delete. Reset it
   on a schedule so someone else's poking does not leave it broken.

---

## Exercise

1. Add Beat heartbeat writing and `/healthz` checking its age. **Kill Beat and confirm healthz
   goes red** — this is the recursive problem solved.
2. Expose `last_successful_poll_age` per service. Stop a worker and watch it climb.
3. External uptime check on `/healthz`. **Stop the whole stack and confirm you get told.**
4. Add Sentry. Trigger a real exception; confirm it arrives with useful context.
5. Choose your monitoring approach and **measure its resource cost.** Justify it in the README.
6. Build the stub connector and the seeding command. Seed it to be genuinely interesting:
   several services, a couple down, a realistic discrepancy mix, months of health history, and
   one stalled scan.
7. Deploy the demo separately with read-only permissions and a scheduled reset.
8. **Give the demo URL to someone who has never seen the project.** Say nothing. Watch what
   they click and where they get confused. Every hesitation is a UX fix.

---

## Done when

- [ ] Beat death is detectable and detected
- [ ] Staleness is a first-class metric
- [ ] An external check catches total failure
- [ ] Sentry live
- [ ] Monitoring approach chosen, costed, and justified
- [ ] Demo instance live with plausible seeded data
- [ ] **The demo does not touch your real library**
- [ ] Demo is read-only and self-resetting
- [ ] Someone else has used it without help
- [ ] Committed: `chore(ops): monitoring, alerting, and public demo instance`

---

## Interview questions this unlocks

- "**How do you monitor a monitoring system?**" — an excellent question and you have a real
  answer.
- "How would you detect that a scheduler stopped?" — staleness, not errors.
- "What's the difference between liveness and readiness?"
- "How do you demo a product built on private data?"
- "How do you avoid alert fatigue?"

---

**Project complete.** Go to
[06-interview/question-bank.md](../06-interview/question-bank.md) and start drilling.
