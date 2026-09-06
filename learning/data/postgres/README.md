---
title: Postgres
description: "Operate Postgres: the WAL, vacuum and bloat, replication, and what an index costs to keep"
type: topic
---

# Learning: Postgres

Be able to operate a running Postgres instance, self-hosted or managed, and to diagnose bloat, replication lag or a slow-to-recover failover instead of guessing at a fix, as well as design storage, replication and index upkeep for a new deployment from the start.

**Latest lesson:** _none yet_

## Success looks like

- Given a bloated table or a lagging replica, diagnose the cause from the WAL, autovacuum and replication mechanics rather than by trial and error.
- Design storage, replication topology and index maintenance for a new deployment and defend each choice.
- Explain what a managed service (RDS-style) does and does not shield you from, versus running the instance yourself.
- Account for what a vector index (pgvector) costs the database to keep, connecting to `llm/rag`'s choice of pgvector as its store.

## Constraints

- Covers both self-hosted operation and what changes under a managed service.

## Out of scope

- Queries, query plans, schema design and isolation semantics: that is `programming/sql`, linked to rather than restated. This workspace owns the running instance, not the language.

## The arc

{N} stages, {start} to {end}. Not a lesson list: a stage takes several lessons, and the boundaries are soft.

| Stage | Covers | Done when |
|---|---|---|
| 1. {Name} | {What it covers} | {The capability that closes the stage} |

## Lessons

Work through these in order.

| # | Lesson | Teaches |
|---|---|---|
| _none yet_ | | |

## Reference

- [Glossary](GLOSSARY.md): canonical terms for this topic
- [Resources](RESOURCES.md): trusted sources

## How this works

Each lesson is short and self-contained. Answer keys are collapsed: recall first, then open them. The real-world reps matter more than the reading, and spacing them out is the point. Anything still unclear at the end of a lesson is worth chasing to its primary source before moving on.
