---
title: Diagnosing Incidents
description: "Four questions in order, the named anomaly vocabulary to describe a symptom precisely, and a symptom-to-mechanism table indexed to the rest of the workspace"
type: reference
---

# Diagnosing Incidents: From Symptom to Mechanism

Stage 5 compressed for lookup. [Lesson 10](../lessons/0010-diagnosing-a-production-incident.md) is the method; this sheet is the thing to have open during an incident review.

## A symptom is not a diagnosis

"The database lost data during a network issue" names what was seen. "The failover logic promoted a replica without checking for a majority, so both sides accepted writes" names the mechanism. Only the second tells anyone what to change.

A finished diagnosis has three parts: **what the system promised**, **what a client observed instead**, and **which mechanism failed to hold up its end**. Stopping after the second is the most common way an incident review produces no fix.

## The four questions, in order

| # | Question | Look for | Sheet |
|---|---|---|---|
| 1 | Was there **partial failure**, silence read as success or as failure? | A request with no response, a retry, an operation reported failed that had actually happened | Lesson 1 |
| 2 | Did anything depend on **time or ordering across machines**? | Timestamp comparison between hosts, a timeout or heartbeat making a slow-versus-dead call | [Time and Order](time-and-order.md) |
| 3 | Did two clients or replicas **disagree about order or currency**? | A stale read, divergent histories, a value that went backwards | [Consistency Models](consistency-models.md) |
| 4 | Was a **leader, lock or agreed value** involved? | Failover, promotion, a lease, a quorum, anything with a term or an epoch | [Consensus](consensus.md) |

Most incidents answer yes to one or two, not all four. Naming which one is the diagnosis.

## Name the anomaly

Jepsen's vocabulary makes a symptom precise. A phenomenon is not automatically a bug: **whether it is legal depends on the model the system claims**. That framing is what turns "the database did something weird" into a checkable question.

| Family | Phenomena |
|---|---|
| Adya, defined by dependencies between transactions | `G0` Write Cycle, `G1a` Aborted Read, `G1b` Intermediate Read, `G1c` Cyclic Information Flow, `G-single`, `G-nonadjacent`, `G2-item`, `G2` |
| SQL, defined by event order | `P0` Dirty Write, `P1` Dirty Read, `P2` Non-Repeatable Read, `P3` Phantom, `P4` Lost Update, `A5A` Read Skew, `A5B` Write Skew or Short Fork, Long Fork |
| Temporal | Process, Real-Time, Stale Read |
| Other | Lost Write |

**Prefer the Adya family for a distributed system.** The SQL phenomena are defined in terms of event order rather than dataflow, which makes them less useful once the events are spread across machines.

Two worth knowing by name because they show up constantly:

- **Stale Read.** A read that fails to observe the consequences of an earlier completed write. Post a photo, ring your parents, they load the page and it is not there. Prohibited by linearizability and strict serializability; **permitted by sequential consistency and by serializability**. So "we saw a stale read" is a bug report only after you say which model was promised.
- **Long Fork.** Two concurrent disjoint writes fork the state, and other transactions read from the divergent forks before they merge. The single-transaction version of the same shape is Short Fork, also called write skew or `A5B`.

## Symptom to mechanism

| Observed | Likely mechanism | Where |
|---|---|---|
| Two nodes both believed they were primary | Failover by heartbeat and timeout, with no majority vote and no term check | [Consensus](consensus.md) |
| A write confirmed, then a read returned the old value | Stale Read. Check the model actually provided, not the one assumed | [Consistency Models](consistency-models.md) |
| Two clients each saw a coherent but different history | No total order in the model, or a partition each side kept serving | [Consistency Models](consistency-models.md) |
| A healthy node was evicted, then rejoined fine | Failure-detector accuracy. A fixed timeout against a tail-latency event | [Time and Order](time-and-order.md) |
| Events replayed in the wrong order | Wall-clock timestamps compared across machines | [Time and Order](time-and-order.md) |
| Duplicate side effects from one logical action | A retry after a timeout, with no idempotency mechanism | Lesson 1 |
| Cluster stopped committing, nothing crashed, no errors | No side holds a majority, or `broadcastTime` grew past the election timeout so no leader survives | [Consensus](consensus.md) |
| A lock was held by two clients at once | A lease whose safety rests on bounded clock skew, or a lock with no consensus underneath | [Consensus](consensus.md) |
| Data written during a partition disappeared afterwards | The minority side kept accepting writes that were never committed by a majority | [Consensus](consensus.md) |
| An entry present on most nodes vanished after an election | An entry from a previous term treated as committed because it was on a majority | [Consensus](consensus.md) |

## Answers that are not diagnoses

- "The network was flaky." That is the environment every one of these mechanisms exists to survive.
- "It was a consistency issue." Which model, promised by whom, violated how?
- "The timeout was too short." Sometimes true, and never the whole answer, because no timeout value removes the slow-versus-dead problem. If the fix is only a larger number, the same incident returns with a longer tail.
- "We added a retry." A retry converts a timeout into duplicate work unless something makes the operation idempotent.
- "The database lost data." Databases have models. Say which guarantee was claimed and which phenomenon was observed.

## Writing the finding

One sentence, in this shape:

> The system promised **{guarantee}**. A client observed **{named phenomenon}**. This happened because **{mechanism}** did not hold, specifically **{the rule that was skipped or assumed}**.

Worked, from the arc's own example:

> The system promised a single primary. Clients observed writes accepted on both sides of a partition. This happened because failover was implemented with heartbeats and a timeout rather than consensus, specifically because promotion never required a majority vote, which is the rule that makes two simultaneous leaders impossible.

## Before closing the review

- The finding names a mechanism, not a condition of the network.
- The phenomenon has a name, and the model that permits or forbids it is stated.
- If a timeout is implicated, the fix is not only a new number.
- If a retry is implicated, idempotency is addressed and not just the retry policy.
- If a quorum is implicated, someone has checked that the code actually counts a majority rather than counting responses.
- The guarantee the system claims has been reread, and either it was violated or the claim was wrong. Both are findings.

## Sources

- [Site: "Consistency Models", Jepsen](https://jepsen.io/consistency)
- [Site: "Phenomena", Jepsen](https://jepsen.io/consistency/phenomena)
- [Site: "Analyses", Jepsen](https://jepsen.io/analyses)
- [Time and Order](time-and-order.md)
- [Consistency Models](consistency-models.md)
- [Consensus](consensus.md)
- [Resources](../RESOURCES.md)
