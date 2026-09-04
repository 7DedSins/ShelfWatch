# 04 — The comparison

**Status:** written in full — this is the deliverable
**Prereqs:** [03-consuming-drf-from-react.md](03-consuming-drf-from-react.md)
**Time:** ~1 week

> **This write-up is the point of building it twice.** It is a publishable article, an interview
> answer, and the thing that makes your portfolio different from everyone else's.

---

## What you are producing

A document — in the repo, and published — titled something like:

> **"I built the same dashboard twice: Django + HTMX and React + TypeScript. Here are the
> numbers."**

Not an opinion piece. **A measurement.** The internet has no shortage of people asserting one
is better. It has very few people who built both and counted.

---

## The structure

### 1. Setup (short)

What the dashboard does, the four screens, the identical DRF API underneath. Establish that the
comparison is fair — same features, same person, same week.

### 2. The numbers

The table from [README](README.md#what-to-measure), filled in:

| Metric | Django + HTMX | React + TS |
|---|---|---|
| Time to first meaningful paint | | |
| First-load bytes | | |
| Subsequent-navigation bytes | | |
| Lines of code | | |
| **Files touched to add one field** | | |
| Build time per screen | | |
| Direct dependencies | | |
| Total dependency tree | | |
| Time to first paint on slow 3G | | |

**Do not round in favour of your preference.** If React lost on five of nine, say so. If it won
on the two that matter for your use case, say that too. **Credibility here comes entirely from
being willing to report the inconvenient number.**

### 3. Where each one won — honestly

Likely findings, but **report what you actually measured:**

**Django + HTMX probably won on:** time to build, first paint, lines of code, files touched per
change, dependency count, and operational simplicity (no build step, no second artifact to
deploy).

**React probably won on:** subsequent navigation, screens with genuine client-side state, the
bulk-acknowledge interaction, and offering a path to a mobile client later.

**Probably a wash:** the chart, form validation, the overall look.

### 4. The surprises

The most-read section. What did you *not* expect?

Candidates, from having done this: the file-count difference being larger than expected; how
many loading and error states the SPA required that Django gave you free; how much of the SPA's
cost was ecosystem rather than React; **how many API design flaws only appeared once a real
client existed** (lesson 03's findings belong here).

### 5. When you would choose each

The section that makes it useful rather than merely interesting. **Decision rules, not
preferences:**

> Choose server-rendered when the interactivity is bounded, the team is backend-heavy, the
> operational budget is small, and there is no mobile client on the roadmap.
>
> Choose a SPA when the screens hold genuine client-side state, when the same API must serve a
> mobile client, when the frontend is a separate team, or when the interaction is dense enough
> that round trips become the felt experience.

### 6. What you would do differently

Honest. Including anything you would have measured differently, or where the comparison was not
quite fair.

---

## Exercise

1. Fill in every row. **Measure again if any number was guessed.**
2. Write the surprises section first — it is the part you will forget.
3. Get one screenshot of each version side by side.
4. Write the decision rules. **Test them against a project that is not this one** — if a rule
   only applies to ShelfWatch, it is not a rule.
5. Have someone read it who does not know the project. **Can they follow the argument without
   knowing what ShelfWatch does?**
6. Publish it: the repo README, your blog, dev.to, or a Reddit post. Both r/django and
   r/reactjs will have opinions; that is fine and the comments will be useful.
7. **Practise the two-minute spoken version.** This is now an interview answer.

---

## Done when

- [ ] Every row measured, none guessed
- [ ] Inconvenient numbers reported as clearly as convenient ones
- [ ] The surprises section is specific
- [ ] Decision rules generalise beyond this project
- [ ] Published somewhere public
- [ ] You can deliver the two-minute version out loud

---

## Why this matters more than either dashboard

Two candidates. One says "I prefer React, it's more flexible." The other says:

> "I built the same four screens both ways against the same API. React's first paint was 340ms
> slower and shipped 180KB more on first load, but subsequent navigation was 90% smaller.
> Adding one field touched two files in Django and five in React. The thing that actually
> surprised me was how many loading and error states I had to build by hand in the SPA that
> Django gave me for free — and how many holes it exposed in an API I thought was finished.
> For this product I shipped the Django version, and I would choose React the moment we needed
> a mobile client."

**The second person is getting the offer.** Not because the conclusion is right — because it is
evidenced, specific, and clearly their own.

---

**Next:** [05-ops/01-production-deployment.md](../05-ops/01-production-deployment.md)
