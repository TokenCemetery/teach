---
title: 4. Sets and Bags
description: A table is a bag, so duplicates are real and UNION quietly pays to remove them
type: lesson
---

# Lesson 4. Sets and Bags

**Mission link:** `UNION` and `UNION ALL` differ by one word and by a sort of the whole result. Knowing which you meant is both a correctness question and, at scale, the difference between a fast query and a slow one.
**Primary source:** [PostgreSQL, 7.4 Combining Queries](https://www.postgresql.org/docs/current/queries-union.html)
**Prerequisites:** [Lesson 3](0003-null-and-three-valued-logic.md)

## Warm-up

1. ▢ Why does `WHERE country <> 'GB'` skip the rows where `country` is `NULL`?

<details markdown="1"><summary>Check</summary>

The comparison is unknown rather than true, and `WHERE` keeps only true.

</details>

2. ▢ `SELECT sum(amount) FROM orders WHERE false` returns what, and why does it matter?

<details markdown="1"><summary>Check</summary>

`NULL`, not `0`. Any arithmetic downstream then produces `NULL`, so report queries wrap it in `coalesce`.

</details>

## Know this

Relational theory talks about sets, where every element is distinct. **SQL tables are bags**, also called multisets: the same row can appear any number of times, and the engine does nothing about it unless you ask.

```sql
INSERT INTO customers (id, email) VALUES (3, 'x@example.com');
-- a second row with the same email is rejected only because of the UNIQUE constraint
```

Without a constraint, nothing prevents duplicates, and no query can tell two identical rows apart. That is the practical reason lesson 6 exists.

### `DISTINCT` removes duplicate output rows

```sql
SELECT DISTINCT country FROM customers;
SELECT DISTINCT country, id FROM customers;    -- distinct over BOTH columns
```

`DISTINCT` applies to the whole output row, not to the column it happens to sit next to. Adding a unique column to the select list therefore makes `DISTINCT` do nothing, which is a common way for it to appear to stop working.

Removing duplicates costs a sort or a hash of the entire result, so `DISTINCT` used to paper over an accidental row multiplication from a join is paying twice: once to produce the extra rows and once to discard them. When `DISTINCT` appears necessary, check the joins first.

### The set operators, and the `ALL` that skips the deduplication

```sql
SELECT country FROM customers
UNION                         -- removes duplicates across both sides
SELECT country FROM archived_customers;

SELECT country FROM customers
UNION ALL                     -- keeps everything, no sort
SELECT country FROM archived_customers;
```

| Operator | Result | Duplicates |
|---|---|---|
| `UNION` | rows in either | removed |
| `UNION ALL` | rows in either | kept |
| `INTERSECT` | rows in both | removed |
| `EXCEPT` | rows in the first and not the second | removed |

All three default to removing duplicates and all three have an `ALL` variant. `UNION ALL` is the one to reach for by default, because most of the time the sides are already disjoint and the deduplication is pure cost. Use `UNION` when duplicates are genuinely possible and unwanted, and know you are paying for a full pass.

Two rules the operators impose: both sides must have the same number of columns with compatible types, and the column names come from the first branch. For deduplication, two NULLs count as the same value, which is lesson 3's asymmetry appearing again.

### Set operations against joins

`EXCEPT` and `NOT EXISTS` often express the same intent, and they are not equivalent:

```sql
-- customers with no orders, as a set difference on whole rows
SELECT id FROM customers EXCEPT SELECT customer_id FROM orders;

-- the same question, row by row
SELECT c.id FROM customers c
WHERE NOT EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.id);
```

The first deduplicates its output and compares whole rows, which is fine when you select one column and surprising when you select several. The second keeps every matching customer row as it is. `NOT EXISTS` is also null-safe, unlike `NOT IN` from lesson 3.

### A result has no order until you ask

`ORDER BY` is not part of the relation. It is applied last, to the output, which is why:

- A subquery's `ORDER BY` is not guaranteed to survive into the outer query, and relying on it is one of the most common invalid assumptions in SQL.
- `UNION` may return rows in any order, even though it had to sort them internally to deduplicate. That sort is an implementation detail, not a promise.
- Only a top-level `ORDER BY` orders a result, and only a unique sort key makes it deterministic.

## Practice

1. ▢ Predict the row counts, given `customers` has 3 rows with countries `'GB'`, `'GB'`, `NULL`.

   ```sql
   SELECT country FROM customers;
   SELECT DISTINCT country FROM customers;
   SELECT DISTINCT country, id FROM customers;
   ```

<details markdown="1"><summary>Check</summary>

`3`, `2`, `3`.

The second collapses the two `'GB'` rows and keeps the `NULL` as its own value, because `DISTINCT` treats NULLs as duplicates of each other rather than as unknown.

The third returns everything, because `id` is unique, so every output row is already distinct. That is the mechanism behind "I added a column and `DISTINCT` stopped working".

</details>

2. ▢ Two tables of 500,000 rows each, known to be disjoint. Which operator, and what does the other one cost?

<details markdown="1"><summary>Check</summary>

`UNION ALL`.

`UNION` would sort or hash a million rows to look for duplicates that cannot exist, then return all of them anyway. The cost is a full extra pass over the data and, if it does not fit in memory, a spill to disk.

The habit worth forming: write `UNION ALL` by default and switch to `UNION` when you can name where a duplicate would come from.

</details>

3. ▢ Which is the safest way to list customers with no orders?

   - a) `SELECT id FROM customers EXCEPT SELECT customer_id FROM orders`
   - b) `SELECT id FROM customers WHERE id NOT IN (SELECT customer_id FROM orders)`
   - c) `SELECT c.id FROM customers c WHERE NOT EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.id)`
   - d) `SELECT c.id FROM customers c LEFT JOIN orders o ON o.customer_id = c.id`

