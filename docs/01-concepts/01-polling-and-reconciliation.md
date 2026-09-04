# 01 — Polling and reconciliation

**Status:** contract — expand when taught
**Prereqs:** none
**Used by:** [m02](../03-build/m02-connectors.md), [m05](../03-build/m05-reconciliation.md)
**Time:** ~60 min

---

## Why this lesson exists

Kavita will not tell you when something changes. Neither will Komga or LANraragi. There are no
webhooks. So you ask, on a schedule, and compare against what you already knew — and the
comparison is the entire product.

---

## What you should be able to say afterwards

- When reconciliation is the right pattern and when events are better
- Why the diff, not the data, is the valuable output
- Why "could not fetch" must never be treated as "nothing there"
- How to make a poller cheap enough to run continuously

---

## Concepts to cover

1. **Events vs. reconciliation.** Events are cheap, immediate, and lossy — miss one and you
   drift forever. Reconciliation is expensive, delayed, and **self-healing**: it converges no
   matter what you missed. **When you cannot have events, this is not a compromise — it is the
   more robust of the two.** Kubernetes works this way for the same reason.
2. **The diff is the product.** Two inventories are not interesting. The set difference is.
   Design the data model around producing that difference cheaply.
3. **The categories.** `MISSING_IN_SERVICE`, `MISSING_ON_DISK`, `COUNT_MISMATCH`, `NO_COVER`,
   `STALLED_SCAN`, `EMPTY_SERIES`. **Derive these from real failures on your own box**, not
   from imagination. Each should map to something that has actually happened to you.
4. **⚠️ Absence versus failure — the dangerous one.** If a connector times out and you treat
   the empty result as the inventory, **every series is now "missing in service"** and you have
   generated hundreds of false alerts. Worse, if you ever added remediation, you would act on
   them. The connector must raise, not return `[]`. Make this an explicit type distinction,
   not a convention.
5. **Matching.** Disk folder `Solo Leveling (Official)` versus service series `Solo Leveling`.
   Normalise before comparing — and know that normalisation is where false matches come from.
   Keep it conservative: an unmatched pair is a visible discrepancy; a wrongly-matched pair is
   invisible.
6. **Poll cost.** Interval × services × API calls. Compute it. Per-service intervals so a
   cheap health check runs often and an expensive full inventory does not.
7. **Change detection.** Do not re-diff everything every time. `seen_at` timestamps and content
   hashes let you skip unchanged libraries.
8. **Flapping.** A service that is up-down-up produces three alerts. Require N consecutive
   failures before declaring it down. Same debounce idea as everywhere else.

---

## Exercise

1. On your real box, list every way a library can silently disagree with its reader. **Use
   real incidents.** That list is your discrepancy taxonomy.
2. Design the diff algorithm on paper. What is the complexity in terms of series count?
3. **Write the failing case first**: a connector that raises versus one that returns empty.
   Show that conflating them produces hundreds of false discrepancies. Fix it with distinct
   types.
4. Design the matching rule. Find two folder names in your library that would falsely match
   under a naive rule.
5. Compute poll cost per day at your intended intervals.
6. Design the flapping rule: how many failures before "down", how many successes before "up"?

---

## Done when

- [ ] The discrepancy taxonomy comes from real incidents
- [ ] Failure and absence are structurally distinguishable, with a test
- [ ] The matching rule is conservative and you know its false-positive case
- [ ] Poll cost per day is computed
- [ ] Flapping thresholds are decided

---

## Interview questions this unlocks

- "How would you detect changes in a system with no webhooks?"
- "What's the difference between event-driven and reconciliation-based design?"
- "Why might reconciliation be more robust than events?"
- "Your API call fails. How do you make sure that doesn't look like deleted data?"
- "How do you avoid alert flapping?"
