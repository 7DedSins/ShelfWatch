# 01 — The server-rendered dashboard

**Status:** contract — expand when taught
**Prereqs:** [README](README.md), [m08](../03-build/m08-performance-pass.md)
**Time:** 2–3 weeks

---

## Why this lesson exists

This is the version most Django jobs actually want, and it is the version that will exist and
work while the React one is still being scaffolded. It also proves something worth knowing:
**a great deal of "we need a SPA" is habit.**

---

## What you should be able to say afterwards

- How Django's template layer, HTMX, and Alpine divide responsibility
- Why server-rendered pages are fast by default and how to keep them that way
- When you genuinely need client-side state
- How to add a chart without adding a build pipeline

---

## Concepts to cover

1. **Template structure.** A base template, per-screen templates, and `_partials/` for every
   fragment HTMX will swap. **Design partials from the start** — retrofitting them out of a
   monolith is tedious work with nothing to learn from it.
2. **Class-based vs. function views.** `ListView` and `DetailView` remove boilerplate and hide
   behaviour. Use them where they fit; drop to function views where they do not. Be able to say
   why for each.
3. **Context and queries.** `get_context_data` is where your N+1s live. Everything from
   [m08](../03-build/m08-performance-pass.md) applies. **Keep debug-toolbar open the entire
   time.**
4. **HTMX.** `hx-get`, `hx-target`, `hx-swap`, `hx-trigger`. Filtering the discrepancy list
   without a reload. Bulk-acknowledge posting and swapping the table back.
   `hx-trigger="every 30s"` to refresh service cards.
5. **Alpine.js** for the genuinely client-side bits — a dropdown, a modal, a toggle. **Alpine
   is not a state manager.** If you find yourself building one, that screen is the argument for
   the SPA and you should note it for lesson 04.
6. **Tailwind.** Via `django-tailwind` or a CDN build. Note whether you added a Node build step
   after all — that is directly relevant to the comparison.
7. **The chart.** Server-render the data into the template, hand it to a small Chart.js line
   chart. **Do not add a frontend build pipeline for one chart.**
8. **Progressive enhancement.** Filters that work as a plain form submit and are enhanced by
   HTMX. Cheap, and it means the page works while HTMX is still loading.
9. **The test-connection button.** Hits the live connector, swaps in the result. A good HTMX
   showcase: real work, real latency, `hx-indicator` for the spinner.
10. **CSRF.** Django's CSRF token with HTMX requests. It will bite you exactly once; know why.

---

## Exercise

1. Base template, Tailwind, navigation. **Note whether you needed Node.**
2. Overview: service cards, storage chart, recent discrepancies. **Debug-toolbar open.**
   Record the query count and load time.
3. Library detail with a paginated disk-items table and scan history.
4. Discrepancies: HTMX filtering, sorting, bulk-acknowledge. No page reloads.
5. Settings: service CRUD with Django forms, plus the live test-connection button.
6. Auto-refresh the service cards every 30s.
7. **Measure everything in the [README's table](README.md#what-to-measure).** Time to first
   paint, bytes, lines of code, files touched, dependency count, build time per screen.
8. **Add one field to the disk-items table** (say, newest chapter date) and **count the files
   you touched.** Write the number down — you will compare it directly in lesson 04.
9. Disable JavaScript. Note what still works.

---

## Done when

- [ ] All four screens work, no page reloads for interactions
- [ ] Query counts within your m08 targets
- [ ] The chart works with no frontend build pipeline
- [ ] Filters work without JavaScript, enhanced by HTMX
- [ ] Test-connection hits the real connector with a loading state
- [ ] **Every metric in the measurement table recorded**
- [ ] The "add one field" file count recorded
- [ ] Committed: `feat(dashboard): server-rendered dashboard with HTMX`

---

## Interview questions this unlocks

- "When would you use HTMX instead of React?"
- "How do you avoid N+1s in a template?"
- "What can't you do with server-rendered HTML?"
- "How does CSRF work with an AJAX request?"

---

**Next:** [02-react-typescript-spa.md](02-react-typescript-spa.md)
