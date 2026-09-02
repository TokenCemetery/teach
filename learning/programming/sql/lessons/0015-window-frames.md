---
title: 15. Window Frames
description: The default frame includes every row that ties with the current one, which is why a running total can jump
type: lesson
---

# Lesson 15. Window Frames

**Mission link:** A running total written with just `ORDER BY` silently changes its meaning the moment two rows tie on the ordering column, because the frame it sums over is not the one most people assume; a report built on that assumption is wrong on exactly the rows that matter.
**Primary source:** [PostgreSQL, 4.2.8 Window Function Calls](https://www.postgresql.org/docs/current/sql-expressions.html#SYNTAX-WINDOW-FUNCTIONS)
**Prerequisites:** [Lesson 5](0005-sorting-and-collation.md), [Lesson 14](0014-window-functions.md)

## Warm-up

1. ▢ Lesson 14 established that `PARTITION BY` splits a query's rows into groups a window function computes over independently, and that without `PARTITION BY` the whole result set is one partition. When a window has no `ORDER BY` at all, what rows does a window function see for a given row: the whole partition, or something narrower?

<details markdown="1"><summary>Check</summary>

The whole partition. Without an `ORDER BY` there is no sequence to say which rows come before or after the current one, so PostgreSQL treats every row of the partition as visible to every other row; narrowing that set to something less than the whole partition only becomes possible once an `ORDER BY` gives the rows something to narrow along.

</details>

## Know this

### A frame is a subset of the partition, and with no ORDER BY it is the whole thing

A frame is the subset of the current partition that a frame-sensitive window function, one that means "so far" or "nearby" rather than "the whole group", actually reads for the current row. Verify the no-`ORDER BY` case directly:

```sql
SELECT customer_id, amount, sum(amount) OVER (PARTITION BY customer_id) AS partition_total
FROM orders
WHERE customer_id IN (1, 4)
ORDER BY customer_id, id;
```

```
customer_id | amount | partition_total
------------+--------+----------------
1           | 120.00 | 215.50
1           | 80.50  | 215.50
1           | 15.00  | 215.50
4           | 999.99 | 1019.99
4           | 10.00  | 1019.99
4           | 10.00  | 1019.99
```

Every row of customer 1 carries the same `215.50`, every row of customer 4 the same `1019.99`. With no `ORDER BY` there is nothing to narrow along, so the frame is the entire partition and the aggregate is the partition's total, not a running one. Add an `ORDER BY` and that stops being true, which is the rest of this lesson.

### The default frame, and why two spellings of "running total" disagree

Adding an `ORDER BY` narrows the frame, but not down to only the current row. The frame PostgreSQL picks when none is written out is `RANGE UNBOUNDED PRECEDING AND CURRENT ROW`, and `RANGE` counts every row that ties with the current one on the ordering column, not just the row itself. The fixture's orders 107 and 108 both cost `10.00`; whichever one is "current", the other is its peer, so the default frame includes both:

```sql
SELECT id, amount, sum(amount) OVER (ORDER BY amount) AS running_total
FROM orders
ORDER BY amount, id;
```

```
id  | amount | running_total
----+--------+--------------
107 | 10.00  | 20.00
108 | 10.00  | 20.00
103 | 15.00  | 35.00
111 | 25.75  | 60.75
105 | 45.25  | 106.00
109 | 60.00  | 166.00
102 | 80.50  | 246.50
101 | 120.00 | 366.50
104 | 200.00 | 566.50
110 | 340.00 | 906.50
112 | 500.00 | 1406.50
106 | 999.99 | 2406.49
```

Both `10.00` rows land on `20.00`, not `10.00` and `20.00`. This is the lesson's reason to exist: a running total written as plainly as `sum(amount) OVER (ORDER BY amount)` is silently a running total over peers, not over rows, and the two coincide only when the ordering column has no duplicate. Spelling the frame out with `ROWS` instead changes the answer:

```sql
SELECT id, amount,
       sum(amount) OVER (ORDER BY amount ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_total
FROM orders
ORDER BY amount, id;
```

```
id  | amount | running_total
----+--------+--------------
107 | 10.00  | 20.00
108 | 10.00  | 10.00
103 | 15.00  | 35.00
111 | 25.75  | 60.75
105 | 45.25  | 106.00
109 | 60.00  | 166.00
102 | 80.50  | 246.50
101 | 120.00 | 366.50
104 | 200.00 | 566.50
110 | 340.00 | 906.50
112 | 500.00 | 1406.50
106 | 999.99 | 2406.49
```

The same two rows now split into `10.00` and `20.00`, in whichever order PostgreSQL happens to place them, lesson 5's unstable tie arriving inside a frame: nothing in the query fixes which tied row counts as first, so which gets which is observable only by running it. The rule that follows: a running total written without an explicit frame is a running total over peers, and the moment the ordering column has a duplicate, `RANGE`'s default and `ROWS`'s explicit spelling disagree.

### Three frame modes, and the question each one honestly answers

`ROWS`, `RANGE` and `GROUPS` disagree about what "one preceding" means. Running the same bound in all three modes over the amount-ordered orders shows exactly where:

```sql
SELECT id, amount,
       sum(amount) OVER (ORDER BY amount ROWS   BETWEEN 1 PRECEDING AND CURRENT ROW) AS by_rows,
       sum(amount) OVER (ORDER BY amount RANGE  BETWEEN 1 PRECEDING AND CURRENT ROW) AS by_range,
       sum(amount) OVER (ORDER BY amount GROUPS BETWEEN 1 PRECEDING AND CURRENT ROW) AS by_groups
FROM orders
ORDER BY amount, id;
```

```
id  | amount | by_rows | by_range | by_groups
----+--------+---------+----------+----------
107 | 10.00  | 20.00   | 20.00    | 20.00
108 | 10.00  | 10.00   | 20.00    | 20.00
103 | 15.00  | 25.00   | 15.00    | 35.00
111 | 25.75  | 40.75   | 25.75    | 40.75
105 | 45.25  | 71.00   | 45.25    | 71.00
109 | 60.00  | 105.25  | 60.00    | 105.25
102 | 80.50  | 140.50  | 80.50    | 140.50
101 | 120.00 | 200.50  | 120.00   | 200.50
104 | 200.00 | 320.00  | 200.00   | 320.00
110 | 340.00 | 540.00  | 340.00   | 540.00
112 | 500.00 | 840.00  | 500.00   | 840.00
106 | 999.99 | 1499.99 | 999.99   | 1499.99
```

`ROWS` counts physical rows: "one preceding" takes the current row and whichever row sits immediately before it, tied or not, so the two `10.00` rows sum to `20.00` and `10.00` depending on which one goes first. `RANGE` counts by value: "one preceding" means every row whose amount is within `1` of the current one, so order 103 at `15.00` reaches back only to itself, since the nearest cheaper order, `10.00`, is more than `1` away. `GROUPS` counts peer groups: "one preceding" means the current peer group plus the one before it, so the running total is `20.00`, then `35.00`, then `40.75` as the amount climbs past each distinct value, treating the tied pair as a single step rather than two. Each mode answers a different question honestly: `ROWS` answers "what do the last N rows total, whatever their value", `RANGE` answers "what totals everything within this distance of the current value", and `GROUPS` answers "what do the last N distinct values, ties included, total".

`ROWS` is also the only one of the three that tolerates a missing `ORDER BY`: it just walks physical rows in whatever order the partition happens to hold, so `sum(amount) OVER (PARTITION BY customer_id ROWS BETWEEN 1 PRECEDING AND CURRENT ROW)` runs without one. `RANGE` and `GROUPS` both need an `ORDER BY` the moment their bound is anything other than `UNBOUNDED`, because "one preceding" has to mean something about a value or a peer group, and without an ordering neither exists.

### The bounds worth knowing, built and printed

The five bounds a frame can be written with are `UNBOUNDED PRECEDING`, `CURRENT ROW`, `n PRECEDING`, `n FOLLOWING` and `UNBOUNDED FOLLOWING`. A running total uses the first two:

```sql
SELECT id, amount,
       sum(amount) OVER (ORDER BY id ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_total
FROM orders
ORDER BY id;
```

```
id  | amount | running_total
----+--------+--------------
101 | 120.00 | 120.00
102 | 80.50  | 200.50
103 | 15.00  | 215.50
104 | 200.00 | 415.50
105 | 45.25  | 460.75
106 | 999.99 | 1460.74
107 | 10.00  | 1470.74
108 | 10.00  | 1480.74
109 | 60.00  | 1540.74
110 | 340.00 | 1880.74
111 | 25.75  | 1906.49
112 | 500.00 | 2406.49
```

A three-row moving average uses `n PRECEDING` and `n FOLLOWING` together:

```sql
SELECT id, amount,
       avg(amount) OVER (ORDER BY id ROWS BETWEEN 1 PRECEDING AND 1 FOLLOWING) AS moving_avg
FROM orders
ORDER BY id;
```

```
id  | amount | moving_avg
----+--------+----------------------
101 | 120.00 | 100.2500000000000000
102 | 80.50  |  71.8333333333333333
103 | 15.00  |  98.5000000000000000
104 | 200.00 |  86.7500000000000000
105 | 45.25  | 415.0800000000000000
106 | 999.99 | 351.7466666666666667
107 | 10.00  | 339.9966666666666667
108 | 10.00  |  26.6666666666666667
109 | 60.00  | 136.6666666666666667
110 | 340.00 | 141.9166666666666667
111 | 25.75  | 288.5833333333333333
112 | 500.00 | 262.8750000000000000
```

And "total still to come" uses `CURRENT ROW` and `UNBOUNDED FOLLOWING`:

```sql
SELECT id, amount,
       sum(amount) OVER (ORDER BY id RANGE BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING) AS still_to_come
FROM orders
ORDER BY id;
```

```
id  | amount | still_to_come
----+--------+--------------
101 | 120.00 | 2406.49
102 | 80.50  | 2286.49
103 | 15.00  | 2205.99
104 | 200.00 | 2190.99
105 | 45.25  | 1990.99
106 | 999.99 | 1945.74
107 | 10.00  | 945.75
108 | 10.00  | 935.75
109 | 60.00  | 925.75
110 | 340.00 | 865.75
111 | 25.75  | 525.75
112 | 500.00 | 500.00
```

It counts down from the grand total `2406.49` to the last row's own `500.00`, the mirror image of a running total.

One clause worth knowing without a section of its own: `EXCLUDE CURRENT ROW`, written after any frame, removes the current row from its own frame while leaving every other bound exactly as computed. Over the tied `10.00` orders, adding it to the default frame changes the answer:

```sql
SELECT id, amount,
       sum(amount) OVER (ORDER BY amount RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS default_frame,
       sum(amount) OVER (ORDER BY amount RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW EXCLUDE CURRENT ROW) AS everyone_else
FROM orders
WHERE amount <= 15
ORDER BY amount, id;
```

```
id  | amount | default_frame | everyone_else
----+--------+---------------+--------------
107 | 10.00  | 20.00         | 10.00
108 | 10.00  | 20.00         | 10.00
103 | 15.00  | 35.00         | 20.00
```

Each `10.00` row now reports `10.00` instead of `20.00`, because its peer is still counted but it no longer counts itself. `EXCLUDE` exists for exactly this: a "total of everyone else so far", which the default frame cannot express because it always counts the current row.

### A frame measured in an interval, the form a real report needs

`RANGE` can also take an interval as its bound when the ordering column is a timestamp, which is what a genuine "trailing seven days" report needs rather than a fixed number of rows:

```sql
SELECT id, amount, shipped_at::text,
       sum(amount) OVER (ORDER BY shipped_at RANGE BETWEEN INTERVAL '7 days' PRECEDING AND CURRENT ROW) AS trailing_7d
FROM orders
WHERE shipped_at IS NOT NULL
ORDER BY shipped_at;
```

```
id  | amount | shipped_at             | trailing_7d
----+--------+------------------------+------------
101 | 120.00 | 2026-01-05 09:00:00+00 | 120.00
102 | 80.50  | 2026-01-09 09:00:00+00 | 200.50
104 | 200.00 | 2026-01-11 09:00:00+00 | 400.50
106 | 999.99 | 2026-02-01 09:00:00+00 | 999.99
107 | 10.00  | 2026-02-02 09:00:00+00 | 1009.99
109 | 60.00  | 2026-02-14 09:00:00+00 | 60.00
111 | 25.75  | 2026-03-01 09:00:00+00 | 25.75
112 | 500.00 | 2026-03-03 09:00:00+00 | 525.75
```

`RANGE` is the mode that makes this possible, and neither of the other two could: its bound is a distance measured in the ordering column's own units, so PostgreSQL requires exactly one ordering column, and one whose type supports subtraction, since "seven days preceding" is only meaningful if subtracting two timestamps produces something an interval can be compared against. `ROWS` has no such requirement, and no such power: it cannot see dates at all, only positions.

## Practice

1. ▢ Predict the two values `sum(amount) OVER (PARTITION BY customer_id ORDER BY amount)` gives for customer 4's two `10.00` orders, and say which rule from this lesson you used.

<details markdown="1"><summary>Check</summary>

Both give `20.00`. Adding `PARTITION BY` restricts the peers to customer 4's own rows, but the default frame rule is unchanged: `RANGE UNBOUNDED PRECEDING AND CURRENT ROW` still counts every peer of the current row within that partition, and both `10.00` orders are each other's peer.

</details>

2. ▢ Predict what `count(*) OVER (ORDER BY amount ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)` gives for the fixture's two `10.00` orders, compared with the same window using `RANGE` in place of `ROWS`.

<details markdown="1"><summary>Check</summary>

`ROWS` gives them `1` and `2`, one row's count including only itself and the other including both, but which tied row gets which count is not fixed by the query, only observable by running it. `RANGE` gives both `2`, since it counts every peer of the current row regardless of physical position, and a tied row is always its own peer.

</details>

3. ▢ Predict the exact SQLSTATE the query below produces, and name the rule it breaks.

   ```sql
   SELECT sum(amount) OVER (PARTITION BY customer_id GROUPS BETWEEN 1 PRECEDING AND CURRENT ROW)
   FROM orders;
   ```

<details markdown="1"><summary>Hint</summary>

One of the three frame modes never needs an `ORDER BY`; the other two need one the moment their bound is not `UNBOUNDED`.

</details>

<details markdown="1"><summary>Check</summary>

`42P20`, "GROUPS mode requires an ORDER BY clause". `GROUPS` counts peer groups, and without an `ORDER BY` there is no ordering to group rows into peers by, only one partition-sized group; `ROWS` would have run, since it only needs physical row order, which a partition always has.

</details>

4. ▢ Predict `avg(amount) OVER (PARTITION BY customer_id ORDER BY id ROWS BETWEEN 1 PRECEDING AND 1 FOLLOWING)` for customer 7's two orders, ids 110 and 111, and say why both give the same number despite neither having both a preceding and a following neighbour.

<details markdown="1"><summary>Check</summary>

Both give `182.8750000000000000`. Order 110 has no row before it in the partition and order 111 has no row after it, but a frame that asks for a neighbour that does not exist simply ends up with fewer rows rather than an error or a `NULL`; with only two rows in the partition, both frames end up covering the same two rows.

</details>

5. ▢ The interval frame in this lesson used `INTERVAL '7 days'`. Predict the new value for order 106, shipped `2026-02-01`, if the interval widens to `INTERVAL '30 days'`.

<details markdown="1"><summary>Hint</summary>

Work out which earlier shipped orders now fall within 30 days of `2026-02-01`, not just within 7.

</details>

<details markdown="1"><summary>Check</summary>

`1400.49`. Orders 101, 102 and 104 all shipped between `2026-01-05` and `2026-01-11`, which is within 30 days of `2026-02-01` though outside 7, so their amounts, `120.00 + 80.50 + 200.00`, join order 106's own `999.99`.

</details>

6. ▢ Predict the value of `sum(amount) OVER (ORDER BY amount RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW EXCLUDE CURRENT ROW)` for order 103, `amount = 15.00`, and compare it with the same frame's value without `EXCLUDE CURRENT ROW`.

<details markdown="1"><summary>Hint</summary>

`EXCLUDE` only removes rows already inside the frame; it cannot add a row the frame's own start and end do not reach.

</details>

<details markdown="1"><summary>Check</summary>

`20.00` with `EXCLUDE CURRENT ROW`, against `35.00` without it. The default frame sums order 103 together with both `10.00` orders that precede it in amount, `10.00 + 10.00 + 15.00`; `EXCLUDE CURRENT ROW` removes only order 103's own `15.00`, leaving the two `10.00` peers it still frames as preceding it.

</details>

## Real-world reps

- [ ] Find a running total or a moving average in a report you maintain and check whether it is written with an explicit frame or is relying on the default; if the ordering column can ever tie, work out what the default frame would silently do to it.
- [ ] Take a report that currently computes "amount so far" by summing rows in application code and rewrite it as one query with an explicit `ROWS` frame, checking that the totals match row for row.
- [ ] Tomorrow: find one metric at work defined as "trailing N days" and check whether it is currently computed with a fixed row count or a genuine date range; if it is a row count, work out whether the two can disagree on a week with a gap or a spike.

## Going further

- [4.2.8. Window Function Calls](https://www.postgresql.org/docs/current/sql-expressions.html#SYNTAX-WINDOW-FUNCTIONS): the full frame grammar, including every `EXCLUDE` option and the `RANGE` offset rules this lesson only summarised
- [9.22. Window Functions](https://www.postgresql.org/docs/current/functions-window.html): the built-in window function reference, including the ones whose default frame lesson 16 has to work around
- [3.5. Window Functions](https://www.postgresql.org/docs/current/tutorial-window.html): the tutorial introduction, a gentler second pass over partitions and frames
- [SELECT](https://www.postgresql.org/docs/current/sql-select.html): the complete syntax reference, including the `WINDOW` clause lesson 16 needs
- [Beyond the basics](../reference/beyond-the-basics.md): the stage 3 reference sheet
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
