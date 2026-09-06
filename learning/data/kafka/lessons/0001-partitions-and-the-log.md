---
title: 1. Partitions and the Log
description: The unit everything else in this workspace (ordering, parallelism, consumer groups) is built around
type: lesson
---

# Lesson 1. Partitions and the Log

**Mission link:** "Own the log" starts with the log's actual unit of storage and parallelism. Every later decision in this mission, ordering, consumer-group layout, delivery guarantees, is stated in terms of a partition, not a topic.
**Primary source:** [Docs: "Design", Apache Kafka](https://kafka.apache.org/documentation/#design)
**Prerequisites:** none

## Know this

### A topic is split into partitions

A Kafka **topic** isn't one log; it's a named collection of one or more **partitions**, each of which is its own independent, append-only, ordered log. A message written to a topic lands in exactly one of its partitions.

Two mechanisms decide which partition a message lands in:

- **With a key**, the producer hashes the key and always sends messages with that same key to the same partition. This is what preserves per-key ordering.
- **Without a key**, messages are spread across partitions (round-robin, or a sticky variant), with no ordering relationship between them at all.

### The ordering guarantee is per-partition, not per-topic

Kafka guarantees message order **only within a single partition**. Two messages in different partitions of the same topic have no guaranteed relative order, no matter what order they were produced in. This is a direct consequence of partitions being independent logs: there's no single global sequence across them to preserve.

Practically, this means: if you need strict ordering between two messages, they must be produced with the same key (or written to a single-partition topic). Ordering across an entire topic's traffic, with more than one partition, is not something Kafka provides, and no amount of consumer-side cleverness recovers it if the producer didn't route the messages to the same partition in the first place.

### Partitions are the unit of parallelism

A partition is also the unit of **parallelism**, in two independent ways:

- Across a cluster, different partitions of a topic can live on (and be served by) different brokers, so a topic's total throughput scales with its partition count spread across machines.
- Within a consumer group, Kafka's rule is that **only one consumer instance in a group reads a given partition at a time**. So a topic with 6 partitions can have at most 6 consumer instances in one group doing useful work simultaneously; a 7th instance in that group sits idle. Partition count is therefore a hard ceiling on a consumer group's parallelism, decided at topic-creation time (or whenever partitions are added).

### Increasing partition count later has a real cost

Partitions can be added to an existing topic, but existing messages already written under the old partition count are not reshuffled. If a topic relies on key-based ordering (same key always in the same partition), adding partitions changes which partition a given key hashes to *going forward*, while everything already written stays where it is. The result: messages for the same key can now be split across two partitions, one from before the change and one after, silently breaking the ordering guarantee that keyed producers were relying on. This is why partition count is usually treated as a decision made upfront rather than a knob tuned casually later.

## Practice

1. ▢ In one sentence, what is Kafka's ordering guarantee, and at what scope does it apply?

<details markdown="1"><summary>Check</summary>

Kafka guarantees message order only within a single partition; it does not guarantee any order between messages in different partitions of the same topic.

</details>

2. ▢ A team wants strict global ordering across all events in a topic, and also wants high throughput from many partitions. Can they have both? What's the actual trade-off?

<details markdown="1"><summary>Hint</summary>

Where does Kafka's ordering guarantee stop applying once there's more than one partition?

</details>

<details markdown="1"><summary>Check</summary>

Not both, at least not from Kafka's guarantee alone. Strict global ordering across all events requires a single partition (so there's only one log to order), which caps throughput and parallelism to what one partition (and one consumer at a time) can handle. Spreading across multiple partitions for throughput means giving up cross-partition ordering; only per-key ordering (via consistent key-to-partition hashing) survives.

</details>

3. ▢ A topic has been running in production for months with keyed messages, relying on same-key-same-partition ordering. An operator increases its partition count to improve throughput. What breaks, and why?

<details markdown="1"><summary>Check</summary>

Per-key ordering can silently break. Existing messages already written under the old partition count stay where they are; they are not reshuffled. But new messages for the same key now hash to a partition count that includes the new partitions, which can route them to a different partition than where that key's earlier messages live. A consumer processing "all of this key's messages in order" may now see them split across two partitions with no ordering relationship between the two.

</details>

4. ▢ A topic has 4 partitions. What determines the maximum number of consumer instances in one consumer group that can be actively processing it in parallel?

   - a) The number of brokers in the cluster
   - b) The partition count: at most 4, one consumer per partition
   - c) The number of unique keys ever produced to the topic
   - d) The replication factor configured for the topic

<details markdown="1"><summary>Check</summary>

**b)** The partition count. Only one consumer instance in a group reads a given partition at a time, so 4 partitions caps active parallel consumption at 4 instances; a 5th instance in the same group would sit idle.

</details>

## Real-world reps

- [ ] On a Kafka cluster you can access (or a local single-node setup), create a topic with 3 partitions and produce 10 keyed messages using only 2 distinct keys. Consume them and confirm which partition each key's messages landed in.
- [ ] For that same topic, produce several messages with no key at all, and observe how they're distributed across partitions compared to the keyed messages.
- [ ] Tomorrow: read the primary source's section on partitions in full, and write down, for a real workload you know of, what partition count you'd choose and why.

## Going further

- [Docs: "Message Delivery Semantics", Apache Kafka](https://kafka.apache.org/documentation/#semantics)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
