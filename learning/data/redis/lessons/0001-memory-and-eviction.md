---
title: 1. Memory and Eviction
description: Why Redis evicts keys at all, and the anti-pattern that follows from forgetting it
type: lesson
---

# Lesson 1. Memory and Eviction

**Mission link:** "The memory model, eviction... and the patterns that quietly misuse it" starts here: the single fact that Redis lives in RAM is what makes eviction necessary, and forgetting that fact is the root of "a cache treated as a store."
**Primary source:** [Docs: "Key eviction", Redis](https://redis.io/docs/latest/develop/reference/eviction/)
**Prerequisites:** none

## Know this

### Redis lives in memory, so capacity is finite by construction

Redis keeps its dataset in RAM. That's the entire reason it's fast: no disk seek sits between a request and its answer. But it also means Redis's capacity is bounded by however much memory the instance has, not by disk space, and RAM is expensive and finite in a way that makes "just let the keyspace grow forever" a real failure mode rather than a theoretical one.

### What happens when memory runs out

Redis is configured with a `maxmemory` limit. What happens when the dataset hits that limit depends entirely on the configured **eviction policy**:

- **`noeviction`** (the default): Redis stops accepting new writes once `maxmemory` is hit, returning an error to the client instead. No data is deleted, but the application starts failing writes, which is usually an outage, not a graceful degradation.
- **An eviction policy** (`allkeys-lru`, `volatile-lru`, `allkeys-lfu`, `volatile-ttl`, and others): Redis actively deletes existing keys to make room for new writes, chosen by whatever the policy's name says (least-recently-used, least-frequently-used, keys closest to TTL expiry, and so on).

The `allkeys-*` policies can evict **any** key. The `volatile-*` policies only evict keys that have a TTL set at all; a key with no expiry is never touched by a `volatile-*` policy, no matter how much memory pressure there is.

### The anti-pattern this produces

The failure mode isn't a Redis bug; it's a mismatch between what an application assumes and what its eviction policy actually does:

- A team sets `allkeys-lru` (evict anything, least-recently-used first) so their cache stays bounded, but stores something they treat as durable, say, a piece of session or configuration state, with no TTL and no equivalent source of truth elsewhere. Under memory pressure from unrelated cache traffic, that "durable" key can be silently evicted, and there is nowhere else to recover it from. This is a cache treated as a store.
- The opposite mismatch also happens: a team runs `noeviction` because they don't want data silently deleted, but never bounds the keyspace (no TTLs, no cleanup), so the dataset grows until `maxmemory` is hit and every write in the application starts failing, often in production, all at once.

Both are the same root cause: not asking, for every key kept in Redis, "what happens if this key disappears right now, and does the eviction policy in force make that scenario impossible, likely, or catastrophic?"

### This is also why Redis's persistence isn't the same guarantee as a database's

Redis can persist to disk (RDB snapshots, an AOF log) so a restart doesn't lose everything. That's useful, but it's a recovery mechanism for the instance restarting, not a durability contract like a database's write-ahead log: an RDB snapshot only captures data as of its last save point, and even AOF's strongest fsync setting has different guarantees and different recovery behavior than what a WAL-backed database (see `data/postgres`) promises for a committed write. Treating Redis's persistence as equivalent to that is a version of the same anti-pattern: assuming durability a cache was never designed to give you.

## Practice

1. ▢ In one sentence, why is eviction even a concept Redis needs, when a typical database doesn't delete your data to make room for new writes?

<details markdown="1"><summary>Check</summary>

Because Redis keeps the entire dataset in RAM rather than on disk, so its capacity is bounded by available memory; a database backed by disk storage doesn't face the same hard, immediate ceiling.

</details>

2. ▢ A service stores session tokens in Redis with `noeviction` set and never expires any of them. Over months, the keyspace grows unbounded. What happens when the instance finally hits `maxmemory`, and how would that look in production?

<details markdown="1"><summary>Check</summary>

With `noeviction`, Redis doesn't delete anything; it starts rejecting new writes with an error once `maxmemory` is reached. In production, this looks like every write path that touches Redis suddenly failing at once, an outage, not silent data loss or graceful degradation. No existing session data is lost, but nothing new can be written.

</details>

3. ▢ A team caches "critical configuration" in Redis, with no TTL set on that key, under an `allkeys-lru` eviction policy chosen to keep the overall cache bounded. During a traffic spike that fills the cache with unrelated data, the configuration key vanishes and the service misbehaves. Diagnose what went wrong.

<details markdown="1"><summary>Hint</summary>

What does `allkeys-lru` promise about which keys it's allowed to touch?

</details>

<details markdown="1"><summary>Check</summary>

`allkeys-*` policies can evict any key, not just ones with a TTL; there is nothing in the policy that exempts a key just because the application considers it "critical" or "durable." The team's mismatch was treating a key as durable while running an eviction policy with no concept of durable keys. The fix is either to store that configuration somewhere with an actual durability guarantee, or, if it must live in Redis, to use a `volatile-*` policy and deliberately never set a TTL on that specific key (while giving cache keys a TTL so they remain evictable).

</details>

4. ▢ Which best distinguishes the `volatile-*` eviction policy family from the `allkeys-*` family?

   - a) `volatile-*` policies are faster because they scan fewer keys
   - b) `volatile-*` policies only evict keys that have a TTL set; `allkeys-*` policies can evict any key
   - c) `allkeys-*` policies only run when `noeviction` is also set
   - d) `volatile-*` policies evict based on key size; `allkeys-*` policies evict based on recency

<details markdown="1"><summary>Check</summary>

**b)** `volatile-*` policies only evict keys that have a TTL set; `allkeys-*` policies are eligible to evict any key regardless of whether it has a TTL. (a), (c), and (d) don't describe the actual distinction.

</details>

## Real-world reps

- [ ] On a Redis instance you can access, run `CONFIG GET maxmemory-policy` and record what it's currently set to.
- [ ] Pick three keys currently in that instance (or ones you'd add for a real use case) and, for each, write down: does it have a TTL, and if the configured eviction policy fired right now, would this key survive? Note any mismatch between what you assumed and what the policy actually does.
- [ ] Tomorrow: read the primary source's section on eviction policies in full, and decide, for a real cache use case you know of, which specific policy you'd choose and why.

## Going further

- [Docs: "Persistence", Redis](https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
