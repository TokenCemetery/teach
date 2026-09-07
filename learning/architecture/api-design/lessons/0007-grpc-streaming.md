---
title: 7. gRPC Streaming and Designing the Same Use Case
description: The four kinds of gRPC RPC, when each fits, and designing one use case as both a REST and a gRPC contract
type: lesson
---

# Lesson 7. gRPC Streaming and Designing the Same Use Case

**Mission link:** This is stage 4's capstone. Lesson 6 covered proto3's wire contract and gRPC's service structure; this lesson covers the four RPC kinds gRPC actually offers, and closes the stage with the mission's second success criterion applied to gRPC specifically: designing the same use case as both a REST and a gRPC contract.
**Primary source:** [Docs: "Core concepts, architecture and lifecycle", gRPC](https://grpc.io/docs/what-is-grpc/core-concepts/)
**Prerequisites:** [Lesson 6](0006-proto3-and-grpc-service-design.md), [Contract](../GLOSSARY.md)

## Warm-up

1. ▢ Why is a proto3 field's number, not its name, the part of the wire contract that must never be reused or changed?

<details markdown="1"><summary>Check</summary>

The field number, not the name, is what actually gets encoded on the wire and used to match fields between serialized bytes and the message definition. The name only affects generated code readability, so renaming is safe, but changing or reusing a number breaks the match for anything still using the old definition.

</details>

2. ▢ How is a gRPC service structured, compared to a REST resource with standard methods?

<details markdown="1"><summary>Check</summary>

A gRPC service groups named RPC methods, each an explicit function-call-like operation with its own request and response message types, rather than a resource with a small, standard set of methods applied to it the way REST does. Nothing structurally forces resource orientation in gRPC, though AIP-style guidance recommends mirroring REST's resource concepts as a design choice.

</details>

## Know this

### Four RPC kinds, not one, and each is a distinct promise

gRPC defines four kinds of service method: **unary** (one request, one response, like a normal function call), **server streaming** (one request, a stream of responses the client reads until the server signals completion), **client streaming** (a stream of requests from the client, one response once the server has processed them), and **bidirectional streaming** (both sides send a stream of messages independently, in either order, over the same call). Choosing among these is a design decision with real consequences, not a stylistic preference: gRPC guarantees message ordering within a single RPC call, but that ordering guarantee only applies within whichever stream direction is actually being used.

### Streaming exists to solve a specific shape of problem, not to be more advanced

Server streaming fits a use case where one request logically produces many results over time that the client wants to start processing before all of them exist (a large paginated result set streamed incrementally instead of fetched page by page, a live feed of events). Client streaming fits the reverse (uploading a large file in chunks, then getting one confirmation once the server has processed the whole upload). Bidirectional streaming fits genuinely interactive, real-time exchanges (a chat session, a live collaborative editing session) where either side needs to send at any time independent of the other. A unary call remains the right default for anything that's a single request producing a single, bounded response, most of an API's surface; reaching for streaming when a use case is really just a paginated list (lesson 5) or a bounded, one-shot operation adds real complexity (managing an open stream, handling partial failure mid-stream) without a corresponding benefit.

### Designing the same use case both ways surfaces what each transport actually optimizes for

Take "list a user's orders, most recent first, filterable by status" (lesson 5's REST example). As REST: `GET /users/{id}/orders?status=shipped&page_token=...`, cursor-paginated, one request per page. As gRPC: a `ListOrders` unary RPC taking the same filter and page token as request fields, returning a page of results and a next-page token in the response message, structurally the same design translated into proto3 request/response messages, *or*, if the use case shifts to "stream every matching order as it's found, without waiting for a full page to accumulate," a server-streaming RPC instead, a design REST's request/response model doesn't cleanly support without inventing something like long-polling or Server-Sent Events on top of it.

### The actual decision: match the RPC kind, and the transport, to the interaction shape

The mission's requirement to design the same use case for both REST and gRPC isn't about producing two equivalent-looking contracts for their own sake; it's about recognizing that most use cases map cleanly to unary gRPC and ordinary REST (the same request/response shape, different encoding), while a genuine streaming need (large results, uploads in chunks, real-time bidirectional exchange) is a signal that plain REST is the wrong fit and gRPC's streaming kinds, or a REST-adjacent alternative like Server-Sent Events, are worth reaching for specifically because of that shape, not because gRPC is assumed to be a strictly "better" choice.

## Practice

1. ▢ Name the four kinds of gRPC RPC and, in one phrase each, what shape of request/response pattern each one is for.

<details markdown="1"><summary>Check</summary>

Unary: one request, one response. Server streaming: one request, a stream of responses. Client streaming: a stream of requests, one response. Bidirectional streaming: both sides stream messages independently over the same call.

</details>

2. ▢ A use case needs a client to upload a large file in chunks and get one confirmation once the whole upload is processed. Which RPC kind fits, and why would a unary RPC be a poor fit instead?

<details markdown="1"><summary>Hint</summary>

Consider what a unary call would require the client to do with a large file before it could even send the request.

</details>

<details markdown="1"><summary>Check</summary>

Client streaming fits: the client sends a stream of chunk messages, and the server responds once with a single confirmation after processing the full upload. A unary RPC would require the entire file to be assembled into one request message before sending, which is impractical or impossible for very large files and loses the ability to start processing before the upload completes.

</details>

3. ▢ Why is reaching for gRPC streaming to implement what's really just a paginated list (lesson 5) usually the wrong design choice?

<details markdown="1"><summary>Check</summary>

A paginated list is a bounded, request-per-page interaction that unary RPCs (or REST's cursor-based pagination) already handle cleanly; adding a stream introduces real complexity, managing an open connection, handling partial failure mid-stream, without solving a problem the use case actually has. Streaming is worth its complexity specifically for genuinely unbounded or real-time interaction shapes, not as a default upgrade.

</details>

4. ▢ Design "list a user's orders, filterable by status" as both a unary gRPC RPC and, separately, describe what would change if the use case shifted to "stream every matching order as it's found."

<details markdown="1"><summary>Check</summary>

As unary gRPC: a `ListOrders(ListOrdersRequest) returns (ListOrdersResponse)` RPC, where the request carries the user ID, status filter, and page token, and the response carries a page of orders plus a next-page token, structurally mirroring the REST design from lesson 5 but as proto3 messages. If the use case shifted to streaming every matching order as found, the design would change to a server-streaming RPC (`rpc StreamOrders(StreamOrdersRequest) returns (stream Order)`), where the client reads orders incrementally as the server finds them rather than waiting for a full page to accumulate, a shape plain REST doesn't support cleanly without an add-on like Server-Sent Events.

</details>

5. ▢ Which claim correctly describes choosing among gRPC's RPC kinds?

   - a) Streaming RPCs should be preferred by default since they're more efficient than unary calls
   - b) The right RPC kind matches the actual interaction shape (bounded single response, incremental results, chunked upload, real-time bidirectional exchange); unary remains the correct default for most of an API's surface
   - c) Client streaming and server streaming are interchangeable, since both involve a stream on one side
   - d) A use case that's really a paginated list should be redesigned as server streaming for consistency with gRPC's other capabilities

