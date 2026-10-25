---
title: 10. The Row-Store Advice That Stops Applying
description: Which habits from indexing and normalizing a row store are wrong on a columnar warehouse, and which still hold
type: lesson
---

# Lesson 10. The Row-Store Advice That Stops Applying

**Mission link:** The mission asks you to say from the storage layout why advice that was right on a row store is wrong on a warehouse. This lesson closes stage 4 by sorting the habits a row-store engineer brings, each by the mechanism from lessons 1 to 9 that breaks it or keeps it.
**Primary source:** [Docs: "Optimize query computation", Google Cloud](https://cloud.google.com/bigquery/docs/best-practices-performance-compute)
**Prerequisites:** [Lesson 9](0009-joins-and-data-distribution.md), [Row store](../GLOSSARY.md), [Column store](../GLOSSARY.md), [Bytes scanned](../GLOSSARY.md)

## Warm-up

1. ▢ Why is broadcasting a 1 GB dimension to 16 nodes usually cheaper than shuffling it with a 400 GB fact table?

<details markdown="1"><summary>Check</summary>

Broadcasting moves 1 GB × 16 = 16 GB. Shuffling moves roughly both sides once, about 401 GB. Copying a small side everywhere beats moving the large side at all.

</details>

2. ▢ A table is clustered on `(country, city)`. Which of `country = 'JP'` and `city = 'Osaka'` prunes better, and why?

<details markdown="1"><summary>Check</summary>

`country = 'JP'`, the leading column. Storage is ordered by country first, so one country's rows sit in a narrow run of blocks; one city's rows are narrow only within its country, and a filter on city alone gets no help from the order.

</details>

## Know this

### Advice is a claim about a mechanism

Every piece of row-store performance advice is true because of how a row store lays out pages and indexes, which [`programming/sql`](../../../programming/sql/reference/performance.md) teaches. When the layout changes, the advice has to be re-derived, not carried over. The test for each habit is the same: what does it save on a row store, and does that saving exist when data is stored by column in large blocks with min and max metadata, across many workers, billed by bytes scanned or compute time?

### Habits that fail

**Adding a secondary B-tree index for a slow filter.** On a row store an [index](../../../programming/sql/GLOSSARY.md) is a separate ordered structure that turns a scan into a walk to a few pages. The warehouses here have no such structure on ordinary tables: BigQuery "doesn't index primary keys" ([Optimize query computation](https://cloud.google.com/bigquery/docs/best-practices-performance-compute)), and Redshift and Snowflake offer sort and clustering keys instead. The equivalent move is to change the storage order, so the per-block minimum and maximum prune on that column (lessons 7 and 8). BigQuery search indexes and Snowflake's search optimization service do exist for needle-in-haystack lookups, as separately billed features, not as the default tool.

**Adding `LIMIT` to make a query cheaper.** On a row store, `LIMIT 10` lets a scan stop after ten rows. A column store reads each referenced column's blocks before rows are assembled, so the limit trims the output, not the scan. BigQuery says it outright: "Applying a `LIMIT` clause to a `SELECT *` query does not affect the amount of data read" ([Optimize query computation](https://cloud.google.com/bigquery/docs/best-practices-performance-compute)). To look at sample rows, use the table preview, which is not billed, or filter on the partition column.

**`SELECT *` for convenience.** On a row store the whole row is on the page anyway, so naming every column costs little extra I/O. On a column store each column is a separate set of chunks, and bytes scanned is the sum over referenced columns (lesson 1). Both BigQuery and Redshift's query guidance say to select only the columns you need ([Query design best practices](https://docs.aws.amazon.com/redshift/latest/dg/c_designing-queries-best-practices.html)).

**A highly normalized schema joined at query time.** Third normal form keeps each fact in one place, so an update touches one row, and joins on a row store are cheap index lookups. On a distributed warehouse each join may shuffle or broadcast rows between workers (lesson 9), and a chain of six joins pays that six times on every query. BigQuery suggests nested and repeated fields where they save "the communication bandwidth that a join requires" ([Optimize query computation](https://cloud.google.com/bigquery/docs/best-practices-performance-compute)). The usual answer is a star schema, one join deep, which stage 5 designs; see the row-store side of the trade in [Denormalisation](../../../programming/sql/reference/schema-design.md#denormalisation).

**Single-row `UPDATE` or `DELETE` in a loop.** On a row store, updating one row rewrites one page. A warehouse stores rows in large compressed column blocks, and Snowflake's micro-partitions are immutable: changing one row means writing a new micro-partition holding all of its rows and columns. A loop issuing one statement per row, the [N+1](../../../programming/sql/GLOSSARY.md) shape, rewrites a block per row. Load the changes as a batch and apply them with one `MERGE`, which lesson 15 makes safe to rerun.

**Point lookups as a serving path.** `SELECT * FROM orders WHERE order_id = 81723` is an index walk and one page on a row store. On a column store it reads at least one block per column, after scheduling a distributed query, which lesson 1 predicted. A warehouse can answer it, but an application that serves one row per user request belongs on a row store.

### Habits that still hold

**Filter early.** Fewer surviving rows mean fewer blocks read, if the filter prunes (lessons 7 and 8), and fewer rows moved, if it runs before a join (lesson 9). Redshift goes further than a row store would: repeat a filter on each joined table, even when it is logically redundant, so each table's blocks are skipped before the scan ([Query design best practices](https://docs.aws.amazon.com/redshift/latest/dg/c_designing-queries-best-practices.html)).

**Avoid joins the answer does not need.** A join that only checks existence, or a dimension joined for a column nobody selects, still moves rows. BigQuery recommends a window function over a self-join, which "potentially squares the number of output rows" ([Optimize query computation](https://cloud.google.com/bigquery/docs/best-practices-performance-compute)).

**Use correct data types.** The reasons multiply rather than vanish. A date stored as a string cannot be a BigQuery time-unit partition, and a cast to compare it may defeat pruning (lesson 7). Join keys compare faster when narrow: BigQuery says to join on `INT64` rather than `STRING`. A column of one well-chosen type also encodes and compresses better (lesson 3). The row-store reasons, refusing bad values and keeping exact money, still apply too: see [Type choice](../../../programming/sql/reference/schema-design.md#type-choice).

### Worked example: the cheap-looking preview

A 1 TB `events` table has 100 columns of roughly equal width, partitioned by day over 1,000 days, 1 GB a day. An analyst runs `SELECT * FROM events LIMIT 10` to see what is in it.

- As written: every column of every partition, 1 TB scanned, for ten rows.
- `SELECT event_id, user_id, event_type FROM events WHERE event_date = '2026-10-20' LIMIT 10`: 3 columns of one partition, 1 GB × 3 ÷ 100 = 30 MB.
- The table preview in the console: 0 bytes billed.

The three return similar-looking rows. Only the first costs as much as a full-table aggregation.

### Predict, then run

Dry runs are free on BigQuery. Against `bigquery-public-data.samples.shakespeare`, predict the bytes each reports relative to the first:

```sql
SELECT * FROM `bigquery-public-data.samples.shakespeare`;
SELECT * FROM `bigquery-public-data.samples.shakespeare` LIMIT 10;
SELECT word FROM `bigquery-public-data.samples.shakespeare` LIMIT 10;
```

The first two report the same bytes; `LIMIT` changed nothing. The third reports only the `word` column's share. Write your three predictions down before you look.

## Practice

1. ▢ Name the mechanism that makes `LIMIT 10` cheap on a row store and the one that makes it no cheaper on a column store.

<details markdown="1"><summary>Check</summary>

Row store: a scan reads pages holding whole rows and can stop once ten qualify. Column store: each referenced column's blocks are read and decoded before rows are assembled, and bytes scanned is set by the columns referenced and the blocks not pruned, not by how many rows are returned.

</details>

2. ▢ Which piece of row-store advice still holds on a columnar warehouse?

    - a) Add a secondary index on any column that appears in a slow filter
    - b) Store dates as proper date types rather than as formatted strings
    - c) Normalize to third normal form and join the tables at query time
    - d) Add a `LIMIT` to exploratory queries so that they cost less

<details markdown="1"><summary>Check</summary>

**b)** A date type can be a partition column, prunes without a cast, and encodes compactly. (a) fails: there are no secondary B-tree indexes on ordinary warehouse tables; the equivalent is a clustering or sort key. (c) fails: every join may move rows between workers, so warehouses favour a star schema one join deep. (d) fails: `LIMIT` trims output, not bytes scanned.

</details>

3. ▢ A job updates customer statuses on Snowflake by looping over 20,000 changed customers, one `UPDATE ... WHERE customer_id = ?` each. It takes hours. Explain from storage why, and give the fix.

<details markdown="1"><summary>Hint</summary>

Ask what Snowflake must write to change one row in an immutable micro-partition, and how many times the loop makes it do that.

</details>

<details markdown="1"><summary>Check</summary>

Micro-partitions are immutable, so each `UPDATE` writes a new micro-partition holding every row and column of the one it changed. The loop does that up to 20,000 times, plus a statement's overhead each time. Stage the changes as one table and run a single `MERGE` (or one `UPDATE ... FROM`), which rewrites each affected micro-partition once.

</details>

4. ▢ A reviewer says: "This fact table is joined to six normalized tables in every dashboard query. Denormalize it." A colleague replies: "Normalization is best practice; joins are cheap." Settle it from the mechanism, and say what you would check.

<details markdown="1"><summary>Check</summary>

Joins are cheap on a row store because an index finds matches on one machine. On a distributed warehouse each join can shuffle or broadcast rows between workers, and six of them on every dashboard query repeat that cost each time. Check the plan or profile: which joins move rows, how many bytes, and how much of the query's time they take. If the movement dominates, flatten into a star schema or nest; if the joined tables are tiny and broadcast, the reviewer's gain is small.

</details>

5. ▢ Interleave lesson 7: a table stores `event_date` as a `STRING` like `'2026-10-20'`. Name two costs this has on BigQuery that a `DATE` column would not.

<details markdown="1"><summary>Check</summary>

It cannot be a time-unit partition column, so date filters cannot prune partitions; the table needs ingestion-time partitioning or a new column. And any date logic on it needs a cast or a parse, which on a partition column can defeat pruning and on any column costs a conversion per value. A string is also wider to compare and store than a date.

</details>

6. ▢ A product team wants its app to fetch one customer's profile from the warehouse on every page view, about 200 lookups a second. Which lesson 1 fact argues against it, and where should that read go?

<details markdown="1"><summary>Check</summary>

A single-row lookup reads at least one block per column on a column store, after scheduling a distributed query, where a row store walks an index to one page. At 200 a second that is slow and, under on-demand or per-second compute billing, expensive. Serve it from a row store, such as Postgres, kept in sync from the warehouse or the source system.

</details>

## Real-world reps

- [ ] Today: run the three dry runs in this lesson's predict-then-run, predictions first.
- [ ] Search your team's saved queries or dbt models for `SELECT *` and for `LIMIT` used as a cost control. Pick one and estimate the bytes a column list would save.
- [ ] Tomorrow: list three performance habits you learned on a row store, and for each write the mechanism that made it true and whether that mechanism exists on your warehouse.
- [ ] Find one job that updates or deletes rows one at a time, and sketch the staged `MERGE` that would replace it.

## Going further

- [Physical Design](../reference/physical-design.md)
- [Docs: "Optimize query computation", Google Cloud](https://cloud.google.com/bigquery/docs/best-practices-performance-compute)
- [Docs: "Query design best practices", Amazon Redshift](https://docs.aws.amazon.com/redshift/latest/dg/c_designing-queries-best-practices.html)
- [Docs: "Optimize query cost", Google Cloud](https://cloud.google.com/bigquery/docs/best-practices-costs)
- [The index decisions on a row store](../../../programming/sql/reference/performance.md#the-index-decisions): what a B-tree index buys and costs, the side of the comparison this lesson drops
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
