---
title: 3. RFC 9457 Problem Details and gRPC Status Codes
description: A structured, machine-readable error format for HTTP, gRPC's parallel status-code vocabulary, and designing one error model that works across both
type: lesson
---

# Lesson 3. RFC 9457 Problem Details and gRPC Status Codes

**Mission link:** This is stage 2's capstone. Lesson 2 established what an HTTP status code promises on its own; this lesson covers the structured format that carries more than a code can alone, plus gRPC's parallel vocabulary, closing the mission's requirement to design an error model across both REST/HTTP and gRPC.
**Primary source:** [RFC 9457: "Problem Details for HTTP APIs", IETF](https://www.rfc-editor.org/rfc/rfc9457)
**Prerequisites:** [Lesson 2](0002-http-status-codes-and-error-semantics.md), [Contract](../GLOSSARY.md)

## Warm-up

1. ▢ Why should a client retry a `503` but not a `400`?

<details markdown="1"><summary>Check</summary>

`503` signals a transient, likely temporary server-side problem, so retrying (ideally after any `Retry-After` duration) has a real chance of succeeding. `400` signals the request itself is malformed; an identical retry fails identically until the request is actually fixed.

</details>

2. ▢ Why is idempotency a property of the HTTP method rather than the status code returned?

<details markdown="1"><summary>Check</summary>

Idempotency describes whether repeating the identical request has the same effect as making it once, a property RFC 9110 defines per method (`GET`, `PUT`, `DELETE` are idempotent; `POST` is not). The status code only reports the outcome of one specific attempt; it doesn't change what repeating the same request would do.

</details>

## Know this

### A status code alone can't carry enough detail

A `400` tells a client "your request was invalid," but not *which* field, *why*, or what would fix it. Before RFC 9457, APIs invented ad hoc JSON error shapes (`{"error": "..."}`, `{"message": "...", "code": "..."}`, one per API), forcing every client integration to learn a bespoke format. RFC 9457's **Problem Details** format standardizes this: a JSON (or XML) object with defined members (`type`, a URI identifying the problem type; `title`, a short human-readable summary; `status`, the HTTP status code; `detail`, a human-readable explanation specific to this occurrence; `instance`, a URI identifying this specific occurrence), extensible with problem-specific members for machine-readable detail (which field was invalid, what constraint it violated).

### The `type` member is what makes it machine-readable, not just prettier

The critical piece is `type`: a URI that identifies the specific *kind* of problem, meant to be dereferenceable to human-readable documentation about that problem type, and, more importantly, meant to be a stable identifier a client's code can branch on. A client checking `type == "https://api.example.com/errors/insufficient-funds"` is checking something the API has promised to keep meaning that specific thing, unlike parsing the prose in `detail`, which RFC 9457 explicitly does not promise will stay stable or parseable. This is lesson 1's contract distinction applied directly: `type` is deliberate contract; `detail`'s exact wording is not.

### gRPC's status codes are a parallel, not identical, vocabulary

gRPC uses its own status code set (`OK`, `CANCELLED`, `INVALID_ARGUMENT`, `NOT_FOUND`, `ALREADY_EXISTS`, `PERMISSION_DENIED`, `UNAUTHENTICATED`, `RESOURCE_EXHAUSTED`, `FAILED_PRECONDITION`, `UNAVAILABLE`, and others), attached to every RPC response as an integer code plus a string description, analogous to HTTP's status line but with different specific codes and a materially different structure (no built-in equivalent to HTTP's `4xx`/`5xx` classing). Some gRPC codes are reserved: the gRPC library itself never generates `INVALID_ARGUMENT`, `NOT_FOUND`, `ALREADY_EXISTS`, `FAILED_PRECONDITION`, `ABORTED`, `OUT_OF_RANGE`, or `DATA_LOSS`, so an application seeing one of these knows the *application*, not the transport layer, produced it, a useful signal when debugging.

### Designing one error model that spans both

The mission's actual requirement is a single error model conceptually consistent across REST/HTTP and gRPC, not identical wire formats (they can't be identical; the transports differ). The pattern: define a small, stable set of problem-type identifiers (or gRPC error-detail messages, via the `google.rpc.Status` extension mechanism) that mean the same thing regardless of transport, mapped to the appropriate status code on each side (`INVALID_ARGUMENT` in gRPC maps naturally to `400` with a Problem Details `type` describing the same validation failure over HTTP). A client integrating with either transport should be able to branch on the same conceptual error, insufficient funds, resource not found, rate limited, using whichever transport-native mechanism carries that identifier.

