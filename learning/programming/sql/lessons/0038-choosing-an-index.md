---
title: 38. Choosing an Index
description: Column order decides which queries an index can answer, and the best index is often the one you decide not to build
type: lesson
---

# Lesson 38. Choosing an Index

**Mission link:** Two indexes built from the same columns in a different order answer different queries, and the harder half of this skill is refusing the ones nobody needed, since every index left in place costs every write forever after.
**Primary source:** [PostgreSQL, 11.3 Multicolumn Indexes](https://www.postgresql.org/docs/current/indexes-multicolumn.html)
**Prerequisites:** [Lesson 36](0036-what-an-index-does.md), [Lesson 37](0037-selectivity-and-statistics.md)

## Warm-up

1. ▢ Lesson 36 showed a query answered entirely from an index, with `Heap Fetches: 0` because every column it needed was already in the index. What has to be true of the `SELECT` list, not just the `WHERE` clause, for that to happen?

<details markdown="1"><summary>Check</summary>

Every column read, filtered on or merely selected, has to be present in the index. Selecting a column the index lacks forces a visit to the table row for it, turning the plan into a plain index scan rather than an index-only one.

</details>

## Know this

### The leftmost-prefix rule, and what it buys or costs

A multicolumn index is a single btree built on a tuple of columns, searchable only from its front: an index on `(customer_id, amount)` jumps straight to one `customer_id`'s rows and can narrow those by `amount`, but has no way to jump to an `amount` without knowing which `customer_id` block it lives in. Building it and asking for one customer's orders gives an index-only scan:

```text
Index Only Scan using i38_cust_amount on orders (actual rows=7.00 loops=1)
  Index Cond: (customer_id = 4242)
  Heap Fetches: 0
  Index Searches: 1
  Buffers: shared hit=4 read=3
```

Asking for that customer's orders over a given amount too costs nothing extra, because `amount` is still part of the same index condition:

```text
Index Only Scan using i38_cust_amount on orders (actual rows=7.00 loops=1)
  Index Cond: ((customer_id = 4242) AND (amount > '10'::numeric))
  Heap Fetches: 0
  Index Searches: 1
  Buffers: shared hit=4 read=3
```

A filter on `amount` with no `customer_id` gets nothing from this index: the planner falls back to a parallel sequential scan of the whole table, `Buffers: shared hit=7346 read=262`, 7608 in total, since `amount` is not the leftmost column. Reverse the order to `(amount, customer_id)` and the pattern reverses too: `amount` alone now works, `customer_id` alone gets the same 7608-buffer scan. Only the leading column can start an index condition; every other column just narrows a scan already under way.

Call this the leftmost-prefix rule: an index on `(a, b, c)` serves a filter on `a`, on `a` and `b`, or on all three, and none of them if the leftmost filtered column is `b` or `c`. A table fielding five query shapes, on `customer_id`, on `customer_id` and `amount`, on `amount` alone, on `shipped_at` alone, and on `customer_id` and `shipped_at`, needs one index per distinct leftmost column: `(customer_id, amount)` answers the first two for free and none of the other three.

The same leading columns also decide what an index hands back already sorted, so an index chosen for a filter sometimes removes a sort too. `customer_id = 4242` ordered by `amount` shows no `Sort` node:

```text
Index Scan using i38_cust_amount on orders (actual rows=7.00 loops=1)
  Index Cond: (customer_id = 4242)
  Index Searches: 1
  Buffers: shared hit=4 read=3
```

The rows come out in `amount` order already, since that is the order the btree stores them in once `customer_id` is fixed, leaving nothing to sort. Pagination leans on this most, and lesson 40 works it through properly.

### Skip scan, and the honest boundary

Release 18 taught the planner a trick for the case the leftmost-prefix rule seems to rule out: searching by a column that is not first, when the leading column only takes a handful of values. On a table of 300,000 rows whose leading column holds five distinct values, indexed on that column and a second one, a filter on the second column alone still reaches the index:

```text
Index Only Scan using i38_bucket_id on t (actual rows=1.00 loops=1)
  Index Cond: (id = 150000)
  Heap Fetches: 0
  Index Searches: 7
  Buffers: shared hit=15 read=13
```

`Index Searches: 7` is the tell, and it is itself new in release 18: a single probe for one row would report one search, and seven means it restarted seven times, roughly once per value the leading column holds, rather than reading the table. That stops being cheap once the leading column has many distinct values instead of few, exactly what happened above when `(amount, customer_id)` was asked for `customer_id` alone: `amount` has far too many for a restart-per-value strategy to pay off, so the planner falls through to the sequential scan already shown. Skip scan rescues a low-cardinality leading column, and does nothing for a high-cardinality one.

### A covering index and INCLUDE

An index lacking a column the query selects can still narrow the search, it just cannot finish the job alone. An index on `customer_id` by itself, asked for `customer_id` and `shipped_at`, has to visit the table row for `shipped_at`:

```text
Index Scan using i38_customer_plain on orders (actual rows=7.00 loops=1)
  Index Cond: (customer_id = 4242)
  Index Searches: 1
  Buffers: shared hit=4 read=3
```

Rebuilding it with `shipped_at` added through `INCLUDE` rather than as a second key column turns the same query into an index-only scan:

```text
Index Only Scan using i38_customer_inc on orders (actual rows=7.00 loops=1)
  Index Cond: (customer_id = 4242)
  Heap Fetches: 0
  Index Searches: 1
  Buffers: shared hit=1 read=3
```

`INCLUDE` is not a shorter way of writing `(customer_id, shipped_at)`. An included column rides in the leaf pages purely so a query can read it without touching the table, but it is not part of the searchable key: a filter on `shipped_at` alone still falls back to a sequential scan, and `ORDER BY shipped_at` still needs an explicit sort, since the leaf pages are not ordered by it:

```text
Sort (actual rows=7.00 loops=1)
  Sort Key: shipped_at
  Sort Method: quicksort  Memory: 25kB
  Buffers: shared hit=4 read=3
  ->  Index Only Scan using i38_customer_inc on orders (actual rows=7.00 loops=1)
        Index Cond: (customer_id = 4242)
        Heap Fetches: 0
        Index Searches: 1
        Buffers: shared hit=4 read=3
```

An included column rides free on `SELECT` only, never on `WHERE` or `ORDER BY`.

### A partial index

Restricting an index to the rows a `WHERE` clause matches keeps it small and out of plans with no business in it. Indexing only orders over `400` and asking one customer for orders over `400` uses it as an index-only scan:

```text
Index Only Scan using i38_partial on orders (actual rows=20.00 loops=1)
  Index Cond: (customer_id = 18743)
  Heap Fetches: 0
  Index Searches: 1
  Buffers: shared hit=4 read=2
```

Asking the same customer for orders over a lower threshold, `50`, cannot trust that index, since rows between `50` and `400` were never put in it, so the planner reaches for a full index on `customer_id` and filters afterwards:

```text
Index Scan using i38_full on orders (actual rows=20.00 loops=1)
  Index Cond: (customer_id = 18743)
  Filter: (amount > '50'::numeric)
  Index Searches: 1
  Buffers: shared hit=1 read=3
```

`pg_relation_size` puts a number on the restriction: the partial index is `1949696` bytes against `9584640` for the full one, about a fifth the size, tracking the roughly one order in five that clears `400` here. A predicate a table's real queries keep asking past that same threshold keeps an index a fifth the size for the same lookups.

### An expression index

An index on `email` cannot answer a query that wraps `email` in a function first, since the function's output, not the column, is what the query filters on. Looking a customer up by a case-folded email with only the plain index in place forces a sequential scan:

```text
Seq Scan on customers (actual rows=1.00 loops=1)
  Filter: (lower(email) = 'katherine@example.com'::text)
  Rows Removed by Filter: 99999
  Buffers: shared hit=135 read=699
```

Indexing the expression itself, `lower(email)`, gives the planner something whose output matches what the query computes:

```text
Index Scan using i38_lower_email on customers (actual rows=1.00 loops=1)
  Index Cond: (lower(email) = 'katherine@example.com'::text)
  Index Searches: 1
  Buffers: shared hit=1 read=3
```

Lesson 25's `citext` solves the same problem from the other direction, making the column's own equality case-insensitive so no query needs `lower` at all.

### Deciding not to build one

Three reasons are worth refusing an index outright, each argued with evidence rather than a hunch.

The predicate is not selective enough, measured with lesson 37's tools: a third of customers, `33000` out of `100000`, carry `country = 'US'`. Removing only two rows in three still leaves the planner reading most of the table, and a sequential scan already reads every row in one pass, so the index buys nothing a plan would choose to use.

An existing index already covers the query as a prefix. `(customer_id, amount)` earlier answered `customer_id` alone as an index-only scan with no single-column index on `customer_id` existing, since `customer_id` is already its leftmost column. A second index built solely on it would be strictly redundant: identical rows, identical work, for queries the wider one already served.

The write cost is real even when the read benefit is worth it. Every index is one more structure every `INSERT`, `UPDATE` or `DELETE` on that table keeps current. A table carrying its primary key plus the partial and full indexes above updates three btrees per write instead of one, and those two cost `1949696` and `9584640` bytes apiece, numbers from `pg_relation_size`, not a writes-per-second figure nobody here measured.

## Practice

1. ▢ An index exists on `(a, b, c)`. Predict, for each filter, whether the index serves it as an index condition or leaves the planner with nothing: `a = 1`, `b = 1`, `a = 1 AND c = 1`.

<details markdown="1"><summary>Check</summary>

`a = 1` is served, as the leftmost column alone. `a = 1 AND c = 1` is served too, but only the `a` part becomes an index condition; `c` is checked as a filter afterwards. `b = 1` alone gets nothing, since it does not start from `a`.

</details>

2. ▢ Two two-column indexes each lead with a different column: one takes three distinct values, the other thirty thousand. Predict which can answer a filter on its second column alone.

<details markdown="1"><summary>Hint</summary>

A skip scan restarts once per leading value, and a restart is only cheap when there are few of them.

</details>

<details markdown="1"><summary>Check</summary>

The three-value one, via a skip scan restarting a handful of times. Restarting thirty thousand times beats nothing, so the planner never attempts it there and falls back to a sequential scan, as `(amount, customer_id)` did above.

</details>

3. ▢ An index is built as `(customer_id) INCLUDE (amount)`. Predict whether `ORDER BY amount` on a query already filtering by `customer_id` avoids a sort.

<details markdown="1"><summary>Check</summary>

No. `amount` rides in the leaf pages for reading, not for ordering, so a `Sort` node still appears, the same shape this lesson showed for `ORDER BY shipped_at` against an included column.

</details>

4. ▢ A partial index is built `WHERE shipped_at IS NULL`. Predict which filter can use it: `customer_id = 4242 AND shipped_at IS NULL`, or `customer_id = 4242 AND shipped_at IS NOT NULL`.

<details markdown="1"><summary>Check</summary>

Only the first. The second asks for exactly the rows the index excludes, so the planner reaches for a different index or a sequential scan instead.

</details>

5. ▢ A table carries an index on `(order_status, customer_id)`. Someone proposes also indexing `customer_id` alone, since some queries filter on it without mentioning `order_status`. Predict whether that proposal is redundant.

<details markdown="1"><summary>Check</summary>

Not redundant, unlike the `(customer_id, amount)` case earlier: `customer_id` is the second column here, so the existing index cannot serve a filter on it alone as a prefix. Selectivity and write cost still apply before building it, but redundancy is not the objection.

</details>

6. ▢ A new predicate, measured with lesson 37's tools, removes 90 percent of a table's rows. Predict what else has to be checked before building an index for it.

<details markdown="1"><summary>Hint</summary>

This lesson gave three reasons to refuse an index, and selectivity was only one.

</details>

<details markdown="1"><summary>Check</summary>

Whether an existing index already serves it as a leftmost prefix, and the write cost of one more structure on every insert, update and delete.

</details>

## Real-world reps

- [ ] Run `EXPLAIN (ANALYZE)` on a query you run often, and check whether an index's column order starts with the column it filters on first.
- [ ] Find an index a typical query never touches, and decide, with this lesson's three reasons to refuse one, whether it should exist.
- [ ] Tomorrow: find a query selecting a column beyond its index's key, and work out whether `INCLUDE` would make it an index-only scan.

## Going further

- [11.9. Index-Only Scans and Covering Indexes](https://www.postgresql.org/docs/current/indexes-index-only-scans.html): `INCLUDE` and the heap fetch it avoids
- [11.8. Partial Indexes](https://www.postgresql.org/docs/current/indexes-partial.html): the `WHERE` clause on `CREATE INDEX`
- [11.7. Indexes on Expressions](https://www.postgresql.org/docs/current/indexes-expressional.html): indexing a function's output
- [E.6. Release 18](https://www.postgresql.org/docs/current/release-18.html): where skip scan and this lesson's `EXPLAIN` changes arrived
- [CREATE INDEX](https://www.postgresql.org/docs/current/sql-createindex.html): `INCLUDE` and partial-index syntax
- [Performance](../reference/performance.md): the stage 6 reference sheet
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
