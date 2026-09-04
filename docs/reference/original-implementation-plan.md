> ## ⚠️ SOLUTIONS MANUAL — DO NOT READ AHEAD
>
> This is the implementation spec written **before** the course in `docs/` existed. It is
> preserved intact because it contains real hard-won knowledge that would be expensive to
> reconstruct.
>
> **It also contains the answers to most of the curriculum.** Each milestone says when it is
> safe to open the relevant section. Reading a design conclusion before you have attempted the
> derivation costs you the lesson — and the derivation is the part that transfers.
>
> Note: the connector design, Kavita API quirks, and Celery queue split are all in here.

---

# ShelfWatch — Implementation Doc

**Stack:** Django 5, DRF, Celery + Redis, PostgreSQL, Docker Compose, HTMX + Alpine
**Goal:** The employable-stack showcase. Every line item in a "Backend Engineer (Python)" job
description, in one repo, running in production on your own VPS.
**Time budget:** 3–4 weeks of evenings. This is the flagship.

---

## 1. Why this project

Self-hosters run 5–10 services (Kavita, Komga, LANraragi, Jellyfin, *arr stack) with no single
place to answer: *what's actually on disk, what's stale, what's mid-scan, what broke overnight?*
Every existing "dashboard" (Homer, Homepage, Dashy) is a static link grid with a green dot. None
of them read the services' APIs and reconcile against the filesystem.

ShelfWatch does: it polls each configured service, walks the library paths, and surfaces the
**deltas** — series on disk that the reader doesn't know about, series in the reader whose files
vanished, chapters that never got a cover, scans that have been "running" for 14 hours.

You have a live instance of exactly this problem on the Contabo box (Kavita, LANraragi, a FUSE
mount over PikPak, a long-running injection pipeline). That makes the demo real, and "deployed and
running in production for N months" is a true statement you can put on a resume.

### What each requirement teaches
| Feature | Django skill it forces |
|---|---|
| Multiple service types | Model inheritance / polymorphism, `JSONField` for per-type config |
| Scheduled polling | Celery Beat, idempotent tasks, task retries with backoff |
| Filesystem walks | Long-running tasks, chunking, `bulk_create`/`bulk_update` |
| Deltas over time | Query optimization, `select_related`/`prefetch_related`, indexes, N+1 hunting |
| Secrets (API keys) | Encrypted fields, `django-environ`, never-in-repo config |
| REST API | DRF serializers, viewsets, pagination, filtering, throttling, OpenAPI schema |
| Multi-user | Django auth, permissions, per-object ownership |
| Admin | Django admin customization — the killer feature nobody demos properly |

---

## 2. Scope

### v1
- Register **Services** (Kavita, Komga, LANraragi, generic HTTP healthcheck) with base URL + API key
- Register **Libraries** — a service-side library mapped to a host path
- Celery Beat polls each service on a per-service interval; records a **HealthCheck** row
- A filesystem scan task walks each library path, upserts **DiskItem** rows (series-level, with
  child count + total bytes + newest mtime)
- **Reconciliation** task diffs service inventory vs disk inventory → **Discrepancy** rows
- Dashboard: service status cards, per-library counts, discrepancy feed, storage over time chart
- Alerts: on new discrepancy or a service going down, fire a webhook (Discord/ntfy/Gotify)
- Full DRF API + auto-generated OpenAPI docs
- One-command `docker compose up` bringing up web, worker, beat, postgres, redis

### Out of scope for v1
- Writing anything back to the services (read-only by design — say this loudly in the README, it's
  a trust feature)
- Media playback / file browsing
- Anything requiring a mobile app

---

## 3. Architecture

```
shelfwatch/
├── config/                     # project package (not "shelfwatch.settings")
│   ├── settings/
│   │   ├── base.py
│   │   ├── local.py
│   │   ├── production.py
│   │   └── test.py
│   ├── celery.py
│   ├── urls.py
│   └── asgi.py / wsgi.py
├── apps/
│   ├── core/                   # abstract models, mixins, utils
│   ├── services/               # Service, HealthCheck, connectors/
│   │   └── connectors/
│   │       ├── base.py         # BaseConnector ABC
│   │       ├── kavita.py
│   │       ├── komga.py
│   │       ├── lanraragi.py
│   │       └── registry.py
│   ├── libraries/              # Library, DiskItem, scanning tasks
│   ├── reconcile/              # Discrepancy, diff engine
│   ├── alerts/                 # AlertRule, Notification, channels/
│   ├── api/                    # DRF: serializers, viewsets, routers
│   └── dashboard/              # HTML views + templates
├── compose/                    # per-service Dockerfiles + entrypoints
├── docker-compose.yml
├── docker-compose.prod.yml
├── Makefile
└── pyproject.toml
```

