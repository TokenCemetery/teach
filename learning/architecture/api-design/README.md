---
title: API Design
description: "Design an interface others depend on: the contract, its errors, and how it changes without breaking them"
type: topic
---

# Learning: API Design

Be able to design a versioned public API (REST/HTTP or gRPC) from scratch, and to evolve an existing one, changing its contract without breaking the clients that depend on it.

**Latest lesson:** _none yet_

## Success looks like

- Design a REST/HTTP or gRPC API's contract, including its error model, for a stated use case.
- Evolve an existing API's contract (adding, deprecating, or changing a field or endpoint) without breaking clients, and explain the versioning or migration strategy used.
- Treat authentication, authorization and rate limiting as part of the contract a client depends on, not an afterthought bolted on separately.

## Constraints

- Covers both REST/HTTP and gRPC, since the mission's guarantees apply across both.

## Out of scope

- Making the compiler reject an impossible state inside one codebase: that is `programming/typescript`. This workspace is the same instinct applied across a boundary where there is no shared compiler.

## The arc

{N} stages, {start} to {end}. Not a lesson list: a stage takes several lessons, and the boundaries are soft.

| Stage | Covers | Done when |
|---|---|---|
| 1. {Name} | {What it covers} | {The capability that closes the stage} |

## Lessons

Work through these in order.

| # | Lesson | Teaches |
|---|---|---|
| _none yet_ | | |

## Reference

- [Glossary](GLOSSARY.md): canonical terms for this topic
- [Resources](RESOURCES.md): trusted sources

## How this works

Each lesson is short and self-contained. Answer keys are collapsed: recall first, then open them. The real-world reps matter more than the reading, and spacing them out is the point. Anything still unclear at the end of a lesson is worth chasing to its primary source before moving on.
