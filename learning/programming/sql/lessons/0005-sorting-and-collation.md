---
title: 5. Sorting and Collation
description: Text ordering depends on a collation, and a tie without a unique key is not stable
type: lesson
---

# Lesson 5. Sorting and Collation

**Mission link:** Two systems that sort the same rows differently, and a paginated list that repeats a row, are both this lesson. Ordering looks like the simplest clause in SQL and it carries the most hidden configuration.
**Primary source:** [PostgreSQL, 7.5 Sorting Rows (ORDER BY)](https://www.postgresql.org/docs/current/queries-order.html)
**Prerequisites:** [Lesson 4](0004-sets-and-bags.md)

## Warm-up

1. ▢ Which of `UNION` and `UNION ALL` should be the default, and why?

<details markdown="1"><summary>Check</summary>

`UNION ALL`. `UNION` sorts or hashes the whole result to remove duplicates, which is pure cost when the sides are disjoint.

</details>

2. ▢ Why can a subquery's `ORDER BY` be discarded by the outer query?

<details markdown="1"><summary>Check</summary>

Because ordering is applied to a result and is not a property of a relation. Only a top-level `ORDER BY` is a promise.

</details>

## Know this

`ORDER BY` sorts the output. It runs after `SELECT`, so it can use output aliases and column positions:

```sql
SELECT amount * 0.2 AS tax FROM orders ORDER BY tax DESC;
SELECT id, amount FROM orders ORDER BY 2 DESC;      -- by position, avoid
```

Ordering by position is legal and fragile: adding a column to the select list changes the meaning silently. Name the column.

### A tie is not an order

```sql
SELECT id, customer_id FROM orders ORDER BY customer_id LIMIT 10;
```

Rows with the same `customer_id` may come back in any order, and that order can change between runs. So a `LIMIT` over a non-unique sort key returns a non-deterministic slice, which is the same problem as lesson 2's unordered `LIMIT`, just harder to notice because the query does have an `ORDER BY`.

**Always end the sort key with something unique:**

```sql
ORDER BY customer_id, id
```

This is also what makes pagination correct. With `OFFSET`, a tie that reshuffles between two page requests can show the same row twice and skip another entirely, and no amount of retrying fixes it because nothing is wrong from the engine's point of view.

### NULLs sort somewhere, and the standard does not say where

In PostgreSQL, NULLs are treated as larger than any value: last under `ASC`, first under `DESC`. The standard leaves it to the engine, so a query that must behave the same on two engines states it:

```sql
ORDER BY shipped_at DESC NULLS LAST
```

That matters most for "most recent first" reports, where the default `DESC` puts every unshipped order at the top.

### Text ordering is a collation, not a rule of SQL

A **collation** decides how text compares: which letters sort together, whether case matters, how accents are handled. It is configured per database, and can be set per column or per expression:

```sql
SELECT email FROM customers ORDER BY email COLLATE "C";
```

Two collations worth knowing about:

- **`C`**, sometimes called `POSIX`, compares raw bytes. It is fast, stable across systems, and sorts `Z` before `a` because uppercase letters have lower byte values.
- **A language collation**, such as `en_US` or an ICU locale, sorts the way a person in that locale expects, which usually means ignoring case for ordering purposes and applying locale-specific rules to accented letters.

Three practical consequences ([collation support](https://www.postgresql.org/docs/current/collation.html)):

1. The same query on two databases with different collations returns rows in a different order, and neither is wrong.
2. Comparison follows the collation too, so whether `'a' = 'A'` depends on it. Most default collations are case-sensitive for equality even when their sort order looks case-insensitive.
3. An index is built in a specific collation. A query that sorts or compares in a different collation cannot use it, which is a stage 6 concern and a real cause of a query that got slower after a locale change.

For case-insensitive matching, the portable spelling is `lower(email) = lower($1)`, and the PostgreSQL-specific answers are the `citext` type and a case-insensitive ICU collation. Note that `lower()` on a column prevents an ordinary index from being used unless the index is built on the same expression.

### Sorting is not free

A sort that fits in the engine's working memory is fast, and one that does not spills to disk. So `ORDER BY` on a large result is often the most expensive part of a query, and an index in the right order can remove the sort entirely. Stage 6 is where that becomes a tool; for now, notice that `ORDER BY` has a cost at all.

## Practice

1. ▢ This list occasionally shows the same order twice across two pages. Explain and fix.

   ```sql
   SELECT id, customer_id FROM orders ORDER BY customer_id LIMIT 20 OFFSET 20;
   ```

<details markdown="1"><summary>Hint</summary>

Ask what the engine is allowed to do with two rows that have the same `customer_id`.

</details>

<details markdown="1"><summary>Check</summary>

Rows sharing a `customer_id` are tied, and a tie has no defined order, so the engine may place them differently on each execution. A row that was on page 1 can appear on page 2, and another can be missed.

Fix by making the sort key unique: `ORDER BY customer_id, id`. That is necessary for any paginated query, and stage 6 will replace `OFFSET` itself with a keyset condition for the separate performance reason.

</details>

2. ▢ Predict where the unshipped orders appear, and write the version a "most recent first" report actually wants.

   ```sql
   SELECT id, shipped_at FROM orders ORDER BY shipped_at DESC;
   ```

<details markdown="1"><summary>Check</summary>

In PostgreSQL they appear first, because NULLs sort as though larger than any value and the order is descending.

```sql
SELECT id, shipped_at FROM orders ORDER BY shipped_at DESC NULLS LAST, id DESC;
```

Being explicit also makes the query behave the same on an engine whose default is the other way round.

</details>

3. ▢ The same query returns a different order on a colleague's machine. Which explanation is most likely?

   - a) One of the databases has corrupt data
   - b) The two databases use different collations
   - c) The query is missing a `WHERE` clause
   - d) One machine has more memory available

