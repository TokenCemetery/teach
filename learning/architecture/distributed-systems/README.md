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

- Practical and operational emphasis: the cost and the trade-offs matter more than a formal proof of a protocol's correctness.

## Out of scope

- Concurrency inside one process (goroutines, threads, `Send`/`Sync`): owned by the language workspaces. This workspace starts where the process boundary is crossed.

## The arc

{N} stages, {start} to {end}. Not a lesson list: a stage takes several lessons, and the boundaries are soft.

| Stage | Covers | Done when |
|---|---|---|
| 1. {Name} | {What it covers} | {The capability that closes the stage} |

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
