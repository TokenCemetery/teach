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
  Official chapter on why dead rows accumulate under MVCC, how autovacuum reclaims them, and the settings that control when it runs and how aggressively. Use for: diagnosing and preventing table and index bloat, and for the exact views and columns that reveal what is holding the horizon back: `pg_stat_activity`, `pg_prepared_xacts` and `pg_replication_slots`.
- [Docs: "Automatic Vacuuming" configuration, PostgreSQL](https://www.postgresql.org/docs/current/runtime-config-autovacuum.html)
  Every autovacuum parameter with its current default. Use for: the numbers behind the trigger formulas rather than remembered ones, including `autovacuum_vacuum_max_threshold`, a ceiling on the scale-factor calculation that is newer than most tuning advice on the subject.
- [Wiki: "Show database bloat", PostgreSQL Wiki](https://wiki.postgresql.org/wiki/Show_database_bloat)
  A runnable query for estimating actual bloat in tables and indexes, with notes on why the estimate is approximate. Use for: measuring bloat on a real instance rather than reasoning about it in the abstract.
- [Docs: "High Availability, Load Balancing, and Replication", PostgreSQL](https://www.postgresql.org/docs/current/high-availability.html)
  Official chapter covering streaming replication, synchronous vs. asynchronous replication, and failover, including what each replication mode costs in latency and durability. Use for: designing a replication topology and explaining what it trades away.
- [Docs: "Replication" configuration, PostgreSQL](https://www.postgresql.org/docs/current/runtime-config-replication.html)
  Every replication parameter with its default. Use for: `max_slot_wal_keep_size`, which defaults to unlimited and is therefore the setting that decides whether an abandoned slot can fill the primary's disk; and `hot_standby_feedback`, whose own documentation warns it can cause bloat on the primary.
- [Docs: "Write Ahead Log" configuration, PostgreSQL](https://www.postgresql.org/docs/current/runtime-config-wal.html)
  The WAL and commit parameters. Use for: the five `synchronous_commit` levels and exactly what each waits for, including the rule that three of them collapse to the same local guarantee when `synchronous_standby_names` is empty.
- [Docs: "Indexes", PostgreSQL](https://www.postgresql.org/docs/current/indexes.html)
  Official chapter on index types and, critically, on the maintenance cost an index imposes on every write to its table. Use for: defending an index maintenance strategy rather than adding indexes without accounting for their upkeep cost.
- [Docs: "CREATE INDEX", PostgreSQL](https://www.postgresql.org/docs/current/sql-createindex.html)
  The per-index storage parameters and their defaults. Use for: `fillfactor` and the range worth choosing for a write-heavy B-tree, and `fastupdate`, including the note that turning it off does not flush the pending list that already exists.
- [Repo: pgvector, pgvector](https://github.com/pgvector/pgvector)
  Official repo for the vector-index extension `llm/rag` standardizes on: index types (IVFFlat, HNSW), their build and maintenance cost, and how they interact with autovacuum. Use for: what a vector index specifically costs the database to keep, connecting to `llm/rag`'s choice of pgvector as its store.
- [Docs: "PostgreSQL on Amazon RDS", AWS](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_PostgreSQL.html)
  Official docs for a managed Postgres service: what RDS handles for you (patching, failover automation, backups) and what it restricts (superuser access, some extensions, direct filesystem access). Use for: naming concretely what a managed service does and does not shield an operator from.
- [Docs: "Multi-AZ DB instance deployments", AWS](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.MultiAZSingleStandby.html)
  The synchronous single-standby shape, with two statements teams get wrong: the standby **cannot** serve read traffic, and write and commit latency is increased against a single-AZ deployment because the replication is synchronous. Use for: separating an availability decision from a read-capacity one, and for seeing the synchronous trade-off appear in a managed product.
- [Docs: "Multi-AZ DB cluster deployments", AWS](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/multi-az-db-clusters-concepts.html)
  The semisynchronous shape, with two readable replicas across three Availability Zones and lower write latency than the single-standby deployment. Use for: the third option, when the requirement is availability and read capacity together.
- [Docs: "Continuous Archiving and Point-in-Time Recovery (PITR)", PostgreSQL](https://www.postgresql.org/docs/current/continuous-archiving.html)
  Official chapter on combining a base backup with a continuous WAL archive to reconstruct any moment since the backup. Use for: why a logical dump can't be combined with WAL archiving, the requirement that the archive be gapless back to the base backup's start, and the exact recovery-target and recovery-target-action settings that control where a restore stops and what happens next.
- [Docs: "Resource Consumption", PostgreSQL](https://www.postgresql.org/docs/current/runtime-config-resource.html)
  Official chapter on `shared_buffers`, `work_mem`, `maintenance_work_mem`, and `autovacuum_work_mem`, with each parameter's current default. Use for: the 25%-of-RAM starting guidance for `shared_buffers`, and the exact rule that `work_mem` is a per-operation limit that multiplies across concurrent sorts and hashes, not a per-connection ceiling.
- [Docs: "The Statistics Collector", PostgreSQL](https://www.postgresql.org/docs/current/monitoring-stats.html)
  Official chapter on `pg_stat_activity`'s state and wait-event columns and how they relate, and the other dynamic statistics views. Use for: the exact backend states (including `idle in transaction`), and the rule that `state` and `wait_event` are reported independently and can disagree instant to instant.
- [Docs: "pg_stat_statements", PostgreSQL](https://www.postgresql.org/docs/current/pgstatstatements.html)
  Official docs for the query-statistics extension: how it normalizes query text, and every column it reports. Use for: the exact difference between ranking by `total_exec_time` versus `mean_exec_time`, and how constant normalization merges semantically identical queries into one entry.
- [Docs: "Error Reporting and Logging", PostgreSQL](https://www.postgresql.org/docs/current/runtime-config-logging.html)
  Official chapter on every logging parameter and its current default. Use for: `log_min_duration_statement`, `log_lock_waits`, `log_checkpoints`, and `log_autovacuum_min_duration`, and which of these force the query text itself into the log versus only a duration.

## Gaps

- No source yet specifically on diagnosing replication lag from `pg_stat_replication` and WAL-shipping metrics in a running incident, as opposed to the reference documentation on how replication works; worth closing once lesson design reaches on-call diagnosis.
