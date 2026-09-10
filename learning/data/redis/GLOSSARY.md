---
title: Glossary
description: "Canonical terms for Redis"
type: glossary
---

# Redis Glossary

Canonical terms for using Redis for what it actually is: an in-memory store with a bounded, evictable keyspace.

## Terms

**Cardinality**:
The number of distinct elements in a collection, the specific quantity HyperLogLog estimates without storing the elements themselves.
_Avoid_: count (say "count" for an exact number; reserve "cardinality" for the specific, estimable-without-storage quantity HyperLogLog targets)

**Eviction policy**:
The rule Redis follows to decide which keys to delete once `maxmemory` is reached, ranging from deleting nothing and rejecting writes (`noeviction`) to deleting any key (`allkeys-*`) or only keys with a TTL (`volatile-*`).
_Avoid_: cache policy (too vague; name the specific policy)

**maxmemory**:
The configured memory ceiling for a Redis instance's dataset. What happens once it's reached is determined entirely by the eviction policy in force.
_Avoid_: memory limit (use the exact setting name once it's been introduced)

**Sorted set**:
A Redis collection where every member carries a numeric score, kept ordered by that score automatically (backed by a skip list), with O(log N) insertion and range queries.
_Avoid_: ranked set, scored list (say "sorted set", matching the `ZADD`/`ZRANGE` command family)
