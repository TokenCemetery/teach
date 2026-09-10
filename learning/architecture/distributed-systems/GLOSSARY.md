---
title: Glossary
description: "Canonical terms for distributed systems"
type: glossary
---

# Distributed Systems Glossary

Canonical terms for reasoning about partial failure, consistency, and consensus once the process boundary is crossed.

## Terms

**Consistent hashing**:
A hashing scheme that maps both nodes and keys onto positions on a shared ring, assigning each key to the nearest node clockwise, so that adding or removing a node remaps only the keys between it and its neighbor (on average `O(K/N)` of the dataset) rather than nearly everything, the way plain `hash(key) mod M` would.
_Avoid_: assuming a bare ring is sufficient in practice; without virtual nodes, a single node's failure dumps its whole load onto one neighbor instead of spreading it

**Partial failure**:
The failure mode unique to distributed systems: a request produces no response, and the caller cannot tell whether it was lost in transit, its reply was lost, or the other side is merely slow.
_Avoid_: network error (too specific; partial failure includes cases with no error at all, just silence)

**Partitioning**:
Splitting a dataset across multiple nodes so no single node holds all of it, the counterpart to replication (which copies the *same* data across nodes rather than dividing *different* data among them).
_Avoid_: sharding (used interchangeably in this workspace and elsewhere; no distinction is drawn between the two terms here)

**Quorum**:
The minimum number of replicas, out of N total, that a read or a write must collect acknowledgment from before it's considered successful. A read quorum of size R and a write quorum of size W are guaranteed to overlap on at least one replica when `R + W > N`.
_Avoid_: majority (imprecise; a quorum's size is a deliberate configuration choice, and only `W > N/2` specifically requires a strict majority, not R or W individually)

**Replication**:
Copying the same data across multiple nodes, either through leader-based replication (one node accepts all writes and propagates them) or leaderless replication (any replica can accept a write directly, with quorum overlap or reconciliation keeping replicas consistent enough).
_Avoid_: mirroring (a narrower, often storage-specific term; this workspace uses "replication" for the general mechanism regardless of implementation)

**Timeout**:
A caller's chosen limit on how long to wait for a response before treating the other side as failed. A guess made under permanent uncertainty, not a fact, since a network has no upper bound on message delay.
_Avoid_: deadline (use only when quoting a source or API that uses that specific term)
