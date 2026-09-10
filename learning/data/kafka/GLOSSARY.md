---
title: Glossary
description: "Canonical terms for Kafka"
type: glossary
---

# Kafka Glossary

Canonical terms for owning a Kafka log: how it's partitioned, and what ordering and parallelism guarantee follows from that.

## Terms

**In-sync replica set (ISR)**:
The subset of a partition's replicas, leader included, caught up closely enough (per `replica.lag.time.max.ms`) to be eligible for leader election without losing data. `acks=all` waits for the current ISR, not the topic's full configured replication factor.
_Avoid_: healthy replicas (vague; "ISR" is the specific, checkable set this workspace means)

**Log compaction**:
A cleanup policy retaining only the latest value per key, via a periodic log cleaner, rather than deleting by age. A key is fully removed only after a tombstone (a `null`-valued write for that key) has itself aged past `delete.retention.ms`.
_Avoid_: garbage collection (a different mechanism in other systems; say "log compaction" for this specific Kafka policy)

**Partition**:
One independent, append-only, ordered log that a topic is split into. A message lands in exactly one partition, chosen by its key's hash or, absent a key, spread across partitions with no ordering relationship.
_Avoid_: shard (use only when quoting a source that uses it)

**Topic**:
A named collection of one or more partitions. Ordering is guaranteed only within a partition, never across a topic's partitions as a whole.
_Avoid_: queue, channel
