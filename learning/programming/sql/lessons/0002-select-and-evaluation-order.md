---
title: 2. SELECT and Evaluation Order
description: The clauses run in a different order than they are written, which explains most beginner errors
type: lesson
---

# Lesson 2. SELECT and Evaluation Order

**Mission link:** "Why can't I use that alias in WHERE" and "why is my filter ignoring the aggregate" are the same question, and one ordering answers both. Reading a query in evaluation order is also how you read a query plan later.
**Primary source:** [PostgreSQL, SELECT](https://www.postgresql.org/docs/current/sql-select.html)
**Prerequisites:** [Lesson 1](0001-tables-rows-and-types.md)

## Warm-up

1. ▢ Which type would you use for an order total, and which would you refuse?

<details markdown="1"><summary>Check</summary>

`numeric`, because decimal values are stored exactly. Refuse `double precision`, where representation error accumulates across a `SUM`.

</details>

2. ▢ What does `timestamptz` give you that `timestamp` does not?

<details markdown="1"><summary>Check</summary>

An absolute instant. Plain `timestamp` records wall-clock text with no zone, so the same stored value means different moments to different readers.

</details>

## Know this

A `SELECT` is written in one order and evaluated in another. The evaluation order is what the database actually does, and it is the key to almost every error a query returns:

```text
1. FROM, JOIN        which rows exist at all
2. WHERE             discard rows, one at a time
3. GROUP BY          collapse rows into groups
4. HAVING            discard groups
5. SELECT            compute the output expressions, including aliases
6. DISTINCT          remove duplicate output rows
7. ORDER BY          sort what is left
8. LIMIT, OFFSET     take a slice
```

Two consequences fall straight out of it.

**`WHERE` cannot see a `SELECT` alias.** The alias is created at step 5, and `WHERE` ran at step 2:

```sql
SELECT amount * 0.2 AS tax
FROM orders
WHERE tax > 100;              -- ERROR: column "tax" does not exist
```

Repeat the expression, or wrap the query:

```sql
SELECT amount * 0.2 AS tax FROM orders WHERE amount * 0.2 > 100;

SELECT tax FROM (SELECT amount * 0.2 AS tax FROM orders) t WHERE tax > 100;
```

`ORDER BY` is the exception in the other direction: it runs at step 7, after the output exists, so it *can* use an alias. That asymmetry is not arbitrary, and it is worth being able to derive rather than memorise.

**`WHERE` filters rows and `HAVING` filters groups.** `WHERE` runs before grouping, so it cannot see an aggregate. `HAVING` runs after, so it can:

```sql
SELECT customer_id, count(*) AS orders
FROM orders
WHERE amount > 0                  -- per row, before grouping
GROUP BY customer_id
HAVING count(*) > 5;              -- per group, after grouping
```

Putting a row-level condition in `HAVING` gives the same answer and does more work, because rows that could have been discarded early are grouped first.

### Filtering

```sql
WHERE country = 'GB'
WHERE amount BETWEEN 10 AND 100            -- inclusive at both ends
WHERE country IN ('GB', 'FR')
WHERE email LIKE '%@example.com'           -- % any string, _ any character
WHERE shipped_at IS NULL                   -- see lesson 3
```

`WHERE` keeps a row only when the condition is **true**. Not true-or-unknown: true. That single sentence is the entire content of lesson 3, and it is why a filter can drop rows you expected to see.

### `LIMIT` without `ORDER BY` returns an arbitrary slice

```sql
SELECT * FROM orders LIMIT 10;             -- ten rows, no promise which
```

A table has no inherent order, so a `LIMIT` with no `ORDER BY` is a request for any ten rows, and the answer may change between runs even with no writes. It will look stable in testing and stop being stable under load or after a plan change.

`OFFSET` has a related problem worth flagging now and solving in stage 6: paging with `LIMIT 10 OFFSET 10000` makes the database produce and discard ten thousand rows, and if the underlying data changes between pages, rows can be skipped or repeated.

## Practice

1. ▢ Why does this fail, and give two ways to fix it?

   ```sql
   SELECT amount * 0.2 AS tax
   FROM orders
   WHERE tax > 100;
   ```

<details markdown="1"><summary>Check</summary>

`WHERE` is evaluated before the `SELECT` list, so the alias `tax` does not exist yet.

Fix one: repeat the expression, `WHERE amount * 0.2 > 100`. Fix two: compute it in a subquery or a common table expression and filter outside, which is worth it when the expression is long or used more than once.

</details>

2. ▢ Both queries return the same rows. Which does less work, and why?

   ```sql
   -- A
   SELECT customer_id, count(*) FROM orders
   WHERE amount > 0 GROUP BY customer_id;

   -- B
   SELECT customer_id, count(*) FROM orders
   GROUP BY customer_id HAVING min(amount) > 0;
   ```

<details markdown="1"><summary>Hint</summary>

They do not return the same rows in every case. Work out what B does with a customer who has one order of zero and one of ten.

</details>

<details markdown="1"><summary>Check</summary>

They are not equivalent, which is the real answer. A discards the zero-amount rows and counts the rest, so that customer appears with a count of 1. B keeps every row, groups, and then rejects the whole group because its minimum is zero, so that customer disappears entirely.

Where the two do agree, A does less work: it filters rows before grouping, so fewer rows reach the aggregation.

The lesson is that moving a condition between `WHERE` and `HAVING` changes meaning, not just performance.

</details>

3. ▢ Put these in evaluation order: `SELECT`, `ORDER BY`, `WHERE`, `LIMIT`, `FROM`, `GROUP BY`, `HAVING`.

<details markdown="1"><summary>Check</summary>

`FROM`, `WHERE`, `GROUP BY`, `HAVING`, `SELECT`, `ORDER BY`, `LIMIT`.

With `DISTINCT` between `SELECT` and `ORDER BY`. The two things to be able to derive from it: `WHERE` cannot use an alias while `ORDER BY` can, and `WHERE` cannot use an aggregate while `HAVING` can.

</details>

4. ▢ A report runs `SELECT * FROM orders LIMIT 100` and shows different rows on two consecutive loads, with no writes in between. Explain, without blaming a bug.

<details markdown="1"><summary>Check</summary>

There is no `ORDER BY`, so the query asks for any hundred rows and the engine is free to return whichever hundred are cheapest to produce. That depends on the plan, on which pages are in cache, and on physical row placement, all of which can change without any write.

The fix is an `ORDER BY` on something unique, or on a column plus a unique tie-breaker. Ordering by a non-unique column alone has the same problem within each group of ties.

</details>

5. ▢ You need the ten most recent orders for a customer. Write it, and name what makes the result deterministic.

<details markdown="1"><summary>Check</summary>

```sql
SELECT id, amount, shipped_at
FROM orders
WHERE customer_id = 1
ORDER BY shipped_at DESC, id DESC
LIMIT 10;
```

The `id DESC` tie-breaker is what makes it deterministic. Without it, two orders sharing a `shipped_at` can appear in either order, so the tenth row is not stable and a page boundary can duplicate or skip a row.

Note also that rows with a `NULL` `shipped_at` sort first under `DESC` in PostgreSQL, which is lesson 3's material and probably not what a "most recent" report wants.

</details>

## Real-world reps

- [ ] Run the failing alias query and read the error. Then fix it both ways and confirm both give the same answer.
- [ ] Run the A and B pair from practice 2 against data containing a customer with one zero-amount order, and watch the row counts differ.
- [ ] Tomorrow: find a query in code you know that uses `LIMIT` without `ORDER BY`, or `ORDER BY` on a non-unique column. Decide whether its result has ever needed to be stable.

## Going further

- [SELECT](https://www.postgresql.org/docs/current/sql-select.html): the reference page, which states the clause evaluation order explicitly
- [2.5 Querying a Table](https://www.postgresql.org/docs/current/tutorial-select.html): the tutorial version, with worked examples
- [7.6 LIMIT and OFFSET](https://www.postgresql.org/docs/current/queries-limit.html): why an unordered `LIMIT` is unpredictable
- [Evaluation order of a SELECT](../reference/select-evaluation-order.md): the reference sheet, for lookup
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
