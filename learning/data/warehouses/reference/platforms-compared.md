---
title: Platforms Compared
description: How BigQuery, Snowflake and Redshift name and bill the same storage and compute ideas
type: reference
---

# Platforms Compared

Stage 3 compressed for lookup. [Lesson 5](../lessons/0005-separating-storage-from-compute.md) covers what each platform separates and [lesson 6](../lessons/0006-compute-sizing-concurrency-and-isolation.md) covers sizing, concurrency and isolation; the pruning and clustering rows preview stage 4. Every value names the documentation page it came from. Defaults, limits and rates move between releases, so check that page before you rely on a number. No price amounts appear here, only what is billed and in what unit.

## At a glance

| Idea | BigQuery | Snowflake | Redshift |
|---|---|---|---|
| Storage unit | Columnar table storage (Capacitor on Colossus), managed by BigQuery | Micro-partition, 50 to 500 MB uncompressed, in cloud object storage | 1 MB column block; on RA3, RG and Serverless held in Redshift Managed Storage on S3 |
| Compute unit | Slot | Virtual warehouse, of a size, with one or more clusters | Node (provisioned) or RPU (Serverless) |
| Scale up | More slots in the reservation | Larger warehouse size | More or larger nodes; higher base RPUs |
| Scale out | Autoscaling slots; the scheduler grants slots per stage | Multi-cluster warehouse | Concurrency scaling |
| Isolation | Reservations and assignments | Separate virtual warehouses | WLM queues and priorities; separate clusters or workgroups |
| Pruning metadata | Partition boundaries and per-block metadata | Per-column value ranges and distinct counts per micro-partition | Zone maps: min and max per block |
| Clustering mechanism | Clustered columns, up to four | Clustering key, maintained by automatic clustering | Sort key, compound or interleaved, or `AUTO` |
| Caching | Query results cache | Result cache, plus warehouse local disk cache | Leader-node result cache, plus local SSD tier |
| Compute billing unit | Bytes processed (on-demand) or slot-hours (capacity) | Credits per second a cluster runs | Node-hours (provisioned) or RPU-hours (Serverless) |
| Storage billing unit | Per GiB per month, logical or physical bytes | Flat rate per TB per month, compressed size | Managed storage per GB per month |

## Storage unit

| Platform | What it is | Source |
|---|---|---|
| BigQuery | Tables stored in columnar format, each column separately, replicated across zones, apart from compute. The format is Capacitor and the file system Colossus | "BigQuery storage overview"; Dremel 2020 paper, sections 3.1 and 6 |
| Snowflake | Loaded data reorganized into a compressed columnar format in cloud storage, divided automatically into micro-partitions of 50 to 500 MB uncompressed | "Key concepts and architecture"; "Micro-partitions and data clustering" |
| Redshift | Columnar data in 1 MB blocks. DC2 keeps them on local NVMe SSD; RA3, RG and Serverless persist every commit to Redshift Managed Storage on S3 and cache on local SSD | "Sort keys"; "Amazon Redshift provisioned clusters"; Redshift Re-invented, section 3 |

## Compute unit

| Platform | Unit | Detail | Source |
|---|---|---|---|
| BigQuery | Slot | A virtual compute unit; you cannot set a query's slot count | "Understand slots" |
| Snowflake | Virtual warehouse | An independent cluster that shares no compute with other warehouses; size sets compute per cluster, and credits per hour double with each size step | "Key concepts and architecture"; "Overview of warehouses" |
| Redshift provisioned | Node | A leader node plus compute nodes; node type sets CPU, memory and storage per node | "Amazon Redshift provisioned clusters" |
| Redshift Serverless | RPU | One Redshift Processing Unit provides 16 GB of memory | "Compute capacity for Amazon Redshift Serverless" |

## Scaling knob

| Platform | Up: one query faster | Out: more queries at once | Source |
|---|---|---|---|
| BigQuery | Larger reservation baseline or maximum | Autoscaling slots, added in multiples of 50 after baseline and idle slots are used | "Understand slots"; "Introduction to BigQuery editions" |
| Snowflake | Resize the warehouse; applies to queued and new queries, not running ones | Multi-cluster warehouse (Enterprise Edition), maximized or auto-scale, Standard or Economy policy | "Overview of warehouses"; "Multi-cluster warehouses" |
| Redshift provisioned | Add nodes or change node type; on RA3 a resize is a metadata operation | Concurrency scaling clusters, per WLM queue | "Amazon Redshift provisioned clusters"; "Concurrency scaling"; Redshift Re-invented, section 3 |
| Redshift Serverless | Base capacity in RPUs, default 128 | Automatic scaling above base, capped by max capacity | "Compute capacity for Amazon Redshift Serverless"; "Billing for on-demand compute capacity" |

