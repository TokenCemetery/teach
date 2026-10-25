---
title: Cost Model
description: What each pricing model charges for, how to read a query's cost, and the controls that cap a bill
type: reference
---

# Cost Model

Stage 7 compressed for lookup. [Lesson 16](../lessons/0016-how-a-warehouse-bills.md) covers what each platform bills and which workload each model rewards, and [lesson 17](../lessons/0017-reading-and-cutting-a-querys-cost.md) covers reading a query's cost and cutting it. No price amounts appear here, only what is billed and in what unit. Every value names the documentation page it came from; units and minimums change between releases, so check that page before you rely on one.

## Two meters

| Model | Bills | Idle compute | Reading more bytes | Rewards |
|---|---|---|---|---|
| On-demand pricing | What each query reads | Free | Costs more, linearly | Spiky, ad-hoc work that is quiet most hours |
| Capacity pricing | Compute held over time | Costs the same as busy | Free at the margin; the query runs longer | Steady work that keeps compute busy most hours |

## Compute: what is billed, in what unit

| Platform and model | Unit | Billing grain and minimum | Source |
|---|---|---|---|
| BigQuery on demand | Bytes processed, per TiB | Rounded up to the nearest MB; minimum 10 MB per table referenced and 10 MB per query; a monthly free allowance | "BigQuery pricing" |
| BigQuery editions (capacity) | Slot-hours | Per second, one-minute minimum by default; fluid scaling, opted into per reservation, removes the minimum; autoscaling adds slots in multiples of 50 | "BigQuery pricing" |
| BigQuery slot commitments | Slots for one or three years | 50-slot minimum, increments of 50; Enterprise and Enterprise Plus editions | "BigQuery pricing" |
| Snowflake virtual warehouse | Credits per hour, by size; X-Small is 1 and each size up roughly doubles | Per second, 60-second minimum on every start or resume; resizing up bills one minute of the added compute | "Understanding compute cost", "Overview of warehouses" |
| Snowflake multi-cluster warehouse | Credits per running cluster | Size rate times clusters running | "Overview of warehouses" |
| Snowflake serverless features | Compute-hours converted to credits | Per second, rounded up to the whole second | "Understanding compute cost" |
| Snowflake cloud services | Credits | Billed only for daily usage above 10% of that day's warehouse credits | "Understanding compute cost" |
| Redshift provisioned | Node-hours | Every node, for as long as the cluster exists; a paused cluster bills only backup storage | "Amazon Redshift provisioned clusters" |
| Redshift Serverless | RPU-hours | Per second while queries run, 60-second minimum; cancelled queries bill the time they ran | "Billing for Amazon Redshift Serverless" |
| Redshift Spectrum, from a provisioned cluster | Bytes scanned in S3 | On demand; on Serverless the same queries bill RPU time instead | "Billing for Amazon Redshift Serverless" |

What keeps billing when nobody is querying:

- A Snowflake warehouse until auto-suspend fires, plus a fresh 60-second minimum on every resume.
- A provisioned Redshift cluster, always, until it is paused.
- Redshift Serverless while a transaction is left open, or while a connection pool sends health-check queries.
- A BigQuery reservation's baseline slots, and commitments for their whole term.

## Storage

| Platform | Unit | What counts | Source |
|---|---|---|---|
| BigQuery | Per GiB per month, prorated per MiB per second | Active, or long-term after 90 consecutive days unmodified (per partition, same performance). Per dataset: logical (uncompressed) bytes with time travel and fail-safe free, or physical (compressed) bytes with them billed | "BigQuery pricing" |
| Snowflake | Flat rate per TB per month | Compressed table data, Time Travel and Fail-safe history, staged files; transient and temporary tables have no Fail-safe | "Understanding storage cost" |
| Redshift | Redshift Managed Storage per GB-month | RA3 and Serverless table data; manual snapshots billed separately; Serverless recovery points under 24 hours are free | "Billing for Amazon Redshift Serverless" |

Modifying a BigQuery table or partition, by load, DML or overwrite, resets its 90-day long-term clock. Querying, exporting and copying from it do not.

## Reading a query's cost

### Before it runs

| Platform | Tool | Returns | Caveat |
|---|---|---|---|
| BigQuery | Dry run: console validator, `bq query --dry_run`, API `dryRun` | Bytes the query would process; free, uses no slots | Upper bound on clustered tables; always 0 bytes on tables with row-level security; under capacity pricing no exact per-query price exists |
| Snowflake | `EXPLAIN` | The plan, including partitions it expects to scan | No price; cost is warehouse time |
| Redshift | `EXPLAIN` | The plan, joins and redistribution steps | No price; cost is cluster or RPU time |