<details markdown="1"><summary>Check</summary>

**b)** The two databases use different collations.

Text ordering is defined by the collation, which is set when the database is created, so the same rows legitimately sort differently. Option d can change whether a sort spills to disk and not its result, unless the sort key has ties, in which case the order was never defined to begin with.

</details>

4. ▢ A login lookup must treat `Ada@Example.com` and `ada@example.com` as the same address. Give a portable spelling and name its cost.

<details markdown="1"><summary>Check</summary>

```sql
WHERE lower(email) = lower($1)
```

The cost is that a plain index on `email` cannot serve this query, because the indexed values are not what is being compared. The fix is an index on the expression, `CREATE INDEX ON customers (lower(email))`, which stage 6 covers.

The other options are engine-specific: a case-insensitive collation on the column, or PostgreSQL's `citext`. Both are cleaner to read and move the decision into the schema, where it is easier to apply consistently and harder to notice.

</details>

5. ▢ Why is `ORDER BY 2` legal, and why would you still not write it?

<details markdown="1"><summary>Check</summary>

It is legal because `ORDER BY` runs after the select list exists, so it can refer to output columns by position as well as by name.

Not worth writing because the meaning depends on the shape of the select list. Insert a column at the front and every positional sort key now refers to something else, with no error, and a reviewer cannot see it in the diff, because the `ORDER BY` clause itself did not change.

</details>

## Real-world reps

- [ ] Sort a text column with `COLLATE "C"` and then with the database default, using values that differ in case, and compare the two orders.
- [ ] Build a table with deliberate ties, page through it with `LIMIT` and `OFFSET`, and try to produce a duplicated row. Then add a unique tie-breaker and try again.
- [ ] Tomorrow: find a paginated query in code you know. Check whether its sort key is unique. Most are not.

## Going further

- [7.5 Sorting Rows](https://www.postgresql.org/docs/current/queries-order.html): `ASC`, `DESC`, `NULLS FIRST` and `NULLS LAST`
- [23.2 Collation Support](https://www.postgresql.org/docs/current/collation.html): how collations are chosen, and what they affect besides ordering
- [7.6 LIMIT and OFFSET](https://www.postgresql.org/docs/current/queries-limit.html): the documentation's own warning about ties
- [Evaluation order of a SELECT](../reference/select-evaluation-order.md): where `ORDER BY` sits, and what it can see
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
