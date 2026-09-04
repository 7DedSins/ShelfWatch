# 04 — The ORM and query optimisation

**Status:** contract — expand when taught
**Prereqs:** [03-models-and-migrations.md](03-models-and-migrations.md)
**Used by:** [m04](../03-build/m04-library-scanning.md), [m08](../03-build/m08-performance-pass.md)
**Time:** ~90 min

> **The highest-value Django lesson for interviews.** "Tell me about an N+1 you fixed" is asked
> constantly, and an answer with query counts in it beats an answer with vocabulary in it.

---

## Why this lesson exists

The ORM makes slow code look identical to fast code. `service.latest_health.ok` in a template
loop is one line and one hundred queries. You will not see it until you measure.

---

## What you should be able to say afterwards

- What an N+1 is, how to *find* one, and how to fix it
- The difference between `select_related` and `prefetch_related`, precisely
- Why bulk operations are not a micro-optimisation here
- How to read a Django query plan

---

## Concepts to cover

1. **Laziness.** A queryset does nothing until evaluated. Know exactly what evaluates it:
   iteration, `len()`, `bool()`, slicing with a step, `list()`. Not `.filter()`, not
   `.order_by()`, not slicing without a step.
2. **N+1, caused deliberately.** Render the service list with a `latest_health` lookup per row.
   **Install `django-debug-toolbar` and look at the query count.** The number is the lesson.
3. **`select_related`** — a SQL join, for forward `ForeignKey` and `OneToOne`. One query.
   **`prefetch_related`** — a second query plus in-Python joining, for reverse FKs and
   many-to-many. Using the wrong one silently does nothing.
4. **`Prefetch` with a sliced queryset** — "the latest health check per service" is the hard
   case, because you cannot slice inside a normal prefetch. Two solutions: a `Prefetch` with a
   filtered queryset, or **denormalise** `Service.last_health_ok`, updated by the poll task.
   **Denormalisation is the right answer here** — work out why (the dashboard reads constantly,
   the poll writes rarely) and be able to defend the duplication.
5. **`only()` / `defer()` / `values()`.** Fetch fewer columns. Matters when a row has a large
   `JSONField` you do not need.
6. **Aggregation.** `annotate` and `aggregate`. Counting in the database instead of in Python.
   `Count`, `Sum`, `Max`, with `filter=` for conditional aggregates.
7. **Bulk operations — not a micro-optimisation.** 8,000 `DiskItem` rows with a `.save()` loop
   is 8,000 round trips: **minutes**. `bulk_create(..., update_conflicts=True,
   unique_fields=[...], update_fields=[...])` in chunks of 1,000: **seconds**. Measure both.
   This is the difference between a scan that works and one that does not.
8. **Chunking.** `iterator(chunk_size=...)` for reading large querysets without loading
   everything into memory. Relevant on a 6 GB box.
9. **Transactions.** `atomic()`, and why holding one across a long filesystem walk is bad —
   it blocks vacuum, holds locks, and grows the WAL.
10. **Reading the plan.** `str(qs.query)` for the SQL, `EXPLAIN ANALYZE` for the plan. Sequential
    scan versus index scan, and when a sequential scan is actually correct.

---

## Exercise

1. Install `django-debug-toolbar`. Build the dashboard naively. **Screenshot the query count.**
2. Fix it with `select_related` / `prefetch_related`. Screenshot again.
   **Both screenshots go in the README.** This is a portfolio artifact.
3. Tackle "latest health check per service". Try `Prefetch` with a sliced queryset. Then
   denormalise. Compare, and write down which you shipped and why.
4. Insert 8,000 `DiskItem` rows with a `.save()` loop. **Time it.** Then with chunked
   `bulk_create`. Time it. Record both in `PROGRESS.md`.
5. Use `update_conflicts=True` to make the upsert idempotent. Run the same scan twice; confirm
   no duplicates.
6. Write the storage-over-time query with `annotate`. Compare against doing it in Python.
7. Load 100,000 rows without `iterator()` and watch memory. Then with it.
8. Take your slowest query and `EXPLAIN ANALYZE` it. Add an index. Compare plans, not just
   times.

---

## Done when

- [ ] Before/after query-count screenshots exist
- [ ] You solved the latest-per-group problem two ways and chose deliberately
- [ ] Bulk vs. loop timings recorded
- [ ] Upserts are idempotent, proven by a repeat run
- [ ] You have read a real query plan and changed it
- [ ] No long-running transaction wraps a filesystem walk

---

## Interview questions this unlocks

- "**What's an N+1 query? How did you find yours?**" — with numbers.
- "`select_related` or `prefetch_related` — when each?"
- "How do you get the latest related row per parent?" — a genuinely hard ORM question.
- "When would you denormalise?"
- "How do you insert 10,000 rows efficiently?"
- "When is a sequential scan fine?"
