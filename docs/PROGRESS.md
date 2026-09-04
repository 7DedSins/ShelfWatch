# Progress

> **This file is the state of the project.** Update it every session. An AI resuming your work
> reads this first.

**Current position:** Phase 0 — orientation understood; environment next. Python writing rehab before Django. **Do not start m00.**
**Last session:** 2026-09-04 — product + teaching contract + VS Code RAM setup. Docker skipped on the laptop.
**Next action:** Open `ShelfWatch.code-workspace`. Create `D:\learn\python-rehab` venv. Evening-1 script (walk a folder, print name/size/mtime) typed by hand. Paste it here.

---

## Status key

`[ ]` not started `[~]` in progress `[x]` done `[!]` done but I could not explain it out loud — revisit

---

## Phase 0 — Orientation

- [x] 01 What we are building
- [x] 02 How to use these docs (teaching contract)
- [~] 03 Prerequisites and setup — Docker **not** on this laptop (RAM). SQLite + venv until Celery/VPS. VS Code workspace + Ruff/Pylance done. Python 3.12 at `D:\ProgramFilesSDKs\python.exe`. Writing rehab not started.

## Phase 1 — Foundations

- [ ] **m00** Skeleton
  - [ ] django/01 Django vs Flask
  - [ ] django/02 Settings and project layout
- [ ] **m01** Services and health
  - [ ] django/03 Models and migrations
  - [ ] django/05 The Django admin
  - [ ] concepts/03 Secrets at rest
- [ ] **m02** Connectors
  - [ ] concepts/01 Polling and reconciliation

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
| AI does not write implementation code | Six months of prompt-and-review atrophied writing. Rehab: type it, AI reviews. |
| Public GitHub yes; daily X/“learning in public” no | 4 YOE backend. GitHub + LinkedIn are the job surface. Bootcamp-style streaks would read as junior. |
| Ruff only (not Black/flake8/pylint/mypy) | One linter. Pylance `basic` for types. |

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

- (none yet)

---

## Session log

```
### 2026-09-04 — orientation + VS Code
Did: Read product + teaching contract. Inspected GitHub (7DedSins) and resume. Configured VS Code (parent RAM guards, ShelfWatch.code-workspace, Ruff/Pylance/Django/Error Lens, ruff.toml).
Struggled with: VS Code RAM with parent folder open; Grok sessions are cwd-scoped so this chat does not appear in the ShelfWatch window.
Decided: skip local Docker; writing rehab before m00; advertise via GitHub/LinkedIn not daily X.
Next: python-rehab evening 1 (folder walk script, typed by hand).
```
