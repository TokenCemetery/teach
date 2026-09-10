---
title: Glossary
description: "Canonical terms for Postgres"
type: glossary
---

# Postgres Glossary

Canonical terms for operating a running Postgres instance: durability, background work, and replication.

## Terms

**Base backup**:
A physical copy of a running instance's data files (typically via `pg_basebackup`), not required to be internally consistent on its own since replaying the WAL archived from its start forward corrects that during recovery. The starting point continuous archiving and point-in-time recovery are built on.
_Avoid_: snapshot (ambiguous with a transaction snapshot or a storage-layer volume snapshot)

**Checkpoint**:
A periodic flush of all currently-dirty data pages to disk, paired with recording the WAL position at that moment, which bounds how far back crash recovery must replay from.
_Avoid_: snapshot (ambiguous with a transaction snapshot)

**Idle in transaction**:
A `pg_stat_activity` backend state where a session opened a transaction and has not yet committed or rolled it back. It still holds that transaction's snapshot and locks, and is one of the states that can hold back the vacuum horizon cluster-wide.
_Avoid_: idle (a materially different state; plain `idle` holds no open transaction and no snapshot)

**Logical replication**:
Replication that decodes WAL into row-level insert/update/delete events tied to a table's replication identity, rather than replaying raw physical WAL. Unlike streaming replication, it allows per-table selection and cross-major-version replication, but does not replicate DDL automatically.
_Avoid_: streaming replication (a different mechanism this workspace defines separately; do not use the two terms interchangeably)

**Partition pruning**:
The planner determining, from a query's `WHERE` clause and each partition's range/list/hash bounds, which partitions cannot possibly contain a matching row, and skipping them entirely rather than scanning them.
_Avoid_: partition elimination (use only when quoting a source that uses that term; this workspace says "partition pruning")

**Point-in-time recovery (PITR)**:
Reconstructing the database as it existed at an arbitrary past moment, by starting from a base backup and replaying its archived WAL forward to a chosen `recovery_target_time` (or LSN, name, or transaction ID), which must fall strictly after the base backup's own completion.
_Avoid_: restoring a backup (imprecise; a base backup alone only restores to its own endpoint, not to a chosen moment after it)

**Process-per-connection**:
Postgres's connection model: each client connection gets its own dedicated OS backend process, not a lightweight thread or a shared worker. Why `max_connections` costs real memory per connection regardless of activity, and why raising it requires a restart.
_Avoid_: thread-per-connection (a different model some other databases use; Postgres backends are OS processes)

**Role**:
Postgres's single unified concept for what other systems split into "user" and "group": a role can log in (given `LOGIN`), own objects, and be granted or hold membership in other roles. Special attributes (`LOGIN`, `SUPERUSER`, `CREATEDB`, `CREATEROLE`, `REPLICATION`, `BYPASSRLS`) are never inherited through membership.
_Avoid_: user, group (Postgres has no separate concepts for these; both are roles)

**Row-level security (RLS)**:
A per-table policy layer, beneath ordinary table-level GRANTs, that filters which specific rows a role may see (`USING`) or write (`WITH CHECK`). Enabling it with no policies defined denies every row by default, except to the table owner or a superuser, who bypass RLS entirely unless `FORCE ROW LEVEL SECURITY` is set.
_Avoid_: row security (imprecise; "row-level security" or "RLS" is this workspace's term)

**TOAST**:
The Oversized-Attribute Storage Technique: transparently compressing and/or moving a large variable-length value out-of-line into a separate TOAST table, since a row can never span more than one 8kB page. The TOAST table is a real table with its own index and its own vacuum and bloat behavior.
_Avoid_: BLOB storage (a different concept in other databases; "TOAST" is this workspace's specific mechanism)

**Wait event**:
The specific thing a backend is currently stalled on (`pg_stat_activity`'s `wait_event`/`wait_event_type` columns), such as a lock, an I/O operation, or an internal lightweight lock. Independent of `state`: a backend can show `active` with a non-null wait event, meaning it's running but currently blocked, not actively executing.
_Avoid_: waiting (vague; "wait event" is the specific, named signal this workspace means)

**Write-ahead log (WAL)**:
A sequential, append-only log of every change, written and fsynced to disk before that change is considered committed, which crash recovery and replication both replay to reconstruct state.
_Avoid_: transaction log, redo log (use only when quoting a source that uses those terms)
