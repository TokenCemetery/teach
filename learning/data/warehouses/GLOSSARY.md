---
title: Glossary
description: "Canonical terms for analytical warehouses"
type: glossary
---

# Analytical Warehouses Glossary

Canonical terms for how a columnar warehouse stores, reads, models, loads and bills data. Where BigQuery, Snowflake and Redshift each name the same idea differently, the entry picks one word and lists the platform names after it.

## Terms

**Broadcast join**:
A join that copies the whole of the smaller input to every worker holding part of the larger one, so only the small side moves over the network.
_Avoid_: replicated join, map-side join

**Bytes scanned**:
The volume of column data a query reads from storage after pruning, which is what on-demand pricing bills and what most warehouse performance work tries to shrink. It counts only the columns the query references, across every block that could not be skipped.
_Avoid_: rows scanned, data read (a row count says nothing about cost when the query touches three columns out of two hundred)

**Capacity pricing**:
A pricing model that charges for compute held over time, whatever the queries on it read: BigQuery slot reservations, Snowflake credits per second a virtual warehouse runs, Redshift node-hours or RPU-hours.
_Avoid_: flat rate, reserved pricing (each covers only one platform's variant)

**Clustering depth**:
Snowflake's measure of how well a table is clustered: the average number of micro-partitions whose value ranges overlap at a given value of the clustering columns. 1 is the floor, and lower prunes better.
_Avoid_: clustering ratio, clustering score

**Clustering key**:
The column or columns a table's storage is ordered or co-located by, so that each block holds a narrow range of their values and a filter on them skips more blocks. BigQuery and Snowflake call it a clustering key; Redshift's equivalent is the sort key.
_Avoid_: index (a clustering key builds no separate lookup structure; it changes where rows are stored)

**Column chunk**:
The values of one column for one row group, stored contiguously and compressed together, with its own statistics. The unit a columnar reader fetches, decompresses or skips.
_Avoid_: column file, column segment (both name different, platform-specific containers)

**Column store**:
A storage layout that keeps each column's values together, so a query reads only the columns it references. Suited to OLAP.
_Avoid_: columnar database (the layout is the point; some databases offer both)

**Conformed dimension**:
A dimension table shared, with the same keys and the same meaning, by several fact tables, so their measures can be compared and combined across business processes.
_Avoid_: shared dimension, master table

**Dictionary encoding**:
An encoding that replaces each value in a column chunk with a small integer index into a list of the chunk's distinct values. Effective when a column has few distinct values relative to its row count.
_Avoid_: lookup compression

**Dimension table**:
A table of descriptive context for facts, such as customer, product or date, one row per member, joined to a fact table through a key. Filters and group-bys come from here.
_Avoid_: lookup table, reference table

**Distribution style**:
The rule a distributed warehouse uses to place a table's rows on compute nodes: by the hash of a key, round-robin, or a full copy on every node. Named explicitly in Redshift (`DISTSTYLE KEY`, `EVEN`, `ALL`, `AUTO`); BigQuery and Snowflake choose placement themselves.
_Avoid_: sharding (sharding usually means separate databases, not one engine's placement rule)

**ELT**:
Extract, load, transform: land source data in the warehouse in its raw form, then transform it there with SQL. The reverse order of ETL, which transforms before loading.
_Avoid_: ETL, when the transform runs inside the warehouse

**Fact table**:
A table whose rows record measurements of a business process at a declared grain, holding numeric measures and foreign keys to dimension tables.
_Avoid_: event table, transaction table (both describe a source, not a modelling role)

**Grain**:
The declaration of what exactly one row of a fact table represents, such as one line item on one order. Stated before any column is chosen, and every measure and dimension must be true at it.
_Avoid_: granularity, level of detail (in this workspace the grain is a stated sentence, not a vague degree)

**Idempotent load**:
A load whose rerun with the same input leaves the target table exactly as a single run would, with no duplicated and no missing rows.
_Avoid_: safe load, re-runnable load

**Lakehouse**:
An architecture that keeps tables as open-format files in object storage, described by a table format that adds transactions and schema, and queried by any engine that reads that format.
_Avoid_: data lake (a lake has the files without the table format's transactions)

**Late materialization**:
Executing filters and joins on column data alone and assembling full rows only for the values that survive, instead of building rows first and filtering them.
_Avoid_: lazy loading

**Load metadata**:
The record a load method keeps of the files it has already loaded, by name and checksum, so a rerun skips them. Snowflake `COPY INTO` keeps it for 64 days and a Snowpipe pipe for 14 days.
_Avoid_: load history, when it means the audit view of past loads

**Micro-batch**:
Loading a continuous stream as a series of small, frequent batch loads, each committed as one unit, rather than as individual rows.
_Avoid_: streaming (true streaming ingestion commits rows or small groups without a batch boundary)

**Micro-partition**:
Snowflake's unit of storage: an immutable file of roughly 50 to 500 MB uncompressed, holding a group of rows in columnar form with per-column metadata used for pruning.
_Avoid_: partition (a Snowflake micro-partition is created automatically, not declared)

**Natural key**:
The identifier the source system gives an entity, such as a customer number, which stays the same across every historical row of a dimension that tracks it.
_Avoid_: business key, ID

**OLAP**:
Online analytical processing: a workload of few queries that each read many rows but few columns, aggregating them. What a column store is built for.
_Avoid_: reporting, analytics (both name a use, not an access pattern)

**OLTP**:
Online transaction processing: a workload of many short queries that each read or write a few whole rows by key. What a row store is built for.
_Avoid_: operational database (names a role, not an access pattern)

**On-demand pricing**:
A pricing model that charges per query for what it reads, independent of how long compute was held. BigQuery on-demand bills bytes scanned; Redshift Spectrum bills bytes scanned from S3.
_Avoid_: pay as you go (also describes Snowflake's per-second compute billing, which is capacity pricing)

**Partition**:
A declared division of a table by the value of one column, usually a date or timestamp, stored and pruned as a unit. Distinct from a Snowflake micro-partition, which is automatic.
_Avoid_: shard, segment

**Point-in-time join**:
A join that matches each fact to the dimension row valid when the fact happened, through a surrogate key stored at load time or through the natural key and a validity interval.
_Avoid_: as-of join, when it means one engine's syntax

**Pruning**:
Skipping a partition, micro-partition or block without reading it, because its metadata proves no row in it can match the filter.
_Avoid_: partition elimination, data skipping (both name pruning by one mechanism)

**Row group**:
A horizontal slice of a columnar file or table holding a fixed range of rows, within which each column is stored as its own column chunk.
_Avoid_: stripe, block (the ORC and engine-specific names)

**Row store**:
A storage layout that keeps all of one row's columns together on a page, so reading one whole row is a single fetch. Suited to OLTP.
_Avoid_: relational database (relational describes the model, not the layout)

**Run-length encoding**:
An encoding that stores a run of repeated values as one value and a count. Effective on sorted or low-cardinality columns, which is part of why sorting a table shrinks it.
_Avoid_: RLE compression, when it is combined with other encodings

**Shuffle**:
Rehashing rows on a join or grouping key and sending each one to the worker that owns its hash, so matching rows meet. Redshift calls it redistribution.
_Avoid_: repartition, when it means the whole operation

**Skew**:
Uneven work across workers, caused by a key with few values, one dominant value, or a filter that keeps rows on few workers. A query finishes when its busiest worker does.
_Avoid_: hot spot, imbalance

**Slot**:
BigQuery's unit of compute: a share of CPU, memory and network that a query's stages run on. A query uses as many as the scheduler grants it, up to what the project or reservation holds.
_Avoid_: worker, node

**Slowly changing dimension**:
A dimension whose attributes change over time, together with the rule that decides whether the old value is overwritten (type 1), kept as a new row with validity dates (type 2), or kept in another column (type 3).
_Avoid_: history table, versioned dimension

**Sort key**:
Redshift's clustering key: the column or columns a table's blocks are ordered by, compound or interleaved, so zone maps let a filter skip blocks.
_Avoid_: index

**Staging table**:
A table holding one batch of typed, deduplicated rows between the raw layer and the modelled tables, where a load is checked before it is merged.
_Avoid_: temp table, landing table

**Star schema**:
A dimensional model with one fact table joined directly to each of its denormalized dimension tables, one join deep. A snowflake schema normalizes the dimensions into further tables.
_Avoid_: snowflake schema, when the dimensions are not normalized

**Storage and compute separation**:
An architecture in which table data lives in shared storage independent of any compute, so compute can be added, removed, resized or isolated without moving data.
_Avoid_: serverless (separation is about where data lives; serverless is about who manages the compute)

**Surrogate key**:
An integer or hash key a warehouse assigns to each dimension row, independent of the source system's natural key, so one natural key can have several historical rows.
_Avoid_: ID, primary key (both say nothing about where the key came from)

**Table format**:
A specification layered over data files in object storage that records which files make up a table at each snapshot, giving transactions, schema evolution and time travel. Apache Iceberg, Delta Lake and Apache Hudi are table formats.
_Avoid_: file format (Parquet is a file format; a table format describes a set of files)

**Vectorized execution**:
Running each operator over a batch of values from one column per call, rather than one row per call, so the CPU spends its time on data instead of on per-row function overhead.
_Avoid_: batch processing (names a scheduling style, not an execution model)

**Virtual warehouse**:
Snowflake's unit of compute: a named, sized cluster that runs queries, bills credits per second while it runs, and suspends when idle, independent of where tables are stored.
_Avoid_: warehouse, alone (in this workspace "warehouse" means the whole platform)

**Zone map**:
Per-block metadata recording the minimum and maximum of each column in the block, which a reader checks before fetching the block. Redshift's name; Parquet and Snowflake keep the same statistics under other names.
_Avoid_: index, block index
