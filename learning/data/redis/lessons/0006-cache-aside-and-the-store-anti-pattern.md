---
title: 6. Cache-Aside and the Store Anti-Pattern
description: What correct cache-aside usage looks like, and the specific way a cache quietly becomes the system of record when that pattern is skipped
type: lesson
---

# Lesson 6. Cache-Aside and the Store Anti-Pattern

**Mission link:** Stage 4 opens the mission's other named misuse pattern, "a cache treated as a store." This lesson establishes correct cache-aside usage first, since the anti-pattern only makes sense as a deviation from it; lesson 7 covers the unbounded-keyspace anti-pattern and spotting both in an existing system.
**Primary source:** [Docs: "Redis cache-aside", Redis](https://redis.io/docs/latest/develop/use-cases/cache-aside/)
**Prerequisites:** [Lesson 5](0005-redlock-and-kleppmanns-critique.md), [Eviction policy](../GLOSSARY.md)

## Warm-up

1. ▢ What does a fencing token protect against that a Redlock majority-quorum acquisition alone doesn't?

<details markdown="1"><summary>Check</summary>

A client acting on the protected resource after its own lock has already expired (the pause-based failure mode). Redlock's quorum only establishes who currently holds the lock across instances; a fencing token, checked by the resource itself, lets the resource reject a stale caller regardless of what the lock believes.

</details>

2. ▢ Why isn't "Redlock is broken" the right conclusion from Kleppmann's critique?

<details markdown="1"><summary>Check</summary>

Redlock genuinely fixes the single-instance failure mode it targets. The critique is that a lock alone, Redlock or otherwise, can't guarantee correctness for a client that pauses past its validity time unless the protected resource itself enforces fencing; that's a property of the resource, not a defect in Redlock's algorithm.

</details>

## Know this

### Cache-aside: the application owns the read and write path

**Cache-aside** (also called lazy loading) is the standard pattern for using Redis as a cache in front of a primary database: on a read, the application checks Redis first; on a hit, it returns the cached value directly; on a miss, it queries the primary database, then writes the result into Redis with a TTL before returning it. Redis never talks to the primary database itself, and the primary database has no idea Redis exists: the application is what wires the two together, on every read.

### The write side: invalidate, don't rewrite

When the underlying record changes, the correct move is to delete the cache key (`DEL`), not to write the new value into Redis directly. This matters because cache-aside's actual safety property is that it never assumes the cache holds the latest value: a miss always re-fetches from the primary, so deleting a stale key is enough to guarantee the next read is correct, even under concurrent writes and reads that would make "write the new value to both places" hard to get right. A TTL is a second, independent line of defense against a delete getting missed for any reason, not a substitute for it.

### The store anti-pattern: when the cache becomes the only copy

The anti-pattern the mission names, "a cache treated as a store," is what happens when this discipline erodes: data gets written to Redis without ever being written to (or backed by) a durable system of record, and the application starts reading it back as if Redis were guaranteed to still have it. Once that happens, an eviction (lesson 1), an unplanned crash before the next RDB snapshot (lesson 2) or AOF fsync (lesson 3), or simply `maxmemory` being reached under `noeviction` all become correctness failures instead of cache misses, because there's no primary copy left to fall back to. The system was never designed to tolerate a miss, even though it was built on a component whose whole design assumes misses are normal and cheap.

### The tell: what a cache miss should cost

The fastest diagnostic for this anti-pattern is asking what happens on a miss. In correct cache-aside usage, a miss costs a slower read from the primary database, nothing more: data isn't lost, just re-fetched. If a miss instead means the data is *gone*, that a "cache" key holds information with no other durable copy anywhere, the system has quietly promoted Redis from a cache to a store without any of the guarantees (durability window, replication, backup) a real store would need, and every one of lessons 1 through 5's failure modes becomes a data-loss incident rather than a latency blip.

## Practice

1. ▢ Walk through cache-aside's read path for a cache hit and a cache miss.

<details markdown="1"><summary>Check</summary>

On a hit, the application reads the value directly from Redis and returns it, never touching the primary database. On a miss, the application queries the primary database for the value, writes that value into Redis with a TTL, and then returns it, so the next read for the same key becomes a hit.

</details>

2. ▢ On a write to the underlying record, why does cache-aside delete the cache key instead of writing the new value into Redis directly?

<details markdown="1"><summary>Hint</summary>

Consider what could go wrong if a write and a concurrent read-triggered cache-fill happen to the same key at close to the same time.

</details>

<details markdown="1"><summary>Check</summary>

Cache-aside's safety comes from never assuming the cache holds the latest value: a miss always re-fetches from the primary. Deleting the key guarantees this, since the next read simply falls back to the primary and refills correctly. Writing the new value directly into Redis on every update introduces a race: a concurrent read that already fetched the *old* value from the primary could write it into Redis right after the update's write, leaving a stale value in the cache with nothing left to correct it until the TTL expires.

</details>

3. ▢ Define the store anti-pattern precisely: what specifically has to be true of how a system uses Redis for it to apply?

<details markdown="1"><summary>Check</summary>

Data gets written to Redis without ever being written to, or backed by, a separate durable system of record, and the application reads it back assuming Redis will still have it. The defining feature is that there is no primary copy to fall back to on a miss, unlike correct cache-aside usage where the primary database always has the data.

</details>

4. ▢ A team stores user session data only in Redis, with no database table backing it, and reports "cache misses" as user-facing bugs (users getting logged out unexpectedly) rather than as expected, cheap events. Diagnose what's actually going on.

<details markdown="1"><summary>Check</summary>

This is the store anti-pattern: Redis holds the only copy of the session data, so what the team calls a "cache miss" is actually data loss, since there's no primary system of record to fall back to and refill from. The bug isn't that misses happen; it's that the system was built assuming Redis is durable enough to be the sole copy, an assumption none of Redis's persistence or eviction behavior (lessons 1 to 3) actually guarantees.

</details>

5. ▢ Which claim correctly distinguishes cache-aside from the store anti-pattern?

    - a) Cache-aside means Redis stores the primary copy of the data; the anti-pattern means the database does
    - b) In cache-aside, a miss costs a slower read from an always-present primary; in the anti-pattern, a miss means the data is actually gone
    - c) The anti-pattern only occurs when `maxmemory` is misconfigured
    - d) Cache-aside and the store anti-pattern are the same pattern, just described differently by different teams

