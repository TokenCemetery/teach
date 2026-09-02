---
title: 12. Common Table Expressions
description: WITH names a step so a long query reads top to bottom, and on this release it is not an optimisation fence
type: lesson
---

# Lesson 12. Common Table Expressions

**Mission link:** A query with three nested subqueries reads inside out, and a reviewer who cannot read it in order cannot review it. Naming each step turns that query into a short story a colleague can follow without a whiteboard.
**Primary source:** [PostgreSQL, 7.8 WITH Queries](https://www.postgresql.org/docs/current/queries-with.html)
**Prerequisites:** [Lesson 9](0009-aggregation-and-group-by.md), [Lesson 11](0011-subqueries.md)

## Warm-up

1. ▢ Lesson 11 wrote a derived table in `FROM` that grouped `orders` by `customer_id` and kept only the customers with more than two orders. What made that subquery need an alias, and where did the alias have to go?

<details markdown="1"><summary>Check</summary>

A subquery used as a table in `FROM` is a derived table, and PostgreSQL requires it to have a name so the outer query has something to call it by (in versions before PostgreSQL 16, an alias was mandatory rather than merely conventional). The alias goes immediately after the closing parenthesis: `(SELECT ... ) AS pre`. A CTE is the same computation given a name up front instead, which is this lesson's whole subject.

</details>

## Know this

### WITH names a step and writes it before the query that uses it

`WITH` introduces one or more named subqueries, written out in full before the statement that reads them. The name behaves like a table for the rest of the statement, used in `FROM` exactly as a real table or a derived table would be.

Take a question stage 2's tools can now answer: which customers have spent more than the average customer, and what is their country called? As a derived table, the per-customer total has to be computed twice, once to produce the rows and once inside the scalar subquery that computes the average to compare against:

```sql
SELECT c.email, t.total, n.name
FROM (
    SELECT customer_id, sum(amount) AS total
    FROM orders
    GROUP BY customer_id
) t
JOIN customers c ON c.id = t.customer_id
LEFT JOIN countries n ON n.code = c.country
WHERE t.total > (
    SELECT avg(total) FROM (
        SELECT customer_id, sum(amount) AS total
        FROM orders
        GROUP BY customer_id
    ) t2
)
ORDER BY t.total DESC;
```

As two named steps, the aggregation is written once, and the second step reads as "the average of the first step":

```sql
WITH customer_totals AS (
    SELECT customer_id, sum(amount) AS total
    FROM orders
    GROUP BY customer_id
),
average_total AS (
    SELECT avg(total) AS avg_total FROM customer_totals
)
SELECT c.email, ct.total, n.name
FROM customer_totals ct
JOIN customers c ON c.id = ct.customer_id
LEFT JOIN countries n ON n.code = c.country
CROSS JOIN average_total a
WHERE ct.total > a.avg_total
ORDER BY ct.total DESC;
```

Both return the same three rows on the fixture:

```
email                 | total   | name
----------------------+---------+--------------
katherine@example.com | 1019.99 | United States
radia@example.com     | 500.00  |
donald@example.com    | 365.75  | Japan
```

The result is identical, but the second version reads in the order a reader thinks about it: totals, then their average, then who beats it. The first version says the same thing inside out and repeats the aggregation, the kind of duplication that drifts out of sync when only one copy gets edited.

### A later CTE can read an earlier one

`average_total` above reads `customer_totals`, which is defined just before it in the same `WITH` list. That is not a special case; any CTE may reference any CTE that came earlier in the same list, and PostgreSQL accepts it:

```sql
WITH a AS (SELECT 1 AS x),
     b AS (SELECT x + 1 AS y FROM a)
SELECT * FROM b;
```

```
y
-
2
```

This is what turns `WITH` into a chain of named steps rather than a single named subquery: each step can build on the last, and a reader walks the chain in the order it executes instead of unwinding a nest of parentheses.

### The optimisation fence is gone, and the plan proves it

Older advice treats a CTE as an optimisation fence, a wall the planner will not see through, computed in full before anything downstream can use an index or a filter. That advice is out of date: verified on PostgreSQL 18.6, a `WITH` referenced exactly once is inlined, and the plan is identical to the same query written as a derived table.

```sql
EXPLAIN (COSTS OFF)
SELECT count(*) FROM (SELECT * FROM orders WHERE amount > 100) AS t;

EXPLAIN (COSTS OFF)
WITH recent AS (SELECT * FROM orders WHERE amount > 100)
SELECT count(*) FROM recent;
```

Both give the same plan, with no `CTE` node anywhere:

```
QUERY PLAN
-----------------------------------------
Aggregate
  ->  Seq Scan on orders
        Filter: (amount > '100'::numeric)
```

`MATERIALIZED` asks for the old behaviour explicitly, and the plan gains a `CTE` node:

```sql
EXPLAIN (COSTS OFF)
WITH recent AS MATERIALIZED (SELECT * FROM orders WHERE amount > 100)
SELECT count(*) FROM recent;
```

```
QUERY PLAN
-------------------------------------------
Aggregate
  CTE recent
    ->  Seq Scan on orders
          Filter: (amount > '100'::numeric)
  ->  CTE Scan on recent
```

`NOT MATERIALIZED` asks for inlining explicitly, and on a single reference it gives back the first plan, with no `CTE` node, since that is what would have happened anyway. The case worth remembering is the one a reader meets without writing either keyword: a CTE referenced twice is materialised automatically.

```sql
EXPLAIN (COSTS OFF)
WITH recent AS (SELECT * FROM orders WHERE amount > 100)
SELECT (SELECT count(*) FROM recent) AS a,
       (SELECT count(*) FROM recent WHERE shipped_at IS NOT NULL) AS b;
```

```
QUERY PLAN
------------------------------------------------
Result
  CTE recent
    ->  Seq Scan on orders
          Filter: (amount > '100'::numeric)
  InitPlan 2
    ->  Aggregate
          ->  CTE Scan on recent
  InitPlan 3
    ->  Aggregate
          ->  CTE Scan on recent recent_1
                Filter: (shipped_at IS NOT NULL)
```

One `CTE recent` node, computed once, and two `CTE Scan`s reading it. PostgreSQL's own release notes for version 12 list "automatic (but overridable) inlining of common table expressions" among that release's changes, which is where this behaviour started; the old advice that `WITH` is always a fence has been wrong since then.

### Asking for materialisation on purpose

Two situations are worth reaching for `MATERIALIZED` deliberately. The first is an expensive step used more than once, which is already materialised automatically, so the keyword only documents the intent. The second is a step used once whose result you want frozen, because another statement in the same transaction is changing the table it reads: inlining re-runs the CTE's definition at the point of use, so a genuine snapshot needs the keyword written. Neither case is a benchmark to quote; measure the query you actually have.

### A CTE can write, not only read

`WITH` can hold `INSERT`, `UPDATE` or `DELETE`, given `RETURNING`, and the result feeds the statement that follows:

```sql
WITH moved AS (
    UPDATE orders SET amount = amount WHERE id = 101 RETURNING id, amount
)
SELECT count(*) FROM moved;
```

```
count
-----
1
```

This is for chaining a write into whatever reads its result, an audit count, a second write keyed on what the first one touched, without a round trip back to the application in between. Two rules make it safe to reason about. Every statement in the `WITH` sees the same snapshot of the data, the one that existed when the outer statement began, so a later part of the same `WITH` cannot see an earlier part's write. And the order in which the statements execute is not something you control, so two data-modifying CTEs that touch the same rows should not be written expecting one to run before the other.

### Where a CTE stops helping

A chain of five CTEs, each just reading the previous one and renaming a column or two, is not automatically clearer than the query it replaced: five names to hold in mind can be worse than one nested shape. The discipline that keeps a `WITH` list worth reading is short: one step per CTE, named after what it produces, `customer_totals` rather than `t1`, `average_total` rather than `data`. A name that says nothing costs the reader exactly the benefit the CTE was meant to buy.

One more form exists and is worth knowing by name without learning it here: `RECURSIVE WITH`, which lets a CTE refer to itself to walk a hierarchy or a graph. It is stage 3's material.

## Practice

1. ▢ Rewrite this nested query as a single CTE with one clear name, without changing what it returns: `SELECT * FROM (SELECT customer_id, sum(amount) AS total FROM orders GROUP BY customer_id) x WHERE x.total > 100`.

<details markdown="1"><summary>Check</summary>

```sql
WITH customer_totals AS (
    SELECT customer_id, sum(amount) AS total
    FROM orders
    GROUP BY customer_id
)
SELECT * FROM customer_totals WHERE total > 100;
```

Same rows, same columns. The point of the exercise is the name: `customer_totals` says what the step produces, where `x` said nothing.

</details>

2. ▢ Predict whether `EXPLAIN` shows a `CTE` node for `WITH t AS (SELECT * FROM orders) SELECT count(*) FROM t WHERE amount > 50`, referenced once with no keyword, before running it.

<details markdown="1"><summary>Hint</summary>

The rule from this lesson depends on how many times `t` is referenced in the outer query, not on how the CTE is written.

</details>

<details markdown="1"><summary>Check</summary>

No `CTE` node. `t` is referenced exactly once, so PostgreSQL 18.6 inlines it, and the plan is a plain `Aggregate` over a `Seq Scan on orders` with the filter pushed down, identical to writing the derived table directly.

</details>

3. ▢ Add `MATERIALIZED` to the previous query's CTE and predict how the plan changes.

<details markdown="1"><summary>Check</summary>

A `CTE t` node appears, holding the `Seq Scan on orders` with no filter pushed into it, and the outer `Aggregate` reads from a `CTE Scan on t` that applies `amount > 50`. `MATERIALIZED` forces the CTE to be computed in full first, so the filter can no longer be pushed down into the scan that produces it.

</details>

4. ▢ Write a `WITH` list of two CTEs where the second references the first, using `orders`: one step that computes each customer's order count, a second that keeps only the customers with more than two orders. Predict the row count on the fixture.

<details markdown="1"><summary>Hint</summary>

Customer 1 has orders 101, 102 and 103; customer 4 has orders 106, 107 and 108. Lesson 9's join-and-group-by over the fixture is the same aggregation this asks for.

</details>

<details markdown="1"><summary>Check</summary>

```sql
WITH order_counts AS (
    SELECT customer_id, count(*) AS n
    FROM orders
    GROUP BY customer_id
),
frequent AS (
    SELECT * FROM order_counts WHERE n > 2
)
SELECT * FROM frequent;
```

Two rows: customer 1 with 3 orders and customer 4 with 3 orders. Every other customer in the fixture has at most two.

</details>

5. ▢ A colleague writes `WITH data AS (SELECT * FROM orders WHERE shipped_at IS NULL) SELECT * FROM data` and asks why `MATERIALIZED` did not change the plan when they added it as an experiment. Explain what they should have expected instead, and name the one thing definitely wrong regardless of the plan.

<details markdown="1"><summary>Check</summary>

Nothing wrong with the plan question: `MATERIALIZED` on a once-referenced CTE does change the plan, adding back the `CTE` node inlining removed. If they saw no change, check the reference count or the PostgreSQL version. What is definitely wrong is the name: `data` says nothing about what the step produces, costing the next reader exactly the clarity a CTE is meant to buy.

</details>

6. ▢ Predict the output of `WITH moved AS (UPDATE orders SET amount = amount WHERE id = 108 RETURNING id, amount) SELECT count(*) FROM moved`, then say what you must do to the fixture afterwards if you actually run it.

<details markdown="1"><summary>Check</summary>

`count` is 1, since exactly one row matches `id = 108` and `RETURNING` hands that one row to the outer `SELECT`. Because this is a write, even one that changes nothing, the fixture must be reloaded afterwards so the next reader sees the data the lesson describes.

</details>

## Real-world reps

- [ ] Find a query at work with a subquery nested two or three levels deep, and rewrite it as a `WITH` list, one CTE per step, each named after what it produces.
- [ ] Run `EXPLAIN` on a CTE you use more than once in the same query, and check whether the plan shows one `CTE` node or several separate scans of the underlying table.
- [ ] Tomorrow: look for a `WITH` block anyone on your team wrote with `t1`, `t2` or `data` as a name, and suggest a replacement that says what the step computes.

## Going further

- [7.8 WITH Queries](https://www.postgresql.org/docs/current/queries-with.html): the primary source, including the data-modifying and recursive forms
- [PostgreSQL 12 Release Notes](https://www.postgresql.org/docs/release/12.0/): the release that introduced automatic CTE inlining
- [INSERT, UPDATE, DELETE, MERGE](https://www.postgresql.org/docs/current/dml.html): the statements a data-modifying CTE can wrap
- [Querying](../reference/querying.md): the stage 2 reference sheet
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
