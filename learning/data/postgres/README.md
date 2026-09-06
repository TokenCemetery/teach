---
title: Postgres
description: "Operate Postgres: the WAL, vacuum and bloat, replication, and what an index costs to keep"
type: topic
---

# Learning: Postgres

Be able to operate a running Postgres instance, self-hosted or managed, and to diagnose bloat, replication lag or a slow-to-recover failover instead of guessing at a fix, as well as design storage, replication and index upkeep for a new deployment from the start.

**Latest lesson:** [1. The Write-Ahead Log](lessons/0001-the-write-ahead-log.md)

## Success looks like

- Given a bloated table or a lagging replica, diagnose the cause from the WAL, autovacuum and replication mechanics rather than by trial and error.
- Design storage, replication topology and index maintenance for a new deployment and defend each choice.
- Explain what a managed service (RDS-style) does and does not shield you from, versus running the instance yourself.
- Account for what a vector index (pgvector) costs the database to keep, connecting to `llm/rag`'s choice of pgvector as its store.

## Constraints

- Assumes basic SQL familiarity (see `programming/sql` for the language itself); no prior database-administration experience required.
- Covers both self-hosted operation and what changes under a managed service.

## Out of scope

- Queries, query plans, schema design and isolation semantics: that is `programming/sql`, linked to rather than restated. This workspace owns the running instance, not the language.

## The arc

Five stages, durability to a defended deployment design. A stage takes several lessons and the boundaries are soft; what makes a stage done is the capability, not the lesson count.

| Stage | Lessons | Covers | Done when |
|---|---|---|---|
| 1. The write-ahead log | 0001 | The durability mechanism everything else in this workspace builds on | Can explain how the WAL makes a crash recoverable |
| 2. Vacuum and bloat | 0002 to 0003 | Autovacuum internals, MVCC and dead tuples, bloat diagnosis and tuning | Can diagnose a bloated table from vacuum and WAL mechanics |
| 3. Replication | 0004 to 0006 | Streaming replication, replication slots, failover, lag diagnosis | Can diagnose a lagging replica and design a replication topology |
| 4. Indexes and their upkeep cost | 0007 to 0008 | B-tree/GiST/GIN maintenance cost, what a pgvector index costs to keep | Can design an index maintenance plan and account for pgvector's cost |
| 5. Managed vs self-hosted | 0009 to 0010 | What an RDS-style managed service shields you from, and what it doesn't | Can explain the managed-service boundary and defend an operating choice |

## Lessons

Work through these in order.

| # | Lesson | Teaches |
|---|---|---|
| [0001](lessons/0001-the-write-ahead-log.md) | The Write-Ahead Log | The durability mechanism everything else in this workspace builds on |

## Reference

- [Glossary](GLOSSARY.md): canonical terms for this topic
- [Resources](RESOURCES.md): trusted sources

## How this works

Each lesson is short and self-contained. Answer keys are collapsed: recall first, then open them. The real-world reps matter more than the reading, and spacing them out is the point. Anything still unclear at the end of a lesson is worth chasing to its primary source before moving on.
