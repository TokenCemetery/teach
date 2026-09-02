---
title: 16. Navigating Within a Window
description: lag, lead and the value functions reach other rows directly, and two of them obey the frame
type: lesson
---

# Lesson 16. Navigating Within a Window

**Mission link:** A report that computes "change from the previous order" or "this customer's largest order, on every row" needs a function that reaches sideways to another row, and two of the most common ones quietly return the current row's own value instead if the reader does not know they obey the frame.
**Primary source:** [PostgreSQL, 9.22 Window Functions](https://www.postgresql.org/docs/current/functions-window.html)
**Prerequisites:** [Lesson 14](0014-window-functions.md), [Lesson 15](0015-window-frames.md)

## Warm-up

1. ▢ Lesson 15 established the default frame a window gets with an `ORDER BY` but no explicit frame clause. State it, and say which row it always includes no matter where in the partition the current row sits.

<details markdown="1"><summary>Check</summary>

The default frame is `RANGE UNBOUNDED PRECEDING AND CURRENT ROW`: everything from the start of the partition up to the current row and its peers. It always includes the current row itself, since that is the frame's end point, and that single fact is what makes two of this lesson's functions return something unexpected.

</details>

## Know this

### `lag` and `lead` reach the partition directly, and ignore the frame

`lag` and `lead` walk to a row a fixed number of positions away in the partition's `ORDER BY`, and hand back its value:

```sql
SELECT customer_id, id, amount,
       lag(amount) OVER (PARTITION BY customer_id ORDER BY id) AS prev_amount,
       lead(amount) OVER (PARTITION BY customer_id ORDER BY id) AS next_amount
FROM orders
ORDER BY customer_id, id;
```

```
customer_id | id  | amount | prev_amount | next_amount
------------+-----+--------+-------------+------------
1           | 101 | 120.00 |             | 80.50
1           | 102 | 80.50  | 120.00      | 15.00
1           | 103 | 15.00  | 80.50       |
2           | 104 | 200.00 |             |
3           | 105 | 45.25  |             |
4           | 106 | 999.99 |             | 10.00
4           | 107 | 10.00  | 999.99      | 10.00
4           | 108 | 10.00  | 10.00       |
5           | 109 | 60.00  |             |
7           | 110 | 340.00 |             | 25.75
7           | 111 | 25.75  | 340.00      |
8           | 112 | 500.00 |             |
```

Every blank cell is `NULL`: customer 1's first order has no earlier one, so `lag` gives `NULL`; its last order has no later one, so `lead` gives `NULL`. A single-order partition, customer 2, 3, 5 or 8, is `NULL` both sides.

Both functions take two more arguments, an offset and a default to use instead of `NULL`. `lag(amount, 2, '0')` reaches back two rows rather than one, falling back to `0` when there is no such row:

```sql
SELECT customer_id, id, amount, lag(amount, 2, '0') OVER (PARTITION BY customer_id ORDER BY id) AS lag2
FROM orders
ORDER BY customer_id, id;
```

Customer 1's three orders get `0`, `0`, `120.00`, since only the third row has one two positions behind it; customer 4's three get `0`, `0`, `999.99`, and every customer with one or two orders gets `0` throughout.

The fact that separates these two from the value functions below: `lag` and `lead` address the partition by position and never consult the frame. Narrowing the frame to `ROWS BETWEEN CURRENT ROW AND CURRENT ROW`, which restricts a value function to the current row alone, changes nothing about what `lag` returns; it still reaches the previous row exactly as before. That makes `lag` and `lead` the safe pair: their answer never depends on a frame clause the reader forgot to write.

### `first_value` and `last_value`, and the trap

`first_value` and `last_value` are not safe the same way, since they read the frame rather than the partition. Over `customer_id` partitions ordered by `amount`:

```sql
SELECT customer_id, id, amount,
       first_value(amount) OVER (PARTITION BY customer_id ORDER BY amount) AS first_amount,
       last_value(amount) OVER (PARTITION BY customer_id ORDER BY amount) AS last_amount
FROM orders
ORDER BY customer_id, amount;
```

```
customer_id | id  | amount | first_amount | last_amount
------------+-----+--------+--------------+------------
1           | 103 | 15.00  | 15.00        | 15.00
1           | 102 | 80.50  | 15.00        | 80.50
1           | 101 | 120.00 | 15.00        | 120.00
2           | 104 | 200.00 | 200.00       | 200.00
3           | 105 | 45.25  | 45.25        | 45.25
4           | 108 | 10.00  | 10.00        | 10.00
4           | 107 | 10.00  | 10.00        | 10.00
4           | 106 | 999.99 | 10.00        | 999.99
5           | 109 | 60.00  | 60.00        | 60.00
7           | 111 | 25.75  | 25.75        | 25.75
7           | 110 | 340.00 | 25.75        | 340.00
8           | 112 | 500.00 | 500.00       | 500.00
```

`first_value` behaves the way its name suggests: customer 1's smallest order, 15.00, appears on every one of that customer's rows. `last_value` does not: instead of the partition's largest, every row gets its own amount back, 15.00 on the 15.00 row and 120.00 on the 120.00 row. This is the warm-up's fact with a consequence: the default frame ends at the current row, so `last_value`'s "last row of the frame" is the current row itself throughout, and the function is doing exactly what it was asked.

Naming the frame fixes it. Widening it to the whole partition with lesson 15's `ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING` makes `last_value` return the partition's actual largest on every row: 120.00 for customer 1, 999.99 for customer 4.

The rule underneath both: a value function is only as wide as its frame. `first_value` looked right with the default frame only because the smallest row is also the frame's first row from the outset; `last_value` had no such luck, since the frame's last row is always the current one until told otherwise. Whenever the intended answer is "the whole partition's first or last", name the frame.

### `nth_value` needs the same widening, for the same reason

`nth_value(amount, 2)` asks for the second value in the frame. Ordered by `id` with no explicit frame, the first row's frame is only itself, so there is no second value and the result is `NULL` there alone; from the second row on, the frame has grown enough and the answer settles at 80.50, order 102's amount. Widening the frame the same way as before makes every row see the same full set and report 80.50, the second amount by `id` order over the whole table. `nth_value` fails the same way `last_value` did and for the identical reason: a value function reports on the frame it is given, not the partition, and a frame that has not finished growing is not the same as one that has.

### The distribution functions: where a row sits, not what it holds

`ntile`, `percent_rank` and `cume_dist` answer a different question: not what value is elsewhere, but where the current row sits in the distribution. `ntile(4)` splits the twelve orders, in ascending `amount` order, into four buckets of three: cheapest three in bucket 1, next three in bucket 2, and so on to the costliest three in bucket 4.

`percent_rank` and `cume_dist` are both fractions between 0 and 1: `percent_rank` is how far into the ordering a row sits, 0 for the first, 1 for the last; `cume_dist` is the fraction of rows at or before this one, so it never reaches 0. Ordered by `amount`, the first four rows give `percent_rank` 0.000, 0.000, 0.182, 0.273 and `cume_dist` 0.167, 0.167, 0.250, 0.333; the tied 10.00 orders share the same value on both, since neither function can tell them apart.

Both return `double precision`, and rounding one directly fails:

```sql
SELECT round(percent_rank() OVER (ORDER BY amount), 3) FROM orders LIMIT 1;
```

```
ERROR:  function round(double precision, integer) does not exist
HINT:  No function matches the given name and argument types. You might need to add explicit type casts.
SQLSTATE: 42883
```

A reader who has only rounded a `numeric` before will hit this in their first minute. The fix is a cast, not a different function: `round(percent_rank() OVER (ORDER BY amount)::numeric, 3)` runs and gives the values above.

### Naming a window once with `WINDOW`, so two uses cannot drift apart

A window repeated across several expressions in one query can be named once instead:

```sql
SELECT o.customer_id, o.id, o.amount,
       avg(o.amount) OVER w AS customer_avg,
       o.amount - avg(o.amount) OVER w AS deviation
FROM orders o
WINDOW w AS (PARTITION BY o.customer_id)
ORDER BY o.customer_id, o.id;
```

Customer 1's rows all report the same average, 71.8333333333333333, and each row's own deviation from it; customer 4's average is 339.9966666666666667, well below the 999.99 order. Both `OVER w` references share one definition. A named window can also be extended: `sum(o.amount) OVER (w ORDER BY o.id)` adds an ordering on top of `w`'s partitioning for a running total, alongside `avg(o.amount) OVER w`'s flat average, without repeating the partition clause.

What this buys is not brevity but safety: two windows written out separately, one for the average and one for the deviation, are two places an edit can touch only one, and the query keeps running while quietly comparing a row against the wrong group. A window named once cannot drift, since there is only one definition to edit.

### This travels: SQLite has the same functions

Unlike lesson 10's grouping-set material, none of this is PostgreSQL-only. Running the same fixture on SQLite 3.51, `lag`, `lead`, `first_value` and `last_value` behave identically, default-frame trap included: `last_value` gives each row its own amount until the frame is widened, then 120.00 for customer 1 and 999.99 for customer 4, matching PostgreSQL exactly. `ntile`, `percent_rank`, `cume_dist` and the `WINDOW` clause all run there too, with the same buckets and fractions. One difference: SQLite's `round` accepts a plain floating-point argument, so the cast just taught is a PostgreSQL-specific step, not a universal one; it does no harm to write it anyway on the engine that does not require it.

## Practice

1. ▢ Predict the exact value, including its printed form, of `lag(amount, 1, -1) OVER (PARTITION BY customer_id ORDER BY id)` for customer 5's single order.

<details markdown="1"><summary>Hint</summary>

Compare this to `lag(amount, 2, '0')` earlier in the lesson: the fallback value's own type decides how it prints, not the column it is standing in for.

</details>

<details markdown="1"><summary>Check</summary>

`-1`, not `-1.00`. Customer 5 has only one order, so the fallback fires, and a plain integer literal keeps its own printed form rather than adopting `amount`'s two-decimal display.

</details>

2. ▢ The first-value-and-last-value query in this lesson orders each partition by `amount` ascending. Predict what changes in `first_amount` and `last_amount` for customer 1 and customer 4 if the `ORDER BY` inside both `OVER` clauses is reversed to `amount DESC`, everything else unchanged.

<details markdown="1"><summary>Check</summary>

`first_amount` becomes each customer's largest order, 120.00 for customer 1 and 999.99 for customer 4, since `first_value` returns the frame's first row in whatever order the window was given. `last_amount` still shows each row's own amount: reversing the order changes which row is first, not where the default frame ends, so the trap is unaffected by the sort direction.

</details>

3. ▢ Predict the value of `last_value(amount) OVER (ORDER BY amount ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING)` on every row, if `PARTITION BY customer_id` is dropped entirely from that window.

<details markdown="1"><summary>Hint</summary>

Dropping `PARTITION BY` does not remove the frame; it changes how many rows the frame is drawn from.

</details>

<details markdown="1"><summary>Check</summary>

999.99 on all twelve rows. With no `PARTITION BY`, the whole table is one partition, so the widened frame spans every order, and order 106's 999.99 is the largest anywhere.

</details>

4. ▢ Predict the exact error message and SQLSTATE of `SELECT round(cume_dist() OVER (ORDER BY amount), 3) FROM orders LIMIT 1;`.

<details markdown="1"><summary>Check</summary>

`ERROR: function round(double precision, integer) does not exist`, SQLSTATE `42883`, identical to `percent_rank`'s error earlier: `cume_dist` returns the same `double precision` type, so the same cast to `numeric` is needed first.

</details>

5. ▢ Ordered by `amount` ascending, order 106 at 999.99 is the largest of the twelve. Predict which bucket `ntile(3)` puts it in, and how many rows share that bucket.

<details markdown="1"><summary>Hint</summary>

Twelve rows split three ways is not the same split as twelve rows split four ways.

</details>

<details markdown="1"><summary>Check</summary>

Bucket 3, along with three other rows. `ntile(3)` divides the twelve orders into buckets of four rather than three, so the costliest quarter, not the costliest third, shares order 106's bucket.

</details>

6. ▢ In the `WINDOW` example, predict whether `customer_avg` changes from row to row within one customer, and whether `sum(o.amount) OVER (w ORDER BY o.id)` does.

<details markdown="1"><summary>Check</summary>

`customer_avg` stays constant across a customer's rows, since `w` has no `ORDER BY`, so its frame is the whole partition throughout. `sum(o.amount) OVER (w ORDER BY o.id)` does change row by row, because adding an `ORDER BY` to `w` gives that expression a running-total frame while `w`'s partitioning still applies.

</details>

## Real-world reps

- [ ] Find a report that computes "change from the previous row" by self-joining a table to itself, and rewrite it with `lag` or `lead`, checking the row count is unchanged.
- [ ] Find a query that uses `last_value`, `first_value` or `nth_value` without an explicit frame, and check by hand whether the default frame gives the right answer or only looks like it does.
- [ ] Tomorrow: pick one dashboard metric described as "this row's rank in the distribution" and decide whether `ntile`, `percent_rank` or `cume_dist` is the one it needs.

## Going further

- [3.5. Window Functions](https://www.postgresql.org/docs/current/tutorial-window.html): the tutorial introduction this lesson's reference chapter assumes
- [SELECT](https://www.postgresql.org/docs/current/sql-select.html): the complete syntax reference, including the `WINDOW` clause's grammar
- [Window Functions](https://www.sqlite.org/windowfunctions.html): SQLite's own account of the same functions, useful for checking what carries over
- [Appendix A. PostgreSQL Error Codes](https://www.postgresql.org/docs/current/errcodes-appendix.html): where SQLSTATE `42883` is catalogued
- [Beyond the basics](../reference/beyond-the-basics.md): the stage 3 reference sheet
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
