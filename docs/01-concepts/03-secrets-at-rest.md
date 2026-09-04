# 03 — Secrets at rest

**Status:** contract — expand when taught
**Prereqs:** none
**Used by:** [m01](../03-build/m01-services-and-health.md), [m06](../03-build/m06-drf-api.md)
**Time:** ~45 min

---

## Why this lesson exists

ShelfWatch stores API keys for other people's services. Unlike a password, you must be able to
**use** the value — so hashing is not an option, and that changes everything about how you
protect it.

---

## What you should be able to say afterwards

- Why an API key you must replay cannot be hashed, and what you do instead
- Where the encryption key lives, and why that is the real problem
- How to guarantee a secret never appears in an API response
- What encryption at rest actually protects against, and what it does not

---

## Concepts to cover

1. **Hash vs. encrypt.** A password is *verified* — hash it, compare hashes, never recover it.
   A service API key is *replayed* — you must send the original value to Kavita, so it must be
   recoverable. **Different requirement, different tool.** This distinction is asked about and
   frequently muddled.
2. **Encryption at rest.** Symmetric encryption (Fernet) on the column. A stolen database dump
   is useless without the key.
3. **The key problem, honestly.** The encryption key lives in the environment on the same box
   as the database. Someone with root has both. **So what does this actually protect against?**
   A leaked backup, a misconfigured volume, an accidental `pg_dump` in a repo, a hosting
   provider's disk. Those are the realistic threats and they are worth defending. **Be able to
   state the limitation as clearly as the benefit** — overclaiming here is a bad look.
4. **Key rotation.** Changing the key means re-encrypting every row. Design for it: store a key
   version alongside the ciphertext so old and new can coexist during a rotation.
5. **Never serialize it out.** `write_only=True` on the DRF field. **And a test asserting the
   key value appears in no response body anywhere** — a real, automated guard, not a promise.
6. **Never log it.** Exception handlers dump local variables. A `repr` that includes the key
   will end up in Sentry. Override `__repr__` on anything holding one.
7. **The admin leaks too.** Django admin renders model fields. An encrypted field displayed in
   the changelist has just been decrypted onto a web page. Set `readonly_fields`, or better,
   exclude it and show only a masked prefix.
8. **What you never store at all.** Derived bearer tokens. Kavita's flow exchanges the API key
   for a short-lived JWT — **hold that in memory on the connector instance, never on disk, never
   in `/tmp`.** Your Contabo notes record a real slip of exactly this kind; the lesson is to
   pipe tokens into the next call rather than persisting them.

---

## Exercise

1. Add an encrypted field for `Service.api_key`. Confirm the ciphertext in the database is
   unreadable — actually run the `SELECT` and look at it.
2. Write the test that greps every API response for the key value. Make it fail first by
   removing `write_only`.
3. Add the service to Django admin naively. **Find the key rendered on the changelist page.**
   Fix it.
4. Trigger an exception with the key in a local variable. Find it in the traceback. Fix
   `__repr__` and confirm it is gone.
5. Rotate the encryption key. Work out what breaks. Implement versioning so it does not.
6. Delete the encryption key entirely and start the app. Confirm it fails loudly at startup
   rather than silently storing plaintext.
7. Write down, in the README, **what this protects against and what it does not.**

---

## Done when

- [ ] Keys encrypted at rest; you have seen the ciphertext
- [ ] An automated test proves keys never appear in any response
- [ ] Admin does not leak them
- [ ] Tracebacks do not leak them
- [ ] Rotation is possible without downtime
- [ ] Missing key fails at startup
- [ ] The threat model is documented honestly

---

## Interview questions this unlocks

- "How do you store an API key you need to use later?"
- "Why not hash it?"
- "What does encryption at rest actually protect against?" — the honest answer is the strong one.
- "How do you rotate an encryption key?"
- "How do you stop a secret ending up in your logs?"
