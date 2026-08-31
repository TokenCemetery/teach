---
title: 3. NULL and Three-Valued Logic
description: WHERE keeps only true, so unknown behaves as false and NOT IN can return nothing
type: lesson
---

# Lesson 3. NULL and Three-Valued Logic

**Mission link:** This is the lesson that lets you say why a query returned exactly those rows. Every "the row is definitely in the table" bug in this workspace comes from a comparison that evaluated to unknown.
**Primary source:** [PostgreSQL, 9.2 Comparison Functions and Operators](https://www.postgresql.org/docs/current/functions-comparison.html)
**Prerequisites:** [Lesson 2](0002-select-and-evaluation-order.md)

## Warm-up

1. ▢ Put `WHERE`, `SELECT`, `HAVING`, `GROUP BY` in evaluation order, and say why `WHERE` cannot use an alias.

<details markdown="1"><summary>Check</summary>

`WHERE`, `GROUP BY`, `HAVING`, `SELECT`. The alias is created by the `SELECT` list, which runs after `WHERE`.

</details>

2. ▢ Why is `SELECT * FROM orders LIMIT 10` not reproducible?

<details markdown="1"><summary>Check</summary>

A table has no inherent order, so without `ORDER BY` the engine may return any ten rows, and which ten can change with the plan or the cache.

</details>

## Know this

SQL has three truth values: **true**, **false** and **unknown**. `NULL` is not a value but a marker for the absence of one, and any comparison involving it yields unknown ([three-valued logic](https://modern-sql.com/concept/three-valued-logic)).

```sql
NULL = NULL        -- unknown, NOT true
NULL <> NULL       -- unknown
NULL = 1           -- unknown
NULL + 1           -- NULL, arithmetic propagates it too
'a' || NULL        -- NULL in standard SQL
```

**`WHERE` keeps a row only when the condition is true.** Unknown is discarded exactly like false. That one sentence explains most of what follows.

```sql
SELECT count(*) FROM customers;                          -- 2
SELECT count(*) FROM customers WHERE country = 'GB';     -- 1
SELECT count(*) FROM customers WHERE country <> 'GB';    -- 0, not 1
```

The customer with a `NULL` country satisfies neither, because both comparisons are unknown. The two filters do not partition the table, and expecting them to is the single most common `NULL` mistake.

### The operators that work on unknown

```sql
WHERE country IS NULL
WHERE country IS NOT NULL
WHERE country IS NOT DISTINCT FROM other      -- like =, but NULL equals NULL
WHERE coalesce(country, 'unknown') = 'unknown'
```

`IS NULL` is the only comparison that answers the question, which is why `= NULL` is always wrong rather than merely unusual. `IS NOT DISTINCT FROM` is the null-safe equality, and `coalesce` substitutes a value.

### Truth tables worth knowing

`AND` and `OR` are not symmetric in how they treat unknown ([logical operators](https://www.postgresql.org/docs/current/functions-logical.html)):

| `AND` | true | false | unknown |
|---|---|---|---|
| **true** | true | false | unknown |
| **false** | false | false | false |
| **unknown** | unknown | false | unknown |

| `OR` | true | false | unknown |
|---|---|---|---|
| **true** | true | true | true |
| **false** | true | false | unknown |
| **unknown** | true | unknown | unknown |

`false AND unknown` is false, and `true OR unknown` is true. So a `NULL` can be harmless in one position and fatal in another, which is why the next trap is so easy to write.

### `NOT IN` with a NULL returns nothing

```sql
SELECT * FROM customers
WHERE id NOT IN (SELECT customer_id FROM orders WHERE amount > 100);
```

If that subquery returns even one `NULL`, the whole query returns **zero rows**, always. `id NOT IN (1, NULL)` expands to `id <> 1 AND id <> NULL`, and the second term is unknown, so the conjunction is never true.

`IN` does not have the problem in the same way: `id IN (1, NULL)` is true when `id` is 1, and unknown otherwise, so it merely fails to match rather than emptying the result.

Use `NOT EXISTS`, which is null-safe and usually faster:

```sql
SELECT * FROM customers c
WHERE NOT EXISTS (
    SELECT 1 FROM orders o WHERE o.customer_id = c.id AND o.amount > 100
);
```

### Aggregates skip NULLs, and one of them counts them

```sql
SELECT count(*)          FROM customers;   -- 2, counts rows
SELECT count(country)    FROM customers;   -- 1, skips NULLs
SELECT avg(amount)       FROM orders;      -- ignores NULL amounts entirely
SELECT sum(amount)       FROM orders WHERE false;   -- NULL, not 0
```

`count(*)` counts rows. `count(column)` counts non-null values, which makes `count(column)` a useful way to ask "how many rows have this". `avg` divides by the number of non-null values, so a `NULL` is not treated as zero. And an aggregate over no rows is `NULL` for everything except `count`, which is why report queries wrap totals in `coalesce(sum(...), 0)`.

### Where NULL behaves as if equal

The inconsistency worth memorising: for **comparison** two NULLs are unknown, and for **grouping and deduplication** they are the same.

| Operation | Two NULLs are |
|---|---|
| `=` | unknown |
| `GROUP BY` | one group |
| `DISTINCT` | duplicates |
| `UNION` | duplicates |
| `ORDER BY` | tied |
| `UNIQUE` constraint | distinct, so several are allowed |

The last row is the surprising one: a `UNIQUE` column accepts any number of NULLs, because two NULLs are not equal for the purposes of the constraint. PostgreSQL 15 added `UNIQUE NULLS NOT DISTINCT` to opt out.

### Ordering

In PostgreSQL, NULLs sort as though larger than every value: last under `ASC`, first under `DESC`. The standard leaves this to the engine, so state it explicitly when it matters:

```sql
ORDER BY shipped_at DESC NULLS LAST
```

## Practice

1. ▢ The table has two rows, one with `country = 'GB'` and one with `country IS NULL`. Predict all three counts.

   ```sql
   SELECT count(*) FROM customers WHERE country = 'GB';
   SELECT count(*) FROM customers WHERE country <> 'GB';
   SELECT count(*) FROM customers WHERE country IS NULL;
   ```

<details markdown="1"><summary>Check</summary>

`1`, `0`, `1`.

The `NULL` row makes both comparisons unknown, and `WHERE` keeps only true. The two filters together return one row out of two, which is the demonstration that they do not partition the table.

</details>

2. ▢ This query is supposed to list customers with no large orders. It returns nothing at all. Why?

   ```sql
   SELECT * FROM customers
   WHERE id NOT IN (SELECT customer_id FROM orders WHERE amount > 100);
   ```

<details markdown="1"><summary>Hint</summary>

Expand `NOT IN` into a chain of `<>` conditions joined by `AND`, then ask what happens if one value in the list is `NULL`.

</details>

<details markdown="1"><summary>Check</summary>

The subquery returned at least one `NULL`, so the expansion contains `id <> NULL`, which is unknown. A conjunction containing unknown is never true unless another term is false, and here no term is false for a row that matches nothing, so no row is ever kept.

Rewrite with `NOT EXISTS`, which compares row by row and is unaffected. Note that in the given schema `customer_id` is `NOT NULL`, so this exact query is safe; the trap appears the moment the subquery selects a nullable column, which is most of the time.

</details>

3. ▢ Which of these correctly finds rows where `country` is absent?

   - a) `WHERE country = NULL`
   - b) `WHERE country IS NULL`
   - c) `WHERE country <> 'GB'`
   - d) `WHERE coalesce(country, '') = ''`

<details markdown="1"><summary>Check</summary>

**b)** always, and **d)** with a caveat.

