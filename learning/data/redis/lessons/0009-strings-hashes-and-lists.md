---
title: 9. Strings, Hashes, and Lists
description: The three core data structures Redis actually stores, and what each one costs to read, write, and grow
type: lesson
---

# Lesson 9. Strings, Hashes, and Lists

**Mission link:** Stage 6 opens what Redis actually stores. Every prior stage assumed a key held some opaque value; this lesson is the first three shapes that value can actually take, and the specific cost each one carries, the foundation "design correct usage from scratch" needs before choosing a structure means anything.
**Primary source:** [Docs: "Data types", Redis](https://redis.io/docs/latest/develop/data-types/)
**Prerequisites:** [Lesson 8](0008-cluster-and-sentinel.md), [maxmemory](../GLOSSARY.md)

## Warm-up

1. ▢ Why is eviction even a concept Redis needs, when a typical disk-backed database doesn't delete data to make room for new writes?

<details markdown="1"><summary>Check</summary>

Redis keeps its entire dataset in RAM, so its capacity is bounded by available memory in a way a disk-backed database isn't; that hard ceiling is what makes eviction necessary.

</details>

2. ▢ What does Redis Cluster's automatic failover not eliminate, even though it keeps the cluster available through a node failure?

<details markdown="1"><summary>Check</summary>

The possibility of losing a write during the failure: Cluster's replication between a slot's primary and its replicas is asynchronous, so a write acknowledged just before a primary fails can still be lost if it never reached the replica that gets promoted.

</details>

## Know this

### A string: one opaque value, and Redis's actual default

A **string** is Redis's simplest type, a binary-safe sequence of bytes up to 512MB, addressed by one key: `SET session:42 "a1b2c3..."`, `GET session:42`. Every value this workspace has discussed so far, a session token, a cached page, a rate-limit counter, has actually been a string; it's the type every other lesson in this mission implicitly assumed. Strings also support atomic numeric operations, `INCR`/`DECR`, useful specifically because they avoid the read-modify-write race a client doing `GET` then `SET` itself would have. A string's cost is close to what it looks like: `GET`/`SET` are O(1) regardless of length, but repeatedly growing one with `APPEND` can force reallocation as it crosses internal capacity boundaries, a cost worth knowing about for a string that grows unboundedly rather than being set once.

### A hash: fields under one key, instead of N separate keys

A **hash** groups several named fields under one key, `HSET user:42 name Ada email ada@x.com plan pro`, `HGET user:42 name`, representing something like an object without needing a separate top-level key per field. This matters for more than convenience: many small keys each carry their own per-key overhead (bookkeeping Redis maintains for every key it tracks), so a hash with a handful of fields is meaningfully more memory-efficient than the same data spread across that many individual string keys. Redis encodes a small hash compactly (a `listpack`, a flat, cache-friendly layout) up to a configured size (`hash-max-listpack-entries`, `hash-max-listpack-value`); crossing that threshold converts it to a full hash table internally, a real shift in both memory use and per-field access cost that a hash growing past its expected size can trigger without anyone noticing until it does.

![Three keys, each holding a different shape. session:42 holds a single string value. user:42 is a hash holding several named fields, name, email, and plan, each with its own value. queue:jobs is a list holding an ordered sequence of values, job3, job2, job1, with new items pushed onto one end.](images/string-hash-list-shapes.svg)

### A list: ordered, cheap at the ends, expensive in the middle

A **list** holds an ordered sequence of values under one key, `LPUSH queue:jobs job1`, `RPOP queue:jobs`, the standard shape for a queue (push one end, pop the other) or a capped recent-items feed (`LPUSH` plus `LTRIM` to keep only the newest N). Internally a list is a **quicklist** (a linked structure of compact nodes), which is exactly why pushing or popping at either end is cheap, O(1), while `LINDEX` at an arbitrary middle position, or `LINSERT` into the middle, is O(N): the list has to walk from an end to reach that position, since nothing in its structure supports jumping there directly. Treating a Redis list like an array with fast random access anywhere is the specific mistake this cost model rules out.

## Practice

1. ▢ A team stores a user's profile as five separate string keys (`user:42:name`, `user:42:email`, `user:42:plan`, and two more) instead of one hash. What does switching to a single hash actually save, beyond looking tidier?

<details markdown="1"><summary>Hint</summary>

Consider what Redis tracks for every individual key it manages, separate from the value each key holds.

</details>

<details markdown="1"><summary>Check</summary>

It saves the per-key overhead Redis maintains for each of those five separate keys (the bookkeeping every tracked key carries, independent of its value's own size); consolidating them into one hash with five fields keeps that overhead to a single key's worth instead of five, meaningfully reducing memory use for data this small and this related.

</details>

2. ▢ A script uses `LINDEX queue:jobs 5000` inside a loop that checks every position in a very long list one at a time. Why does this get slower as the list grows, in a way `LPUSH`/`RPOP` at the ends wouldn't?

<details markdown="1"><summary>Check</summary>

A Redis list is a quicklist, a linked structure with no direct way to jump to an arbitrary middle position; reaching position 5000 means walking from an end, an O(N) operation whose cost grows with the list's length. `LPUSH`/`RPOP` only ever touch an end directly, staying O(1) regardless of how long the list gets.

</details>

3. ▢ A counter is implemented as `value=$(redis-cli GET counter); value=$((value + 1)); redis-cli SET counter "$value"` from a client, rather than `redis-cli INCR counter`. What real risk does this introduce that `INCR` avoids?

<details markdown="1"><summary>Check</summary>

A race condition: two clients doing `GET` then `SET` at close to the same time can both read the same starting value and both write back the same incremented result, silently losing one of the two increments. `INCR` performs the read-modify-write as a single atomic operation inside Redis, closing that window entirely.

</details>

4. ▢ A hash is expected to stay small (a handful of fields per user) but one user's account accumulates hundreds of fields over time. What changes once it crosses `hash-max-listpack-entries`, and why might this go unnoticed until it matters?

<details markdown="1"><summary>Check</summary>

Redis converts the hash's internal encoding from a compact `listpack` to a full hash table, a real shift in memory use and per-field access characteristics. This can go unnoticed because nothing about the hash's external behavior (`HGET`/`HSET` still work identically) signals the change; only inspecting the hash's actual memory footprint or encoding would reveal it crossed the threshold.

</details>

5. ▢ Which claim correctly distinguishes a Redis hash from spreading the same fields across separate string keys?

    - a) A hash and separate string keys have identical memory and per-key overhead; the difference is purely stylistic
    - b) Grouping related fields into one hash avoids the per-key overhead each separate string key would carry individually, at the cost of a size threshold beyond which the hash's internal encoding changes
    - c) A hash can only ever use as much memory as a single string key, regardless of how many fields it holds
    - d) Fields inside a hash are accessed in O(N) time, while separate string keys are always O(1)

