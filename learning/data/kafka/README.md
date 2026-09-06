---
title: Kafka
description: "Own the log: partitions, consumer groups, delivery guarantees, and what \"exactly once\" actually costs"
type: topic
---

# Learning: Kafka

Be able to design a topic and partition layout for a real workload and to diagnose consumer lag, rebalancing storms or unexpected message loss instead of guessing at a fix.

**Latest lesson:** [1. Partitions and the Log](lessons/0001-partitions-and-the-log.md)

## Success looks like

- Design a topic, partition and consumer-group layout for a stated workload and defend the delivery-guarantee choice behind it.
- Given a consumer lagging or rebalancing repeatedly, diagnose which setting or usage pattern is at fault.
- State what "exactly once" actually costs and when at-least-once with idempotent handling is the better trade.

## Constraints

- Assumes no prior Kafka or messaging-system experience.
- Apache Kafka is the reference implementation; alternatives (Redpanda, managed services) are not covered.
- Touches the surrounding ecosystem (Schema Registry, Kafka Connect basics) briefly, where the log's guarantees alone do not explain how a real pipeline is built.

## Out of scope

- The failure model behind the delivery guarantees themselves: that is `architecture/distributed-systems`, linked to rather than re-derived here.
- ksqlDB and Kafka Streams as topics in their own right.

## The arc

Five stages, the log to a designed layout. A stage takes several lessons and the boundaries are soft; what makes a stage done is the capability, not the lesson count.

| Stage | Lessons | Covers | Done when |
|---|---|---|---|
| 1. Partitions and the log | 0001 | The unit everything else (ordering, parallelism, consumer groups) is built around | Can explain why a partition is the unit of ordering and parallelism |
| 2. Consumer groups and rebalancing | 0002 to 0003 | Group coordination, cooperative rebalancing, consumer lag | Can diagnose a lagging or repeatedly rebalancing consumer |
| 3. Delivery guarantees | 0004 to 0005 | At-most/at-least/exactly-once semantics, idempotent producers, transactions | Can defend a delivery-guarantee choice and state what exactly-once costs |
| 4. Designing the layout | 0006 to 0007 | Key choice, partition-count trade-offs, ordering guarantees | Can design a topic and partition layout for a stated workload |
| 5. The surrounding ecosystem | 0008 to 0009 | Schema Registry, Kafka Connect basics | Can explain how these fit around the log in a real pipeline |

## Lessons

Work through these in order.

| # | Lesson | Teaches |
|---|---|---|
| [0001](lessons/0001-partitions-and-the-log.md) | Partitions and the Log | The unit everything else in this workspace (ordering, parallelism, consumer groups) is built around |

## Reference

- [Glossary](GLOSSARY.md): canonical terms for this topic
- [Resources](RESOURCES.md): trusted sources

## How this works

Each lesson is short and self-contained. Answer keys are collapsed: recall first, then open them. The real-world reps matter more than the reading, and spacing them out is the point. Anything still unclear at the end of a lesson is worth chasing to its primary source before moving on.
