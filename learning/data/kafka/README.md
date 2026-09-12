---
title: Kafka
description: "Own the log: partitions, consumer groups, delivery guarantees, and what \"exactly once\" actually costs"
type: topic
---

# Learning: Kafka

Be able to design a topic and partition layout for a real workload and to diagnose consumer lag, rebalancing storms or unexpected message loss instead of guessing at a fix.

**Latest lesson:** [16. The Metrics That Matter for Operating a Cluster](lessons/0016-the-metrics-that-matter-for-operating-a-cluster.md)

## Success looks like

- Design a topic, partition and consumer-group layout for a stated workload and defend the delivery-guarantee choice behind it.
- Given a consumer lagging or rebalancing repeatedly, diagnose which setting or usage pattern is at fault.
- State what "exactly once" actually costs and when at-least-once with idempotent handling is the better trade.

## Constraints

- Assumes no prior Kafka or messaging-system experience.
- Apache Kafka is the reference implementation; alternatives (Redpanda, managed services) are not covered.
- Touches the surrounding ecosystem (Schema Registry, Kafka Connect basics) briefly, where the log's guarantees alone do not explain how a real pipeline is built.

## Out of scope

- The failure model behind the delivery guarantees themselves: see [`architecture/distributed-systems`](../../architecture/distributed-systems/), linked to rather than re-derived here.
- ksqlDB and Kafka Streams as topics in their own right.

## The arc

Ten stages, the log to operating the cluster in production. A stage takes several lessons and the boundaries are soft; what makes a stage done is the capability, not the lesson count.

| Stage | Lessons | Covers | Done when |
|---|---|---|---|
| 1. Partitions and the log | 0001 | The unit everything else (ordering, parallelism, consumer groups) is built around | Can explain why a partition is the unit of ordering and parallelism |
| 2. Consumer groups and rebalancing | 0002 to 0003 | Group coordination, cooperative rebalancing, consumer lag | Can diagnose a lagging or repeatedly rebalancing consumer |
| 3. Delivery guarantees | 0004 to 0005 | At-most/at-least/exactly-once semantics, idempotent producers, transactions | Can defend a delivery-guarantee choice and state what exactly-once costs |
| 4. Designing the layout | 0006 to 0007 | Key choice, partition-count trade-offs, ordering guarantees | Can design a topic and partition layout for a stated workload |
| 5. The surrounding ecosystem | 0008 to 0009 | Schema Registry, Kafka Connect basics | Can explain how these fit around the log in a real pipeline |
| 6. Retention and replication | 0010 to 0011 | `cleanup.policy`, log compaction, replication factor, ISR, `acks`, `min.insync.replicas`, unclean leader election | Can defend how long a topic's data lives and what durability its replication settings actually guarantee |
| 7. Client configuration under load | 0012 | `batch.size`, `linger.ms`, `fetch.min.bytes`, `max.poll.interval.ms` | Can match a throughput, latency or spurious-rebalance symptom to the specific client setting that addresses it |
| 8. Cluster coordination | 0013 | KRaft, the controller quorum, `process.roles`, what replaced ZooKeeper | Can explain what the controller quorum does and why KRaft failover needs no full metadata re-fetch |
| 9. Security and multi-tenancy | 0014 to 0015 | TLS, SASL, `security.protocol`, ACLs, deny-by-default, quotas | Can name which mechanism (encryption, authentication, authorization, or resource isolation) a given security question actually concerns |
| 10. Operating the cluster | 0016 | `UnderReplicatedPartitions`, `UnderMinIsr`, disk headroom, request latency, request-handler saturation | Can name which of the three signal families a given operational symptom belongs to, and triage isolated-broker versus cluster-wide |

## Lessons

Work through these in order.