### After it ran

| Platform | Where | Columns or fields | Source |
|---|---|---|---|
| BigQuery | `INFORMATION_SCHEMA.JOBS` (180 days) | `total_bytes_billed` (on-demand projects only), `total_bytes_processed`, `total_slot_ms`, `cache_hit` | "JOBS view" |
| Snowflake | Query profile in Snowsight | Bytes scanned, partitions scanned against partitions total, spill | "Monitor query activity with Query History" |
| Snowflake | `ACCOUNT_USAGE.QUERY_HISTORY` | `bytes_scanned`, `partitions_scanned`, `partitions_total`, `percentage_scanned_from_cache`, `bytes_spilled_to_remote_storage` | "QUERY_HISTORY view" |
| Snowflake | `ACCOUNT_USAGE.QUERY_ATTRIBUTION_HISTORY` (365 days, latency up to 8 hours) | `credits_attributed_compute`; excludes idle time and queries of about 100 ms or less | "QUERY_ATTRIBUTION_HISTORY view" |
| Snowflake | `ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY` (365 days, latency up to 3 hours) | `credits_used`, `credits_used_compute`, `credits_used_cloud_services` per warehouse per hour, idle included | "WAREHOUSE_METERING_HISTORY view" |
| Redshift Serverless | `SYS_SERVERLESS_USAGE` | `charged_seconds` (RPU-seconds billed) and `compute_seconds` per one-minute interval | "Billing for on-demand compute capacity" |

Metered credits minus the sum of attributed query credits is a Snowflake warehouse's idle cost.

## Cutting a query's cost without changing its answer

| Lever | Why it works | Watch for |
|---|---|---|
| Name only the needed columns | A column store reads referenced columns only | `SELECT *` on a wide table is the largest single waste |
| Filter the partitioning column with a half-open range | Whole partitions are pruned | A function wrapped around the column scans everything; BigQuery's `require_partition_filter` turns that into an error |
| Filter on the clustering or sort key | More blocks skipped by their min and max | Shows as bytes billed below the dry run estimate |
| Aggregate in SQL | Fewer bytes leave the warehouse to be summed elsewhere | The scan is unchanged, so pair it with the levers above |
| Result cache | Identical query over unchanged tables returns a stored result | BigQuery: about 24 hours, any text change misses, no charge on a hit. Snowflake: 24 hours renewed per reuse up to 31 days, exact text match |
| Materialized view or pre-aggregated table | The aggregation is paid once and read many times | Costs storage and maintenance; pays off only when read far more often than its base data changes |
| Not `LIMIT` | Trims rows after the scan | Cuts bytes only on a BigQuery clustered table |

Cache misses on both platforms: changed underlying data, nondeterministic functions (`CURRENT_TIMESTAMP()` on BigQuery, `RANDOM()` or `UUID_STRING()` on Snowflake), and a different role or privileges on Snowflake. BigQuery also skips the cache when a destination table is set or the table has recent streaming inserts.

## Materialized views per platform

| Platform | Maintenance | Query rewrite | Cost | Source |
|---|---|---|---|---|
| BigQuery | Incremental views take base-table changes automatically; non-incremental views rerun the full query on each refresh | Smart tuning reroutes queries to incremental views | Storage plus refresh; reads honour maximum bytes billed | "Introduction to materialized views" |
| Snowflake | A background service keeps the view current; requires Enterprise Edition | Not covered in the source used here | Storage plus serverless maintenance credits | "Working with materialized views" |
| Redshift | Manual `REFRESH MATERIALIZED VIEW`, auto refresh, or a schedule | Automatic rewrite when the view is up to date | Storage plus the compute the refresh uses | "Materialized views in Amazon Redshift" |

## Controls that cap a bill