<details markdown="1"><summary>Check</summary>

**b)** That's the actual design discipline: match the RPC kind to the interaction shape, don't default to streaming out of assumed superiority. (a) is false: streaming adds real complexity (open connections, partial-failure handling) that's only worth it for a genuine streaming need. (c) is false: client streaming (many requests, one response) and server streaming (one request, many responses) are opposite shapes, not interchangeable. (d) is false: a bounded, page-at-a-time list is exactly the case where a unary (or REST) request/response design remains the better fit, per this lesson's guidance.

</details>

## Real-world reps

- [ ] Find a real gRPC service definition you have access to (or a well-known open-source `.proto` file). Identify which of the four RPC kinds each method uses, and for any streaming method, check whether the interaction shape actually needs streaming or could be a unary call instead.
- [ ] Using lesson 5's REST design for "list a user's orders, filterable by status," write the equivalent gRPC service definition (request and response messages, the RPC signature) and compare which pieces translated directly versus which needed rethinking for proto3.
- [ ] Tomorrow: read the primary source's section on all four RPC kinds and the RPC life cycle in full, and note what happens, per the docs, when a client or server ends a streaming call early or encounters an error mid-stream.

## Going further

- [Docs: "Core concepts, architecture and lifecycle", gRPC](https://grpc.io/docs/what-is-grpc/core-concepts/)
- [Docs: "Language Guide (proto3)", Protocol Buffers](https://protobuf.dev/programming-guides/proto3/)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
