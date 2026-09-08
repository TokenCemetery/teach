---
title: Index Maintenance
description: "What each index type charges per write and what degrades it, and the parameters and memory cliff a pgvector index brings with it"
type: reference
---

# Index Maintenance

Stage 4 compressed for lookup. [Lesson 7](../lessons/0007-index-maintenance-cost.md) covers how B-tree, GiST and GIN each pay for writes and [lesson 8](../lessons/0008-what-a-pgvector-index-costs.md) covers what a vector index costs to keep; this sheet is the parameters and the numbers.

PostgreSQL values are from the version 18 documentation; pgvector values from its current README. Both move.

## Every index taxes every write

An `INSERT`, `UPDATE` or `DELETE` maintains every index on the table, independently. The question per index type is not whether it costs, but where the cost lands.

| Type | Per-write cost | Degrades by | Restored by |
|---|---|---|---|
| B-tree | Cheap, until a leaf page splits | Dead entries left in place, like table bloat | `REINDEX`, or a lower `fillfactor` up front |
| GiST | Higher per operation, since descent uses type-specific functions | Bounding regions growing and overlapping | `REINDEX`. Vacuum does not undo it |
| GIN | Expensive, **deliberately deferred** to a pending list | The pending list filling, then a bulk flush | Vacuum, or `gin_clean_pending_list()` |
| HNSW | Graph edges maintained per insert | Update-heavy workloads, version dependent | `REINDEX`, and reading that version's notes |
| IVFFlat | Cheap relative to HNSW | Data drifting away from the lists trained at build | Rebuild after the data changes shape |

## B-tree

`fillfactor` defaults to **90**. Leaf pages are filled to that percentage during a build and when extending at the right-hand edge. Pages that later fill completely split, fragmenting the on-disk structure.

For a table expecting many inserts or updates, a fillfactor between **50 and 90** set at `CREATE INDEX` time smooths the rate of page splits during the index's early life, and the documentation notes it may even lower the absolute number of splits.

## GIN and its pending list

`fastupdate` defaults to **ON**. New entries go to a pending list rather than into the main structure, which is what makes GIN inserts affordable. When the list exceeds `gin_pending_list_limit`, default **4MB**, the entries are moved into the main structure **in bulk**.

So GIN's write cost is not lower, it is lumpy: cheap inserts punctuated by a flush that some unlucky statement pays for.

**The trap:** turning `fastupdate` off with `ALTER INDEX` stops future entries going to the pending list and **does not flush what is already there**. Follow it with a `VACUUM` of the table, or call `gin_clean_pending_list()`.

`gin_pending_list_limit` is a server setting and can be overridden per index, in kilobytes, through index storage parameters.

## Parallel index builds

`max_parallel_maintenance_workers` applies to `CREATE INDEX` for **B-tree, GIN and BRIN**, and to `VACUUM` without `FULL`.

GiST is not on that list. A large GiST build is single-threaded, which is worth knowing before scheduling a maintenance window around it.

## pgvector

| | HNSW | IVFFlat |
|---|---|---|
| Structure | Multilayer graph | Vectors divided into lists, a subset searched |
| Query performance | Better speed-to-recall | Lower |
| Build time | Slower | Faster |
| Memory | More | Less |
| Can be built on an empty table | **Yes**, there is no training step | No, it needs data first |

### Parameters worth knowing by heart

| Parameter | Default | Effect |
|---|---|---|
| `m` | 16 | Max connections per layer. More edges, larger index |
| `ef_construction` | 64 | Candidate list size while building. Higher means better recall, at build and insert cost |
| `hnsw.ef_search` | 40 | Candidate list size at query time. Higher means better recall, slower. Use `SET LOCAL` for one query |
| `ivfflat.probes` | 1 | Lists searched. Raising it to the list count gives exact search, at which point the planner stops using the index |

IVFFlat sizing, from the README: `lists` around `rows / 1000` up to a million rows, and `sqrt(rows)` beyond that; `probes` starting around `sqrt(lists)`.

### The build memory cliff

Lesson 8 warns that too little `maintenance_work_mem` "can force a much slower fallback path". The signal is explicit, and it is worth watching for by name:

```text
NOTICE:  hnsw graph no longer fits into maintenance_work_mem after 100000 tuples
DETAIL:  Building will take significantly more time.
HINT:  Increase maintenance_work_mem to speed up builds.
```

`maintenance_work_mem` defaults to **64MB**, which is nowhere near a real vector workload. Raise it for the build, and not so far that the server runs out of memory. Build after loading data, not before, and watch progress in `pg_stat_progress_create_index`, where HNSW reports the phases `initializing` and `loading tuples`.

### Two operational facts the arc does not mention

- **An approximate index shared between tenants leaks across them.** One tenant's vectors affect the recall and the speed another tenant sees, because the structure is shared. Tenant isolation means list partitioning or separate tables, not a filter on the query.
- **Filtered vector search needs its own plan.** A `WHERE` clause the index does not know about degrades recall, and the answers are iterative scan, a partial index when there are few distinct filter values, or partitioning when there are many.

Smaller indexes are available without changing the algorithm: `halfvec` for half precision, and binary quantization for faster builds at scale.

## Before adding an index

- Name the query it serves, and accept the write cost on every statement touching the table.
- For a write-heavy B-tree, set `fillfactor` at creation rather than reindexing later.
- For GIN, decide whether lumpy write latency is acceptable, since that is what `fastupdate` buys.
- For GiST, plan a periodic `REINDEX`, because vacuum does not undo region overlap, and expect a single-threaded build.
- For HNSW, raise `maintenance_work_mem` before the build and watch for the notice, and build after loading.
- For IVFFlat, build after the data is representative, and revisit `lists` when the volume changes materially.
- For any vector index, check the extension's release notes for the version you run, because its update handling has changed between releases.

## Sources

- [Docs: "Indexes", PostgreSQL](https://www.postgresql.org/docs/current/indexes.html)
- [Docs: "CREATE INDEX", PostgreSQL](https://www.postgresql.org/docs/current/sql-createindex.html)
- [Docs: "Resource Consumption" configuration, PostgreSQL](https://www.postgresql.org/docs/current/runtime-config-resource.html)
- [Repo: pgvector, pgvector](https://github.com/pgvector/pgvector)
- [Vacuum and Bloat](vacuum-and-bloat.md)
- [Resources](../RESOURCES.md)
