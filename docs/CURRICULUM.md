# Curriculum — the learning path

**The build milestones are the spine.** Concepts and Django lessons are pulled in when a
milestone needs them.

Estimated total: **14–18 weeks at ~8 focused hours/week**, including the frontend built twice.
Milestones 00–06 alone already make a stronger backend repo than most of what is on GitHub.

---

## Phase 0 — Orientation (1 session)

| Lesson | Purpose |
|---|---|
| [00-orientation/01](00-orientation/01-what-we-are-building.md) | The product, concretely |
| [00-orientation/02](00-orientation/02-how-to-use-these-docs.md) | **The teaching contract.** Non-optional. |
| [00-orientation/03](00-orientation/03-prerequisites-and-setup.md) | Docker, Postgres, Redis, repo, Contabo access |

---

## Phase 1 — Foundations (m00–m02)

| Milestone | Detours | You will be able to explain |
|---|---|---|
| [m00 — Skeleton](03-build/m00-skeleton.md) | [django/01](02-django/01-django-vs-flask.md), [django/02](02-django/02-settings-and-project-layout.md) | Split settings, `apps/` layout, why not one `settings.py` |
| [m01 — Services and health](03-build/m01-services-and-health.md) | [django/03](02-django/03-models-and-migrations.md), [django/05](02-django/05-the-django-admin.md), [concepts/03](01-concepts/03-secrets-at-rest.md) | Models, migrations, encrypted fields, a genuinely customised admin |
| [m02 — Connectors](03-build/m02-connectors.md) | [concepts/01](01-concepts/01-polling-and-reconciliation.md) | Abstracting a service's HTTP quirks behind a dataclass boundary |

---

## Phase 2 — The engine (m03–m05)

Where the real engineering is.

| Milestone | Detours | You will be able to explain |
|---|---|---|
| [m03 — Celery and polling](03-build/m03-celery-and-polling.md) | **[django/07](02-django/07-celery-and-beat.md)**, [concepts/02](01-concepts/02-scheduled-work-and-idempotency.md) | Beat, two queues, `.s` vs `.si`, `acks_late`, locking |
| [m04 — Library scanning](03-build/m04-library-scanning.md) | [django/04](02-django/04-orm-and-query-optimization.md) | Bulk upserts, chunking, long tasks that must not block fast ones |
| [m05 — Reconciliation](03-build/m05-reconciliation.md) | [concepts/01](01-concepts/01-polling-and-reconciliation.md) | The diff engine — **write the tests first here** |

**Checkpoint:** the system does something nothing else does. Do the
[system-design drill](06-interview/question-bank.md#the-system-design-drill).

---

## Phase 3 — Interfaces (m06–m08)

| Milestone | Detours | You will be able to explain |
|---|---|---|
| [m06 — DRF API](03-build/m06-drf-api.md) | [django/06](02-django/06-drf.md), [concepts/04](01-concepts/04-authorization-and-tenancy.md) | Serializers, viewsets, `get_queryset` filtering, why 404 not 403 |
| [m07 — Alerts](03-build/m07-alerts.md) | — | Webhook delivery, dedup, not spamming yourself at 3am |
| [m08 — Performance pass](03-build/m08-performance-pass.md) | [django/04](02-django/04-orm-and-query-optimization.md), [django/08](02-django/08-testing-django.md) | Finding and fixing N+1s **with numbers** |

---

## Phase 4 — The dashboard, twice

**The most valuable part of this project for full-stack roles.** You build the same dashboard
in two paradigms and can argue the trade-off from experience rather than opinion.

| Lesson | Focus |
|---|---|
| [04-frontend/README](04-frontend/README.md) | **Why build it twice** — read first |
| [04-frontend/01](04-frontend/01-django-templates-and-htmx.md) | Server-rendered: templates, HTMX, Alpine, a chart |
| [04-frontend/02](04-frontend/02-react-typescript-spa.md) | The same screens as a typed React SPA |
| [04-frontend/03](04-frontend/03-consuming-drf-from-react.md) | Auth, pagination, generated types, the API contract |
| [04-frontend/04](04-frontend/04-comparing-the-two.md) | **The write-up.** Measured, honest, and a genuine portfolio piece. |

> If you have done [Ferryman's frontend track](../../Ferryman/docs/09-frontend/), lessons 02–03
> here are mostly application rather than new learning — move faster and spend the time on 04.
> If you have not, do Ferryman's track first; it teaches React properly and this one assumes it.

---

## Phase 5 — Production (ops)

| Lesson | Focus |
|---|---|
| [05-ops/01](05-ops/01-production-deployment.md) | Compose, Caddy, Contabo, read-only mounts, zero-downtime |
| [05-ops/02](05-ops/02-monitoring-and-the-demo.md) | Sentry, `/healthz`, and a **public demo that does not expose your library** |

---

## Phase 6 — Interview (ongoing, not last)

[06-interview/question-bank.md](06-interview/question-bank.md) — drill from Phase 2 onward.

---

## Dependency graph

```
m00 ──> m01 ──> m02 ──> m03 ──> m04 ──> m05 ──┬──> m06 ──> m08 ──> ops
                                              │            │
                                              └──> m07     └──> frontend (×2)
```

---

## What "done" looks like

- [ ] Deployed on Contabo, TLS, running against your real services
- [ ] It has told you something about your own libraries you did not know
- [ ] Both dashboards built; the comparison write-up published
- [ ] N+1 fixes documented with before/after query counts
- [ ] 80%+ coverage, CI green
- [ ] A public demo instance seeded with fake data, `demo/demo`
- [ ] You can answer every question in the [bank](06-interview/question-bank.md) without notes
