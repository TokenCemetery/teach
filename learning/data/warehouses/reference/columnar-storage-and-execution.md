---
title: Columnar Storage and Execution
description: row against column layout, the encodings, and what a column engine skips
type: reference
---

# Columnar Storage and Execution

Stages 1 and 2 compressed for lookup: [lesson 1](../lessons/0001-row-stores-and-column-stores.md) (row against column layout), [lesson 2](../lessons/0002-inside-a-columnar-file.md) (row groups, column chunks, statistics), [lesson 3](../lessons/0003-encoding-and-compression.md) (encodings and compression) and [lesson 4](../lessons/0004-vectorized-execution-and-late-materialization.md) (vectorized execution, late materialization, `SELECT *`).

Platform values below name the page they came from. Check that page for the current value.

## Which layout wins

| Query shape | Winner | Why |
|---|---|---|
| Fetch or update one whole row by key ([OLTP](../GLOSSARY.md)) | [Row store](../GLOSSARY.md) | The row sits together on one page: one fetch. A column store touches one place per column |
| Aggregate many rows over a few columns ([OLAP](../GLOSSARY.md)) | [Column store](../GLOSSARY.md) | Reads only the referenced columns, each compressed well |
| Insert rows one at a time, at high rate | Row store | A column store writes one place per column per row, so warehouses prefer batches |
| `SELECT *` over many rows | Neither by much | Every column is read either way; the column store still compresses better |

## Bytes a query reads

```text
bytes scanned ≈ (sum of the referenced columns' sizes) × (fraction of blocks not pruned)
```

| Table | Query | Column store reads | Row store reads |
|---|---|---|---|
| 200 equal columns, 1 TB | 3 columns, no filter | about 15 GB | 1 TB |
| same | 3 columns, filter that prunes 90 percent of blocks | about 1.5 GB | 1 TB without an index |
| same | `SELECT *`, no filter | 1 TB | 1 TB |

The ratio follows the fraction of columns referenced and the fraction of blocks pruned, never the number of rows returned. Redshift's own illustration: a query using 5 of 100 columns reads about 5 percent of the table ([Docs: "Columnar storage", Amazon Redshift](https://docs.aws.amazon.com/redshift/latest/dg/c_columnar_storage_disk_mem_mgmnt.html)).

## Inside a columnar file

| Level | What it is | What a reader does with it |
|---|---|---|
| File footer | Metadata written after the data: where every column chunk starts, plus statistics | Reads it first, to plan which chunks to fetch |
| [Row group](../GLOSSARY.md) | A horizontal slice of rows | The unit skipped as a whole when no chunk in it can match |
| [Column chunk](../GLOSSARY.md) | One column's values for one row group, encoded and compressed together | Fetches only the chunks of referenced columns |
| Statistics | Minimum, maximum and null count per chunk | Compares the filter against them to prune |