**Rules that make this read as senior work:**
- `config/settings/` split, never a single `settings.py` with `if DEBUG`
- All apps under `apps/`, each with `apps.py` declaring an explicit `name`
- **Connectors are the only place that knows about a specific service's HTTP quirks.** Everything
  above them speaks `ServiceInventory` dataclasses. Adding Jellyfin later = one new file + one
  registry line, zero changes elsewhere. This is the design point a reviewer will notice.
- Business logic in `services.py` modules (plain functions), not in views and not in model methods.
  Celery tasks are thin wrappers that call them — so the logic is testable without a broker.

---

## 4. Data model

```python
# apps/core/models.py
class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta: abstract = True

# apps/services/models.py
class Service(TimeStampedModel):
    owner        = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name         = models.CharField(max_length=100)
    kind         = models.CharField(max_length=32, choices=ServiceKind.choices)
    base_url     = models.URLField()
    api_key      = EncryptedTextField(blank=True)      # django-fernet-fields or custom
    poll_interval_seconds = models.PositiveIntegerField(default=300)
    enabled      = models.BooleanField(default=True)
    config       = models.JSONField(default=dict, blank=True)   # per-kind extras
    class Meta:
        constraints = [models.UniqueConstraint(fields=["owner", "name"], name="uniq_service_name_per_owner")]

class HealthCheck(TimeStampedModel):
    service      = models.ForeignKey(Service, related_name="health_checks", on_delete=models.CASCADE)
    ok           = models.BooleanField()
    latency_ms   = models.PositiveIntegerField(null=True)
    status_code  = models.PositiveSmallIntegerField(null=True)
    error        = models.TextField(blank=True)
    class Meta:
        indexes = [models.Index(fields=["service", "-created_at"])]

# apps/libraries/models.py
class Library(TimeStampedModel):
    service            = models.ForeignKey(Service, related_name="libraries", on_delete=models.CASCADE)
    remote_id          = models.CharField(max_length=64)      # id inside Kavita/Komga
    name               = models.CharField(max_length=255)
    host_path          = models.CharField(max_length=1024)    # as mounted into the worker
    scan_interval_hours = models.PositiveIntegerField(default=24)
    last_scanned_at    = models.DateTimeField(null=True, blank=True)

class DiskItem(TimeStampedModel):
    library      = models.ForeignKey(Library, related_name="disk_items", on_delete=models.CASCADE)
    relative_path = models.CharField(max_length=1024)
    name         = models.CharField(max_length=512, db_index=True)
    file_count   = models.PositiveIntegerField(default=0)
    total_bytes  = models.BigIntegerField(default=0)
    newest_mtime = models.DateTimeField(null=True)
    seen_at      = models.DateTimeField()      # set to scan start; stale rows = deleted on disk
    class Meta:
        constraints = [models.UniqueConstraint(fields=["library", "relative_path"], name="uniq_diskitem_path")]

# apps/reconcile/models.py
class Discrepancy(TimeStampedModel):
    library      = models.ForeignKey(Library, related_name="discrepancies", on_delete=models.CASCADE)
    kind         = models.CharField(max_length=32, choices=DiscrepancyKind.choices)
    subject      = models.CharField(max_length=512)
    detail       = models.JSONField(default=dict)
    resolved_at  = models.DateTimeField(null=True, blank=True)
    acknowledged = models.BooleanField(default=False)
```

`DiscrepancyKind`: `MISSING_IN_SERVICE`, `MISSING_ON_DISK`, `COUNT_MISMATCH`, `NO_COVER`,
`STALLED_SCAN`, `EMPTY_SERIES`.

**Storage-over-time** comes from a small `StorageSnapshot(library, taken_at, total_bytes, item_count)`
written once per scan. Don't try to derive history from `DiskItem` — you'll want a separate,
cheap, append-only table for the chart.

### Query-optimization lessons to hit deliberately
- Dashboard first draft will N+1 on `service.latest_health`. Fix it with a `Prefetch` of a sliced
  queryset, or a denormalized `Service.last_health_ok` updated by the poll task. **Do it the naive
  way first, capture `django-debug-toolbar` before/after query counts, and put both screenshots in
  the README.** Demonstrating you can find and fix an N+1 is worth more than never having one.
