---
title: 14. Window Functions
description: A window function computes across other rows without collapsing the one it is on
type: lesson
---

# Lesson 14. Window Functions

**Mission link:** A report that needs an order's own amount next to that customer's running total, or a row's rank among its peers, cannot get both from `GROUP BY`, which throws the row away to compute the total; a window function computes the total and keeps the row.
**Primary source:** [PostgreSQL, 3.5 Window Functions](https://www.postgresql.org/docs/current/tutorial-window.html)
**Prerequisites:** [Lesson 9](0009-aggregation-and-group-by.md), [Lesson 10](0010-having-and-filter.md)

## Warm-up

1. ▢ Lesson 9 established that `GROUP BY` collapses every row of a group into one output row. If a query needs each order's own amount printed next to that customer's total, can `GROUP BY` produce it in one pass?

<details markdown="1"><summary>Check</summary>

No. `GROUP BY customer_id` collapses a customer's three orders into one row, so there is no longer an "order's own amount" to print; only the aggregate survives. Getting both means either joining the grouped total back onto the ungrouped rows, or using a mechanism that computes the aggregate without collapsing anything, which is this lesson's subject.

</details>

## Know this

### A window function does not collapse anything

Over the whole `orders` table:

```sql
SELECT o.id, o.customer_id, o.amount, sum(o.amount) OVER () AS total
FROM orders o
ORDER BY o.id;
```

```
id  | customer_id | amount | total
----+-------------+--------+--------
101 | 1           | 120.00 | 2406.49
102 | 1           | 80.50  | 2406.49
103 | 1           | 15.00  | 2406.49
104 | 2           | 200.00 | 2406.49
105 | 3           | 45.25  | 2406.49
106 | 4           | 999.99 | 2406.49
107 | 4           | 10.00  | 2406.49
108 | 4           | 10.00  | 2406.49
109 | 5           | 60.00  | 2406.49
110 | 7           | 340.00 | 2406.49
111 | 7           | 25.75  | 2406.49
112 | 8           | 500.00 | 2406.49
```

All twelve rows survive, and all twelve carry `2406.49`, the total of every order. `count(*) OVER ()` on the same query puts `12` on every row for the same reason. Compare `SELECT sum(amount) FROM orders`, which returns that same `2406.49` but as the query's only row: a bare aggregate collapses, a window function does not. `OVER (...)` is what turns `sum` from an aggregate into a window function; the empty parentheses say the window is the whole table.

The mechanism: a window function is computed over a set of rows related to the current row, here the whole table, and the current row is then written out unchanged alongside that computed value. Nothing is thrown away; the aggregate rides along as an extra column instead of replacing the row.

### PARTITION BY: a GROUP BY that does not collapse

`OVER ()` treated every row as one set. `PARTITION BY` splits that set the way `GROUP BY` splits a table into groups, without discarding a single row:

```sql
SELECT o.customer_id, o.id, o.amount, sum(o.amount) OVER (PARTITION BY o.customer_id) AS cust_total
FROM orders o
ORDER BY o.customer_id, o.id;
```

```
customer_id | id  | amount | cust_total
------------+-----+--------+-----------
1           | 101 | 120.00 | 215.50
1           | 102 | 80.50  | 215.50
1           | 103 | 15.00  | 215.50
2           | 104 | 200.00 | 200.00
3           | 105 | 45.25  | 45.25
4           | 106 | 999.99 | 1019.99
4           | 107 | 10.00  | 1019.99
4           | 108 | 10.00  | 1019.99
5           | 109 | 60.00  | 60.00
7           | 110 | 340.00 | 365.75
7           | 111 | 25.75  | 365.75
8           | 112 | 500.00 | 500.00
```

Twelve rows in, twelve rows out, each carrying its own partition's total. A partition is a `GROUP BY` that does not collapse: the grouping logic is identical, but every row of every group is still there afterwards, each one now labelled with its group's aggregate.

### Ranking a tie: row_number, rank and dense_rank

The fixture's deliberate tie, orders 107 and 108 at `10.00`, both belonging to customer 4, is the clearest place to see the three ranking functions differ:

```sql
SELECT o.customer_id, o.id, o.amount,
       row_number() OVER (PARTITION BY o.customer_id ORDER BY o.amount DESC) AS rn,
       rank()       OVER (PARTITION BY o.customer_id ORDER BY o.amount DESC) AS rk,
       dense_rank() OVER (PARTITION BY o.customer_id ORDER BY o.amount DESC) AS drk
FROM orders o
ORDER BY o.customer_id, o.amount DESC, o.id;
```

```
customer_id | id  | amount | rn | rk | drk
------------+-----+--------+----+----+----
4           | 106 | 999.99 | 1  | 1  | 1
4           | 107 | 10.00  | 2  | 2  | 2
4           | 108 | 10.00  | 3  | 2  | 2
```

(customers 1, 2, 3, 5, 7 and 8 omitted; none of their orders tie). `row_number` hands out 1, 2, 3 with no regard for ties, so the two `10.00` rows land on 2 and 3 as if one genuinely outranked the other. `rank` gives peers the same number, 2 and 2, then skips the number a plain count would use next; there is no rank 3 in this partition. `dense_rank` also gives peers 2 and 2, but never skips: the next distinct amount gets 3, not 4. All three agree when nothing ties, and only `rank` leaves a gap after one.

Ranked globally instead of per customer, by amount ascending with no `PARTITION BY`, the same tie shows a sharper problem:

```sql
SELECT o.id, o.amount,
       row_number() OVER (ORDER BY o.amount) AS rn,
       rank()       OVER (ORDER BY o.amount) AS rk,
       dense_rank() OVER (ORDER BY o.amount) AS drk
FROM orders o
ORDER BY o.amount, o.id
LIMIT 4;
```

```
id  | amount | rn | rk | drk
----+--------+----+----+----
107 | 10.00  | 2  | 1  | 1
108 | 10.00  | 1  | 1  | 1
103 | 15.00  | 3  | 3  | 2
111 | 25.75  | 4  | 4  | 3
```

(the first four of twelve rows, ordered by amount then id; the other eight have no ties and add nothing new).

`rank` and `dense_rank` cope with the tie predictably, 1 and 1 either way, then 3 or 2 for the next distinct amount. `row_number` cannot cope at all: it must hand out two different numbers to two rows that its own `ORDER BY` calls equal, and nothing in the query says which row gets which. This run put 108 on 1 and 107 on 2; running it again could swap them. That is lesson 5's unstable tie, the one about text order having no defined result without a unique key, arriving at a ranking function instead of a sort.

The fix is the same one lesson 5 already taught: add a column that actually is unique to the window's `ORDER BY`, breaking the tie deterministically.

```sql
SELECT o.id, o.amount,
       row_number() OVER (ORDER BY o.amount, o.id) AS rn
FROM orders o
ORDER BY o.amount, o.id;
```

```
id  | amount | rn
----+--------+---
107 | 10.00  | 1
108 | 10.00  | 2
```

With `id` as a tiebreaker, `107` gets `1` and `108` gets `2` on every run, because no two rows are equal under `amount, id` together. `rank` and `dense_rank` were never in danger here, since a query only needs a `row_number` to be deterministic when it later relies on which specific row won the tie, for instance keeping exactly one row per group.

### Where a window function may run, and where it may not

```sql
SELECT o.id, o.amount
FROM orders o
WHERE row_number() OVER (ORDER BY o.amount DESC) <= 3;
```

```
ERROR:  window functions are not allowed in WHERE
SQLSTATE: 42P20
```

Lesson 2's evaluation order explains this rather than a bare rule explaining it away: `FROM`, `WHERE`, `GROUP BY` and `HAVING` all run before `SELECT`, and a window function is computed later still, once the rows that survive those stages are fixed. `WHERE` cannot filter on a value that does not exist yet at the point `WHERE` runs. The same reasoning rules it out of `HAVING` for an identical SQLSTATE, `42P20`, since `HAVING` also finishes before a window is computed.

A filter on a window result has to happen in a later query, one step removed. Wrapping the ranking in a derived table and filtering the alias outside it, where the window has already run and `rn` is an ordinary column, works:

```sql
SELECT *
FROM (
  SELECT o.id, o.customer_id, o.amount,
         row_number() OVER (PARTITION BY o.customer_id ORDER BY o.amount DESC) AS rn
  FROM orders o
) s
WHERE rn = 1
ORDER BY id;
```

Seven rows, one per customer with at least one order: ids 101, 104, 105, 106, 109, 110 and 112, each that customer's largest order. Lesson 12's `WITH` says the identical thing more readably, naming the ranked step instead of nesting it: `WITH ranked AS (... row_number() ...) SELECT ... FROM ranked WHERE rn = 1`, the same seven rows, the derived table given a name instead of a parenthesis.

### A window over grouped rows

One more consequence of that evaluation order is worth seeing run rather than stated: a window function can sit on top of an aggregate, because by the time the window is computed, `GROUP BY` has already finished collapsing the table.

```sql
SELECT customer_id, count(*), sum(count(*)) OVER () AS n_orders
FROM orders
GROUP BY customer_id
ORDER BY customer_id;
```

```
customer_id | count | n_orders
------------+-------+---------
1           | 3     | 12
2           | 1     | 12
3           | 1     | 12
4           | 3     | 12
5           | 1     | 12
7           | 2     | 12
8           | 1     | 12
```

Seven rows, one per customer with an order, `count(*)` on each the size of that customer's group, and `sum(count(*)) OVER ()` the same `12` on every one of them: the total across groups, not across the twelve original orders, though it happens to equal that here since every order belongs to exactly one customer's group. The rows the window sees are the groups themselves, not the rows that fed them; that is the clearest demonstration that a window runs after grouping, not instead of it.

### A portability note

Window functions are not a PostgreSQL extra. SQLite 3.51 accepts the same ranking and aggregate windows, `PARTITION BY` included, and also accepts a frame such as `ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW`, the subject of lesson 15; both were checked by loading a small table and running them there. A query written against this lesson's material is not PostgreSQL-specific.

## Practice

1. ▢ Predict the row count and the value in the `total` column for every row of the query below.

   ```sql
   SELECT o.id, sum(o.amount) OVER () AS total
   FROM orders o
   WHERE o.customer_id = 4
   ORDER BY o.id;
   ```

<details markdown="1"><summary>Hint</summary>

Decide what rows exist by the time the window runs before deciding what the window sums.

</details>

<details markdown="1"><summary>Check</summary>

Three rows, ids 106, 107 and 108, each showing `1019.99`. `WHERE` runs before the window, so only customer 4's own three orders are left for `OVER ()` to sum; the total is customer 4's total, not the whole table's `2406.49`, because the other rows were never there to be summed.

</details>

2. ▢ Predict the row count of the query below.

   ```sql
   SELECT o.customer_id, count(*) OVER (PARTITION BY o.customer_id) AS n
   FROM orders o
   WHERE o.customer_id = 6;
   ```

<details markdown="1"><summary>Check</summary>

Zero rows. Customer 6 has no orders at all, so `WHERE o.customer_id = 6` leaves nothing in `FROM orders o` for the window to run over; the partition and the count never get a chance to matter.

</details>

3. ▢ Continuing the globally-ranked tie in this lesson, predict `rank` and `dense_rank` for order 103, the next distinct amount above the tied pair.

<details markdown="1"><summary>Check</summary>

`rank` gives 103 the value 3, since `rank` counts the two tied rows ahead of it and then continues from there. `dense_rank` gives it 2, since `dense_rank` counts only that one distinct amount, `10.00`, as having come before.

</details>

4. ▢ Predict the exact error message and SQLSTATE of moving the `<= 3` filter on `row_number()` from `WHERE` into `HAVING` instead, on a query already grouped by `customer_id`.

<details markdown="1"><summary>Hint</summary>

`HAVING` finishes before `SELECT` too, exactly like `WHERE`.

</details>

<details markdown="1"><summary>Check</summary>

`ERROR: window functions are not allowed in HAVING`, SQLSTATE `42P20`, the identical code `WHERE` produces. `HAVING` filters groups before a window is computed, the same evaluation-order reason `WHERE` was rejected.

</details>

5. ▢ Predict the row count of the query below, and which customers appear.

   ```sql
   SELECT customer_id, count(*), count(*) OVER () AS n_groups
   FROM orders
   GROUP BY customer_id
   HAVING count(*) > 1
   ORDER BY customer_id;
   ```

<details markdown="1"><summary>Check</summary>

Three rows, customers 1, 4 and 7, the only ones with more than one order. `HAVING` removes the single-order customers' groups first; the window then runs over the three groups left, so `n_groups` reads 3 on every row rather than the unfiltered 7.

</details>

6. ▢ Predict which order id gets `row_number` 1 when the tied pair is ranked with `ORDER BY amount DESC, id`, rather than the ascending, tiebreaker-free version taught above.

<details markdown="1"><summary>Hint</summary>

`DESC` reverses the amount ordering; it does not touch how the tiebreaker column resolves the tie between the two equal amounts.

</details>

<details markdown="1"><summary>Check</summary>

Order 106, the `999.99` row, gets `row_number` 1, since it is the largest amount in the whole table, not one of the tied pair. The tied `10.00` rows fall to the last two positions, 11 and 12, with 107 still ahead of 108 because `id` breaks the tie the same way regardless of which end of the amount ordering they fall at.

</details>

## Real-world reps

- [ ] Find a report you maintain that currently joins a table to itself, or re-runs a subquery per row, to attach a total or a rank to each row, and rewrite it with a window function instead.
- [ ] Take a query that ranks rows with `row_number` and check whether its `ORDER BY` actually pins down a unique order; if not, add a tiebreaker and confirm the result stops changing between runs.
- [ ] Tomorrow: find one place at work where a value needs filtering by its rank or its running position, write it first with a window function in the outer position it belongs in, then check it against whatever the existing report does today.

## Going further

- [9.22 Window Functions](https://www.postgresql.org/docs/current/functions-window.html): the built-in list, including the ranking functions this lesson covers and the ones a later lesson picks up
- [4.2.8 Window Function Calls](https://www.postgresql.org/docs/current/sql-expressions.html#SYNTAX-WINDOW-FUNCTIONS): the syntax grammar behind `OVER`, `PARTITION BY` and a window's `ORDER BY`
- [7.2.5 Window Function Processing](https://www.postgresql.org/docs/current/queries-table-expressions.html#QUERIES-WINDOW): where window functions sit in evaluation order, the reason `WHERE` and `HAVING` cannot filter on one
- [Appendix A. PostgreSQL Error Codes](https://www.postgresql.org/docs/current/errcodes-appendix.html): where SQLSTATE `42P20` is catalogued
- [Beyond the basics](../reference/beyond-the-basics.md): the stage 3 reference sheet
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
