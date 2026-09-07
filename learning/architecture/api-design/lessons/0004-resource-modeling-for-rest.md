---
title: 4. Resource Modeling for REST
description: Why REST models an API around nouns and state, not verbs, and how a resource hierarchy shapes what a URL means
type: lesson
---

# Lesson 4. Resource Modeling for REST

**Mission link:** Stage 3 opens REST/HTTP design. Lessons 1-3 covered the contract and error model that apply to any HTTP API; this lesson is the first REST-specific design decision, what a resource actually is, since pagination and filtering (lesson 5) only make sense once resources and collections are modeled correctly.
**Primary source:** [Site: "API Improvement Proposals", Google](https://google.aip.dev/)
**Prerequisites:** [Lesson 3](0003-problem-details-and-grpc-status-codes.md), [Contract](../GLOSSARY.md)

## Warm-up

1. ▢ What specific problem does RFC 9457's Problem Details format solve that a bare HTTP status code doesn't?

<details markdown="1"><summary>Check</summary>

A status code alone can't convey which specific field was invalid, why, or what would fix it. Problem Details standardizes a shape (`type`, `title`, `status`, `detail`, `instance`, plus extensible members) so a client can handle errors structurally instead of every API inventing its own ad hoc format.

</details>

2. ▢ Why is `type` the member a client should branch its logic on, rather than `detail`?

<details markdown="1"><summary>Check</summary>

`type` is meant to be a stable identifier for a specific kind of problem, a deliberate, documented part of the contract. `detail` is a human-readable explanation of this specific occurrence, and RFC 9457 doesn't promise its exact wording stays stable, so branching on it is the accidental-contract trap from lesson 1.

</details>

## Know this

### REST models nouns, not verbs: a resource is a thing, not an action

A **resource** is a named, addressable thing (a user, an order, a specific comment on a specific post), and its URL identifies that thing, not an action performed on it. The HTTP method carries the action: `GET /orders/42` reads order 42; `PUT /orders/42` replaces it; `DELETE /orders/42` removes it. An endpoint like `POST /createOrder` or `POST /getUserDetails` reintroduces the action into the URL itself, duplicating what the method already expresses and making the URL space grow with every new verb instead of staying organized around a fixed set of things.

### Collections and resources form a hierarchy, and the hierarchy is part of the contract

A **collection** is a named set of resources of the same kind (`/orders` is the collection of orders; `/orders/42` is one specific resource within it). Nesting a collection under a resource (`/users/7/orders`, the orders belonging to user 7) expresses a real ownership or containment relationship, and clients build logic around that nesting exactly the way lesson 1 described for any other observable behavior: once `/users/7/orders` means "user 7's orders," changing what the nesting means, or flattening it later, breaks every client that learned the relationship from the URL shape.

### Standard methods are a contract clients can rely on without reading extra docs

Google's AIP guidance names five **standard methods** (`List`, `Get`, `Create`, `Update`, `Delete`) that map onto HTTP's `GET` (collection), `GET` (single resource), `POST`, `PATCH` or `PUT`, and `DELETE` respectively, with consistent, predictable semantics for each. A client that has learned how `List` and `Get` behave on one resource type in an API can correctly predict how they behave on a different resource type in the same API, without reading that resource's documentation from scratch. Deviating from these standard shapes for no reason (a `List` that mutates state, a `Get` with side effects) breaks that transferable expectation, the REST-specific version of lesson 1's "contract is bigger than documentation."

### When an action doesn't fit CRUD, model it as its own resource or a custom method, deliberately

Not every real-world action is a clean create, read, update, or delete: "send this order for shipping," "approve this request," "refresh this token." Forcing these into a `PATCH` that secretly triggers a side effect hides the action inside what looks like a plain field update, an accidental-contract risk in the other direction (a client updating a field for an unrelated reason accidentally triggers the side effect). AIP guidance instead recommends either modeling the action as its own sub-resource (`POST /orders/42/shipment`) or as an explicitly named custom method (`POST /orders/42:approve`), so the action is visible in the URL rather than smuggled inside a generic update.

## Practice

1. ▢ Why does an endpoint like `POST /createOrder` violate REST's resource-modeling principle, and what would a more resource-oriented alternative look like?

<details markdown="1"><summary>Check</summary>

It puts the action ("create") into the URL itself, duplicating what the HTTP method (`POST`) already expresses, and grows the URL space with a new verb-named endpoint for every action instead of staying organized around a fixed set of resources. A more resource-oriented alternative is `POST /orders`, where the collection's URL identifies the thing (orders) and the method (`POST`) carries the action (create a new one).

</details>

2. ▢ What does nesting `/users/7/orders` communicate, and why does changing what that nesting means later break clients?

<details markdown="1"><summary>Hint</summary>

Consider what a client learns just from the URL shape, independent of any documentation.

</details>

<details markdown="1"><summary>Check</summary>

It communicates a real containment or ownership relationship: these are specifically user 7's orders. Clients build logic around this nesting the moment they observe it (lesson 1's Hyrum's Law), so if the API later changes what the nesting represents, or flattens the URL structure, any client that relied on the original meaning breaks, even if the change was never documented as a promise.

</details>

3. ▢ Why does having a consistent set of standard methods (`List`, `Get`, `Create`, `Update`, `Delete`) across an API's resource types matter to a client, beyond just being tidy?

<details markdown="1"><summary>Check</summary>

A client that has learned how these methods behave on one resource type can correctly predict their behavior on a different resource type in the same API, without reading fresh documentation for each one. This transferable expectation is itself part of the contract; deviating from standard semantics for no reason breaks a promise the client never had to be told about explicitly.

</details>

4. ▢ An API needs to support "approve this request." Contrast hiding this inside a `PATCH` that sets a hidden internal flag versus modeling it as an explicit custom method or sub-resource. What risk does the first approach create?

<details markdown="1"><summary>Check</summary>

Hiding the action inside a generic-looking `PATCH` risks a client updating an unrelated field for an unrelated reason and accidentally triggering the approval side effect, since nothing in the request shape signals that this update does more than update a field. Modeling it as an explicit custom method (`POST /requests/42:approve`) or a sub-resource makes the action visible in the URL, so a client can't trigger it by accident and can reason about it as its own operation.

</details>

5. ▢ Which claim correctly describes REST resource modeling?

    - a) A resource's URL should describe the action being taken on it, since that's clearer to read
    - b) A resource identifies a thing, the HTTP method carries the action, and nesting a collection under a resource expresses a real relationship clients will build logic around
    - c) Standard methods (List, Get, Create, Update, Delete) should be customized per resource type to fit each resource's specific needs
    - d) Any action that doesn't fit CRUD should be forced into the closest-matching standard method, even if it has side effects the method name doesn't suggest

