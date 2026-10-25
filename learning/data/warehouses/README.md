---
title: Warehouses
description: "Own the analytical warehouse: columnar storage and execution, storage separated from compute, and why row-store performance advice stops applying"
type: topic
---

# Learning: Analytical Warehouses

Be able to design a table, a model and a load path on BigQuery, Snowflake or Redshift that answers the analytical questions asked of it at a cost you can predict, and to say from the storage layout why advice that was right on a row store is wrong there.

**Latest lesson:** [20. Changing a Model Others Query](lessons/0020-changing-a-model-others-query.md)

## Success looks like

- Explain from the storage layout why a query is cheap on a row store and expensive on a columnar warehouse, or the reverse, and predict what a change to the query does to the bytes it scans.
- Say what BigQuery, Snowflake and Redshift each separate between storage and compute, and size or isolate compute for a stated workload.
- Choose partitioning, clustering or sort keys and a distribution for a table from its query pattern, and show the scan that choice saves.
- Design a dimensional model at a stated grain, including how a changing dimension keeps its history.
- Design a load path, batch or micro-batch, that can be rerun without duplicating or losing rows.
- Estimate what a query or a workload costs under on-demand and under capacity pricing, and cut that cost without changing the answer.
- Decide between a warehouse, Postgres and a lakehouse for a workload, review someone else's warehouse schema and bill, and change a model others query without breaking them.

## Constraints

- Assumes working SQL and no prior warehouse experience. The language, query plans and transactional schema design are taught in [`programming/sql`](../../programming/sql/), and these lessons assume them.
- BigQuery, Snowflake and Redshift are the three platforms compared throughout. Each lesson teaches the mechanism first and then names how each platform exposes it, so the material survives a change of vendor.
- Platform defaults, limits and prices move between releases. Where a lesson quotes one it names the documentation page it came from, and the reader should check that page for the current value.

## Out of scope

- The SQL language, query plans, schema design and isolation on a row store: see [`programming/sql`](../../programming/sql/), which this track builds on rather than restates.
- Operating a Postgres instance: see [`data/postgres`](../../data/postgres/). Stage 8 compares Postgres as a candidate for an analytical workload; it does not teach running one.
- Streaming platforms as a subject. Stage 6 loads from a stream; how the log itself works is [`data/kafka`](../../data/kafka/).
- Orchestration and transformation frameworks (Airflow, dbt) as subjects. They appear where a loading or modelling lesson needs them, and how to configure one is not taught.
- BI tools, semantic layers and dashboard design.
- Spark, Trino and other engines as subjects. Stage 8 places the lakehouse they query against the warehouse; it does not teach running them.

## The arc

Eight stages, from the storage layout to judgment. A stage takes several lessons and the boundaries are soft; what makes a stage done is the capability, not the lesson count.

| Stage | Lessons | Covers | Done when |
|---|---|---|---|
| 1. Row and column storage | 0001 to 0002 | OLTP and OLAP access patterns, row stores against column stores, row groups, column chunks and their statistics | Can predict which layout reads fewer bytes for a stated query, and why |
| 2. Columnar execution | 0003 to 0004 | Dictionary, run-length and delta encoding, compression, vectorized execution, late materialization | Can say why a column store compresses and executes the way it does, and what `SELECT *` costs there |
| 3. Storage and compute | 0005 to 0006 | How BigQuery, Snowflake and Redshift separate storage from compute, slots, virtual warehouses, node types, concurrency and workload isolation | Can size and isolate compute for a stated workload on any of the three |
| 4. Physical design | 0007 to 0010 | Partitioning and pruning, clustering and sort keys, zone maps, distribution and join strategy, the row-store advice that stops applying | Can choose a table's physical layout from its query pattern and show the scan it saves |
| 5. Dimensional modelling | 0011 to 0013 | Facts, dimensions and the grain, star schemas against wide and nested tables, slowly changing dimensions | Can design a model at a stated grain that keeps the history a question needs |
| 6. Loading | 0014 to 0015 | ELT against ETL, batch loading and file sizing, micro-batch and streaming ingestion, idempotent merges | Can design a load path that can be rerun without duplicating or losing rows |
| 7. Cost | 0016 to 0017 | On-demand and capacity pricing on each platform, reading a query's cost, caches, materialized views and the controls that cap a bill | Can estimate a workload's cost and cut it without changing the answer |
| 8. Judgment | 0018 to 0020 | Warehouse against Postgres against a lakehouse, reviewing a schema and its bill, changing a model others query, settling a dispute from the platform's documentation | Trusted to make the call and to explain it to someone else |

## Lessons

Work through these in order.

