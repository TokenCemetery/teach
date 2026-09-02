---
title: 17. Lateral Joins
description: LATERAL lets a subquery in FROM see the row beside it, which is how you take the top few per group
type: lesson
---

# Lesson 17. Lateral Joins

**Mission link:** The largest order per customer, the latest login per account, the top three products in each category: every one of these needs a subquery that knows which customer, account or category it is currently working on, and a plain subquery in `FROM` cannot be told that. `LATERAL` is the keyword that tells it.
**Primary source:** [PostgreSQL, 7.2.1.5 LATERAL Subqueries](https://www.postgresql.org/docs/current/queries-table-expressions.html)
**Prerequisites:** [Lesson 11](0011-subqueries.md), [Lesson 14](0014-window-functions.md)

## Warm-up

1. ▢ Lesson 11's derived table runs in `FROM` as a self-contained query, planned and evaluated before the rest of the statement has any row for it to sit beside. What could that derived table never do, and what does this lesson's subject let it do instead?

<details markdown="1"><summary>Check</summary>

A derived table could never reference a column of another table in the same `FROM` clause, because it is planned on its own, with no row from anywhere else in view. `LATERAL` gives a subquery in `FROM` exactly that: the row of the table beside it, so it can be correlated the way a subquery in `WHERE` always could.

</details>

## Know this

### The restriction, as an error first

Ask for the largest order per customer with an ordinary derived table, correlated the way lesson 11's `WHERE` subqueries always were, and PostgreSQL refuses before a single row runs:

```sql
SELECT c.id, top.id, top.amount
FROM customers c
JOIN (
  SELECT o.id, o.amount
  FROM orders o
  WHERE o.customer_id = c.id
  ORDER BY o.amount DESC
  LIMIT 1
) AS top ON true;
```

```
ERROR:  invalid reference to FROM-clause entry for table "c"
DETAIL:  There is an entry for table "c", but it cannot be referenced from this part of the query.
HINT:  To reference that table, you must mark this subquery with LATERAL.
SQLSTATE: 42P01
```

`c` exists, and the `DETAIL` is careful to say so; it simply is not visible from inside a subquery that lesson 11 taught you is planned as a standalone unit. The `HINT` does something a database error rarely bothers to do: it names the exact word that fixes the query, and that word is this lesson's whole subject.

### What LATERAL means, and why order now matters

Add it:

```sql
SELECT c.id, top.id, top.amount
FROM customers c
JOIN LATERAL (
  SELECT o.id, o.amount
  FROM orders o
  WHERE o.customer_id = c.id
  ORDER BY o.amount DESC
  LIMIT 1
) AS top ON true;
```

and the subquery stops being planned once and becomes something evaluated once per row of the `FROM` items to its left, each time with that row's own columns in view. That is the entire mechanism: a lateral subquery is a small program run once per outer row, with the outer row supplying its parameters.

One consequence is easy to miss: a lateral subquery can only see what is already to its left, so the order of `FROM` now carries meaning it never had before this lesson. Put the lateral subquery before the table it needs:

```sql
SELECT c.id, top.id, top.amount
FROM
  LATERAL (
    SELECT o.id, o.amount
    FROM orders o
    WHERE o.customer_id = c.id
    ORDER BY o.amount DESC
    LIMIT 1
  ) AS top,
  customers c;
```

```
ERROR:  missing FROM-clause entry for table "c"
SQLSTATE: 42P01
```

The `SQLSTATE` matches, but the message does not, and there is no `HINT` this time: `c` genuinely has not been reached yet. Writing `LATERAL` does not reorder anything in `FROM`; it only grants permission to look left.

### The archetypal use: the top row per group

The largest order per customer, run properly:

```sql
SELECT c.id, top.id, top.amount
FROM customers c
JOIN LATERAL (
  SELECT o.id, o.amount
  FROM orders o
  WHERE o.customer_id = c.id
  ORDER BY o.amount DESC
  LIMIT 1
) AS top ON true;
```

returns 7 rows, one per customer who has ever ordered. Raise the `LIMIT` to 2 and it returns 10, the top two orders per customer wherever a customer has two to offer. `ON true` reads oddly at first: an ordinary join condition compares columns from both sides, but here the join has nothing left to check, since `WHERE o.customer_id = c.id` already sits inside the subquery and decided which orders belong to `c` before the outer join ever runs. `ON true` just tells PostgreSQL to accept whatever the lateral subquery produced, once per outer row, with no further filtering.

### LEFT JOIN LATERAL, and the join-type decision arriving again

Customer 6 has no orders, so the query above cannot produce a row for it: there is nothing for the subquery to return, and an inner join drops a row with nothing to join to. That is lesson 8's decision, not a new one, so write `LEFT JOIN` if the answer must include every customer:

```sql
SELECT c.id, top.id, top.amount
FROM customers c
LEFT JOIN LATERAL (
  SELECT o.id, o.amount
  FROM orders o
  WHERE o.customer_id = c.id
  ORDER BY o.amount DESC
  LIMIT 1
) AS top ON true;
```

returns 8 rows, customer 6's `top.id` and `top.amount` both `NULL`. `LATERAL` decides whether the subquery may look sideways; `LEFT` still decides whether a customer with nothing to show survives the join. The two questions are independent, and this syntax just asks both of them in the same clause.

### A lateral subquery that aggregates

Nothing about `LATERAL` requires `LIMIT`; any correlated subquery in `FROM` needs it. A per-customer order count, including the customers with none:

```sql
SELECT c.id, cnt.n
FROM customers c
CROSS JOIN LATERAL (
  SELECT count(*) AS n
  FROM orders o
  WHERE o.customer_id = c.id
) AS cnt;
```

returns 8 rows, customer 6 among them with `n` equal to 0. `CROSS JOIN LATERAL` needs no `ON` clause at all, since a `CROSS JOIN` never had one; the correlation inside the subquery is doing all the filtering, and an aggregate always returns exactly one row per group, including a group of zero, so no customer can be dropped the way an inner join to `orders` would drop one.

### The comparison the reader actually needs

Lesson 14's `row_number()` answers the same top-1-per-customer question from a different direction:

```sql
SELECT id, customer_id, amount FROM (
  SELECT o.id, o.customer_id, o.amount,
         row_number() OVER (PARTITION BY o.customer_id ORDER BY o.amount DESC) AS rn
  FROM orders o
) ranked
WHERE rn = 1;
```

gives the identical 7 ids as the lateral version: 101, 104, 105, 106, 109, 110, 112. Same answer, genuinely different question. The lateral form asks "give me the top order, per customer" once for each row on the left and can stop as soon as its own `LIMIT` is satisfied; the window form asks "rank every order within its customer" over the whole table and only discards the rows that failed to rank first afterwards. The window form hands back the rank itself, which is useful the moment you need to know it was second rather than first; the lateral form never computes a rank, only the row that satisfied its `ORDER BY` and `LIMIT`. Keeping a customer with nothing at all costs the lateral form a `LEFT JOIN`; the window form keeps that customer only if the query it ranks over already came from an outer join, since `row_number()` never sees a customer who never reached it. Which of the two runs faster on a given table is stage 6's question, not this lesson's, and nothing here should be read as an answer to it.

One portability note closes the comparison: `LATERAL` is not a keyword in SQLite, and writing it there is a syntax error. The lateral pattern does not travel to every engine; the window rewrite above is standard enough that it does.

## Practice

1. ▢ Predict the row count of the query below, changing only the `LIMIT` from the archetypal example.

   ```sql
   SELECT c.id, top.id, top.amount
   FROM customers c
   JOIN LATERAL (
     SELECT o.id, o.amount
     FROM orders o
     WHERE o.customer_id = c.id
     ORDER BY o.amount DESC
     LIMIT 3
   ) AS top ON true;
   ```

<details markdown="1"><summary>Check</summary>

12, every order in the table. No customer has more than three orders, so `LIMIT 3` never truncates anyone's orders, and the query becomes a roundabout way of listing every order, ranked within its own customer.

</details>

2. ▢ Predict the row count of the same query with `ORDER BY o.amount ASC` instead of `DESC`, and say why the specific row returned for customer 4 is not something you can predict.

<details markdown="1"><summary>Hint</summary>

Customer 4 has two orders at the identical amount.

</details>

<details markdown="1"><summary>Check</summary>

Still 7 rows, one per customer with an order. Customer 4's two smallest orders, 107 and 108, both cost 10.00, and lesson 5 already established that a tie without a unique key in `ORDER BY` is not a stable order, so which of the two the `LIMIT 1` keeps is not fixed by anything in the query.

</details>

3. ▢ Predict the exact error, its `HINT`, and its `SQLSTATE` for the query below, which asks for the same largest-order-per-customer answer but keeps every customer.

   ```sql
   SELECT c.id, top.id, top.amount
   FROM customers c
   LEFT JOIN (
     SELECT o.id, o.amount
     FROM orders o
     WHERE o.customer_id = c.id
     ORDER BY o.amount DESC
     LIMIT 1
   ) AS top ON true;
   ```

<details markdown="1"><summary>Check</summary>

The identical failure as the plain `JOIN` version: `ERROR: invalid reference to FROM-clause entry for table "c"`, `DETAIL: There is an entry for table "c", but it cannot be referenced from this part of the query.`, `HINT: To reference that table, you must mark this subquery with LATERAL.`, `SQLSTATE 42P01`. The restriction belongs to a correlated subquery in `FROM`, not to any particular join type, so `LEFT JOIN` needs `LATERAL` exactly as much as `JOIN` does.

</details>

4. ▢ Two lateral subqueries can chain, the second one reading a column from the first. Predict what happens if their order is swapped, so the second subquery below, which produces `top`, is written after the first, which already tries to use `top.amount`.

   ```sql
   SELECT c.id
   FROM customers c
   JOIN LATERAL (
     SELECT count(*) AS n
     FROM orders o2
     WHERE o2.customer_id = c.id AND o2.amount < top.amount
   ) AS cheaper ON true
   JOIN LATERAL (
     SELECT o.amount
     FROM orders o
     WHERE o.customer_id = c.id
     ORDER BY o.amount DESC
     LIMIT 1
   ) AS top ON true;
   ```

<details markdown="1"><summary>Hint</summary>

`LATERAL` grants permission to look left; it does not move anything.

</details>

<details markdown="1"><summary>Check</summary>

`ERROR: missing FROM-clause entry for table "top"`, `SQLSTATE 42P01`, and no `HINT`, since `top` has not been written yet at the point `cheaper` tries to reference it. Written in the other order, with `top` first, the same two subqueries run and return one row per customer with an order, each carrying its largest amount and a count of that customer's cheaper orders.

</details>

5. ▢ Predict the single row, and its `n`, returned by filtering the per-customer count from "Know this" with an outer `WHERE cnt.n = 0`.

<details markdown="1"><summary>Check</summary>

One row: customer 6, `n` equal to 0. The lateral aggregate gives every customer a count, including a real zero for the one customer with no orders, and an ordinary `WHERE` on the outer query can then pick that customer out precisely because a row for it exists to filter.

</details>

6. ▢ The window rewrite in "Know this" joins `customers` to `orders` with a plain `JOIN` inside the derived table, so customer 6 never reaches `row_number()`. Predict the row count if that inner join is changed to a `LEFT JOIN`.

<details markdown="1"><summary>Hint</summary>

Look at what `LEFT JOIN LATERAL` needed earlier in this lesson to keep the same customer.

</details>

<details markdown="1"><summary>Check</summary>

8 rows. With `LEFT JOIN orders o ON o.customer_id = c.id` inside the derived table, customer 6 gets one row with `o.id` and `o.amount` both `NULL`, `row_number()` still assigns it `rn` equal to 1 within its own partition of one, and the outer `WHERE rn = 1` keeps it. The window form needed the same outer-join decision the lateral form needed, just made one level further in.

</details>

## Real-world reps

- [ ] Find a report at work that fetches "the top few rows per group" by running one query per group in application code, or by overfetching everything and filtering in memory, and rewrite it as a single query with `LATERAL` and `LIMIT`.
- [ ] Find a place where a window function was used only to pull the first or last row of each group, with the rank itself never read afterwards, and judge whether a `LATERAL` join with `LIMIT` would have asked the actual question more directly.
- [ ] Tomorrow: pick one report that silently drops a group with nothing in it, whether through an inner join or an aggregate with no outer join beneath it, decide whether that silence is a bug, and fix it with `LEFT JOIN LATERAL ... ON true`.

## Going further

- [7.2.1.5 LATERAL Subqueries](https://www.postgresql.org/docs/current/queries-table-expressions.html): the section this lesson compresses, including how a lateral item may refer to anything on the left-hand side of a join it sits on the right of
- [SELECT](https://www.postgresql.org/docs/current/sql-select.html): the complete syntax reference, including the full grammar of the `FROM` clause `LATERAL` belongs to
- [Appendix A. PostgreSQL Error Codes](https://www.postgresql.org/docs/current/errcodes-appendix.html): where SQLSTATE `42P01`, `undefined_table`, is catalogued
- [Beyond the basics](../reference/beyond-the-basics.md): the stage 3 reference sheet
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
