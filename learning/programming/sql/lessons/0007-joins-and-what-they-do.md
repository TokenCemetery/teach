---
title: 7. Joins, and What a Join Actually Does
description: A join is a filtered cross product, so the ON condition decides which rows exist before anything else runs
type: lesson
---

# Lesson 7. Joins, and What a Join Actually Does

**Mission link:** Every non-trivial query touches more than one table, and a wrong join either multiplies rows that should not exist or silently drops rows that should. Knowing exactly what a join produces before a WHERE or an aggregate lands on top stops those mistakes reaching a report where they are much harder to notice.
**Primary source:** [PostgreSQL, 7.2 Table Expressions](https://www.postgresql.org/docs/current/queries-table-expressions.html)
**Prerequisites:** [Lesson 2](0002-select-and-evaluation-order.md), [Lesson 6](0006-keys-and-constraints.md)

## Warm-up

1. ▢ Lesson 2 placed `FROM` and `JOIN` before `WHERE` in the evaluation order. What does that tell you about when a join's `ON` condition is checked, relative to `WHERE`?

<details markdown="1"><summary>Check</summary>

The `ON` condition is checked while the joined rows are being built, during the `FROM` step, which runs first. By the time `WHERE` runs, the joined rows already exist as a fixed set; `WHERE` can only remove some of them, it cannot change which rows the join produced in the first place.

</details>

## Know this

### A join is a cross product with a condition

The small fixture has eight customers and twelve orders. A `CROSS JOIN` pairs every customer row with every order row, with no condition at all:

```sql
SELECT count(*) FROM customers CROSS JOIN orders;
```

```
count
-----
96
```

Eight customers times twelve orders is ninety-six, and that is exactly what comes back. An `INNER JOIN` is the same cross product with a condition attached that discards every pair for which the condition is not true:

```sql
SELECT count(*) FROM customers c JOIN orders o ON c.id = o.customer_id;
```

```
count
-----
12
```

Twelve survive, one per order, because `c.id = o.customer_id` is true for exactly one customer per order, which is what the foreign key from lesson 6 guarantees. The other eighty-four pairs are not deleted rows, they are pairs the condition never accepted. PostgreSQL's planner does not actually build ninety-six rows to throw most away, but the result is defined as though it did, and that definition is what a join is.

### ON versus WHERE, for an inner join

For an inner join, the condition can live in `ON` or in `WHERE` and the two forms give the same rows. Written with `ON`:

```sql
SELECT count(*) FROM customers c JOIN orders o ON c.id = o.customer_id;
```

gives 12, as above. Written as an implicit cross product filtered in `WHERE`:

```sql
SELECT count(*) FROM customers, orders WHERE customers.id = orders.customer_id;
```

```
count
-----
12
```

Also 12. For an inner join, `ON` and `WHERE` are two spellings of the same filter, a matter of readability rather than correctness. That equivalence stops holding once an outer join is involved: lesson 8 shows a left join where moving a condition from `ON` into `WHERE` turns it back into an inner join and changes the row count.

### Aliases, and the ambiguous column error

`customers` and `orders` both have a column called `id`, and the two columns mean entirely different things: one identifies a customer, the other identifies an order. Selecting `id` unqualified from the join between them does not guess which one you mean:

```sql
SELECT id FROM customers c JOIN orders o ON c.id = o.customer_id;
```

```
ERROR:  column reference "id" is ambiguous
SQLSTATE: 42702
```

The alias exists to resolve exactly this. Qualifying each reference with the alias it came from removes the ambiguity, and lets both `id` columns appear side by side in the same row:

```sql
SELECT o.id, c.id, c.email, c.country
FROM orders o JOIN customers c ON o.customer_id = c.id
ORDER BY o.id LIMIT 3;
```

```
id  | id | email           | country
----+----+-----------------+--------
101 | 1  | ada@example.com | GB
102 | 1  | ada@example.com | GB
103 | 1  | ada@example.com | GB
```

The output still has two columns called `id`: PostgreSQL demands only that the *reference* be unambiguous, not the output's names.

### Many-to-one, and a three-way join through countries

That last result also shows the shape a join takes when the relationship is many-to-one: an order has exactly one customer, so joining orders to customers gives one row per order, and the customer's own columns, `email` and `country`, repeat identically across every order of that customer. Customer 1 appears three times because customer 1 placed three orders. That repetition is the join working correctly, not a bug; one row per customer instead is a different question, and grouping is how you ask it, lesson 9's job.

Adding a third table chains the same logic. Joining `orders` to `customers` to `countries`, matching each customer's country code against the lookup table:

```sql
SELECT count(*)
FROM customers c
JOIN orders o ON o.customer_id = c.id
JOIN countries n ON n.code = c.country;
```

```
count
-----
9
```

Nine, not twelve. Three orders vanished, belonging to customers 2, 5 and 8. Customer 5's country is `NL`, and `countries` has no row for `NL`, so `n.code = c.country` never has a match to make. Customers 2 and 8 have `country IS NULL`, and a `NULL` cannot equal anything, the same rule lesson 3 gave: an unknown value never satisfies an equality test. The inner join treats "no match" and "no data to match" identically and drops the row either way. Lesson 8 covers the fix, an outer join that keeps a row even when this table has nothing to offer it.

### A self-join: pairs of orders from the same customer

A table can join to itself, useful for a relationship between two rows of the same table, such as pairs of orders placed by the same customer. The first attempt joins `orders` to itself on `customer_id`:

```sql
SELECT count(*) FROM orders o1 JOIN orders o2 ON o1.customer_id = o2.customer_id;
```

```
count
-----
26
```

Twenty-six is too many, for two separate reasons. First, every order pairs with itself, since an order's `customer_id` always equals its own `customer_id`; that accounts for twelve of the twenty-six. Second, every genuine pair appears twice, `(101, 102)` and `(102, 101)` both satisfy the condition. Excluding self-pairs with `o1.id <> o2.id` removes the first problem and leaves the doubled genuine pairs:

```sql
SELECT count(*) FROM orders o1 JOIN orders o2
ON o1.customer_id = o2.customer_id AND o1.id <> o2.id;
```

```
count
-----
14
```

Fourteen, which is exactly twice seven. Replacing `<>` with `<` keeps only one direction of each pair, which fixes both problems at once, since a row can never satisfy `id < id` against itself either:

```sql
SELECT count(*) FROM orders o1 JOIN orders o2
ON o1.customer_id = o2.customer_id AND o1.id < o2.id;
```

```
count
-----
7
```

Seven genuine pairs: customer 1 contributes three, from orders 101 to 103; customer 4 contributes three, from 106 to 108, the customer with three orders including a large one; customer 7 contributes one, from 110 and 111. `o1.id < o2.id` is worth writing as a habit whenever a self-join's two sides are an unordered pair rather than an ordered one.

### USING as shorthand, and NATURAL JOIN as a trap

When both sides of a join name the shared column identically, `USING` says the same as an `ON` equality with less repetition, and folds the two copies of that column into one:

```sql
SELECT count(*) FROM orders o1 JOIN orders o2 USING (customer_id) WHERE o1.id < o2.id;
```

```
count
-----
7
```

Same seven pairs, and `customer_id` appears once in a `SELECT *` rather than twice. `NATURAL JOIN` goes further and guesses the shared columns instead of naming them, joining on every column with the same name on both sides. That guess is the trap. `customers` and `orders` both have a column called `id`, one identifying a customer and the other an order, and `NATURAL JOIN` cannot tell they are unrelated:

```sql
SELECT count(*) FROM customers NATURAL JOIN orders;
```

```
count
-----
0
```

Zero rows, not an error. PostgreSQL joined on `customers.id = orders.id`, and since customer identifiers run 1 to 8 while order identifiers run 101 to 112, no pair matches. The query is syntactically fine and silently answers a question nobody asked. A `NATURAL JOIN` between `orders` and `countries`, sharing no column name at all, is quietly worse: it degrades to a plain cross product, the same 96 rows as the earlier unconditional `CROSS JOIN`, with nothing in the query to say so. A natural join's condition depends on which columns two tables happen to name alike, a fact that lives in the schema rather than the query and can change under you. Writing the condition out with `ON` or `USING` keeps the join's meaning where you can read it.

## Practice

1. ▢ Predict the row count of `SELECT count(*) FROM countries CROSS JOIN customers`, from the sizes of the two tables.

<details markdown="1"><summary>Check</summary>

Sixty-four: eight countries times eight customers, with no condition to remove any pair.

</details>

2. ▢ Predict the row count of joining `orders` to `customers` on the foreign key, then filtering to `amount > 100` in `WHERE` after the join.

<details markdown="1"><summary>Hint</summary>

Filtering after an inner join filters the join's own output; only which rows survive changes, not the join itself.

</details>

<details markdown="1"><summary>Check</summary>

5 rows, from orders 101, 104, 106, 110 and 112.

</details>

3. ▢ The three-way join through `countries` in this lesson gives 9 rows. Predict what happens if you select the bare column `id` instead of a qualified one.

<details markdown="1"><summary>Check</summary>

`ERROR: column reference "id" is ambiguous`, SQLSTATE `42702`, the same error as the two-table case: `customers.id` and `orders.id` are both still present, and a third table does not remove the ambiguity between the first two.

</details>

4. ▢ Without running it, predict the row count of the self-join with `o1.id <> o2.id` instead of `o1.id < o2.id`, and say in one sentence why it is not 7.

<details markdown="1"><summary>Check</summary>

Fourteen rows: `<>` removes only the self-pairs, not the doubling, so each of the seven genuine pairs still appears twice, once with each order first.

</details>

5. ▢ Predict the row count of `SELECT count(*) FROM orders NATURAL JOIN countries`, given that the two tables share no column name at all.

<details markdown="1"><summary>Hint</summary>

`NATURAL JOIN` needs at least one shared column name to build a condition from. What is left when there are none?

</details>

<details markdown="1"><summary>Check</summary>

96, the same as `orders CROSS JOIN countries`. With no shared name, `NATURAL JOIN` has nothing to filter on and degrades to an unconditional cross product.

</details>

6. ▢ Rewrite item 4's self-join to use `USING (customer_id)` instead of `ON`, and predict whether `SELECT *` from it shows `customer_id` once or twice.

<details markdown="1"><summary>Check</summary>

Once. `USING` merges the two `customer_id` columns into a single output column, unlike an `ON` join, which keeps both. The row count is unaffected.

</details>

## Real-world reps

- [ ] Take a report at work built on two or more joined tables and write out, in one sentence per join, what the `ON` condition claims about the relationship between the tables.
- [ ] Find a query in your own work that uses an implicit join, a comma in `FROM` and a condition in `WHERE`, and rewrite it with an explicit `JOIN ... ON`. Confirm the row count is unchanged.
- [ ] Tomorrow: search your own codebase for `NATURAL JOIN`. If you find one, work out by hand which columns it is actually joining on, and whether that is still true after the last schema change.

## Going further

- [7.2 Table Expressions](https://www.postgresql.org/docs/current/queries-table-expressions.html): the full grammar for `ON`, `USING` and `NATURAL JOIN`, including the note that `NATURAL` is riskier than `USING` when a table gains a column
- [Joins Between Tables](https://www.postgresql.org/docs/current/tutorial-join.html): a tutorial-level walkthrough with more join shapes than this lesson covers
- [9.2 Comparison Functions and Operators](https://www.postgresql.org/docs/current/functions-comparison.html): why `NULL` never satisfies an equality condition, the reason customers 2, 5 and 8 dropped out above
- [Querying](../reference/querying.md): the stage 2 reference sheet
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
