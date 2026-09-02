---
title: 47. Reading What an ORM Emits
description: The ORM writes the SQL you did not write, and the only way to know what it sent is to look
type: lesson
---

# Lesson 47. Reading What an ORM Emits

**Mission link:** A review of a pull request that touches `customer.orders` cannot say whether that line is safe until something tells it how many statements the line actually sends, because the call site alone never says.
**Primary source:** [PostgreSQL, 14.1 Using EXPLAIN](https://www.postgresql.org/docs/current/using-explain.html)
**Prerequisites:** [Lesson 11](0011-subqueries.md), [Lesson 44](0044-reviewing-a-query.md)

## Warm-up

1. ▢ Lesson 11 showed a correlated subquery, naming the outer query's tables and running once per outer row. Application code fetches five customers, then loops over them asking for each one's orders one call at a time. Which subquery shape does that resemble, and what does it lack?

<details markdown="1"><summary>Check</summary>

A correlated subquery: an inner fetch depending on a value the outer step produced, repeated once per row. What it lacks is the nesting: a correlated subquery is one statement the planner sees whole, while the loop is two round trips repeated per row, invisible to the database. That gap is this lesson's subject.

</details>

## Know this

### The statement nobody wrote

Once an ORM sits between the source file and the database, the SQL reaching the server is not the SQL in the source: `customer.orders` compiles into a statement the code never spells out, and the only source of truth for what ran is a client saying so. Every skill this arc built from stage 2 onward applies just as much to a statement an ORM wrote as one a person typed, because the database cannot tell the difference. Reading the call site in a diff is not enough, since a review needs a statement count and a shape, either of which can turn one intended read into five hundred without showing in the line that produced them. Which loader method was named is the library's own style, documented by the library, not what this lesson checks; it does not teach SQLAlchemy or any ORM as a subject, only how to read what one sent.

### Turning statement logging on, and where else the same text lives

Every ORM has a switch that does this job under a different name; SQLAlchemy's is a keyword on the engine itself.

```python
engine = create_engine(url, echo=True)
```

That line is documented as equivalent to attaching a handler to a logger named `sqlalchemy.engine` set to `INFO`, the form used to capture every statement quoted below. The same text lives in two further places untouched by the application. The server's own log records a statement the moment it arrives, whatever client sent it, once `log_statement` is set to log it there, seeing an ORM's SQL exactly as hand-written SQL, since the two are indistinguishable by then. The plan is the second place: `auto_explain`, loaded for one session with `LOAD 'auto_explain';` and its minimum duration set to zero, writes the plan for every statement that session runs, without the restart `pg_stat_statements` needs, the per-statement view lesson 41 already showed cannot be switched on for a session that only just thought to ask.

### The N+1, arriving from application code

Fetching five customers, then touching each one's orders, emits six statements: one for the customers, five more, one per customer, differing only in which id they ask for.

```text
SELECT customers.id, customers.email, customers.country FROM customers WHERE customers.country = %s::VARCHAR LIMIT %s::INTEGER
SELECT orders.id AS orders_id, orders.customer_id AS orders_customer_id, orders.amount AS orders_amount FROM orders WHERE %s::INTEGER = orders.customer_id
```

The second line is one of five, identical to the other four apart from the bound parameter, which the log marks only with a placeholder. Eight lines were logged, but two are `BEGIN` and `ROLLBACK`, bookkeeping any transactional client performs regardless of the ORM, leaving the six that matter: one `SELECT` against `customers`, five against `orders`. Six was only true because the test asked for five customers; ask for five hundred and the same code emits five hundred and one. The tell is N identical statements beside the single statement that produced N, whatever N happens to be in production.

### Two fixes, and what each one pays

SQLAlchemy's name for loading a relationship up front rather than one row at a time is `selectinload`; every ORM has an equivalent eager-loading option under its own name. The same five customers and their orders, loaded this way, emit two statements instead of six.

```text
SELECT customers.id, customers.email, customers.country FROM customers WHERE customers.country = %s::VARCHAR LIMIT %s::INTEGER
SELECT orders.customer_id AS orders_customer_id, orders.id AS orders_id, orders.amount AS orders_amount FROM orders WHERE orders.customer_id IN (%s::INTEGER, %s::INTEGER, %s::INTEGER, %s::INTEGER, %s::INTEGER)
```

The second statement carries one bound parameter per customer returned, so the `IN` list grows with the page size, but the statement count stays at two, whether five customers came back or five hundred. The other fix, `joinedload`, asks the database to do the join itself, costing the opposite trade: one statement instead of two.

```text
SELECT anon_1.id, anon_1.email, anon_1.country, orders_1.id AS id_1, orders_1.customer_id, orders_1.amount FROM (SELECT customers.id AS id, customers.email AS email, customers.country AS country FROM customers WHERE customers.country = %s::VARCHAR LIMIT %s::INTEGER) AS anon_1 LEFT OUTER JOIN orders AS orders_1 ON anon_1.id = orders_1.customer_id
```

A `LEFT OUTER JOIN` against the "many" side repeats the "one" side's row once per match, the fan-out lesson 9 named when a join multiplied a total: a customer with three orders comes back as three rows repeating the same customer columns, so the application must deduplicate, work `.unique()` did here. The `IN`-list form is the one to reach for first, since its statement count is fixed at two regardless of fan-out, while the join's row count is as unpredictable as the data behind it.

### Counting, sorting, filtering and paginating in the wrong place

Loading every matching order to ask Python for its length emits a `SELECT` of every column, then discards it all for one integer.

```text
SELECT orders.id, orders.customer_id, orders.amount FROM orders WHERE orders.customer_id = %s::INTEGER
```

Asking the database for the same integer emits a different statement and returns the same answer without the detour.

```text
SELECT count(*) AS count_1 FROM orders WHERE orders.customer_id = %s::INTEGER
```

Both runs above answered seven for the same customer; the difference is that one sent every column of every row before discarding it, and the other sent one number. The same mistake generalises three ways. Sorting in the application sends every row unordered before Python re-orders what an index-backed `ORDER BY` could have handed back sorted already. Filtering in the application still sends rows a `WHERE` clause would have excluded, paying transfer and CPU before discarding them. Paginating with `.limit().offset()` compiles straight to `LIMIT` and `OFFSET`, confirmed by compiling that call directly, so the database still reads and discards every skipped row on the way to the page asked for, the cost lesson 40 measured growing with how far a reader pages.

### What the ORM gets right, and the question worth carrying into review

A lesson that only complains about generated SQL has missed what it is usually right about. Every statement captured above bound its values as parameters rather than splicing them into the text, visible as the `%s` placeholder sitting where the country code or customer id belongs, the one thing hand-written SQL gets wrong often enough to matter, since a string built by concatenation trusts whatever arrived in the value. The ORM also maps every returned row into an object the application already knows how to use, the whole reason anyone reached for one, and the plain statements above are usually what a person would have written by hand anyway; it becomes a review question only once a relationship access turns one call into N, a join turns one row into several, or a count turns into a length. For any ORM call in a diff, ask how many statements it emits and what shape they are, and capture them to find out, since reading the call site cannot tell you.

## Practice

1. ▢ A diff adds a loop fetching twenty customers, then reads `customer.orders` on each, with no loader option set. Predict the statement count and shape a capture would show.

<details markdown="1"><summary>Check</summary>

Twenty-one statements: one for the customers, twenty against `orders`, identical apart from the bound id, the N+1 signature.

</details>

2. ▢ The same code switches to a join-based eager load instead. A colleague asks whether `len()` on the result still counts customers correctly, given one can have several orders.

<details markdown="1"><summary>Hint</summary>

A `LEFT OUTER JOIN` repeats the row on the "one" side once for every match on the "many" side.

</details>

<details markdown="1"><summary>Check</summary>

No, not without deduplicating first. A customer with three orders arrives as three rows, so raw `len()` overcounts by exactly lesson 9's fan-out; only `len()` after deduplication, as `.unique()` does here, is trustworthy.

</details>

3. ▢ Predict the statement count of the N+1, `IN`-list and join forms as the customers fetched grow from five to five hundred.

<details markdown="1"><summary>Check</summary>

The N+1 form grows from six statements to five hundred and one. The `IN`-list form stays at two, with a longer parameter list. The join form stays at one, with more rows in it. The fixes are safe at scale precisely because their count does not move; the N+1 form's does.

</details>

4. ▢ A captured statement reads `WHERE customers.country = %s::VARCHAR`. A colleague proposes rebuilding it with string interpolation instead, "to make it simpler". Say in one sentence what that rewrite costs.

<details markdown="1"><summary>Check</summary>

It would drop the placeholder the ORM uses here, so a country value containing SQL rather than a plain code would be interpreted as part of the statement rather than as data, the exact bug binding every value as a parameter prevents.

</details>

5. ▢ Two ways answer "how many orders does this customer have": load the rows and take `len()`, or run `count(*)` in the database. Predict which gets worse as the rows involved widen, and whether that changes your choice.

<details markdown="1"><summary>Check</summary>

`len()` gets worse as rows widen, since it always sends every column of every matching row; `count(*)` sends one integer regardless. Row width changes the size of the gap, not the choice: `count(*)` is never the worse option.

</details>

6. ▢ A diff replaces `.limit(20)` with `.limit(20).offset(page * 20)`, called on page 500. Predict, from lesson 40, what a plan captured as the page number grows would show.

<details markdown="1"><summary>Hint</summary>

`OFFSET` does not skip rows for free; the database still has to read them to know they are the ones being skipped.

</details>

<details markdown="1"><summary>Check</summary>

The rows-scanned figure grows with the page number, since the database reads and discards every skipped row before returning the twenty asked for; page 500 costs proportionally more than page one for the same twenty rows, exactly what lesson 40 measured about `OFFSET`.

</details>

## Real-world reps

- [ ] Turn on statement logging, or your ORM's equivalent, for one endpoint you maintain, and count how many statements a single call emits.
- [ ] Find one place where a collection's length is taken after loading it fully, and check what a database-side count would emit instead.
- [ ] Tomorrow: pick one ORM call in a diff you review, ask how many statements it emits and what shape they are, and capture them rather than guessing.

## Going further

- [Configuring Logging](https://docs.sqlalchemy.org/en/20/core/engines.html#configuring-logging): the `echo` flag this lesson used
- [Relationship Loading Techniques](https://docs.sqlalchemy.org/en/20/orm/queryguide/relationships.html): every loader strategy this lesson named
- [19.8. Error Reporting and Logging](https://www.postgresql.org/docs/current/runtime-config-logging.html#GUC-LOG-STATEMENT): `log_statement`, this lesson's server-side alternative
- [F.3. auto_explain](https://www.postgresql.org/docs/current/auto-explain.html): the plan-logging module, loadable per session without a restart
- [Operating](../reference/operating.md): the stage 7 reference sheet
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
