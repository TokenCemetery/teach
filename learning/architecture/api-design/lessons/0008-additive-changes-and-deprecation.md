---
title: 8. Additive Changes and Deprecation
description: Why adding is usually safe and removing or changing meaning is usually not, and how to deprecate a field or endpoint without breaking clients on the spot
type: lesson
---

# Lesson 8. Additive Changes and Deprecation

**Mission link:** Stage 5 opens versioning and evolution, the mission's second success criterion. Lessons 1-7 designed contracts; this lesson is what changing an already-shipped contract safely actually requires, before lesson 9 covers the full migration strategy for a change that can't be additive.
**Primary source:** [Site: "API Improvement Proposals", Google](https://google.aip.dev/)
**Prerequisites:** [Lesson 7](0007-grpc-streaming.md), [Contract](../GLOSSARY.md)

## Warm-up

1. ▢ Name gRPC's four RPC kinds and, in one phrase each, the request/response shape each is for.

<details markdown="1"><summary>Check</summary>

Unary: one request, one response. Server streaming: one request, a stream of responses. Client streaming: a stream of requests, one response. Bidirectional streaming: both sides stream messages independently over the same call.

</details>

2. ▢ Why is reaching for gRPC streaming to implement what's really just a paginated list usually the wrong design choice?

<details markdown="1"><summary>Check</summary>

A paginated list is a bounded, request-per-page interaction that a unary RPC already handles cleanly; a stream introduces real complexity (managing an open connection, handling partial failure mid-stream) without solving a problem the use case actually has.

</details>

## Know this

### Additive changes are safe because old clients can ignore what's new

An **additive change**, adding a new, optional field to a response, adding a new endpoint, adding a new enum value, is safe specifically because an old client that doesn't know about the addition simply doesn't look for it and keeps working exactly as before. This is the same principle proto3 uses for schema evolution (lesson 6): a client parsing a response only reads the fields it knows about, so a field it's never heard of is invisible to it, not an error. The contract from lesson 1's perspective hasn't been broken for existing clients; it's only been extended for clients that choose to read the new part.

### Removing or changing meaning is never safe without a transition

The opposite direction, removing a field, changing what a field means, changing a status code's semantics, breaks any client depending on the old behavior the moment it ships, since that client has no way to know the change happened until its own logic fails. This is why removal and meaning-changes require a deliberate transition, not a direct edit: the old behavior has to keep working for some announced period while clients migrate away from it, rather than disappearing the instant the new design is ready.

### Deprecation is a documented promise about a specific timeline, not a warning label

**Deprecating** a field or endpoint means committing to two things explicitly: that it still works exactly as before for now, and a real, stated point (a date, a version, an announced cutoff) after which it may stop working or behave differently. A deprecation notice that never actually gets enforced, a field marked "deprecated" for years with no real removal plan, is worse than no notice at all: it trains clients to ignore deprecation warnings entirely, since the label has never once corresponded to an actual consequence. A deprecation notice a client can trust is one an API is actually willing to act on.

### Signaling deprecation so a client can actually respond

A deprecation should be observable, not just written in a changelog nobody reads: a response header (`Deprecation: true`, or a date), a field explicitly marked deprecated in the schema (proto3 supports a `deprecated = true` field option; OpenAPI has an equivalent), or a Problem Details `type` warning included alongside an otherwise-successful response. The goal is that a client's own tooling, not just a human reading documentation, can detect "this thing I'm using is going away" and flag it, the same way a compiler flags a deprecated function call, rather than relying on every integrating team to have read and remembered a changelog entry from months earlier.

## Practice

1. ▢ Why is adding a new, optional field to an API response usually a safe change for existing clients?

<details markdown="1"><summary>Check</summary>

An existing client only reads the fields it already knows about; a new field it's never heard of is simply absent from its parsing logic, not an error. The client keeps working exactly as it did before the addition, since nothing it depended on changed.

</details>

2. ▢ Why can't a field removal or a meaning-change simply be shipped directly, the way an addition can?

<details markdown="1"><summary>Hint</summary>

Consider what a client that depends on the current field or meaning would experience the moment the change ships, with no advance notice.

</details>

<details markdown="1"><summary>Check</summary>

A client depending on the old field or meaning has no way to know it changed until its own logic fails, since removal or a meaning-change isn't invisible the way an addition is. It breaks working clients immediately rather than extending the contract for new ones, which is why it requires an announced transition period instead of a direct edit.

</details>

3. ▢ Why is an unenforced deprecation notice (marked deprecated for years with no actual removal) described as worse than no notice at all?

<details markdown="1"><summary>Check</summary>

It trains clients and integrating teams to ignore deprecation warnings entirely, since the label has never once corresponded to a real consequence. Once that trust is broken, a future deprecation notice that the API actually intends to enforce is likely to be ignored too, since nothing distinguishes it from the ones that never mattered.

</details>

4. ▢ Why does a deprecation need to be observable by a client's own tooling, not just documented in a changelog?

<details markdown="1"><summary>Check</summary>

Relying on every integrating team to have read and remembered a changelog entry is fragile; a machine-readable signal (a response header, a schema-level `deprecated` flag, a structured warning) lets automated tooling detect and flag the deprecation the way a compiler flags a deprecated function call, catching it even for teams that never saw the changelog or forgot about it.

</details>

5. ▢ Which claim correctly describes evolving an API contract safely?

   - a) Any change that adds new capability is automatically safe, regardless of what else it touches
   - b) Additive changes (new optional fields, new endpoints) are safe because old clients ignore what they don't recognize; removals and meaning-changes require an announced transition and a real, enforced deprecation timeline
   - c) A deprecation notice is primarily a documentation courtesy with no specific timeline attached
   - d) Deprecation only needs to be mentioned in a changelog, since responsible clients will read it

<details markdown="1"><summary>Check</summary>

**b)** That's the precise asymmetry this lesson covers: additions are safe by nature; removals and meaning-changes need a deliberate, honored transition. (a) is false: an addition that also silently changes existing behavior isn't purely additive and isn't automatically safe. (c) is false: a deprecation notice's value comes specifically from committing to a real, stated timeline, not vague courtesy language. (d) is false: relying solely on a changelog is fragile compared to a machine-detectable signal.

</details>

## Real-world reps

- [ ] Find a real API's changelog or version history (one you use or maintain). Identify one additive change and one removal or meaning-change, and check whether the removal had an announced transition period.
- [ ] For that same API, find a field or endpoint marked deprecated. Check whether it has a stated removal date or version, and whether that date has already passed without actual removal (an unenforced deprecation).
- [ ] Tomorrow: read the primary source's guidance on backward compatibility and deprecation in full, and note its specific recommendation for how long a deprecated field or method should remain functional before removal.

## Going further

- [Site: "API Improvement Proposals", Google](https://google.aip.dev/)
- [Docs: "API versioning", Stripe](https://docs.stripe.com/api/versioning)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
