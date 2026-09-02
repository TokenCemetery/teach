---
title: 44. Reviewing a Query
description: Read the query for the rows it returns before reading it for speed, because a fast wrong answer is worse
type: lesson
---

# Lesson 44. Reviewing a Query

**Mission link:** A review comment is the last chance to stop a wrong query before it ships, and reading for speed before reading for correctness lets a fast wrong answer through.
**Primary source:** [PostgreSQL, 14.1 Using EXPLAIN](https://www.postgresql.org/docs/current/using-explain.html)
**Prerequisites:** [Lesson 9](0009-aggregation-and-group-by.md), [Lesson 35](0035-reading-a-plan.md)

## Warm-up

1. ▢ Lesson 9's fan-out bug joined `customers` to `orders` and then to `countries`, filtered only on `region = 'Europe'` with nothing relating an order to a specific country, and returned 7219.47 against a true 2406.49, three times too big because three country rows matched. If the filter had matched five countries instead, predict the total the same broken query would print.

<details markdown="1"><summary>Check</summary>

12032.45, five times the true 2406.49. The multiplier is exactly the number of matching country rows, which is why the bug worsens quietly as the lookup table grows, with no error at any size.

</details>

## Know this

### The order a review follows, and why

Read a query in this order and stop as soon as one step fails: what rows does it return, what does it do to `NULL`s and duplicates, what does the plan say, and what happens at a much larger table. The order is deliberate: a fast wrong answer is worse than a slow right one, so correctness comes before cost; and a plan cannot tell you the query answers the wrong question, since `EXPLAIN` only reports what the statement does. The four defects below are each caught at a different one of those steps, in the same order.

### What the rows themselves give away

Joining `customers` to `orders` and then to `countries` on `region = 'Europe'` alone, with no condition tying an order to a specific country, is lesson 9's fan-out bug, caught at the first step, before any `NULL` or any plan is in view:

```sql
SELECT count(*) AS n, sum(o.amount) AS total
FROM customers c
JOIN orders o ON o.customer_id = c.id
JOIN countries n ON n.region = 'Europe';
```

```text
n  | total
---+--------
36 | 7219.47
```

Against the true 12 and 2406.49 read straight from `orders`, this is wrong by exactly the three country rows the join found, not a rounding error a second glance would forgive. The comment: this joins every order to every European country row and sums the result, three times too big because nothing relates an order to a specific country; aggregate `orders` by `customer_id` before joining to `countries`, as lesson 9 showed. The second step catches what the first cannot, since a `NULL` does not always change a row count, only which rows survive:

```sql
SELECT id FROM customers WHERE id NOT IN (SELECT customer_id FROM orders UNION SELECT NULL);
```

```text
id
--
(0 rows)
```

Customer 6 has no orders and belongs in this list, but the query returns nothing at all, because `NOT IN` expands to a chain of `<>` and one `NULL` in the set makes every comparison unknown, lesson 11's trap exactly. `NOT EXISTS` asks the same question without building that list: `SELECT id FROM customers c WHERE NOT EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.id)` returns `6`, correctly, whatever the subquery holds. The comment: this returns nothing for every customer, including customer 6 who genuinely has no orders, because a `NULL` inside the subquery poisons every `NOT IN` comparison; rewrite as `NOT EXISTS`.

### What only the plan and a larger table give away

Some defects leave every row correct and hide until the third or fourth step. Filtering on a case-folded email, only a plain index on `email`:

```sql
SELECT id FROM customers WHERE lower(email) = 'customer50000@example.com';
```

```text
Seq Scan on customers (actual rows=1.00 loops=1)
  Filter: (lower(email) = 'customer50000@example.com'::text)
  Rows Removed by Filter: 99999
  Buffers: shared hit=834
```

The row that comes back is right. What is wrong is the cost: 834 buffers to read almost the whole 100000-row table for one match, since `lower(email)` is not the column the index was built on, lesson 38's leftmost-prefix problem once removed. `create index i44_lower_email on customers (lower(email))` turns this into a `Bitmap Heap Scan` touching four buffers; dropping the index afterwards returns the next run to the sequential scan. The comment: this filters on `lower(email)` with only a plain index on `email`, so every lookup reads the table end to end; add an expression index on `lower(email)`. A page far into a list shows the same pattern, correct rows and a cost the text does not hint at:

```sql
SELECT id, amount FROM orders ORDER BY id DESC LIMIT 20 OFFSET 500000;
```

```text
Limit (actual rows=20.00 loops=1)
  Buffers: shared hit=4993
  ->  Index Scan Backward using orders_pkey on orders (actual rows=500020.00 loops=1)
        Buffers: shared hit=4993
```

4993 buffers for twenty rows, because `OFFSET` produces and discards every row ahead of the page first, lesson 40's material. `WHERE id < 550905 ORDER BY id DESC LIMIT 20` answers the same page at 7 buffers, regardless of depth. The comment: page 25001 costs 4993 buffers because `OFFSET` walks and discards the 500000 rows ahead of it, growing with depth; switch to keyset pagination on `id`.

### What the plan adds to a review, and what it does not

Take the fan-out query back up and read its plan, not only its total. On the small table:

```text
Aggregate (actual rows=1.00 loops=1)
  Buffers: shared hit=3
  ->  Nested Loop (cost=28.23..116.52 rows=3600 width=16) (actual rows=36.00 loops=1)
        ->  Hash Join (cost=28.23..53.39 rows=1200 width=16) (actual rows=12.00 loops=1)
              Hash Cond: (o.customer_id = c.id)
        ->  Materialize (actual rows=3.00 loops=12)
              ->  Seq Scan on countries n (actual rows=3.00 loops=1)
                    Filter: (region = 'Europe'::text)
```

`Hash Join` estimated 1200 rows and produced 12, a hundredfold miss small-table statistics explain but do not excuse, and `Nested Loop` inherits it as 3600 estimated against 36 actual. That gap, the estimate against the actual at the node where they part, is the first thing worth checking in a plan: a planner this wrong about its own query may belong to an author just as wrong about the query itself. The second thing is whether the shape holds at a larger table, checked with a count rather than a timing: on the large fixture, `Parallel Hash Join` reports `actual rows=1049916.00` for each of three loops, 3149748 rows in total, still exactly three times the true 1049916 orders, the same multiplier the twelve-row table showed. The bug does not change shape with scale, only cost. What the plan cannot add, at either size, is whether three times too big was ever the right answer: `EXPLAIN` reports the join and the sum ran exactly as written, and a plan matching its query has nothing to say about whether that query matches the report it was meant to produce.

### Reviewing what you cannot run

Most review happens without a database in front of you, from the SQL text and, if you are lucky, a plan someone ran. Four questions travel with no data at all. What does this do with a `NULL`, on either side of a comparison, inside an `IN` list, or across a `GROUP BY`. Which side of a `LEFT JOIN` or `RIGHT JOIN` is kept, and does every condition sit in `ON` rather than `WHERE`. Does the `GROUP BY` key determine every other selected column through a primary key, or only look as if it does today. Is every predicate written so its column, not a function around it, is what an index could match. Where you can get more, ask for the plan and the row counts on each side.

### Writing the comment

A comment naming a style preference is easy to argue with and ignore; one naming the row that comes out wrong is neither. Weak: "this `NOT IN` subquery looks risky, `NULL`s can cause problems, maybe use something else." Good: "customer 6 has no orders and should be in this result, but the query returns zero rows for every customer, because the `NULL` `UNION` adds to the subquery poisons every `NOT IN` comparison; `NOT EXISTS` asks the same question and returns customer 6 correctly regardless of what the column holds." The good version names the row, gives the query producing the wrong answer, and proposes the rewrite rather than stopping at the objection: precision costs length, and it earns it here. This lesson keeps entirely to queries; reviewing a schema change is next.

## Practice

1. ▢ A report joins `orders` to `promotions` filtered only on `promotions.active = true`, nothing relating a promotion to the order, then sums `orders.amount`. Predict which review step catches this fastest, and why.

<details markdown="1"><summary>Check</summary>

The first: what rows does this return. A total far larger than `orders` itself holds is visible without a plan or a `NULL`, the signal the fan-out query gave at 36 rows against a true 12.

</details>

2. ▢ `SELECT country FROM customers WHERE country NOT IN (SELECT code FROM countries WHERE region = 'Asia')` means to list customers outside Asia. `countries.code` is `NOT NULL`; `customers.country` is not. Predict whether the query is safe, and which column's nullability actually matters.

<details markdown="1"><summary>Hint</summary>

`NOT IN` is poisoned by a `NULL` inside the subquery, not by a `NULL` on the side being tested.

</details>

<details markdown="1"><summary>Check</summary>

Safe. The subquery selects `countries.code`, `NOT NULL`, so no `NULL` enters the list `NOT IN` compares against; a nullable `customers.country` only means some output rows are `NULL`, a different and harmless thing.

</details>

3. ▢ A plan node estimates 40 rows, actual is 40000. Predict what that gap alone tells you, and what it does not.

<details markdown="1"><summary>Hint</summary>

An estimate is a guess made before running anything; neither it nor the actual says whether the query asked the right question.

</details>

<details markdown="1"><summary>Check</summary>

It tells you the planner badly misjudged this query, worth asking about on its own. It does not tell you 40000 is wrong: a plan can mis-estimate and still return the right rows, or estimate perfectly and still answer the wrong question.

</details>

4. ▢ A query filters `WHERE customer_id = 4242` and `WHERE lower(customer_email) = 'x'`, only `customer_id` indexed. Predict which filter to flag without running either, and what to ask for to confirm it.

<details markdown="1"><summary>Check</summary>

`lower(customer_email)`, since the existing index cannot serve a column wrapped in a function; ask for the plan, expecting a sequential scan with a large `Rows Removed by Filter`, the shape the expression-index case showed.

</details>

5. ▢ `SELECT c.id, email, sum(amount) FROM customers c JOIN orders o ON o.customer_id = c.id GROUP BY c.id` runs with no error. Predict why `email` needs no aggregate, and what would make the same shape unsafe.

<details markdown="1"><summary>Check</summary>

`c.id` is the primary key, so it determines exactly one `email`, lesson 9's functional dependency; grouping instead by a merely unique-looking column, such as `country`, would make the shape an error, since several rows could disagree on `email`.

</details>

6. ▢ Rewrite this comment to meet this lesson's standard: "the pagination here doesn't scale well, might want to look at it." Say in one sentence what it was missing.

<details markdown="1"><summary>Check</summary>

It named no row, no query and no fix. A satisfying version names the depth at which it gets expensive, shows the `OFFSET` query's buffer count, and proposes the keyset rewrite on the key `ORDER BY` already uses.

</details>

## Real-world reps

- [ ] Take a `NOT IN` subquery from a codebase you can read, and check by hand whether its column can ever hold a `NULL`.
- [ ] Find a join in a report you maintain, and check whether every predicate relating two tables actually does, rather than filtering one side alone as the fan-out example did.
- [ ] Tomorrow: leave one review comment on a real query in this lesson's format, naming the row or number that comes out wrong, the query that shows it, and the change you are proposing.

## Going further

- [9.24. Subquery Expressions](https://www.postgresql.org/docs/current/functions-subquery.html): `NOT IN` and `NOT EXISTS`, and the `NULL` behaviour that separates them
- [11.7. Indexes on Expressions](https://www.postgresql.org/docs/current/indexes-expressional.html): why a predicate wrapped in a function needs an index built the same way
- [7.6. LIMIT and OFFSET](https://www.postgresql.org/docs/current/queries-limit.html): the clause a deep page needs to stop using
- [69.1. Row Estimation Examples](https://www.postgresql.org/docs/current/row-estimation-examples.html): why a planner's estimate and the actual row count can disagree even on a plan that is otherwise correct
- [Operating](../reference/operating.md): the stage 7 reference sheet
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
