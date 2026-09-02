---
title: 26. Denormalising on Purpose
description: A second copy of a fact is a second chance to be wrong, unless the database is the one keeping it
type: lesson
---

# Lesson 26. Denormalising on Purpose

**Mission link:** A report that reads a live join or count on every request is a real cost, and the fix reached for first is a second copy of the answer kept closer to hand, so a senior engineer needs to know which copies stay honest on their own and which need watching.
**Primary source:** [PostgreSQL, 5.4 Generated Columns](https://www.postgresql.org/docs/current/ddl-generated-columns.html)
**Prerequisites:** [Lesson 21](0021-normalisation.md), [Lesson 24](0024-constraints-that-hold.md)

## Warm-up

1. ▢ Lesson 21's `UPDATE` against `country_name` reported 3 rows updated, correctly, and still left `GB` with two spellings, since the typo never matched the predicate. Given that, what would have to be true of a second copy of a fact for that drift to become impossible rather than merely unlikely?

<details markdown="1"><summary>Check</summary>

A single rule would have to run every time the source changes, so nobody can update one copy and leave the other behind. This lesson asks which mechanisms actually give you that rule: a database expression, a trigger, a scheduled refresh, or nothing at all, because the value turns out to be a different fact rather than a copy of one.

</details>

## Know this

### Generated columns, the case where it cannot go wrong

A generated column puts a second copy of a fact back into a schema with the database doing the writing, not a person running `UPDATE`.

```sql
CREATE TABLE design.line_items (
    price numeric(12,2),
    qty   int,
    total numeric(12,2) GENERATED ALWAYS AS (price * qty) STORED
);

INSERT INTO design.line_items (price, qty) VALUES (2.50, 4);
```

`total` reads 10.00, computed from the two columns beside it. Writing to it directly fails before the row is even touched:

```sql
UPDATE design.line_items SET total = 999;
```

`ERROR: column "total" can only be updated to DEFAULT`, `DETAIL: Column "total" is a generated column.`, SQLSTATE `428C9`. There is only one place `total` can come from, so it cannot disagree with `price * qty`.

On PostgreSQL 18, a generated column written with neither `STORED` nor `VIRTUAL` defaults to `VIRTUAL`, computed on read; `total` above stores its value only because `STORED` was written out. `pg_attribute.attgenerated` tells the two apart:

```sql
CREATE TABLE design.gen_demo (
    a int,
    b int,
    virt int GENERATED ALWAYS AS (a + b),
    stor int GENERATED ALWAYS AS (a + b) STORED
);

SELECT attname, attgenerated FROM pg_attribute
WHERE attrelid = 'design.gen_demo'::regclass AND attnum > 0
ORDER BY attnum;
```

`virt` reports `v`, `stor` reports `s`. On PostgreSQL 12 to 17, `STORED` was the only kind and required, so an undecorated column means something different on 18 than on 17. The trade is when the arithmetic runs: a stored column pays once, at write; a virtual one pays again on every read. Which side wins, and by how much, is stage 6's question.

The sharper limit: the expression sees only its own row.

```sql
ALTER TABLE design.parent ADD COLUMN kid_count int GENERATED ALWAYS AS (
    (SELECT count(*) FROM design.child WHERE child.parent_id = parent.id)
) STORED;
```

`ERROR: cannot use subquery in column generation expression`, SQLSTATE `0A000`. A count of child rows needs another table, and a generated column's guarantee rests on never looking outside its own.

### A redundant column, maintained by a trigger, and its honest cost

The value a generated column cannot reach, a count of rows in another table, is what a trigger is reached for instead. Keep it to the smallest trigger that does the job; writing one well is not this lesson's subject.

```sql
CREATE TABLE design.parent (
    id bigint PRIMARY KEY,
    child_count int NOT NULL DEFAULT 0 CHECK (child_count >= 0)
);

CREATE TABLE design.child (
    id bigint PRIMARY KEY,
    parent_id bigint REFERENCES design.parent(id)
);

CREATE FUNCTION design.trg_child_count() RETURNS trigger AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE design.parent SET child_count = child_count + 1 WHERE id = NEW.parent_id;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE design.parent SET child_count = child_count - 1 WHERE id = OLD.parent_id;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER child_count_trg
AFTER INSERT OR DELETE ON design.child
FOR EACH ROW EXECUTE FUNCTION design.trg_child_count();
```

Two inserts and one delete give `child_count` 1, then 2, then 1, just as trustworthy as a generated column, so far. The difference shows the moment something touches the column directly:

```sql
UPDATE design.parent SET child_count = 99 WHERE id = 1;
```

That succeeds, because nothing connects `child_count` to the rows it counts, only a trigger on `child`'s own writes. The `CHECK` already there does not help: it rejects `-1` with SQLSTATE `23514`, since a count cannot be negative, but accepts 99 without complaint. A `CHECK` bounds a value; it cannot verify that value is what the rows underneath add up to.

That gap is the honest cost: a denormalised column is a claim nothing audits. What it needs is a query that recomputes the real answer and compares it against the stored one.

```sql
SELECT p.id, p.child_count AS stored, count(c.id) AS actual
FROM design.parent p
LEFT JOIN design.child c ON c.parent_id = p.id
GROUP BY p.id, p.child_count
HAVING p.child_count <> count(c.id);
```

Against the corrupted row this returns one, `stored` 99 against `actual` 1; fixed, or on a parent with no children at all, it returns nothing. The query is a smoke detector, not a fix, and a schema without one is choosing not to know when the column is lying.

### The materialised view

A materialised view is a query's result kept as if it were a table, rather than recomputed on every read the way an ordinary view is; `pg_class.relkind` marks the difference, `m` against `r`.

```sql
CREATE MATERIALIZED VIEW design.mv_customer_orders AS
SELECT customer_id, count(*) AS n_orders
FROM orders
GROUP BY customer_id;
```

Seven rows, one per customer, covering all twelve orders. Built `WITH NO DATA`, the view exists but holds nothing, and reading it fails outright:

```sql
CREATE MATERIALIZED VIEW design.mv_nodata AS
SELECT customer_id, count(*) AS n_orders FROM orders GROUP BY customer_id
WITH NO DATA;

SELECT * FROM design.mv_nodata;
```

`ERROR: materialized view "mv_nodata" has not been populated`, `HINT: Use the REFRESH MATERIALIZED VIEW command.`, SQLSTATE `55000`. `REFRESH MATERIALIZED VIEW` populates it. `REFRESH ... CONCURRENTLY`, which lets readers keep the old contents while the new ones compute, asks for more: it refuses on `mv_customer_orders` with the same `55000` but `HINT: Create a unique index with no WHERE clause on one or more columns of the materialized view.`, succeeding only once such an index exists.

What makes this a schema decision, not a performance trick, is what happens between refreshes: until the next `REFRESH`, the view is wrong, and nothing about querying it says so. Whether that staleness is acceptable is stage 6's question; making it visible is this lesson's, and one way is a companion row recording the last refresh:

```sql
CREATE TABLE design.mv_refresh_log (
    view_name text PRIMARY KEY,
    refreshed_at timestamptz NOT NULL
);

INSERT INTO design.mv_refresh_log (view_name, refreshed_at)
VALUES ('mv_customer_orders', now())
ON CONFLICT (view_name) DO UPDATE SET refreshed_at = excluded.refreshed_at;
```

A reader now has somewhere to check the view's age, rather than trusting a refresh job ran on schedule.

### The one duplicated column this lesson endorses

Every case so far copies a fact that lives elsewhere, and every one needs a way to keep the copy honest. One shape looks identical on the page and needs none of that machinery, because it is not a copy of the same fact at all.

```sql
CREATE TABLE design.products (
    sku text PRIMARY KEY,
    current_price numeric(12,2) NOT NULL
);

CREATE TABLE design.order_lines (
    order_id bigint,
    sku text REFERENCES design.products(sku),
    price_at_sale numeric(12,2) NOT NULL,
    qty int NOT NULL,
    PRIMARY KEY (order_id, sku)
);

INSERT INTO design.products (sku, current_price) VALUES ('A1', 20.00);
INSERT INTO design.order_lines (order_id, sku, price_at_sale, qty) VALUES (1, 'A1', 20.00, 2);
UPDATE design.products SET current_price = 25.00 WHERE sku = 'A1';
```

Order 1 shows `price_at_sale` 20.00 next to `current_price` 25.00, both correct at once. The order sold at 20.00; the product now costs 25.00; totalling that order's revenue at `current_price` instead would say 50.00 for a sale that actually brought in 40.00, backdating a price rise onto a transaction that predates it. The two columns never had to agree, so there is no drift to detect and no trigger to write, since `price_at_sale` never claimed to be `current_price`, only to record what the price was at a moment already past. Naming it `price_at_sale` rather than `price` is the whole argument: once a column names a different fact, a snapshot rather than a live mirror, it stops being denormalisation at all, since normalisation only forbade two rows disagreeing about one fact, not two columns holding similar-looking numbers.

### How to decide

Four questions cover every case above.

Who recomputes it: a generated column, on every write or read; a trigger, only for writes to the table it watches; a materialised view, nobody, until something runs `REFRESH`; a snapshot column like `price_at_sale`, nobody, ever.

What happens if it is wrong: a generated column cannot be wrong without the row itself being wrong. A trigger-maintained column can go wrong silently, as `child_count` did at 99, and its `CHECK` only bounds a plausible range, not the truth. A materialised view is wrong by exactly what changed since the last refresh. A snapshot column is never wrong on its own terms, since its terms are the past.

How you would notice: the drift query, for a trigger-maintained column; the refresh log, or its absence, for a materialised view; nothing, for a generated column, which is the feature; whether the name is honest, for a snapshot column.

Whether the read it exists for is actually a problem yet: every case traded write-time simplicity for read-time convenience, or the reverse, and a column added before that trade-off is known to matter is a cost against a problem that might not exist. Confirming it does is stage 6's question.

## Practice

1. ▢ Predict whether `INSERT INTO design.line_items (price, qty, total) VALUES (3.00, 2, DEFAULT)` succeeds, and if so, what `total` becomes.

<details markdown="1"><summary>Check</summary>

It succeeds, giving `total` 6.00. PostgreSQL rejects any explicit value for a generated column except the keyword `DEFAULT`, which just asks it to compute the column the normal way.

</details>

2. ▢ `design.gen_demo` holds a row with `a` 1, `b` 2, so `virt` and `stor` both read 3. Predict what the two columns read after `UPDATE design.gen_demo SET a = 100 WHERE a = 1`, and say whether `virt` needed anything different from `stor` to reflect it.

<details markdown="1"><summary>Check</summary>

Both read 102. Changing `a` writes the row, so `stor` recomputes in the same instant `virt` would compute on its next read anyway; they differ only in timing, and which costs less is stage 6's question.

</details>

3. ▢ Predict whether the `AFTER INSERT` trigger on `design.child` ever runs for `INSERT INTO design.child (id, parent_id) VALUES (999, 42)`, given no row with `id = 42` in `design.parent`.

<details markdown="1"><summary>Hint</summary>

`design.child.parent_id` is declared `REFERENCES design.parent(id)`.

</details>

<details markdown="1"><summary>Check</summary>

No. The foreign key rejects the insert with SQLSTATE `23503` before any row is written, and an `AFTER` trigger only fires for a write that actually happened.

</details>

4. ▢ Predict what the drift-detection query from this lesson returns for a parent row with `child_count` 0 that has never had a matching row in `design.child`.

<details markdown="1"><summary>Check</summary>

Nothing. The `LEFT JOIN` gives zero matching child rows, so `count(c.id)` is 0, matching the stored 0; the query only surfaces a disagreement, and a parent with no children saying so is not lying.

</details>

5. ▢ Order 1 sold at `price_at_sale` 20.00 while `current_price` for the same `sku` has since risen to 25.00. Predict which of `sum(price_at_sale * qty)` and `sum(current_price * qty)` gives the wrong revenue for that order, and by how much.

<details markdown="1"><summary>Check</summary>

`sum(current_price * qty)` is wrong, giving 50.00 against the true 40.00. `current_price` answers what the product costs now, a question order 1 never asked; `price_at_sale` answers what the order actually paid, the only figure a revenue report can use.

</details>

6. ▢ Reading `design.mv_nodata` before its first refresh and refreshing `design.mv_customer_orders` `CONCURRENTLY` without a unique index both raise SQLSTATE `55000`. Predict whether their `HINT` text is the same.

<details markdown="1"><summary>Hint</summary>

One view has never been filled in; the other already has data and wants a specific kind of refresh.

</details>

<details markdown="1"><summary>Check</summary>

No. The unpopulated view's `HINT` says to run `REFRESH MATERIALIZED VIEW`; the concurrent refresh's says to create a unique index, since `CONCURRENTLY` needs a way to match old rows against new. The shared SQLSTATE only means the operation is not ready; the `HINT` is where they differ.

</details>

## Real-world reps

- [ ] Find a column at work updated by a trigger or a job rather than by the query that reads it, and check whether a drift query like this lesson's exists to catch it disagreeing with its source.
- [ ] Find a materialised view or a cache table at work and check how a reader would learn its age: a refresh timestamp, a job's last-run log, or nothing.
- [ ] Tomorrow: find a column at work named after a live value, such as `price` or `status`, that really answers a question about the past, and check whether it should be renamed the way `price_at_sale` is here.

## Going further

- [39.3. Materialized Views](https://www.postgresql.org/docs/current/rules-materializedviews.html): storage, refresh, and the unique index CONCURRENTLY needs
- [CREATE TABLE](https://www.postgresql.org/docs/current/sql-createtable.html): where GENERATED ALWAYS AS and its STORED and VIRTUAL forms are specified in full
- [37.1. Overview of Trigger Behavior](https://www.postgresql.org/docs/current/trigger-definition.html): what AFTER and BEFORE actually guarantee, for the one trigger used here
- [Appendix A. PostgreSQL Error Codes](https://www.postgresql.org/docs/current/errcodes-appendix.html): where SQLSTATE 55000 and 428C9 are catalogued
- [Schema design](../reference/schema-design.md): the stage 4 reference sheet
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