<details markdown="1"><summary>Check</summary>

**b)** That's the precise, checkable distinction: whether a primary copy actually exists to fall back to on a miss. (a) has it backwards: cache-aside always has the primary database hold the real data, with Redis as a disposable accelerator. (c) is false: the anti-pattern is about whether a durable primary copy exists at all, independent of any specific `maxmemory` setting; even a generously-configured instance can be the sole copy of data it was never meant to be. (d) is false: they're distinguished exactly by whether a miss is a cheap re-fetch or an actual loss.

</details>

## Real-world reps

- [ ] Find a place in a codebase you know of that writes to Redis. For each one, check: is there a durable system of record this data is also written to (or derived from), or does Redis hold the only copy?
- [ ] For any cache-aside usage you find, check the write path specifically: does an update to the underlying record delete the cache key, or does it write the new value directly into Redis? Note which, and whether that choice is deliberate.
- [ ] Tomorrow: read the primary source's cache-aside doc in full, including its note on cache stampedes (many concurrent misses on a popular key hitting the primary database at once), a related but distinct risk from the store anti-pattern this lesson covers.

## Going further

- [Docs: "Redis cache-aside", Redis](https://redis.io/docs/latest/develop/use-cases/cache-aside/)
- [Docs: "Key eviction", Redis](https://redis.io/docs/latest/develop/reference/eviction/)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
