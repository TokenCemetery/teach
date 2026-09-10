---
title: 13. KRaft, and What Replaced ZooKeeper
description: How the cluster agrees on its own metadata now that the external coordination service is gone, and why a full-state re-fetch on failover was the problem worth solving
type: lesson
---

# Lesson 13. KRaft, and What Replaced ZooKeeper

**Mission link:** Stage 8 opens the cluster's own coordination layer, the part every prior lesson quietly assumed worked: something has to decide which broker leads which partition, and track that decision durably enough to survive a failure. Older Kafka clusters answered this with an external system, ZooKeeper; current Kafka answers it with KRaft, a consensus protocol Kafka runs itself.
**Primary source:** [Docs: "KRaft", Apache Kafka](https://kafka.apache.org/documentation/#kraft)
**Prerequisites:** [Lesson 12](0012-producer-and-consumer-configuration-under-load.md), [Partition](../GLOSSARY.md)

## Warm-up

1. ▢ Why does `max.poll.interval.ms` catch a failure `session.timeout.ms` alone would miss?

<details markdown="1"><summary>Check</summary>

`session.timeout.ms` only checks that the consumer's background heartbeat thread is still alive; a consumer can keep heartbeating successfully while its main processing loop is stuck on a slow batch. `max.poll.interval.ms` bounds the time between actual `poll()` calls, catching exactly that stuck-but-still-heartbeating case.

</details>

2. ▢ A producer's `batch.size` is reached well before `linger.ms` elapses. Does the producer wait out the rest of `linger.ms` anyway?

<details markdown="1"><summary>Check</summary>

No. The batch sends the moment either condition is met, whichever comes first; a full batch is sent immediately rather than waiting for the remaining linger time to elapse.

</details>

## Know this

### What ZooKeeper used to hold for a Kafka cluster

Older Kafka clusters stored their cluster metadata, broker registration, topic and partition configuration, ACLs, and which broker was the **controller**, in **ZooKeeper**, a separate distributed coordination service Kafka depended on but did not implement itself. Controller election worked through an **ephemeral znode**: whichever broker successfully created it became the controller, and if that broker died, the znode disappeared and a new election ran. This worked, but it meant operating two distributed systems, each with its own quorum, its own security configuration, and its own failure modes, to run one Kafka cluster.

### The specific cost that motivated replacing it: a full state re-fetch on every failover

The expensive part wasn't ZooKeeper's normal operation; it was what happened on controller failover. A newly elected controller had to re-read the cluster's entire metadata state from ZooKeeper before it could do anything, then push that full state back out to every broker, rather than picking up from wherever the previous controller left off. At a small partition count this was fast enough not to matter; at the partition counts a large cluster actually accumulates, exactly what lesson 7 warned a topic layout not to grow carelessly, this full re-fetch-and-rebroadcast became slow enough to noticeably lengthen how long a cluster stayed partially unavailable during failover.

### KRaft: Kafka's own metadata quorum, replicated via Raft, with no full re-fetch

**KRaft** (Kafka Raft) removes the external dependency by having Kafka run its own metadata consensus, using the Raft protocol, among a small set of nodes called the **controller quorum**. Metadata changes are appended to a replicated **metadata log**, and every controller in the quorum, not just the active one, continuously replays that log as it arrives. One controller is active (the `QuorumController`, a single-threaded event loop that processes every metadata change atomically, topic creation, partition reassignment, leader election, broker heartbeats, in the order it received them); the rest are standby, already caught up because they've been replaying the same log the whole time. Failover, then, is nothing more than a standby that was already current becoming active, not a fresh read of the entire cluster's state from an external store.

![Two architecture diagrams side by side. On the left, ZooKeeper mode: an external ZooKeeper ensemble outside the Kafka cluster elects a controller via an ephemeral znode, and on failover the new controller re-reads the full cluster state from ZooKeeper before pushing that full state out to every broker. On the right, KRaft mode: a controller quorum inside the cluster replicates a metadata log via Raft, with one controller active and the others continuously replaying that log as standby, so a new active controller is already caught up and needs no full state re-fetch on failover.](images/zookeeper-vs-kraft.svg)

### `process.roles`: a node is a broker, a controller, or both

A KRaft node's **`process.roles`** setting decides its job: `broker` (serves produce and fetch requests), `controller` (participates in the metadata quorum), or `broker,controller` together, **combined mode**, common for a small cluster or local development where running dedicated controller nodes isn't worth the overhead. A larger production cluster typically runs a small, dedicated controller quorum (often 3 nodes, an odd number so a majority is always well-defined) separate from the brokers actually serving traffic, so metadata-quorum load never competes with data-plane load on the same process. ZooKeeper-specific configuration has been removed from current Kafka entirely: this isn't an optional mode alongside ZooKeeper anymore, it's the only way a current Kafka cluster manages its own metadata.

## Practice

1. ▢ A cluster running ZooKeeper mode loses its controller broker. What has to happen before the new controller can start processing metadata changes, and why did this get slower as the cluster's partition count grew?

<details markdown="1"><summary>Hint</summary>

Consider what the new controller has to obtain before it can act, and where that comes from.

</details>

<details markdown="1"><summary>Check</summary>

The new controller has to re-read the cluster's entire metadata state from ZooKeeper, then push that full state back out to every broker, before it can begin processing new changes. As partition count grows, that full state grows too, so both the re-read and the rebroadcast take longer, lengthening how long the cluster stays partially unavailable during failover.

</details>

2. ▢ In KRaft mode, why doesn't a newly active controller need to do that same full re-fetch?

<details markdown="1"><summary>Check</summary>

Every controller in the quorum, not just the active one, continuously replays the replicated metadata log as entries arrive, so a standby controller is already caught up on the cluster's current state. Failover is just that already-current standby becoming active, not a fresh read of the entire state from an external store.

</details>

3. ▢ A small team runs a single-node development cluster and sets `process.roles=broker,controller` on it. What does this combined mode actually mean, and why would a large production cluster typically avoid it?

<details markdown="1"><summary>Check</summary>

Combined mode means the same process both serves broker traffic and participates in the controller quorum, which is convenient for a small or development setup with no need for dedicated controller capacity. A large production cluster typically separates the two so that controller-quorum load (processing metadata changes) never competes for resources with data-plane load (serving produces and fetches) on the same process.

</details>

4. ▢ Why does the controller quorum typically use an odd number of nodes, such as 3 or 5?

<details markdown="1"><summary>Check</summary>

Raft-based consensus, which the controller quorum uses to replicate its metadata log, requires a majority of members to agree; an odd number avoids a tie when the quorum needs to determine that majority, the same reason odd-sized quorums are standard in consensus protocols generally.

</details>

5. ▢ Which claim correctly describes the difference between ZooKeeper mode and KRaft mode?

    - a) Both store cluster metadata in an external system; KRaft simply uses a faster external database than ZooKeeper
    - b) ZooKeeper mode requires a new controller to re-fetch and rebroadcast the cluster's full metadata state on failover; KRaft mode's standby controllers continuously replay a replicated metadata log, so failover needs no such re-fetch
    - c) KRaft is an optional mode that current Kafka still lets a cluster disable in favor of ZooKeeper
    - d) `process.roles=broker,controller` is invalid configuration and only single-role nodes are supported

<details markdown="1"><summary>Check</summary>

**b)** That's the precise mechanism, and the specific cost it removes. (a) is false: KRaft isn't an external system at all, it's a consensus protocol Kafka runs itself among controller-role nodes. (c) is false: ZooKeeper-specific configuration has been removed entirely from current Kafka; KRaft is the only supported mode. (d) is false: combined mode (`broker,controller` together) is valid and common for small or development clusters.

</details>

## Real-world reps

- [ ] For a Kafka cluster you have access to, check whether its controller nodes run in combined mode or as a dedicated controller quorum, and how many controller nodes the quorum has.
- [ ] If you've operated (or read a postmortem of) an older ZooKeeper-mode cluster, look for whether a controller failover was ever the visible cause of a longer-than-expected availability gap.
- [ ] Tomorrow: read the primary source's KRaft documentation in full, and note what `kafka-metadata-quorum.sh describe --status` actually reports about a running quorum's health.

## Going further

- [Docs: "KRaft", Apache Kafka](https://kafka.apache.org/documentation/#kraft)
- [Docs: "ZooKeeper to KRaft Migration", Apache Kafka](https://kafka.apache.org/documentation/#kraft_zk_migration)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
