---
title: 1. The Contract
description: What a client can rely on is bigger than what you documented, and design has to account for both
type: lesson
---

# Lesson 1. The Contract

**Mission link:** "The contract" is the mission's first word for a reason: everything else, the error model, versioning, deprecation, is a decision about what the contract says or how it's allowed to change.
**Primary source:** [RFC 9110: "HTTP Semantics", IETF](https://www.rfc-editor.org/rfc/rfc9110)
**Prerequisites:** none

## Know this

### A contract is bigger than your documentation

An API's contract is every promise a client can build logic against and expect to keep working. RFC 9110 is a good model of what a *deliberate* contract looks like: it doesn't just describe typical server behavior, it specifies exactly what each status code and method means, precisely enough that a client can make decisions from it (whether a request is safe to retry, whether a method is idempotent, what a `201` implies that a `200` doesn't).

But **the contract a client actually depends on is not limited to what you documented.** This is [Hyrum's Law](https://www.hyrumslaw.com/): with enough users of an API, every observable behavior of the system, documented or not, will end up depended on by somebody. Field ordering in a JSON response you never promised to preserve. The exact wording of an error message. How long a request usually takes. None of these were promises you made on purpose, and all of them can become promises you're stuck keeping, the moment enough clients build on them.

### Two jobs, not one

This splits API design into two distinct jobs:

1. **Decide the deliberate contract.** What you document and commit to: endpoints, fields, status codes, error shapes, what's guaranteed to stay stable and what's explicitly allowed to change.
2. **Minimize the accidental contract.** Reduce how much of your implementation's incidental behavior looks stable enough for a client to build on it, even though you never promised it. Randomizing something that doesn't need a guaranteed order, explicitly documenting a field as "may be absent, do not assume it's always present," and being consistent about behavior you *do* intend to guarantee, are all moves in this direction.

You cannot eliminate the second job. You can only make the accidental contract smaller and more visible, so fewer surprises land on you later.

### Errors are part of the contract too

A response's error shape is exactly as much a contract as its success shape. A client that wants to react differently to "you sent something invalid" versus "try again later" versus "this resource doesn't exist" needs that distinction to be a reliable, documented part of the response, not something it has to infer from a status code alone or, worse, from parsing human-readable error text. (RFC 9457's *Problem Details* format, covered in a later lesson, is one standard way to make that distinction explicit and machine-readable.)

## Practice

1. ▢ In one sentence, why is "the contract" bigger than what's written in an API's documentation?

<details markdown="1"><summary>Check</summary>

Because clients can and do build logic around any observable behavior, not just documented ones (Hyrum's Law), so anything a client can reliably observe functions as part of the contract whether or not it was ever promised.

</details>

2. ▢ A team notices their JSON responses have always returned object fields in a consistent order, though this was never documented or promised. They change the field order in a minor internal refactor "since it wasn't part of the API." Several client integrations break. Explain what happened, in terms of this lesson.

<details markdown="1"><summary>Check</summary>

This is Hyrum's Law in action: the consistent field ordering was an *accidental* contract, never deliberately promised, but reliable enough in practice that some clients came to depend on it (perhaps by comparing raw JSON strings, or fragile parsing). The team was correct that it wasn't part of the *documented* contract, but that doesn't mean it wasn't part of the *actual* contract clients were relying on.

</details>

3. ▢ Give one concrete design practice that shrinks the gap between the accidental contract and the deliberate one, for a behavior an API doesn't want to promise.

<details markdown="1"><summary>Hint</summary>

If a behavior is never meant to be relied on, what could you do to that behavior itself, rather than just writing "don't rely on this" in the docs?

</details>

<details markdown="1"><summary>Check</summary>

Deliberately vary the unpromised behavior instead of leaving it accidentally stable, for example, randomizing field order or pagination page sizes if order or size was never meant to be guaranteed. A behavior that's actually inconsistent is much harder for a client to accidentally depend on than one that happens to be stable by coincidence. (Explicitly documenting "this is not guaranteed" helps but is weaker on its own, since Hyrum's Law doesn't care what the docs say.)

</details>

4. ▢ Which of these is safest to change without breaking clients, all else being equal?

   - a) The exact wording of an error message that was never documented as stable, changed at random for no functional reason
   - b) The presence or absence of a documented, guaranteed response field
   - c) A status code's meaning as specified by RFC 9110 (for example, making `404` mean something other than "not found")
   - d) The order of fields in a JSON object, changed without ever having randomized or varied it before

<details markdown="1"><summary>Check</summary>

**a)** An arbitrary, never-documented error message wording is the least likely to be relied on deliberately, though Hyrum's Law means even this carries some risk. (b) breaks a deliberate, documented promise. (c) violates a widely-relied-on, spec-defined meaning. (d) is exactly the accidental-contract trap from Practice item 2: undocumented but historically stable behavior that's likely being relied on even though it was never promised.

</details>

## Real-world reps

- [ ] Pick a real API you use or maintain (a public one, or an internal one). List three behaviors it exhibits that are *not* documented as guaranteed, and for each, guess whether a real client is likely relying on it anyway.
- [ ] For that same API, find one place in its docs where a behavior is explicitly called out as "not guaranteed" or "subject to change." Note whether the implementation actually varies that behavior, or just says so in prose while leaving it stable in practice.
- [ ] Tomorrow: read RFC 9110's definitions of at least three status codes you use often, and check whether your own mental model of what each one means matches the spec exactly.

## Going further

- [Site: "API Improvement Proposals", Google](https://google.aip.dev/)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