- `DiskItem` upserts: `bulk_create(..., update_conflicts=True, unique_fields=[...], update_fields=[...])`
  in chunks of 1000. A per-row `.save()` loop over 8,000 series is the difference between 4 seconds
  and 6 minutes.

---

## 5. Connectors

```python
@dataclass(frozen=True)
class RemoteSeries:
    remote_id: str
    name: str
    item_count: int
    has_cover: bool

@dataclass(frozen=True)
class RemoteLibrary:
    remote_id: str
    name: str
    paths: list[str]

class BaseConnector(ABC):
    def __init__(self, service: Service, http: httpx.Client): ...
    @abstractmethod
    def health(self) -> HealthResult: ...
    @abstractmethod
    def list_libraries(self) -> list[RemoteLibrary]: ...
    @abstractmethod
    def list_series(self, library_remote_id: str) -> Iterator[RemoteSeries]: ...
    def active_scans(self) -> list[ScanStatus]: return []      # optional capability
```

`registry.py` maps `ServiceKind -> connector class`. Capabilities that not every service has get a
default implementation, not an abstract method — otherwise adding a connector becomes a chore.

**Kavita specifics you already know and should encode:**
- Auth: exchange the API key for a JWT via `/api/Plugin/authenticate`, then `Authorization: Bearer`.
  Cache the JWT on the connector instance; re-auth on 401 exactly once, then fail.
