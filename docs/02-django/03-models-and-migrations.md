# 03 — Models and migrations

**Status:** contract — expand when taught
**Prereqs:** [02-settings-and-project-layout.md](02-settings-and-project-layout.md)
**Used by:** [m01](../03-build/m01-services-and-health.md)
**Time:** ~75 min

---

## Why this lesson exists

The schema is where the interesting failures live. Django makes models pleasant enough that
people skip thinking about constraints and indexes — and then wonder why the dashboard takes
nine seconds.

---

## What you should be able to say afterwards

- Why a database constraint beats validation in code
- How Django migrations work and what autogenerate misses
- How to add a column to a large live table without locking it
- When a `JSONField` is right and when it is laziness

---

## Concepts to cover

1. **Abstract base models.** `TimeStampedModel` with `created_at`/`updated_at`, inherited
   everywhere. `abstract = True` means no table of its own.
2. **The schema.** `Service`, `HealthCheck`, `Library`, `DiskItem`, `Discrepancy`,
   `StorageSnapshot`. **Design it yourself from the access patterns before looking at anything.**
3. **Constraints over validation.** `UniqueConstraint(fields=["owner", "name"])` in
   `Meta.constraints`. A `clean()` method is advisory — it does not run on `bulk_create`, it
   does not run on `update()`, and it does not protect you from a second process. **The
   database is the only thing that is actually enforced.** This is the sentence to remember.
4. **Indexes, deliberately.** `Index(fields=["service", "-created_at"])` for "latest health
   check per service". Add them **after** you have a slow query, not speculatively — and every
   index costs write performance.
5. **`JSONField`, honestly.** Right for genuinely per-type configuration where the shape varies
   by service kind. **Wrong** as a place to avoid designing a schema. If you find yourself
   querying inside it constantly, those should have been columns.
6. **`StorageSnapshot` — a design lesson.** Storage-over-time comes from a small append-only
   table written once per scan, **not** derived from `DiskItem` history. Cheap to write, cheap
   to chart, and it does not couple your history to your current-state table. Make them try the
   derived version first and feel why it is wrong.
7. **`seen_at` for soft deletion.** A scan sets `seen_at` on every row it touches; rows with an
   older `seen_at` were deleted on disk. Elegant, and it makes "what disappeared" a query rather
   than a diff.
8. **Migrations.** `makemigrations` / `migrate` / `sqlmigrate` to see the SQL. **Read every
   generated migration.** Autogenerate frequently misses index and constraint changes, and
   silently.
9. **Zero-downtime schema change.** Adding a `NOT NULL` column to a large live table takes a
   lock. Expand/contract: add nullable → backfill in batches → start writing → add the
   constraint → remove the old. This separates people who have run a production database from
   people who have not.
10. **Data migrations.** `RunPython` with a reverse function. Never import a model directly —
    use `apps.get_model()`, because the model's *current* code does not match the migration's
    point in history.

---

## Exercise

1. Design the schema from the access patterns. Justify every table, field, and relationship.
2. Implement it. `sqlmigrate` the initial migration and read the SQL properly.
3. Add a unique constraint. **Violate it via `bulk_create`** and confirm `IntegrityError`.
   Then add a `clean()` rule and confirm `bulk_create` sails straight past it. **That contrast
   is the lesson.**
4. Try to build the storage chart from `DiskItem` history. Feel the pain. Add
   `StorageSnapshot`.
5. Seed 100,000 `DiskItem` rows. Write the dashboard query. Time it. `EXPLAIN ANALYZE`. Add the
   index. Time it again. **Record both numbers in `PROGRESS.md`.**
6. Add a `NOT NULL` column to the seeded table naively. Observe the lock. Then do it
   expand/contract.
7. Write a data migration with a working reverse. Migrate down and back up.

---

## Done when

- [ ] Schema designed by you and defensible field by field
- [ ] You have proven `clean()` does not protect you and a constraint does
- [ ] Index before/after numbers recorded
- [ ] Expand/contract performed on a large table
- [ ] A data migration that reverses cleanly
- [ ] Every generated migration has been read

---

## Interview questions this unlocks

- "Where should a uniqueness rule live — code or database?"
- "How would you add a `NOT NULL` column to a 50-million-row table?"
- "What does Django's autogenerate miss?"
- "When would you use a `JSONField`?"
- "How do you write a reversible data migration?"
