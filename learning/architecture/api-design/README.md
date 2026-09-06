---
title: API Design
description: "Design an interface others depend on: the contract, its errors, and how it changes without breaking them"
type: topic
---

# Learning: API Design

Be able to design a versioned public API (REST/HTTP or gRPC) from scratch, and to evolve an existing one, changing its contract without breaking the clients that depend on it.

**Latest lesson:** [1. The Contract](lessons/0001-the-contract.md)

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

## Reference

- [Glossary](GLOSSARY.md): canonical terms for this topic
- [Resources](RESOURCES.md): trusted sources

## How this works

Each lesson is short and self-contained. Answer keys are collapsed: recall first, then open them. The real-world reps matter more than the reading, and spacing them out is the point. Anything still unclear at the end of a lesson is worth chasing to its primary source before moving on.
