---
title: 20. Choosing the Tool
description: Top-N, running totals and deduplication each have two or three correct spellings, and the choice is about what the question asks
type: lesson
---

# Lesson 20. Choosing the Tool

**Mission link:** A report asking for "the latest per customer", "the total so far" or "exactly one row per key" has two or three correct spellings in SQL, and a senior engineer's job is picking between them on purpose rather than by habit.
**Primary source:** [SELECT](https://www.postgresql.org/docs/current/sql-select.html)
**Prerequisites:** [Lesson 16](0016-navigating-within-a-window.md), [Lesson 17](0017-lateral-joins.md)

## Warm-up

1. ▢ Lesson 14 established that a window function cannot appear in `WHERE` or `HAVING`, because both finish running before a window is computed. Given that, what does a query filtering on `row_number()` have to do instead?

<details markdown="1"><summary>Check</summary>

It has to compute the window one layer down, in a derived table or a CTE, and filter the alias it produced from the query wrapped around it, since only there has the window already run and turned into an ordinary column.

</details>

## Know this

### The newest row per group, three ways

The most common report query there is: one row per customer, the newest one. Three queries answer it.

```sql
SELECT id, customer_id FROM (
  SELECT o.id, o.customer_id,
         row_number() OVER (PARTITION BY o.customer_id ORDER BY o.shipped_at DESC NULLS LAST, o.id DESC) AS rn
  FROM orders o
) s
WHERE rn = 1
ORDER BY customer_id;
```

```sql
SELECT DISTINCT ON (customer_id) customer_id, id
FROM orders
ORDER BY customer_id, shipped_at DESC NULLS LAST, id DESC;
```

```sql
SELECT c.id AS customer_id, newest.id
FROM customers c
JOIN LATERAL (
  SELECT o.id
  FROM orders o
  WHERE o.customer_id = c.id
  ORDER BY o.shipped_at DESC NULLS LAST, o.id DESC
  LIMIT 1
) AS newest ON true
ORDER BY c.id;
```

All three return the identical seven customers, order ids 102, 104, 105, 107, 109, 111 and 112. Lesson 17 already set two of these three side by side on a different question, the largest order rather than the newest, and reached the same verdict about what separates them; the third form and the ordering trap below are what this pass adds. Printed once, what genuinely differs is not correctness. `DISTINCT ON` is the shortest and is PostgreSQL only. `row_number` hands back the rank itself, which matters the moment a later step needs to know a row came second rather than first, and it travels to any engine that has window functions at all. The lateral form can stop as soon as its own `LIMIT` is satisfied rather than ranking every row in the table, and it is the one that extends to the top three without changing shape, only raising `LIMIT 1` to `LIMIT 3`. Which of the three actually runs fastest on a given table is stage 6's question, not this lesson's, and nothing above should be read as an answer to it.

The ordering detail decides correctness here, not style. Ordering by `shipped_at DESC` alone is wrong, because four of the twelve orders have no `shipped_at` at all, and the tie between an unshipped order and a shipped one has to be broken on purpose. Drop `NULLS LAST` and, since PostgreSQL's default for `DESC` is `NULLS FIRST`, every unshipped order sorts ahead of every shipped one and wins the "newest" seat it has no business holding: the same `row_number` query without it returns ids 103, 104, 105, 108, 109, 110 and 112, three of them the unshipped orders for customers 1, 4 and 7. `shipped_at DESC NULLS LAST, id DESC` fixes both problems at once, sending unshipped orders to the back and then breaking the remaining tie, customer 4's two same-day orders, with `id`.

### A running total, per customer and overall

Ordered by id, with an explicit `ROWS` frame:

```sql
SELECT customer_id, id, amount::text,
       sum(amount) OVER (PARTITION BY customer_id ORDER BY id ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)::text AS per_customer,
       sum(amount) OVER (ORDER BY id ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)::text AS overall
FROM orders
ORDER BY id;
```

Customer 1's running total reads 120.00, 200.50, 215.50, and the overall column runs from 120.00 up to 2406.49 across all twelve rows in order. `id` never ties, so `ROWS` and the default `RANGE` agree here, and swapping one for the other changes nothing, verified directly. That agreement is the exception, not the rule: lesson 15 already showed a running total ordered by `amount` splitting the two `10.00` orders into `10.00` and `20.00` under `ROWS` while `RANGE` gives both `20.00`, so the frame stops being optional the moment the ordering column can tie, and writing it out is the only way to know which answer a report is actually giving.

### Deduplication, seen from the other side

Problem one asks which row survives. The same question, read backwards, asks which rows to delete.

```sql
SELECT id, customer_id FROM (
  SELECT o.id, o.customer_id,
         row_number() OVER (PARTITION BY o.customer_id ORDER BY o.shipped_at DESC NULLS LAST, o.id DESC) AS rn
  FROM orders o
) s
WHERE rn > 1
ORDER BY customer_id, id;
```

Five rows: orders 101 and 103 for customer 1, 106 and 108 for customer 4, and 110 for customer 7. Problem one's `rn = 1` query returns seven, this one's `rn > 1` returns five, and seven plus five is twelve, every order in the table accounted for exactly once. A real cleanup wraps this same `SELECT` inside a `DELETE ... WHERE id IN (...)`, but the shape that decides which rows go is identical to the shape that decided which row stays, only the comparison on `rn` flips.

### What SQL still should not do, and what it no longer has to

Two honest limits, in opposite directions. A computation that needs data the database does not hold, a fraud score from a model that lives outside it, an address validated against a mapping service, still belongs in application code, because no `SELECT` can read a value that was never stored. The same is true of an action whose result has to be transactional with an outside system: a database commit can guarantee the row changed, but it cannot guarantee an email was sent or a payment provider was called at the same instant, and treating the two as one transaction is a promise SQL cannot keep.

What this stage has made unnecessary is the pattern most often reimplemented in application code anyway: fetch every row for a customer, hold them in a list, sort the list, and keep the first one, repeated once per customer in a loop. That is problem one's question, asked by hand, at the cost of round trips instead of a `PARTITION BY`, and every one of this lesson's three verified queries already does it in the database in a single pass. Written out as a loop next to `DISTINCT ON (customer_id) ... ORDER BY customer_id, shipped_at DESC NULLS LAST, id DESC`, it looks like exactly what it is: a ranking function, reinvented one row at a time.

### What the stage bought

Lesson 14's window computes a value across a set of rows without collapsing them, so a row survives its own aggregate instead of being thrown away for it. Lesson 15's frame decides how much of that set counts, which is why a running total can silently mean two different things depending on whether the ordering column ties. Lesson 16's navigation functions split on that same frame: `lag` and `lead` reach across the whole partition regardless of it, while `first_value`, `last_value` and `nth_value` obey it and need it widened on purpose to mean anything past the current row. Lesson 17's `LATERAL` lets a subquery in `FROM` see the row sitting beside it, which is what makes a per-row top-N possible at all. Lesson 18's recursive query terminates when its recursive term stops producing rows nobody has seen, or, under `UNION`, stops producing rows the accumulated result does not already hold. Lesson 19's document column costs the schema's own guarantees: no column list, no foreign key, no type check, only what a `->>` and a cast can recover at query time. The next stage is not about querying this schema any better; it is about designing one that does not need rescuing.

## Practice

1. ▢ Predict the row count of the archetypal newest-row lateral query with its `LIMIT` raised from 1 to 3, and say in one sentence why that count is not seven times anything.

<details markdown="1"><summary>Hint</summary>

No customer in the fixture has more than three orders.

</details>

<details markdown="1"><summary>Check</summary>

Twelve, every order in the table. Raising the limit to 3 only matters for a customer with more than three orders to rank, and the largest count any customer has is three, so the query stops truncating anyone and becomes a roundabout way of listing every order.

</details>

2. ▢ Predict what `DISTINCT ON (customer_id) ... ORDER BY customer_id, shipped_at DESC, id DESC` returns for customer 4, with `NULLS LAST` removed from this lesson's version.

<details markdown="1"><summary>Check</summary>

Order 108, the one with no `shipped_at` at all. `DESC` defaults to `NULLS FIRST`, so the unshipped row sorts ahead of both shipped ones and `DISTINCT ON` keeps whichever row is first under its `ORDER BY`, the same mistake problem one's `row_number` version makes without `NULLS LAST`.

</details>

3. ▢ Predict the exact error and SQLSTATE of dropping `customer_id` from the `ORDER BY` below, leaving `DISTINCT ON (customer_id)` in place.

   ```sql
   SELECT DISTINCT ON (customer_id) customer_id, id
   FROM orders
   ORDER BY shipped_at DESC NULLS LAST, id DESC;
   ```

<details markdown="1"><summary>Check</summary>

`ERROR: SELECT DISTINCT ON expressions must match initial ORDER BY expressions`, SQLSTATE `42P10`. `DISTINCT ON` needs its own expression to be the leading term of the `ORDER BY`, since that is how it decides which rows are peers before picking the first one.

</details>

4. ▢ Predict what a plain `OFFSET 1` does to this lesson's `DISTINCT ON` query, and say why it does not return each customer's second-newest order.

   ```sql
   SELECT DISTINCT ON (customer_id) customer_id, id
   FROM orders
   ORDER BY customer_id, shipped_at DESC NULLS LAST, id DESC
   OFFSET 1;
   ```

<details markdown="1"><summary>Hint</summary>

`DISTINCT ON` has already collapsed every group to one row before `OFFSET` runs at all.

</details>

<details markdown="1"><summary>Check</summary>

Six rows, customer 1 missing entirely rather than replaced by its second-newest order. `DISTINCT ON` reduces the table to one row per customer first, and `OFFSET` then drops the first row of that already-reduced result, which happens to belong to customer 1; there is no way to ask `DISTINCT ON` itself for a rank other than first.

</details>

5. ▢ Predict the row count of a `UNION` between problem one's `rn = 1` query and problem three's `rn > 1` query, both by order id, and say what a mismatch would mean.

<details markdown="1"><summary>Check</summary>

Twelve, every order id exactly once, seven from one side and five from the other with nothing shared for `UNION` to deduplicate away. A different count would mean the two conditions on `rn` were not a true partition of every order, either overlapping or leaving one out.

</details>

6. ▢ Predict whether swapping `ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW` for the default `RANGE` changes any value in this lesson's overall running total, ordered by `id`.

<details markdown="1"><summary>Check</summary>

No value changes. `id` is a primary key, so no two rows ever tie on it, and `ROWS` and `RANGE` only disagree on rows that tie; ordering by `amount` instead, where the fixture has a genuine tie, is exactly where lesson 15 showed them split.

</details>

## Real-world reps

- [ ] Find a report at work computing "latest per key" and check which of the three forms it uses, then decide, from what the report does with the result next, whether a different one would serve it better.
- [ ] Take a total that a report currently computes with a loop over fetched rows, in whatever language runs it, and rewrite it as one query with an explicit frame, checking the totals agree row for row.
- [ ] Tomorrow: find one place where a script deduplicates by fetching everything and keeping the first match per key, and replace it with a single query using whichever of this lesson's three forms fits the question being asked.

## Going further

- [DELETE](https://www.postgresql.org/docs/current/sql-delete.html): the statement problem three's query points toward, once you are ready to remove rows rather than list them
- [9.22. Window Functions](https://www.postgresql.org/docs/current/functions-window.html): the full function reference, useful now that the choice among several correct ones is the point
- [Appendix A. PostgreSQL Error Codes](https://www.postgresql.org/docs/current/errcodes-appendix.html): where SQLSTATE 42P10, `DISTINCT ON`'s mismatch error, is catalogued
- [Beyond the basics](../reference/beyond-the-basics.md): the stage 3 reference sheet
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
