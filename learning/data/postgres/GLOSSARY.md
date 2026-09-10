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

**Point-in-time recovery (PITR)**:
Reconstructing the database as it existed at an arbitrary past moment, by starting from a base backup and replaying its archived WAL forward to a chosen `recovery_target_time` (or LSN, name, or transaction ID), which must fall strictly after the base backup's own completion.
_Avoid_: restoring a backup (imprecise; a base backup alone only restores to its own endpoint, not to a chosen moment after it)

**Wait event**:
The specific thing a backend is currently stalled on (`pg_stat_activity`'s `wait_event`/`wait_event_type` columns), such as a lock, an I/O operation, or an internal lightweight lock. Independent of `state`: a backend can show `active` with a non-null wait event, meaning it's running but currently blocked, not actively executing.
_Avoid_: waiting (vague; "wait event" is the specific, named signal this workspace means)

**Write-ahead log (WAL)**:
A sequential, append-only log of every change, written and fsynced to disk before that change is considered committed, which crash recovery and replication both replay to reconstruct state.
_Avoid_: transaction log, redo log (use only when quoting a source that uses those terms)
