---
title: Resources
description: "Trusted sources for Postgres"
type: resources
---

# Postgres Resources

## Knowledge

- [Docs: "Reliability and the Write-Ahead Log", PostgreSQL](https://www.postgresql.org/docs/current/wal.html)
  Official chapter on why the WAL exists, how it makes crash recovery and durability possible, and the settings that trade durability against throughput. Use for: the primary mechanism everything else in this workspace (replication, crash recovery) builds on.
- [Docs: "Routine Vacuuming", PostgreSQL](https://www.postgresql.org/docs/current/routine-vacuuming.html)
  Official chapter on why dead rows accumulate under MVCC, how autovacuum reclaims them, and the settings that control when it runs and how aggressively. Use for: diagnosing and preventing table and index bloat.
- [Wiki: "Show database bloat", PostgreSQL Wiki](https://wiki.postgresql.org/wiki/Show_database_bloat)
  A runnable query for estimating actual bloat in tables and indexes, with notes on why the estimate is approximate. Use for: measuring bloat on a real instance rather than reasoning about it in the abstract.
- [Docs: "High Availability, Load Balancing, and Replication", PostgreSQL](https://www.postgresql.org/docs/current/high-availability.html)
  Official chapter covering streaming replication, synchronous vs. asynchronous replication, and failover, including what each replication mode costs in latency and durability. Use for: designing a replication topology and explaining what it trades away.
- [Docs: "Indexes", PostgreSQL](https://www.postgresql.org/docs/current/indexes.html)
  Official chapter on index types and, critically, on the maintenance cost an index imposes on every write to its table. Use for: defending an index maintenance strategy rather than adding indexes without accounting for their upkeep cost.
- [Repo: pgvector, pgvector](https://github.com/pgvector/pgvector)
  Official repo for the vector-index extension `llm/rag` standardizes on: index types (IVFFlat, HNSW), their build and maintenance cost, and how they interact with autovacuum. Use for: what a vector index specifically costs the database to keep, connecting to `llm/rag`'s choice of pgvector as its store.
- [Docs: "PostgreSQL on Amazon RDS", AWS](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_PostgreSQL.html)
  Official docs for a managed Postgres service: what RDS handles for you (patching, failover automation, backups) and what it restricts (superuser access, some extensions, direct filesystem access). Use for: naming concretely what a managed service does and does not shield an operator from.

## Gaps

- No source yet specifically on diagnosing replication lag from `pg_stat_replication` and WAL-shipping metrics in a running incident, as opposed to the reference documentation on how replication works; worth closing once lesson design reaches on-call diagnosis.