Layout from [Docs: "File Format", Apache Parquet](https://parquet.apache.org/docs/file-format/).

| Platform | Its version of the unit | Source |
|---|---|---|
| Parquet | Row group of column chunks, footer statistics | [Docs: "File Format", Apache Parquet](https://parquet.apache.org/docs/file-format/) |
| Snowflake | [Micro-partition](../GLOSSARY.md), 50 MB to 500 MB uncompressed, columns stored separately inside, per-column metadata | [Docs: "Micro-partitions and data clustering", Snowflake](https://docs.snowflake.com/en/user-guide/tables-clustering-micropartitions) |
| Redshift | 1 MB block per column, with a [zone map](../GLOSSARY.md) of its minimum and maximum | [Docs: "Columnar storage", Amazon Redshift](https://docs.aws.amazon.com/redshift/latest/dg/c_columnar_storage_disk_mem_mgmnt.html) |
| BigQuery | Each column stored separately in its own columnar format; block internals not documented | [Docs: "BigQuery storage overview", Google Cloud](https://cloud.google.com/bigquery/docs/storage_overview) |
| Postgres, for contrast | 8 kB heap page of whole rows | [Docs: "Database Page Layout", PostgreSQL](https://www.postgresql.org/docs/current/storage-page-layout.html) |

## The encodings

| Encoding | Stores | Suits | Fails on | Parquet | Redshift |
|---|---|---|---|---|---|
| [Dictionary encoding](../GLOSSARY.md) | Distinct values once, then a small integer code per row | Few distinct values: status, country, category | High cardinality: Parquet falls back to `PLAIN` | `RLE_DICTIONARY` | `BYTEDICT` (up to 256 values per block) |
| [Run-length encoding](../GLOSSARY.md) | A value and a count per run | Equal values next to each other, usually a sorted column | Unsorted data, where every run has length 1 | Inside the `RLE` hybrid | `RUNLENGTH` |
| Delta encoding | Differences between consecutive values | Integers and timestamps that change steadily: IDs, event times in order | Values that jump randomly | `DELTA_BINARY_PACKED` | `DELTA`, `DELTA32K` |
| Bit-packing | Each integer in only the bits the block's largest needs | Small integers, which the encodings above produce | Large or outlying values, which widen the whole block | Inside the `RLE` hybrid and delta blocks | `MOSTLY8`, `MOSTLY16`, `MOSTLY32` (a narrower width, outliers stored raw) |
| General-purpose codec | Byte-level compression over the encoded pages | Long free text, JSON, logs | Already-encoded or random data, where it adds little | Snappy, ZSTD and others, per column chunk | `ZSTD`, `LZO` |

Parquet names from [Docs: "Encodings", Apache Parquet](https://parquet.apache.org/docs/file-format/data-pages/encodings/). Redshift keywords from [Docs: "Compression encodings", Amazon Redshift](https://docs.aws.amazon.com/redshift/latest/dg/c_Compression_encodings.html), which also lists `AZ64` (Amazon's own encoding for numeric, date and time types), `TEXT255`, `TEXT32K` and `RAW`.

Encodings stack: dictionary codes are bit-packed or run-length encoded, deltas are bit-packed, and a codec runs last.

## Who chooses the encoding

| Platform | Control | Source |
|---|---|---|
| BigQuery | None; the format chooses, and reorders rows to lengthen runs | [Docs: "BigQuery storage overview", Google Cloud](https://cloud.google.com/bigquery/docs/storage_overview), [Blog: "Inside Capacitor, BigQuery's next-generation columnar storage format", Google Cloud](https://cloud.google.com/blog/products/bigquery/inside-capacitor-bigquerys-next-generation-columnar-storage-format) |
| Snowflake | None; chosen per column per micro-partition | [Docs: "Micro-partitions and data clustering", Snowflake](https://docs.snowflake.com/en/user-guide/tables-clustering-micropartitions) |
| Redshift | `ENCODE AUTO` by default. Naming an encoding on any column turns it off for the table, and then sort key, `BOOLEAN`, `REAL` and `DOUBLE PRECISION` columns default to `RAW`, other numerics and dates to `AZ64`, strings to `LZO` | [Docs: "Compression encodings", Amazon Redshift](https://docs.aws.amazon.com/redshift/latest/dg/c_Compression_encodings.html) |

## Sorting and compression

- Sorting creates runs and small deltas, so a sorted column shrinks, sometimes to almost nothing.
- Only the leading sort column gets perfect runs. Later sort columns are ordered only within each value of the one before.
- Columns uncorrelated with the sort order, such as a random measure, do not shrink at all.
- Redshift advises against `RUNLENGTH` on a sort key column: range-restricted scans work best when blocks hold similar row counts.
- Sorting also tightens each block's minimum and maximum, which is what [clustering keys](../GLOSSARY.md) and [sort keys](../GLOSSARY.md) are for in stage 4.

## Operating on compressed data

| Operation | Shortcut | Needs |
|---|---|---|
| `SUM`, `COUNT` over a run | Value × run length; run length | Run-length encoding |
| `WHERE col = 'x'` | Look up `'x'` once, compare integer codes | Dictionary encoding |
| `WHERE col < 'x'` | Compare codes directly | An order-preserving dictionary |
| String predicate scan on Redshift | SIMD-vectorized scan over the compressed values | `BYTEDICT` on `CHAR` or `VARCHAR` |

The survey reports compression alone rarely buys more than a factor of three, and operating on compressed data more than an order of magnitude on sorted columns ([Paper: Abadi et al., section 4.3](https://www.cs.umd.edu/~abadi/papers/abadi-column-stores.pdf)).

## Execution models

| Model | One call returns | Cost it carries | Where it is used |
|---|---|---|---|
| Volcano iterator, row at a time | One row | An indirect call and branch per row per operator | Classic row stores |
| [Vectorized execution](../GLOSSARY.md) | A vector of values from one column, about 1,000 in VectorWise, 2,048 in DuckDB | Calls fall by the vector size; tight loops allow SIMD | VectorWise, DuckDB, Redshift's scan layer |
| Compiled code | Generated code per query, no interpreted calls | Compilation time before the first row | Redshift, for joins and aggregation |

From [Paper: Abadi et al., section 4.1](https://www.cs.umd.edu/~abadi/papers/abadi-column-stores.pdf) and [Paper: "Amazon Redshift Re-invented", Armenatzoglou et al., SIGMOD (2022)](https://www.amazon.science/publications/amazon-redshift-re-invented), section 2.

## Early against late materialization

| | Early materialization | [Late materialization](../GLOSSARY.md) |
|---|---|---|
| When rows are built | Right after the scan | After filters and joins, for survivors only |
| Intermediate results | Rows | Position lists or bitmaps per column, intersected |
| Compressed data | Decoded at once | Stays encoded through the filters |
| Wins when | Predicates pass most rows, on many columns | Predicates are selective |

Late materialization saves decoding and row building. It does not save I/O: every block that might hold a survivor is still read for every referenced column.

## What `SELECT *` costs

1. **Bytes scanned:** every column's chunks in every block pruning could not skip.
2. **Decoding:** every surviving value of every column.
3. **Row building and transfer:** full-width rows for every survivor.

| Platform | What changes | Source |
|---|---|---|
| BigQuery | On-demand bills every referenced column, sized by data type, not compressed size. `LIMIT` does not reduce bytes read on an unclustered table. Use table preview to look at data, and `SELECT * EXCEPT (...)` to drop wide columns | [Docs: "Optimize query computation", Google Cloud](https://cloud.google.com/bigquery/docs/best-practices-performance-compute), [Docs: "BigQuery pricing", Google Cloud](https://cloud.google.com/bigquery/pricing) |
| Snowflake | Only referenced columns are scanned, so `SELECT *` scans them all and costs [virtual warehouse](../GLOSSARY.md) time | [Docs: "Micro-partitions and data clustering", Snowflake](https://docs.snowflake.com/en/user-guide/tables-clustering-micropartitions) |
| Redshift | "Avoid using `select *`. Include only the columns you specifically need." | [Docs: "Query design best practices", Amazon Redshift](https://docs.aws.amazon.com/redshift/latest/dg/c_designing-queries-best-practices.html) |

## Traps worth checking

- Expecting better compression to cut a BigQuery on-demand bill. It cuts time, not bytes billed; pruning cuts bytes billed.
- Expecting `LIMIT` to cut bytes scanned.
- Expecting a selective filter on an unsorted column to cut bytes scanned. Without pruning, every block is read; selectivity only saves work after the read.
- Run-length encoding chosen for a column that is not sorted.
- On Redshift, naming one column's encoding and silently turning off `ENCODE AUTO` for the rest.

## Try it locally

```sql
SELECT path_in_schema, encodings, stats_min, stats_max,
       total_uncompressed_size, total_compressed_size
FROM parquet_metadata('file.parquet');

EXPLAIN ANALYZE SELECT col_a, sum(col_b) FROM 'file.parquet' GROUP BY col_a;
```

The first prints each column chunk's encodings, statistics and sizes; the second prints the row groups scanned and the data read ([Docs: "Parquet Files", DuckDB](https://duckdb.org/docs/stable/data/parquet/overview)).

## Sources

- [Paper: "The Design and Implementation of Modern Column-Oriented Database Systems", Abadi, Boncz, Harizopoulos, Idreos and Madden, Foundations and Trends in Databases (2013)](https://www.cs.umd.edu/~abadi/papers/abadi-column-stores.pdf)
- [Docs: "File Format", Apache Parquet](https://parquet.apache.org/docs/file-format/)
- [Docs: "Parquet Files", DuckDB](https://duckdb.org/docs/stable/data/parquet/overview)
- [Docs: "Columnar storage", Amazon Redshift](https://docs.aws.amazon.com/redshift/latest/dg/c_columnar_storage_disk_mem_mgmnt.html)
- [Paper: "Amazon Redshift Re-invented", Armenatzoglou et al., SIGMOD (2022)](https://www.amazon.science/publications/amazon-redshift-re-invented)
- [Docs: "Micro-partitions and data clustering", Snowflake](https://docs.snowflake.com/en/user-guide/tables-clustering-micropartitions)
- [Docs: "BigQuery storage overview", Google Cloud](https://cloud.google.com/bigquery/docs/storage_overview)
- [Resources](../RESOURCES.md)
