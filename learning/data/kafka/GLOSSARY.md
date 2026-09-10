---
title: Glossary
description: "Canonical terms for Kafka"
type: glossary
---

# Kafka Glossary

Canonical terms for owning a Kafka log: how it's partitioned, and what ordering and parallelism guarantee follows from that.

## Terms

**ACL (Access Control List)**:
A grant of a specific operation (Read, Write, Create, Describe, Alter, and others) on a specific resource (Topic, Group, or Cluster) to a specific principal. Once an authorizer is enabled, an operation with no matching ACL is denied, not silently allowed.
_Avoid_: permission (vague; "ACL" is the specific, checkable grant this workspace means)

**Controller quorum**:
The set of KRaft nodes (`process.roles=controller`) that replicate the cluster's metadata log via Raft; only quorum members are eligible to become the active controller, and only the active controller processes metadata writes.
_Avoid_: ZooKeeper ensemble (a different, removed external system; "controller quorum" is KRaft's own internal quorum)

**In-sync replica set (ISR)**:
The subset of a partition's replicas, leader included, caught up closely enough (per `replica.lag.time.max.ms`) to be eligible for leader election without losing data. `acks=all` waits for the current ISR, not the topic's full configured replication factor.
_Avoid_: healthy replicas (vague; "ISR" is the specific, checkable set this workspace means)

**KRaft**:
Kafka's own Raft-based metadata consensus, replacing ZooKeeper. A controller quorum replicates a metadata log that every controller continuously replays, so failover promotes an already-caught-up standby instead of re-fetching a full state from an external store.
_Avoid_: ZooKeeper (the external system KRaft replaced; current Kafka no longer supports it)

**Log compaction**:
A cleanup policy retaining only the latest value per key, via a periodic log cleaner, rather than deleting by age. A key is fully removed only after a tombstone (a `null`-valued write for that key) has itself aged past `delete.retention.ms`.
_Avoid_: garbage collection (a different mechanism in other systems; say "log compaction" for this specific Kafka policy)

**Partition**:
One independent, append-only, ordered log that a topic is split into. A message lands in exactly one partition, chosen by its key's hash or, absent a key, spread across partitions with no ordering relationship.
_Avoid_: shard (use only when quoting a source that uses it)

**Principal**:
The identity a client establishes by authenticating (via mutual TLS or a SASL mechanism), and the subject an ACL actually grants an operation to. Authentication establishes a principal; authorization decides what that principal may do.
_Avoid_: user (this workspace's ACLs and quotas are keyed on the principal, which can also be a service identity, not only a human user)

**Quota**:
A per-client or per-principal limit on produce/consume byte rate or on request-handling percentage, enforced independently of ACLs. A fully authorized client can still be throttled by a quota; the two mechanisms protect against different failure modes.
_Avoid_: rate limit (use only when quoting a source that uses it; "quota" is this workspace's term)

**Topic**:
A named collection of one or more partitions. Ordering is guaranteed only within a partition, never across a topic's partitions as a whole.
_Avoid_: queue, channel
