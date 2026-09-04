# Build milestones — the spine

Nine milestones. Each produces a working, committed, deployable increment.

---

## The shape of every milestone

| Section | What it does |
|---|---|
| **Goal** | One sentence. |
| **Detours** | Concept and Django lessons to take first. |
| **Design decisions** | Answer and **write down** before coding. These become interview answers. |
| **Build** | What to implement, at the level of behaviour. |
| **Break it** | Deliberate failure exercises. **The most valuable section.** |
| **Done when** | A checklist. |
| **Interview connection** | What this lets you claim. |

---

## The milestones

| # | Milestone | Produces |
|---|---|---|
| [m00](m00-skeleton.md) | Skeleton | Compose stack, split settings, six apps, CI green |
| [m01](m01-services-and-health.md) | Services and health | Models, encrypted keys, a real admin |
| [m02](m02-connectors.md) | Connectors | The abstraction reviewers notice first |
| [m03](m03-celery-and-polling.md) | Celery and polling | Two queues, Beat, locks, health history |
| [m04](m04-library-scanning.md) | Library scanning | Bulk upserts, long tasks, storage snapshots |
| [m05](m05-reconciliation.md) | Reconciliation | **The product.** The diff engine. Tests first. |
| [m06](m06-drf-api.md) | DRF API | Serializers, viewsets, authz matrix, OpenAPI |
| [m07](m07-alerts.md) | Alerts | Webhook delivery, dedup, no 3am spam |
| [m08](m08-performance-pass.md) | Performance pass | N+1s killed **with numbers** |

**Milestones 00–06 are a complete backend.** m05 is where the product exists.

---

## Rules

**Commit at every milestone.** `feat(m03): two-queue Celery with per-library locking`.

**Do the naive version first** where a milestone says to. The measured before/after is the
artifact — "I fixed an N+1" is a claim; "1,247 queries down to 4, here are the screenshots" is
an answer.

**Do not skip "Break it".**

**Collect the numbers.** [PROGRESS.md](../PROGRESS.md) has a table. Fill it in as you go; you
cannot reconstruct them later.

**⚠️ Do not open `docs/reference/original-implementation-plan.md`** until a milestone says so.

**Read-only, always.** No milestone in this project writes to a watched service or deletes
anything. If you find yourself designing a remediation feature, stop — that is a different
product with a much larger blast radius.

---

## Rough pacing

| Milestones | Sessions | Weeks at 2–3/wk |
|---|---|---|
| m00–m02 | 7–9 | 3 |
| m03–m05 | 9–12 | 4 |
| m06–m08 | 7–9 | 3 |
| frontend ×2 | 10–14 | 5 |
| ops | 3–4 | 1 |

Phase 2 (m03–m05) is the hardest and the most valuable. Do not rush it to reach the dashboard.
