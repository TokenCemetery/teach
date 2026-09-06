---
title: Resources
description: "Trusted sources for Kafka"
type: resources
---

# Kafka Resources

## Knowledge

- [Docs: "Design", Apache Kafka](https://kafka.apache.org/documentation/#design)
  Official chapter on the log itself: partitions, replication, how persistence and batching make the log fast, and log compaction. Use for: the primary mechanics a topic and partition layout decision rests on.
- [Docs: "Message Delivery Semantics", Apache Kafka](https://kafka.apache.org/documentation/#semantics)
  Official explanation of at-most-once, at-least-once and exactly-once delivery, and precisely where in the produce/consume path each guarantee is won or lost. Use for: the delivery-guarantee vocabulary and its precise definitions.
- [Article: "Exactly-once Semantics is Possible: Here's How Kafka Does it", Gustafson and Mehta, Confluent](https://www.confluent.io/blog/exactly-once-semantics-are-possible-heres-how-apache-kafka-does-it/)
  Written by the engineers who built it: the idempotent producer and transactions mechanisms that make exactly-once possible, and what each costs in throughput and complexity. Use for: defending or challenging an "exactly once" claim with the actual mechanism behind it.
- [Article: "Incremental Cooperative Rebalancing in Apache Kafka", Confluent](https://www.confluent.io/blog/incremental-cooperative-rebalancing-in-kafka/)
  Explains why the original stop-the-world rebalance protocol causes a rebalancing storm under churn, and how cooperative rebalancing narrows the disruption to only the partitions that actually move. Use for: diagnosing a consumer group stuck repeatedly rebalancing.
- [Docs: "Kafka Connect", Apache Kafka](https://kafka.apache.org/documentation/#connect)
  Official chapter on the connector framework for moving data in and out of Kafka without hand-writing a producer or consumer for every integration. Use for: the surrounding-ecosystem piece this mission touches briefly.
- [Docs: "Schema Registry", Confluent](https://docs.confluent.io/platform/current/schema-registry/index.html)
  Official docs for managing and evolving message schemas across producers and consumers without breaking compatibility. Use for: the other surrounding-ecosystem piece, schema management, this mission touches briefly.

## Gaps

- No source yet on diagnosing consumer lag specifically from a real cluster's metrics (`records-lag-max`, consumer group describe output) in an active incident, as opposed to the reference documentation on how consumer groups work; worth closing once lesson design reaches on-call diagnosis.
