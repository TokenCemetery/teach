---
title: Clustering
description: "What Cluster's slots take away, the settings that decide whether a degraded cluster serves or stops, and why Sentinel's quorum does not control failover"
type: reference
---

# Clustering: Redis Cluster and Sentinel

Stage 5 compressed for lookup. [Lesson 8](../lessons/0008-cluster-and-sentinel.md) covers the compromises each introduces; this sheet is the numbers, the settings and the two distinctions people get wrong.

## Which problem each solves

| | Redis Cluster | Sentinel |
|---|---|---|
| Solves | Capacity beyond one instance, plus availability | Availability for a single primary and its replicas |
| Shards | Yes, 16,384 hash slots | No |
| Failover | Built in | Its whole job |
| Multi-key operations | Constrained to one slot | Unconstrained |
| Use both together | No. Cluster has its own promotion | Not applicable |

Needing availability but not capacity is Sentinel. Needing both is Cluster. Needing capacity but not availability is still probably Cluster, with the availability arriving whether you asked for it or not.

## Cluster: slots and what they cost

Every key hashes to one of **16,384** slots, and each slot has exactly one owning primary. A client may talk to any node and gets redirected to the owner.

Multi-key commands, transactions and Lua scripts work **only if every key involved is in the same slot**. There is no cross-node transaction. **Hash tags** are the escape hatch: if a key contains a substring in `{}`, only that substring is hashed, so `user:{123}:profile` and `user:{123}:account` are guaranteed to share a slot and can be operated on together.

Resharding, adding and removing nodes, and changing the slot distribution require no downtime. Getting the key design wrong does not fail at deploy time; it fails the first time an operation needs two keys that landed apart.

## Cluster: the minimums

| | Value |
|---|---|
| Minimum masters for a working cluster | **3** |
| Strongly recommended deployment | **6** nodes, three masters and three replicas |

## Cluster: what happens when it degrades

Three settings decide whether a damaged cluster serves or stops, and their defaults are conservative.

| Setting | Default | Effect |
|---|---|---|
| `cluster-node-timeout` | | How long a node may be unreachable before it is failed over. **Also**: any node that cannot reach a majority of masters for this long **stops accepting queries** |
| `cluster-require-full-coverage` | **yes** | The cluster stops accepting writes when part of the keyspace is uncovered. Set to `no` to keep serving the covered subset |
| `cluster-allow-reads-when-down` | **no** | A node stops serving **all** traffic once the cluster is marked failed, rather than serve possibly stale data |

The `cluster-node-timeout` row is the one that surprises people. It is not only a failure-detection threshold; it is also the rule that makes a node on the wrong side of a partition take itself out of service.

## Cluster: consistency, stated plainly

**Redis Cluster does not guarantee strong consistency.** It can lose writes it already acknowledged to the client. Two documented paths:

1. **Asynchronous replication.** The master replies OK before propagating. If it crashes first, a replica that never saw the write can be promoted and the write is gone. The documentation compares this to a database configured to flush to disk once a second, which is a failure mode most people already know how to reason about.
2. **A minority partition.** A client isolated with a minority master keeps writing, and those writes are lost once the majority side promotes a replica. The window is **bounded by `cluster-node-timeout`**, because after that the minority master stops accepting writes.

`WAIT` makes loss much less likely by waiting for replica acknowledgements. It does **not** make Cluster strongly consistent: under more complex failures a replica that never received the write can still be elected.

So the trade the arc asks a team to accept is capacity and automatic failover, in exchange for a bounded window in which an acknowledged write can vanish.

## Sentinel: the quorum does not do what its name suggests

`sentinel monitor <name> <ip> <port> <quorum>`.

| Step | Who decides |
|---|---|
| Marking the master as failing | The **quorum**: that many Sentinels must agree it is unreachable |
| Actually performing the failover | A Sentinel elected leader and authorised by **a majority of all Sentinel processes** |

**The quorum only controls detection.** With five Sentinels and a quorum of two, two agreeing starts an attempt, and the failover proceeds only if at least three are reachable. The consequence is the useful one: **no failover happens in a minority partition**, whatever the quorum is set to.

Other things to know before deploying:

- **At least three Sentinel instances**, on machines or availability zones that fail independently.
- Sentinels listen on TCP **26379**. If that port is not open between them they cannot agree, and failover never happens at all.
- **Clients need Sentinel support.** Many popular libraries have it; not all.
- Sentinel does not retain acknowledged writes through a failure either, because replication is asynchronous. It shortens the outage, not the loss window.

## Choosing

| Need | Answer |
|---|---|
| One instance is enough, and downtime is acceptable | Neither |
| One instance is enough, downtime is not | Sentinel, three instances, independently placed |
| More capacity than one instance holds | Cluster, at least three masters, six nodes recommended |
| Acknowledged writes must never be lost | Not this. Reconsider the storage choice |

## Before running either

- Key design has been checked against slots: every multi-key operation's keys share a hash tag, or the operation has been rewritten.
- The cluster has at least three masters, and replicas if failover is expected to work.
- Somebody has decided whether a partially covered cluster should serve reads or stop, rather than inheriting `cluster-require-full-coverage` and `cluster-allow-reads-when-down` by accident.
- `cluster-node-timeout` is understood as both the failover threshold and the self-eviction rule for a node that loses the majority.
- The acknowledged-write loss window is written down and accepted, and `WAIT` is not mistaken for a fix.
- For Sentinel: three instances, port 26379 reachable between them, a client library that speaks Sentinel, and nobody assuming the quorum setting controls failover.

## Sources

- [Docs: "Scaling with Redis Cluster", Redis](https://redis.io/docs/latest/operate/oss_and_stack/management/scaling/)
- [Docs: "High availability with Redis Sentinel", Redis](https://redis.io/docs/latest/operate/oss_and_stack/management/sentinel/)
- [Persistence](persistence.md)
- [Resources](../RESOURCES.md)
