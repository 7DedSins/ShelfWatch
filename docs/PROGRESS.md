# Progress

> **This file is the state of the project.** Update it every session. An AI resuming your work
> reads this first.

**Current position:** Phase 1 — **m02**. Kavita + LANraragi + registry. 26 tests passed (Kavita respx `[!]`; no LRR respx yet).
**Last session:** 2026-09-09 — LRR parse AI-fixed; Kavita/`base`/registry/admin aligned to same JSON-guard style.
**Next action:** LRR respx tests (you type or grant). Stash mapping on paper. No Celery.

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

- [ ] **m03** Celery and polling
  - [ ] django/07 Celery and Beat
  - [ ] concepts/02 Scheduled work and idempotency
- [ ] **m04** Library scanning
  - [ ] django/04 ORM and query optimization
- [ ] **m05** Reconciliation *(tests first)*
- [ ] **CHECKPOINT** — first system-design drill

## Phase 3 — Interfaces

- [ ] **m06** DRF API
  - [ ] django/06 DRF
  - [ ] concepts/04 Authorization and tenancy
- [ ] **m07** Alerts
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
