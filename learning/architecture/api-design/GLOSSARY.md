---
title: Glossary
description: "Canonical terms for API design"
type: glossary
---

# API Design Glossary

Canonical terms for designing and evolving an interface others depend on.

## Terms

**Batch operation**:
A request that acts on several resources at once instead of one call per resource, requiring an explicit choice between atomic (all succeed or all fail) and partial success (each item reports its own result), since the two make genuinely different promises to the client.
_Avoid_: bulk operation (use interchangeably only when quoting a source; this workspace standardizes on "batch operation" as the term with a settled contract)

**Breaking-change detector**:
A tool (`buf breaking`, `oasdiff breaking`) that compares two versions of a contract artifact and reports only the changes that break an existing client, distinct from a style linter (Spectral), which checks a single document's conformance to a ruleset at one point in time with no notion of a previous version.
_Avoid_: linter (too broad; a style linter and a breaking-change detector check genuinely different properties and neither substitutes for the other)

**Contract**:
Every behavior of an API a client can rely on, whether deliberately documented or merely observed and depended on in practice (see Hyrum's Law).
_Avoid_: interface (too broad; a contract is specifically what's relied on, not the shape of the API alone)

**Field mask**:
A `google.protobuf.FieldMask`, a list of field paths (`user.displayName`) that either narrows a read to a subset of fields (a read mask, part of a partial response) or scopes a write to only the fields named (an update mask), travelling as a query parameter, header, or metadata entry rather than as a body field.
_Avoid_: assuming a read mask and an update mask behave identically; a read mask may allow non-terminal repeated fields where an update mask is not obligated to

**Hyrum's Law**:
The principle that with enough users of an API, every observable behavior, documented or not, will end up depended on by somebody.
_Avoid_: none in particular, but do not use as an excuse to skip documenting a deliberate contract

**Idempotency fingerprint**:
A value the server derives from a request's payload (a checksum, a field match, or a digest), checked alongside a repeated idempotency key to confirm the retry is genuinely the same request, not a different one reusing the key by mistake.
_Avoid_: hash (imprecise; a fingerprint can be a full digest, a partial-field match, or another scheme, not only a hash)

**Idempotency key**:
A unique, client-generated value (a UUID is the recommended form) attached to a non-idempotent request (`POST`, `PATCH`) via the `Idempotency-Key` header, letting the server recognize and safely respond to a retried request without reprocessing it.
_Avoid_: request ID (a different, often server-assigned concept; an idempotency key is specifically client-generated and retry-safety-oriented)

**Long-running operation**:
A method whose actual work may take longer than an ordinary request-response cycle, returning an operation resource (`name`, `done`, and eventually `response` or `error`) immediately instead of blocking until the work finishes.
_Avoid_: async job (use only when quoting a source that uses it; "long-running operation" and "operation resource" are this workspace's terms)

**OpenAPI document**:
A single machine-readable artifact describing a REST contract's paths, operations, and reusable schemas, which SDKs, mock servers, and structural or breaking-change checks can be generated or run from directly. Must include at least one of `components`, `paths`, or `webhooks`; its `openapi` field (the specification version) and `info.version` field (the API's own version) track different things and advance independently.
_Avoid_: Swagger file (the specification and its ecosystem are called OpenAPI since version 3.0; "Swagger" now properly refers only to a specific set of Smartbear tools)

**Optimistic concurrency**:
Detecting, at write time, whether a resource has changed since a client last read it (via `If-Match` and a strong ETag), rejecting the write with `412 Precondition Failed` if so, rather than locking the resource in advance or silently overwriting a concurrent change.
_Avoid_: pessimistic locking (a different strategy this workspace does not cover; optimistic concurrency detects a conflict after the fact instead of preventing one in advance)

**Partial response**:
A response narrowed to a client-requested subset of a resource's fields via a field mask, defaulting to every field when the mask is omitted; changing that default later is a breaking change, since every caller that omitted the mask relied on getting everything back.
_Avoid_: sparse fieldset (a JSON:API-specific term this workspace does not otherwise use; "partial response" and "field mask" are the terms in use here)

**Validator (HTTP)**:
An opaque identifier (an `ETag`) for a specific state of a representation. Strong validators change on any byte-level difference and support strong comparison (required for `If-Match`); weak validators (`W/` prefix) only change on a semantically significant difference and support only weak comparison (sufficient for `If-None-Match`).
_Avoid_: version number (a validator need not be sequential or human-meaningful; it only needs to support equality comparison)

**Webhook**:
A server-initiated HTTP request delivering an event notification to a client-registered URL, inverting who initiates the request compared to polling. Requires the receiver to verify a signature and timestamp tolerance, acknowledge quickly, and deduplicate by event ID, since neither delivery order nor a single delivery attempt is guaranteed.
_Avoid_: callback (too generic; this workspace uses "webhook" for this specific HTTP-delivery pattern)
