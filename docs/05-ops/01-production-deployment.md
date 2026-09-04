# 01 — Production deployment

**Status:** contract — expand when taught
**Prereqs:** [04-frontend/04](../04-frontend/04-comparing-the-two.md)
**Time:** 2 sessions

> **The most important session in this project.** "Deployed and running against my real
> infrastructure for N months" is a true statement you can put on a CV, and almost nobody else
> can.

---

## Why this lesson exists

ShelfWatch is only credible if it runs against real services. It also has to share a 6 GB box
with six media containers that were there first, which makes every resource decision real.

---

## What you should be able to say afterwards

- Where every megabyte on the box goes
- Why library mounts are read-only, and what that guarantees
- How to deploy without dropping requests or corrupting a running scan
- What your rollback procedure is, having used it

---

## Concepts to cover

1. **⚠️ The RAM budget, for real.** Already running: Kavita, Komga, LANraragi, Stash, two nginx
   proxies, and an rclone mount. Adding: web, worker-default, worker-scans, beat, Postgres,
   Redis. **That is six new containers.** Do the arithmetic before you deploy, not after the
   OOM killer picks a victim. If it does not fit, the honest options are fewer workers, or
   Postgres tuned right down, or accepting slower scans.
2. **`docker-compose.prod.yml`.** `web` (gunicorn + WhiteNoise), `worker-default`,
   `worker-scans`, `beat`, `postgres`, `redis`, `caddy`. `mem_limit` on each, matching the
   budget.
3. **⚠️ Read-only mounts.** Library paths mounted `:ro` into the scan workers.
   **This is both correct and the single best thing a reviewer can spot** — it makes
   "read-only by design" a structural guarantee rather than a promise in a README. It also
   means a bug in your scan code cannot touch your media.
4. **Do not touch the rclone mount.** ShelfWatch reads through it. It never restarts it, never
   remounts it, never restarts the media containers. If a scan detects a stale mount, it
   **reports** it. Remediation is a human decision — see your Contabo guardrails.
5. **Entrypoint.** `migrate`, then `collectstatic`, then exec the command. **Migrations in an
   init container**, not in the entrypoint of every replica, or they race.
6. **Caddy.** Automatic TLS. Serving the React build as static files on the same origin as the
   API, so no CORS. Tailscale-only or public? **Tailscale-only for your real instance** — the
   public demo is a separate deployment (lesson 02).
7. **Zero-downtime, with a wrinkle.** Web is easy — health-checked rolling restart. **Workers
   need care:** a `SIGTERM` mid-scan must not corrupt state. `acks_late` means the task
   redelivers, and idempotency means that is safe — **your m03/m04 work is what makes this
   deploy safe**, and being able to trace that chain is a good interview answer.
8. **`stop_grace_period`** longer than a scan chunk, so workers finish cleanly.
9. **Secrets.** `django-environ` reading a `.env` on the host with tight permissions. Not in
   git, not in the image. A documented rotation procedure — including the field-encryption key,
   which has the re-encryption consequence from [concepts/03](../01-concepts/03-secrets-at-rest.md).
10. **Backups.** Nightly `pg_dump`, encrypted, off-site. **A restore drill you have actually
    run.** Your RPO and RTO, written down.

---

## Exercise

1. Write the RAM budget. Deploy. **Measure actual usage.** Compare. Adjust the budget, not the
   measurement.
2. Deploy with library mounts `:ro`. **Try to write to one from inside the scan worker** and
   confirm it fails.
3. Point it at your real Kavita, Komga, and LANraragi. Let it run a full cycle.
   **Look at what it finds.**
4. Caddy with TLS. Verify the cert. Confirm the React build serves from the same origin.
5. Deploy a change with a rolling restart **while a scan is running**. Confirm the scan
   completes or is safely redelivered, and no data is corrupted.
6. **Practise a rollback.** Deploy something broken, revert, time it.
7. Reboot the VPS. Confirm everything comes back without intervention.
8. Nightly backups, encrypted, off-site. **Then do a full restore into a scratch container and
   verify the data.** Time it — that time is your real RTO.
9. Constrain a worker's `mem_limit` too low deliberately. Confirm that container dies alone and
   the media stack is untouched.

Exercise 9 matters: the failure you must never have is ShelfWatch taking down Kavita.

---

## Done when

- [ ] RAM budget written and matched against measurement
- [ ] Library mounts `:ro`, proven unwritable
- [ ] Running against real services, having found real discrepancies
- [ ] TLS valid; SPA and API same origin
- [ ] Rolling deploy safe during an active scan
- [ ] **You have performed a rollback**
- [ ] Survives a reboot
- [ ] **You have restored from a backup and verified it**
- [ ] A resource-starved ShelfWatch container cannot affect the media stack
- [ ] Committed: `chore(ops): production deployment on Contabo`

---

## Interview questions this unlocks

- "How do you deploy this?"
- "How do you deploy without interrupting running jobs?" — the `acks_late` + idempotency chain.
- "How do you stop one service affecting others on the same host?"
- "How do you roll back?"
- "Have you ever restored from a backup?"
- "How do you guarantee a monitoring tool can't damage what it monitors?" — `:ro` mounts.

---

**Next:** [02-monitoring-and-the-demo.md](02-monitoring-and-the-demo.md)
