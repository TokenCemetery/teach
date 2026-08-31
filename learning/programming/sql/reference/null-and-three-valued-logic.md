---
title: NULL and Three-Valued Logic
description: Truth tables, where NULL counts as equal, and the operators that survive it
type: reference
---

# NULL and Three-Valued Logic

Lookup sheet for stage 1. The question it exists to answer: **why did this row not come back?**

## The one rule

`NULL` is a marker for the absence of a value, not a value. Any comparison with it yields **unknown**.

**`WHERE`, `ON` and `HAVING` keep a row only when the condition is true.** Unknown is discarded exactly like false.

## Truth tables

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

| `NOT` | |
|---|---|
| `NOT true` | false |
| `NOT false` | true |
| `NOT unknown` | unknown |

`false AND unknown` is false and `true OR unknown` is true, so a `NULL` can be harmless in one position and fatal in another.

## What each expression yields

| Expression | Result |
|---|---|
| `NULL = NULL` | unknown |
| `NULL <> NULL` | unknown |
| `NULL = 1` | unknown |
| `NULL IS NULL` | true |
| `NULL IS NOT DISTINCT FROM NULL` | true |
| `NULL + 1` | `NULL` |
| `'a' \|\| NULL` | `NULL` |
| `count(*)` over 0 rows | `0` |
| `sum(x)` over 0 rows | `NULL` |
| `coalesce(NULL, NULL, 3)` | `3` |

## Where NULL behaves as if equal

The asymmetry worth memorising: for **comparison** two NULLs are unknown, and for **grouping and deduplication** they are the same thing.

| Operation | Two NULLs are |
|---|---|
| `=`, `<>`, `<`, `>` | unknown |
| `IS NOT DISTINCT FROM` | equal |
| `GROUP BY` | one group |
| `DISTINCT` | duplicates |
| `UNION`, `INTERSECT`, `EXCEPT` | duplicates |
| `ORDER BY` | tied |
| `UNIQUE` constraint | distinct, so several are allowed |
| `CHECK` constraint | passes, because only false fails |

## Aggregates

| Query | Behaviour |
|---|---|
| `count(*)` | counts rows |
| `count(col)` | counts non-null values |
| `sum`, `avg`, `min`, `max` | skip NULLs entirely |
| `avg(col)` | divides by the count of non-null values, not by the row count |
| any aggregate over no rows | `NULL`, except `count`, which is `0` |

`count(*)` next to `count(col)` is the cheapest way to measure how complete a column is.

Wrap any total that feeds arithmetic or a report: `coalesce(sum(amount), 0)`.

## Traps, with the fix

| Trap | Why | Fix |
|---|---|---|
| `WHERE col = NULL` | always unknown, returns nothing | `WHERE col IS NULL` |
| `WHERE col <> 'x'` expecting the NULL rows | unknown, so they are dropped | `WHERE col <> 'x' OR col IS NULL` |
| `NOT IN (SELECT nullable)` | one `NULL` empties the result | `NOT EXISTS (...)` |
| `UNIQUE` on a nullable column | many NULLs allowed | add `NOT NULL`, or `UNIQUE NULLS NOT DISTINCT` |
| `sum()` used in arithmetic | `NULL` over no rows | `coalesce(sum(...), 0)` |
| `ORDER BY d DESC` for "most recent" | NULLs sort first in PostgreSQL | `ORDER BY d DESC NULLS LAST` |
| `avg()` treating NULL as zero | it does not | `avg(coalesce(col, 0))` when zero is meant |
| a `CHECK` that is unknown | unknown passes | state the null case explicitly |

## Expanding `NOT IN`

```sql
id NOT IN (1, NULL)
-- expands to
id <> 1 AND id <> NULL
-- which is
(true or false) AND unknown
-- which is never true
```

`IN` is safer only by accident: `id IN (1, NULL)` is true when `id` is 1 and unknown otherwise, so it fails to match rather than emptying the result.

## Substituting a value

| Function | Does |
|---|---|
| `coalesce(a, b, c)` | first non-null argument |
| `nullif(a, b)` | `NULL` when `a = b`, else `a` |
| `greatest`, `least` | ignore NULLs in PostgreSQL, which is engine-specific |

Note that `coalesce(col, 'x') = 'x'` prevents an index on `col` from being used, so it is a reporting tool rather than a filtering one.

## Deciding in review

1. Which columns in this query are nullable? Check the schema, not the sample data.
2. Does any of them appear in a comparison? Then the unknown case is being discarded.
3. Is there a `NOT IN` with a subquery? Then check the selected column is `NOT NULL`.
4. Does the query claim to partition rows, for example a matching and a non-matching branch? Then the NULL rows are in neither.
5. Does an aggregate feed arithmetic? Then the empty-input case is `NULL`.

## Sources

- [9.2 Comparison Functions and Operators](https://www.postgresql.org/docs/current/functions-comparison.html)
- [9.1 Logical Operators](https://www.postgresql.org/docs/current/functions-logical.html)
- [9.18 Conditional Expressions](https://www.postgresql.org/docs/current/functions-conditional.html)
- [Three-Valued Logic, Modern SQL](https://modern-sql.com/concept/three-valued-logic)
- [NULL Handling in SQLite](https://www.sqlite.org/nulls.html)