<details markdown="1"><summary>Check</summary>

**b)** That's the actual REST resource-modeling principle: nouns for resources, methods for actions, and nesting as a real, contract-bearing relationship. (a) is false: it's exactly the anti-pattern (`POST /createOrder`) this lesson opens with. (c) is false: consistency across resource types is what gives standard methods their transferable value; customizing them per resource undermines that. (d) is false: forcing a side-effecting action into a generic-looking method is the accidental-contract risk this lesson specifically warns against; a dedicated sub-resource or custom method is the better fit.

</details>

## Real-world reps

- [ ] Find a real API's URL structure (one you use or maintain). Check whether its endpoints are modeled as resources (nouns, with methods carrying the action) or as verb-named endpoints (`/createX`, `/getY`).
- [ ] For that same API, find one action that doesn't cleanly fit create/read/update/delete (an approval, a state transition, a computed action). Check how it's modeled: a custom method, a sub-resource, or hidden inside a generic update.
- [ ] Tomorrow: read the primary source's guidance on standard methods and resource-oriented design in full, and note its specific recommendation for naming custom methods that don't fit the standard five.

## Going further

- [Site: "API Improvement Proposals", Google](https://google.aip.dev/)
- [RFC 9110: "HTTP Semantics", IETF](https://www.rfc-editor.org/rfc/rfc9110)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