## Isolation mechanism

| Platform | Mechanism | Detail | Source |
|---|---|---|---|
| BigQuery | Reservation plus assignment | Projects, or in Enterprise editions folders and organizations, are assigned to a reservation. Fair scheduling splits slots equally among projects, then queries. Idle slots are shared unless `ignore_idle_slots` is set | "Understand slots"; "Introduction to BigQuery editions" |
| Snowflake | Separate virtual warehouses | Each warehouse has no effect on another's performance | "Key concepts and architecture" |
| Redshift provisioned | WLM queues | Automatic WLM with up to eight queues and query priorities; manual WLM fixes memory and concurrency per queue | "Workload management" |
| Redshift, any | Separate compute over shared data | Another cluster or Serverless workgroup reading the same managed storage | Redshift Re-invented, section 3 |

## Pruning metadata

| Platform | Metadata | Source |
|---|---|---|
| BigQuery | Partition boundaries for partitioned tables; block metadata that a filter on clustered columns prunes against | "Introduction to partitioned tables"; "Introduction to clustered tables" |
| Snowflake | Per micro-partition: the range of values of each column and the number of distinct values | "Micro-partitions and data clustering" |
| Redshift | Zone maps: the min and max of each 1 MB block | "Sort keys" |

## Clustering mechanism

| Platform | Mechanism | Maintenance | Source |
|---|---|---|---|
| BigQuery | Clustered columns, up to four, sort storage blocks | Automatic reclustering, free | "Introduction to clustered tables" |
| Snowflake | Clustering key | Automatic clustering, which consumes credits | "Clustering keys and clustered tables" |
| Redshift | Sort key, compound (default) or interleaved (up to eight columns); `SORTKEY AUTO` recommended | Automatic table optimization chooses it when `AUTO` | "Sort keys" |

## Caching

| Platform | Cache | Behaviour | Source |
|---|---|---|---|
| BigQuery | Query results cache | About 24 hours, per user per project; a cache hit is not charged | "Using cached query results" |
| Snowflake | Persisted query results | Expire after 24 hours; each reuse resets that, up to 31 days | "Using persisted query results" |
| Snowflake | Warehouse local disk cache | Table data cached while the warehouse runs; dropped on suspend or when the warehouse shrinks | "Warehouse considerations" |
| Redshift | Result cache on the leader node | On by default; used only if tables are unmodified and the query matches | "Amazon Redshift performance" |
| Redshift | Local SSD tier of managed storage | Keeps each cluster's working set; rehydrated after a resize or restore | Redshift Re-invented, section 3 |

## Billing unit

| Platform | Compute | Storage | Source |
|---|---|---|---|
| BigQuery | On-demand: bytes processed, per TiB, rounded up to the MB, with a 10 MB minimum per table referenced and per query. Capacity: slot-hours, per second with a one-minute minimum | Per GiB per month, logical or physical bytes; a table or partition unmodified for 90 consecutive days drops to the long-term rate | "BigQuery pricing"; "Introduction to BigQuery editions" |
| Snowflake | Credits per second each cluster runs, with a 60-second minimum each start; cloud services billed only above 10% of daily warehouse use; serverless features billed separately | Flat rate per TB per month on compressed size | "Understanding compute cost"; "Overview of warehouses"; "Understanding storage cost" |
| Redshift provisioned | Node-hours by node type and count; a paused cluster bills only backup storage; concurrency scaling only while it runs queries | Managed storage per GB per month on RA3 and RG | "Amazon Redshift provisioned clusters"; "Concurrency scaling" |
| Redshift Serverless | RPU-hours, per second with a 60-second minimum, only while queries run | Managed storage per GB per month | "Billing for Amazon Redshift Serverless"; "Billing for on-demand compute capacity" |

## Traps worth checking

