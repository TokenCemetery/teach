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

- Assumes no prior Redis experience.

## Out of scope

- Operating a production Postgres instance: that is `data/postgres`, linked to for the comparison rather than restated.

## The arc

Five stages, eviction to spotting misuse on sight. A stage takes several lessons and the boundaries are soft; what makes a stage done is the capability, not the lesson count.

| Stage | Lessons | Covers | Done when |
|---|---|---|---|
| 1. Memory and eviction | 0001 | Why Redis evicts keys at all, and the anti-pattern that follows from forgetting it | Can explain an eviction policy's effect on a given workload |
| 2. Persistence | 0002 to 0003 | RDB and AOF, and how their durability compares to Postgres's WAL | Can say when reaching for Redis instead of a database is right versus an anti-pattern |
| 3. Distributed locks | 0004 to 0005 | Naive locking mistakes, Redlock, Kleppmann's critique | Can design, or correctly reject, a Redis-based distributed lock |
| 4. Cache-vs-store anti-patterns | 0006 to 0007 | Cache-aside, a cache treated as a durable store, an unbounded keyspace | Given an existing system, can identify the misuse and say what breaks |
| 5. Clustering | 0008 | Redis Cluster and Sentinel, the compromises clustering introduces | Can reason about clustering trade-offs without needing to operate one |

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
