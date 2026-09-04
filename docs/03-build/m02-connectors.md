# Milestone 02 — Connectors

**Goal:** one interface that talks to Kavita, Komga, and LANraragi, so nothing above it knows
which service it is dealing with.

**Detours first:** [concepts/01 Polling and reconciliation](../01-concepts/01-polling-and-reconciliation.md)

**Sessions:** 3

> **The design point a reviewer notices first.** "How would you add Jellyfin?" should have a
> one-sentence answer: one new file, one registry line.

---

## Design decisions to make and write down

1. **The boundary.** What does a connector return? **Plain frozen dataclasses** —
   `RemoteLibrary`, `RemoteSeries`, `HealthResult` — never a service's raw JSON. The moment
   Kavita's field names leak upward, the abstraction is gone.
2. **Required vs. optional capabilities.** Every service has health and libraries. Not every
   service exposes running scans. Make `active_scans()` a **default implementation returning
   empty**, not an abstract method — otherwise each new connector must implement things it
   cannot do, and adding a connector becomes a chore instead of a pleasure.
3. **⚠️ Errors: unavailable vs. empty.** A timeout must raise a distinct exception. **It must
   never return an empty list.** If it does, m05 will conclude every series was deleted.
   Design the exception hierarchy now: `ServiceUnavailable`, `ServiceAuthFailed`,
   `ServiceBadResponse` — three distinct things a caller may want to treat differently.
4. **Auth is per-connector.** Kavita exchanges an API key for a JWT; LANraragi uses a
   base64-encoded key in a header. **The connector owns this entirely.** Where is the JWT
   cached, and for how long? (In memory on the instance. Never to disk — including `/tmp`.)
5. **Retry policy — whose job?** The connector's, or the Celery task's? **The task's.** A
   connector that retries internally makes its own latency unpredictable and hides failures
   from the retry policy you configured. One exception: a single re-auth on `401`, because that
   is recovery rather than retry.
6. **Pagination.** Never assume one response holds everything. `list_series` returns an
   iterator so callers do not accumulate 8,000 objects.

---

## Build

- `apps/services/connectors/base.py` — `BaseConnector` ABC, the dataclasses, the exception
  hierarchy.
- `kavita.py`, `komga.py`, `lanraragi.py`.
- `registry.py` mapping `ServiceKind` → class.
- Shared `httpx.Client` with explicit connect and read timeouts.
- A "test connection" service function the admin and API can both call.
- Tests against **recorded fixtures** using `respx`. CI must not need your VPS.

---

## Kavita specifics

These are **discovered facts, not derivable** — no time is wasted by knowing them:

- Auth: `POST /api/Plugin/authenticate` exchanges the API key for a JWT, then
  `Authorization: Bearer`. Cache the JWT on the instance; re-auth once on `401`, then fail.
- **`/api/Series/all-v2` ignores the `libraryId` filter.** A real, confirmed quirk. Filter
  client-side and **leave a comment saying why the obvious code is not there** — reviewers
  value a comment that explains an absence.
- Paginate.

Anything about the *design* is still yours to derive. If you want to check your connector
abstraction against the original, `docs/reference/original-implementation-plan.md` §5 is safe
to open **after** you have written yours.

---

## Break it

1. Point a connector at a URL that does not resolve. Confirm `ServiceUnavailable`.
2. Point it at a service returning HTML instead of JSON. Confirm `ServiceBadResponse`.
3. Wrong API key. Confirm `ServiceAuthFailed`, and confirm **no retry** — the credentials will
   not improve.
4. Expire the JWT mid-session. Confirm exactly one re-auth, then success.
5. **The important one:** make the connector time out and confirm it **raises rather than
   returning `[]`**. Then deliberately make it return `[]` and hold on to what that would mean
   in m05 — hundreds of false "series deleted" discrepancies.
6. A service with 8,000 series. Confirm pagination works and memory stays flat (the iterator
   is doing its job).
7. Point the Kavita connector at Komga. Confirm a clear failure, not a confusing partial parse.
8. **Write the Jellyfin connector signature** — just the class and method stubs, no
   implementation. If that took more than ten minutes, your abstraction is wrong.

---

## Done when

- [ ] Three working connectors behind one interface
- [ ] Optional capabilities have defaults, not abstract methods
- [ ] Unavailable / auth-failed / bad-response are distinct, each tested
- [ ] **A timeout raises and never returns empty** — tested
- [ ] JWT cached in memory only, re-auth once
- [ ] Retries live in the task layer, not the connector
- [ ] CI hermetic on recorded fixtures
- [ ] Adding a connector is provably one file plus one line
- [ ] Committed: `feat(m02): pluggable service connectors with typed failures`

---

## Interview connection

- *"How would you support a new service type?"* — one file, one line. Demonstrate it.
- *"How do you distinguish 'no data' from 'couldn't fetch'?"* — and why it matters here.
- *"Where does retry logic belong?"*
- *"How do you test code that calls a third-party API?"*
- *"How do you stop a third party's data model leaking through your system?"*

---

**Next:** [m03 — Celery and polling](m03-celery-and-polling.md)
