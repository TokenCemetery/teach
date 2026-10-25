---
title: 1. Row Stores and Column Stores
description: Why an analytical query reads a fraction of the bytes from a column store that it reads from a row store, and why a single-row lookup goes the other way
type: lesson
---

# Lesson 1. Row Stores and Column Stores

**Mission link:** Every claim this course makes about warehouse speed and cost starts from which bytes sit next to which in storage. This lesson is that fact, and the arithmetic that turns it into a prediction of bytes scanned.
**Primary source:** [Paper: "The Design and Implementation of Modern Column-Oriented Database Systems", Abadi, Boncz, Harizopoulos, Idreos and Madden, Foundations and Trends in Databases (2013)](https://www.cs.umd.edu/~abadi/papers/abadi-column-stores.pdf)
**Prerequisites:** [Row store](../GLOSSARY.md), [Column store](../GLOSSARY.md), [OLAP](../GLOSSARY.md)

## Know this

### Two workloads, two access patterns

An [OLTP](../GLOSSARY.md) workload is many short queries, each reading or writing a few whole rows by key: fetch order 81723, mark it shipped. An [OLAP](../GLOSSARY.md) workload is few queries, each reading many rows but only a few columns and aggregating them: revenue by region for the last quarter. The first wants every column of one row in one place; the second wants one column of every row in one place.

Storage is read in fixed-size units (a page, a block), never one value at a time. So the question that decides cost is not "how many rows does the query need" but "how many units hold the values it needs, and what else is in them". The survey that is this lesson's primary source puts it plainly: a row-oriented block holds all columns, so there is no way to read the needed attributes "without also transferring the surrounding attributes" (Abadi et al., section 1).

### A row store page

PostgreSQL is a row store, and its [page layout](https://www.postgresql.org/docs/current/storage-page-layout.html) shows the shape exactly. A table is a sequence of 8 kB pages. Each page starts with a 24-byte header, then an array of 4-byte item identifiers growing forward, while the rows themselves (tuples) are placed from the end of the page backward. Each tuple is a 23-byte header (24 once aligned) followed by that row's column values, one after another. Every column of a row sits in the same tuple, on the same page.

Fetching one whole row is a single page read. Reading one column of every row reads every page, because that column is interleaved with all the others.

### A column store

A [column store](../GLOSSARY.md) keeps each column's values together: a block of `amount` holds thousands of amounts and nothing else. A query that references three columns never fetches the others.

![On the left, a row store keeps orders 1 and 2 with all four columns on page 1 and orders 3 and 4 on page 2, so summing amount by region reads both pages whole, sixteen values. On the right, a column store keeps one chunk per column, so the same query reads only the region and amount chunks, eight values. A lookup of order 3 is one page on the left but touches all four chunks on the right.](images/row-and-column-layout.svg)

All three platforms in this course store tables this way. BigQuery "stores each column separately" and describes column-oriented storage as efficient "at scanning individual columns over an entire dataset" ([BigQuery storage overview](https://cloud.google.com/bigquery/docs/storage_overview)). Snowflake stores each column independently inside a [micro-partition](../GLOSSARY.md) and scans only the columns a query references ([Micro-partitions and data clustering](https://docs.snowflake.com/en/user-guide/tables-clustering-micropartitions)). Redshift writes each column to its own 1 MB blocks, and its documentation gives the same arithmetic this lesson does: a query using 5 of 100 columns reads about 5 percent of the table ([Columnar storage](https://docs.aws.amazon.com/redshift/latest/dg/c_columnar_storage_disk_mem_mgmnt.html)).

### Worked example: the analytical query

Take an `orders` table with 1 billion rows and 200 columns. Call each column 5 bytes on average, so each row carries 1,000 bytes of data and the table holds 1 TB of values. The query:

```sql
SELECT region, SUM(amount)
FROM orders
WHERE order_date >= DATE '2026-01-01'
GROUP BY region;
```

It references 3 of the 200 columns.

**Row store.** Each tuple is 24 bytes of header plus 1,000 bytes of data, plus a 4-byte item identifier: 1,028 bytes. A page has 8,192 − 24 = 8,168 bytes for tuples, so 7 rows fit (an eighth would need 8,224). One billion rows need about 143 million pages, which is about 1.17 TB. With no index that narrows the date range, the query reads all of it: roughly 1.17 TB to use 15 GB of values.

**Column store.** The three referenced columns hold 3 × 5 bytes × 1 billion = 15 GB. That is what the query reads, before compression, which lesson 3 adds and which shrinks it further. On BigQuery's [on-demand pricing](../GLOSSARY.md), those 15 GB are the [bytes scanned](../GLOSSARY.md) the query is billed for, not the 1 TB.

The ratio, about 1 to 78, grows as the table gets wider and the query stays narrow.

### Worked example: the single-row lookup

Now the other workload, on the same table:

```sql
SELECT * FROM orders WHERE order_id = 81723;
```

**Row store.** A B-tree index on `order_id` over a billion rows is about four levels deep. The lookup reads four index pages and one heap page: 5 pages, 40 kB, and the whole row arrives in one of them.

**Column store.** There is no B-tree to descend, and `SELECT *` needs a value from every one of the 200 columns, each stored separately. Even if the engine could locate the row's position perfectly, it reads at least one block per column: 200 reads. At Parquet's recommended 8 KB page size that is about 1.6 MB; at Redshift's 1 MB block size it is about 200 MB. On BigQuery, a table with no [partition](../GLOSSARY.md) or [clustering key](../GLOSSARY.md) has nothing that lets the filter skip storage, so the query scans every column in full and is billed for the whole 1 TB. The survey names the trade directly: a single-record query on a column store "will have to seek several times (to all columns/files of the table referenced in the query)" (Abadi et al., section 1).

Writes go the same way. Updating one row on a row store rewrites one tuple on one page; on a column store it touches one place per column, which the survey's section 4.7 describes as "as many as the attributes in the table". This is why warehouses load in batches, which stage 6 covers.

### Predict, then run

DuckDB reads Parquet, a columnar file format, on a laptop at no cost ([Parquet Files](https://duckdb.org/docs/stable/data/parquet/overview)). Make a four-column file of a million rows:

```sql
COPY (
  SELECT i AS order_id,
         i % 5000 AS customer_id,
         round((i * 7919 % 100000) / 100.0, 2) AS amount,
         'note ' || i AS note
  FROM range(1000000) t(i)
) TO 'orders.parquet' (FORMAT parquet);
```

Predict what fraction of the file `SELECT sum(amount) FROM 'orders.parquet'` reads, then run it under `EXPLAIN ANALYZE` and compare the `Data Read` line with the same for `SELECT *`. When this lesson was checked with DuckDB 2.0, the sum read 4.8 MB and `SELECT *` read 15.3 MB: about a third, because `amount` is one of four columns and roughly a third of the bytes. The columns are not equal widths, which is the point of Practice item 2.

## Practice

1. ▢ Label each as an OLTP or an OLAP access pattern: (a) load one customer's profile page; (b) weekly active users per country over two years; (c) decrement stock for the three items in a basket; (d) the median order value per product category.

<details markdown="1"><summary>Check</summary>

(a) OLTP, (b) OLAP, (c) OLTP, (d) OLAP. The test is the shape, not the subject: a few whole rows by key is OLTP; many rows, few columns, aggregated is OLAP. "Customer" appears in both kinds of question.

</details>

2. ▢ A table holds 500 GB across 50 columns. A query references 2 of them. Predict the bytes a column store reads if the columns are equal width. Then predict it again if one of the two referenced columns is a free-text `description` holding 40 percent of the table's bytes.

<details markdown="1"><summary>Hint</summary>

A column store reads the bytes of the referenced columns, not a share of the column count.

</details>

<details markdown="1"><summary>Check</summary>

Equal widths: 2 × 10 GB = 20 GB. With `description`: 200 GB for it plus about 300 GB ÷ 49 ≈ 6 GB for the other, so about 206 GB. The column count predicts nothing once widths differ. Bytes scanned is the sum of the referenced columns' sizes, which is why one wide text column in a query can cost more than every other column together.

</details>

3. ▢ Which statement best explains why a single-row lookup by key is cheaper on a row store?

    - a) Row stores compress each column better, so one row takes fewer bytes on disk
    - b) The whole row sits in one tuple on one page, so one read returns it
    - c) Column stores cannot filter by a key value until every row is decompressed
    - d) Row stores keep every table in memory, so a lookup never reads storage

<details markdown="1"><summary>Check</summary>

**b)** One tuple on one page, reached through a few index pages. (a) has compression backwards: one column of one type compresses better, which is lesson 3. (c) is false: a column store can filter on the key column alone, and lesson 2 shows statistics skipping most of it; the cost is fetching the other 199 columns afterward. (d) is false: PostgreSQL reads 8 kB pages from storage, cached or not.

</details>

4. ▢ A PostgreSQL table's rows carry 300 bytes of column data each and have no nulls. How many rows fit on one 8 kB page, and how many heap pages does a lookup of one row by its indexed key read?

<details markdown="1"><summary>Check</summary>

Tuple: 24 bytes of header plus 300 bytes of data, 324, aligned to 328, plus a 4-byte item identifier, 332. Space for tuples: 8,192 − 24 = 8,168. 8,168 ÷ 332 ≈ 24.6, so 24 rows per page. The lookup reads one heap page (after the index pages), whatever the row width, as long as the row fits on a page.

</details>

5. ▢ On the 200-column, 1-billion-row `orders` table in PostgreSQL, a colleague adds a B-tree index on `order_date` so the revenue-by-region query reads less. The filter matches 30 percent of rows, spread evenly through the table. Does the index bring the bytes read anywhere near the 15 GB a column store reads?

<details markdown="1"><summary>Hint</summary>

The index finds rows, but each matching row still lives in a heap page with 7 rows and 200 columns. What share of pages contain no matching row?

</details>

<details markdown="1"><summary>Check</summary>

No. A page escapes only if all 7 of its rows miss the filter: 0.7^7 ≈ 8 percent. So about 92 percent of the 143 million pages still have to be read, roughly 1.07 TB, now in index order rather than sequentially, which is why the PostgreSQL planner would likely ignore the index and scan the table. An index narrows which rows are read; it cannot stop each row's other 197 columns from coming along. Only a different layout does that.

</details>

6. ▢ A team moved its order-tracking application onto a warehouse to "get one database". Every status change is a single-row `UPDATE`, and each one is slow and, on their platform, expensive. Explain from the layout what is happening.

<details markdown="1"><summary>Check</summary>

The workload is OLTP: one whole row at a time, by key. A column store spreads that row across one storage unit per column, so each update touches many units instead of one tuple on one page, and those units are large (a 1 MB Redshift block, a micro-partition of 50 to 500 MB before compression) and written in bulk. The layout that makes dashboards cheap makes these writes expensive.

</details>

## Real-world reps

- [ ] Today: run the DuckDB comparison above, then add a fifth, wide text column to the file and predict how the `Data Read` of `SELECT sum(amount)` changes before you run it.
- [ ] In a PostgreSQL database you can read, run `SELECT avg(pg_column_size(t.*)) FROM some_table t` on a wide table, and compute its rows per 8 kB page by hand as in Practice item 4. Compare with `SELECT reltuples / relpages FROM pg_class WHERE relname = 'some_table'`.
- [ ] Tomorrow: take a dashboard query you know. Count the columns it references against the table's total, estimate what share of the table a column store reads, and say which column dominates.
- [ ] If you have a BigQuery project, dry-run `SELECT one_column` and then `SELECT *` on the same table, and compare the bytes each would process. A dry run is not billed.

## Going further

- [Columnar Storage and Execution](../reference/columnar-storage-and-execution.md)
- [Paper: "The Design and Implementation of Modern Column-Oriented Database Systems", Abadi, Boncz, Harizopoulos, Idreos and Madden, Foundations and Trends in Databases (2013)](https://www.cs.umd.edu/~abadi/papers/abadi-column-stores.pdf)
- [Docs: "Database Page Layout", PostgreSQL](https://www.postgresql.org/docs/current/storage-page-layout.html)
- [Docs: "Columnar storage", Amazon Redshift](https://docs.aws.amazon.com/redshift/latest/dg/c_columnar_storage_disk_mem_mgmnt.html)
- [Docs: "BigQuery storage overview", Google Cloud](https://cloud.google.com/bigquery/docs/storage_overview)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
