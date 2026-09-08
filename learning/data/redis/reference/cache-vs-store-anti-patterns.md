---
title: Cache vs Store Anti-Patterns
description: "Cache-aside done correctly, the two ways a cache stops being one, and the eviction settings that decide which failure you get"
type: reference
---

# Cache and Store: The Anti-Patterns

Stage 4 compressed for lookup. [Lesson 6](../lessons/0006-cache-aside-and-the-store-anti-pattern.md) covers cache-aside and the store anti-pattern, [lesson 7](../lessons/0007-unbounded-keyspace-and-spotting-misuse.md) covers the unbounded keyspace; this sheet is the settings that decide how each one fails, and the checklist.

## Cache-aside, correctly

| Path | What the application does |
|---|---|
| Read, hit | Return the cached value |
| Read, miss | Query the primary, write the result into Redis **with a TTL**, return it |
| Write | **`DEL` the key.** Do not write the new value into Redis |

Redis never talks to the primary. The application wires them together on every read.

The write rule is the one people get wrong. Deleting is correct because cache-aside's safety property is that it **never assumes the cache holds the latest value**: a miss re-fetches, so removing a stale key is enough even under concurrent readers and writers, where updating both places correctly is genuinely hard. The TTL is a second, independent line of defence for when a delete is missed, not a substitute for it.

## The two anti-patterns

| | Cache as a store | Unbounded keyspace |
|---|---|---|
| What happened | Data written to Redis with no durable copy behind it | Keys created with no TTL and nothing that removes them |
| The tell | A cache miss is a correctness failure, not a slow path | Nothing removes a key, and nobody can say what would |
| Fails when | An eviction, a crash before the next snapshot or fsync, or `maxmemory` under `noeviction` | `maxmemory`, or physical memory, is finally reached |
| Why it hides | The system was never designed to tolerate a miss, on a component whose design assumes misses are normal | It works perfectly until the ceiling, which can be months away |

The test for the first: **what does a cache miss cost?** If the answer is "wrong behaviour" rather than "a slower request", it is not a cache.

The test for the second: **for every key, what removes it and when?** There are exactly three acceptable answers, a TTL at write time, an explicit `DEL` at a known point, or a deliberate decision that it lives forever with capacity planned for it. No answer is the anti-pattern.

## What actually happens at the ceiling

`maxmemory` defaults to **0**, meaning no limit, on 64-bit systems. Thirty-two-bit systems get an implicit 3GB. So an unbounded keyspace on a default 64-bit instance does not hit a Redis limit at all; it grows until the operating system intervenes.

Once `maxmemory` is set, `maxmemory-policy` decides what happens.

| Policy | Evicts |
|---|---|
| `noeviction` | Nothing. **The default** |
| `allkeys-lru` | Least recently used, any key |
| `allkeys-lrm` | Least recently **modified**, any key |
| `allkeys-lfu` | Least frequently used, any key |
| `allkeys-random` | At random, any key |
| `volatile-lru` | Least recently used **among keys with a TTL** |
| `volatile-lrm` | Least recently modified, among keys with a TTL |
| `volatile-lfu` | Least frequently used, among keys with a TTL |
| `volatile-random` | At random, among keys with a TTL |
| `volatile-ttl` | Shortest remaining TTL first |

Three consequences worth knowing before choosing:

- **`volatile-*` behaves like `noeviction` when no key has a TTL.** Selecting a volatile policy and never setting TTLs buys nothing, and the failure looks like the default rather than like eviction.
- **Under `noeviction`, or when any policy finds nothing to evict, writes error out.** Commands that create keys, add data or modify keys: `SET`, `INCR`, `HSET`, `LPUSH`, `SUNIONSTORE`, `SORT` with `STORE`, and `EXEC` if the transaction contains one. **Read-only commands keep working**, which is why the instance can look healthy while every write fails.
- `allkeys-lrm` evicts by last modification rather than last read, which suits keys that should go when they stop being updated regardless of how often they are read.

### The accounting has a hole worth leaving room for

Replication and AOF buffers are **not counted** toward `maxmemory`. `INFO memory` reports `mem_not_counted_for_evict` for exactly this. Leave headroom below physical memory when replication or persistence is on. Not needed under `noeviction`.

### LRU here is approximate

Redis samples a pool of candidates rather than maintaining true LRU, because true LRU costs more memory. `maxmemory-samples` tunes how many are checked, default **5**. The approximation is close enough for application use, and it is an approximation.

## Spotting either one in an existing system

- Ask what a cache miss costs. If the answer is not "a slower request", stop there.
- Look for a write path into Redis with no corresponding write to a system of record.
- Check `maxmemory`. If it is `0` on a 64-bit host, nothing bounds growth except the machine.
- Check `maxmemory-policy`. If it is `noeviction`, the plan at the ceiling is to fail writes.
- If it is a `volatile-*` policy, check that keys actually carry TTLs. If they do not, the policy is inert.
- Take a sample of live keys and ask what removes each one. Anything with no answer is the unbounded pattern, however small it looks.
- Check whether anything reads a key back and assumes it is present. That assumption is the store anti-pattern written down.

## Sources

- [Docs: "Key eviction", Redis](https://redis.io/docs/latest/develop/reference/eviction/)
- [Docs: "Redis cache-aside", Redis](https://redis.io/docs/latest/develop/use-cases/cache-aside/)
- [Persistence](persistence.md)
- [Resources](../RESOURCES.md)
