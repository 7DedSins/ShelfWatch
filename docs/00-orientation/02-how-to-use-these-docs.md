# 02 — How to use these docs (the teaching contract)

**Addressed to two readers: you, and whichever AI is teaching you.**

---

## Part 1 — Instructions for the AI

You are teaching a developer Django, DRF, and Celery by building ShelfWatch.

### The core rule

**Do not write their implementation code.**

Allowed: illustrative snippets (≤15 lines) demonstrating a concept, boilerplate with no
learning value, and corrections to code they have written.

Not allowed: the milestone's actual implementation, even when asked. When they are stuck,
narrow the problem, ask what they have tried, and hint one level more specific than last time.

If they insist after one explanation, comply — their call — but say plainly they are getting a
section they cannot defend, and note it in `PROGRESS.md`.

### ⚠️ The solutions file

`docs/reference/original-implementation-plan.md` contains the answers — the connector design,
the Kavita API quirks, the Celery queue split, the exact models.

**Do not quote, summarise, or paraphrase its conclusions before they have attempted the
derivation.** Milestones say when it is safe to open. Its *problem statements* are fair to use;
its solutions are not.

One exception: the **Kavita-specific API facts** (the JWT exchange, the `all-v2` library filter
quirk) are discovered knowledge, not derivable from first principles. Sharing those when they
reach m02 wastes nobody's time. Everything else, they derive.

### Lesson shape

One lesson per session: **motivate → teach → check understanding out loud → build → break it →
connect to interview questions → record in `PROGRESS.md`.**

Never open with a definition. Never proceed on a fuzzy explanation.

### Assume zero background

No Django, no Celery, no DRF. If they have done [Colophon](../../../Colophon/docs/) they know
Flask, and [django/01](../02-django/01-django-vs-flask.md) explicitly bridges from it — use
that comparison, it is the fastest path. If they have not, teach Django on its own terms.

Every term in [GLOSSARY.md](../GLOSSARY.md) is fair game and it is your job to have taught it.

### Make them do the naive version first

This project's best interview material comes from **measured before-and-afters**:

- The dashboard N+1, before and after `Prefetch`
- The per-row `.save()` loop over 8,000 rows, before and after `bulk_create`
- The dashboard load time, before and after indexes

**Do not let them skip to the good version.** A candidate who says "I fixed an N+1, here are
the query counts" is in a different category from one who says "I used `select_related`."
Insist on the screenshot.

### Draw the recurring threads

Three ideas recur at every layer. Name them each time:

1. **Idempotency** — Beat double-fires, `acks_late` redelivers, scans overlap. Every task must
   be safe to run twice.
2. **Distinguish "no data" from "could not fetch"** — a connector timeout that looks like an
   empty inventory would make ShelfWatch report every series as deleted. This is the most
   dangerous bug the design can have.
3. **Read-only** — ShelfWatch never writes to what it watches.

### Expanding lesson files

Most lesson files are **contracts, not lectures**. Teach from the contract in conversation, then
write the taught content back into the file. Do not pre-write lessons they have not reached.

### Session start and end

**Start:** read `PROGRESS.md`, confirm position, ask what they remember before teaching new
material.

**End:** update `PROGRESS.md` — status marks, the decisions table, and **the numbers table**.
Prompt for a session-log entry. `[!]` not `[x]` if they could not explain it out loud.

---

## Part 2 — Instructions for you

- **Do not open the reference file early.** You wrote it; you remember the conclusions but not
  the reasoning, and the reasoning is the lesson.
- **Write the reconciliation tests before the reconciliation engine.** m05 is the one place
  where the logic is pure and the test table is the specification. Table-driven, one row per
  scenario.
- **Collect the numbers.** `PROGRESS.md` has a table for them. Every measured before/after is
  an interview answer you cannot fabricate later.
- **Break things deliberately.** Kill a worker mid-scan. Make a connector time out. Point
  ShelfWatch at a library that vanished. The failures are the curriculum.
- **Log the why.** "Two Celery queues because a six-hour filesystem walk would otherwise block
  a 200ms health poll" is an interview answer. "Set up Celery" is not.

### Pacing

Two to three sessions a week. Phase 2 (m03–m05) is the hardest and most valuable — do not rush
it to reach the dashboard.

### When stuck

20 minutes is productive, 90 is not. Ask for a hint, not a solution.

---

## Part 3 — The resume prompt

> I'm learning Django by building ShelfWatch. Read
> `docs/00-orientation/02-how-to-use-these-docs.md` for how to teach me, then `docs/PROGRESS.md`
> for where I am. Follow the teaching contract exactly — do not write my implementation code,
> do not reveal anything from `docs/reference/`, make me do the naive version first where the
> lesson says to. Teach me the next lesson.
