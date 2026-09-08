---
title: API Design
description: "Design an interface others depend on: the contract, its errors, and how it changes without breaking them"
type: topic
---

# Learning: API Design

Be able to design a versioned public API (REST/HTTP or gRPC) from scratch, and to evolve an existing one, changing its contract without breaking the clients that depend on it.

**Latest lesson:** [10. Auth, Authz, and Rate Limiting as Contract](lessons/0010-auth-authz-and-rate-limiting-as-contract.md)

## Success looks like

- Design a REST/HTTP or gRPC API's contract, including its error model, for a stated use case.
- Evolve an existing API's contract (adding, deprecating, or changing a field or endpoint) without breaking clients, and explain the versioning or migration strategy used.
- Treat authentication, authorization and rate limiting as part of the contract a client depends on, not an afterthought bolted on separately.

## Constraints

- Assumes professional experience building a service with HTTP or RPC; no prior formal API-design study required.
- Covers both REST/HTTP and gRPC, since the mission's guarantees apply across both.

## Out of scope

- Making the compiler reject an impossible state inside one codebase: that is `programming/typescript`. This workspace is the same instinct applied across a boundary where there is no shared compiler.

## The arc

Six stages, the contract to a treated-as-contract auth model. A stage takes several lessons and the boundaries are soft; what makes a stage done is the capability, not the lesson count.

| Stage | Lessons | Covers | Done when |
|---|---|---|---|
| 1. The contract | 0001 | What a client can rely on is bigger than what's documented (Hyrum's Law) | Can name a contract's implicit surface beyond its documented one |
| 2. Error models | 0002 to 0003 | HTTP status codes, RFC 9457 Problem Details, gRPC status codes | Can design an error model for a stated API |
| 3. REST/HTTP design | 0004 to 0005 | Resource modeling, pagination and filtering, AIP-style guidance | Can design a REST contract for a stated use case |
| 4. gRPC design | 0006 to 0007 | proto3, service design, streaming | Can design a gRPC contract for the same use case |
| 5. Versioning and evolution | 0008 to 0009 | Additive changes, deprecation, migration strategy | Can evolve an existing API's contract without breaking its clients |
| 6. Auth, authz and rate limiting as contract | 0010 | Treating these as part of what a client depends on, not an afterthought | Can design auth and rate limiting as contract, not bolted on separately |

## Lessons

Work through these in order.

| # | Lesson | Teaches |
|---|---|---|
| [0001](lessons/0001-the-contract.md) | The Contract | What a client can rely on is bigger than what you documented, and design has to account for both |
| [0002](lessons/0002-http-status-codes-and-error-semantics.md) | HTTP Status Codes and Error Semantics | What a status code actually promises a client about safety, idempotency, and what to do next, beyond the vague 2xx/4xx/5xx grouping |
| [0003](lessons/0003-problem-details-and-grpc-status-codes.md) | RFC 9457 Problem Details and gRPC Status Codes | A structured, machine-readable error format for HTTP, gRPC's parallel status-code vocabulary, and designing one error model that works across both |
| [0004](lessons/0004-resource-modeling-for-rest.md) | Resource Modeling for REST | Why REST models an API around nouns and state, not verbs, and how a resource hierarchy shapes what a URL means |
| [0005](lessons/0005-pagination-and-filtering.md) | Pagination, Filtering, and Designing a REST Contract | Why cursor-based pagination beats offsets at scale, how filtering stays a stable contract, and putting resource modeling together into a full REST design |
| [0006](lessons/0006-proto3-and-grpc-service-design.md) | Proto3 and gRPC Service Design | How proto3's field numbers, not field names, are the real wire contract, and how a gRPC service is structured around RPC methods rather than resources |
| [0007](lessons/0007-grpc-streaming.md) | gRPC Streaming and Designing the Same Use Case | The four kinds of gRPC RPC, when each fits, and designing one use case as both a REST and a gRPC contract |
| [0008](lessons/0008-additive-changes-and-deprecation.md) | Additive Changes and Deprecation | Why adding is usually safe and removing or changing meaning is usually not, and how to deprecate a field or endpoint without breaking clients on the spot |
| [0009](lessons/0009-versioning-and-migration-strategy.md) | Versioning and Migration Strategy | How to ship a genuine breaking change without breaking every existing integration at once, using Stripe's versioning strategy as a worked example |
| [0010](lessons/0010-auth-authz-and-rate-limiting-as-contract.md) | Auth, Authz, and Rate Limiting as Contract | Why scopes, not just tokens, and visible rate-limit state, not just a 429, are what make access control and quotas part of the deliberate contract |

## Reference

- [Glossary](GLOSSARY.md): canonical terms for this topic
- [Resources](RESOURCES.md): trusted sources
- [Error Models](reference/error-models.md): HTTP status codes, Problem Details members and gRPC status codes side by side, for when you are designing an error model rather than learning why it is contract
- [REST Resource Design](reference/rest-resource-design.md): resource names, the standard and custom methods, pagination and filtering, with the AIP rule each decision has to satisfy
- [gRPC Design](reference/grpc-design.md): proto3 field numbers, which schema changes are safe on the binary wire and which break JSON, the four RPC kinds, and the call semantics a gRPC contract inherits
- [Versioning and Evolution](reference/versioning-and-evolution.md): which changes break which kind of compatibility, the headers that make a deprecation visible to tooling, and the versioning models to choose between

## How this works

Each lesson is short and self-contained. Answer keys are collapsed: recall first, then open them. The real-world reps matter more than the reading, and spacing them out is the point. Anything still unclear at the end of a lesson is worth chasing to its primary source before moving on.
