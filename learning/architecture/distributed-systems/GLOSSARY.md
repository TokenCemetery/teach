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

**CRDT (conflict-free replicated data type)**:
A data type designed so that concurrent updates always merge to the same result regardless of delivery order, avoiding the need for a separate conflict-resolution step. State-based (CvRDT) sends whole states and requires a commutative, associative, idempotent merge; operation-based (CmRDT) broadcasts operations and requires commutative, associative operations plus exactly-once delivery in place of idempotence.
_Avoid_: assuming any commutative merge is automatically a CRDT; the merge (or operation set) must also be associative and, for the state-based form, idempotent, or convergence isn't guaranteed

**Last-write-wins (LWW)**:
A conflict-handling rule that keeps the write with the later timestamp and silently discards the other when two writes conflict, guaranteeing convergence at the cost of losing the discarded write, whether or not the two writes were genuinely concurrent.
_Avoid_: conflict resolution (imprecise; LWW avoids the need to reconcile by discarding one side, rather than resolving what both writes were trying to do)

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

**Saga**:
A sequence of local transactions, each committing independently on its own service and publishing an event to trigger the next, used in place of one atomic cross-service transaction. A failed step is undone by compensating transactions rather than automatic rollback, and the sequence can be coordinated by choreography (each service reacts to the previous one's event) or orchestration (one dedicated coordinator directs every step).
_Avoid_: distributed transaction (a saga deliberately gives up the atomicity and isolation a real distributed transaction would provide, in exchange for never blocking on another service's lock)

**Timeout**:
A caller's chosen limit on how long to wait for a response before treating the other side as failed. A guess made under permanent uncertainty, not a fact, since a network has no upper bound on message delay.
_Avoid_: deadline (use only when quoting a source or API that uses that specific term)

**Transactional outbox**:
A pattern that writes an event as an ordinary row in the same local database transaction as the business update it accompanies, so the two commit or roll back atomically without a distributed transaction; a separate message relay then publishes each outbox row to the broker, at-least-once, which is why a consumer of these events must be idempotent.
_Avoid_: message queue (too generic; the outbox table itself is not the queue, it's the durable, transactionally-consistent staging area a relay drains into one)

**Two-phase commit (2PC)**:
A protocol for committing one transaction atomically across several independent participants: a voting phase where every participant agrees to commit or aborts, followed by a commit phase where the coordinator commits only if all votes were yes. Its defining weakness is blocking: a participant that voted yes must wait, still holding its locks, until the coordinator's final decision, even if the coordinator has failed permanently.
_Avoid_: two-phase locking (2PL) (an unrelated concurrency-control protocol that happens to share the "two-phase" name)

**Version vector**:
A mechanism that tracks, per replica, how many updates it has seen from every other replica, letting any two versions be compared to determine whether one happened-before the other or whether they're concurrent. Maintains the same state as a vector clock but with update rules specifically adapted to replica versioning.
_Avoid_: vector clock (a related but distinct mechanism; the two aren't interchangeable despite sharing the same underlying state)
