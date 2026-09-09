---
title: 6. Proto3 and gRPC Service Design
description: How proto3's field numbers, not field names, are the real wire contract, and how a gRPC service is structured around RPC methods rather than resources
type: lesson
---

# Lesson 6. Proto3 and gRPC Service Design

**Mission link:** Stage 4 opens gRPC design. Everything in stage 3 assumed HTTP/JSON; gRPC is a materially different transport and message format, and this lesson is the foundational contract unit, a proto3 message and its field numbers, before lesson 7 covers streaming and the same use-case-in-gRPC comparison.
**Primary source:** [Docs: "Language Guide (proto3)", Protocol Buffers](https://protobuf.dev/programming-guides/proto3/)
**Prerequisites:** [Lesson 5](0005-pagination-and-filtering.md), [Contract](../GLOSSARY.md)

## Warm-up

1. ▢ Why does offset-based pagination risk silently skipping or duplicating items under concurrent writes?

<details markdown="1"><summary>Check</summary>

A numeric offset identifies a position in the collection, and that position shifts whenever an item is inserted or deleted before it; a client paging through sequential offsets can therefore skip an item that shifted into an already-seen position, or see one twice, with no error raised.

</details>

2. ▢ Why should a pagination cursor be treated as opaque by the client?

<details markdown="1"><summary>Check</summary>

So the server remains free to change the cursor's internal encoding or sort key later without breaking any client, since the client only ever depends on passing the token back unmodified, never on parsing or constructing it.

</details>

## Know this

### A proto3 message's real contract is field numbers, not names

A proto3 message defines fields with both a name and a **field number** (`string name = 1;`, `int32 age = 2;`). The field number, not the name, is what gets encoded on the wire; the name exists only for generated code readability. This means renaming a field is safe (the wire format is unaffected), but reusing or changing a field's number is not, since a message serialized under an old definition and deserialized under a new one is matched up by number. This inverts the usual REST/JSON intuition, where a field's *name* is the part of the contract a client depends on; in proto3, the number is the deliberate contract, and the name is comparatively free to change.

### Adding fields is safe; removing or renumbering is not

proto3 is designed so that **adding a new field with a new, unused number** is a backward-compatible change: old clients simply ignore fields they don't recognize, and new clients see a default value (proto3's zero-value defaults, since proto3 has no explicit "required" fields) for a field an old server never set. **Removing a field or reusing its number for something else** is unsafe: a client still sending the old field number, expecting it to mean what it used to, gets data interpreted according to the new, incompatible definition. proto3 supports explicitly marking a field number `reserved` specifically to prevent accidental reuse after a field is removed.

![Two side-by-side message evolutions. On the left, safe: v1 has field 1 name and field 2 age; v2 adds field 3 email, a brand new number, so an old client reading v2 data still reads fields 1 and 2 correctly and simply ignores field 3. On the right, unsafe: v1 has field 1 name and field 2 age; v2 removes age and reuses field number 2 for a new email field, so an old client still expecting field 2 to mean age instead receives the email value, silently misinterpreted as an age.](images/proto3-field-number-safety.svg)

### A gRPC service groups RPC methods, not resources

A gRPC **service** definition (`service OrderService { rpc GetOrder(...) returns (...); }`) is organized around named remote procedure calls, not around resources and a fixed set of standard methods the way REST is (lesson 4). This is a genuinely different shape of contract: instead of `GET /orders/42` (a resource with a method applied to it), gRPC exposes `OrderService.GetOrder(request) -> response`, an explicit function-call-like operation, with the request and response each being their own proto3 messages. Nothing forces a gRPC service to model resources at all, though AIP-style guidance (already used for REST in lessons 4-5) recommends structuring gRPC services around resource-oriented methods (`GetOrder`, `ListOrders`, `CreateOrder`) specifically so the same conceptual design translates across both transports.

### Why this matters for evolving a gRPC API safely

