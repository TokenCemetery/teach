---
title: 8. Outer Joins and the Rows That Are Not There
description: An outer join keeps the rows that matched nothing, and one WHERE clause silently throws them away again
type: lesson
---

# Lesson 8. Outer Joins and the Rows That Are Not There

**Mission link:** A report that must add "customers with zero orders" to a total needs exactly the rows an inner join throws away. Get the WHERE clause wrong on the outer join built to find them, and the report silently goes back to counting only what matched, with no error to say so.
**Primary source:** [PostgreSQL, 7.2.1 The FROM Clause](https://www.postgresql.org/docs/current/queries-table-expressions.html)
**Prerequisites:** [Lesson 3](0003-null-and-three-valued-logic.md), [Lesson 7](0007-joins-and-what-they-do.md)

## Warm-up

1. ▢ Lesson 7's three-table join through `countries` returned 9 rows instead of 12, because customer 5's country `NL` matched nothing and customers 2 and 8's country was `NULL`. What kind of join produced that drop, and does it ever keep a row when the other side has nothing to offer?

<details markdown="1"><summary>Check</summary>

An inner join, and no: it keeps only pairs where the condition is true, so a customer with no match, or no value to match, is dropped entirely, with no trace left behind.

</details>

## Know this

### LEFT JOIN keeps the row, and invents what the other side would have had

Lesson 7's inner join of `customers` and `orders` returns 12 rows and drops customer 6, because no order's `customer_id` ever equals 6. A `LEFT JOIN` keeps every left-hand row regardless of whether anything on the right matches:

```sql
SELECT count(*) FROM customers c LEFT JOIN orders o ON o.customer_id = c.id;
```

```
count
-----
13
```

One more than the inner join's 12; the extra row:

```sql
SELECT c.id, c.email, o.id, o.amount, o.shipped_at
FROM customers c LEFT JOIN orders o ON o.customer_id = c.id
WHERE c.id = 6;
```

```
id | email               | id | amount | shipped_at
---+---------------------+----+--------+-----------
6  | barbara@example.com |    |        |
```

Every `orders` column is `NULL`, and the origin matters: lesson 3's `NULL`s sit inside a row that exists, while this one sits inside a row that does not exist, since there is no order for customer 6 and PostgreSQL invented an empty one so it could still appear. The origin differs, a manufactured placeholder rather than an absent value, but the behaviour afterwards is identical: unknown in every comparison, exactly as lesson 3 described.

### The trap: a WHERE clause after LEFT JOIN can undo it

Add a condition on `amount`, written in `WHERE`:

```sql
SELECT count(*)
FROM customers c LEFT JOIN orders o ON o.customer_id = c.id
WHERE o.amount > 100;
```

```
count
-----
5
```

Five rows, fewer even than the inner join's 12: only orders over 100 survive, and customer 6 is not among them. Its invented `amount` is `NULL`, and `NULL > 100` is unknown, so `WHERE` drops the row. The join produced the row; `WHERE`, running after `FROM` by lesson 2's evaluation order, then discarded it. The query still reads `LEFT JOIN` but behaves like the inner join over the same condition, with nothing in the syntax to say so.

Move the identical condition into `ON`:

```sql
SELECT count(*)
FROM customers c LEFT JOIN orders o ON o.customer_id = c.id AND o.amount > 100;
```

```
count
-----
8
```

Eight rows, one per customer. `amount > 100` now decides which `orders` rows match, rather than filtering the output afterwards. A customer whose every order is 100 or under matches nothing, and the join invents a `NULL` row exactly as for a customer with no orders. Customer 6 reappears, this time for the ordinary reason: no order of theirs met the amount.

The rule: a condition on the outer table's own columns belongs in `ON`, deciding what counts as a match; the same condition in `WHERE` filters the result after the join has run, and testing a real value against an invented `NULL` can turn that invention into a reason to drop the row it exists for.

### count(*) against count(o.id): the most common wrong answer in the stage

Grouped per customer, counting two ways:

```sql
SELECT c.id, count(*), count(o.id)
FROM customers c LEFT JOIN orders o ON o.customer_id = c.id
GROUP BY c.id ORDER BY c.id;
```

```
id | count | count
---+-------+------
1  | 3     | 3
2  | 1     | 1
3  | 1     | 1
4  | 3     | 3
5  | 1     | 1
6  | 1     | 0
7  | 2     | 2
8  | 1     | 1
```

Every customer agrees on both counts except customer 6, where they read 1 and 0. `count(*)` counts rows, full stop, and customer 6 still has one: the invented row. `count(o.id)` counts values of a specific column, ignoring `NULL` like every aggregate, and the invented row's `o.id` is `NULL`, contributing nothing. Asked "how many orders does customer 6 have", `count(*)` answers 1, wrongly; `count(o.id)`, or any other `orders` column, answers 0, correctly. The gap opens only on the invented row, so the two counts agree everywhere else, which is what makes the wrong habit easy to pick up.

### Finding the rows with nothing on the other side

```sql
SELECT c.id, c.email
FROM customers c LEFT JOIN orders o ON o.customer_id = c.id
WHERE o.id IS NULL;
```

```
id | email
---+--------------------
6  | barbara@example.com
```

Customer 6, and only customer 6. This `WHERE` tests a `NULL` after an outer join, the same shape flagged as a trap above, correct here because what the condition asks has changed. `amount > 100` tests a value that would matter if it existed, and returns unknown when it does not; `o.id IS NULL` asks whether the value is missing, and `IS NULL` is lesson 3's one test that never returns unknown on a `NULL`: true for the rows the join invented, false everywhere else. It is safe here only because the condition asks about nullness itself. This idiom is called an anti-join: the standard way to ask which rows have nothing on the other side. Lesson 11 covers `NOT EXISTS` and `NOT IN` as an alternative.

### RIGHT JOIN and FULL JOIN, and reading a query left to right

Against `countries`:

```sql
SELECT count(*) FROM customers c RIGHT JOIN countries n ON n.code = c.country;
```

```
count
-----
10
```

`RIGHT JOIN` is `LEFT JOIN` with the tables' roles swapped: it keeps every `countries` row, matched or not, and drops any `customers` row that fails to match. Five of the ten rows are `DE`, `FR`, `BR`, `IN` and `KE`, the countries nobody lives in; the rest are the matched pairs for `GB`, `US` and `JP`. Customer 5 (`NL`) and customers 2 and 8 (`NULL` country) are simply absent.

```sql
SELECT count(*) FROM customers c FULL JOIN countries n ON n.code = c.country;
```

```
count
-----
13
```

Three more than the `RIGHT JOIN`'s 10: `FULL JOIN` also keeps the left side's unmatched rows, so customers 5, 2 and 8 reappear, each with every `countries` column `NULL`, the same pattern as before, now on the other table.

Swapping which table is named first turns the `RIGHT JOIN` above into a `LEFT JOIN` with the identical ten rows:

```sql
SELECT count(*) FROM countries n LEFT JOIN customers c ON c.country = n.code;
```

```
count
-----
10
```

Every reader reads `FROM` left to right, and `LEFT JOIN`'s shape, everything named first plus whatever matches, is the one already being tracked; `RIGHT JOIN` asks them to hold that picture backwards. In SQLite 3.51 both queries return the same 10 and 13 rows against the identical fixture, so the rewrite is a habit worth having, not a portability workaround.

### Reconciling two lists with FULL JOIN

This is what `FULL JOIN` is actually for: comparing two lists that should line up, and finding where they do not.

```sql
SELECT c.id, c.country, n.code
FROM customers c FULL JOIN countries n ON n.code = c.country
WHERE n.code IS NULL OR c.id IS NULL
ORDER BY c.id NULLS LAST, n.code;
```

```
id | country | code
---+---------+-----
2  |         |
5  | NL      |
8  |         |
   |         | BR
   |         | DE
   |         | FR
   |         | IN
   |         | KE
```

Each row names which side is missing: where `n.code` is `NULL`, that country value exists among customers but nowhere in `countries`, the `NL` case; where `c.id` is `NULL`, that code exists in `countries` but no customer has it, the five country-only codes. Testing `IS NULL` on each side separately, rather than combined with `OR` as above, is what lets a report say which list a mismatch belongs to.

## Practice

1. ▢ Rewrite `SELECT count(*) FROM orders o RIGHT JOIN customers c ON o.customer_id = c.id` as a `LEFT JOIN`, tables swapped, and predict whether the count changes.

<details markdown="1"><summary>Check</summary>

It does not: both return 13. `RIGHT JOIN` is `LEFT JOIN` with the operands reversed, not a separate operation.

</details>

2. ▢ After `customers c LEFT JOIN orders o ON o.customer_id = c.id`, predict whether `WHERE o.shipped_at IS NULL` still keeps customer 6, and how that differs from `WHERE o.amount > 100`.

<details markdown="1"><summary>Hint</summary>

What does the invented row's `shipped_at` equal, and what does `IS NULL` do with that, as opposed to `>`?

</details>

<details markdown="1"><summary>Check</summary>

Customer 6 is kept, one of 5 rows returned. Its invented `shipped_at` is `NULL`, and `IS NULL` does not evaluate to unknown against a `NULL`, so it reports true, unlike `amount > 100`, which compares `NULL` to a number and returns unknown, dropping the row instead.

</details>

3. ▢ Grouped per customer, predict `count(*)` and `count(o.amount)` for customer 6, and whether `count(o.customer_id)` would differ from `count(o.amount)`.

<details markdown="1"><summary>Check</summary>

1 and 0. `count(o.customer_id)` also gives 0: every column of the invented row is `NULL`, so any `orders` column gives the same answer. `count(*)` never asks about a specific column, so it alone reports the row.

</details>

4. ▢ Predict the row count of `customers c LEFT JOIN countries n ON n.code = c.country WHERE n.region = 'Europe'`, and whether customer 5 is in the result.

<details markdown="1"><summary>Hint</summary>

Customer 5's country is `'NL'`, which has no row in `countries` at all, so what does `n.region` equal for that customer once the join has run?

</details>

<details markdown="1"><summary>Check</summary>

2 rows, customers 1 and 3, both country `GB`. Customer 5 is gone: the same trap as `amount > 100`, moved to a lookup join. `n.region` is `NULL` for the invented row, `NULL = 'Europe'` is unknown, and `WHERE` drops it.

</details>

5. ▢ `customers FULL JOIN countries ON n.code = c.country` returns 13 rows. For the `NL` row, predict which of `n.code` and `c.id` is `NULL`; for the `BR` row, predict which side is `NULL` instead.

<details markdown="1"><summary>Check</summary>

For `NL`, `n.code` is `NULL`: no `countries` row has that code. For `BR`, `c.id` and every other customer column is `NULL`: no customer's country equals `'BR'`. `NULL` lands on whichever side failed to match, letting `IS NULL` tell you which list is missing a row.

</details>

6. ▢ Write a query that lists every country code with no customers, using a `LEFT JOIN` rather than `RIGHT JOIN` or `FULL JOIN`.

<details markdown="1"><summary>Hint</summary>

An anti-join needs the table you are asking about, `countries`, on the left, then a `WHERE` testing the invented side of the join for `NULL`.

</details>

<details markdown="1"><summary>Check</summary>

```sql
SELECT n.code
FROM countries n
LEFT JOIN customers c ON c.country = n.code
WHERE c.id IS NULL;
```

Five rows: `BR`, `DE`, `FR`, `IN`, `KE`. `LEFT JOIN` from `countries` invents a `NULL` customer for every code nothing matches, and `c.id IS NULL` picks those out, the same idiom as earlier, tables reversed.

</details>

## Real-world reps

- [ ] Take a report that should include rows with a zero or empty count, and check whether its filter sits correctly on an outer join, or an inner join quietly excludes them.
- [ ] Find a `RIGHT JOIN` you can read, rewrite it as a `LEFT JOIN` with the tables swapped, and confirm the result is identical.
- [ ] Tomorrow: pick two lists that should reconcile, write a `FULL JOIN` with `IS NULL` tested on each side, then find a row that exists on only each list.

## Going further

- [SQLite, Release 3.39.0](https://www.sqlite.org/releaselog/3_39_0.html): the release that added support for `RIGHT` and `FULL OUTER JOIN`, in its own words long overdue
- [Use The Index, Luke, Outer Joins](https://use-the-index-luke.com/sql/join): why a WHERE clause can undo an outer join
- [PostgreSQL, 9.2 Comparison Functions and Operators](https://www.postgresql.org/docs/current/functions-comparison.html): the `IS NULL` predicate that survives a `NULL`
- [Querying](../reference/querying.md): the stage 2 reference sheet
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