<details markdown="1"><summary>Check</summary>

**b)** That's the exact trade-off: real memory savings from consolidation, with a real encoding-change threshold to be aware of. (a) is false: per-key overhead is exactly what consolidating into a hash avoids. (c) is false: a hash's memory use grows with its fields and can exceed a single small string's, though it's still typically cheaper than N separate keys for the same data. (d) is false: `HGET`/`HSET` on a specific field are O(1), the same as a string key's `GET`/`SET`.

</details>

## Real-world reps

- [ ] Find a system you have access to storing related fields as several separate Redis keys (`user:*:name`, `user:*:email`, and similar). Estimate the per-key overhead being paid and what consolidating into one hash would save.
- [ ] Find (or design) a queue implemented with a Redis list. Confirm it only ever accesses the list from its two ends (`LPUSH`/`RPOP`, or the reverse), never at an arbitrary middle index.
- [ ] Tomorrow: read the primary source's sections on strings, hashes, and lists in full, and note the exact configured thresholds (`hash-max-listpack-entries` and its list equivalent) your own instance is running with.

## Going further

- [Docs: "Data types", Redis](https://redis.io/docs/latest/develop/data-types/)
- [Docs: "Key eviction", Redis](https://redis.io/docs/latest/develop/reference/eviction/)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
