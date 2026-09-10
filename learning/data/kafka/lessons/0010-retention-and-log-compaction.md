---
title: 10. Retention and Log Compaction
description: How long a message actually survives in a topic, and the other cleanup policy that keeps a key's history instead of its age
type: lesson
---

# Lesson 10. Retention and Log Compaction

**Mission link:** Stage 6 opens the part of a topic layout lesson 7 assumed but never named: how long data actually lives, and under which of two genuinely different deletion models. A defended layout has to state this, not leave it as whatever the cluster default happens to be.
**Primary source:** [Docs: "Design", Apache Kafka](https://kafka.apache.org/documentation/#design)
**Prerequisites:** [Lesson 9](0009-kafka-connect-basics.md), [Partition](../GLOSSARY.md)

## Warm-up

1. ▢ Does using Kafka Connect grant a new delivery guarantee beyond what the underlying producer and consumer APIs already provide?

<details markdown="1"><summary>Check</summary>

No. A sink connector's delivery and ordering guarantees still come from whatever the topic and its consumer-side configuration actually provide, and a source connector's exactly-once behavior still relies on the same idempotent-producer and transaction machinery lesson 5 derived.

</details>

2. ▢ Why does more partitions cost something beyond just capping consumer parallelism?

<details markdown="1"><summary>Check</summary>

Every partition adds file and replication overhead on every broker holding a replica, and adds to the leadership reassignment work a broker failure or restart has to do; producer batching efficiency can also suffer, since the same produce rate spread across more partitions shrinks the batch each producer accumulates per partition.

</details>

## Know this

### `cleanup.policy=delete`: whole segments age out, not individual messages

The default cleanup policy, **delete**, removes data once it's older than `retention.ms` (or exceeds `retention.bytes`, a size-based cap), but not at the granularity of one message at a time: a partition's log is physically stored as a sequence of **segments**, and Kafka deletes an entire segment once every message inside it has aged past retention, not individual messages within a segment still holding some data younger than the cutoff. This means the practical deletion boundary is closer to "whichever segment boundary falls after the retention cutoff" than an exact per-message guarantee, and it's why retention isn't instantaneous the moment a message crosses the configured age: it waits for that message's segment to close out entirely.

### `cleanup.policy=compact`: keep the latest value per key, regardless of age

**Log compaction** is a genuinely different cleanup model: instead of deleting by age, a background **log cleaner** thread retains only the most recent value for each distinct key in the topic, removing older values for that same key once it runs. A compacted topic's guarantee is "at least the latest value for every key that's ever been written still exists somewhere in the log," not "every message survives for some fixed window." This is the shape a **changelog topic** needs, a topic backing a materialized view or a key-value store's replicated state, where a consumer replaying the topic from the beginning should reconstruct the current state of every key, not relay every historical write that key ever had.

![Two partitions shown as a sequence of messages. On the left, cleanup.policy=delete: messages are grouped into segments, and a whole segment is deleted once every message in it is older than retention.ms, regardless of whether any individual message inside it might still be wanted. On the right, cleanup.policy=compact: multiple messages for the same key, such as key A appearing three times, are compacted down to just the latest value for that key, A3, with the older A1 and A2 removed, while a different key's single message, B1, is kept as is.](images/retention-vs-compaction.svg)

### Compaction isn't synchronous, and a tombstone is how a key actually disappears

The log cleaner runs periodically and opportunistically, not on every single write; a consumer reading a compacted topic shortly after several writes to the same key can still see older, not-yet-compacted values for a while, since compaction hasn't caught up to that segment yet. To actually remove a key from a compacted topic entirely (not just keep its latest value), a producer writes a **tombstone**, a message with that key and a `null` value; the cleaner removes the key's prior values as usual, and after `delete.retention.ms` (a grace period giving any consumer that hasn't yet seen the tombstone a chance to), the tombstone itself is also removed, at which point the key is gone from the log completely. `cleanup.policy=compact,delete` combines both: keep the latest value per key, but also enforce an outer time bound, useful for cleaning up genuinely stale keys after a grace period rather than keeping every key's latest value forever.

### Why this belongs in a defended topic layout, not left as a default

Lesson 7's defended layout named a key choice, a partition count, and a delivery guarantee; it never named how long the data itself survives, or under which deletion model. `cleanup.policy` changes what a consumer replaying the topic from the start actually gets: a full history within a time window under `delete`, or a materialized, latest-value-per-key snapshot under `compact`, a materially different contract a downstream consumer's own logic has to be written against. Leaving `cleanup.policy` and `retention.ms` as whatever the cluster-wide default happens to be is exactly the kind of unstated, accidental decision the rest of this mission has argued against for every other setting.

## Practice

1. ▢ A topic is configured with `retention.ms` set to 7 days. A message is written into a segment that also contains messages up to 2 days older. Does that specific message get deleted the instant it turns 7 days old?

<details markdown="1"><summary>Hint</summary>

Consider what Kafka actually deletes: a message, or something larger containing it.

</details>

<details markdown="1"><summary>Check</summary>

Not necessarily the instant it turns 7 days old. Kafka deletes whole segments once every message in that segment has aged past `retention.ms`; if the segment also holds messages up to 2 days older than this one, the segment (and this message along with it) isn't deleted until the oldest message in that segment also crosses 7 days, meaning this specific message can survive somewhat past its own 7-day mark.

</details>

2. ▢ A topic backs a materialized view of "current account balance per user ID." Which cleanup policy fits, and what would `cleanup.policy=delete` with a 7-day retention get wrong for this use case?

<details markdown="1"><summary>Check</summary>

`cleanup.policy=compact` fits: the topic needs to guarantee the latest balance for every user ID that's ever existed, regardless of how long ago it was last updated, not a rolling window of recent writes. `delete` with a 7-day retention would silently lose the state of any user ID that hasn't been updated in the last 7 days, breaking a consumer trying to reconstruct the full current state from the topic.

</details>

3. ▢ A consumer reads a compacted topic moments after a key was updated twice in quick succession. Is it guaranteed to see only the final value, skipping the intermediate one? Why or why not?

<details markdown="1"><summary>Check</summary>

Not necessarily. The log cleaner runs periodically, not synchronously on every write, so a consumer reading shortly after the writes can still see the intermediate, not-yet-compacted value if the cleaner hasn't processed that segment yet. Compaction guarantees the latest value eventually remains, not that intermediate values are immediately invisible.

</details>

4. ▢ A team wants a key to actually disappear from a compacted topic entirely, not just have its latest value retained. What do they write, and what determines how long it takes for the key to actually vanish from the log?

<details markdown="1"><summary>Check</summary>

A tombstone: a message for that key with a `null` value. The cleaner removes the key's prior values as usual, and the tombstone itself is retained for `delete.retention.ms` (a grace period letting any consumer that hasn't yet seen it catch up) before it, too, is removed, at which point the key is fully gone from the log.

</details>

5. ▢ Which claim correctly distinguishes `cleanup.policy=delete` from `cleanup.policy=compact`?

    - a) Both delete data at the same granularity, individual messages, just triggered by different conditions (age versus key)
    - b) `delete` removes whole segments once every message in them is past `retention.ms`; `compact` retains only the latest value per key regardless of age, via a periodic, not synchronous, log cleaner
    - c) A compacted topic guarantees a consumer never sees an outdated value for any key, even momentarily
    - d) `cleanup.policy=compact,delete` is invalid; a topic must choose exactly one policy

<details markdown="1"><summary>Check</summary>

**b)** That's the precise mechanism and guarantee shape for each policy. (a) is false: `delete` operates at the segment granularity, not per-message. (c) is false: the cleaner runs periodically, so a consumer can momentarily see a stale, not-yet-compacted value. (d) is false: `compact,delete` is a valid, combined policy, keeping the latest value per key while also enforcing an outer time bound.

</details>

## Real-world reps

- [ ] For a topic you have access to, check its `cleanup.policy` and, if `delete`, its `retention.ms`/`retention.bytes`. Confirm whether that matches what a consumer replaying the topic from the start would actually need.
- [ ] Find (or design) a topic that should logically be a changelog (representing current state per key rather than an event history). Check whether it's actually configured with `cleanup.policy=compact`, or is quietly relying on `delete` with a long retention instead.
- [ ] Tomorrow: read the primary source's section on log compaction in full, and note what it says about the minimum guarantees compaction provides for a consumer that never falls behind versus one that's frequently disconnected.

## Going further

- [Docs: "Design", Apache Kafka](https://kafka.apache.org/documentation/#design)
- [Docs: "Topic Configs", Apache Kafka](https://kafka.apache.org/documentation/#topicconfigs)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
