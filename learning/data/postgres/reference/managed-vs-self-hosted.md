---
title: Managed vs Self-Hosted
description: "What a managed service automates and what it only relocates, the three high-availability shapes that are not interchangeable, and the decisions a defended design has to name"
type: reference
---

# Managed and Self-Hosted

Stage 5 compressed for lookup. [Lesson 9](../lessons/0009-what-managed-shields-you-from.md) covers what managed automation removes and [lesson 10](../lessons/0010-defending-an-operating-choice.md) is the defended design; this sheet is the boundary, drawn concretely, and the checklist.

AWS specifics are from the Amazon RDS user guide and are used as the worked example. Other providers draw the line in similar places, and not identically.

## The line, in one sentence

A managed service changes **who performs an operation and how**. It does not change **whether the underlying mechanism happens**.

| What it automates | What it relocates rather than removes |
|---|---|
| Patching and minor upgrades, on a maintenance window | Deciding when your workload can absorb a restart |
| Backups and point-in-time recovery | Knowing your recovery point objective and testing a restore |
| Failure detection and promotion, the gap PostgreSQL itself leaves | Timeline divergence and how much committed data a failover may lose |
| Provisioning a standby | Whether that standby is synchronous, and what that costs per commit |
| Storage growth | Why the storage is growing, which may be bloat |

Everything in the right-hand column is a question from an earlier stage, asked through a console instead of a shell.

## Access is what actually changes

On RDS for PostgreSQL the master user is **not** a PostgreSQL superuser. It receives `CREATE ROLE`, `CREATE DB` and membership of the `rds_superuser` role. That is enough for ordinary administration and not enough for anything requiring the `SUPERUSER` attribute or the filesystem.

Consequences worth planning for rather than discovering:

- Configuration changes go through the provider's parameter groups, not by editing `postgresql.conf`.
- Anything assuming OS-level access to the data directory is unavailable in that form.
- Extension availability is the provider's list, not PostgreSQL's. `pgvector` is supported by most major offerings, which matters for a vector workload, and "most" is not "all", so it is a thing to confirm for the specific offering rather than assume.

## Three high-availability shapes, not one

These are commonly conflated, and they answer different questions.

| | Multi-AZ DB **instance** | Multi-AZ DB **cluster** | Read replica |
|---|---|---|---|
| Standbys | One | Two readers, three AZs total | As many as configured |
| Replication | Synchronous | Semisynchronous | Asynchronous |
| Standby serves reads | **No** | **Yes** | Yes |
| Write latency | **Increased** against single-AZ, from the synchronous replication | Lower than the Multi-AZ instance | Unaffected |
| Answers | Availability | Availability and read capacity | Read capacity |

**The Multi-AZ standby is not a read replica.** The documentation states it plainly: the high availability option is not a scaling solution for read-only scenarios, and you cannot use the standby to serve read traffic. A team that provisioned Multi-AZ expecting to offload reports has bought availability and no read capacity.

The latency row is the managed embodiment of the synchronous trade on [Replication](replication.md). Choosing Multi-AZ instance is choosing to pay commit latency for a bounded loss, whether or not anyone framed it that way.

## What you still own

Every row here is diagnosed with the same signals as on self-hosted, through whatever the provider exposes.

| Concern | Still yours | Sheet |
|---|---|---|
| Dead tuples and bloat | Autovacuum tuning per table, and the horizon holders | [Vacuum and Bloat](vacuum-and-bloat.md) |
| Replica lag | Receive against apply, and which one is happening | [Replication](replication.md) |
| Replication slots | An abandoned one still retains WAL and still holds the vacuum horizon | [Replication](replication.md) |
| Index cost | Every index still taxes every write | [Index Maintenance](index-maintenance.md) |
| Vector index memory | Whether the graph fits, at build and at rest | [Index Maintenance](index-maintenance.md) |

## A defended operating choice

Not "we chose RDS because it is popular". One decision and its cost, from each stage.

| Stage | Name |
|---|---|
| Durability and replication | The recovery point objective, and the synchronous or asynchronous choice that bounds it, with the commit latency accepted in exchange |
| Slots | Which standbys warrant one, and who removes it when that standby is decommissioned |
| Vacuum | The write pattern of each major table, and the per-table autovacuum settings that follow, rather than one global default |
| Indexes | For each index, its type and the write cost it imposes; for a vector index, the disk, the build memory and the standing memory |
| Operating model | The team's actual capacity to monitor and diagnose the four rows above, against what the provider automates, and confirmation that every required extension exists on that offering |

The test for each row is whether it names a number or a trade-off. A row that names neither has not been decided, it has been defaulted.

## Before signing up to either

- The managed offering supports every extension the design needs, checked rather than assumed.
- Someone knows the master user is not a superuser, and no planned procedure requires one.
- The high-availability shape chosen answers the question actually being asked, availability or read capacity or both.
- If a Multi-AZ instance is chosen, the commit latency it adds is acceptable and known.
- Monitoring covers bloat, replica lag split by kind, and slot retention, because none of those become someone else's problem.
- A restore has been tested, not merely enabled.

## Sources

- [Docs: "PostgreSQL on Amazon RDS", AWS](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_PostgreSQL.html)
- [Docs: "Multi-AZ DB instance deployments", AWS](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.MultiAZSingleStandby.html)
- [Docs: "Multi-AZ DB cluster deployments", AWS](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/multi-az-db-clusters-concepts.html)
- [Docs: "Master user account privileges", AWS](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/UsingWithRDS.MasterAccounts.html)
- [Vacuum and Bloat](vacuum-and-bloat.md)
- [Replication](replication.md)
- [Index Maintenance](index-maintenance.md)
- [Resources](../RESOURCES.md)
