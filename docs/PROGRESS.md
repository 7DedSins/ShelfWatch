# Progress

> **This file is the state of the project.** Update it every session. An AI resuming your work
> reads this first.

**Current position:** m06 remainder on `feat/jwt-openapi`. Page-number pagination in. Next: N+1 query counts in this file, then merge, then m07. Stash last.
**Last session:** 2026-09-17 — Pagination. Typo `PAgeNumberPagination` vs settings `PageNumberPagination`; AI renamed `[!]`. List tests use `results`. No HealthCheck cursor.
**Next action:** Measure list/detail query counts (N+1) and record in the numbers table. Then open PR / merge this branch. Then m07 alerts (engine, not dashboard).

---

## Status key

`[ ]` not started `[~]` in progress `[x]` done `[!]` done but I could not explain it out loud — revisit

---

## Phase 0 — Orientation

- [x] 01 What we are building
- [x] 02 How to use these docs (teaching contract)
- [x] 03 Prerequisites and setup — Docker **not** on this laptop (RAM). SQLite + venv. VS Code workspace + Ruff/Pylance. Python 3.12 at `D:\ProgramFilesSDKs\python.exe`. Writing rehab is the connector work (type, AI reviews).

## Phase 1 — Foundations

- [x] **m00** Skeleton (partial vs original: no Docker, no six apps). Django 6.1, `config/`, split settings, django-environ. PRs 1–2.
- [x] **m01** Services and health. `Service` + encrypted `api_key`, admin, `/healthz/`, pytest in `apps/<app>/tests/`. PRs 3–6.
  - [x] django/03 Models and migrations *(used; interview explain still needed)*
  - [x] django/05 The Django admin
  - [x] concepts/03 Secrets at rest — Fernet process key vs per-row Kavita key; hashing is wrong for API keys
- [~] **m02** Connectors
  - [x] `apps/services/connectors/base.py` — frozen dataclasses, three errors, ABC; user typed
  - [x] `kavita.py` HTTP — user typed JWT, libraries, series (all-v2 + client filter)
  - [~] `lanraragi.py` — user typed auth/health; **AI fixed** search pagination + category filter 2026-09-09 (`[!]` until explained)
  - [x] `registry.py` + `Service.kind`
  - [!] respx tests — AI-written; 46 services tests passed 2026-09-09 (Kavita + LRR + registry). Explain before interview.
  - [!] concepts/01 Polling and reconciliation — taught; user could not explain empty vs `[]` at first — revisit out loud

## Phase 2 — The engine

- [~] **m03** Celery and polling — PRs #10–#11 on `main`. Lock/starvation/two workers still not started (needs Redis)
  - [~] django/07 — settings + retries taught; two workers / lock not done; `.s` vs `.si` used on scan→reconcile chain
  - [~] concepts/02 — taught; lock not implemented
  - [x] `poll_interval_seconds` + `schedule_polls`; persist then re-raise; tests `[!]`
  - [x] Beat + `default`/`scans` routes + Unavailable retries + pytest GHA `[!]` tests
- [x] **m04** Library scanning — PR #12 on `main` (`feat(m04): library scan with chunked upsert, snapshot, schedule`)
  - `Library` / `DiskItem` / `StorageSnapshot`; `seen_at` vs `last_scanned_at`; `remote_id`; scan task on `scans`
  - [~] django/04 ORM — N+1/bulk taught; **timings still empty** in the numbers table
- [x] **m05** Reconciliation — PR #13 on `main`. `diff_inventories` + `Discrepancy`; skip `ConnectorError` (never treat as `[]`); `chain(.s, .si)`
  - Failed-fetch vs empty inventory still `[!]` until explained out loud
- [ ] **CHECKPOINT** — first system-design drill (due after m05; skipped so far)

## Phase 3 — Interfaces

