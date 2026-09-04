# 02 — Settings and project layout

**Status:** contract — expand when taught
**Prereqs:** [01-django-vs-flask.md](01-django-vs-flask.md)
**Used by:** [m00](../03-build/m00-skeleton.md)
**Time:** ~50 min

---

## Why this lesson exists

Django's default layout does not survive a real project. One `settings.py` full of
`if DEBUG:` and a flat pile of apps is what most tutorials leave you with, and it is the first
thing a reviewer notices is wrong.

---

## What you should be able to say afterwards

- Why split settings beat conditionals
- How to structure apps so they stay independent
- Where business logic goes, and why not in views or models
- How secrets reach the application

---

## Concepts to cover

1. **Split settings.** `config/settings/base.py`, `local.py`, `production.py`, `test.py`.
   Each imports `base` and overrides. `DJANGO_SETTINGS_MODULE` selects one.
   **Never `if DEBUG:` in application code** — every such branch is a path your tests do not
   cover in the configuration that matters.
2. **`config/` as the project package**, not `shelfwatch/settings/`. Clearer, and it makes the
   distinction between "the project" and "the apps" structural.
3. **Apps under `apps/`.** `core`, `services`, `libraries`, `reconcile`, `alerts`, `api`,
   `dashboard`. Each with an `apps.py` declaring an explicit `name`. Split by **domain**, not
   by layer — no `models/` app and `views/` app.
4. **The dependency direction.** `core` depends on nothing. `services` may not import
   `dashboard`. **Draw the arrows before you write code**, and add a test that fails if an app
   imports one it should not. An architectural rule that is not enforced is a suggestion.
5. **Business logic in `services.py`.** Plain functions, no `request`, no Celery import.
   Views call them. Tasks call them. The API calls them. **This is the single most important
   layout decision** — it is what makes the logic testable without a broker and reusable by
   three different callers.
6. **`django-environ`.** Typed environment variables, `.env.example` committed, `.env` never.
   `SECRET_KEY`, `DATABASE_URL`, `REDIS_URL`, the field-encryption key. Missing values fail at
   startup.
7. **Production settings that matter.** `DEBUG=False`, `ALLOWED_HOSTS`, `SECURE_SSL_REDIRECT`,
   `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`, `CSRF_TRUSTED_ORIGINS`, HSTS. Know what each
   does — `manage.py check --deploy` will list them and you should be able to explain every
   line of its output.
8. **Static files.** `collectstatic` and WhiteNoise, so you serve static assets without a
   separate web server. Relevant to your RAM budget.

---

## Exercise

1. Build the split settings. Run with each and confirm the differences are real.
2. Create the six apps with explicit `AppConfig` names.
3. **Draw the dependency graph.** Then write a test that fails if `apps.core` imports anything
   from another app.
4. Move one piece of logic into a `services.py` function. Call it from a view **and** from a
   management command. Notice it needed no changes.
5. Wire `django-environ`. Delete a required variable and confirm startup fails naming it.
6. Run `manage.py check --deploy` against production settings. Fix everything. **Be able to
   explain each fix**, not just apply it.
7. Set up WhiteNoise; run `collectstatic`; serve with `DEBUG=False` and confirm CSS loads.

---

## Done when

- [ ] Split settings; no `if DEBUG` in application code
- [ ] Six apps, explicit configs, dependency graph drawn
- [ ] An automated test enforces the dependency direction
- [ ] Logic lives in `services.py` and is called from two places
- [ ] Missing config fails at startup
- [ ] `check --deploy` is clean and you understand every item

---

## Interview questions this unlocks

- "How do you structure a large Django project?"
- "How do you manage settings across environments?"
- "Where does business logic belong in Django?"
- "How do you enforce an architectural boundary?"
- "What does `check --deploy` warn about?"