| Platform | Control | Scope | What happens at the limit | Source |
|---|---|---|---|---|
| BigQuery on demand | Maximum bytes billed | One query or job | The query fails before running, with no charge | "Optimize query cost" |
| BigQuery on demand | Custom query quotas | Bytes per day, per project or per user | Further queries are refused until the next day | "Optimize query cost" |
| BigQuery editions | Reservation maximum slots | One reservation | Queries queue or slow; spend cannot exceed the maximum | "Optimize query cost" |
| Any Google Cloud project | Cloud Billing budgets | Billing account or project | Alert only; does not stop spend | "Optimize query cost" |
| Snowflake | Auto-suspend | One warehouse | Suspends after the set idle period; set it to the workload's real gaps | "Overview of warehouses" |
| Snowflake | Resource monitor | Account, or a set of warehouses; resets daily, weekly, monthly, yearly or never | Notify, Notify and Suspend (after running statements), or Notify and Suspend Immediately (cancels them), at a percentage of the credit quota; warehouses only, not serverless features | "Working with resource monitors" |
| Snowflake | Budgets | Serverless features and other spend a resource monitor misses | Alert | "Working with resource monitors" |
| Redshift Serverless | Max capacity | One workgroup | Scaling stops at that RPU count; work slows instead of costing more | "Billing for on-demand compute capacity" |
| Redshift Serverless | Usage limit, maximum RPU-hours | One workgroup; daily, weekly or monthly | Log, alert, or turn off user queries | "Billing for on-demand compute capacity" |
| Redshift provisioned | Usage limit | Concurrency scaling in minutes, Spectrum in TB scanned; daily, weekly or monthly | Log, emit a metric, or disable the feature until the next period | "CreateUsageLimit" |
| Redshift provisioned | Pause | One cluster | Compute billing stops; storage continues | "Amazon Redshift provisioned clusters" |

## Sources

- [Docs: "BigQuery pricing", Google Cloud](https://cloud.google.com/bigquery/pricing)
- [Docs: "Introduction to BigQuery editions", Google Cloud](https://cloud.google.com/bigquery/docs/editions-intro)
- [Docs: "Run a query", Google Cloud](https://cloud.google.com/bigquery/docs/running-queries)
- [Docs: "JOBS view", Google Cloud](https://cloud.google.com/bigquery/docs/information-schema-jobs)
- [Docs: "Optimize query cost", Google Cloud](https://cloud.google.com/bigquery/docs/best-practices-costs)
- [Docs: "Use cached query results", Google Cloud](https://cloud.google.com/bigquery/docs/cached-results)
- [Docs: "Introduction to materialized views", Google Cloud](https://cloud.google.com/bigquery/docs/materialized-views-intro)
- [Docs: "Understanding compute cost", Snowflake](https://docs.snowflake.com/en/user-guide/cost-understanding-compute)
- [Docs: "Overview of warehouses", Snowflake](https://docs.snowflake.com/en/user-guide/warehouses-overview)
- [Docs: "Understanding storage cost", Snowflake](https://docs.snowflake.com/en/user-guide/cost-understanding-data-storage)
- [Docs: "Using persisted query results", Snowflake](https://docs.snowflake.com/en/user-guide/querying-persisted-results)
- [Docs: "Working with materialized views", Snowflake](https://docs.snowflake.com/en/user-guide/views-materialized)
- [Docs: "Working with resource monitors", Snowflake](https://docs.snowflake.com/en/user-guide/resource-monitors)
- [Docs: "Monitor query activity with Query History", Snowflake](https://docs.snowflake.com/en/user-guide/ui-snowsight-activity)
- [Docs: "QUERY_HISTORY view", Snowflake](https://docs.snowflake.com/en/sql-reference/account-usage/query_history)
- [Docs: "QUERY_ATTRIBUTION_HISTORY view", Snowflake](https://docs.snowflake.com/en/sql-reference/account-usage/query_attribution_history)
- [Docs: "WAREHOUSE_METERING_HISTORY view", Snowflake](https://docs.snowflake.com/en/sql-reference/account-usage/warehouse_metering_history)
- [Docs: "Amazon Redshift provisioned clusters", AWS](https://docs.aws.amazon.com/redshift/latest/mgmt/working-with-clusters.html)
- [Docs: "Billing for Amazon Redshift Serverless", AWS](https://docs.aws.amazon.com/redshift/latest/mgmt/serverless-billing.html)
- [Docs: "Billing for on-demand compute capacity", AWS](https://docs.aws.amazon.com/redshift/latest/mgmt/serverless-billing-on-demand.html)
- [Docs: "CreateUsageLimit", Amazon Redshift API Reference](https://docs.aws.amazon.com/redshift/latest/APIReference/API_CreateUsageLimit.html)
- [Docs: "Materialized views in Amazon Redshift", AWS](https://docs.aws.amazon.com/redshift/latest/dg/materialized-view-overview.html)
- [Resources](../RESOURCES.md)
