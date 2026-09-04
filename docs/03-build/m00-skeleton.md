# Milestone 00 — Skeleton

**Goal:** `docker compose up` brings up Postgres, Redis, and Django with split settings, six
apps, a `/healthz` endpoint, and CI running tests.

**Detours first:** [django/01 Django vs Flask](../02-django/01-django-vs-flask.md) ·
[django/02 Settings and project layout](../02-django/02-settings-and-project-layout.md)

**Sessions:** 2–3

> Get the boring infrastructure green on day one. Every project that leaves CI and Compose
> until "later" never does them.

---

## Design decisions to make and write down

1. **App boundaries.** `core`, `services`, `libraries`, `reconcile`, `alerts`, `api`,
   `dashboard`. Draw the dependency arrows. `core` depends on nothing; nothing depends on
   `dashboard`. **This graph is a decision, not a diagram** — you will enforce it with a test.
2. **`services.py` for business logic.** Write the rule down now, before there is any logic to
   misplace. Views, tasks, and API all call the same functions.
3. **`/healthz` semantics.** Does it check Postgres? Redis? Celery? What should it return when
   Redis is down but the app can still serve pages? Decide, because Compose health checks and
   your future monitoring both depend on the answer.
4. **RAM budget.** From the setup questions: four Python containers plus Postgres and Redis, on
   a box already running six media containers. **Write the number down.** It will constrain m03.

---

## Build

- `docker-compose.yml`: postgres, redis, web, with health checks and `service_healthy`
  ordering.
- `config/settings/{base,local,production,test}.py`, selected by `DJANGO_SETTINGS_MODULE`.
- `django-environ`; `.env.example` committed, `.env` ignored.
- Six apps under `apps/`, each with an explicit `AppConfig.name`.
- `/healthz` checking real dependencies.
- Structured JSON logging with a request ID.
- `pytest` + `pytest-django` configured; one passing test.
- GitHub Actions: `ruff`, `pytest`, with Postgres and Redis service containers.

---

## Break it

1. Delete a required env var. Confirm startup fails naming it — not a `KeyError` from deep in
   the stack.
2. Start `web` before Postgres is ready by removing the health-check condition. Watch it
   crash-loop. Restore it and understand what changed.
3. Stop Postgres. Confirm `/healthz` fails and says which dependency. Stop Redis instead.
   **Confirm the behaviour matches the decision you wrote down** — if you said "degrade", it
   should degrade.
4. Run with `production` settings locally. Run `manage.py check --deploy`. Fix everything and
   **be able to explain each item**.
5. Make `apps/core` import from `apps/services`. **Write the test that catches it.** This is
   the enforcement, not the code review.
6. Break CI deliberately, confirm it goes red, fix it.
7. Measure actual RAM of the running stack. Compare against your budget.

---

## Done when

- [ ] One command brings up the whole stack
- [ ] Split settings; no `if DEBUG` in application code
- [ ] Six apps with the dependency graph drawn **and enforced by a test**
- [ ] `/healthz` behaves as designed under each dependency failure
- [ ] `check --deploy` clean and understood
- [ ] CI green
- [ ] Measured RAM recorded against budget
- [ ] Committed: `chore(m00): project skeleton with compose, split settings, CI`

---

## Interview connection

- *"How do you structure a large Django project?"*
- *"How do you manage settings across environments?"*
- *"What does your health check actually check?"*
- *"How do you enforce an architectural boundary?"* — a test. Strong answer.

---

**Next:** [m01 — Services and health](m01-services-and-health.md)