Option a is unknown for every row and returns nothing. Option c misses the NULL rows entirely. Option d works and also matches a row whose country is the empty string, which is a different state, and it prevents an index on `country` from being used, which stage 6 will care about.

</details>

4. ▢ Predict both, and say what each is useful for.

   ```sql
   SELECT count(*), count(country) FROM customers;
   SELECT sum(amount) FROM orders WHERE customer_id = 999;
   ```

<details markdown="1"><summary>Check</summary>

`2, 1`, then `NULL`.

`count(*)` counts rows, `count(country)` counts non-null values, so the pair together tells you how complete a column is. That is genuinely useful in data investigation.

The `sum` over no rows is `NULL` rather than `0`, which breaks any arithmetic downstream. Write `coalesce(sum(amount), 0)` in any query whose result feeds a calculation or a report.

</details>

5. ▢ A `UNIQUE` constraint exists on `customers(email)`. A colleague says the table therefore cannot contain two rows with the same email. Under what condition are they wrong?

<details markdown="1"><summary>Check</summary>

They are wrong if `email` is nullable: a `UNIQUE` constraint permits any number of NULLs, because two NULLs are not equal for the constraint's purposes.

In this workspace's schema `email` is `NOT NULL`, so the constraint means what they think. That combination, `UNIQUE` plus `NOT NULL`, is what actually guarantees at most one row per value, and it is also exactly what a primary key is.

</details>

## Real-world reps

- [ ] Insert a customer with a `NULL` country and run the three counts from practice 1. Getting `0` from the `<>` query once is what makes this permanent.
- [ ] Build the `NOT IN` trap deliberately: a subquery over a nullable column with one `NULL` in it. Then convert it to `NOT EXISTS` and see the rows appear.
- [ ] Tomorrow: search queries you know for `NOT IN (SELECT`. Each one is a bug unless the selected column is `NOT NULL`, and the constraint is worth checking rather than assuming.

## Going further

- [9.2 Comparison Functions and Operators](https://www.postgresql.org/docs/current/functions-comparison.html): `IS NULL`, `IS NOT DISTINCT FROM` and the rest
- [9.1 Logical Operators](https://www.postgresql.org/docs/current/functions-logical.html): the truth tables, from the engine
- [Three-Valued Logic](https://modern-sql.com/concept/three-valued-logic): why the standard works this way, and where engines differ
- [NULL Handling in SQLite](https://www.sqlite.org/nulls.html): the same rules on the second engine, with its historical deviations noted
- [NULL and three-valued logic](../reference/null-and-three-valued-logic.md): the reference sheet, for lookup
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
