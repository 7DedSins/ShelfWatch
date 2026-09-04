# Milestone 01 — Services and health

**Goal:** register a service with an encrypted API key, store health-check history, and manage
all of it through an admin that is genuinely useful.

**Detours first:** [django/03 Models and migrations](../02-django/03-models-and-migrations.md) ·
[django/05 The Django admin](../02-django/05-the-django-admin.md) ·
[concepts/03 Secrets at rest](../01-concepts/03-secrets-at-rest.md)

**Sessions:** 3

---

## Design decisions to make and write down

1. **The schema.** `Service`, `HealthCheck`, and the `TimeStampedModel` base. Design from
   access patterns before looking at anything.
2. **Why is `HealthCheck` a separate table** rather than fields on `Service`? Answer from what
   the product must show: uptime over time, latency trends, and *when* something broke. A
   current-status column cannot serve any of those. **But you will also want a denormalised
   `Service.last_health_ok`** for the dashboard — decide now whether to add it and why the
   duplication is justified.
3. **`ServiceKind` as choices** versus separate models per type. Choices plus a `JSONField` for
   per-kind config. Justify — and know what you would do if the kinds diverged substantially.
4. **Encryption.** `api_key` encrypted at rest. Where does the key come from? What happens at
   startup if it is missing? What is your rotation story?
5. **Retention.** A health check every 60s per service is 1,440 rows/day/service. **Do the
   arithmetic for a year.** Then decide: prune, downsample into hourly aggregates, or keep
   everything? On 75 GB shared with your media stack, this is a real constraint.
6. **Uniqueness.** `UniqueConstraint(["owner", "name"])` — a database constraint, not a
   `clean()` method.

---

## Build

- `apps/core/models.py` — `TimeStampedModel`.
- `apps/services/models.py` — `Service`, `HealthCheck`, `ServiceKind`, constraints, indexes.
- Encrypted field for `api_key`.
- Migrations, reviewed by hand.
- `ServiceAdmin`: coloured status column, filters, search, read-only task-written fields,
  **`api_key` excluded or masked**.
- `HealthCheckAdmin`: `date_hierarchy`, `select_related` in `get_queryset()`.
- A retention management command.

---

## Break it

1. `SELECT api_key FROM services_service;` — **look at the ciphertext with your own eyes.**
2. Register the service in admin naively. **Find the key on the changelist.** Fix it.
3. Trigger an exception with a `Service` in scope. Find the key in the traceback. Fix
   `__repr__`. Confirm.
4. Start the app with the encryption key missing. Confirm it fails loudly rather than storing
   plaintext.
5. Violate the unique constraint via `bulk_create`. Confirm `IntegrityError`. Then add a
   `clean()` rule and confirm `bulk_create` walks straight past it. **This contrast is the
   lesson about where rules belong.**
6. Insert 500,000 `HealthCheck` rows. **Load the admin changelist and time it.** Add the index
   from `Meta.indexes`. Time again. Record both.
7. Measure the table size. Extrapolate to a year at your poll interval. **Confirm your
   retention policy fits your disk budget** — or change the policy.

---

## Done when

- [ ] Schema designed by you and defensible field by field
- [ ] Keys encrypted; you have seen the ciphertext
- [ ] Admin does not leak them; tracebacks do not either
- [ ] You have proven a constraint enforces and `clean()` does not
- [ ] Changelist before/after timings recorded
- [ ] Retention policy fits the disk budget, with arithmetic
- [ ] The admin is genuinely usable
- [ ] Committed: `feat(m01): service registry with encrypted credentials and admin`

---

## Interview connection

- *"How do you store an API key you need to replay?"* — and why not hashed.
- *"What does encryption at rest actually protect against?"*
- *"Where should a uniqueness rule live?"*
- *"How do you decide data retention?"* — with arithmetic.
- *"Why is the Django admin slow by default?"*

---

**Next:** [m02 — Connectors](m02-connectors.md)