| # | Lesson | Teaches |
|---|---|---|
| [0001](lessons/0001-partitions-and-the-log.md) | Partitions and the Log | The unit everything else in this workspace (ordering, parallelism, consumer groups) is built around |
| [0002](lessons/0002-consumer-group-coordination.md) | Consumer Group Coordination | How a group coordinator and a group leader divide partitions among consumers, and how offsets track each group's progress |
| [0003](lessons/0003-cooperative-rebalancing-and-lag.md) | Cooperative Rebalancing and Diagnosing Consumer Lag | Why the original rebalance protocol causes a rebalancing storm, how cooperative rebalancing narrows it, and a diagnostic order for consumer lag |
| [0004](lessons/0004-delivery-semantics.md) | At-Most-Once, At-Least-Once, and Exactly-Once | Where each delivery guarantee is actually won or lost across the produce, broker, and consume legs of the path |
| [0005](lessons/0005-idempotent-producers-and-transactions.md) | Idempotent Producers and Transactions | Why idempotence is nearly free but transactions carry the real cost of exactly-once |
| [0006](lessons/0006-partition-key-choice.md) | Partition Key Choice and Ordering Guarantees | Choosing a partition key means choosing both what ordering you get and what parallelism you give up, in the same decision |
| [0007](lessons/0007-partition-count-and-topic-layout.md) | Partition-Count Trade-offs and Designing a Topic Layout | Why more partitions isn't free, and what a fully defended topic layout has to name from every earlier stage |
| [0008](lessons/0008-schema-registry.md) | Schema Registry | How catching an incompatible schema change at produce time replaces a silent, downstream consume-time break |
| [0009](lessons/0009-kafka-connect-basics.md) | Kafka Connect Basics | How Connect's tasks and worker modes provide parallelism and fault tolerance, and why Connect grants no guarantee the underlying producer or consumer API didn't already provide |
| [0010](lessons/0010-retention-and-log-compaction.md) | Retention and Log Compaction | How long a message actually survives in a topic, and the other cleanup policy that keeps a key's history instead of its age |
| [0011](lessons/0011-replication-isr-acks-and-unclean-leader-election.md) | Replication, ISR, acks, and Unclean Leader Election | What acks=all actually waits for, the floor that stops it from silently meaning less than it sounds like, and the trade-off when every in-sync replica is gone |
| [0012](lessons/0012-producer-and-consumer-configuration-under-load.md) | Producer and Consumer Configuration Under Load | The client-side knobs that trade latency for throughput, and the one that can trigger a rebalance for a consumer that was never actually dead |
| [0013](lessons/0013-kraft-and-what-replaced-zookeeper.md) | KRaft, and What Replaced ZooKeeper | How the cluster agrees on its own metadata now that the external coordination service is gone, and why a full-state re-fetch on failover was the problem worth solving |
| [0014](lessons/0014-tls-and-sasl-authenticating-to-a-cluster.md) | TLS and SASL: Authenticating to a Cluster | Encrypting the channel and authenticating the client are two separate jobs that security.protocol combines in one setting, and conflating them is where most confusion starts |
| [0015](lessons/0015-acls-and-quotas-authorization-and-multi-tenancy.md) | ACLs and Quotas: Authorization and Multi-Tenancy | An authenticated principal still isn't authorized to do anything until an ACL says so, and a principal allowed to act still isn't protected from starving every other tenant of the cluster's capacity |
| [0016](lessons/0016-the-metrics-that-matter-for-operating-a-cluster.md) | The Metrics That Matter for Operating a Cluster | Under-replicated partitions, disk headroom, and request latency are the three signals worth watching, and each one points to a different kind of trouble |

## Reference

- [Glossary](GLOSSARY.md): canonical terms for this topic
- [Resources](RESOURCES.md): trusted sources
- [Consumer Groups and Rebalancing](reference/consumer-groups-and-rebalancing.md): the two rebalance protocols, the two independent liveness timeouts, and a diagnostic order for consumer lag with the config that governs each step
- [Delivery Guarantees](reference/delivery-guarantees.md): which config decides each leg of the path, why idempotence can be silently off, and what a read_committed consumer actually waits for
- [Topic and Partition Design](reference/topic-and-partition-design.md): how a record actually reaches a partition, what ordering that does and does not buy, and the two directions partition count is expensive to change
- [Ecosystem](reference/ecosystem.md): the seven compatibility types with who has to upgrade first under each, and what Kafka Connect adds around the log, including the guarantee that is off by default

## How this works

Each lesson is short and self-contained. Answer keys are collapsed: recall first, then open them. The real-world reps matter more than the reading, and spacing them out is the point. Anything still unclear at the end of a lesson is worth chasing to its primary source before moving on.
