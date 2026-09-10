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
