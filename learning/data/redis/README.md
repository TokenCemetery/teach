---
title: Redis
description: "Use Redis for what it is: the memory model, eviction, persistence, and the patterns that quietly misuse it"
type: topic
---

# Learning: Redis

Be able to spot where an existing system is quietly misusing Redis, such as a cache treated as a store or a lock that is not one, and to design correct usage from scratch instead.

**Latest lesson:** [17. ACLs and Protected Mode](lessons/0017-acls-and-protected-mode.md)

## Success looks like

- Given an existing system's use of Redis, identify whether it is treating a cache as a durable store, implementing a lock incorrectly, or running an unbounded keyspace, and say what breaks because of it.
- Design correct usage of Redis (bounded keyspace, appropriate eviction policy, real distributed lock) for a new use case from scratch.
- Compare Redis's persistence guarantees (RDB/AOF) against Postgres's WAL-backed durability, and say when reaching for Redis instead of a database is the right call versus an anti-pattern.
- Reason about Redis Cluster/Sentinel at the level of the compromises clustering introduces, without needing to operate one.

## Constraints

- Assumes no prior Redis experience.

## Out of scope

- Operating a production Postgres instance: see [`data/postgres`](../../data/postgres/), linked to for the comparison rather than restated.

## The arc

Ten stages, eviction to access control. A stage takes several lessons and the boundaries are soft; what makes a stage done is the capability, not the lesson count.

| Stage | Lessons | Covers | Done when |
|---|---|---|---|
| 1. Memory and eviction | 0001 | Why Redis evicts keys at all, and the anti-pattern that follows from forgetting it | Can explain an eviction policy's effect on a given workload |
| 2. Persistence | 0002 to 0003 | RDB and AOF, and how their durability compares to Postgres's WAL | Can say when reaching for Redis instead of a database is right versus an anti-pattern |
| 3. Distributed locks | 0004 to 0005 | Naive locking mistakes, Redlock, Kleppmann's critique | Can design, or correctly reject, a Redis-based distributed lock |
| 4. Cache-vs-store anti-patterns | 0006 to 0007 | Cache-aside, a cache treated as a durable store, an unbounded keyspace | Given an existing system, can identify the misuse and say what breaks |
| 5. Clustering | 0008 | Redis Cluster and Sentinel, the compromises clustering introduces | Can reason about clustering trade-offs without needing to operate one |
| 6. Data types and their cost model | 0009 to 0010 | Strings, hashes, lists, sets, sorted sets, bitmaps, HyperLogLog, and picking between them | Can choose a data structure for a stated use case and explain what it costs |
| 7. Messaging and expiration | 0011 to 0012 | Pub/Sub vs streams, consumer groups compared to Kafka's, lazy vs active key expiration | Can pick the right messaging mechanism for a use case and explain how a key actually leaves Redis |
| 8. Transactions and scripting | 0013 to 0014 | `MULTI`/`EXEC`, optimistic locking with `WATCH`, Lua scripting, Redis Functions | Can build a check-then-act sequence that's actually safe, and explain what makes a lock's release atomic |
| 9. Performance and operations | 0015 to 0016 | Round-trip cost, pipelining, connection pooling, `INFO`/`SLOWLOG`/latency monitor/`MEMORY USAGE`, `SCAN` vs `KEYS` | Can reduce a chatty client's network cost and diagnose an instance's actual behavior without freezing it |
| 10. Access control | 0017 | Protected mode, ACLs, command categories, the default user | Can restrict what an unauthenticated connection and an authenticated user can each do |

## Lessons

Work through these in order.