| # | Lesson | Teaches |
|---|---|---|
| [0001](lessons/0001-row-stores-and-column-stores.md) | Row Stores and Column Stores | Why an analytical query reads a fraction of the bytes from a column store that it reads from a row store, and why a single-row lookup goes the other way |
| [0002](lessons/0002-inside-a-columnar-file.md) | Inside a Columnar File | How row groups, column chunks and per-chunk statistics let a reader skip data it never decompresses |
| [0003](lessons/0003-encoding-and-compression.md) | Encoding and Compression | Why one column of one type compresses far better than a row, and which encoding suits which shape of data |
| [0004](lessons/0004-vectorized-execution-and-late-materialization.md) | Vectorized Execution and Late Materialization | How a column engine processes a batch of values per call and assembles rows only for the values that survive |
| [0005](lessons/0005-separating-storage-from-compute.md) | Separating Storage from Compute | What BigQuery, Snowflake and Redshift each keep apart between where data lives and what reads it, and what that buys and costs |
| [0006](lessons/0006-compute-sizing-concurrency-and-isolation.md) | Compute Sizing, Concurrency and Workload Isolation | How to size compute for a workload and keep one team's queries from queueing behind another's |
| [0007](lessons/0007-partitioning-and-pruning.md) | Partitioning and Pruning | How a partitioned table lets a filter skip whole partitions, and the filters that silently scan everything |
| [0008](lessons/0008-clustering-and-sort-keys.md) | Clustering and Sort Keys | How ordering data inside storage tightens the min and max of each block so a filter skips more of them |
| [0009](lessons/0009-joins-and-data-distribution.md) | Joins and Data Distribution | How a distributed warehouse moves rows to join them, and how a distribution choice decides whether it has to |
| [0010](lessons/0010-the-row-store-advice-that-stops-applying.md) | The Row-Store Advice That Stops Applying | Which habits from indexing and normalizing a row store are wrong on a columnar warehouse, and which still hold |
| [0011](lessons/0011-facts-dimensions-and-the-grain.md) | Facts, Dimensions and the Grain | How to declare what one row of a fact table means before choosing a single column |
| [0012](lessons/0012-star-schemas-wide-tables-and-nesting.md) | Star Schemas, Wide Tables and Nesting | When to keep dimensions in their own tables, when to flatten them into one wide table, and when to nest them |
| [0013](lessons/0013-slowly-changing-dimensions.md) | Slowly Changing Dimensions | How a dimension keeps or discards its history when an attribute changes, and what each choice does to old reports |
| [0014](lessons/0014-elt-and-batch-loading.md) | ELT and Batch Loading | Why warehouses load raw data first and transform it in place, and how file count and size decide load speed |
| [0015](lessons/0015-micro-batch-streaming-and-idempotent-merges.md) | Micro-Batch, Streaming and Idempotent Merges | How to land data continuously and make a rerun of any load leave the table exactly as one run would |
| [0016](lessons/0016-how-a-warehouse-bills.md) | How a Warehouse Bills | What each platform charges for under on-demand and under capacity pricing, and which workload each model rewards |
| [0017](lessons/0017-reading-and-cutting-a-querys-cost.md) | Reading and Cutting a Query's Cost | How to find what a query will cost before it runs, and the changes that cut it without changing its answer |
| [0018](lessons/0018-warehouse-postgres-or-lakehouse.md) | Warehouse, Postgres or Lakehouse | How to decide where an analytical workload belongs, and when the usual answer of a warehouse is the wrong one |
| [0019](lessons/0019-reviewing-a-warehouse-schema-and-its-bill.md) | Reviewing a Warehouse Schema and Its Bill | How to review someone else's warehouse design and name what each choice costs, in bytes and in money |
| [0020](lessons/0020-changing-a-model-others-query.md) | Changing a Model Others Query | How to change a table that dashboards and pipelines depend on without breaking them, and how to settle a disputed claim from the documentation |

## Reference

- [Glossary](GLOSSARY.md): canonical terms for this topic
- [Resources](RESOURCES.md): trusted sources, each annotated with what it covers
- [Columnar Storage and Execution](reference/columnar-storage-and-execution.md): row against column layout, the encodings, and what a column engine skips
- [Platforms Compared](reference/platforms-compared.md): how BigQuery, Snowflake and Redshift name and bill the same storage and compute ideas
- [Physical Design](reference/physical-design.md): partitioning, clustering, sort keys and distribution on each platform, and the row-store habits to drop
- [Dimensional Modelling](reference/dimensional-modelling.md): the four design steps, schema shapes and the slowly changing dimension types
- [Loading](reference/loading.md): load methods per platform, file sizing, and the patterns that make a load safe to rerun
- [Cost Model](reference/cost-model.md): what each pricing model charges for, how to read a query's cost, and the controls that cap a bill
- [Schema and Bill Review](reference/schema-and-bill-review.md): a checklist for reviewing a warehouse design and its bill, and the placement decision

## How this works

Each lesson is short and self-contained. Answer keys are collapsed: recall first, then open them. The real-world reps matter more than the reading, and spacing them out is the point. Anything still unclear at the end of a lesson is worth chasing to its primary source before moving on.
