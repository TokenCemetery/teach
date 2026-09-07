---
title: 5. Pagination, Filtering, and Designing a REST Contract
description: Why cursor-based pagination beats offsets at scale, how filtering stays a stable contract, and putting resource modeling together into a full REST design
type: lesson
---

# Lesson 5. Pagination, Filtering, and Designing a REST Contract

**Mission link:** This is stage 3's capstone. Lesson 4 established what a resource and a collection are; this lesson covers how a client actually consumes a large collection safely, and closes the stage with the mission's first success criterion: designing a REST contract for a stated use case.
**Primary source:** [Site: "API Improvement Proposals", Google](https://google.aip.dev/)
**Prerequisites:** [Lesson 4](0004-resource-modeling-for-rest.md), [Contract](../GLOSSARY.md)

## Warm-up

1. ▢ Why does an endpoint like `POST /createOrder` violate REST's resource-modeling principle?

<details markdown="1"><summary>Check</summary>

It puts the action into the URL itself, duplicating what the HTTP method already expresses, and grows the URL space with a new verb-named endpoint for every action instead of staying organized around a fixed set of resources like `/orders`.

</details>

2. ▢ Why does nesting `/users/7/orders` matter beyond just being a convenient URL shape?

<details markdown="1"><summary>Check</summary>

It communicates a real containment relationship, these are specifically user 7's orders, and clients build logic around that nesting the moment they observe it (Hyrum's Law). Changing what the nesting means later breaks any client relying on the original meaning, even if that meaning was never explicitly documented.

</details>

## Know this

### Offset pagination looks simple and breaks under concurrent writes

**Offset-based pagination** (`?offset=100&limit=20`) asks for "the 20 items starting at position 100" in some ordering. This looks simple but has a real correctness problem: if an item is inserted or deleted before position 100 while a client is paging through, every subsequent page shifts, and the client can skip an item entirely or see the same item twice, without any error being raised. The pagination contract silently promises something ("position 100 means the same thing across requests") that concurrent writes make false.

### Cursor-based pagination makes the actual guarantee explicit

**Cursor-based pagination** (`?page_token=<opaque_token>&page_size=20`) instead returns an opaque token alongside each page, meaning "resume exactly after this specific item," typically derived from a stable field like a creation timestamp plus ID rather than a raw position. This survives concurrent inserts and deletes at other positions in the collection, since the cursor identifies a specific point in the sequence rather than a numeric offset that shifts when the collection changes size. The token being opaque (a client should not parse or construct one, only pass back what the server returned) is deliberate: it lets the server change the underlying implementation (the encoding, the sort key) without breaking the pagination contract, since the client never depended on the token's internal structure, only on passing it back unmodified.

### Filtering needs the same "stable, not incidental" discipline as resource modeling

A filter parameter (`?status=shipped`, `?created_after=2024-01-01`) becomes part of the contract the moment a client relies on it, exactly like any other observable behavior (lesson 1). Two design choices matter: which fields are actually filterable should be a deliberate, documented decision, not "whatever happens to be a column in the underlying database," since exposing an internal field as a filter parameter makes changing that internal representation a breaking change; and filter semantics (does `created_after` include the boundary date, is filtering case-sensitive) need to be specified precisely enough that a client doesn't have to guess or reverse-engineer them through trial and error.

### Putting it together: a full REST contract for a stated use case

Designing a REST contract now means resolving each of these pieces deliberately, not accidentally: the resource and collection hierarchy (lesson 4) that expresses the actual data model; the standard methods each resource type supports and their exact semantics; the error model (lessons 2-3) with a `type`-bearing Problem Details response; and, for any collection endpoint expected to grow large, cursor-based pagination plus an explicit, documented set of filterable fields. Skipping any one of these doesn't remove the decision, it just makes the decision "whatever the current implementation happens to do," which is exactly the accidental contract lesson 1 warned becomes expensive to change later.

## Practice

1. ▢ A client pages through `?offset=0&limit=20`, then `?offset=20&limit=20`, while another process deletes an item from position 15 between the two requests. What goes wrong?

