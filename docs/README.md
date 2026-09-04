# ShelfWatch — Documentation

ShelfWatch watches a fleet of self-hosted media services (Kavita, Komga, LANraragi, anything
with an HTTP API) and answers the question none of them can: **what does each service think it
has, what is actually on disk, and where do those two disagree?**

It polls each service, walks the library paths, and surfaces the **deltas** — series on disk
the reader has never indexed, series in the reader whose files have vanished, chapters with no
cover, scans that have been "running" for fourteen hours.

Existing dashboards (Homer, Homepage, Dashy) are link grids with a green dot. None of them read
the services' APIs and reconcile against the filesystem. That gap is the product.

**But that is not what this folder is.**

This folder is a **course**. It teaches you Django, DRF, and Celery — the exact stack in almost
every "Backend Engineer (Python)" job description — by building one real system end to end,
deployed and running on your own VPS.

---

## Why this project is the flagship

You have a live instance of this problem on the Contabo box: Kavita, LANraragi, Komga, a FUSE
mount over PikPak, and a long-running injection pipeline. The demo is real, and **"deployed and
running in production for N months" is a true statement you can put on a CV.**

| Feature the product needs | Django skill it forces |
|---|---|
| Several kinds of service | Polymorphism, `JSONField` for per-type config |
| Scheduled polling | Celery Beat, idempotent tasks, retries with backoff |
| Filesystem walks | Long tasks, chunking, bulk upserts |
| Deltas over time | Query optimisation, `select_related`, indexes, N+1 hunting |
| API keys | Encrypted fields, secrets never in the repo |
| REST API | DRF serializers, viewsets, pagination, throttling, OpenAPI |
| Multiple users | Django auth, object-level permissions |
| Admin | Django admin customisation — the killer feature nobody demos properly |

---

## Read this first

These docs assume **no Django knowledge** and no distributed-systems vocabulary. Every term is
taught from zero in the lesson where you first need it.

What is assumed: Python, a terminal, and having met SQL. Flask experience helps but is not
required — [02-django/01](02-django/01-django-vs-flask.md) covers the differences explicitly if
you have done [Colophon](../../Colophon/docs/) first.

---

## How to start

1. Read [00-orientation/01-what-we-are-building.md](00-orientation/01-what-we-are-building.md).
2. Read [00-orientation/02-how-to-use-these-docs.md](00-orientation/02-how-to-use-these-docs.md) — **the teaching contract.**
3. Do the setup.
4. Open [CURRICULUM.md](CURRICULUM.md), start at Milestone 00.

---

## Resuming with any AI

> I'm learning Django by building ShelfWatch. Read `docs/00-orientation/02-how-to-use-these-docs.md`
> for how to teach me, then `docs/PROGRESS.md` for where I am. Follow the teaching contract —
> do not write my implementation code, do not reveal anything from `docs/reference/`.
> Teach me the next lesson.

---

## Map of this folder

| Path | What it is |
|---|---|
| [CURRICULUM.md](CURRICULUM.md) | The master learning path. |
| [PROGRESS.md](PROGRESS.md) | Your state file. |
| [GLOSSARY.md](GLOSSARY.md) | Terms in plain language. |
| [00-orientation/](00-orientation/) | What we're building, how to learn here, setup. |
| [01-concepts/](01-concepts/) | Polling, reconciliation, scheduling, secrets, authorization. |
| [02-django/](02-django/) | Django, DRF, and Celery skills. Just-in-time. |
| [03-build/](03-build/) | **The spine.** Nine milestones. |
| [04-frontend/](04-frontend/) | **The dashboard, built twice** — Django templates, then React. |
| [05-ops/](05-ops/) | Deployment to Contabo, monitoring, the public demo instance. |
| [06-interview/](06-interview/) | Question bank. |
| [reference/](reference/) | ⚠️ The original implementation plan — **contains the answers.** |

---

## ⚠️ About `reference/original-implementation-plan.md`

That file is the spec you wrote before this course existed. It is good and it is preserved
intact, because it contains real knowledge — the Kavita API quirks you discovered, the
connector design, the Celery queue split.

**It also contains the answers to most of this course.**

Treat it as a solutions manual. Attempt the derivation first, then check. Each milestone says
when it is safe to open.

---

## The two structural ideas

**1. Connectors are the only code that knows about a specific service.** Everything above them
speaks in plain dataclasses. Adding Jellyfin later is one new file and one registry line, with
zero changes anywhere else. This is the design point a reviewer will notice first.

**2. Business logic lives in `services.py` modules, not in views and not in model methods.**
Celery tasks are thin wrappers that call them. That means the logic is testable without a
broker, reusable by the API and the dashboard, and does not care how it was invoked.

Both rules exist to be enforced, not admired. There are tests for them.

---

## Ground rules

- **The AI does not write your implementation code.**
- **Update [PROGRESS.md](PROGRESS.md) every session.**
- **Read-only by design.** ShelfWatch never writes to the services it watches and never deletes
  anything. Say it loudly in the README — it is a trust feature, not a limitation.
- **Do the naive version first** where a lesson says to. The N+1 you fix with a screenshot of
  the query count before and after is worth more than the N+1 you never had.
