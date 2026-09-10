---
title: Distributed Systems
description: "Reason about partial failure: what a network can do to you, which consistency you are actually buying, and why consensus is expensive"
type: topic
---

# Learning: Distributed Systems

Be able to choose and defend a consistency model for a system you are designing, and to reason about a production incident caused by a partial failure instead of treating the network as reliable.

**Latest lesson:** [12. Partitioning and Sharding](lessons/0012-partitioning-and-sharding.md)

## Success looks like

- Given a system design, choose a consistency model and defend the trade-off against the alternatives.
- Given an incident caused by a partial failure (a network partition, a slow node mistaken for a dead one), name the mechanism responsible.
- Explain what a consensus protocol buys you and why it costs what it costs, without needing to prove its correctness from first principles.

## Constraints

- Assumes professional experience building a networked service; no prior formal distributed-systems study required.
- Practical and operational emphasis: the cost and the trade-offs matter more than a formal proof of a protocol's correctness.

## Out of scope

- Concurrency inside one process (goroutines, threads, `Send`/`Sync`): owned by the language workspaces. This workspace starts where the process boundary is crossed.

## The arc

Twelve stages, partial failure to a diagnosed incident to the mechanisms production systems actually use to survive one. A stage takes several lessons and the boundaries are soft; what makes a stage done is the capability, not the lesson count.

| Stage | Lessons | Covers | Done when |
|---|---|---|---|
| 1. Partial failure | 0001 | The one problem every later topic in this workspace is a response to | Can explain why a network can't be treated as reliable |
| 2. Time and order | 0002 to 0003 | Clocks, ordering, why a timeout is the only failure signal available | Can explain why a timeout can't distinguish a slow node from a dead one |
| 3. Consistency models | 0004 to 0006 | CAP, linearizability, sequential and eventual consistency | Can choose and defend a consistency model for a stated design |
| 4. Consensus | 0007 to 0009 | Raft, leader election, what consensus buys and why it costs what it costs | Can explain what a consensus protocol buys and costs without proving its correctness |
| 5. Diagnosing incidents | 0010 | Applying the mechanisms above to a real production incident | Given an incident caused by partial failure, can name the mechanism responsible |
| 6. Replication and quorums | 0011 | Leader-based vs. leaderless replication, read/write quorums, the `R + W > N` condition | Can explain how a quorum guarantees a read sees the latest write, and choose R and W for a stated workload |
| 7. Partitioning and sharding | 0012 | Consistent hashing, virtual nodes, hot-key replication, request routing | Can explain why consistent hashing bounds the cost of a resize, and what a bare ring still needs to handle failure and hot keys |

## Lessons

Work through these in order.

| # | Lesson | Teaches |
|---|---|---|
| [0001](lessons/0001-partial-failure.md) | Partial Failure | The one problem every later topic in this workspace is a response to |
| [0002](lessons/0002-clocks-and-ordering.md) | Clocks and Ordering | Why wall-clock timestamps from different machines can't be trusted to order events, and how a logical clock orders them without needing synchronized time |
| [0003](lessons/0003-timeouts-as-failure-detectors.md) | Timeouts as Failure Detectors | Why every practical failure detector is built on a timeout, and the formal vocabulary for the accuracy-versus-speed trade-off that follows from it |
| [0004](lessons/0004-the-cap-theorem-precisely.md) | The CAP Theorem, Precisely | What CAP actually proves, why partition tolerance was never optional, and the specific misreadings that make "pick two" the wrong way to state it |
| [0005](lessons/0005-linearizability.md) | Linearizability | What linearizability actually guarantees, why it's the strongest common consistency model, and what it costs to provide during a partition |
| [0006](lessons/0006-sequential-and-eventual-consistency.md) | Sequential and Eventual Consistency | Two models weaker than linearizability, what each still guarantees, and how to choose among all three for a stated design |
| [0007](lessons/0007-what-consensus-is-for.md) | What Consensus Is For | The replicated-state-machine problem consensus protocols solve, and why it's the mechanism underneath a linearizable system's coordination |
| [0008](lessons/0008-raft-leader-election-and-log-replication.md) | Raft, Leader Election and Log Replication | How Raft elects a single leader and replicates a log through it, the two mechanisms that turn the replicated-state-machine problem into something concrete |
| [0009](lessons/0009-what-consensus-costs.md) | What Consensus Costs | Why every write pays a round trip to a majority, why a minority partition loses availability rather than consistency, and how to weigh that cost against what consensus buys |
| [0010](lessons/0010-diagnosing-a-production-incident.md) | Diagnosing a Production Incident | Applying partial failure, failure detection, consistency models, and consensus to name the mechanism behind a real incident, instead of reasoning about "the network" or "consistency" in the abstract |
| [0011](lessons/0011-replication-and-quorums.md) | Replication and Quorums | A consensus protocol isn't the only way to replicate data, and the quorum condition behind its cheaper alternative is a single overlap guarantee, not a vague notion of majority agreement |
| [0012](lessons/0012-partitioning-and-sharding.md) | Partitioning and Sharding | Consistent hashing exists because naive hash-mod-N partitioning remaps almost everything the moment a node joins or leaves, and even consistent hashing needs virtual nodes before it stops dumping a failed node's whole load onto one unlucky neighbor |

## Reference

- [Glossary](GLOSSARY.md): canonical terms for this topic
- [Resources](RESOURCES.md): trusted sources
- [Time and Order](reference/time-and-order.md): what happens-before can and cannot decide, what a Lamport clock refuses to tell you, and the failure-detector vocabulary a timeout is one instance of
- [Consistency Models](reference/consistency-models.md): CAP stated as it was proved, the models side by side with what each guarantees, and which of them can answer at all during a partition
- [Consensus](reference/consensus.md): the replicated-state-machine problem, Raft's five safety properties and the rules that produce them, and what a majority costs on writes and on reads
- [Diagnosing Incidents](reference/diagnosing-incidents.md): four questions in order, the named anomaly vocabulary for describing a symptom precisely, and a symptom-to-mechanism table indexed to the sheets above

## How this works

Each lesson is short and self-contained. Answer keys are collapsed: recall first, then open them. The real-world reps matter more than the reading, and spacing them out is the point. Anything still unclear at the end of a lesson is worth chasing to its primary source before moving on.
