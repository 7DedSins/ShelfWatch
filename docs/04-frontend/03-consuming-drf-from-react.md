# 03 — The API contract, audited

**Status:** contract — expand when taught
**Prereqs:** [02-react-typescript-spa.md](02-react-typescript-spa.md)
**Time:** ~1 week

> **The most interesting lesson in this track.** Building a real client against your own API
> reveals design mistakes that no amount of reading the code would have shown you.

---

## Why this lesson exists

In lesson 01, a Django template could just call the ORM. It never needed an endpoint for
"overview counts" because it computed them inline. The SPA cannot do that — **and every place
it cannot is a place your API was incomplete.**

You designed the API in m06 without a real consumer. Now you have one. This lesson is about
what it found.

---

## What you should be able to say afterwards

- Which API design decisions only reveal themselves under a real client
- Why "one endpoint per model" is not an API design
- How chattiness happens and how to fix it without over-fetching
- How to evolve an API that already has a consumer

---

## Concepts to cover

1. **The chattiness audit.** Open the network tab on your overview screen. **Count the
   requests.** If loading one page takes seven calls, the API is model-shaped rather than
   screen-shaped. The Django version made one query set; the SPA made seven round trips.
2. **Screen-shaped endpoints.** A `GET /api/dashboard/overview/` returning exactly what the
   overview needs. **The tension:** this is less RESTful, less reusable, and much better for
   the actual client. Real APIs end up with both. Decide where each belongs and say why.
3. **Over- and under-fetching.** The disk-items table needs four fields; the serializer returns
   twenty including a large `JSONField`. Sparse fieldsets (`?fields=`), or a separate list
   serializer? **Measure the payload before deciding** — it may not matter, and knowing it does
   not matter is also a result.
4. **Where GraphQL would have helped, and why you did not use it.** This is the exact problem
   it solves. Also a whole additional technology, a new performance model, and a new security
   surface. **Be able to argue both sides** — it comes up.
5. **Pagination in practice.** Your m06 cursor pagination — is it actually usable from a UI?
   Cursor pagination means **no page numbers and no jumping to the end.** Discover that
   constraint from the client side and decide whether it was the right call.
6. **Errors the client can act on.** DRF's 400 body maps to form fields — does yours? Is there
   a stable machine-readable error code, or only prose? A client cannot branch on prose.
7. **Auth round trips.** Token refresh, concurrent 401s (Ferryman lesson 07), and what happens
   when refresh itself fails mid-session.
8. **Versioning with a live consumer.** You now have one. How do you change a field name? The
   answer is additive change plus a deprecation window — and having felt the constraint is
   different from having read about it.
9. **The write-up.** Every gap found becomes a note. **These notes are the most credible
   material in the project**, because "I found these six problems in my own API by building a
   real client against it" is a genuinely senior thing to say.

---

## Exercise

1. **Count network requests per screen.** Record all four.
2. Add one screen-shaped endpoint for the overview. Measure the improvement. Decide whether to
   keep it, and write down the trade-off.
3. Measure the disk-items payload. Decide on sparse fieldsets from the number, not by instinct.
4. Try to build a "jump to last page" control on a cursor-paginated list. **Discover you
   cannot.** Decide whether that is acceptable.
5. Trigger every error path from the SPA — 400, 401, 403, 404, 429, 500. **Is each actionable
   from the client?** Fix the ones that are not.
6. Rename a serializer field. Watch the generated types change and the build fail. **Now do it
   without breaking the client** — additive, deprecate, remove.
7. Make refresh fail mid-session. Confirm the user is logged out cleanly rather than trapped in
   a retry loop.
8. **Write the findings document.** Every API design decision you would change, with the
   evidence that revealed it.

---

## Done when

- [ ] Request counts recorded for all four screens
- [ ] At least one screen-shaped endpoint added, with the trade-off written down
- [ ] Payload sizes measured; a fieldset decision made from data
- [ ] Cursor pagination's UI constraint discovered and judged
- [ ] Every error path is actionable from the client
- [ ] You have renamed a field without breaking the consumer
- [ ] **The findings document is written and committed**

---

## Interview questions this unlocks

- "**How did building a client change your API design?**" — a genuinely strong question to
  have a real answer to.
- "REST or GraphQL?" — with a specific reason from your own experience.
- "How do you evolve an API with live consumers?"
- "How do you avoid a chatty API?"
- "What makes an API error useful to a client?"

---

**Next:** [04-comparing-the-two.md](04-comparing-the-two.md)
