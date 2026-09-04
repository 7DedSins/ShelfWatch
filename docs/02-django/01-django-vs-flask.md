# 01 — Django vs Flask

**Status:** contract — expand when taught
**Prereqs:** none (Flask experience helps)
**Used by:** [m00](../03-build/m00-skeleton.md)
**Time:** ~40 min, mostly discussion

---

## Why this lesson exists

If you have done [Colophon](../../../Colophon/docs/), you have Flask habits. Some transfer,
some actively hurt. Naming the differences up front saves you fighting the framework for three
weeks — and "when would you choose Django over Flask?" is a real interview question.

---

## What you should be able to say afterwards

- The philosophical difference, in one sentence each
- What Django gives you that you would otherwise build
- When Flask is genuinely the better choice
- Which Flask habits to unlearn

---

## Concepts to cover

1. **The one-sentence version.** Flask: a microframework — you assemble the pieces.
   Django: batteries included — the pieces are chosen and integrated. Neither is better;
   they optimise for different situations.
2. **What Django hands you for free.** ORM, migrations, admin, auth and permissions, forms,
   sessions, CSRF, i18n, a management-command framework, and a settings system.
   **The admin alone is weeks of work you do not do** — and it is why this project can have a
   usable internal UI on day three.
3. **Project vs. app.** Flask has blueprints; Django has apps, which are heavier — models,
   migrations, admin, and templates travel together. ShelfWatch has six.
4. **The ORM vs. SQLAlchemy.** Django's is more opinionated and less flexible; the migration
   story is better integrated. Know one real limitation you will hit (complex joins and window
   functions get awkward; `.raw()` and `Subquery` exist for a reason).
5. **Flask habits to unlearn.**
   - No app factory — Django's settings module *is* the configuration mechanism
   - No `db.session.commit()` — Django autocommits per query unless you open a transaction
   - `request` is passed to your view as an argument, not a magic global. **Simpler, and no
     application-context surprise in Celery tasks** — a genuine relief after Colophon m05.
   - Django models *are* the schema; migrations are generated from them, not written first
6. **Django's own gotchas.** Lazy querysets (nothing executes until iterated), the
   `settings.py` import-order trap, `AppConfig.ready()` for startup code, and signals — which
   are powerful and become untraceable action-at-a-distance if overused. **Prefer explicit
   calls to signals.**
7. **When to choose which.** Flask/FastAPI: a small service, an unusual architecture, an API
   with no admin surface. Django: models, users, an admin, background jobs, and a schema that
   will change — i.e. exactly ShelfWatch. Be able to argue both directions.

---

## Exercise

1. Write a two-column table: what you built by hand in Colophon versus what Django provides.
   Be specific — app factory, config classes, migrations, admin, auth.
2. Start a Django project. `runserver`. Reach the admin. **Note how long that took** compared
   with getting to the equivalent in Flask.
3. Write one model, migrate, register it in admin. You now have a working CRUD UI. Reflect on
   the amount of code.
4. Write a queryset and *do not* iterate it. Print the SQL with `.query`. Confirm nothing ran.
   Then iterate. **Laziness is the source of most ORM surprises.**
5. Write down, in one paragraph, when you would pick Flask for a new project. Be specific
   enough that it is a decision rule, not a preference.

---

## Done when

- [ ] The comparison table exists
- [ ] Admin CRUD working from a single model
- [ ] You have proven querysets are lazy
- [ ] You can argue Django vs Flask in both directions

---

## Interview questions this unlocks

- "When would you use Django over Flask or FastAPI?"
- "What does Django give you out of the box?"
- "What are the downsides of Django's ORM?"
- "What's a Django app versus a project?"
- "Why are querysets lazy, and when does that bite you?"
