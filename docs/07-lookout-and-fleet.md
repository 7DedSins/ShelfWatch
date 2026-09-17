# Lookout and the full-fleet slice

**Status:** pointer. The detailed contract lives in
[Lookout `docs/07-fleet/`](../../Lookout/docs/07-fleet/README.md).
Nothing here is on the Django spine (m00–m08). Do not start it
because a Lookout session is enthusiastic.

Lookout is the Android client of this API
([`D:\Github Projects\Lookout`](../../Lookout/)). v1 consumes
services, discrepancies, poll/scan, and (m04) host/docker
**snapshots**. That is still read-only aside from acknowledge and
queued poll/scan.

---

## What this repo must grow if the phone (and admin) watch the *whole* box

Sourced from [Contabo](../../Contabo/README.md), not from imagination.

| Slice | ShelfWatch work | Lookout work |
|---|---|---|
| JWT + OpenAPI | m06 remainder | m01 |
| Host/docker GET snapshots | observer + `GET /api/host/latest/` | m04 |
| **Fleet** (FUSE, systemd/cron/timers, Redis/Celery/Beat, Tailscale, every container including future ones, Stash ping) | new app `apps.fleet` | Phase 7 screens |
| **Allowlisted actions** (`remount_fuse`, `rebind_fuse_consumers`) | worker + lock + audit + cooldown shared with `pikpak-fuse-health.timer` | confirm UI, staff-only |
| Stash inventory connector | **last**, after Kavita+LRR engine; GraphQL ≠ series ABC | fleet can show container+ping earlier |

Django admin, templates, React SPA, and Lookout **share one JSON**
(`GET /api/fleet/latest/`). Do not compute "FUSE ok" in a template
and again in Kotlin.

---

## Rules that do not move

- The phone still never sees `docker.sock`, SSH, or PikPak.
- Failed FUSE/connector fetch still must not look like empty
  inventory (m05).
- Demo instance: actions disabled.
- Remount is Contabo §3.4: rclone **then** every discovered FUSE
  consumer — not a hardcoded six, not `docker restart kavita` alone.
- Never unmount if `findmnt` still says `fuse.rclone` (2026-09-10).
- This is **not** an MCP "fix it" tool.
  [AGENT-SURFACE.md](AGENT-SURFACE.md) §5 still refuses agent
  remediation. Fleet actions are a human with a confirm token.

Implement from
[Lookout `07-fleet/02-django-changes.md`](../../Lookout/docs/07-fleet/02-django-changes.md)
when Phase 7 is granted. Log hours in this `PROGRESS.md`, not only
Lookout's.

---

## Teaching

Same contract as [00-orientation/02](00-orientation/02-how-to-use-these-docs.md).
`apps.fleet` is a ShelfWatch milestone (or a small chain), taught
here. Lookout only generates types and draws screens.
