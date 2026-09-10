---
title: 11. Streams and Pub/Sub as a Messaging Surface
description: Two ways Redis moves messages between clients, and why only one of them is safe to build a queue on
type: lesson
---

# Lesson 11. Streams and Pub/Sub as a Messaging Surface

**Mission link:** Stage 7 opens what Redis does beyond storing a value under a key: moving a message from one client to another. This lesson is the two mechanisms that do it, and why reaching for the wrong one for a queue quietly loses messages the moment a subscriber isn't there to catch them.
**Primary source:** [Docs: "Data types", Redis](https://redis.io/docs/latest/develop/data-types/)
**Prerequisites:** [Lesson 10](0010-sets-sorted-sets-and-probabilistic-structures.md), [maxmemory](../GLOSSARY.md)

## Warm-up

1. ▢ Why does a sorted set beat a plain list for keeping a leaderboard ordered as scores keep changing?

<details markdown="1"><summary>Check</summary>

A sorted set's skip-list backing keeps members ordered automatically at O(log N) per insertion or score update; keeping a plain list sorted by hand costs O(N) to find and insert at the correct position every time a score changes.

</details>

2. ▢ Why might a bitmap beat a set for tracking a simple yes/no per user ID across 50 million users?

<details markdown="1"><summary>Check</summary>

A bitmap costs one bit per ID regardless of how many are actually marked, a fixed, predictable footprint; a set storing the same information as individual member entries carries far more per-member overhead at that scale.

</details>

## Know this

### Pub/Sub: fire-and-forget, with nothing kept for anyone who wasn't listening

**Pub/Sub** (`PUBLISH channel message`, `SUBSCRIBE channel`) delivers a published message only to clients subscribed to that channel at the exact moment it's published; Redis keeps no record of it afterward. A subscriber that connects a second later, or one that briefly disconnected, simply never sees a message published in that gap, with no error and no way to notice one was missed. This makes Pub/Sub a genuinely good fit for something where a missed message is harmless (a live notification a connected dashboard happens to be showing right now) and a fundamentally wrong fit for anything resembling a queue, a job, or a message a system actually needs delivered.

### Streams: an append-only log, with entry IDs and real consumer groups

A **stream** (`XADD mystream '*' field value`, `XREAD`) is a persisted, append-only log of entries, each automatically assigned an ID (a timestamp plus a sequence number) that can be replayed later with `XRANGE`, unlike Pub/Sub's here-and-gone delivery. A stream's **consumer group** (`XGROUP CREATE`, `XREADGROUP`) tracks, per group, the last entry ID delivered and a **pending entries list (PEL)**, every entry delivered to some consumer but not yet acknowledged with `XACK`. A consumer that crashes mid-processing leaves its unacknowledged entries in the PEL, where `XCLAIM` lets another consumer explicitly take them over after a timeout, rather than losing them the way an unfinished Pub/Sub delivery would.

![Two panels. On the left, pub/sub: a publisher sends a message that reaches only the two subscribers currently connected; a third subscriber that connects a moment later never sees it, since nothing was kept. On the right, a stream: entries are appended to a persisted log with their own IDs; a consumer group tracks each consumer's last-delivered ID and a pending entries list of unacknowledged messages, so a late-joining or crashed consumer can still read from where it left off or have its pending entries reclaimed by another consumer.](images/pubsub-vs-streams.svg)

### How a stream's consumer group differs from Kafka's

Both track group progress and let multiple consumers split the work, but the mechanism differs in a way worth naming precisely: Kafka tracks one committed offset per partition per group, a single number marking how far a group has confirmed reading. A Redis stream's consumer group instead tracks an explicit **pending entries list per consumer**, individually acknowledged per entry via `XACK`, which is closer to a per-message acknowledgment model than Kafka's offset-based one. A stream also has no native cross-node partitioning the way a Kafka topic does (a single stream lives on whatever node holds its key, though Cluster can shard different streams by key across nodes); a Kafka topic's partitions are the unit that spreads one logical stream of data across a cluster from the start.

### Choosing between them isn't about which is "better," it's about what a missed message costs

Pub/Sub's fire-and-forget shape is the right choice specifically when nothing needs to survive a gap in delivery; a stream's persisted log and per-entry acknowledgment is the right choice the moment a message represents work that has to happen, a job to process, an event a downstream system can't be allowed to silently miss. Reaching for Pub/Sub because it looks simpler, for something that's actually a job queue, is the same shape of mistake `data/kafka`'s workspace and this one both warn against from opposite directions: treating a fire-and-forget mechanism as if it had delivery guarantees it was never designed to provide.

## Practice

1. ▢ A service publishes order-confirmation events over Pub/Sub. A consumer service is redeployed and briefly disconnects for a few seconds during the restart. What happens to any order-confirmation events published during that gap?

<details markdown="1"><summary>Hint</summary>

Consider what Pub/Sub actually keeps after a message is published.

</details>

<details markdown="1"><summary>Check</summary>

They're lost entirely. Pub/Sub delivers only to clients subscribed at the exact moment of publishing and keeps no record afterward, so a consumer that was disconnected during that window has no way to retrieve what it missed once it reconnects; nothing was persisted to replay.

</details>

2. ▢ Why does a stream's `XCLAIM` mechanism matter specifically for a consumer that crashes mid-processing, in a way Pub/Sub has no equivalent for?

<details markdown="1"><summary>Check</summary>

A crashed consumer's in-flight entries stay in the consumer group's pending entries list (PEL), unacknowledged; `XCLAIM` lets another consumer explicitly take over those specific entries after a timeout, so the work isn't lost. Pub/Sub has no delivery record at all once a message is sent, so there's nothing analogous to reclaim; a message a crashed subscriber was "processing" simply never existed anywhere Pub/Sub could recover it from.

</details>

3. ▢ Contrast how a Kafka consumer group tracks progress against how a Redis stream's consumer group does.

<details markdown="1"><summary>Check</summary>

Kafka tracks one committed offset per partition per group, a single number marking confirmed progress. A Redis stream's consumer group instead tracks a pending entries list per consumer, acknowledging individual entries one at a time via `XACK`, a closer-to-per-message model than Kafka's single offset marker.

</details>

4. ▢ A team builds a background job queue on Redis Pub/Sub because "it's already there and simpler than setting up a stream." A worker restart during a deploy causes several jobs to silently never run. Diagnose what went wrong, using this lesson's vocabulary.

<details markdown="1"><summary>Check</summary>

Pub/Sub was the wrong mechanism for a job queue in the first place: it has no persistence and no acknowledgment model, so any job published while a worker was disconnected (during the restart) is gone with no trace, and no worker (the same one or a different one) can recover or retry it. A stream's persisted log and consumer-group PEL, with `XACK`/`XCLAIM`, is what a job queue actually needs; choosing Pub/Sub for this traded away exactly the delivery guarantee the use case required.

</details>

5. ▢ Which claim correctly distinguishes Pub/Sub from a Redis stream?

    - a) Both persist every message identically; the only difference is API syntax
    - b) Pub/Sub delivers only to clients connected at publish time with nothing kept afterward; a stream persists entries with IDs and supports consumer groups with per-entry acknowledgment and reclaiming via `XCLAIM`
    - c) Streams cannot support multiple consumers reading the same data independently
    - d) Pub/Sub is always the correct choice for anything resembling a job queue, since it's simpler to set up

