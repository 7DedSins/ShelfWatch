# Milestone 04 — Library scanning

**Goal:** walk each library path, record what is actually on disk, and do it fast enough that a
scan over 8,000 series is minutes rather than hours.

**Detours first:** [django/04 The ORM and query optimisation](../02-django/04-orm-and-query-optimization.md)

**Sessions:** 3

---

## Design decisions to make and write down

1. **Granularity.** One `DiskItem` per **series folder**, not per file. Counts, total bytes,
   newest mtime. A row per chapter would be hundreds of thousands of rows for no extra insight
   — but be able to say what you lose by aggregating.
2. **Deletion detection via `seen_at`.** The scan stamps every row it touches with the scan
   start time. Rows with an older `seen_at` were deleted on disk. **Elegant — "what
   disappeared" becomes a query rather than a set difference held in memory.**
3. **Bulk upserts.** `bulk_create(update_conflicts=True, unique_fields=["library",
   "relative_path"], update_fields=[...])`, chunked at ~1,000. **Do the `.save()` loop first
   and time it.** The difference is not a micro-optimisation, it is the difference between a
   feature and an unusable one.
4. **Transactions.** Do **not** wrap a 45-minute filesystem walk in one transaction. Commit per
   chunk. What does that mean for a scan that fails halfway? (Partial data with a partial
   `seen_at` — decide whether that is acceptable and how the next scan repairs it.)
5. **⚠️ FUSE realities.** Your paths are an rclone mount over PikPak. `os.walk` there is a
   network call per directory. Every stat is a round trip. A scan that is fast locally may take
   hours on the mount. **Measure on the real mount, not on your laptop.**
6. **Hangs.** A FUSE call can block in kernel `D` state indefinitely — a real, documented
   incident on your box. `soft_time_limit` on the task, or a scan hangs a worker forever.
7. **`StorageSnapshot`.** One append-only row per scan for the chart. Not derived from
   `DiskItem` history.
8. **Chaining.** `chain(scan_library.s(id), reconcile_library.si(id))` — **`.si`, not `.s`**.
   Hit the bug first if you have not already.

---

## Build

- `apps/libraries/models.py` — `Library`, `DiskItem`, `StorageSnapshot`, unique constraints.
- `scan_library(library_id)` on the **`scans` queue**.
- The walk: directory tree → aggregate per series → chunked bulk upsert → stamp `seen_at`.
- `soft_time_limit` and `time_limit` on the task.
- A per-library Redis lock, timeout tuned to real scan durations.
- `schedule_scans()` Beat entry, fanning out due libraries.
- `StorageSnapshot` written once per scan.
- Tests against a real `tmp_path` tree, including a deleted-file case.

---

## Break it

1. **Time the naive version.** 8,000 rows with a `.save()` loop. Then chunked `bulk_create`.
   **Record both numbers in [PROGRESS.md](../PROGRESS.md).** This is one of your best interview
   numbers.
2. Run the same scan twice. Confirm no duplicates — the upsert is idempotent.
3. Delete a folder on disk, rescan, and confirm the stale row is detectable by `seen_at`.
4. **Scan a real library on the FUSE mount.** Time it. Compare against the same tree copied
   locally. The ratio will surprise you and it belongs in your notes.
5. Wrap the whole scan in one transaction. Run it against a large library. Observe the lock
   duration and what it does to concurrent queries. Remove it.
6. Kill the worker mid-scan. Confirm partial data plus a partial `seen_at`, and confirm the
   next scan repairs it rather than compounding the mess.
7. Make a scan hang (point at a stalled mount, or simulate it). Confirm `soft_time_limit` fires
   and the worker recovers rather than being lost.
8. Build the chain with `.s`. Read the error. Switch to `.si`.
9. Run a scan while a health poll is due. **Confirm the poll is unaffected** — the payoff for
   m03's two queues.
10. Load 200,000 `DiskItem` rows and query "series in this library". `EXPLAIN ANALYZE`. Index.
    Compare.

---

## Done when

- [ ] Bulk vs. loop timings recorded
- [ ] Scans idempotent, proven by a repeat run
- [ ] Deletion detected via `seen_at`
- [ ] **Measured on the real FUSE mount**, not just locally
- [ ] No long-running transaction
- [ ] Mid-scan crash recovers on the next run
- [ ] A hung scan is time-limited and the worker survives
- [ ] Health polls unaffected during a long scan
- [ ] Committed: `feat(m04): library scanning with chunked bulk upserts`

---

## Interview connection

- *"How do you insert 10,000 rows efficiently?"* — with timings.
- *"How do you detect deletions without storing a diff?"* — `seen_at`.
- *"Why not wrap the whole job in a transaction?"*
- *"What happens if a task hangs?"*
- *"What's the difference between `.s` and `.si`?"*
- *"How do you stop a long job blocking short ones?"* — demonstrated end to end.

---

**Next:** [m05 — Reconciliation](m05-reconciliation.md)
