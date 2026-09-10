---
title: 12. Key Expiration: Lazy vs Active Expiry
description: Why a key's TTL reaching zero doesn't remove it from memory by itself, and the two mechanisms that eventually do
type: lesson
---

# Lesson 12. Key Expiration: Lazy vs Active Expiry

**Mission link:** This is stage 7's capstone. Lesson 11 covered messages moving between clients; this lesson closes the loop on lesson 1's eviction policy by covering the other way a key actually leaves Redis: its TTL running out, and the two distinct mechanisms that make that removal actually happen.
**Primary source:** [Docs: "Key eviction", Redis](https://redis.io/docs/latest/develop/reference/eviction/)
**Prerequisites:** [Lesson 11](0011-streams-and-pubsub-as-messaging.md), [Eviction policy](../GLOSSARY.md)

## Warm-up

1. ▢ Why is Pub/Sub a poor fit for a job queue, even though it's simpler to set up than a stream with a consumer group?

<details markdown="1"><summary>Check</summary>

Pub/Sub delivers only to clients connected at the exact moment of publishing and keeps no record afterward; a worker that's briefly disconnected loses any job published during that gap with no way to recover it, exactly the guarantee a job queue needs and Pub/Sub doesn't provide.

</details>

2. ▢ How does a Redis stream's consumer group track progress differently from a Kafka consumer group?

<details markdown="1"><summary>Check</summary>

Kafka tracks one committed offset per partition per group. A Redis stream's consumer group tracks a pending entries list per consumer, acknowledged per entry via `XACK`, a closer-to-per-message model than Kafka's single offset marker.

</details>

## Know this

### Setting and checking a TTL

`EXPIRE key seconds` (or `PEXPIRE key milliseconds`, `EXPIREAT key unix-timestamp`) attaches a time-to-live to an existing key; `TTL key` reports the remaining seconds (`-1` if the key exists with no TTL set, `-2` if the key doesn't exist at all, both worth distinguishing from an actual positive countdown). A TTL is what lesson 1's `volatile-*` eviction policies specifically check for: a key with no TTL is never eligible under `volatile-lru` or `volatile-ttl`, regardless of memory pressure.

### Lazy expiration: nothing happens until something looks

Redis does not delete a key the instant its TTL reaches zero. **Lazy expiration** means a key past its TTL is still physically present in memory until the next time *that specific key* is accessed, a `GET`, an `EXISTS`, any command that touches it; only then does Redis check the TTL, find it's passed, delete the key, and report back as if it had never been there. A key nobody ever reads again after it should have expired can sit in memory indefinitely under lazy expiration alone, since nothing ever triggers the check.

![A timeline marks the moment a key's TTL reaches zero. In the lazy expiry row, the key still occupies memory until something actually accesses it, well after the TTL passed, at which point it's found to be expired and removed. In the active expiry row, a background cycle samples keys with a TTL several times a second and removes this one within its next sweep, shortly after the TTL passed, regardless of whether anything ever accessed it again.](images/lazy-vs-active-expiry.svg)

### Active expiration: a background sweep that doesn't wait to be asked

**Active expiration** runs a background cycle, several times a second by default, that samples a random selection of keys carrying a TTL, checks each one, and deletes any that have already expired; if a large share of the sampled keys turn out to be expired, it immediately runs another pass rather than waiting for the next scheduled one. This is exactly what reclaims memory from a key nobody ever accesses again after its TTL passes, the case lazy expiration alone would leave sitting in memory forever. Active expiration runs on its own schedule, independent of `maxmemory` pressure; it removes an expired key regardless of whether the instance is anywhere near its memory limit.

### How this interacts with eviction, and a subtlety in replication

Active expiration and lesson 1's eviction are two separate mechanisms, triggered by two separate conditions: expiration runs continuously based on a key's own TTL, whether or not memory is tight; eviction only activates once `maxmemory` is actually reached, and only under a policy that permits it (`noeviction` never evicts anything; `volatile-*` evicts only keys with a TTL; `allkeys-*` evicts any key). A key with a TTL is a candidate for both, on independent triggers; a key with no TTL will never be removed by expiration at all, and can only be removed by eviction under an `allkeys-*` policy. One subtlety worth knowing: a **replica** doesn't expire a key on its own local clock, since clock differences between machines are exactly the kind of problem that makes trusting two independent clocks to agree unsafe; instead, the primary performs the actual deletion and propagates it as an explicit `DEL` to replicas, while a replica masks an expired-but-not-yet-deleted key from client reads in the meantime, so a client never observes a key past its TTL even before the propagated delete arrives.

## Practice

1. ▢ A key is set with `EXPIRE session:42 60`. Sixty seconds pass, and nothing accesses `session:42` again. Is it still occupying memory at that moment, considering lazy expiration alone?

<details markdown="1"><summary>Check</summary>

Yes, potentially. Lazy expiration only checks and removes a key when something actually accesses it; if nothing touches `session:42` after its TTL passes, lazy expiration alone never triggers, and the key stays in memory until either something does access it or active expiration's background sweep happens to sample and remove it.

</details>

2. ▢ Why does active expiration exist at all, given that lazy expiration already prevents an expired key from ever being incorrectly returned to a client?

<details markdown="1"><summary>Hint</summary>

Consider what happens to memory, not correctness, for a key nobody ever reads again.

</details>

<details markdown="1"><summary>Check</summary>

Lazy expiration alone is correct (a client never sees an expired value), but it does nothing to reclaim the memory of a key that's expired and simply never gets accessed again; that key would sit in memory indefinitely. Active expiration's background sweep exists specifically to find and remove exactly these otherwise-orphaned expired keys, regardless of whether anything ever touches them again.

</details>

3. ▢ A key has no TTL set at all. Under `volatile-lru` (evict only keys with a TTL, least-recently-used first), and separately under active expiration, what happens to it?

<details markdown="1"><summary>Check</summary>

Nothing, under either mechanism. Active expiration only ever samples and removes keys that actually carry a TTL; a key with none is never a candidate for it. `volatile-lru` specifically excludes keys with no TTL from eviction as well, so a key with no TTL persists under both mechanisms; only an `allkeys-*` policy, once `maxmemory` is hit, could ever remove it.

</details>

4. ▢ Why doesn't a replica expire a key on its own local clock, even though it could technically check the same TTL the primary is tracking?

<details markdown="1"><summary>Check</summary>

Clock differences between the primary and the replica could make the replica decide a key has expired at a different moment than the primary does, risking the two disagreeing about whether the key still exists. Instead, the primary performs the actual expiration and propagates it as an explicit `DEL`, while the replica masks an expired-but-not-yet-deleted key from reads in the meantime, so a client never sees a stale value even before the replica physically deletes it.

</details>

5. ▢ Which claim correctly distinguishes lazy expiration from active expiration?

    - a) Lazy expiration runs on a fixed background schedule; active expiration only triggers when a key is accessed
    - b) Lazy expiration removes a key only when something accesses it after its TTL has passed; active expiration is a background sweep that removes expired keys regardless of whether anything accesses them
    - c) Only one of the two mechanisms can be active on a given Redis instance at a time
    - d) Active expiration is triggered by `maxmemory` pressure, the same condition that triggers eviction

<details markdown="1"><summary>Check</summary>

**b)** That's the exact distinction: access-triggered versus continuously scheduled. (a) is false and reverses the two mechanisms. (c) is false: both run simultaneously by default, covering different cases. (d) is false: active expiration runs on its own schedule independent of memory pressure, unlike eviction, which specifically requires `maxmemory` to be reached.

</details>

## Real-world reps

- [ ] On a Redis instance you can access, run `TTL` against a handful of keys and note which return `-1` (no TTL), which return `-2` (don't exist), and which return an actual countdown.
- [ ] For a key pattern you use that carries a TTL but might rarely be read again after it should expire, consider whether relying on lazy expiration alone would leave memory tied up longer than expected, and whether active expiration's default sweep rate is fast enough for your workload.
- [ ] Tomorrow: read the primary source's section on expiration in full, and note the exact default sweep frequency and sample size active expiration uses, and what setting (if any) controls it.

## Going further

- [Docs: "Key eviction", Redis](https://redis.io/docs/latest/develop/reference/eviction/)
- [Docs: "Data types", Redis](https://redis.io/docs/latest/develop/data-types/)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
