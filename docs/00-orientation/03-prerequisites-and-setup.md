# 03 — Prerequisites and setup

**Time:** one session. Do not start m00 until `docker compose ps` is green.

---

## What you need to already know

| Skill | Level |
|---|---|
| Python | Comfortable. Classes, decorators, virtualenvs. |
| Terminal | Can navigate and read errors. |
| Git | Branches and commits. |
| SQL | Helpful. Taught where needed. |
| Flask | Optional. If you have it, [django/01](../02-django/01-django-vs-flask.md) bridges quickly. |

### What you do **not** need

Django, DRF, Celery, Redis, Postgres, Docker, React. All taught from zero.

---

## Local environment

**Python 3.12+**, **Docker Desktop**, and an editor with a Python language server.

Everything runs in Compose — Postgres, Redis, web, worker, beat. Nothing installed natively.

---

## The repository

```bash
cd "/d/Github Projects/ShelfWatch"
git init
git add docs
git commit -m "Add ShelfWatch learning curriculum"
```

Public repo. This one is the flagship — the commit history over four months is itself evidence.

---

## Contabo access

This project targets your real infrastructure, which is what makes the demo credible. Confirm
you can reach it before Milestone 02:

```bash
ssh media@100.109.106.14
docker ps
```

If Tailscale is down, the public-IP fallback is documented in your Contabo notes.

### ⚠️ Standing rules for this project

From your Contabo guardrails, and they are absolute:

1. **ShelfWatch is read-only.** It never writes to Kavita, Komga, LANraragi, or the filesystem
   it scans. Library paths are mounted `:ro` into the scan workers — both correct and a nice
   thing for a reviewer to notice.
2. **Never delete anything from PikPak.** ShelfWatch only *reads* the mount. There should be no
   code path capable of a delete — not disabled, absent.
3. **Do not restart the rclone mount or the media containers** as part of anything ShelfWatch
   does. If a scan finds a stale mount, it **reports** that — it does not fix it. The full
   six-container restart procedure is a human decision.
4. **API keys never go in the repo.** Kavita and LANraragi both have permanent `vps-automation`
   keys; retrieve them from the running instances at runtime. Stash has none — ask for it each
   session. Never commit a value, never write a derived token to disk.

Rule 3 is worth dwelling on: **a monitoring tool that takes remedial action is no longer a
monitoring tool.** It is an automation tool with a much larger blast radius. Keep the boundary.

---

## Setup task

Your first work, unassisted:

1. `docker-compose.yml` with **postgres**, **redis**, and a placeholder **web** service.
   Named volumes for Postgres. Health checks on both backing services.
2. `pyproject.toml` with Django 5, DRF, Celery, `django-environ`, plus `pytest`,
   `pytest-django`, `factory_boy`, `respx`, `ruff` as dev dependencies.
3. `.env.example` committed; `.env` gitignored.
4. Verify:
   ```bash
   docker compose up -d
   docker compose ps                                 # both healthy
   docker compose exec postgres psql -U <user> -d <db> -c "SELECT version();"
   docker compose exec redis redis-cli PING          # PONG
   ```
5. Stop and restart everything. Confirm Postgres data survived.

**Questions to answer before moving on:**

1. What does the named volume do, and what breaks without it?
2. Why does the web service need `depends_on: condition: service_healthy` rather than plain
   `depends_on`? What actually goes wrong without it?
3. You will run **four** Python containers eventually (web, worker-default, worker-scans, beat).
   On a 6 GB VPS also running Kavita, Komga, LANraragi, Stash, and two nginx proxies — **what is
   your memory budget?** Write it down now. This constraint will shape real decisions in m03
   and again at deployment.

Question 3 is not busywork. The two-queue design in m03 costs you a whole extra container, and
you should know what that costs before you commit to it.

---

**Next:** [Milestone 00 — Skeleton](../03-build/m00-skeleton.md)
