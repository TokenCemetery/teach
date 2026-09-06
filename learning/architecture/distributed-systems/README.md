---
title: Distributed Systems
description: "Reason about partial failure: what a network can do to you, which consistency you are actually buying, and why consensus is expensive"
type: topic
---

# Learning: Distributed Systems

Be able to choose and defend a consistency model for a system you are designing, and to reason about a production incident caused by a partial failure instead of treating the network as reliable.

**Latest lesson:** [1. Partial Failure](lessons/0001-partial-failure.md)

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

Five stages, partial failure to a diagnosed incident. A stage takes several lessons and the boundaries are soft; what makes a stage done is the capability, not the lesson count.

| Stage | Lessons | Covers | Done when |
|---|---|---|---|
| 1. Partial failure | 0001 | The one problem every later topic in this workspace is a response to | Can explain why a network can't be treated as reliable |
| 2. Time and order | 0002 to 0003 | Clocks, ordering, why a timeout is the only failure signal available | Can explain why a timeout can't distinguish a slow node from a dead one |
| 3. Consistency models | 0004 to 0006 | CAP, linearizability, sequential and eventual consistency | Can choose and defend a consistency model for a stated design |
| 4. Consensus | 0007 to 0009 | Raft, leader election, what consensus buys and why it costs what it costs | Can explain what a consensus protocol buys and costs without proving its correctness |
| 5. Diagnosing incidents | 0010 | Applying the mechanisms above to a real production incident | Given an incident caused by partial failure, can name the mechanism responsible |

## Lessons

Work through these in order.

| # | Lesson | Teaches |
|---|---|---|
| [0001](lessons/0001-partial-failure.md) | Partial Failure | The one problem every later topic in this workspace is a response to |

## Reference

- [Glossary](GLOSSARY.md): canonical terms for this topic
- [Resources](RESOURCES.md): trusted sources

## How this works

Each lesson is short and self-contained. Answer keys are collapsed: recall first, then open them. The real-world reps matter more than the reading, and spacing them out is the point. Anything still unclear at the end of a lesson is worth chasing to its primary source before moving on.
