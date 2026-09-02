---
title: 10. HAVING, FILTER and Several Groupings at Once
description: Where a condition belongs decides which rows it can still see, and one pass can answer several groupings
type: lesson
---

# Lesson 10. HAVING, FILTER and Several Groupings at Once

**Mission link:** A condition in the wrong clause either fails with an error that looks unrelated to the mistake, or runs and silently answers a different question. `FILTER` and grouping sets let one query do what would otherwise take several.
**Primary source:** [PostgreSQL, SELECT](https://www.postgresql.org/docs/current/sql-select.html)
**Prerequisites:** [Lesson 2](0002-select-and-evaluation-order.md), [Lesson 9](0009-aggregation-and-group-by.md)

## Warm-up

1. ▢ Lesson 2's evaluation order runs `FROM`, `WHERE`, `GROUP BY`, `HAVING`, `SELECT`, `DISTINCT`, `ORDER BY`, `LIMIT`, always in that order. At which of those stages does the engine stop working with individual rows and start working with groups?

<details markdown="1"><summary>Check</summary>

At `GROUP BY`. Everything before it, `FROM` and `WHERE`, sees one row at a time. Everything from `GROUP BY` onward, including `HAVING`, sees a group: rows collapsed into one, with only the grouped columns and whatever an aggregate computes over them visible.

</details>

## Know this

### WHERE sees a row, HAVING sees a group

`WHERE` and `HAVING` both restrict which rows survive, and it is tempting to treat them as two spellings of one idea. They are not: `WHERE` runs before `GROUP BY` exists, so it can only test something true of one row, while `HAVING` runs after and tests something true of a whole group, usually an aggregate's result. The difference falls straight out of lesson 2's evaluation order.

Group the small dataset's orders by the customer's country and keep only the countries with more than two orders:

```sql
SELECT c.country, count(*) AS n, sum(o.amount) AS total
FROM customers c JOIN orders o ON o.customer_id = c.id
GROUP BY c.country
HAVING count(*) > 2
ORDER BY c.country;
```

```
country | n | total
--------+---+--------
GB      | 4 | 260.75
US      | 3 | 1019.99
```

`HAVING` ran after all five country groups already existed and discarded three of them. Now put a condition on the same column, `amount`, into `WHERE` instead:

```sql
SELECT c.country, count(*) AS n, sum(o.amount) AS total
FROM customers c JOIN orders o ON o.customer_id = c.id
WHERE o.amount > 50
GROUP BY c.country
ORDER BY c.country;
```

```
country | n | total
--------+---+-------
GB      | 2 | 200.50
JP      | 1 | 340.00
NL      | 1 | 60.00
US      | 1 | 999.99
        | 2 | 700.00
```

Five rows, not two, and the GB and US totals do not match the first query either. `WHERE` threw out every order of 50 or less before grouping happened, so the groups were built from fewer rows and every count and sum reflects that. `HAVING` never got a chance to remove a whole group here. These two queries answer different questions, and knowing which one you wrote means knowing when each clause runs.

### Three errors, each explained by what stage the query had reached

An aggregate in `WHERE`:

```sql
SELECT customer_id FROM orders WHERE count(*) > 1;
```

```
ERROR:  aggregate functions are not allowed in WHERE
SQLSTATE: 42803
```

`WHERE` runs before `GROUP BY`, so nothing has been collapsed into anything an aggregate could summarise; `count(*)` has no set of rows to count yet. The wording is the same whichever aggregate you try.

An ungrouped column in `HAVING`:

```sql
SELECT c.country, count(*)
FROM customers c JOIN orders o ON o.customer_id = c.id
GROUP BY c.country
HAVING o.amount > 100;
```

```
ERROR:  column "o.amount" must appear in the GROUP BY clause or be used in an aggregate function
SQLSTATE: 42803
```

By the time `HAVING` runs, the rows behind `o.amount` are already collapsed into groups, and a single order's amount is not a property of the whole group unless it is grouped or wrapped in an aggregate. This is lesson 9's rule again, enforced one clause later.

A nested aggregate:

```sql
SELECT c.country, count(count(*))
FROM customers c JOIN orders o ON o.customer_id = c.id
GROUP BY c.country;
```

```
ERROR:  aggregate function calls cannot be nested
SQLSTATE: 42803
```

An aggregate consumes a set of rows and produces one scalar. Feeding that scalar into another aggregate leaves the outer one with nothing resembling a set of rows to work over, since the inner call already consumed the only one there was. All three errors share SQLSTATE `42803`: a clause was given something it cannot have at the point it runs.

### One group, no GROUP BY, and a genuinely surprising result

`HAVING` does not require a `GROUP BY`. Without one, the whole table is treated as a single group, and `HAVING` can still reject it:

```sql
select count(*) from orders having count(*) > 5;
```

```
count
-----
12
```

Twelve passes, so the one group's row prints. Ask for something the data cannot satisfy:

```sql
select count(*) from orders having count(*) > 500;
```

```
(0 rows)
```

No output at all, not a row holding `0`. An aggregate query with no `GROUP BY` normally always answers with exactly one row, because there is always exactly one group, even an empty table has one, which is why `count(*)` on nothing is `0` rather than absent. `HAVING` is the one thing that can make an aggregate query answer with nothing: it filters groups after they exist, a table with no `GROUP BY` has exactly one, and rejecting that group leaves none.

### FILTER, a WHERE for a single aggregate

A report often needs several aggregates over different subsets of the same rows. `FILTER (WHERE ...)`, attached to one aggregate call, restricts only what that call sees, leaving every other aggregate in the same `SELECT` untouched:

```sql
SELECT c.country,
       count(*) AS all_orders,
       count(*) FILTER (WHERE o.shipped_at IS NOT NULL) AS shipped,
       sum(o.amount) FILTER (WHERE o.amount > 100) AS total_over_100
FROM customers c JOIN orders o ON o.customer_id = c.id
GROUP BY c.country
ORDER BY c.country;
```

```
country | all_orders | shipped | total_over_100
--------+------------+---------+---------------
GB      | 4          | 2       | 120.00
JP      | 2          | 1       | 340.00
NL      | 1          | 1       |
US      | 3          | 2       | 999.99
        | 2          | 2       | 700.00
```

NL's `total_over_100` is `NULL`, not `0`: no order from NL cleared 100, and `sum` over nothing is `NULL`, exactly as lesson 9 established for an empty group. `FILTER` did not change that rule, only which rows the aggregate saw.

The older way uses `CASE` inside the aggregate instead:

```sql
SELECT c.country,
       count(*) AS all_orders,
       sum(CASE WHEN o.shipped_at IS NOT NULL THEN 1 ELSE 0 END) AS shipped,
       sum(CASE WHEN o.amount > 100 THEN o.amount END) AS total_over_100
FROM customers c JOIN orders o ON o.customer_id = c.id
GROUP BY c.country
ORDER BY c.country;
```

Same five rows, same numbers, the same `NULL` for NL. `FILTER` reads as what it means, count these rows but only where a condition holds; `CASE` reads as an expression that happens to add up to the right count. Expect to meet the `CASE` form constantly in existing code even once `FILTER` is the one you write.

### Several groupings in one pass

A report needing a per-country breakdown and a grand total is usually written as two queries. `GROUPING SETS` produces both in one pass, one result for each set of columns listed:

```sql
SELECT country, count(*) AS n
FROM customers
GROUP BY GROUPING SETS ((country), ())
ORDER BY country;
```

```
country | n
--------+--
GB      | 2
JP      | 1
NL      | 1
US      | 2
        | 8
        | 2
```

Six rows: the five country groups a plain `GROUP BY country` would produce, plus a sixth row for the empty grouping `()`, a total over every customer, 8. `ROLLUP (country)` produces the same six rows more briefly, since rolling up one column is exactly the country groups plus the grand total:

```sql
SELECT country, count(*) AS n, grouping(country) AS g
FROM customers
GROUP BY ROLLUP (country)
ORDER BY country;
```

```
country | n | g
--------+---+--
GB      | 2 | 0
JP      | 1 | 0
NL      | 1 | 0
US      | 2 | 0
        | 8 | 1
        | 2 | 0
```

Here is the trap. Two rows print `country` as blank: the total row, where `country` is `NULL` because the grand total was never grouped by country at all, and the real group of customers whose `country` column genuinely is `NULL`. Nothing in the printed output distinguishes an aggregate over "everyone" from one over "everyone with no country on file", and mistaking one for the other is exactly the kind of error a report ships silently. `grouping(country)` tells them apart: `1` on the synthetic total row, `0` on every real group, including the real `NULL`-country one. Above, only `g = 1, n = 8` is the total; `g = 0, n = 2` is genuinely two customers with no country recorded. A grouping set is close in spirit to stacking several groupings into one result, though building it that way with an explicit set operation is a different lesson's tool.

### Portability

`GROUPING SETS` and `ROLLUP` are PostgreSQL only within this course: SQLite 3.51 rejects both before the query runs, one as a syntax error naming `SETS`, the other as an unrecognised function called `ROLLUP`, with no equivalent syntax to reach for instead. `FILTER (WHERE ...)`, by contrast, is accepted by both engines and behaves identically on each.

## Practice

1. ▢ Predict the exact row returned by grouping the join of `customers` and `orders` by `c.country` with `HAVING count(*) = 1`.

<details markdown="1"><summary>Check</summary>

One row: `NL`, `n = 1`. Per-country order counts are GB 4, JP 2, NL 1, US 3 and 2 for no country, so only NL has exactly one order.

</details>

2. ▢ Predict the SQLSTATE for `SELECT c.country FROM customers c JOIN orders o ON o.customer_id = c.id WHERE sum(o.amount) > 100 GROUP BY c.country;`.

<details markdown="1"><summary>Check</summary>

`42803`, message `aggregate functions are not allowed in WHERE`. It makes no difference which aggregate you write; `WHERE` runs before `GROUP BY`, so no aggregate has anything to work over yet.

</details>

3. ▢ Predict what `select count(*) from orders having count(*) > 20;` returns.

<details markdown="1"><summary>Hint</summary>

How many groups exist in this query when there is no `GROUP BY` at all, and what happens to that single group under `HAVING`?

</details>

<details markdown="1"><summary>Check</summary>

No rows at all, not a row containing `0`. Twelve is not greater than twenty, so the table's one implicit group fails the condition and `HAVING` discards it. An aggregate query with no `HAVING` always returns exactly one row; a `HAVING` the sole group fails is the one way to get none.

</details>

4. ▢ Using `FILTER`, count unshipped orders (`shipped_at IS NULL`) per country. Predict NL's value and say why it is not `NULL`, even though NL's earlier `sum(...) FILTER (WHERE amount > 100)` was.

<details markdown="1"><summary>Hint</summary>

Compare what `count(*)` returns over an empty set with what `sum` returns over the same empty set.

</details>

<details markdown="1"><summary>Check</summary>

```sql
SELECT c.country, count(*) FILTER (WHERE o.shipped_at IS NULL) AS unshipped
FROM customers c JOIN orders o ON o.customer_id = c.id
GROUP BY c.country
ORDER BY c.country;
```

NL's row is `0`. No unshipped order exists for NL, but `count(*)` always has an answer, even zero, exactly as it does over an empty group. `sum` needs at least one value to add and returns `NULL` when none pass the filter, which is why NL's earlier `sum(...) FILTER` result was `NULL` rather than `0`. Same missing data, different aggregate, different empty-case answer.

</details>

5. ▢ Using the `ROLLUP (country)` output shown in this lesson, predict what `grouping(country)` prints for the row where `country` is `NL`, and explain why.

<details markdown="1"><summary>Check</summary>

`0`. NL is a real group, not the synthetic total row. `grouping(country)` is `1` only on the row produced by the empty grouping `()`, where `country` was never part of the grouping at all.

</details>

6. ▢ You run the `ROLLUP (country)` query against SQLite instead of PostgreSQL. Predict what happens, and whether the failure matches `GROUPING SETS ((country), ())` run there.

<details markdown="1"><summary>Hint</summary>

Neither keyword is implemented on that engine, but "not implemented" can surface as more than one kind of error.

</details>

<details markdown="1"><summary>Check</summary>

Both fail, but not with the same wording: `GROUPING SETS` is a syntax error naming `SETS`, while `ROLLUP` is a call to a function that does not exist, since SQLite's parser reads `ROLLUP (country)` as an ordinary function call. Neither has a workaround; this material is PostgreSQL only.

</details>

## Real-world reps

- [ ] Find a query filtering on an aggregate-looking condition, a per-customer total or a per-day count, and check whether it sits in `WHERE` or `HAVING`. In the wrong one, it either fails or answers a narrower question than intended.
- [ ] Take a report that computes a conditional count or sum with `CASE WHEN ... THEN ... END` inside an aggregate, and rewrite it with `FILTER (WHERE ...)`. Confirm the numbers match.
- [ ] Tomorrow: find a report that runs a per-group query and a separate grand-total query side by side, and rewrite it as one query using `GROUPING SETS` or `ROLLUP`, checking `grouping()` to keep the total distinguishable from any real `NULL` group.

## Going further

- [SELECT, Grouping Sets](https://www.postgresql.org/docs/current/queries-table-expressions.html#QUERIES-GROUPING-SETS): full syntax for `GROUPING SETS`, `ROLLUP` and `CUBE`
- [4.2.8 Aggregate Expressions](https://www.postgresql.org/docs/current/sql-expressions.html#SYNTAX-AGGREGATES): where `FILTER` is defined
- [9.21 Aggregate Functions](https://www.postgresql.org/docs/current/functions-aggregate.html): `grouping()` alongside every other aggregate
- [Appendix A. PostgreSQL Error Codes](https://www.postgresql.org/docs/current/errcodes-appendix.html): where SQLSTATE `42803` is catalogued
- [Querying](../reference/querying.md): the stage 2 reference sheet
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
