---
title: 7. Partition-Count Trade-offs and Designing a Topic Layout
description: Why more partitions isn't free, and what a fully defended topic layout has to name from every earlier stage
type: lesson
---

# Lesson 7. Partition-Count Trade-offs and Designing a Topic Layout

**Mission link:** This is stage 4's capstone: lessons 1 and 6 established partition count as a hard ceiling on consumer parallelism and showed how a key choice ties into it; this lesson is choosing the actual number, and pulling every earlier stage together into one defended layout.
**Primary source:** [Docs: "Design", Apache Kafka](https://kafka.apache.org/documentation/#design)
**Prerequisites:** [Lesson 6](0006-partition-key-choice.md), [Partition](../GLOSSARY.md)

## Warm-up

1. ▢ Why is a hot key a design-time problem best addressed through the key choice itself, rather than an operational problem to fix by adding more consumers?

<details markdown="1"><summary>Check</summary>

A hot key's traffic always routes to the same single partition, regardless of how many consumer instances exist, since only one consumer reads a given partition at a time. Adding consumers doesn't split that key's traffic across more of them; only changing the key itself can fix it.

</details>

2. ▢ A topic has 4 partitions. What determines the maximum number of consumer instances in one group that can actively process it in parallel?

<details markdown="1"><summary>Check</summary>

The partition count: at most 4, since only one consumer instance in a group reads a given partition at a time.

</details>

## Know this

### More partitions isn't strictly more parallelism with no downside

Lesson 1 established partition count as a hard ceiling on consumer parallelism, which makes "more partitions" sound like a purely upward lever. It isn't: partition count also has real costs that scale with the total number of partitions across an entire cluster, not just within one topic. Every partition needs its own files on disk and its own replication traffic between brokers, so a cluster carrying far more partitions than it needs strains broker memory and file-handle limits, and slows down leader election and other controller operations during a broker failure or restart, since more partitions means more leadership reassignment work to do. More partitions also spreads a given produce rate thinner across more individual partitions, which can shrink the size of the batches a producer accumulates per partition, reducing producer batching efficiency and adding per-message overhead that a coarser partition count wouldn't have incurred.

### Choosing partition count from the workload's actual requirement, not a generously large guess

The right partition count starts from the workload's actual required parallelism: how many consumer instances the group genuinely needs running concurrently to hit its throughput or latency target, per lesson 1's ceiling. Some headroom above that number for expected growth is reasonable; padding it out far beyond what's needed "to be safe" isn't free, given the per-partition overhead that scales cluster-wide. And lesson 1 already established that increasing partition count later isn't a clean escape hatch either: it can silently break existing key-based ordering, since a key's hash target changes going forward while everything already written stays where it is. There's no version of this decision where guessing too high costs nothing and fixing it later costs nothing either; both directions have a real, different cost, which is exactly why the number has to be reasoned about upfront rather than deferred.

### A fully defended topic layout names a decision from every stage

Bringing the whole arc together, a defended topic and consumer-group layout states: what ordering guarantee the workload actually needs, and the key choice (lesson 6) that provides it without creating an avoidable hot key; what parallelism target the workload needs, and the partition count chosen to meet it with reasonable headroom, weighed against the per-partition overhead that scales with the whole cluster; and what delivery guarantee the workload needs, and the specific producer and consumer settings, acks, idempotence, and transactions if genuinely required, that provide it at the cost lessons 4 and 5 already measured. A layout that only states a partition count, with no accounting for ordering, key choice, or delivery guarantee, hasn't defended a design; it's picked a number.

## Practice

1. ▢ Besides capping consumer parallelism, name at least two direct costs that scale with the total partition count across a whole cluster, not just within one topic.

<details markdown="1"><summary>Check</summary>

Per-partition file and replication overhead on every broker holding a replica, and slower leader election or controller operations during a broker failure or restart, since more total partitions means more leadership reassignment work. Producer batching efficiency can also suffer, since the same produce rate spread across more partitions shrinks the batch each producer accumulates per partition.

</details>

2. ▢ Why does choosing an unnecessarily large partition count "to be safe" have a real cost, rather than being a free way to future-proof a topic?

<details markdown="1"><summary>Hint</summary>

Consider what the extra partitions cost the cluster even if the workload never actually needs that much parallelism.

</details>

<details markdown="1"><summary>Check</summary>

Every additional partition adds file and replication overhead on the brokers holding it and adds to the leadership reassignment work a broker failure or restart has to do, regardless of whether the workload ever actually uses that parallelism. Padding the count well beyond the workload's real requirement pays this ongoing cluster-wide cost for headroom that may never be needed.

</details>

3. ▢ Given that adding partitions later can break existing key-based ordering, how should a team actually decide a partition count upfront, rather than simply picking a large number to avoid ever revisiting it?

<details markdown="1"><summary>Check</summary>

Start from the workload's actual required consumer parallelism, add reasonable headroom for expected growth, and accept that both directions of getting this wrong have a real cost: too generous a count pays ongoing cluster-wide overhead for parallelism that may never be used, while increasing it later risks silently breaking existing key-based ordering. Reasoning about expected growth upfront, rather than treating either "pick something huge now" or "just add more later" as a free option, is what the decision actually requires.

</details>

4. ▢ List what a fully defended topic layout needs to state, pulling one decision from each of stages 1 through 3.

<details markdown="1"><summary>Check</summary>

The ordering guarantee the workload needs and the key choice that provides it without creating an avoidable hot key (stage 1, refined in this stage). The parallelism target the workload needs and the partition count chosen to meet it with reasonable headroom against per-partition overhead (this lesson). The delivery guarantee the workload needs and the specific producer/consumer settings, acks, idempotence, and transactions if genuinely required, that provide it (stage 3).

</details>

5. ▢ Which claim is true of choosing a topic's partition count?

    - a) Partition count only affects consumer parallelism, with no cost independent of how many consumers actually exist
    - b) Partition count should be chosen from the workload's actual required parallelism plus reasonable headroom, since both an unnecessarily large count and a later increase carry real, different costs
    - c) Increasing partition count later is always safe and never affects existing ordering guarantees
    - d) A defended topic layout only needs to state its partition count; ordering and delivery guarantees are separate concerns

<details markdown="1"><summary>Check</summary>

**b)** That's exactly the trade-off this lesson holds the decision to. (a) is false: extra partitions cost real cluster-wide file, replication, and controller overhead regardless of consumer count. (c) is false: lesson 1 already established that increasing partition count later can silently break existing key-based ordering. (d) is false: a defended layout names ordering, parallelism, and delivery guarantee decisions together, not partition count alone.

</details>

## Real-world reps

- [ ] For a topic you operate or are designing, write down its required consumer parallelism, its chosen partition count, and how much headroom that represents.
- [ ] Check a cluster you have access to for its total partition count across all topics, and whether that number is close to any documented per-broker limits for file handles or replication.
- [ ] Tomorrow: write a full defended layout for one real topic, naming its key choice, partition count, and delivery guarantee together, as this lesson's synthesis describes.

## Going further

- [Docs: "Design", Apache Kafka](https://kafka.apache.org/documentation/#design)
- [Docs, Apache Kafka](https://kafka.apache.org/documentation/)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