- `/api/Series/all-v2` ignores the `libraryId` filter — a real, confirmed quirk. Filter client-side
  and leave a comment with that fact. (Reviewers love a comment that explains *why* the obvious
  code isn't there.)
- Paginate; don't assume one response holds everything.

Write connectors against **recorded fixtures** (`respx` or `responses`), not the live VPS, so CI is
hermetic. Keep one opt-in integration test marked `@pytest.mark.integration`, skipped unless env
vars are set.

---

## 6. Celery layout

```python
# tasks
poll_service(service_id)                 # ~seconds, retries 3x exp backoff
scan_library(library_id)                 # minutes-to-hours, own queue
reconcile_library(library_id)            # after scan
dispatch_alerts(discrepancy_ids)
schedule_polls()                         # beat: every 60s, fans out due services
schedule_scans()                         # beat: every 15m, fans out due libraries
```

**Two queues:** `default` (fast) and `scans` (slow), with separate worker containers. A 6-hour
filesystem walk must not block health polls. Set `worker_prefetch_multiplier=1` and
`task_acks_late=True` on the scans queue.

**Idempotency + locking:** wrap `scan_library` in a Redis lock keyed on the library id
(`cache.add(key, "1", timeout=...)`) so a slow scan can't be double-launched by the next beat tick.
Release in a `finally`. This is a real distributed-systems detail and it belongs in the README.

**Chain:** `chain(scan_library.s(id), reconcile_library.si(id))` — note `.si` (immutable) so the
scan's return value isn't passed as an argument. Getting `.s` vs `.si` wrong is the classic Celery
bug; knowing the difference is a genuine interview answer.

**Never trust a log file for progress.** Python fully buffers stdout when it isn't a TTY, so a
tailed log can look frozen while the job is fine. Progress lives in the DB (`Library.last_scanned_at`,
row counts) — that's the ground truth, and the dashboard reads it.

---

## 7. DRF API

- `ModelViewSet` for Service / Library / Discrepancy; read-only viewsets for HealthCheck & DiskItem
- `IsAuthenticated` + a custom `IsOwner` object permission; **override `get_queryset()` to filter by
  `request.user`** — never rely on object permissions alone for list endpoints (the classic
  broken-object-level-authorization bug)
- Never serialize `api_key`. `write_only=True` on input, absent from output. Add a test asserting
  the string never appears in any response body.
- `django-filter` for `?kind=`, `?resolved=`, `?library=`; `OrderingFilter`; cursor pagination on
  `HealthCheck`
- Custom actions: `POST /api/services/{id}/poll/`, `POST /api/libraries/{id}/scan/`,
  `POST /api/discrepancies/{id}/acknowledge/`
- Throttling on the manual-trigger actions
- `drf-spectacular` → `/api/schema/` + Swagger UI at `/api/docs/`. Screenshot this in the README.
- Token auth via `djangorestframework-simplejwt`

---

## 8. Dashboard

Django templates + HTMX + Alpine.js + Tailwind (via `django-tailwind` or a CDN build). No SPA.

Pages: **Overview** (service cards, storage chart, recent discrepancies), **Library detail**
(disk items table, scan history), **Discrepancies** (filterable, bulk-acknowledge),
**Settings** (service CRUD, test-connection button that hits the connector live).

Storage chart: server-rendered data → a small Chart.js line chart. Don't add a frontend build
pipeline for one chart.

---

## 9. Django admin (the underrated demo)

Genuinely customize it — most portfolios ship the default and it shows.
- `list_display` with computed columns, `list_filter`, `search_fields`, `date_hierarchy`
- `readonly_fields` for anything task-written
- Admin actions: "Poll now", "Scan now", "Acknowledge selected"
- `ServiceAdmin` with a colored ✅/❌ status column via a `@admin.display(boolean=True)` method
- `get_queryset()` with `select_related` so the changelist isn't 200 queries

---

## 10. Testing

`pytest` + `pytest-django` + `factory_boy` + `respx`.

- Model tests: constraints actually raise `IntegrityError`
- Connector tests: mocked HTTP, including 401-then-retry and malformed-JSON paths
- Task tests: `CELERY_TASK_ALWAYS_EAGER=True` in the test settings
- Reconcile tests: the whole point — construct disk + remote inventories, assert the exact
  discrepancy set. Table-driven.
- API tests: authz matrix — owner ✅, other user 404 (**404, not 403** — don't leak existence),
  anonymous 401
- Scan tests: `tmp_path` with a real synthetic tree
- `pytest --cov`, target 80%+, badge in README

---

## 11. Deployment (Contabo)

`docker-compose.prod.yml`: `web` (gunicorn + whitenoise), `worker-default`, `worker-scans`, `beat`,
`postgres`, `redis`, `caddy` (auto-TLS). Media/library paths mounted **read-only** into the scan
workers — `:ro` is both correct and a nice thing for a reviewer to spot.

- `django-environ`, `.env.example` committed, `.env` never
- `DEBUG=False`, `ALLOWED_HOSTS`, `SECURE_*` settings, `CSRF_TRUSTED_ORIGINS`
- Healthchecks in compose; `depends_on: condition: service_healthy`
- `entrypoint.sh` runs `migrate` then `collectstatic` then execs the command
- Sentry (free tier) for error tracking — 5 lines, big credibility
- `/healthz` returning DB + Redis + Celery-ping status
- Structured JSON logging via `python-json-logger`

**Caveat about a "live demo":** don't expose a public instance with your real library. Deploy a
separate instance seeded with a demo fixture (a fake service backed by a stub connector) behind
`demo/demo` credentials, and link that. Keeps your actual media private while still giving reviewers
something clickable.

---

## 12. Build order

1. Compose skeleton: postgres, redis, Django, `/healthz`, CI running `pytest` — get the boring
   infrastructure green on day one
2. `apps/core` + `apps/services` models + admin + migrations
3. `BaseConnector` + Kavita connector + fixture tests
4. `poll_service` task + Celery + Beat + HealthCheck rows
5. `apps/libraries`: model, scan task, bulk upserts, `StorageSnapshot`
6. `apps/reconcile`: diff engine + tests (do the tests first here)
7. DRF API + spectacular docs
8. Dashboard templates + HTMX + chart
9. `apps/alerts` + webhook channel
10. Production compose, Caddy, deploy to Contabo, Sentry
11. Performance pass: debug-toolbar, kill the N+1s, document before/after
12. README + architecture diagram + GIF; post to r/selfhosted

Ship steps 1–7 and you already have a stronger backend repo than 95% of what's on GitHub.

---

## 13. README structure

Pitch → architecture diagram (Excalidraw or Mermaid, committed as source) → screenshot GIF →
quickstart → **"Engineering notes"** section covering: the connector abstraction, the two-queue
Celery split, the Redis scan lock, the N+1 fix with query counts, and the read-only-by-design
stance. That section is what a hiring engineer reads. Write it for them.

---

## 14. Interview answers this repo hands you

Have a two-sentence version of each ready:
- Why two Celery queues, and what `task_acks_late` + prefetch=1 actually do
- `.s` vs `.si` in a chain
- How you made a task idempotent under a scheduler that can double-fire
- How you found and fixed an N+1 (with numbers)
- Why list endpoints filter in `get_queryset()` rather than relying on object permissions
- Why you return 404 instead of 403 for another user's object
- How you'd add a Jellyfin connector (answer: one file, one registry entry)
