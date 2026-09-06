---
title: Glossary
description: "Canonical terms for Kafka"
type: glossary
---

# Kafka Glossary

Canonical terms for owning a Kafka log: how it's partitioned, and what ordering and parallelism guarantee follows from that.

## Terms

**Partition**:
One independent, append-only, ordered log that a topic is split into. A message lands in exactly one partition, chosen by its key's hash or, absent a key, spread across partitions with no ordering relationship.
_Avoid_: shard (use only when quoting a source that uses it)

**Topic**:
A named collection of one or more partitions. Ordering is guaranteed only within a partition, never across a topic's partitions as a whole.
_Avoid_: queue, channel