Because field numbers, not names or JSON key ordering, are proto3's actual wire contract, safely evolving a gRPC API means the same discipline as any other contract (lesson 1): decide deliberately what's allowed to change (add a field, reserve a removed one's number) and what isn't (reuse a number, change an existing field's type incompatibly). A team that doesn't know this discipline exists is exposed to a subtle, hard-to-catch failure mode: reusing a field number after removing an old field looks like a harmless cleanup in the `.proto` file, but silently reinterprets old data under a new meaning for any client still using the old definition.

## Practice

1. ▢ Why is renaming a proto3 field's name a safe change, while changing its field number is not?

<details markdown="1"><summary>Check</summary>

The field number, not the name, is what actually gets encoded on the wire and used to match fields between a message's serialized bytes and its definition; the name only affects generated code readability. Renaming leaves the wire encoding untouched, but changing the number breaks the match between old serialized data and the field it was meant to represent.

</details>

2. ▢ Why is reusing a removed field's number for a new, unrelated field unsafe, and what mechanism does proto3 provide to prevent this mistake?

<details markdown="1"><summary>Hint</summary>

Consider what an old client, still using the previous message definition, would do with data serialized under the new one.

</details>

<details markdown="1"><summary>Check</summary>

A client still using the old message definition expects that field number to mean what it used to; if the number is reused for something new, old clients or old data get reinterpreted according to the new, incompatible meaning, silently corrupting data rather than raising an error. proto3 provides a `reserved` keyword to explicitly mark a removed field's number (and name) so it can't be accidentally reused later.

</details>

3. ▢ Contrast how a gRPC service is structured (`OrderService.GetOrder(request)`) against how a REST resource is structured (`GET /orders/{id}`, lesson 4).

<details markdown="1"><summary>Check</summary>

REST organizes around a resource (the URL identifies a thing) with a small set of standard methods (the HTTP method carries a standard action). gRPC organizes around named RPC methods within a service definition, an explicit function-call-like operation with its own request and response message types, rather than a resource with a method applied to it. Nothing structurally forces a gRPC service to be resource-oriented, though AIP-style guidance recommends designing gRPC methods to mirror the same resource concepts REST uses.

</details>

4. ▢ A team removes a deprecated field from a proto3 message but doesn't mark its old number as `reserved`. A future engineer adds a new field and, not knowing the number was previously used, accidentally reuses it. What goes wrong for any client still running the old proto definition?

<details markdown="1"><summary>Check</summary>

A client running the old definition, if it ever receives a message serialized under the new definition, will interpret whatever value now occupies that field number as if it were the old, removed field's value, since it's matching purely by number. This silently produces wrong data rather than an obvious error, exactly the failure `reserved` exists to prevent by making the number's reuse a compile-time mistake instead of a runtime surprise.

</details>

5. ▢ Which claim correctly describes proto3's wire contract?

    - a) A proto3 field's name is the part of the contract that must never change, the same as a REST JSON field name
    - b) A proto3 field's number, not its name, is encoded on the wire and is the part of the contract that must not be reused or changed once assigned
    - c) Removing a field from a proto3 message has no risk as long as the field's name is never reused
    - d) gRPC services must be structured as one RPC method per REST-style standard method (List, Get, Create, Update, Delete)

<details markdown="1"><summary>Check</summary>

**b)** That's proto3's actual wire contract, the inverse of the REST/JSON intuition that names are what's stable. (a) is false and is exactly the REST intuition this lesson says doesn't transfer to proto3. (c) is false: the risk is in the *number* being reused, regardless of whether the old name is reused too. (d) is false: nothing structurally requires this mapping, though AIP-style guidance recommends it as a design choice, not a protocol requirement.

</details>

## Real-world reps

- [ ] Find a real `.proto` file (one you maintain, or a well-known open-source one). Check whether any field numbers are marked `reserved`, and if so, look at the git history to see what field used to occupy that number.
- [ ] For the same file, check whether its service definitions are organized around resource-oriented methods (`GetX`, `ListX`, `CreateX`) or a more ad hoc set of RPC names, and compare that to the REST resource modeling from lesson 4.
- [ ] Tomorrow: read the primary source's section on field numbers and message evolution in full, and note its guidance on which field number ranges are reserved for future protocol use versus safe for application use.

## Going further

- [Docs: "Language Guide (proto3)", Protocol Buffers](https://protobuf.dev/programming-guides/proto3/)
- [Docs: "Status Codes", gRPC](https://grpc.io/docs/guides/status-codes/)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
