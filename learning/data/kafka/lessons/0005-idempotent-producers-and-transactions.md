---
title: 5. Idempotent Producers and Transactions
description: Why idempotence is nearly free but transactions carry the real cost of exactly-once
type: lesson
---

# Lesson 5. Idempotent Producers and Transactions

**Mission link:** This is stage 3's capstone: lesson 4 established that commit ordering alone can't achieve exactly-once, and this lesson is the two mechanisms that actually close the gap, and why they belong in very different cost tiers.
**Primary source:** [Article: "Exactly-once Semantics is Possible: Here's How Kafka Does it", Gustafson and Mehta, Confluent](https://www.confluent.io/blog/exactly-once-semantics-are-possible-heres-how-apache-kafka-does-it/)
**Prerequisites:** [Lesson 4](0004-delivery-semantics.md), [Partition](../GLOSSARY.md)

## Warm-up

1. ▢ Name the three legs of the produce/consume path where loss or duplication can independently occur.

<details markdown="1"><summary>Check</summary>

Producer to broker (retry behavior), the broker's own durability (when it acknowledges relative to replication), and consumer to processing (whether the offset commits before or after processing).

</details>

2. ▢ Contrast `acks=1` and `acks=all`. Which protects against a leader crash right after acknowledging?

<details markdown="1"><summary>Check</summary>

`acks=1` waits only for the partition leader's acknowledgment, so a leader crash before replication can still lose an already-acked message. `acks=all` waits for every in-sync replica, so the message survives a leader crash, at the cost of higher produce latency.

</details>

## Know this

### The idempotent producer: fixing the producer-to-broker leg, almost for free

Lesson 4's first leg, a producer retrying a send whose acknowledgment was lost, risks writing a duplicate if the original send actually succeeded. The **idempotent producer** fixes this directly: each producer instance gets a unique producer ID assigned by the broker, and every message it sends to a partition carries a sequence number that increases monotonically. The broker tracks the last sequence number it accepted for each producer-ID-and-partition pair, and if a retried send arrives with a sequence number it has already accepted, the broker recognizes it as a duplicate and discards it rather than writing it again. This eliminates the producer-retry duplication failure mode with only a small metadata overhead per message, no meaningful latency or throughput cost, which is why enabling it (`enable.idempotence=true`, the default in modern Kafka versions) is close to a free correctness improvement.

### Idempotence alone doesn't solve read-process-write atomicity

A stream-processing application commonly does one logical unit of work made of several separate steps: consume a message from one topic, process it, produce a result to another topic, and commit the offset for the original message. The idempotent producer only guarantees no duplicate writes from one producer to one partition; it says nothing about whether these several steps, spanning two different topics (and the internal `__consumer_offsets` topic the commit itself writes to), succeed or fail together. If producing the result succeeds but committing the offset fails, or the reverse, the application ends up with a duplicated or dropped result depending on which side failed, even with idempotence fully enabled on every producer involved.

### Transactions: atomicity across multiple writes, including the offset commit

Kafka's **transactions** mechanism wraps a producer's writes to multiple partitions and topics, explicitly including a write to `__consumer_offsets`, into one atomic unit: either every write in the transaction becomes visible to consumers, or none of them do. A **transaction coordinator** (a broker, playing a role analogous to lesson 2's group coordinator) writes markers to the log recording whether a transaction committed or aborted. A consumer configured with `isolation.level=read_committed` only ever sees messages from transactions that actually committed, filtering out anything from a transaction that aborted or is still in doubt, which is what makes the read-process-write cycle atomic end to end, offset commit included.

### Where the real cost actually lives

Idempotence and transactions are not the same cost tier, and treating "exactly-once" as one monolithic expensive feature misses that. Idempotence costs almost nothing. Transactions cost something real: added latency, since a transactional commit requires an extra round trip to write its commit marker through the transaction coordinator; reduced throughput for `read_committed` consumers, since they may need to wait for a transaction's outcome before delivering its messages, even a transaction that ultimately commits successfully; and real operational complexity, since a producer's transactional ID has to be managed carefully across restarts to avoid a rolling deployment accidentally running two producer instances under the same transactional ID at once, which triggers Kafka's fencing mechanism to protect against exactly that. The defensible position: enable idempotence essentially always, since it costs nothing meaningful, and reach for full transactions specifically when read-process-write atomicity is actually needed, not as a blanket default for every simple producer.

## Practice

1. ▢ Describe how the idempotent producer mechanism (a producer ID plus a per-partition sequence number) prevents a retried send from being written as a duplicate.

<details markdown="1"><summary>Check</summary>

Each message carries a monotonically increasing sequence number for its producer-ID-and-partition pair. The broker tracks the last sequence number it accepted for that pair; if a retry arrives with a sequence number already accepted, the broker recognizes it as a duplicate of a send that already succeeded and discards it rather than writing it again.

</details>

2. ▢ Why doesn't idempotence alone solve the atomicity problem in a consume-process-produce-commit cycle? Describe the specific inconsistency that can still occur.

<details markdown="1"><summary>Check</summary>

Idempotence only guarantees no duplicate writes from one producer to one partition; it says nothing about whether producing a result and committing the original offset succeed or fail together. If producing the result succeeds but the offset commit fails (or the reverse), the application ends up with a duplicated or dropped result, even with every producer involved fully idempotent.

</details>

3. ▢ What does `isolation.level=read_committed` change about what a consumer sees, and how does that relate to the transaction coordinator's commit and abort markers?

<details markdown="1"><summary>Hint</summary>

Consider what a consumer would see without filtering by transaction outcome.

</details>

<details markdown="1"><summary>Check</summary>

A consumer set to `read_committed` only sees messages belonging to transactions the coordinator has marked as committed, filtering out messages from transactions that aborted or are still undecided. The coordinator's commit and abort markers written to the log are exactly what the consumer checks to make that filtering decision.

</details>

4. ▢ Contrast the cost of enabling idempotence alone against enabling full transactions. Which is essentially free, and which carries real latency and throughput cost, and why?

<details markdown="1"><summary>Check</summary>

Idempotence is essentially free: it adds only small per-message metadata overhead with no meaningful latency or throughput impact. Transactions carry a real cost: an extra round trip through the transaction coordinator to write the commit marker adds latency, and `read_committed` consumers may need to wait for a transaction's outcome before delivering its messages, reducing throughput even for transactions that ultimately succeed.

</details>

5. ▢ Which claim is true of idempotent producers and transactions?

   - a) Idempotence and transactions cost roughly the same in latency and throughput, so there's no reason to distinguish them
   - b) Idempotence fixes producer-retry duplication at almost no cost, while transactions add real latency and throughput cost to achieve atomicity across multiple writes, including the offset commit
   - c) Enabling idempotence alone is sufficient to make a consume-process-produce-commit cycle atomic
   - d) A consumer set to read_committed sees every message written, regardless of the transaction it belongs to

<details markdown="1"><summary>Check</summary>

**b)** That cost distinction is exactly the lesson's central point. (a) is false: idempotence is close to free, while transactions add a real, measurable cost. (c) is false: idempotence only covers one producer writing to one partition, not atomicity across the whole cycle. (d) is false: `read_committed` specifically filters out messages from aborted or undecided transactions.

</details>

## Real-world reps

- [ ] Check whether `enable.idempotence` is set on a producer you use, and if not, consider whether there's a reason not to enable it given how little it costs.
- [ ] For a stream-processing pipeline you have or are designing (consume, process, produce, commit), decide whether it actually needs transactional atomicity, or whether idempotence alone is sufficient for its failure tolerance.
- [ ] Tomorrow: read the primary source's section on transactional IDs and producer fencing, and note what happens if a rolling deployment briefly runs two producer instances under the same transactional ID.

## Going further

- [Article: "Exactly-once Semantics is Possible: Here's How Kafka Does it", Gustafson and Mehta, Confluent](https://www.confluent.io/blog/exactly-once-semantics-are-possible-heres-how-apache-kafka-does-it/)
- [Docs: "Message Delivery Semantics", Apache Kafka](https://kafka.apache.org/documentation/#semantics)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