- [~] **m06** DRF API — first slice on `main` (PR #14). Remainder on `feat/jwt-openapi`
  - [x] `apps.api`, `Service.owner`, ReadOnly viewsets, `get_queryset` tenancy (404 not 403), `api_key` write_only
  - [x] POST poll/scan/acknowledge, throttles, `SessionAuthentication` (anon 403). Nested tests `[!]`
  - [!] JWT (`simplejwt`) + keep session — package + token URLs user-typed; `JWTAuthentication` in REST_FRAMEWORK **AI-written 2026-09-17**
  - [x] drf-spectacular `/api/schema/` `/api/docs/` — `SERVE_PERMISSIONS` AllowAny; `api_key` writeOnly in schema
  - [!] List-leak: `IsOwner` + `get_queryset`. User built it; **`permission_class` typo AI-fixed** (must be `permission_classes`). Tests `[!]`
  - [~] concepts/04 — leak taught; explain out loud: object perm ≠ list, 404 vs 403, plural attribute
  - [!] django-filter — user typed backends; **`filterset_fileds` typo + missing INSTALLED_APPS `django_filters` AI-fixed**. `?kind=` / `?status=` / `?library=` / `?service=` stay inside `get_queryset`
  - [!] Page-number pagination (`?page=` / `?page_size=`). Class typo `PAgeNumberPagination` AI-fixed. **No cursor** — no HealthCheck log; `last_health_ok` on Service
  - [ ] N+1 measurement recorded below
  - [~] django/06 DRF — JWT/OpenAPI/filter/page in; N+1 numbers not yet
- [ ] **m07** Alerts — after this branch. Do not skip the engine for a dashboard
- [ ] **m08** Performance pass
  - [ ] django/08 Testing Django

## Phase 4 — The dashboard, twice

- [ ] frontend/README — why build it twice
- [ ] frontend/01 Django templates and HTMX
- [ ] frontend/02 React + TypeScript SPA
- [ ] frontend/03 Consuming DRF from React
- [ ] frontend/04 **The comparison write-up**

## Phase 5 — Production

- [ ] ops/01 Production deployment
- [ ] ops/02 Monitoring and the demo instance
- [ ] **CHECKPOINT** — live on Contabo against real services

## Phase 6 — Interview

- [ ] Question bank Section A without notes
- [ ] Question bank Section B without notes
- [ ] Question bank Section C without notes
- [ ] System-design drill: 3 clean passes

## Phase 7 — Lookout / full fleet (optional)

- [ ] [07-lookout-and-fleet.md](07-lookout-and-fleet.md) read
- [ ] `apps.fleet` snapshots (`GET /api/fleet/latest/`)
- [ ] Allowlisted actions + audit (flag off on demo)
- [ ] Stash: container + GraphQL ping before full inventory connector

---

## Decisions I have made and why

> These become your interview answers. Write them down as you go.

| Decision | Why |
|---|---|
| Do not open `D:\Github Projects` as the VS Code folder | It indexes KomaReader/Unity/Android `build/` (~100k files). Open `ShelfWatch.code-workspace` only. |
| No Docker Desktop alongside VS Code on this machine | ~15 GB RAM, ~3.6 GB free. Django + SQLite locally; Postgres/Redis/Celery later on Contabo or when RAM allows. |
| AI does not write implementation code | Rehab: type it, AI reviews. **Exception 2026-09-06:** tests. **Exception 2026-09-07:** user granted AI the Kavita **test suite** + comments on `kavita.py`. **Cannot defend those tests in an interview until explained out loud.** `kavita.py` logic was user-typed. |
| Public GitHub yes; daily X/“learning in public” no | 4 YOE backend. GitHub + LinkedIn are the job surface. Bootcamp-style streaks would read as junior. |
| Ruff only (not Black/flake8/pylint/mypy) | One linter. Pylance `basic` for types. |
| Connector returns frozen dataclasses, never vendor JSON | Kavita field names must not leak; adding Komga/Jellyfin is one file. |
| Connector timeout **raises**, never `[]` | Empty inventory vs failed fetch must be different types or m05 will mark every series deleted. |
| `active_scans` default `[]` on the ABC, not abstract | Optional capability; not every vendor has running scans. |
| Retries live in Celery (later), not the connector | One exception later: single re-auth on Kavita 401. |
| Watch **every app on the VPS**, not only manga readers | 2026-09-09: live set is Kavita, LANraragi, Stash (Komga not running). Stash is in scope; it does not fit library/series without stretching the ABC. |
| Order: poll → Celery → engine → Stash last | Naive Django poll first (no Redis). Celery when Redis exists (VPS). Disk/reconcile on Kavita+LRR before a Stash GraphQL client. |
| Teaching: code in chat, then I type | 2026-09-11. Drop skeleton-first. AI pastes one slice in chat with gotchas; I type; AI does not write implementation files. `[!]` if I cannot explain a line. |
| Exception 2026-09: tests + `[!]` + corrections | Walkthrough in chat; user types implementation. Persist-then-raise and empty-vs-`[]` must be explainable. |
| JWT + session together | Session for browsable API/cookie; Bearer for Lookout/React. Adding JWT flips anon from 403→401 (`WWW-Authenticate`). Tests already allow both. |
| No HealthCheck log for cursor demo | Health is denormalized on `Service.last_health_ok`. Cursor pagination needs another append-only table or a written skip. |
| m07 alerts before a dashboard | Dedupe/batch/flap engine first. Lookout/fleet is Phase 7 after JWT. |
| Branch `feat/jwt-openapi` | Not `feat/m06-jwt-openapi`. Do not start m07 on this branch. |

---

## Numbers I have measured

> This project generates a lot of quotable numbers. Collect them — they are what turn claims
> into evidence.

| What | Before | After |
|---|---|---|
| Dashboard query count (N+1 fix) | | |
| Bulk upsert vs. per-row save (8,000 rows) | | |
| Scan duration, real library | | |
| Dashboard load time | | |
| React bundle size | | |

---

## Open questions I still have

- How does `RemoteLibrary` / `RemoteSeries` map to Stash scenes/galleries without lying? New dataclasses vs a wider inventory type?

---

## Session log

```
### 2026-09-17 — JWT lesson + PROGRESS backfill
Did: Confirmed teaching contract. Repo is m00–m05 + m06 DRF slice on main (PRs #11–#14). Branch `feat/jwt-openapi`. Taught JWT + keep session (401 vs 403, access/refresh, token URLs outside the router). User pip + INSTALLED_APPS + token views. AI granted: JWTAuthentication before SessionAuthentication; token paths above api include. `[!]`.
Struggled with: REST_FRAMEWORK still session-only after installing simplejwt — token view worked, Bearer on /api/services/ did not. Progress lag vs git.
Decided: One slice = JWT; spectacular next; leak demo last or skip note. m07 after this branch.
Next: Smoke obtain-pair + Bearer GET. Then spectacular.
### 2026-09 (backfill from git, not live session notes)
Did on main: m03 Beat/queues/retries (PR #11); m04 chunked scan + DiskItem.seen_at (PR #12); m05 reconcile skip ConnectorError + chain .s/.si (PR #13); m06 scoped ReadOnly API, owner, poll/scan/acknowledge, session auth (PR #14).
Not done: JWT, spectacular, list-leak demo, django-filter, cursor pagination, N+1 numbers.
### 2026-09-07 — Kavita connector + AI tests
Did: User typed kavita.py (JWT, libraries, all-v2 series + client filter). AI added comments, json/params keywords, series JSON guard; respx suite (8 tests). User granted this — cannot defend tests until explained.
Struggled with: DevTools empty on Tailscale UI; `/library/7` vs `/api/Library/libraries`; `_send` not forwarding json; int vs str libraryId.
Decided: No live VPS in CI. Komga/registry not this commit.
Next: User explains timeout vs []. Then registry or Komga, or PR.
### 2026-09-06 — m02 base connector
Did: Branch `feat/kavita-connector` from main (PR #6). Typed `apps/services/connectors/base.py` (+ empty `__init__.py`). Validated: HealthResult/RemoteLibrary/RemoteSeries frozen; ConnectorError + Unavailable/AuthFailed/BadResponse; ABC health/list_libraries/list_series iterator; active_scans default []. No HTTP yet.
Struggled with: Could not initially explain why timeout ≠ `[]`, or what to put in base.py. Needed samples (dataclass, ABC, exceptions) then assembled.
Decided: First file is the contract, not Kavita HTTP. Do not start komga/lanraragi/registry this session.
Next: Say empty-vs-failure in own words. Type `kavita.py`.
### 2026-09-04 — orientation + VS Code
Did: Read product + teaching contract. Inspected GitHub (7DedSins) and resume. Configured VS Code (parent RAM guards, ShelfWatch.code-workspace, Ruff/Pylance/Django/Error Lens, ruff.toml).
Struggled with: VS Code RAM with parent folder open; Grok sessions are cwd-scoped so this chat does not appear in the ShelfWatch window.
Decided: skip local Docker; writing rehab before m00; advertise via GitHub/LinkedIn not daily X.
Next: python-rehab evening 1 (folder walk script, typed by hand).
```
