---
title: 11. Subqueries, and Which Kind Answers the Question
description: A scalar, an IN, an EXISTS and a derived table answer four different questions, and one of them lies when NULL appears
type: lesson
---

# Lesson 11. Subqueries, and Which Kind Answers the Question
**Mission link:** A report that filters customers by their orders, or picks out the largest order, needs a query nested inside a query. Four shapes exist and answer four different questions; reaching for the wrong one, especially `NOT IN`, produces a query silently wrong on data it has never seen.
**Primary source:** [PostgreSQL, 9.24 Subquery Expressions](https://www.postgresql.org/docs/current/functions-subquery.html)
**Prerequisites:** [Lesson 3](0003-null-and-three-valued-logic.md), [Lesson 9](0009-aggregation-and-group-by.md)

## Warm-up

1. ▢ Lesson 3 established that `NOT IN` against a set containing a `NULL` returns no rows at all, whatever else is in the set. Why does one `NULL` poison the whole comparison, rather than just the row it came from?

<details markdown="1"><summary>Check</summary>

`NOT IN (a, b, NULL)` means `<> a AND <> b AND <> NULL`. The last comparison is always unknown, and `true AND unknown` is unknown, so the whole expression can never come out true, for any row, once a single `NULL` sits in the list. It is not the row that is poisoned; it is the comparison itself.

</details>

## Know this

A subquery is a `SELECT` nested inside another query, and PostgreSQL gives it four distinct shapes. They look similar and answer different questions, so the choice between them, not the syntax of any one, is the subject of this lesson.

- A **scalar subquery** returns exactly one row and one column, and stands wherever a single value belongs.
- **`IN`** and **`EXISTS`** test a subquery as a set, asking whether an outer value is a member of it.
- A **correlated subquery** mentions the outer query's tables and runs once per outer row.
- A **derived table** puts a subquery in `FROM`, so it is queried like any other table.

### The scalar subquery, and what happens when it lies about being scalar

The order with the largest amount, found without a separate query to look up the maximum first:

```sql
SELECT id, customer_id, amount FROM orders WHERE amount = (SELECT max(amount) FROM orders);
```

```
id  | customer_id | amount
----+-------------+-------
106 | 4           | 999.99
```

The parenthesised subquery is treated as a single value, `999.99`, and the outer `WHERE` compares against it exactly as it would against a literal. That only works because `max` guarantees one row. Ask for something that does not:

```sql
SELECT id FROM orders WHERE amount = (SELECT amount FROM orders WHERE customer_id = 4);
```

```
ERROR:  more than one row returned by a subquery used as an expression
SQLSTATE: 21000
```

Customer 4 has three orders, so the inner query returns three rows, and a scalar subquery can only stand for one. This is a runtime failure, not a compile-time one: PostgreSQL cannot know how many rows the inner query will return until it runs, so the same statement can pass review and testing against a customer with one order, then fail in production the day a customer gets a second.

### The correlated subquery: one answer per outer row

A correlated subquery names the outer table inside its own `WHERE`, so it cannot run once and be reused; the planner runs it, conceptually, once for every row the outer query considers.

```sql
SELECT c.id, (SELECT count(*) FROM orders o WHERE o.customer_id = c.id) AS n
FROM customers c ORDER BY c.id;
```

```
id | n
---+--
1  | 3
2  | 1
3  | 1
4  | 3
5  | 1
6  | 0
7  | 2
8  | 1
```

Customer 6 gets a 0, the fact an inner join cannot produce, since an inner join has no row for customer 6 to attach a count to. This is the third route to that number: lesson 8 reached it with a `LEFT JOIN` grouped per customer, lesson 9 with the same grouping and the `count(*)` against `count(column)` distinction, and this correlated subquery reaches it directly, once per customer, with no join and no `GROUP BY`. Which of the three to write is the last section's subject.

### IN, EXISTS and a join, on the same question

Which customers have an order over 50. Three ways to ask it:

```sql
SELECT c.id FROM customers c WHERE c.id IN (SELECT o.customer_id FROM orders o WHERE o.amount > 50) ORDER BY c.id;

SELECT c.id FROM customers c WHERE EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.id AND o.amount > 50) ORDER BY c.id;
```

Both return the same six ids: 1, 2, 4, 5, 7, 8. Now the join version of the same idea:

```sql
SELECT c.id, count(*) FROM customers c JOIN orders o ON o.customer_id = c.id WHERE o.amount > 50 GROUP BY c.id ORDER BY c.id;
```

```
id | count
---+------
1  | 2
2  | 1
4  | 1
5  | 1
7  | 1
8  | 1
```

Without the `GROUP BY`, that join returns 7 rows, not 6, because customer 1 has two orders over 50 and appears once per matching order. `count(distinct c.id)` on the same join gives 6, confirming six customers actually qualify: the plain row count answers a different question than the one asked. `IN` and `EXISTS` avoid this, because neither duplicates the outer row: a subquery used this way is a **semi-join**, asking "does at least one match exist" and returning the outer row at most once. A join returns one row per match and needs an explicit `GROUP BY` or `DISTINCT` to collapse that back down, one more step where a report can go wrong.

### The trap this lesson exists for: NOT IN against a NULL

`NOT IN` expands to a chain of `<>` joined by `AND`, exactly as the warm-up described, so one `NULL` anywhere in the subquery's results turns the whole test unknown, and `WHERE` keeps nothing unknown. `NOT EXISTS` never expands into a comparison against every value; it only asks whether a matching row exists, so a `NULL` among the non-matching rows changes nothing.

```sql
SELECT id FROM customers WHERE id NOT IN (SELECT customer_id FROM orders);
```

```
id
--
6
```

That subquery has no `NULL` in it, `orders.customer_id` being `NOT NULL`, so `NOT IN` gives the right answer, customer 6. Introduce one `NULL` into the set, the way a nullable column or a stray `UNION` might:

```sql
SELECT id FROM customers WHERE id NOT IN (SELECT customer_id FROM orders UNION SELECT NULL);
```

```
id
--
```

Zero rows. Customer 6 disappears with everyone else, and nothing says why. The `NOT EXISTS` form of the identical question is unaffected:

```sql
SELECT id FROM customers c WHERE NOT EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.id);
```

```
id
--
6
```

This is one of the most expensive mistakes in this stage, because it fails silently, only on data that happens to contain a `NULL`. The rule: reach for `NOT EXISTS` by default, and use `NOT IN` only against a column you have checked is `NOT NULL`, not one you assume is. `NOT EXISTS` is the correlated anti-join lesson 8 built with `LEFT JOIN ... IS NULL`, the same idea written as a subquery instead of a join.

### The derived table: a subquery queried like a table

A subquery in `FROM` is a **derived table**, and it is queried exactly like any other table, including further filtering from outside it.

```sql
SELECT * FROM (SELECT customer_id, count(*) AS n FROM orders GROUP BY customer_id) t WHERE t.n > 2;
```

```
customer_id | n
------------+--
4           | 3
1           | 3
```

Joined back to `customers` for the emails:

```sql
SELECT c.email, t.n FROM customers c
JOIN (SELECT customer_id, count(*) AS n FROM orders GROUP BY customer_id) t ON t.customer_id = c.id
WHERE t.n > 2 ORDER BY c.email;
```

```
email                  | n
-----------------------+--
ada@example.com        | 3
katherine@example.com  | 3
```

The alias `t` is what makes the derived table's columns reachable from outside, and every example above writes one. On PostgreSQL 18.6 the alias is in fact optional: `SELECT count(*) FROM (SELECT * FROM orders WHERE amount > 100)` runs and returns 5 with none at all, because PostgreSQL 16 added support for an unaliased subquery in `FROM`. A reader on PostgreSQL 14 or 15 gets a syntax error for that same query, and it is a version difference, not a mistake on their part. Write the alias anyway: every derived table written before PostgreSQL 16 has one.

### When a subquery is the wrong tool

A correlated subquery in `SELECT` computes, once per outer row, what a join and a `GROUP BY` compute once over the whole table. The per-customer count earlier asks its question directly and pays little for it; the same pattern added to every row of a large report re-scans `orders` once per customer, where one join and one `GROUP BY` read it a single time. Reach for the join when the whole result needs the number. When a query grows past two or three nested pieces, lesson 12 gives those pieces names instead.

## Practice

1. ▢ Predict the customer id and email for `SELECT c.id, c.email FROM customers c WHERE c.id = (SELECT customer_id FROM orders WHERE amount = 60.00)`, and say why this scalar subquery is safe while `WHERE amount = (SELECT amount FROM orders WHERE customer_id = 4)` was not.

<details markdown="1"><summary>Hint</summary>

Only one order in the fixture costs exactly 60.00. Count how many rows the inner query can return before deciding whether the outer comparison is at risk.

</details>

<details markdown="1"><summary>Check</summary>

Customer 5, `edsger@example.com`. It is safe today because exactly one order equals 60.00, but nothing about the query's text guarantees that stays true; a second order of 60.00 for any customer turns this into the same `21000` error, on data not yet written.

</details>

2. ▢ Predict the SQLSTATE of `SELECT id FROM orders WHERE customer_id = (SELECT id FROM customers WHERE country = 'GB')`.

<details markdown="1"><summary>Check</summary>

`21000`, "more than one row returned by a subquery used as an expression". Customers 1 and 3 both have country `GB`, so the inner query returns two rows and the scalar comparison fails at runtime, the same shape as the amount example above.

</details>

3. ▢ Predict the row count of `SELECT c.id FROM customers c WHERE c.id IN (SELECT customer_id FROM orders WHERE shipped_at IS NULL)`, and whether it differs from the `EXISTS` form of the same question.

<details markdown="1"><summary>Check</summary>

4 rows: customers 1, 3, 4 and 7, each with at least one unshipped order (103, 105, 108 and 110). `EXISTS` gives the identical 4 rows; both are semi-joins over the same set, and neither is a `NOT IN`, so there is no `NULL` here to disagree about.

</details>

4. ▢ `customers.country` is nullable, true of customers 2 and 8. Predict what `SELECT code FROM countries WHERE code NOT IN (SELECT country FROM customers)` returns, given that two customers have a `NULL` country.

<details markdown="1"><summary>Hint</summary>

The trap section covered exactly this shape. Ask what a `NULL` inside the subquery's result set does to every row of the outer `NOT IN`, not just the rows connected to that `NULL`.

</details>

<details markdown="1"><summary>Check</summary>

Zero rows, for every country, not just the ones genuinely used. Customers 2 and 8 contribute `NULL` to the subquery's results, and one `NULL` in a `NOT IN` list makes the comparison unknown for every row, so `WHERE` discards everything. `SELECT code FROM countries n WHERE NOT EXISTS (SELECT 1 FROM customers c WHERE c.country = n.code)` asks the same question correctly: `BR`, `DE`, `FR`, `IN`, `KE`.

</details>

5. ▢ Predict the result of `SELECT count(*) FROM (SELECT DISTINCT country FROM customers WHERE country IS NOT NULL) t`, and say whether it needed a derived table at all.

<details markdown="1"><summary>Check</summary>

4: `GB`, `US`, `NL` and `JP`, `NL` included even though it matches no row in `countries`. It did not need a derived table; `SELECT count(DISTINCT country) FROM customers WHERE country IS NOT NULL` gives the identical answer directly. A derived table earns its place when the inner query needs filtering or joining on a column, such as a computed count, that does not exist until the inner `SELECT` produces it.

</details>

6. ▢ A colleague writes `SELECT c.email, (SELECT sum(amount) FROM orders o WHERE o.customer_id = c.id) AS total FROM customers c ORDER BY total DESC LIMIT 100` against a table of a million customers. Name the join and `GROUP BY` that would compute the same result reading `orders` once, and say what stays the same and what changes.

<details markdown="1"><summary>Check</summary>

`SELECT c.email, sum(o.amount) AS total FROM customers c LEFT JOIN orders o ON o.customer_id = c.id GROUP BY c.id, c.email ORDER BY total DESC LIMIT 100`. `LEFT JOIN` is needed rather than an inner join, so a customer with no orders still appears with a `total` of `NULL` rather than vanishing, matching what the correlated subquery returned. What changes is that `orders` is read once for the whole query instead of once per customer, the entire cost of the rewrite at a million rows.

</details>

## Real-world reps

- [ ] Find a `WHERE ... NOT IN (SELECT ...)` in a codebase you can read, and check by hand whether the column inside the subquery can ever be `NULL`. If it can, or if you cannot be sure, that query has a latent bug.
- [ ] Find a query that filters on `EXISTS` or `IN` against a subquery, and rewrite it as a join with `GROUP BY` or `DISTINCT`. Confirm the row count matches before and after.
- [ ] Tomorrow: find a query with a subquery nested inside another subquery, and decide whether naming each step with a construct from the next lesson would make it easier for the next person to read.

## Going further

- [9.24 Subquery Expressions](https://www.postgresql.org/docs/current/functions-subquery.html): `IN`, `EXISTS`, `ANY`, `ALL` and the scalar subquery, in the reference's own words
- [7.2.1.3 Subqueries](https://www.postgresql.org/docs/current/queries-table-expressions.html#QUERIES-SUBQUERIES): the derived table, as part of the `FROM` clause grammar
- [PostgreSQL 16 Release Notes](https://www.postgresql.org/docs/16/release-16.html): the item allowing a `FROM`-clause subquery to omit its alias
- [9.25 Row and Array Comparisons](https://www.postgresql.org/docs/current/functions-comparisons.html): `IN`, `NOT IN` and the quantifiers again, stated as comparisons, which is where the `NULL` behaviour is spelled out
- [Querying](../reference/querying.md): the stage 2 reference sheet
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
