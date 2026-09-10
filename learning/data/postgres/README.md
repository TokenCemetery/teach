---
title: Postgres
description: "Operate Postgres: the WAL, vacuum and bloat, replication, and what an index costs to keep"
type: topic
---

# Learning: Postgres

Be able to operate a running Postgres instance, self-hosted or managed, and to diagnose bloat, replication lag or a slow-to-recover failover instead of guessing at a fix, as well as design storage, replication and index upkeep for a new deployment from the start.

**Latest lesson:** [13. Monitoring: Activity, Statements, and the Log](lessons/0013-monitoring-activity-statements-and-the-log.md)

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

Eight stages, durability to monitoring the instance. A stage takes several lessons and the boundaries are soft; what makes a stage done is the capability, not the lesson count.

| Stage | Lessons | Covers | Done when |
|---|---|---|---|
| 1. The write-ahead log | 0001 | The durability mechanism everything else in this workspace builds on | Can explain how the WAL makes a crash recoverable |
| 2. Vacuum and bloat | 0002 to 0003 | Autovacuum internals, MVCC and dead tuples, bloat diagnosis and tuning | Can diagnose a bloated table from vacuum and WAL mechanics |
| 3. Replication | 0004 to 0006 | Streaming replication, replication slots, failover, lag diagnosis | Can diagnose a lagging replica and design a replication topology |
| 4. Indexes and their upkeep cost | 0007 to 0008 | B-tree/GiST/GIN maintenance cost, what a pgvector index costs to keep | Can design an index maintenance plan and account for pgvector's cost |
| 5. Managed vs self-hosted | 0009 to 0010 | What an RDS-style managed service shields you from, and what it doesn't | Can explain the managed-service boundary and defend an operating choice |
| 6. Backup and point-in-time recovery | 0011 | Base backups, continuous WAL archiving, `recovery_target_time`, and why an untested restore isn't a verified backup | Can design and defend a backup strategy that actually reconstructs a working database when tested |
| 7. Configuration and memory tuning | 0012 | `shared_buffers`, `work_mem`, `maintenance_work_mem`, checkpoint tuning | Can size these settings against actual concurrency instead of an isolated single-query test |
| 8. Monitoring | 0013 | `pg_stat_activity`, wait events, `pg_stat_statements`, the server log | Can pick the right monitoring surface (live backend state, aggregate query cost, or a logged event) for a given symptom |

## Lessons

Work through these in order.

| # | Lesson | Teaches |
|---|---|---|
| [0001](lessons/0001-the-write-ahead-log.md) | The Write-Ahead Log | The durability mechanism everything else in this workspace builds on |
| [0002](lessons/0002-mvcc-and-dead-tuples.md) | MVCC and Dead Tuples | Why an UPDATE or DELETE never removes anything immediately, and why that leaves dead tuples for vacuum to clean up |
| [0003](lessons/0003-bloat-diagnosis-and-autovacuum-tuning.md) | Bloat Diagnosis and Autovacuum Tuning | How to measure bloat, why autovacuum falls behind, and the diagnostic order that finds the actual cause instead of guessing |
| [0004](lessons/0004-streaming-replication-and-slots.md) | Streaming Replication and Replication Slots | How a standby actually connects and catches up, and what a replication slot guarantees that plain streaming doesn't |
| [0005](lessons/0005-failover-mechanics.md) | Failover Mechanics | What happens when a standby is promoted, why a former primary can't just rejoin, and the data-loss trade-off synchronous replication bounds |
| [0006](lessons/0006-diagnosing-replication-lag.md) | Diagnosing Replication Lag | Why receive lag and apply lag are different measurements, and the diagnostic order that finds which one is actually happening |
| [0007](lessons/0007-index-maintenance-cost.md) | B-Tree, GiST, and GIN Maintenance Cost | Why every index makes writes more expensive, and how B-tree, GiST, and GIN each pay that cost differently |
| [0008](lessons/0008-what-a-pgvector-index-costs.md) | What a pgvector Index Costs to Keep | The disk, build-time, and standing-memory cost a vector index adds beyond the raw vectors it indexes |
| [0009](lessons/0009-what-managed-shields-you-from.md) | What a Managed Service Shields You From | What RDS-style automation actually removes, and why everything from earlier lessons still needs understanding underneath it |
| [0010](lessons/0010-defending-an-operating-choice.md) | Defending an Operating Choice | A worked deployment design that cites a specific decision and cost from each stage, rather than assuming a default answer |
| [0011](lessons/0011-backup-and-point-in-time-recovery.md) | Backup and Point-in-Time Recovery | A base backup and a continuous WAL archive together let you reconstruct any moment since the backup, not just the moment the backup itself was taken, and an untested restore isn't a verified backup |
| [0012](lessons/0012-configuration-and-memory-tuning.md) | Configuration and Memory Tuning | shared_buffers, work_mem and maintenance_work_mem each answer a different memory question, and the one most often mistuned is the one that quietly multiplies by however many operations are actually running at once |
| [0013](lessons/0013-monitoring-activity-statements-and-the-log.md) | Monitoring: Activity, Statements, and the Log | A live view of what every backend is doing right now, an aggregate view of what's actually costing the server the most over time, and a log that names exactly what a stuck query is blocked behind, are three different questions |

## Reference

- [Glossary](GLOSSARY.md): canonical terms for this topic
- [Resources](RESOURCES.md): trusted sources
- [Vacuum and Bloat](reference/vacuum-and-bloat.md): what triggers autovacuum and with which numbers, what holds back the space it can reclaim, and the views to check in which order
- [Replication](reference/replication.md): what a slot guarantees and what it risks, the five synchronous levels and when three of them do nothing, and the two lags with the columns that separate them
- [Index Maintenance](reference/index-maintenance.md): what each index type charges per write and what degrades it, and the parameters and memory cliff a pgvector index brings with it
- [Managed vs Self-Hosted](reference/managed-vs-self-hosted.md): what a managed service automates and what it only relocates, the three high-availability shapes that are not interchangeable, and the decisions a defended design has to name

## How this works

Each lesson is short and self-contained. Answer keys are collapsed: recall first, then open them. The real-world reps matter more than the reading, and spacing them out is the point. Anything still unclear at the end of a lesson is worth chasing to its primary source before moving on.
