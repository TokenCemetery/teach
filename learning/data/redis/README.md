---
title: Redis
description: "Use Redis for what it is: the memory model, eviction, persistence, and the patterns that quietly misuse it"
type: topic
---

# Learning: Redis

Be able to spot where an existing system is quietly misusing Redis, such as a cache treated as a store or a lock that is not one, and to design correct usage from scratch instead.

**Latest lesson:** [1. Memory and Eviction](lessons/0001-memory-and-eviction.md)

## Success looks like

- Given an existing system's use of Redis, identify whether it is treating a cache as a durable store, implementing a lock incorrectly, or running an unbounded keyspace, and say what breaks because of it.
- Design correct usage of Redis (bounded keyspace, appropriate eviction policy, real distributed lock) for a new use case from scratch.
- Compare Redis's persistence guarantees (RDB/AOF) against Postgres's WAL-backed durability, and say when reaching for Redis instead of a database is the right call versus an anti-pattern.
- Reason about Redis Cluster/Sentinel at the level of the compromises clustering introduces, without needing to operate one.

## Constraints

- None beyond what the mission states.

## Out of scope

- Operating a production Postgres instance: that is `data/postgres`, linked to for the comparison rather than restated.

## The arc

{N} stages, {start} to {end}. Not a lesson list: a stage takes several lessons, and the boundaries are soft.

| Stage | Covers | Done when |
|---|---|---|
| 1. {Name} | {What it covers} | {The capability that closes the stage} |

## Lessons

Work through these in order.

| # | Lesson | Teaches |
|---|---|---|
| [0001](lessons/0001-memory-and-eviction.md) | Memory and Eviction | Why Redis evicts keys at all, and the anti-pattern that follows from forgetting it |

## Reference

- [Glossary](GLOSSARY.md): canonical terms for this topic
- [Resources](RESOURCES.md): trusted sources

## How this works

Each lesson is short and self-contained. Answer keys are collapsed: recall first, then open them. The real-world reps matter more than the reading, and spacing them out is the point. Anything still unclear at the end of a lesson is worth chasing to its primary source before moving on.
