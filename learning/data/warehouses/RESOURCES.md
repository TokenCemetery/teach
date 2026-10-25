---
title: Resources
description: "Trusted sources for analytical warehouses"
type: resources
---

# Analytical Warehouses Resources

## Knowledge

### Column stores and execution

- [Paper: "The Design and Implementation of Modern Column-Oriented Database Systems", Abadi, Boncz, Harizopoulos, Idreos and Madden, Foundations and Trends in Databases (2013)](https://www.cs.umd.edu/~abadi/papers/abadi-column-stores.pdf)
  The survey of column-store internals by the researchers who built C-Store, MonetDB and VectorWise: column layout, compression and operating on compressed data, vectorized execution, late materialization and joins. Use for: the mechanism behind stages 1 and 2, settled from the people who designed it.
- [Docs: "File Format", Apache Parquet](https://parquet.apache.org/docs/file-format/)
  The specification's overview of a Parquet file: row groups, column chunks, pages and the footer metadata that holds each chunk's statistics. Use for: a concrete, open columnar layout to reason about, since every warehouse's proprietary format follows the same shape.
- [Docs: "Configurations", Apache Parquet](https://parquet.apache.org/docs/file-format/configurations/)
  The recommended row group and page sizes, with the reasoning behind each. Use for: why a row group is hundreds of megabytes and a page a few kilobytes.
- [Spec: "parquet.thrift", Apache Parquet Format](https://github.com/apache/parquet-format/blob/master/src/main/thrift/parquet.thrift)
  The authoritative definition of the footer metadata, including the optional `Statistics` and `ColumnMetaData` structures. Use for: settling exactly which statistics a writer may record and that every one of them is optional.
- [Docs: "Parquet Files", DuckDB](https://duckdb.org/docs/stable/data/parquet/overview)
  How DuckDB reads Parquet directly, including projection and filter pushdown and the metadata functions that print a file's row groups and statistics. Use for: running the predict-then-run reps of stages 1 and 2 on a laptop, with no warehouse account.
- [Docs: "Database Page Layout", PostgreSQL](https://www.postgresql.org/docs/current/storage-page-layout.html)
  How a row store lays whole tuples onto 8 kB heap pages. Use for: the row-store side of the comparison in lesson 1, from a real engine rather than a diagram.
- [Course: "CMU 15-721 Advanced Database Systems", Andy Pavlo, Carnegie Mellon University (Spring 2024)](https://15721.courses.cs.cmu.edu/spring2024/)
  Lecture videos, slides and reading list on analytical database internals: storage formats, vectorized and compiled execution, and dedicated lectures on systems such as BigQuery, Snowflake and Redshift. Use for: going deeper on any stage 1 or 2 mechanism than a vendor document will.
- [Docs: "Encodings", Apache Parquet](https://parquet.apache.org/docs/file-format/data-pages/encodings/)
  Every Parquet encoding, the types each applies to, and the fallback from dictionary to plain encoding. Use for: the exact encoding names a Parquet file reports.
- [Docs: "Compression encodings", Amazon Redshift](https://docs.aws.amazon.com/redshift/latest/dg/c_Compression_encodings.html)
  `ENCODE AUTO`, the default encoding per data type, and each encoding Redshift offers. Use for: choosing or auditing column encodings on Redshift.
- [Blog: "Inside Capacitor, BigQuery's next-generation columnar storage format", Google Cloud](https://cloud.google.com/blog/products/bigquery/inside-capacitor-bigquerys-next-generation-columnar-storage-format)
  How BigQuery's storage format reorders rows to lengthen runs before encoding them. Use for: how BigQuery applies encodings it does not let you choose.

### Platform architecture

- [Paper: "Dremel: Interactive Analysis of Web-Scale Datasets", Melnik et al., VLDB (2010)](https://www.vldb.org/pvldb/vol3/R29.pdf)
  The paper behind BigQuery's execution engine and its nested columnar encoding of repeated and optional fields. Use for: why BigQuery stores nested data as columns, and the serving-tree execution model.
- [Paper: "Dremel: A Decade of Interactive SQL Analysis at Web Scale", Melnik et al., VLDB (2020)](https://www.vldb.org/pvldb/vol13/p3461-melnik.pdf)
  The authors' retrospective on what changed as Dremel became BigQuery: disaggregated storage, compute and shuffle, and in situ analysis. Use for: the primary account of BigQuery's storage and compute separation.
- [Paper: "Amazon Redshift Re-invented", Armenatzoglou et al., SIGMOD (2022)](https://www.amazon.science/publications/amazon-redshift-re-invented)
  How Redshift moved from shared-nothing local disks to managed storage on S3, with code generation, automatic table optimization and serverless compute. Use for: Redshift's architecture from its own engineers, and why a provisioned cluster still behaves differently from BigQuery or Snowflake.
- [Docs: "Key concepts and architecture", Snowflake](https://docs.snowflake.com/en/user-guide/intro-key-concepts)
  Snowflake's three layers: database storage, query processing in virtual warehouses, and cloud services. Use for: what Snowflake separates and what each layer bills.
- [Docs: "BigQuery storage overview", Google Cloud](https://cloud.google.com/bigquery/docs/storage_overview)
  How BigQuery stores tables in its columnar format on distributed storage, apart from the compute that queries them. Use for: the storage half of BigQuery's separation.
- [Docs: "Understand slots", Google Cloud](https://cloud.google.com/bigquery/docs/slots)
  What a slot is, how the scheduler shares slots across a query's stages and across concurrent queries, and fair scheduling within a reservation. Use for: sizing and isolating BigQuery compute.
- [Docs: "Introduction to BigQuery editions", Google Cloud](https://cloud.google.com/bigquery/docs/editions-intro)
  Reservations, baseline and autoscaling slots, and what each edition includes. Use for: capacity-based compute on BigQuery.
- [Docs: "Overview of warehouses", Snowflake](https://docs.snowflake.com/en/user-guide/warehouses-overview)
  Virtual warehouse sizes, the credit rate of each, auto-suspend and auto-resume. Use for: sizing Snowflake compute.
- [Docs: "Multi-cluster warehouses", Snowflake](https://docs.snowflake.com/en/user-guide/warehouses-multicluster)
  How a warehouse adds clusters under concurrency, the scaling policies, and how the extra clusters bill. Use for: concurrency on Snowflake, as distinct from making one query faster.
- [Docs: "Amazon Redshift provisioned clusters", AWS](https://docs.aws.amazon.com/redshift/latest/mgmt/working-with-clusters.html)
  Node types, including RA3 nodes with managed storage, and how a cluster's size is set. Use for: Redshift provisioned compute and what RA3 separates.
- [Docs: "Workload management", Amazon Redshift](https://docs.aws.amazon.com/redshift/latest/dg/cm-c-implementing-workload-management.html)
  Automatic and manual WLM queues, query priorities and concurrency scaling. Use for: workload isolation on a provisioned Redshift cluster.
- [Docs: "Warehouse considerations", Snowflake](https://docs.snowflake.com/en/user-guide/warehouses-considerations)
  How to size a warehouse and set auto-suspend to the gaps in a workload, and that each warehouse keeps a local cache of table data that suspending or resizing drops. Use for: the trade between cache warmth and idle credits.
- [Docs: "Concurrency scaling", Amazon Redshift](https://docs.aws.amazon.com/redshift/latest/dg/concurrency-scaling.html)
  Which queries can run on transient extra clusters and how that capacity is billed only while it runs queries. Use for: scaling a provisioned Redshift cluster out under concurrency.
- [Docs: "Compute capacity for Amazon Redshift Serverless", AWS](https://docs.aws.amazon.com/redshift/latest/mgmt/serverless-capacity.html)
  What an RPU is, base capacity and its default, and the steps it can be set in. Use for: sizing Redshift Serverless.
- [Docs: "Billing for on-demand compute capacity", AWS](https://docs.aws.amazon.com/redshift/latest/mgmt/serverless-billing-on-demand.html)
  Base and maximum capacity, RPU-hour usage limits, and no compute charge while idle. Use for: capping Redshift Serverless.
- [Docs: "Amazon Redshift performance", AWS](https://docs.aws.amazon.com/redshift/latest/dg/c_challenges_achieving_high_performance_queries.html)
  The features behind Redshift query speed, including the result cache on the leader node and when a query uses it. Use for: Redshift caching.

### Physical design

- [Docs: "Introduction to partitioned tables", Google Cloud](https://cloud.google.com/bigquery/docs/partitioned-tables)
  Time-unit, ingestion-time and integer-range partitioning, partition limits, and requiring a partition filter. Use for: declared partitioning and pruning on BigQuery.
- [Docs: "Introduction to clustered tables", Google Cloud](https://cloud.google.com/bigquery/docs/clustered-tables)
  How clustering orders storage blocks, automatic reclustering, and why a clustered query's bytes estimate is an upper bound. Use for: clustering on BigQuery.
- [Docs: "Micro-partitions and data clustering", Snowflake](https://docs.snowflake.com/en/user-guide/tables-clustering-micropartitions)
  What a micro-partition holds, the metadata kept per column, pruning, and clustering depth. Use for: Snowflake's automatic partitioning and how to tell whether a table is well clustered.
- [Docs: "Clustering keys and clustered tables", Snowflake](https://docs.snowflake.com/en/user-guide/tables-clustering-keys)
  When a clustering key is worth defining, choosing one, and the credit cost of automatic clustering. Use for: deciding whether to cluster a Snowflake table at all.
- [Docs: "Sort keys", Amazon Redshift](https://docs.aws.amazon.com/redshift/latest/dg/t_Sorting_data.html)
  Compound and interleaved sort keys, zone maps, and automatic sort key selection. Use for: Redshift's clustering mechanism.
- [Docs: "Data distribution for query optimization", Amazon Redshift](https://docs.aws.amazon.com/redshift/latest/dg/t_Distributing_data.html)
  The `AUTO`, `EVEN`, `KEY` and `ALL` distribution styles and how they decide whether a join has to redistribute rows. Use for: distribution and join cost.
- [Docs: "Choose the best distribution style", Amazon Redshift](https://docs.aws.amazon.com/redshift/latest/dg/c_best-practices-best-dist-key.html)
  The guidance on co-locating joined tables and avoiding skew. Use for: choosing a distribution key.
- [Docs: "Columnar storage", Amazon Redshift](https://docs.aws.amazon.com/redshift/latest/dg/c_columnar_storage_disk_mem_mgmnt.html)
  Redshift's own comparison of row-wise and column-wise block storage, with the I/O saved for an analytical query. Use for: the row against column argument as one vendor states it.
- [Docs: "Optimize query computation", Google Cloud](https://cloud.google.com/bigquery/docs/best-practices-performance-compute)
  BigQuery's performance guidance: reducing data processed, join patterns, and the cases where denormalizing or nesting helps. Use for: the row-store habits that change on BigQuery.
- [Docs: "Use nested and repeated fields", Google Cloud](https://cloud.google.com/bigquery/docs/nested-repeated)
  `STRUCT` and `ARRAY` columns and when to model with them instead of joins. Use for: nesting as a schema shape in stage 5.
- [Docs: "Query design best practices", Amazon Redshift](https://docs.aws.amazon.com/redshift/latest/dg/c_designing-queries-best-practices.html)
  Redshift's query guidance, including avoiding `SELECT *` and filtering on sort key columns. Use for: the row-store habits that change on Redshift.
- [Docs: "Query partitioned tables", Google Cloud](https://cloud.google.com/bigquery/docs/querying-partitioned-tables)
  Which filters prune partitions and which do not, and the error a missing required partition filter raises. Use for: debugging a filter that does not prune.
- [Docs: "Automatic Clustering", Snowflake](https://docs.snowflake.com/en/user-guide/tables-auto-reclustering)
  How Snowflake keeps a clustered table ordered with serverless compute, and the credit and storage cost of doing so. Use for: what a clustering key costs to keep.
- [Docs: "Distribution styles", Amazon Redshift](https://docs.aws.amazon.com/redshift/latest/dg/c_choosing_dist_sort.html)
  The exact definitions of `AUTO`, `EVEN`, `KEY` and `ALL`. Use for: settling what each distribution style does.
- [Docs: "Evaluating the query plan", Amazon Redshift](https://docs.aws.amazon.com/redshift/latest/dg/c_data_redistribution.html)
  The `DS_DIST_*` and `DS_BCAST_*` labels in a plan and which of them signal costly data movement. Use for: reading a join's movement in `EXPLAIN`.
- [Docs: "Interleaved sort key", Amazon Redshift](https://docs.aws.amazon.com/redshift/latest/dg/t_Sorting_data-interleaved.html)
  When an interleaved sort key helps, why monotonically increasing columns suit it badly, and `VACUUM REINDEX`. Use for: compound against interleaved.
- [Docs: "External tables for Redshift Spectrum", Amazon Redshift](https://docs.aws.amazon.com/redshift/latest/dg/c-spectrum-external-tables.html)
  Partitioned external tables over S3 prefixes and adding partitions to them. Use for: declared partitioning on Redshift, which only external tables have.
- [Docs: "Query plan and timeline", Google Cloud](https://cloud.google.com/bigquery/docs/query-plan-explanation)
  Reading a BigQuery query's stages, broadcast against hash joins, and skew shown as maximum against average compute. Use for: seeing which join strategy BigQuery chose.

### Dimensional modelling

- [Docs: "Dimensional Modeling Techniques", Kimball Group](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/)
  The Kimball Group's own index of dimensional modelling techniques, from the four-step design process to every slowly changing dimension type. Use for: settling what a modelling term means from the people who named it.
- [Docs: "Four-Step Dimensional Design Process", Kimball Group](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/four-4-step-design-process/)
  Select the business process, declare the grain, identify the dimensions, identify the facts. Use for: the order a model is designed in.
- [Docs: "Declare the Grain", Kimball Group](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/grain/)
  Why the grain is declared before facts or dimensions, and why atomic grain is preferred. Use for: lesson 11.
- [Docs: "Type 2: Add New Row", Kimball Group](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/type-2/)
  The type 2 technique: a new dimension row per change, with effective dates and a current-row indicator. Use for: keeping a dimension's history.
- [Docs: "Snapshots", dbt](https://docs.getdbt.com/docs/build/snapshots)
  How dbt implements type 2 history over a mutable source, with the timestamp and check strategies. Use for: a concrete implementation of a slowly changing dimension in SQL.
- [Docs: "Data types", Google Cloud](https://docs.cloud.google.com/bigquery/docs/reference/standard-sql/data-types)
  BigQuery's data types, with the logical size of each that on-demand billing counts. Use for: predicting bytes billed for a schema choice.
- [Docs: "Use primary and foreign keys", Google Cloud](https://docs.cloud.google.com/bigquery/docs/primary-foreign-keys)
  BigQuery does not enforce these keys, and its optimizer uses them to remove or reorder joins. Use for: why a grain must be tested after every load.
- [Docs: "Table constraints", Amazon Redshift](https://docs.aws.amazon.com/redshift/latest/dg/t_Defining_constraints.html)
  Uniqueness, primary and foreign key constraints are informational, and the planner trusts them. Use for: the same point on Redshift.
- [Docs: "Table design considerations", Snowflake](https://docs.snowflake.com/en/user-guide/table-considerations)
  Which constraints standard tables enforce, and when a clustering key is worth considering. Use for: the same point on Snowflake.

### Loading

- [Docs: "Introduction to loading data", Google Cloud](https://cloud.google.com/bigquery/docs/loading-data)
  Batch loading, streaming and the Storage Write API, and the formats BigQuery loads. Use for: choosing a load method on BigQuery.
- [Docs: "Introduction to the BigQuery Storage Write API", Google Cloud](https://cloud.google.com/bigquery/docs/write-api)
  Committed, pending and buffered streams, and exactly-once delivery through stream offsets. Use for: streaming ingestion that does not duplicate rows.
- [Docs: "Preparing your data files", Snowflake](https://docs.snowflake.com/en/user-guide/data-load-considerations-prepare)
  File sizing for parallel loads and Snowpipe. Use for: why many small files or one huge file both load slowly.
- [Docs: "COPY INTO table", Snowflake](https://docs.snowflake.com/en/sql-reference/sql/copy-into-table)
  The batch load command, including the load metadata that skips files already loaded. Use for: rerunning a Snowflake batch load safely.
- [Docs: "Snowpipe", Snowflake](https://docs.snowflake.com/en/user-guide/data-load-snowpipe-intro)
  Continuous micro-batch loading from staged files, and how its load history prevents duplicate loads. Use for: micro-batch ingestion on Snowflake.
- [Docs: "Snowpipe Streaming", Snowflake](https://docs.snowflake.com/en/user-guide/snowpipe-streaming/data-load-snowpipe-streaming-overview)
  Row-level streaming ingestion through channels with offset tokens. Use for: streaming on Snowflake without staging files.
- [Docs: "COPY", Amazon Redshift](https://docs.aws.amazon.com/redshift/latest/dg/r_COPY.html)
  The batch load command from S3 and other sources. Use for: loading Redshift in parallel across slices.
- [Docs: "Amazon Redshift best practices for loading data", AWS](https://docs.aws.amazon.com/redshift/latest/dg/c_loading-data-best-practices.html)
  One COPY over many files, file counts as a multiple of slices, and loading in sort key order. Use for: batch load speed on Redshift.
- [Docs: "Streaming ingestion to a materialized view", Amazon Redshift](https://docs.aws.amazon.com/redshift/latest/dg/materialized-view-streaming-ingestion.html)
  Ingesting from Kinesis or Kafka into a materialized view without staging in S3. Use for: streaming on Redshift.
- [Docs: "MERGE", Snowflake](https://docs.snowflake.com/en/sql-reference/sql/merge)
  Upserting a batch into a target, and the nondeterministic-update error when a source matches a target row twice. Use for: idempotent merges.
- [Docs: "Data manipulation language (DML) statements", Google Cloud](https://cloud.google.com/bigquery/docs/reference/standard-sql/dml-syntax)
  BigQuery's `MERGE`, `UPDATE` and `DELETE`, including the rule that a target row may match at most one source row. Use for: idempotent merges on BigQuery.
- [Docs: "MERGE", Amazon Redshift](https://docs.aws.amazon.com/redshift/latest/dg/r_MERGE.html)
  Redshift's `MERGE` and its restrictions. Use for: idempotent merges on Redshift.
- [Docs: "Incremental models", dbt](https://docs.getdbt.com/docs/build/incremental-models)
  Transforming only new data on each run, with merge, delete+insert and insert-overwrite strategies. Use for: ELT that stays correct when a run is repeated.
- [Docs: "Batch loading data", Google Cloud](https://cloud.google.com/bigquery/docs/batch-loading-data)
  Load jobs, their write dispositions, preferred formats, and that a load job commits atomically. Use for: batch loading on BigQuery.
- [Docs: "Quotas and limits", Google Cloud](https://cloud.google.com/bigquery/quotas)
  Load job limits per table per day, per job, and per compressed file. Use for: sizing a BigQuery load schedule. Limits change, so read the current values.
- [Docs: "COPY JOB", Amazon Redshift](https://docs.aws.amazon.com/redshift/latest/dg/r_COPY-JOB.html)
  Automatic loading from S3 that tracks the files it has loaded. Use for: micro-batch on Redshift.
- [Docs: "Loading data", Snowflake](https://docs.snowflake.com/en/user-guide/data-load-considerations-load)
  How `COPY INTO` decides whether a file was already loaded, the load metadata window, and the options that override it. Use for: rerunning a Snowflake load without duplicating rows.
- [Docs: "Named Channels and exactly-once delivery", Snowflake](https://docs.snowflake.com/en/user-guide/snowpipe-streaming/snowpipe-streaming-channels)
  Channels, offset tokens and recovering the last committed offset after a restart. Use for: streaming into Snowflake without duplicates.

### Cost

- [Docs: "BigQuery pricing", Google Cloud](https://cloud.google.com/bigquery/pricing)
  On-demand bytes-processed pricing, capacity pricing by edition, and storage pricing. Use for: what BigQuery bills, checked for current prices.
- [Docs: "Run a query", Google Cloud](https://cloud.google.com/bigquery/docs/running-queries)
  Running queries, including dry runs that report the bytes a query would process. Use for: finding a BigQuery query's cost before it runs.
- [Docs: "JOBS view", Google Cloud](https://cloud.google.com/bigquery/docs/information-schema-jobs)
  `INFORMATION_SCHEMA.JOBS` and its bytes billed and slot-milliseconds columns. Use for: reading a project's bill one query at a time.
- [Docs: "Optimize query cost", Google Cloud](https://cloud.google.com/bigquery/docs/best-practices-costs)
  Why `LIMIT` does not reduce bytes billed, previewing data for free, and capping bytes billed per query. Use for: cutting on-demand cost.
- [Docs: "Introduction to materialized views", Google Cloud](https://cloud.google.com/bigquery/docs/materialized-views-intro)
  Precomputed, incrementally refreshed results and automatic query rewriting. Use for: paying for an aggregation once instead of per query.
- [Docs: "Understanding compute cost", Snowflake](https://docs.snowflake.com/en/user-guide/cost-understanding-compute)
  Credits per second by warehouse size, the 60-second minimum on resume, and serverless and cloud services credits. Use for: what Snowflake bills.
- [Docs: "Working with resource monitors", Snowflake](https://docs.snowflake.com/en/user-guide/resource-monitors)
  Credit quotas with notify and suspend actions. Use for: capping a Snowflake bill.
- [Docs: "Using persisted query results", Snowflake](https://docs.snowflake.com/en/user-guide/querying-persisted-results)
  The result cache and the conditions under which a repeated query reuses it without running a warehouse. Use for: why an identical query can cost nothing.
- [Docs: "Working with materialized views", Snowflake](https://docs.snowflake.com/en/user-guide/views-materialized)
  Snowflake's background-maintained materialized views and their serverless maintenance cost. Use for: the cost side of precomputing.
- [Docs: "Materialized views in Amazon Redshift", AWS](https://docs.aws.amazon.com/redshift/latest/dg/materialized-view-overview.html)
  Redshift materialized views, incremental refresh and automatic query rewriting. Use for: precomputing on Redshift.
- [Docs: "Billing for Amazon Redshift Serverless", AWS](https://docs.aws.amazon.com/redshift/latest/mgmt/serverless-billing.html)
  RPU-hours, the per-second billing with a 60-second minimum, base capacity and usage limits. Use for: what Redshift Serverless bills and how to cap it.
- [Docs: "Use cached query results", Google Cloud](https://cloud.google.com/bigquery/docs/cached-results)
  How long BigQuery keeps cached results, when a query skips the cache, and that a cache hit is not charged. Use for: the result cache as a cost lever.
- [Docs: "Understanding storage cost", Snowflake](https://docs.snowflake.com/en/user-guide/cost-understanding-data-storage)
  What Snowflake bills for storage, including Time Travel and Fail-safe. Use for: the storage side of a Snowflake bill.
- [Docs: "QUERY_ATTRIBUTION_HISTORY view", Snowflake](https://docs.snowflake.com/en/sql-reference/account-usage/query_attribution_history)
  Credits attributed to each query, excluding warehouse idle time. Use for: finding the idle share of a Snowflake bill.

### Lakehouse and changing shared models

- [Paper: "Lakehouse: A New Generation of Open Platforms that Unify Data Warehousing and Advanced Analytics", Armbrust, Ghodsi, Xin and Zaharia, CIDR (2021)](https://www.cidrdb.org/cidr2021/papers/cidr2021_paper17.pdf)
  The argument for a lakehouse from its proponents: open formats in object storage with a metadata layer adding transactions. Use for: the lakehouse case in its own words, to weigh against the warehouse.
- [Paper: "Delta Lake: High-Performance ACID Table Storage over Cloud Object Stores", Armbrust et al., VLDB (2020)](https://www.vldb.org/pvldb/vol13/p3411-armbrust.pdf)
  How a transaction log over Parquet files gives a table atomic commits on object storage. Use for: what a table format actually adds to a pile of files.
- [Docs: "Iceberg Table Spec", Apache Iceberg](https://iceberg.apache.org/spec/)
  The specification of snapshots, manifests, hidden partitioning and schema evolution by field ID. Use for: settling what a table format guarantees from the primary source.
- [Docs: "Introduction to views", Google Cloud](https://cloud.google.com/bigquery/docs/views-intro)
  Logical views and authorized views. Use for: putting a stable interface in front of a table whose physical layout will change.
- [Docs: "Model contracts", dbt](https://docs.getdbt.com/docs/mesh/govern/model-contracts)
  Declaring a model's columns and types so a build fails before a breaking change ships. Use for: changing a model others query without breaking them.

## Gaps

- No vendor-neutral, primary source compares the three platforms' prices for the same workload. Each pricing page is authoritative for its own platform only, and published comparisons are written by vendors or by firms selling one of them. Lessons 16 and 19 teach the shape of each bill from each vendor's own page and leave the comparison to the reader's own workload.
- Snowflake's architecture paper ("The Snowflake Elastic Data Warehouse", SIGMOD 2016) is not listed because no stable, freely readable copy was found. The Snowflake documentation above covers what the lessons use from it.
