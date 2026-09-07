---
title: 6. Partition Key Choice and Ordering Guarantees
description: Choosing a partition key means choosing both what ordering you get and what parallelism you give up, in the same decision
type: lesson
---

# Lesson 6. Partition Key Choice and Ordering Guarantees

**Mission link:** Stage 4 opens designing the layout: lesson 1 established that a key routes a message to a partition deterministically; this lesson is choosing that key deliberately, since it decides both the ordering guarantee and the parallelism ceiling in a single decision.
**Primary source:** [Docs: "Design", Apache Kafka](https://kafka.apache.org/documentation/#design)
**Prerequisites:** [Lesson 5](0005-idempotent-producers-and-transactions.md), [Partition](../GLOSSARY.md)

## Warm-up

1. ▢ Contrast the cost of enabling idempotence alone against enabling full transactions.

<details markdown="1"><summary>Check</summary>

Idempotence is essentially free: small per-message metadata overhead, no meaningful latency or throughput impact. Transactions carry a real cost: added latency for the commit marker round trip, and reduced throughput for `read_committed` consumers waiting on a transaction's outcome.

</details>

2. ▢ How does a producer decide which partition a keyed message lands in, versus an unkeyed one?

<details markdown="1"><summary>Check</summary>

With a key, the producer hashes the key and always sends messages with that key to the same partition. Without a key, messages spread across partitions (round-robin or a sticky variant) with no ordering relationship between them.

</details>

## Know this

### A key choice is one decision with two consequences

Choosing what to key a topic's messages by isn't only a decision about ordering; it's simultaneously a decision about parallelism, because both follow from the same fact: every message with a given key always lands in the same partition, and a partition is read by only one consumer at a time. Preserving ordering for a given key necessarily means that key's entire message stream is processed sequentially by whatever single consumer is currently assigned that partition; there is no way to parallelize processing *within* one key's own stream, only *across* different keys' streams landing in different partitions.

### The same topic, two different keys, two different trade-offs

Take an e-commerce order-events topic. Keying it by `customer_id` preserves ordering across everything that happens to a given customer, useful if the application needs to process a customer's event history in the order it occurred. But it also means all of one customer's traffic, however much of it there is, funnels through a single partition regardless of how many partitions the topic has. If one customer produces disproportionately more events than others, a **hot key**, that one partition, and the one consumer serving it, becomes a bottleneck no amount of adding more partitions or consumer instances can fix, since that customer's traffic can never be split across more than the one partition it hashes to.

Keying the same topic by `order_id` instead spreads a single customer's different orders across different partitions, removing that hot-key risk and improving parallelism, at the cost of losing ordering *across* a customer's different orders: only the events within a single order's own stream are guaranteed to arrive in order, not the customer's activity as a whole. Neither choice is universally correct; each is the right choice for a different actual ordering requirement.

### Hot-key skew is created at design time, not just discovered at runtime

Lesson 3 named lag concentrated on one specific partition as a sign of uneven skew, something to diagnose after the fact. This lesson is where that skew actually gets created, or avoided, in the first place: the key choice is the load-balancing decision. A key that distributes traffic close to evenly across the topic's expected traffic pattern prevents the hot-key symptom from ever appearing; a key chosen without considering the traffic distribution behind it creates the exact bottleneck lesson 3 taught how to recognize.

### No key at all is sometimes the correct choice, not a lazy default

Some topics carry independent, self-contained events with no ordering requirement across any subset of them at all. For that kind of topic, choosing no key, letting messages spread round-robin or sticky across partitions, maximizes parallelism and eliminates hot-key risk entirely, since there is no ordering guarantee being traded away to get it. Choosing no key isn't skipping a decision; it's the correct decision specifically when no ordering constraint exists to preserve in the first place.

## Practice

1. ▢ An order-events topic is keyed by `customer_id`. What ordering guarantee does this give, and what parallelism limitation does it create for one especially active customer?

<details markdown="1"><summary>Check</summary>

It guarantees that a given customer's own events arrive in the order they were produced, since they all hash to the same partition. The limitation: that customer's entire event stream is processed sequentially by a single consumer, and no matter how many partitions or consumer instances the topic has, that one customer's traffic can never be split across more than the single partition it always routes to, making an especially active customer a potential bottleneck.

</details>

2. ▢ Contrast keying the same order-events topic by `customer_id` versus by `order_id`. What ordering is preserved or lost in each, and what's the parallelism consequence?

<details markdown="1"><summary>Check</summary>

Keying by `customer_id` preserves ordering across everything that happens to a given customer, but funnels all of that customer's traffic through one partition, risking a hot-key bottleneck. Keying by `order_id` preserves ordering only within a single order's own events, losing ordering across a customer's different orders, but spreads a customer's various orders across different partitions, improving parallelism and removing that specific hot-key risk.

</details>

3. ▢ Why is a hot key better understood as a design-time problem to solve through the key choice itself, rather than purely an operational problem to fix by adding more consumers?

<details markdown="1"><summary>Hint</summary>

Consider what happens to a hot key's traffic no matter how many consumers are added.

</details>

<details markdown="1"><summary>Check</summary>

A hot key's traffic always routes to the same single partition regardless of how many consumers exist in the group; adding more consumer instances doesn't split that key's own traffic across more of them, since only one consumer reads a given partition at a time. The bottleneck can only be fixed by changing what the key actually is (or how granular it is), which is a design-time decision, not something operational scaling around it can resolve.

</details>

4. ▢ Describe a scenario where choosing no key at all for a topic is actually the correct choice, not a lazy default.

<details markdown="1"><summary>Check</summary>

A topic carrying independent, self-contained events with no ordering requirement across any subset of them, for instance, isolated log entries or metrics readings that never need to be processed in relation to one another. Choosing no key here maximizes parallelism and avoids any hot-key risk, since there's no ordering guarantee being given up in exchange, making it the deliberately correct choice rather than an unconsidered default.

</details>

5. ▢ Which claim is true of choosing a partition key?

   - a) A key choice only affects ordering, with no consequence for parallelism
   - b) The key choice determines both the ordering guarantee a topic provides and the granularity at which its traffic can be parallelized, since both follow from same-key-same-partition routing
   - c) Adding more partitions always fixes a hot-key bottleneck, regardless of what the key is
   - d) Choosing no key at all is always a worse choice than choosing some key, regardless of the topic's ordering requirements

<details markdown="1"><summary>Check</summary>

**b)** Both consequences follow from the same underlying routing fact, which is why the key choice is one decision, not two independent ones. (a) is false: since one key always maps to one partition, ordering and parallelism are tied together by construction. (c) is false: a hot key's traffic still funnels through the same single partition no matter how many total partitions exist. (d) is false: for a topic with no ordering requirement at all, no key is the deliberately correct choice, not an inferior one.

</details>

## Real-world reps

- [ ] For a topic you produce to or plan to produce to, identify what it's currently keyed by (or not keyed at all), and name the specific ordering requirement that choice is meant to preserve.
- [ ] Estimate whether that topic's traffic distribution across keys is likely to be even or skewed, and whether a different key granularity would reduce hot-key risk.
- [ ] Tomorrow: for a topic with no key currently, write down whether it actually has an ordering requirement across any subset of its messages, and if so, what key would be needed to preserve it.

## Going further

- [Docs: "Design", Apache Kafka](https://kafka.apache.org/documentation/#design)
- [Docs, Apache Kafka](https://kafka.apache.org/documentation/)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
