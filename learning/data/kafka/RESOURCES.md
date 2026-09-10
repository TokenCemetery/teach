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
- [Docs: "Producer Configs", Apache Kafka](https://kafka.apache.org/documentation/#producerconfigs)
  The generated producer reference. Use for: the exact conditions `enable.idempotence` requires, and the rule that decides whether a conflicting setting disables idempotence silently or throws at startup; also the transaction settings, including that `transaction.timeout.ms` is measured from the first partition added rather than from the call that opened the transaction.
- [Docs: "Topic Configs", Apache Kafka](https://kafka.apache.org/documentation/#topicconfigs)
  The per-topic reference. Use for: `min.insync.replicas`, and the rule that decides visibility rather than acknowledgement: regardless of `acks`, a message is not visible to consumers until it is replicated to all in-sync replicas and the minimum is met.
- [Docs: "Consumer Configs", Apache Kafka](https://kafka.apache.org/documentation/#consumerconfigs)
  The generated reference for every consumer configuration, with each option's type, default and the conditions under which it applies at all. Use for: settling what a timeout actually measures and what its current default is, and for spotting which options are silently unsupported once `group.protocol` is set to `consumer`. Defaults move between releases, so read it for the version you run.
- [Docs: "Broker Configs", Apache Kafka](https://kafka.apache.org/documentation/#brokerconfigs)
  The same for the broker, including the `group.consumer.*` family that takes over heartbeat cadence, session timeout and assignor choice under the new consumer group protocol. Use for: the server side of any coordination question, and for deprecations such as `group.coordinator.rebalance.protocols`, which is removed in Kafka 5.0.
- [Article: "Incremental Cooperative Rebalancing in Apache Kafka", Confluent](https://www.confluent.io/blog/incremental-cooperative-rebalancing-in-kafka/)
  Explains why the original stop-the-world rebalance protocol causes a rebalancing storm under churn, and how cooperative rebalancing narrows the disruption to only the partitions that actually move. Use for: diagnosing a consumer group stuck repeatedly rebalancing.
- [Docs: "Schema Evolution and Compatibility", Confluent](https://docs.confluent.io/platform/current/schema-registry/fundamentals/schema-evolution.html)
  The compatibility types in full, with per-format tables of which changes each one allows, and the section that matters operationally: which clients have to be upgraded first under each type. Use for: choosing a compatibility mode from the upgrade order you can actually execute, and for the distinction between `BACKWARD` and `BACKWARD_TRANSITIVE`, which decides whether replay from the start of a topic is covered.
- [Docs: "Kafka Connect", Apache Kafka](https://kafka.apache.org/documentation/#connect)
  Official chapter on the connector framework for moving data in and out of Kafka without hand-writing a producer or consumer for every integration. Use for: the surrounding-ecosystem piece this mission touches briefly.
- [Docs: "Connect Configs", Apache Kafka](https://kafka.apache.org/documentation/#connectconfigs)
  The worker configuration reference. Use for: the three internal topics distributed mode needs, the converters that are configured independently of any connector, and `exactly.once.source.support`, which is `disabled` by default and takes a two-step rollout to enable on a running cluster.
- [Docs: "Schema Registry", Confluent](https://docs.confluent.io/platform/current/schema-registry/index.html)
  Official docs for managing and evolving message schemas across producers and consumers without breaking compatibility. Use for: the other surrounding-ecosystem piece, schema management, this mission touches briefly.
- [Docs: "KRaft", Apache Kafka](https://kafka.apache.org/documentation/#kraft)
  Official chapter on Kafka's own Raft-based metadata quorum: `process.roles`, combined versus dedicated controller nodes, and the operational commands for describing and reshaping a running quorum. Use for: how the controller quorum actually works, and why its failover needs no full metadata re-fetch.
- [Docs: "Security", Apache Kafka](https://kafka.apache.org/documentation/#security)
  Official chapter on `security.protocol`, the SASL mechanisms (PLAIN, SCRAM, GSSAPI, OAUTHBEARER), authorization and ACLs, and quotas. Use for: the precise default behavior on authorization, including that with no authorizer configured every authenticated principal has full access, and that deny-by-default applies only once an authorizer is actually in place.

## Gaps

- No source yet on diagnosing consumer lag specifically from a real cluster's metrics (`records-lag-max`, consumer group describe output) in an active incident, as opposed to the reference documentation on how consumer groups work; worth closing once lesson design reaches on-call diagnosis.
