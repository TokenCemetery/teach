---
title: 9. Versioning and Migration Strategy
description: How to ship a genuine breaking change without breaking every existing integration at once, using Stripe's versioning strategy as a worked example
type: lesson
---

# Lesson 9. Versioning and Migration Strategy

**Mission link:** This is stage 5's capstone. Lesson 8 covered additive changes and deprecation for changes that can stay backward-compatible; this lesson is what to do when a change genuinely can't be, closing the mission's second success criterion: evolving an existing API without breaking the clients that depend on it.
**Primary source:** [Docs: "API versioning", Stripe](https://docs.stripe.com/api/versioning)
**Prerequisites:** [Lesson 8](0008-additive-changes-and-deprecation.md), [Contract](../GLOSSARY.md)

## Warm-up

1. ▢ Why is adding a new, optional field to an API response usually a safe change for existing clients?

<details markdown="1"><summary>Check</summary>

An existing client only reads the fields it already knows about; a new field it's never heard of is simply absent from its parsing logic, not an error. The client keeps working exactly as it did before the addition.

</details>

2. ▢ Why is an unenforced deprecation notice worse than no notice at all?

<details markdown="1"><summary>Check</summary>

It trains clients to ignore deprecation warnings entirely, since the label has never once corresponded to a real consequence. A future deprecation notice the API actually intends to enforce is then likely to be ignored too, since nothing distinguishes it from the ones that never mattered.

</details>

## Know this

### A version is a commitment to a frozen contract, not just a number

**Versioning** means giving a specific point-in-time snapshot of an API's contract a stable name (a date, a number, a header value) and committing to keep that exact snapshot's behavior unchanged going forward, even as the API itself continues to evolve. This is what lets a breaking change ship at all: instead of changing the one contract every client uses, a new version is introduced as its own frozen contract, and existing clients, pinned to the old version, are entirely unaffected until they deliberately choose to move.

### Per-request versioning lets each client migrate on its own schedule

Stripe's specific approach pins each API key (or each request, via a header) to a version at the time an integration first starts using the API, and keeps serving that version's behavior indefinitely, even as newer versions ship for new integrations. This is a materially different model from a single global "v2 replaces v1 on this date" cutover: a breaking change doesn't force every existing integration to migrate simultaneously, and a team can upgrade an integration to a newer version only when they've actually done the work to handle the change, on their own timeline rather than the API's.

![Two side-by-side timelines, each showing three client integrations, A, B, and C. On the left, a global cutover: all three clients run on v1 until one fixed date, then all switch to v2 simultaneously, regardless of whether each has done the work to handle it. On the right, per-key pinned versioning: client A stays on v1 the whole time, client B migrates to v2 partway through on its own schedule, and client C migrates even later, each choosing when to move independently of the others.](images/global-cutover-vs-pinned-versioning.svg)

### Migration is a translation layer, not a demand

Making a breaking change safe to adopt means providing a real path from the old behavior to the new one: documentation describing exactly what changed and why, and often a compatibility or translation layer that can convert between old and new request/response shapes so a client doesn't have to rewrite everything at once. A migration guide that only says "this changed, update your code" without explaining the mapping between old and new shapes pushes the entire cost of the transition onto every integrating team independently, the opposite of the mission's goal of evolving a contract without breaking the clients that depend on it.

### Choosing between versioning and staying additive is itself a design decision

Not every change needs a new version: lesson 8's additive changes never do, since they don't break anything. A new version is the tool specifically for a change that can't be made additive, removing a field, changing a type, changing a status code's meaning, changing validation rules to reject previously-valid input. Reaching for a new version when an additive change would have worked adds unnecessary migration burden on clients (a coordinated upgrade they didn't need to make); avoiding a new version when a change is genuinely breaking silently breaks clients who trusted the contract to stay stable. The actual skill is telling these two situations apart correctly, not defaulting to either one.

## Practice

1. ▢ What does giving an API contract a specific version name actually commit an API provider to?

<details markdown="1"><summary>Check</summary>

Keeping that exact version's behavior unchanged going forward, even as the API's overall design continues to evolve in newer versions. It's a frozen snapshot of the contract, not just a label.

</details>

2. ▢ How does Stripe's per-key (or per-request) versioning model differ from a single global cutover date, and why does that difference matter for migration?

<details markdown="1"><summary>Hint</summary>

Consider what happens to an existing integration that has done no work at all, under each model, once a breaking change ships.

</details>

<details markdown="1"><summary>Check</summary>

Under a global cutover, every existing integration is forced onto the new behavior at the same fixed date regardless of whether they've done the migration work. Under Stripe's per-key model, each integration keeps its pinned version's behavior indefinitely and only moves to a newer version when that team deliberately chooses to, letting migration happen on each client's own timeline instead of a single forced deadline.

</details>

3. ▢ Why is a migration guide that only says "this changed, update your code" insufficient, according to this lesson?

<details markdown="1"><summary>Check</summary>

It pushes the entire cost of understanding and translating between the old and new behavior onto every integrating team independently, rather than the API provider doing that translation work once. A real migration path documents the specific old-to-new mapping and, ideally, provides a compatibility layer, reducing the burden instead of just announcing the change occurred.

</details>

4. ▢ A team is deciding whether a planned change (tightening input validation to reject a previously-accepted value) needs a new API version. Walk through the reasoning.

<details markdown="1"><summary>Check</summary>

This is not additive: a request that used to succeed with the old, looser validation would now fail, breaking any existing client sending that previously-valid input, exactly the kind of change lesson 8 says can't be shipped directly. It needs a new version (or an equivalent deprecation-and-transition process) so existing clients keep their current behavior until they deliberately adopt the stricter validation, rather than having working requests suddenly start failing.

</details>

5. ▢ Which claim correctly describes versioning and migration strategy?

    - a) Every change to an API, additive or not, should get its own new version for consistency
    - b) A version is a commitment to a frozen contract snapshot; genuinely breaking changes (not additive ones) are the right occasion for a new version, ideally paired with per-client migration timing and a real translation path, not just an announcement
    - c) A single global cutover date is always the correct way to introduce a breaking change, since it's simpler for the API provider
    - d) A migration guide only needs to state that a change occurred, since integrating teams are responsible for figuring out the rest

<details markdown="1"><summary>Check</summary>

**b)** That's the precise discipline this lesson (and stage) closes on. (a) is false: additive changes (lesson 8) never need a new version, since they don't break anything; forcing a version bump on them adds needless migration burden. (c) is false: a global cutover forces every integration to migrate simultaneously regardless of readiness, the exact problem Stripe's per-key model avoids. (d) is false: this is exactly the insufficient migration guide this lesson warns against.

</details>

## Real-world reps

- [ ] Find a real API's versioning strategy (one you use or maintain). Determine whether it uses per-client pinned versions, a global cutover date, or no explicit versioning at all, and note what that implies for how existing integrations experience a breaking change.
- [ ] For that same API, find one documented breaking change and its migration guide. Check whether it explains the specific old-to-new mapping or only announces that something changed.
- [ ] Tomorrow: read the primary source's versioning strategy in full, and note specifically how Stripe communicates a version's behavior to a client (a response header, a dashboard setting, documentation), and how long they support older versions before any real deprecation pressure begins.

## Going further

- [Docs: "API versioning", Stripe](https://docs.stripe.com/api/versioning)
- [Site: "API Improvement Proposals", Google](https://google.aip.dev/)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