<details markdown="1"><summary>Check</summary>

**c)** is the safe default.

Option a works here and deduplicates its output, which becomes wrong the moment you select more than the key. Option b is the `NOT IN` trap: one `NULL` in the subquery empties the result. Option d is incomplete: it needs `WHERE o.id IS NULL` to keep only the non-matching rows, and without that it returns every customer with an order too.

</details>

4. ▢ A developer relies on this and it works in testing. Say what is wrong with it.

   ```sql
   SELECT * FROM (SELECT id FROM orders ORDER BY shipped_at DESC) t LIMIT 10;
   ```

<details markdown="1"><summary>Hint</summary>

Ask what the inner query hands to the outer one. Is it an ordered list of rows, or a relation?

</details>

<details markdown="1"><summary>Check</summary>

The inner `ORDER BY` is not guaranteed to be preserved by the outer query. Nothing in the standard requires an ordering to survive a surrounding `SELECT`, and a plan change, a parallel scan or an added join can reorder the rows with no warning.

It works in testing because a simple plan happens to preserve the order. The fix is to put the `ORDER BY` at the top level, where it is a promise rather than an accident.

</details>

5. ▢ A query returns 4,000 rows instead of the expected 1,000, so a colleague adds `DISTINCT` and the count is right again. Why is that a bad fix?

<details markdown="1"><summary>Check</summary>

Because the extra rows are evidence of something else: almost always a join that matches more rows than intended, meaning a missing condition or a one-to-many relationship that was assumed to be one-to-one. `DISTINCT` hides that, and the query now costs the multiplication plus the deduplication.

It is also fragile. As soon as the select list gains a column that differs between the duplicated rows, such as an order id, the duplicates come back and the query looks broken again for a reason nobody remembers.

The fix is to find the join that multiplied the rows and decide what the query should actually aggregate.

</details>

## Real-world reps

- [ ] Insert two rows with the same value in a non-unique column, then run the three queries from practice 1 and watch the counts.
- [ ] Write the same "customers with no orders" question all four ways from practice 3, including the broken `LEFT JOIN`, and compare the results.
- [ ] Tomorrow: find a `DISTINCT` in code you know. Decide whether it is removing genuine duplicates or hiding a join, and check the join to be sure.

## Going further

- [7.4 Combining Queries](https://www.postgresql.org/docs/current/queries-union.html): the operators, the type rules, and the `ALL` variants
- [7.5 Sorting Rows](https://www.postgresql.org/docs/current/queries-order.html): why ordering is applied last, which is lesson 5
- [Modern SQL](https://modern-sql.com/): what the standard says about set operators and where engines differ
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
