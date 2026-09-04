# Agent surface — a proposal, not yet curriculum

**Status: proposed. Nothing here is committed to [CURRICULUM.md](CURRICULUM.md), and no
milestone depends on it.** It is written so the decision can be made once, deliberately,
rather than re-made badly every time an "add AI" impulse arrives.

This file poses the design decisions. It deliberately does not answer them — the same rule
as everywhere else in this folder ([teaching contract](00-orientation/02-how-to-use-these-docs.md)).

---

## 1. Where ShelfWatch stands today

Audited across all 38 files in this folder: **there is no agent, MCP, or LLM capability, and
no lesson mentions one.** The only occurrences of "AI" are instructions to whichever AI is
teaching you.

That is not an oversight to apologise for. It is the correct state for milestones 00–08,
and the argument below is for *one* addition after them — not a retrofit of the spine.

---

## 2. The thesis

> **Be legible to agents. Do not contain an LLM.**

The market moved toward agents; the naive read of that is to bolt a chat box onto a
monitoring tool. That is the version to refuse. Two reasons, both stated plainly so they can
be argued with:

- **The box cannot host inference.** [Prospect's CONTEXT.md](../../Prospect/CONTEXT.md) §7 —
  no GPU, no self-hosted models. Every LLM feature calls a hosted API and carries a
  per-call cost, forever, on a project with no revenue.
- **The honest counterpoint.** A METR study (via
  [RESEARCH-2026-09.md](../../Prospect/RESEARCH-2026-09.md) §2, confidence **[M]**) found
  experienced developers using AI tools took **19% longer** while believing they were 20%
  faster. An LLM wrapped around a tool that already answers the question precisely is
  usually a downgrade.

What is *not* a downgrade is being the thing an agent can safely call. ShelfWatch is
unusually well-shaped for that, for reasons that already exist in the codebase.

---

## 3. Proposal A — an MCP server over the existing service layer

### Why this is load-bearing rather than decorative

**It tests an architectural claim you already made.** [README.md](README.md) states that
business logic lives in `services.py`, is "reusable by the API and the dashboard, and does
not care how it was invoked." An MCP server is a *third* caller. If the claim is true,
adding it changes no business logic. If it is false, you find out here — which is the
useful outcome either way.

> *"I added a third protocol surface and touched zero business logic"* is a stronger
> interview sentence than any description of a design pattern, because it is falsifiable
> and the diff proves it.

**Read-only by design is already true, and it is the whole safety story.** [README.md](README.md)
commits ShelfWatch to never writing to the services it watches and never deleting anything.

That matters more in an MCP context than anywhere else. Blast radius is the hard problem in
MCP servers: a vendor scan of five popular open-source MCP servers found issues in **all
five** ([RESEARCH-2026-09.md](../../Prospect/RESEARCH-2026-09.md) §2, **[M]**), including a
browser-automation server exposing an `evaluate` tool that accepted raw JavaScript with no
sandboxing — CVSS 9.8, reachable by prompt injection.

ShelfWatch is structurally incapable of that class of bug. So the answer to *"how do you
stop prompt injection from doing damage through your tools?"* is an argument about what the
code cannot do, not a promise about what it will not do. Very few candidates can offer the
first kind.

### The data is already question-shaped

The deltas this system computes are what people ask in sentences:

| Question a human actually asks | Comes from |
|---|---|
| What is on disk that Kavita never indexed? | m05 reconciliation |
| What does the reader still list whose files have vanished? | m05 reconciliation |
| What has been "scanning" for more than an hour? | m01 + m03 |
| Where do Komga and the filesystem disagree about this series? | m05 |
| Which services are unhealthy, and since when? | m01 |

### The decisions to derive — not to be handed

These are the interesting part, and the reason this file does not contain a tool list:

1. **Granularity.** Five narrow tools, or one query tool with parameters? Narrow tools are
   easier for a model to pick correctly and harder to misuse; a general one is fewer moving
   parts and degrades less badly on questions you did not anticipate. There is a real
   trade-off here and interviewers ask about it.
2. **Tools vs resources.** A reconciliation report is arguably a *resource* (a document the
   client reads) rather than a *tool* (an action it invokes). Getting this boundary right is
   most of MCP design.
3. **Pagination and truncation.** A library with 4,000 series does not fit in a context
   window. What does the tool return when the answer is large — and how does the model know
   it was truncated? Answering "silently truncate" is how agents fail quietly.
4. **Auth and tenancy.** m06 already establishes object-level permissions. Does the MCP
   surface inherit them, or is it single-user by construction? Say which, and why.
5. **Error shape.** A tool that returns a stack trace teaches the model to retry forever.

### Cost

| | |
|---|---|
| RAM | **~64 MiB estimated.** The comparable `docforge-mcp` container measures 54 MiB in [CONTEXT.md](../../Prospect/CONTEXT.md) §3. This figure is arithmetic by analogy, not a measurement of ShelfWatch — measure it before believing it. |
| New containers | One. It gets a `mem_limit` like everything else ([05-ops/01](05-ops/01-production-deployment.md)). |
| New ports | None. A Caddy route, per the same doc. |
| Ongoing | Low. The tools are thin; the service layer is already tested. |

⚠️ The RAM budget in [05-ops/01](05-ops/01-production-deployment.md) is already the tightest
constraint in this project — six containers against roughly 1.5 GiB free. Adding a seventh is
only honest *after* the deployed footprint has been measured, not estimated.

### Where it slots

After [m06](03-build/m06-drf-api.md), which is where the service-layer boundary becomes real.
It is genuinely parallel to [m07](03-build/m07-alerts.md) — both are consumers of the same
engine — and it must not displace [m08](03-build/m08-performance-pass.md), because "I found
and fixed N+1s with numbers" beats "I added an MCP server" in every interview that is not
specifically about agents.

```
m05 ──> m06 ──┬──> m07 (alerts)
              ├──> m08 (performance) ──> ops
              └──> m09 (agent surface)   <-- proposed
```

---

## 4. Proposal B — evals for your own tools

The smaller addition, and the one almost nobody's portfolio has.

[RESEARCH-2026-09.md](../../Prospect/RESEARCH-2026-09.md) §2 names evals as the weakest link
in the whole agent stack (**[M]**): most prototypes have zero, only ~37% of organisations run
online evaluation, and 86–89% of agent pilots stall before production on operational
readiness rather than on model quality.

**Shape:** thirty real phrasings of the questions in §3, a scoring script, run in CI. Two
things being measured:

- **Tool selection.** Given the phrasing, does the model call the right tool with the right
  arguments? This is a classification problem with a fixture file, not a research project.
- **Grounding.** Does it invent a series name that is not in the response? Answer keys come
  from the same database the tools read, so this is checkable exactly.

**Cost:** thirty calls per run against a hosted API — cents, not dollars — which is what
makes it viable on a project with no budget. Pin the model version, or the suite measures
drift you did not cause.

**Why it is worth more than it looks:** it converts "I built an MCP server" into "I measured
whether it works, and here is the number." That is the same move as the N+1 before/after
screenshot in m08, applied to a domain where most people have no number at all.

---

## 5. Deliberately not building

Recorded so these stay decided.

| Idea | Why not |
|---|---|
| Chat interface over the library | The precise question already has a precise answer. An LLM in the path adds latency, cost and a failure mode, and removes determinism. |
| LLM-generated "summaries" of scan results | A reconciliation delta is already the summary. This is the padding an interviewer spots. |
| Embedding-based fuzzy series matching | Genuinely tempting — matching disk names to service names is the real hard problem — but it needs a model on a box with no GPU and ~1.5 GiB free. `rapidfuzz` on CPU is the honest first answer, and it is not an agent feature. Revisit only if deterministic matching demonstrably fails. |
| Any tool that writes to a watched service | Breaks the read-only guarantee, which is the entire safety argument. Non-negotiable. |
| Agent that "fixes" detected problems | Same, plus it fights the guardrails in `Contabo/README.md` §3. |

---

## 6. What this buys in an interview

The specific questions it lets you answer from experience rather than reading:

- How do you expose an existing system to an agent without widening its blast radius?
- What is the difference between an MCP tool and an MCP resource, and how did you decide?
- How does your tool behave when the honest answer is 4,000 rows?
- How do you know your tool descriptions are good? *(Almost nobody can answer this one.)*
- Why did adding a third protocol surface not require changing your business logic?

Add them to [06-interview/question-bank.md](06-interview/question-bank.md) only once the work
is done — an unanswerable question in your own bank is worse than an absent one.

---

## 7. Risks, honestly

- **Scope creep against the spine.** Milestones 00–08 plus the dashboard built twice already
  run 14–18 weeks at 8 hours a week. This is a tenth milestone, not a free addition.
- **MCP is young.** The specification moves. A tool surface written today may need revising,
  and that is a maintenance cost on a project whose value is being deployed and stable.
- **It could read as trend-chasing** if the rest of the repo is thin. It only works as the
  *last* thing on a system that already reconciles real libraries in production. Built
  earlier, it is exactly the padding §5 rejects.
- **The RAM may simply not be there.** See §3. Measurement decides this, not enthusiasm.

---

## 8. Open questions for the operator

1. Is the goal here interview material, or a tool you will actually use? They point at
   different granularities in §3, decision 1.
2. Does the public demo instance ([05-ops/02](05-ops/02-monitoring-and-the-demo.md)) expose
   the MCP surface too? If yes, the auth question in §3 stops being theoretical.
3. If [Prospect's Assay](../../Prospect/portfolio/05-assay/) ever happens, this becomes its
   first test subject — a real MCP server you control, with a known-good safety property to
   verify against. Worth knowing before designing either one.

---

## What "done" would look like

- [ ] Footprint **measured** after deployment, and the seventh container justified against it
- [ ] The five decisions in §3 answered on paper, with reasons, before any code
- [ ] MCP surface added with **zero diff** to `services.py` — or a written explanation of why that was impossible
- [ ] Truncation behaviour explicit and tested with a library larger than a context window
- [ ] Eval suite in CI with a number, not a vibe
- [ ] Two entries in `PROGRESS.md` carrying a decision, a reason, and a measurement
