---
title: Resources
description: "Trusted sources for distributed systems"
type: resources
---

# Distributed Systems Resources

## Knowledge

- [Article: "Fallacies of distributed computing", Wikipedia](https://en.wikipedia.org/wiki/Fallacies_of_distributed_computing)
  The canonical list (originated by Peter Deutsch, extended by James Gosling) of assumptions that hold on one machine and quietly stop holding once a network sits between two of them. Use for: the vocabulary for what a network can do to you, before reasoning about any specific failure.
- [Paper: "Time, Clocks, and the Ordering of Events in a Distributed System", Leslie Lamport, 1978](https://lamport.azurewebsites.net/pubs/time-clocks.pdf)
  The original paper defining the happens-before relation and logical clocks: a way to order events across machines without relying on synchronized physical clocks. Use for: why wall-clock timestamps from different machines can't be trusted to order events, and what to use instead.
- [Paper: "Virtual Time and Global States of Distributed Systems", Friedemann Mattern, 1988](https://www.vs.inf.ethz.ch/publ/papers/VirtTimeGlobStates.pdf)
  One of the standard references for vector clocks, the mechanism that supplies the direction Lamport's clock condition deliberately does not: with a vector, `a` happens-before `b` **if and only if** the vectors compare, so concurrency becomes detectable. Use for: deciding whether a system needs to recognise concurrent events, and what that costs in message size.
- [Paper: "Impossibility of Distributed Consensus with One Faulty Process", Fischer, Lynch and Paterson, 1985](https://groups.csail.mit.edu/tds/papers/Lynch/jacm85.pdf)
  The FLP result: no deterministic algorithm in an asynchronous system can guarantee consensus with even one faulty process. Use for: why failure detectors exist at all, since they are the standard way of adding just enough assumption to escape this result without pretending the network is synchronous.
- [Paper: "Unreliable Failure Detectors for Reliable Distributed Systems", Chandra and Toueg, 1996](https://www.cs.utexas.edu/~lorenzo/corsi/cs380d/papers/p225-chandra.pdf)
  The paper formalizing failure detectors by their completeness and accuracy properties, and showing consensus is solvable even with a failure detector that makes infinitely many mistakes. Use for: the formal vocabulary behind why a practical failure detector (a timeout) trades accuracy for speed, and the bridge into what consensus protocols (stage 4) actually need from failure detection.
- [Site: "Consistency Models", Jepsen](https://jepsen.io/consistency)
  An interactive, precisely-defined map of consistency models (linearizability, serializability, causal consistency, and more), with the guarantees and violations that distinguish each. Use for: pinning down exactly which consistency model a system is buying, rather than reasoning about "consistency" as one vague thing.
- [Paper: "Brewer's Conjecture and the Feasibility of Consistent, Available, Partition-Tolerant Web Services", Gilbert and Lynch, 2002](https://www.comp.nus.edu.sg/~gilbert/pubs/BrewersConjecture-SigAct.pdf)
  The proof, as opposed to the conjecture and the retrospective. Its definitions are narrower than the words: consistency means atomic, meaning linearizable, and availability means every request received by a non-failing node must terminate in a response, with no bound on how long. Use for: settling what CAP actually claims, especially when an argument turns on what "available" was supposed to mean.
- [Paper: "Linearizability: A Correctness Condition for Concurrent Objects", Herlihy and Wing, 1990](https://cs.brown.edu/~mph/HerlihyW90/p463-herlihy.pdf)
  The paper that introduced linearizability, and with it strict serializability. Use for: the precise guarantee, and the fact that it is a **single-object** condition, so a system calling itself linearizable has promised nothing about two objects together.
- [Paper: "How to Make a Multiprocessor Computer That Correctly Executes Multiprocess Programs", Leslie Lamport, 1979](https://lamport.azurewebsites.net/pubs/multi.pdf)
  Two pages, and the origin of sequential consistency: the result of any execution is as if all processors' operations ran in some sequential order, with each processor's own operations in program order. Use for: the definition itself, and for seeing how much weaker it is than linearizability once the real-time clause is absent.
- [Article: "CAP Twelve Years Later: How the 'Rules' Have Changed", Eric Brewer, InfoQ](https://www.infoq.com/articles/cap-twelve-years-later-how-the-rules-have-changed/)
  CAP's own author revisiting and correcting common misreadings of the theorem, including that partition tolerance isn't optional and that the real trade-off is more nuanced than "pick two". Use for: using CAP correctly instead of the oversimplified version most engineers repeat.
- [Paper: "In Search of an Understandable Consensus Algorithm", Ongaro and Ousterhout, 2014](https://raft.github.io/raft.pdf)
  The Raft paper, written explicitly to make a consensus protocol's mechanism and cost understandable without requiring a from-scratch proof of correctness. Use for: the primary source on what a consensus protocol actually does and what it costs to run.
- [Site: "The Raft Consensus Algorithm", raft.github.io](https://raft.github.io/)
  Interactive visualization of Raft's leader election and log replication, letting you watch the protocol handle a simulated node failure or partition. Use for: building intuition for Raft's mechanics before or alongside reading the paper.
- [Site: "Phenomena", Jepsen](https://jepsen.io/consistency/phenomena)
  The named anomaly vocabulary: Adya's dependency-based phenomena (`G0` through `G2`), the SQL ones (dirty read, lost update, write skew), the temporal ones (stale read, real-time, process) and long fork. Each page says which models permit the phenomenon and which forbid it. Use for: describing an incident symptom precisely enough to ask whether it was a bug, since whether a phenomenon is legal depends on the model the system claimed. Prefer the Adya family for distributed systems; the SQL phenomena are defined by event order rather than dataflow.
- [Site: "Analyses", Jepsen](https://jepsen.io/analyses)
  Real distributed databases and coordination systems tested under actual network partitions and process pauses, with the specific consistency violations each analysis found. Use for: concrete, real-system evidence of what partial failure actually does to a system that assumed the network was reliable.

- [Paper: "The Accrual Failure Detector", Hayashibara, Defago, Yared and Katayama, 2004](https://dspace.jaist.ac.jp/dspace/bitstream/10119/4784/1/IS-RR-2004-010.pdf)
  Introduces accrual failure detection, where the detector reports a suspicion level on a continuous scale instead of a boolean trust-or-suspect, so each application picks its own threshold against a scale the detector adapts to observed network conditions. The `phi` detector is the implementation, measured over an intercontinental link. Use for: the detection and timeout mechanics behind telling a slow node from a dead one, and for why a fixed timeout is a bet on a distribution.

- [Article: "Dynamo (storage system)", Wikipedia](https://en.wikipedia.org/wiki/Dynamo_(storage_system))
  A summary of Amazon's Dynamo paper (DeCandia et al., 2007) and its techniques table: consistent hashing for partitioning, vector clocks for highly available writes, sloppy quorums and hinted handoff for temporary failures, and Merkle-tree anti-entropy for permanent ones. Use for: leaderless replication as a concrete, real design, and the fact that DynamoDB itself later chose single-leader replication instead, despite the shared name and lineage.
- [Article: "Quorum (distributed computing)", Wikipedia](https://en.wikipedia.org/wiki/Quorum_(distributed_computing))
  Covers Gifford's 1979 quorum-based voting for replicated data: the `Vr + Vw > V` rule that guarantees a read quorum and a write quorum overlap, and the separate `Vw > V/2` rule that guarantees two write quorums overlap with each other. Use for: the precise arithmetic behind `R + W > N`, rather than an intuitive but imprecise notion of "majority agreement".
- [Article: "Consistent hashing", Wikipedia](https://en.wikipedia.org/wiki/Consistent_hashing)
  Covers the ring construction, the `O(K/N)` average-case bound on keys remapped when a node joins or leaves, and the practical extensions: virtual nodes (to avoid dumping a failed node's whole load onto one neighbor) and replicating a single "hot" key onto multiple contiguous nodes. Use for: precisely why consistent hashing beats plain `hash(key) mod M`, and the specific gaps a bare ring still leaves that virtual nodes and hot-key replication close.
- [Article: "Version vector", Wikipedia](https://en.wikipedia.org/wiki/Version_vector)
  Covers how a version vector detects happened-before versus concurrent updates for causality tracking among replicas, and its explicit distinction from a vector clock despite sharing the same underlying state. Use for: the precise mechanism behind detecting whether two writes actually conflict, before any resolution strategy is applied.
- [Article: "Conflict-free replicated data type", Wikipedia](https://en.wikipedia.org/wiki/Conflict-free_replicated_data_type)
  Covers the state-based (CvRDT) versus operation-based (CmRDT) distinction, the commutative/associative/idempotent properties each requires, and a concrete worked example (the G-Counter, merging by element-wise maximum). Use for: how a CRDT merges concurrent updates without loss, and the delivery-guarantee trade-off between the two CRDT shapes.
- [Article: "Two-phase commit protocol", Wikipedia](https://en.wikipedia.org/wiki/Two-phase_commit_protocol)
  Covers the voting and commit phases, the exact message flow, and the documented blocking failure mode when a coordinator fails after a participant has voted yes. Use for: precisely why 2PC is a blocking protocol, and the specific, worse case where the coordinator and a participant fail together.
- [Pattern: "Saga", microservices.io](https://microservices.io/patterns/data/saga.html)
  Chris Richardson's pattern reference for sagas: compensating transactions in place of automatic rollback, choreography versus orchestration, and the drawbacks (lost isolation, the dual-write problem each step still faces). Use for: the precise trade-offs a saga makes against 2PC, not just "it's the microservices way to do transactions."
- [Pattern: "Transactional outbox", microservices.io](https://microservices.io/patterns/data/transactional-outbox.html)
  Chris Richardson's pattern reference for the outbox table and message relay. Use for: exactly what the pattern guarantees (atomicity between a database commit and a message send, preserved order) and what it explicitly does not (exactly-once delivery, which is why a consumer must be idempotent).

## Gaps

- No source yet on how a real incident is diagnosed end to end, as opposed to the mechanisms individually. Rechecked while writing the stage 5 reference sheet: the Phenomena pages supply the vocabulary for naming a symptom, and the Analyses supply worked examples, but each analysis is written about one system rather than as a method, so the four-question sequence in the sheet is the workspace's own synthesis and rests on no single source. Still open.
