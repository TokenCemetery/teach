---
title: Glossary
description: "Canonical terms for Redis"
type: glossary
---

# Redis Glossary

Canonical terms for using Redis for what it actually is: an in-memory store with a bounded, evictable keyspace.

## Terms

**Active expiration**:
A background cycle that samples keys carrying a TTL several times a second and deletes any that have already expired, independent of `maxmemory` pressure.
_Avoid_: garbage collection (a different mechanism in other systems; say "active expiration" for this specific sweep)

**Atomic**:
In this workspace, "nothing else interleaves during this operation," never "every step either fully succeeds together or fully rolls back on a runtime failure," the sense a SQL transaction implies. `MULTI`/`EXEC` and a Lua script are atomic in the first sense only.
_Avoid_: transactional (reserve for a system that actually rolls back on a runtime failure, which Redis's `MULTI`/`EXEC` does not)

**Cardinality**:
The number of distinct elements in a collection, the specific quantity HyperLogLog estimates without storing the elements themselves.
_Avoid_: count (say "count" for an exact number; reserve "cardinality" for the specific, estimable-without-storage quantity HyperLogLog targets)

**Eviction policy**:
The rule Redis follows to decide which keys to delete once `maxmemory` is reached, ranging from deleting nothing and rejecting writes (`noeviction`) to deleting any key (`allkeys-*`) or only keys with a TTL (`volatile-*`).
_Avoid_: cache policy (too vague; name the specific policy)

**Lazy expiration**:
Removing a key past its TTL only when something actually accesses it; until then, the key still physically occupies memory.
_Avoid_: on-demand expiration (say "lazy expiration", matching this workspace's paired term "active expiration")

**maxmemory**:
The configured memory ceiling for a Redis instance's dataset. What happens once it's reached is determined entirely by the eviction policy in force.
_Avoid_: memory limit (use the exact setting name once it's been introduced)

**Optimistic concurrency control**:
Proceeding without blocking other clients, then detecting at commit time whether a watched value changed and retrying if it did, the strategy `WATCH`/`MULTI`/`EXEC` implements.
_Avoid_: locking (the opposite strategy; reserve "locking" for actually blocking other clients, lessons 4-5's approach)

**Pending entries list (PEL)**:
A Redis stream consumer group's per-consumer record of entries delivered but not yet acknowledged with `XACK`, reclaimable by another consumer via `XCLAIM`.
_Avoid_: unacked queue (say "pending entries list" or "PEL", the stream's own term)

**Pipelining**:
Sending several commands in one batch without waiting for each response individually, reducing round trips; a purely network-level optimization with no atomicity guarantee on its own.
_Avoid_: batching (too generic; "pipelining" is the specific mechanism of not waiting for each response before sending the next)

**Round trip**:
The time spent sending a request and waiting for its response, separate from and usually far larger than a command's own execution time inside Redis.
_Avoid_: latency (use "round trip" specifically for the request-response cycle cost this workspace's performance lessons address)

**Sorted set**:
A Redis collection where every member carries a numeric score, kept ordered by that score automatically (backed by a skip list), with O(log N) insertion and range queries.
_Avoid_: ranked set, scored list (say "sorted set", matching the `ZADD`/`ZRANGE` command family)
