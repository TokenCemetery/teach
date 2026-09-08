---
title: Topic and Partition Design
description: "How a record actually reaches a partition, what ordering that does and does not buy, and the two directions partition count is expensive to change"
type: reference
---

# Topic and Partition Design

Stage 4 compressed for lookup. [Lesson 6](../lessons/0006-partition-key-choice.md) covers key choice as one decision about ordering and parallelism, and [lesson 7](../lessons/0007-partition-count-and-topic-layout.md) covers partition count and a defended layout; this sheet is the mechanics underneath, and the checklist to hold a design against.

Values are from the Kafka 4.3 configuration reference.

## How a record reaches a partition

With `partitioner.class` unset, the default logic applies. It has three cases, and only one of them is the one people picture.

| The record has | Partition chosen |
|---|---|
| An explicit partition | That one |
| A key | By a **hash of the key**, so the same key always lands in the same partition for a given partition count |
| Neither | The **sticky** partition, which changes once at least `batch.size` bytes have gone to it |

### The keyless case is not round-robin

Two defaults shape it, and neither is obvious:

- **Sticky, not per record.** The producer keeps sending to one partition until a batch fills, which is what keeps batches large. A record-by-record spread would shrink every batch.
- **Adaptive, not uniform.** `partitioner.adaptive.partitioning.enable` defaults to `true`, so the producer deliberately sends **more** to partitions on faster brokers. Set it to `false` for uniform distribution.

There is also `partitioner.availability.timeout.ms`, which treats a partition as unavailable when its broker has not processed produce requests for that long. It defaults to `0`, meaning **disabled**, and it does nothing unless adaptive partitioning is on.

Neither setting has any effect if a custom partitioner is in use.

### Two switches worth knowing

| Config | Default | Effect |
|---|---|---|
| `partitioner.ignore.keys` | `false` | When `true`, keys are present but ignored for partitioning. The way to keep a key for its own sake without buying its ordering constraint |
| `partitioner.class` | unset | `RoundRobinPartitioner` sends consecutive records to different partitions, key or not. Note the documented issue, `KAFKA-9965`, causing uneven distribution when a new batch is created |

## What ordering you actually get

| Scope | Ordered? |
|---|---|
| Within one partition | **Yes** |
| Within one key, at a fixed partition count | Yes, because the key always hashes to one partition |
| Within one key, across a partition-count change | **No.** New records hash differently while old ones stay put |
| Across keys in the same topic | No |
| Across topics | No |
| Within one key, when `partitioner.ignore.keys` is on | No |

Ordering is a property of a partition. Everything else is a consequence of how records were routed into partitions.

## Key choice

The key decides both what is ordered and how work divides, because both follow from the same fact: one key means one partition, and one partition means one consumer at a time.

| Key | Ordering bought | Parallelism given up |
|---|---|---|
| `customer_id` | Everything for one customer, in order | A busy customer is one partition, so a hot key no partition count can fix |
| `order_id` | Only within one order | Nothing to a hot customer, since their orders spread |
| None | Nothing beyond a partition | Nothing, and batching stays efficient thanks to stickiness |

A hot key is not discovered, it is chosen. The distribution of the field you key on **is** the load balance.

## Partition count

The ceiling first: a partition goes to at most one consumer in a group, so partition count caps useful consumer instances. Past that, extra consumers idle.

### Costs that scale with the whole cluster

| Cost | Why |
|---|---|
| Broker memory and file handles | Every partition is its own files |
| Replication traffic | Per partition, per replica |
| Controller work during failure or restart | More leadership to reassign |
| Producer batching | The same produce rate spread thinner means smaller batches per partition, and `batch.size` is reached less often |

That last one interacts with the keyless default above: stickiness exists precisely to protect batch sizes, and a very high partition count works against it.

### Both directions are one-way doors

| Change | Consequence |
|---|---|
| **Increasing** partitions | Existing records stay where they are while new records with the same key hash elsewhere. Per-key ordering breaks silently at the moment of the change |
| **Decreasing** partitions | Not supported. The only route is a new topic and a migration |

Which is why the number is reasoned about at design time. There is no version of this where guessing high is free and correcting later is free.

`num.partitions` on the broker defaults to **1**. It applies to auto-created topics, internal Streams topics, and `AdminClient#createTopics` when the count is `-1`. A topic that quietly got one partition is a parallelism ceiling of one consumer.

## A defended layout

A layout is defended when it names a decision from every stage, not just a number.

- **Ordering requirement.** What actually has to be in order, and at what scope.
- **Key.** The field that provides exactly that scope, checked against its real distribution for hot keys.
- **Parallelism target.** How many consumer instances the throughput needs, from lesson 1's ceiling.
- **Partition count.** That target plus modest headroom, weighed against the cluster-wide costs above.
- **Delivery guarantee.** The `acks`, idempotence and transaction settings that provide it, at the cost measured in [Delivery Guarantees](delivery-guarantees.md).
- **Group behaviour.** The assignor, and whether restarts should rebalance, from [Consumer Groups and Rebalancing](consumer-groups-and-rebalancing.md).

Stating only a partition count is picking a number, not defending a design.

## Before creating the topic

- The ordering scope is written down, and it matches what the key provides.
- The key's real-world distribution has been looked at, not assumed uniform.
- Partition count comes from a parallelism target, not from caution.
- Somebody knows that increasing it later breaks per-key ordering, and that decreasing it is not possible.
- If the topic is keyless on purpose, that is recorded as a choice rather than left as an omission.
- The topic was created explicitly rather than auto-created, so it did not inherit `num.partitions` of 1.

## Sources

- [Docs: "Producer Configs", Apache Kafka](https://kafka.apache.org/documentation/#producerconfigs)
- [Docs: "Broker Configs", Apache Kafka](https://kafka.apache.org/documentation/#brokerconfigs)
- [Docs: "Design", Apache Kafka](https://kafka.apache.org/documentation/#design)
- [Consumer Groups and Rebalancing](consumer-groups-and-rebalancing.md)
- [Delivery Guarantees](delivery-guarantees.md)
- [Resources](../RESOURCES.md)