| # | Lesson | Teaches |
|---|---|---|
| [0001](lessons/0001-memory-and-eviction.md) | Memory and Eviction | Why Redis evicts keys at all, and the anti-pattern that follows from forgetting it |
| [0002](lessons/0002-rdb-snapshotting.md) | RDB Snapshotting | What an RDB snapshot actually captures, and the data-loss window its save interval leaves open |
| [0003](lessons/0003-aof-and-wal-comparison.md) | AOF and the WAL Comparison | How AOF's fsync policy sets its data-loss window, and why even Redis's strongest common setting trades more durability for speed than Postgres does by default |
| [0004](lessons/0004-naive-locking-mistakes.md) | Naive Locking Mistakes | Why SET NX PX alone is not a distributed lock, and the two failure modes that break it under real conditions |
| [0005](lessons/0005-redlock-and-kleppmanns-critique.md) | Redlock and Kleppmann's Critique | What Redlock actually fixes about the naive lock, what Kleppmann's critique shows it still doesn't, and how to decide whether a Redis lock is the right tool at all |
| [0006](lessons/0006-cache-aside-and-the-store-anti-pattern.md) | Cache-Aside and the Store Anti-Pattern | What correct cache-aside usage looks like, and the specific way a cache quietly becomes the system of record when that pattern is skipped |
| [0007](lessons/0007-unbounded-keyspace-and-spotting-misuse.md) | The Unbounded-Keyspace Anti-Pattern and Spotting Misuse | How a keyspace grows without bound when nobody sets it a TTL or an eviction policy, and a checklist for spotting this and the store anti-pattern in an existing system |
| [0008](lessons/0008-cluster-and-sentinel.md) | Redis Cluster and Sentinel | The compromises Redis Cluster's sharding and Sentinel's automatic failover each introduce, reasoned about without needing to operate either |
| [0009](lessons/0009-strings-hashes-and-lists.md) | Strings, Hashes, and Lists | The three core data structures Redis actually stores, and what each one costs to read, write, and grow |
| [0010](lessons/0010-sets-sorted-sets-and-probabilistic-structures.md) | Sets, Sorted Sets, and Probabilistic Structures | Picking a data structure for a use case, from exact membership to an approximate count that costs almost nothing to keep |
| [0011](lessons/0011-streams-and-pubsub-as-messaging.md) | Streams and Pub/Sub as a Messaging Surface | Two ways Redis moves messages between clients, and why only one of them is safe to build a queue on |
| [0012](lessons/0012-key-expiration-lazy-vs-active.md) | Key Expiration: Lazy vs Active Expiry | Why a key's TTL reaching zero doesn't remove it from memory by itself, and the two mechanisms that eventually do |
| [0013](lessons/0013-multi-exec-and-optimistic-locking-with-watch.md) | MULTI/EXEC and Optimistic Locking with WATCH | Queuing several commands to run without interruption, and detecting a value changed out from under you before you act on it |
| [0014](lessons/0014-lua-scripting-and-redis-functions.md) | Lua Scripting and Redis Functions | The mechanism that actually makes a lock's release safe, by running a check and an action as one atomic step |
| [0015](lessons/0015-pipelining-round-trip-cost-and-connection-pooling.md) | Pipelining, Round-Trip Cost, and Connection Pooling | Why N sequential commands cost N network round trips even though each one executes in microseconds, and the two separate fixes |
| [0016](lessons/0016-operational-visibility.md) | Operational Visibility | The tools that show what a Redis instance is actually doing, and the one command that has caused more outages than almost any other |
| [0017](lessons/0017-acls-and-protected-mode.md) | ACLs and Protected Mode | How Redis stops an unauthenticated instance from being reachable at all, and scopes what an authenticated client is actually allowed to do |

## Reference

- [Glossary](GLOSSARY.md): canonical terms for this topic
- [Resources](RESOURCES.md): trusted sources
- [Persistence](reference/persistence.md): what RDB and AOF each promise, the exact loss window every fsync policy leaves, and what Redis's own documentation says about matching a database's durability
- [Distributed Locks](reference/distributed-locks.md): the naive lock and its two holes, Redlock's algorithm with the validity arithmetic, and the one question that decides whether either is the right tool
- [Cache vs Store Anti-Patterns](reference/cache-vs-store-anti-patterns.md): cache-aside done correctly, the two ways a cache stops being one, and the eviction settings that decide which failure you get
- [Clustering](reference/clustering.md): what Cluster's slots take away, the settings that decide whether a degraded cluster serves or stops, and why Sentinel's quorum does not control failover

## How this works

Each lesson is short and self-contained. Answer keys are collapsed: recall first, then open them. The real-world reps matter more than the reading, and spacing them out is the point. Anything still unclear at the end of a lesson is worth chasing to its primary source before moving on.
