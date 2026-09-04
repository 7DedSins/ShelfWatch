# The dashboard — built twice

**Status:** written in full — read before starting either version
**Prereqs:** [m06 DRF API](../03-build/m06-drf-api.md) and [m08](../03-build/m08-performance-pass.md) complete
**Time:** 5–6 weeks for both

---

## The idea

You are going to build the same dashboard twice: once **server-rendered** with Django
templates and HTMX, once as a **typed React SPA** against the DRF API you already built.

That sounds wasteful. It is the most valuable thing in this project for a full-stack job search,
for three reasons.

**1. You will be asked to choose, and most people cannot.** "Server-rendered or SPA?" is a real
architecture question. Almost everyone answers from habit or fashion. You will answer from
having built the same screens both ways and measured the difference.

**2. Both stacks are employable, and they hire differently.** Django-template shops and React
shops are largely separate job markets. Doing both roughly doubles the roles you can apply for
honestly.

**3. The second one is fast.** The API exists. The data model is settled. The screens are
designed. The second build is mostly application, not discovery — most of the cost is in
version one.

---

## The screens (both versions build all four)

1. **Overview** — service status cards, storage-over-time chart, recent discrepancies
2. **Library detail** — disk items table, scan history, per-library discrepancies
3. **Discrepancies** — filterable, sortable, bulk-acknowledge
4. **Settings** — service CRUD, and a **test-connection** button that hits the connector live

The same four screens, twice. Identical functionality, so the comparison is honest.

---

## The lessons

| # | Lesson | Focus |
|---|---|---|
| [01](01-django-templates-and-htmx.md) | Server-rendered | Templates, HTMX, Alpine, Tailwind, one chart |
| [02](02-react-typescript-spa.md) | The SPA | Vite, routing, TanStack Query, the same four screens |
| [03](03-consuming-drf-from-react.md) | The contract | Generated types, JWT, pagination, the API gaps you find |
| [04](04-comparing-the-two.md) | **The write-up** | Measured, honest, published. The actual deliverable. |

---

## ⚠️ Prerequisite: learn React properly first

**These lessons do not teach React.** They assume it.

If you have not done
[**Ferryman's frontend track**](../../../Ferryman/docs/09-frontend/README.md) — ten lessons
covering TypeScript, React fundamentals, Vite, TanStack Query, SSE, browser auth, forms,
testing, and deployment — **do that first.** It teaches the concepts properly against a simpler
UI.

Coming here afterwards, lessons 02–03 are mostly application: you already know the tools, you
are pointing them at a Django backend instead of a FastAPI one. **That is the right order** and
it is why the estimate above is five weeks rather than ten.

---

## Which to build first, and why it matters

**Build the Django version first.** Three reasons:

1. **You will finish it.** A working dashboard in week two keeps the project alive.
2. **It surfaces the data questions** — what the overview needs, how discrepancies should be
   grouped, what the chart shows — using the cheapest possible tooling. Discovering those in
   React costs three times as much.
3. **It exposes the gaps in your API.** You will find that the SPA needs endpoints the
   server-rendered version did not, because a template can just call the ORM. **Those gaps are
   the most interesting finding of this whole exercise** and lesson [03](03-consuming-drf-from-react.md)
   is where you write them down.

---

## What to measure

Collect these for both. They are the substance of lesson 04 and they go in
[PROGRESS.md](../PROGRESS.md).

| Metric | Why it matters |
|---|---|
| Time to first meaningful paint | The user-visible difference |
| Total bytes transferred, first load | Where the SPA pays its cost |
| Total bytes on a subsequent navigation | Where the SPA earns it back |
| Lines of code, each version | The maintenance proxy |
| Number of files touched to add one field | **The best proxy for real cost** |
| Time to build each screen | Honest, including debugging |
| Dependency count | What you are agreeing to maintain |

That fifth row is the one people never measure and it is the most revealing. Adding a field to
a server-rendered page is a template and a query. In the SPA it is a serializer, a regenerated
type, a component, and possibly a test. **Two files versus five is a real number about
long-term cost.**

---

## The honest expected conclusion

You will probably find the Django version is **faster to build, faster to first paint, and
simpler to maintain**, and that the React version is **better on subsequent navigation, better
for genuinely interactive screens, and required for a mobile app later.**

That conclusion is unremarkable. **The value is that you will have measured it** rather than
asserted it — and being the person in the room who says "I built this both ways, here are the
numbers" is a completely different position from having an opinion.

---

**Next:** [01-django-templates-and-htmx.md](01-django-templates-and-htmx.md)
