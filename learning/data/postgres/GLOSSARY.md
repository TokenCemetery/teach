---
title: Glossary
description: "Canonical terms for Postgres"
type: glossary
---

# Postgres Glossary

Canonical terms for operating a running Postgres instance: durability, background work, and replication.

## Terms

**Checkpoint**:
A periodic flush of all currently-dirty data pages to disk, paired with recording the WAL position at that moment, which bounds how far back crash recovery must replay from.
_Avoid_: snapshot (ambiguous with a transaction snapshot)

**Write-ahead log (WAL)**:
A sequential, append-only log of every change, written and fsynced to disk before that change is considered committed, which crash recovery and replication both replay to reconstruct state.
_Avoid_: transaction log, redo log (use only when quoting a source that uses those terms)