<details markdown="1"><summary>Check</summary>

Because everything after position 15 shifts up by one after the deletion, the item that was at position 21 (which the client hasn't seen yet) moves to position 20, and the item that was at position 20 (which the client already saw on the first page) shifts to position 19, so it gets skipped entirely on the second page. The client silently misses an item, with no error raised.

</details>

2. ▢ Why is a pagination cursor supposed to be treated as opaque by the client, rather than something the client parses or constructs?

<details markdown="1"><summary>Hint</summary>

Consider what freedom this gives the server to change its own implementation later.

</details>

<details markdown="1"><summary>Check</summary>

If the client never depends on the cursor's internal structure, only on passing back exactly what the server gave it, the server is free to change the cursor's encoding or the underlying sort key later without breaking any client. If clients started parsing or constructing cursors themselves, the cursor's internal format would become an accidental contract the server couldn't safely change.

</details>

3. ▢ Why does exposing an internal database column as a filter parameter (`?internal_status_code=3`) create a risk that exposing a deliberately-designed filter (`?status=shipped`) doesn't?

<details markdown="1"><summary>Check</summary>

An internal column exposed directly as a filter ties the API's contract to the current database schema; changing that column later (renaming it, changing its type, restructuring the underlying table) becomes a breaking change for any client filtering on it. A deliberately-designed filter is a stable, documented abstraction the API commits to, decoupled from whatever the underlying storage actually looks like, so the storage can change without breaking clients.

</details>

4. ▢ Design, at a high level, a REST contract for a "list a user's orders, most recent first, filterable by status" use case, naming the pieces from this lesson and lesson 4 that the design needs to resolve.

<details markdown="1"><summary>Check</summary>

Resource and collection: `/users/{id}/orders` as the nested collection expressing ownership (lesson 4). Standard method: `List` (`GET`) on that collection. Pagination: cursor-based (`page_token`/`page_size`), since order history can grow large and should tolerate concurrent inserts without skipping or duplicating results. Filtering: a deliberately-named `status` parameter with documented semantics (which values are valid, how it combines with default sort order), not an internal database field exposed directly. Error model: a Problem Details response with a `type` for an invalid `status` value or malformed `page_token` (lessons 2-3).

</details>

5. ▢ Which claim correctly distinguishes offset from cursor-based pagination?

    - a) Offset pagination is always faster and should be preferred whenever performance matters
    - b) Offset pagination can silently skip or duplicate items under concurrent inserts or deletes, since a numeric position shifts as the collection changes; cursor-based pagination avoids this by identifying a specific point in the sequence instead
    - c) Cursor-based pagination requires the client to parse the cursor to know which page it's on
    - d) Filtering and pagination are unrelated design decisions with no shared discipline

<details markdown="1"><summary>Check</summary>

**b)** That's the precise correctness difference this lesson covers. (a) is false: this lesson makes no performance claim, only a correctness one, and offset pagination's simplicity doesn't make it safe under concurrent writes. (c) is false: a cursor is meant to be opaque, treated as an unparsed token the client passes back unmodified. (d) is false: both need the same discipline of being deliberately designed, stable contract surfaces rather than incidental exposure of the underlying implementation.

</details>

## Real-world reps

- [ ] Find a real API's list endpoint (one you use or maintain). Check whether it uses offset or cursor-based pagination, and if offset-based, whether its documentation acknowledges the skip/duplicate risk under concurrent writes.
- [ ] For that same endpoint, list its filterable parameters and check whether each maps to a deliberately-designed, documented field or appears to expose an internal implementation detail directly.
- [ ] Tomorrow: using this lesson and lesson 4, sketch a full REST contract (resource hierarchy, standard methods, pagination, filtering, error model) on paper for one real collection endpoint you know of, and compare it against what actually exists.

## Going further

- [Site: "API Improvement Proposals", Google](https://google.aip.dev/)
- [RFC 9457: "Problem Details for HTTP APIs", IETF](https://www.rfc-editor.org/rfc/rfc9457)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
