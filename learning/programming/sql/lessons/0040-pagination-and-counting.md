---
title: 40. Pagination and Counting
description: OFFSET reads and discards every row it skips, and counting exactly costs a pass over the table
type: lesson
---

# Lesson 40. Pagination and Counting

**Mission link:** A paginated list fast on page one and slow on page five hundred is not a server problem but a query shape problem, and the fix a senior engineer reaches for never gets slower no matter how deep a reader scrolls.
**Primary source:** [PostgreSQL, LIMIT and OFFSET](https://www.postgresql.org/docs/current/queries-limit.html)
**Prerequisites:** [Lesson 5](0005-sorting-and-collation.md), [Lesson 38](0038-choosing-an-index.md)

## Warm-up

1. ▢ Lesson 5 showed that `ORDER BY customer_id LIMIT 10` with no tiebreaker can place a tied row differently between two runs, so a page can show a row twice or skip it entirely. Why does adding `OFFSET` to that same query make the problem worse rather than just carrying it along unchanged?

<details markdown="1"><summary>Check</summary>

`OFFSET` decides which rows to skip using that same unstable order, so a reshuffle among tied rows can move one across the page boundary, not just within a page. A row ranked 20 on one run and 21 on the next appears on both pages or on neither, and nothing looks wrong to the database: the order was never unique, so every rank past the tie is up for grabs.

</details>

## Know this

### OFFSET reads what it skips

A "recent orders" page reads the newest rows first, backed by the primary key:

```sql
SELECT id, amount FROM orders ORDER BY id DESC LIMIT 20;
```

```text
Limit (actual rows=20.00 loops=1)
  Buffers: shared hit=4
  ->  Index Scan Backward using orders_pkey on orders (actual rows=20.00 loops=1)
        Index Searches: 1
        Buffers: shared hit=4
```

Twenty rows out, 4 buffers touched; `Index Searches` is release 18's own addition to this node. Page twenty-five thousand of the same list, the ordinary way, adds `OFFSET 500000`:

```sql
SELECT id, amount FROM orders ORDER BY id DESC LIMIT 20 OFFSET 500000;
```

```text
Limit (actual rows=20.00 loops=1)
  Buffers: shared hit=4993
  ->  Index Scan Backward using orders_pkey on orders (actual rows=500020.00 loops=1)
        Index Searches: 1
        Buffers: shared hit=4993
```

The one number that answers the question is buffers: 4 against 4993, well over a thousand times as many, for the same twenty columns. The scan node's own row count explains why, reporting `500020.00`: the server has no way to hand back row 500001 without first producing and discarding rows 1 through 500000. `OFFSET` is not a jump, it is a full walk from the start of the order, and only after the walk does the server start keeping rows. The rule: the cost of page N grows with N, so the last page of a long list is the slowest thing in the feature, and it only gets slower as the list grows.

### Keyset pagination

The fix remembers a row instead of a position. A client that has already seen the last page's final row, id `550905`, asks for the next slice with a condition:

```sql
SELECT id, amount FROM orders WHERE id < 550905 ORDER BY id DESC LIMIT 20;
```

```text
Limit (actual rows=20.00 loops=1)
  Buffers: shared hit=7
  ->  Index Scan Backward using orders_pkey on orders (actual rows=20.00 loops=1)
        Index Cond: (id < 550905)
        Index Searches: 1
        Buffers: shared hit=7
```

Seven buffers, for the same depth that `OFFSET` paid 4993 for, because the index condition starts the scan exactly where the last page ended rather than walking past everything before it. That is the whole trade: a client stops sending "page 25001" and starts sending "the last row I saw was id 550905", and every page then costs the same seven buffers regardless of depth. What crosses the wire changes shape too: not a page number, but a key, opaque to the client beyond "send this back next time".

That key has to be unique, or the order it walks is not stable, the warm-up's problem now applied to `WHERE` as well as `ORDER BY`. Sorting by `customer_id` alone, a column many orders share, shows why a bare comparison breaks. With an index on `(customer_id, id)` built for this, and a page's last row recorded as `(9, 1008)`, the naive rewrite drops the tiebreaker:

```sql
SELECT customer_id, id FROM orders WHERE customer_id > 9 ORDER BY customer_id, id LIMIT 20;
```

That returns rows starting at `(10, 1019)`, silently skipping the rest of customer 9's orders, ids 1009 through 1018, since none satisfy `customer_id > 9`. Nothing errors; those rows are simply gone from every page ever requested. The correct rewrite compares both columns together as a row, [Row Constructor Comparison](https://www.postgresql.org/docs/current/functions-comparisons.html#ROW-WISE-COMPARISON):

```sql
SELECT customer_id, id FROM orders WHERE (customer_id, id) > (9, 1008) ORDER BY customer_id, id LIMIT 20;
```

```text
Limit (actual rows=20.00 loops=1)
  Buffers: shared hit=4
  ->  Index Only Scan using i40_customer_id on orders (actual rows=20.00 loops=1)
        Index Cond: (ROW(customer_id, id) > ROW(9, 1008))
        Heap Fetches: 20
        Index Searches: 1
        Buffers: shared hit=4
```

This continues correctly, the rest of customer 9's orders then customer 10 from 1019 onward, no gap and no repeat. The rule that generalises: any keyset condition on a non-unique column needs the same tiebreaker in `WHERE` as in `ORDER BY`, compared as a tuple, or it reintroduces the gap it was meant to close.

### What keyset pagination gives up

Three things, honestly: no jumping to page fifty-seven, since there is no page number left, only "after this key"; no total page count without a separate query; and an arbitrary sort the user picks freely needs a matching tiebreaker and usually a matching index per sort offered, lesson 38's territory. None of that makes `OFFSET` wrong: a settings page capped at a few hundred rows never reaches the depth where its cost matters, and a keyset rewrite there buys nothing a reader notices.

### Counting, and the three answers

"How many rows match" has three honest answers, and the choice is about what the number is for. An exact count reads every row:

```sql
SELECT count(*) FROM orders;
```

```text
Finalize Aggregate (actual rows=1.00 loops=1)
  Buffers: shared hit=7230 read=378
  ->  Gather (actual rows=3.00 loops=1)
        Workers Planned: 2
        ->  Partial Aggregate (actual rows=1.00 loops=3)
              ->  Parallel Seq Scan on orders (actual rows=349972.00 loops=3)
```

7608 buffers, the whole table, split across parallel workers (`Gather` is lesson 39's subject). A filtered `count(*)`, `WHERE amount > 100`, costs the same 7608, since every heap page still has to be read before deciding what to keep. The second answer is an estimate that costs nothing to ask:

```sql
SELECT reltuples::bigint FROM pg_class WHERE relname = 'orders';
```

Immediately after `ANALYZE orders` this returned `1049916`, matching `count(*)` exactly. `reltuples` is maintained by `ANALYZE` and autovacuum, lesson 37's subject, and it drifts between those runs rather than tracking every write. The third answer is a bounded count, cheap because it stops early:

```sql
SELECT count(*) FROM (SELECT 1 FROM orders WHERE amount > 100 LIMIT 1000) s;
```

```text
Aggregate (actual rows=1.00 loops=1)
  Buffers: shared hit=9
  ->  Limit (actual rows=1000.00 loops=1)
        ->  Seq Scan on orders (actual rows=1000.00 loops=1)
              Filter: (amount > '100'::numeric)
```

Nine buffers, against 7608 for the exact filtered count, since the scan stops the moment it has a thousand matches. It answers "more than a thousand" cheaply and nothing finer; asked about a predicate matching fewer rows than the bound, it still reports the true number, since there was nothing left to cut off. The rule across all three: decide what the number is for before deciding how to get it, since a page count nobody reads is not worth a pass over the table.

### An index that removes the sort

The first plan above already showed this unnamed: ordering by `id`, the primary key's own order, produced no `Sort` node, because `Index Scan Backward` hands rows back already in that order. The same query ordered by a column with no matching index, `amount`, plans entirely differently:

```sql
SELECT id, amount FROM orders ORDER BY amount DESC LIMIT 20;
```

```text
Limit (actual rows=20.00 loops=1)
  Buffers: shared hit=7682
  ->  Gather Merge (actual rows=20.00 loops=1)
        ->  Sort (actual rows=16.00 loops=3)
              Sort Key: amount DESC
              Sort Method: top-N heapsort  Memory: 26kB
              ->  Parallel Seq Scan on orders (actual rows=349972.00 loops=3)
```

7682 buffers, most of the table, since every row has to be read before the twenty largest are known; `Gather Merge`, combining sorted streams from parallel workers, is lesson 39's subject, named here only in passing. `Sort Method: top-N heapsort` and its 26kB show this sort knew only twenty rows would survive, keeping a small heap rather than sorting everything. Choosing, or refusing, an index whose leading columns match an `ORDER BY` is lesson 38's decision; this lesson only shows what that decision buys back.

### A LIMIT changes the plan, not just the result

The planner treats a bounded result as a different problem from a full one, and a query fast at one `LIMIT` can change shape at another. Filtering for unshipped orders, ordered newest first, with a small `LIMIT`:

```sql
SELECT id, amount FROM orders WHERE shipped_at IS NULL ORDER BY id DESC LIMIT 20;
```

```text
Limit (actual rows=20.00 loops=1)
  Buffers: shared hit=5
  ->  Index Scan Backward using orders_pkey on orders (actual rows=20.00 loops=1)
        Filter: (shipped_at IS NULL)
        Rows Removed by Filter: 122
        Buffers: shared hit=5
```

Five buffers: the planner bets that walking the index backward turns up twenty matches quickly, and it does. Raising `LIMIT` to 150000, close to everything that filter matches, changes the plan's shape entirely:

```text
Limit (actual rows=149991.00 loops=1)
  Buffers: shared hit=7611, temp read=460 written=462
  ->  Sort (actual rows=149991.00 loops=1)
        Sort Key: id DESC
        Sort Method: external merge  Disk: 3680kB
        ->  Seq Scan on orders (actual rows=149991.00 loops=1)
              Filter: (shipped_at IS NULL)
              Rows Removed by Filter: 899925
```

7611 buffers, plus a disk-backed sort, `Sort Method: external merge Disk: 3680kB`, because at this depth the earlier bet no longer pays: filtering the index in order would touch nearly the whole table anyway, so a plain sequential scan followed by one sort of just the matches wins outright. Nothing about the query changed except the number after `LIMIT`; the plan answering it is a different shape, not a slower version of the same one.

## Practice

1. ▢ Predict whether the buffer count at `OFFSET 900000` is higher or lower than at `OFFSET 500000`, and why.

<details markdown="1"><summary>Check</summary>

Higher: `OFFSET 900000 LIMIT 20` reads `rows=900020.00` and touches 8984 buffers, against 500020 rows and 4993 buffers at `OFFSET 500000`. Buffers track the rows produced and discarded before any are kept, so the count grows with the offset, not with the twenty rows returned.

</details>

2. ▢ A page's last row, sorted by `customer_id` then `id`, is `(12, 2044)`. Predict what `WHERE customer_id >= 12 ORDER BY customer_id, id LIMIT 20` returns, against the correct keyset condition.

<details markdown="1"><summary>Hint</summary>

Ask which rows satisfy `customer_id >= 12` that the previous page already returned.

</details>

<details markdown="1"><summary>Check</summary>

It repeats rows: every order of customer 12 with `id` at or before `2044` still satisfies `customer_id >= 12`. The correct condition, `(customer_id, id) > (12, 2044)`, excludes exactly the already-seen rows.

</details>

3. ▢ `SELECT count(*) FROM (SELECT 1 FROM orders WHERE customer_id = 999999999 LIMIT 1000) s` runs against a `customer_id` matching nothing. Predict the number returned.

<details markdown="1"><summary>Check</summary>

`0`, the true count, not `1000` or an error. `LIMIT` only caps the count from above; when fewer matches exist than the bound, the scan simply runs out of rows first and reports exactly how many it found.

</details>

4. ▢ The same `ORDER BY amount DESC` query runs once with `LIMIT 20` and once with no `LIMIT` at all. Predict how the `Sort Method` line differs between the two.

<details markdown="1"><summary>Hint</summary>

One version can discard every row outside the top twenty as it goes; the other has to keep all of them.

</details>

<details markdown="1"><summary>Check</summary>

With `LIMIT 20` it is `Sort Method: top-N heapsort Memory: 26kB`, a small heap keeping only the current best twenty. With no `LIMIT`, sorting all 1049916 rows, it is `Sort Method: external merge Disk: 25656kB`, spilling to disk since every row has to be held, not just the winners.

</details>

5. ▢ `SELECT id, amount FROM orders LIMIT 20` runs with no `ORDER BY` at all. Predict the scan node and whether the twenty rows returned are the same on a repeated run.

<details markdown="1"><summary>Check</summary>

A plain `Seq Scan`, cheap at 2 buffers, reading whichever rows sit first in storage. Nothing promises those are the same twenty next time: without an `ORDER BY` there is no order to begin with, the same gap the warm-up named, minus even a tiebreaker to argue about.

</details>

6. ▢ A table is `ANALYZE`d at 50000 rows, then 20000 more rows are inserted with no further `ANALYZE`. Predict what `count(*)` and `reltuples` each report.

<details markdown="1"><summary>Check</summary>

`count(*)` reports `70000`, the true count, since it reads the rows that exist right now. `reltuples` still reports `50000`, the figure from the last `ANALYZE`, because nothing has refreshed it since; the estimate is only as current as its last statistics run, the drift the counting section named.

</details>

## Real-world reps

- [ ] Find a paginated list in code you maintain and check whether it sends a page number or a remembered key.
- [ ] Run `EXPLAIN (ANALYZE)` on a query of your own past a large `OFFSET`, and read its scan node's row count against the rows it actually returns.
- [ ] Tomorrow: pick one list in your own systems that uses `OFFSET`, and decide honestly whether its depth is bounded enough to leave alone or large enough to earn a keyset rewrite.

## Going further

- [7.6. LIMIT and OFFSET](https://www.postgresql.org/docs/current/queries-limit.html): the clause this lesson replaces past a shallow page
- [9.25.5. Row Constructor Comparison](https://www.postgresql.org/docs/current/functions-comparisons.html#ROW-WISE-COMPARISON): the `(a, b) > (x, y)` syntax behind a composite keyset condition
- [52.11. pg_class](https://www.postgresql.org/docs/current/catalog-pg-class.html): where `reltuples` lives
- [CREATE INDEX](https://www.postgresql.org/docs/current/sql-createindex.html): syntax for the composite index behind the keyset example
- [Performance](../reference/performance.md): the stage 6 reference sheet
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
