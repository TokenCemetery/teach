---
title: Kafka
description: "Own the log: partitions, consumer groups, delivery guarantees, and what \"exactly once\" actually costs"
type: topic
---

# Learning: Kafka

Be able to design a topic and partition layout for a real workload and to diagnose consumer lag, rebalancing storms or unexpected message loss instead of guessing at a fix.

**Latest lesson:** _none yet_

## Success looks like

- Design a topic, partition and consumer-group layout for a stated workload and defend the delivery-guarantee choice behind it.
- Given a consumer lagging or rebalancing repeatedly, diagnose which setting or usage pattern is at fault.
- State what "exactly once" actually costs and when at-least-once with idempotent handling is the better trade.

## Constraints

- Apache Kafka is the reference implementation; alternatives (Redpanda, managed services) are not covered.
- Touches the surrounding ecosystem (Schema Registry, Kafka Connect basics) briefly, where the log's guarantees alone do not explain how a real pipeline is built.

## Out of scope

- The failure model behind the delivery guarantees themselves: that is `architecture/distributed-systems`, linked to rather than re-derived here.
- ksqlDB and Kafka Streams as topics in their own right.

## The arc

{N} stages, {start} to {end}. Not a lesson list: a stage takes several lessons, and the boundaries are soft.

| Stage | Covers | Done when |
|---|---|---|
| 1. {Name} | {What it covers} | {The capability that closes the stage} |

## Lessons

Work through these in order.

| # | Lesson | Teaches |
|---|---|---|
| _none yet_ | | |

## Reference

- [Glossary](GLOSSARY.md): canonical terms for this topic
- [Resources](RESOURCES.md): trusted sources

## How this works

Each lesson is short and self-contained. Answer keys are collapsed: recall first, then open them. The real-world reps matter more than the reading, and spacing them out is the point. Anything still unclear at the end of a lesson is worth chasing to its primary source before moving on.