- Treating a Snowflake multi-cluster warehouse as a speed-up for one slow query. It adds concurrency; size adds speed.
- Assuming a bigger BigQuery reservation makes one project's queries faster when fair scheduling is splitting it among many projects.
- Setting a Snowflake auto-suspend to the minimum on a dashboard warehouse and then wondering why every query reads cold data.
- Reading a Redshift DC2 cluster's behaviour as RA3's: DC2 storage is the nodes' own disks, so more data means more nodes.
- Counting BigQuery baseline slots as free when idle. They are always charged.

## Sources

- [Docs: "BigQuery storage overview", Google Cloud](https://cloud.google.com/bigquery/docs/storage_overview)
- [Docs: "Understand slots", Google Cloud](https://cloud.google.com/bigquery/docs/slots)
- [Docs: "Introduction to BigQuery editions", Google Cloud](https://cloud.google.com/bigquery/docs/editions-intro)
- [Docs: "Introduction to partitioned tables", Google Cloud](https://cloud.google.com/bigquery/docs/partitioned-tables)
- [Docs: "Introduction to clustered tables", Google Cloud](https://cloud.google.com/bigquery/docs/clustered-tables)
- [Docs: "Using cached query results", Google Cloud](https://cloud.google.com/bigquery/docs/cached-results)
- [Docs: "BigQuery pricing", Google Cloud](https://cloud.google.com/bigquery/pricing)
- [Docs: "Key concepts and architecture", Snowflake](https://docs.snowflake.com/en/user-guide/intro-key-concepts)
- [Docs: "Overview of warehouses", Snowflake](https://docs.snowflake.com/en/user-guide/warehouses-overview)
- [Docs: "Multi-cluster warehouses", Snowflake](https://docs.snowflake.com/en/user-guide/warehouses-multicluster)
- [Docs: "Warehouse considerations", Snowflake](https://docs.snowflake.com/en/user-guide/warehouses-considerations)
- [Docs: "Micro-partitions and data clustering", Snowflake](https://docs.snowflake.com/en/user-guide/tables-clustering-micropartitions)
- [Docs: "Clustering keys and clustered tables", Snowflake](https://docs.snowflake.com/en/user-guide/tables-clustering-keys)
- [Docs: "Using persisted query results", Snowflake](https://docs.snowflake.com/en/user-guide/querying-persisted-results)
- [Docs: "Understanding compute cost", Snowflake](https://docs.snowflake.com/en/user-guide/cost-understanding-compute)
- [Docs: "Understanding storage cost", Snowflake](https://docs.snowflake.com/en/user-guide/cost-understanding-data-storage)
- [Docs: "Amazon Redshift provisioned clusters", AWS](https://docs.aws.amazon.com/redshift/latest/mgmt/working-with-clusters.html)
- [Docs: "Workload management", Amazon Redshift](https://docs.aws.amazon.com/redshift/latest/dg/cm-c-implementing-workload-management.html)
- [Docs: "Concurrency scaling", Amazon Redshift](https://docs.aws.amazon.com/redshift/latest/dg/concurrency-scaling.html)
- [Docs: "Sort keys", Amazon Redshift](https://docs.aws.amazon.com/redshift/latest/dg/t_Sorting_data.html)
- [Docs: "Amazon Redshift performance", Amazon Redshift](https://docs.aws.amazon.com/redshift/latest/dg/c_challenges_achieving_high_performance_queries.html)
- [Docs: "Compute capacity for Amazon Redshift Serverless", AWS](https://docs.aws.amazon.com/redshift/latest/mgmt/serverless-capacity.html)
- [Docs: "Billing for Amazon Redshift Serverless", AWS](https://docs.aws.amazon.com/redshift/latest/mgmt/serverless-billing.html)
- [Docs: "Billing for on-demand compute capacity", AWS](https://docs.aws.amazon.com/redshift/latest/mgmt/serverless-billing-on-demand.html)
- [Paper: "Dremel: A Decade of Interactive SQL Analysis at Web Scale", Melnik et al., VLDB (2020)](https://www.vldb.org/pvldb/vol13/p3461-melnik.pdf)
- [Paper: "Amazon Redshift Re-invented", Armenatzoglou et al., SIGMOD (2022)](https://www.amazon.science/publications/amazon-redshift-re-invented)
- [Resources](../RESOURCES.md)
