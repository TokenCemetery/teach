---
title: Glossary
description: "Canonical terms for API design"
type: glossary
---

# API Design Glossary

Canonical terms for designing and evolving an interface others depend on.

## Terms

**Contract**:
Every behavior of an API a client can rely on, whether deliberately documented or merely observed and depended on in practice (see Hyrum's Law).
_Avoid_: interface (too broad; a contract is specifically what's relied on, not the shape of the API alone)

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

**Optimistic concurrency**:
Detecting, at write time, whether a resource has changed since a client last read it (via `If-Match` and a strong ETag), rejecting the write with `412 Precondition Failed` if so, rather than locking the resource in advance or silently overwriting a concurrent change.
_Avoid_: pessimistic locking (a different strategy this workspace does not cover; optimistic concurrency detects a conflict after the fact instead of preventing one in advance)

**Validator (HTTP)**:
An opaque identifier (an `ETag`) for a specific state of a representation. Strong validators change on any byte-level difference and support strong comparison (required for `If-Match`); weak validators (`W/` prefix) only change on a semantically significant difference and support only weak comparison (sufficient for `If-None-Match`).
_Avoid_: version number (a validator need not be sequential or human-meaningful; it only needs to support equality comparison)

**Webhook**:
A server-initiated HTTP request delivering an event notification to a client-registered URL, inverting who initiates the request compared to polling. Requires the receiver to verify a signature and timestamp tolerance, acknowledge quickly, and deduplicate by event ID, since neither delivery order nor a single delivery attempt is guaranteed.
_Avoid_: callback (too generic; this workspace uses "webhook" for this specific HTTP-delivery pattern)
