# 01 — What we are building

**Time:** 10 minutes.

---

## The problem, concretely

You run Kavita, Komga, LANraragi, and a FUSE mount over PikPak. One morning you notice a series
you definitely added last week is not showing up in Kavita. Was the scan never triggered? Did
it fail? Is the mount stale? Did the folder name break the parser?

There is no single place to look. Kavita's UI shows what Kavita knows about — which is exactly
the information that is wrong. To find out what is actually on disk you `ssh` in and start
running `ls`.

Now scale that: 178 series folders, four services, a mount that occasionally hangs, and scans
that sometimes report "in progress" for fourteen hours because a FUSE call is blocked in
kernel state `D`. **You would not notice any of it until you went looking.**

---

## What ShelfWatch does

```
  ┌──────────┐   ┌──────────┐   ┌──────────┐        ┌───────────────────┐
  │  Kavita  │   │  Komga   │   │LANraragi │        │   the filesystem  │
  │   API    │   │   API    │   │   API    │        │  /pikpak_mount/*  │
  └────┬─────┘   └────┬─────┘   └────┬─────┘        └─────────┬─────────┘
       │              │              │                        │
       └──────────────┴──────────────┘                        │
                      │ connectors                            │ scan task
                      v                                       v
            ┌───────────────────┐                  ┌────────────────────┐
            │  ServiceInventory │                  │     DiskItem       │
            │  (what it thinks) │                  │  (what's there)    │
            └─────────┬─────────┘                  └──────────┬─────────┘
                      │                                       │
                      └──────────────┬────────────────────────┘
                                     v
                        ┌─────────────────────────┐
                        │      RECONCILE          │
                        └────────────┬────────────┘
                                     v
                        ┌─────────────────────────┐
                        │      Discrepancies      │
                        ├─────────────────────────┤
                        │ MISSING_IN_SERVICE  ×12 │  on disk, reader doesn't know
                        │ MISSING_ON_DISK     × 3 │  reader has it, files gone
                        │ COUNT_MISMATCH      × 7 │  40 chapters vs 38 files
                        │ STALLED_SCAN        × 1 │  "scanning" for 14 hours
                        │ NO_COVER            ×22 │
                        └────────────┬────────────┘
                                     v
                          dashboard · API · alerts
```

Five responsibilities:

1. **Poll each service** on its own interval; record health, latency, and errors.
2. **Walk the library paths** and record what is actually there — counts, bytes, newest mtime.
3. **Reconcile.** Diff the two. Everything interesting is in the difference.
4. **Alert** when a new discrepancy appears or a service goes down — to Discord, ntfy, or
   Gotify.
5. **Show it**, over a dashboard and a full REST API.

---

## What ShelfWatch is deliberately not

- **Not a writer.** It never modifies the services it watches and never deletes anything.
  **Say this loudly in the README** — it is a trust feature. Nobody installs a tool that might
  reorganise their library.
- **Not a media player.** No streaming, no file browsing.
- **Not a replacement for Homepage.** It is not a link grid. It is a reconciliation engine.

---

## Why this project and not another Django CRUD app

Almost every Django tutorial project is a blog or a shop: models, forms, views, done. None of
them teach the things that actually get asked about.

| What this needs | What a blog app never teaches you |
|---|---|
| Poll several services on schedules | Celery Beat, idempotent tasks, retries |
| Scans that run for hours | Two queues, `acks_late`, prefetch, distributed locks |
| 8,000 rows per scan | Bulk upserts, chunking, and why a `.save()` loop is unusable |
| A dashboard over that data | Real N+1s, and fixing them with measured query counts |
| API keys for other services | Encrypted fields, `write_only` serializers |
| Several users | Object-level permissions, and why 404 beats 403 |
| A public demo | Separating demo data from your actual private library |

The Celery section alone — **two queues, `.s` vs `.si`, and a Redis lock that stops a slow scan
being double-launched by the next Beat tick** — is more distributed-systems substance than most
candidates bring to a mid-level Python interview.

---

## The honest scope

**Weeks 1–3:** skeleton, models, admin, connectors.
**Weeks 4–7:** Celery, polling, scanning, reconciliation. The engine.
**Weeks 8–10:** DRF API, alerts, performance pass.
**Weeks 11–15:** the dashboard, built twice — Django templates, then React.
**Week 16:** production deployment and the demo instance.

Milestones 00–06 are a complete, deployable backend. Phase 4 is what makes it a full-stack
portfolio piece.

---

**Next:** [02-how-to-use-these-docs.md](02-how-to-use-these-docs.md)
