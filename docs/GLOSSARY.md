# Glossary

Plain-language definitions.

---

## The domain

**Service** — One media application ShelfWatch watches: Kavita, Komga, LANraragi, or anything
with an HTTP health endpoint.

**Library** — A collection inside a service, mapped to a path on disk. Kavita's "Manhwa"
library pointing at `/manga/manhwa` is one Library row.

**Connector** — The *only* code that knows how a specific service's API behaves. Everything
above it speaks in plain dataclasses. Adding Jellyfin is one new connector file.

**Inventory** — What a service says it has. **DiskItem** — what is actually on disk.

**Discrepancy** — A disagreement between the two. The product.

**Reconciliation** — Computing discrepancies by diffing inventory against disk.

**Stalled scan** — A service reporting a scan "in progress" for far longer than plausible.
A real failure mode on a FUSE mount, and one nothing else detects.

**Read-only by design** — ShelfWatch never writes to the services it watches. A trust feature,
stated loudly.

---

## Scheduling

**Celery** — A distributed task queue. Your Django code hands work to a broker; a separate
worker process picks it up.

**Broker** — The queue itself. Redis here.

**Celery Beat** — The scheduler. Fires tasks on a cron-like schedule.

**Queue** — A named channel. ShelfWatch uses two: `default` for fast health polls and `scans`
for filesystem walks that may run for hours. **Separate worker containers**, so a six-hour scan
cannot block a health check.

**`task_acks_late`** — Acknowledge a task *after* it completes rather than when received.
A worker that dies mid-task means the task is redelivered rather than lost.

**`worker_prefetch_multiplier=1`** — Take one task at a time. Without it, a worker grabs a
batch and sits on them while running the first — disastrous for long tasks.

**`.s` vs `.si`** — In a chain, `.s` (signature) passes the previous task's return value as an
argument; `.si` (immutable signature) does not. Getting this wrong is *the* classic Celery bug.

**Idempotent task** — Safe to run twice. Essential, because Beat can double-fire and
`acks_late` means redelivery.

**Distributed lock** — A Redis key claimed before starting a task so a second copy will not
start. Released in a `finally`. Needs a timeout, or a crashed worker locks the resource forever.

**Backoff** — Waiting longer between each retry. **Jitter** — randomness added so many retries
do not land simultaneously.

---

## Django

**Project vs. app** — The project is the whole thing (`config/`). An app is a self-contained
feature (`apps/services/`). ShelfWatch has six.

**Split settings** — `base.py`, `local.py`, `production.py`, `test.py` — instead of one file
full of `if DEBUG`.

**Migration** — A versioned schema change. Django generates them from model changes.

**QuerySet** — Lazy. Nothing hits the database until you iterate it. Understanding *when*
evaluation happens is most of Django ORM performance.

**N+1 query** — One query for a list, then one more per item. Fixed with `select_related`
(joins, for foreign keys) or `prefetch_related` (a second query, for reverse and many-to-many).

**`bulk_create` / `bulk_update`** — Insert or update thousands of rows in a handful of queries
instead of thousands. The difference between 4 seconds and 6 minutes on 8,000 rows.

**Upsert** — Insert-or-update. `bulk_create(update_conflicts=True, ...)`.

**Django admin** — A generated CRUD interface. Genuinely customisable, and most portfolios ship
the default, which shows.

**`JSONField`** — A schemaless column. Right for per-service-type config; wrong as a substitute
for a schema you were too lazy to design.

---

## DRF

**Serializer** — Converts models to and from JSON, and validates input. Pydantic's rough
equivalent.

**ViewSet** — A class bundling list/create/retrieve/update/destroy for one model.

**Router** — Generates URLs from a viewset.

**`get_queryset()`** — Where you filter by the current user. **This, not object permissions, is
what secures list endpoints** — object permissions only run on single-object views, so relying
on them alone leaks every other user's rows in a list. The classic broken-object-level-
authorization bug.

**Throttling** — Rate limiting. **Pagination** — cursor-based for append-only logs, because
offset pagination skips and duplicates rows as new ones arrive.

**`drf-spectacular`** — Generates an OpenAPI schema from your serializers, which gives you
Swagger UI and lets the React frontend generate its types.

---

## Security

**Encrypted field** — A model field encrypted at rest. Service API keys need this: unlike a
password, you must be able to *use* the value, so it cannot be one-way hashed.

**`write_only`** — A serializer field accepted on input and never returned. How an API key
enters the system and never leaves it.

**404 vs 403** — Requesting another user's object returns **404**. A 403 confirms the object
exists, which is an information leak.

**Object-level permission** — "Can this user touch *this* row?" Distinct from "can this user
use this endpoint at all?"

---

## Frontend

**Server-rendered** — HTML built on the server. Django templates.

**SPA** — Single-page application. React downloads once and then talks JSON.

**HTMX** — Attributes that make HTTP requests and swap the HTML response into the page.
Interactivity without a build step.

**Alpine.js** — Small client-side reactivity for the bits HTMX cannot do, like a dropdown.

**Server state** — A cached copy of data owned by the server. Different from client state, and
the reason TanStack Query exists.

**Hydration / bundle / code splitting** — See
[Ferryman's frontend track](../../Ferryman/docs/09-frontend/), which teaches React properly.
This project applies it.