## Practice

1. ▢ What specific problem does RFC 9457's Problem Details format solve that a bare HTTP status code doesn't?

<details markdown="1"><summary>Check</summary>

A status code alone can't convey which specific field was invalid, why, or what would fix it, and without a standard shape, every API invents its own ad hoc error JSON, forcing every client to learn a bespoke format. Problem Details standardizes a shape (`type`, `title`, `status`, `detail`, `instance`, plus extensible members) so clients can handle errors structurally across different APIs.

</details>

2. ▢ Why is `type` the member a client should branch its logic on, rather than `detail`?

<details markdown="1"><summary>Hint</summary>

Consider which member RFC 9457 actually promises will stay stable.

</details>

<details markdown="1"><summary>Check</summary>

`type` is meant to be a stable identifier for a specific kind of problem, the deliberate, documented part of the error contract a client can safely check against. `detail` is a human-readable explanation of this specific occurrence, and RFC 9457 doesn't promise its exact wording will stay stable or parseable, so branching logic on it is exactly the accidental-contract trap from lesson 1.

</details>

3. ▢ Why does it matter that gRPC never generates certain status codes (like `INVALID_ARGUMENT` or `NOT_FOUND`) from the library itself?

<details markdown="1"><summary>Check</summary>

It means an application seeing one of those codes knows it was produced by the application's own logic, not by a transport-level failure, which is a useful signal for distinguishing "my service explicitly rejected this" from "something broke in the RPC machinery itself" (which would surface as one of the library-generated codes instead).

</details>

4. ▢ A team wants clients to handle "insufficient funds" the same way whether they're calling the REST or the gRPC version of an API. Describe an approach that achieves this without requiring identical wire formats.

<details markdown="1"><summary>Check</summary>

Define one stable, transport-independent identifier for "insufficient funds" (a Problem Details `type` URI on the REST side, a corresponding error-detail identifier via `google.rpc.Status` on the gRPC side), each mapped to the transport-appropriate status code (an HTTP `4xx` with that `type`, a gRPC `FAILED_PRECONDITION` or similar with that detail). A client can then branch on the same conceptual identifier regardless of which transport it used, without the two wire formats needing to be identical.

</details>

5. ▢ Which claim correctly describes designing an error model across REST and gRPC?

    - a) The wire formats must be made byte-for-byte identical across both transports for the error model to count as consistent
    - b) A consistent error model means the same conceptual error types are identifiable across transports, using each transport's native mechanism (Problem Details `type` for HTTP, structured detail for gRPC), not identical wire formats
    - c) gRPC status codes are simply renamed HTTP status codes with a one-to-one mapping
    - d) A client should always branch on the human-readable `detail` field, since it contains the most specific information

<details markdown="1"><summary>Check</summary>

**b)** That's the actual, achievable consistency the mission requires: same conceptual errors, transport-native representations. (a) is false and impossible, since HTTP and gRPC have structurally different response formats. (c) is false: gRPC's status codes are their own vocabulary with different granularity and no built-in class structure like HTTP's `4xx`/`5xx`. (d) is false: `detail` is explicitly not promised to be stable, exactly the accidental-contract trap `type` exists to avoid.

</details>

## Real-world reps

- [ ] Find a real API's error response format (one you use or maintain). Check whether it follows RFC 9457's Problem Details shape, an ad hoc equivalent, or nothing structured at all, and whether it has a `type`-like stable identifier a client could safely branch on.
- [ ] For a gRPC service you know of (or gRPC's public documentation for a service you've used), find one status code it returns and check whether it's one of the library-reserved codes or an application-generated one.
- [ ] Tomorrow: read RFC 9457's full member definitions in full, and design a Problem Details response (on paper) for one real error case from your own work, naming its `type`, `title`, and one extension member.

## Going further

- [RFC 9457: "Problem Details for HTTP APIs", IETF](https://www.rfc-editor.org/rfc/rfc9457)
- [Docs: "Status Codes", gRPC](https://grpc.io/docs/guides/status-codes/)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