<details markdown="1"><summary>Check</summary>

**b)** That's the precise, load-bearing distinction this lesson draws. (a) is false: Pub/Sub keeps nothing after delivery, the opposite of a stream's persisted log. (c) is false: multiple consumer groups can each read the same stream independently, tracking their own separate progress. (d) is false: Pub/Sub's lack of persistence and acknowledgment makes it a poor fit for anything where a missed message has a real cost.

</details>

## Real-world reps

- [ ] Find a system you have access to using Redis Pub/Sub. Check whether a missed message (a brief subscriber disconnect) would actually be harmless for that use case, or whether it's quietly relying on a guarantee Pub/Sub doesn't provide.
- [ ] Find (or design) a job queue built on a Redis stream. Confirm it uses a consumer group with `XACK` (and, ideally, a periodic `XCLAIM` sweep for stuck pending entries) rather than reading with plain `XREAD` and no acknowledgment at all.
- [ ] Tomorrow: read the primary source's sections on Pub/Sub and streams in full, and compare a stream consumer group's pending-entries model against `data/kafka`'s offset-based model, in your own words.

## Going further

- [Docs: "Data types", Redis](https://redis.io/docs/latest/develop/data-types/)
- [Consumer Groups and Rebalancing](../../kafka/reference/consumer-groups-and-rebalancing.md): `data/kafka`'s reference sheet on its offset-based consumer group model, for the direct comparison this lesson draws
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
