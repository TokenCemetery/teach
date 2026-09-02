---
title: 21. Normalisation
description: Every normal form removes a way for two rows to disagree about the same fact
type: lesson
---

# Lesson 21. Normalisation

**Mission link:** A schema that lets two rows disagree about the same fact turns every report built on it into a coin flip that never shows up as an error, only as a wrong but plausible answer. Normal forms are the checklist for finding which table is still capable of that before a customer does.
**Primary source:** [PostgreSQL, 5.1 Table Basics](https://www.postgresql.org/docs/current/ddl-basics.html)
**Prerequisites:** [Lesson 6](0006-keys-and-constraints.md), [Lesson 9](0009-aggregation-and-group-by.md)

## Warm-up

1. ▢ Lesson 6 established that a key is a claim the database enforces, not a claim about the data being tidy. A table can store `country_code` next to `country_name` on every row with no key linking the two. Given that, what stops two rows from recording two different names for the same code?

<details markdown="1"><summary>Check</summary>

Nothing. `country_code` and `country_name` are just two columns filled in together most of the time, and the database has no claim to enforce when they drift apart. That gap is this lesson's whole subject.

</details>

## Know this

### Two rows, one fact

Build a signup table the way a pipeline usually does: one row per signup, every fact flattened onto it.

```sql
CREATE TABLE design.signups (
    country_code text,
    country_name text,
    plan         text,
    plan_price   numeric(12,2),
    email        text
);

INSERT INTO design.signups (country_code, country_name, plan, plan_price, email) VALUES
    ('GB', 'United Kingdom', 'pro',  20.00, 'ada@example.com'),
    ('GB', 'United Kingdom', 'free',  0.00, 'grace@example.com'),
    ('GB', 'United Kingdom', 'PRO',  25.00, 'alan@example.com'),
    ('GB', 'Untied Kingdom', 'pro',  20.00, 'katherine@example.com'),
    ('US', 'United States',  'free',  0.00, 'ada@example.com');
```

Three rows spell it `United Kingdom`, one spells it `Untied Kingdom`. Somebody fixes the typo the obvious way:

```sql
UPDATE design.signups SET country_name = 'United Kingdom of Great Britain'
WHERE country_code = 'GB' AND country_name = 'United Kingdom';
```

That reports 3 rows updated, correctly. `SELECT DISTINCT country_code, country_name FROM design.signups WHERE country_code = 'GB'` now returns two rows, `GB, United Kingdom of Great Britain` and `GB, Untied Kingdom`, because the typo never matched the predicate. Nobody ran a bad query, yet the table still holds two spellings of one country, and no later query can tell which is true. That is this lesson's thesis: a table that repeats a fact on more than one row lets the copies disagree, and normalisation makes that structurally impossible rather than merely unlikely.

The mess has a name for each direction it goes wrong in. An **update anomaly** is what just happened: a correction applied to every row matching a predicate misses a row that should have matched, because the fact was copied rather than stored once. An **insertion anomaly** shows going in: `GROUP BY email HAVING count(*) > 1` finds `ada@example.com` twice, because a second signup means retyping the same email, plan and country, a fresh chance to disagree with the first. A **deletion anomaly** takes an unrelated fact out with the row: only one signup here came from `US`, so `DELETE FROM design.signups WHERE country_code = 'US'` removes the only place recording that `US` means `United States`.

### First normal form

A different table, one column holding more than one fact:

```sql
CREATE TABLE design.products (
    name text,
    tags text
);

INSERT INTO design.products (name, tags) VALUES
    ('widget',    'red,small'),
    ('gizmo',     'blue'),
    ('gadget',    'red,large,fragile'),
    ('doohickey', 'infrared');
```

Asking for everything tagged red:

```sql
SELECT name FROM design.products WHERE tags LIKE '%red%';
```

Three rows come back, `doohickey`, `gadget` and `widget`, and the first is wrong: its tag is `infrared`, which merely contains the letters `r`, `e`, `d` in a row. A cleverer predicate only trades one problem for another: `WHERE 'red' = ANY (string_to_array(tags, ','))` returns the correct two, `gadget` and `widget`, a workaround for a column that never needed one. `CROSS JOIN LATERAL unnest(string_to_array(tags, ','))` shows what the table should have been, seven rows where the design has four: `doohickey, infrared`, `gadget, fragile`, `gadget, large`, `gadget, red`, `gizmo, blue`, `widget, red` and `widget, small`. First normal form asks for exactly that, one value per column per row: `red,small` fails it for the same reason `LIKE` cannot search it reliably, an unstated number of facts joined by a comma. The fix is a second table, one row per tag, which the `LATERAL` query already reconstructs.

### A functional dependency, stated plainly

The glossary already gave you the term: a functional dependency is one column's value determining another's. Stated as a query, `country_code` determines `country_name` when grouping by the first and counting the distinct second gives 1 every time, and not when it comes back higher.

```sql
SELECT country_code, count(DISTINCT country_name) FROM design.signups GROUP BY country_code;
```

Against the first table, `GB` groups to 2 distinct names, because the typo still sits there next to the fix. A separate `code, name` lookup has no such option: grouped by `code`, the count is 1 for every code, not because anyone was careful, but because the table has nowhere for a second name to go. Every normal form from here on forces exactly that shape onto a dependency a denormalised table only respects by convention.

### Second normal form

Second normal form is about a composite key, and a fact that only cares about part of it.

```sql
CREATE TABLE design.order_items (
    order_id        bigint,
    sku             text,
    sku_description text,
    qty             int,
    PRIMARY KEY (order_id, sku)
);

INSERT INTO design.order_items (order_id, sku, sku_description, qty) VALUES
    (1, 'A1', 'Red widget',   2),
    (2, 'A1', 'Red widget',   1),
    (3, 'B2', 'Blue widget',  5),
    (4, 'A1', 'Red widget, small', 3);
```

The key is `(order_id, sku)`, but `sku_description` depends on `sku` alone, and the table lets that partial dependency drift: `SELECT DISTINCT sku, sku_description FROM design.order_items WHERE sku = 'A1'` returns two rows, `Red widget` and `Red widget, small`, one product described two ways because the description was retyped on every line that sold it. The fix splits along the boundary the dependency already pointed at: the composite key stays for `qty`, which needs both columns, and `sku` alone becomes the key for the description.

```sql
CREATE TABLE design.order_lines (
    order_id bigint,
    sku      text REFERENCES design.skus (sku),
    qty      int,
    PRIMARY KEY (order_id, sku)
);

CREATE TABLE design.skus (
    sku             text PRIMARY KEY,
    sku_description text NOT NULL
);
```

Joining them back gives `Red widget` on every line that sells `A1`, because exactly one row now gets to say what `A1` means.

### Third normal form

Third normal form catches the same drift one step removed, through a column that is not part of the key at all.

```sql
CREATE TABLE design.employees (
    emp_id    bigint PRIMARY KEY,
    emp_name  text NOT NULL,
    dept_id   bigint NOT NULL,
    dept_name text NOT NULL,
    dept_head text NOT NULL
);

INSERT INTO design.employees (emp_id, emp_name, dept_id, dept_name, dept_head) VALUES
    (1, 'Ada',   10, 'Engineering', 'Grace'),
    (2, 'Alan',  10, 'Engineering', 'Grace'),
    (3, 'Kate',  20, 'Sales',       'Donald');
```

`dept_head` does not depend on `emp_id`, the key, it depends on `dept_id`, an ordinary attribute here, and that chain, key to `dept_id` to `dept_head`, is the transitive dependency. Promote Ada to head of Engineering and the update lands on her row alone:

```sql
UPDATE design.employees SET dept_head = 'Alan' WHERE emp_id = 1;
```

`SELECT dept_id, dept_head FROM design.employees WHERE dept_id = 10` now returns `Grace` and `Alan` for the same department, both correct according to the table and only one true. Splitting `dept_id, dept_name, dept_head` into its own table, keyed on `dept_id`, removes the row the update could have missed: department 10 now has exactly one row to change, so its head cannot be right for some employees and wrong for others.

### Boyce-Codd normal form, the boundary, and what a split costs

Boyce-Codd normal form catches one case third normal form waves through: a non-key column determining part of the key. A small school records which subject each student takes with which teacher, on the assumption that any one teacher only ever teaches one subject.

```sql
CREATE TABLE design.class_assignments (
    student text,
    subject text,
    teacher text,
    PRIMARY KEY (student, subject)
);

INSERT INTO design.class_assignments (student, subject, teacher) VALUES
    ('Alice', 'Math',    'Mr Smith'),
    ('Bob',   'Math',    'Mr Smith'),
    ('Alice', 'Science', 'Ms Jones'),
    ('Bob',   'English', 'Mr Lee');
```

The candidate keys are `(student, subject)` and `(student, teacher)`, and `subject` is part of one of them, so `teacher` determining `subject` lands on a column the table treats as prime, exactly why third normal form says nothing about it. `teacher` itself is not a candidate key, though, and Boyce-Codd normal form requires every determinant to be one. The anomaly that gap permits: updating only Alice's row to move Mr Smith onto Physics leaves him teaching Math for Bob and Physics for Alice at once, both true according to the table and impossible at the school it describes. Splitting `teacher` and `subject` onto their own table closes the gap: there is now exactly one row where `teacher` can be wrong.

```sql
CREATE TABLE design.teacher_subjects (
    teacher text PRIMARY KEY,
    subject text NOT NULL
);

CREATE TABLE design.enrolments (
    student text,
    teacher text REFERENCES design.teacher_subjects (teacher),
    PRIMARY KEY (student, teacher)
);
```

Fourth and fifth normal form exist past this point, named rather than taught here, because neither has a violation this lesson can produce on a schema built from tables a reader would recognise; both concern multi-valued facts interacting inside a single relation, in ways that need a deliberately contrived example to see at all. A schema is not finished just because a further normal form still has a name.

None of this is free. Lesson 7 already made a join routine, and every split above adds one more: a description that sat on the row is now one join away, and a report reading one table now reads two or three. That cost is the price of the guarantee, not a flaw in the method, and the next few lessons make a split like this safe to build on rather than merely tidy. Lesson 26 is where a redundant column occasionally goes back in on purpose.

## Practice

1. ▢ Predict what `SELECT country_code, count(DISTINCT country_name) FROM design.signups GROUP BY country_code` returns for `GB` before the `UPDATE` in this lesson's first table runs at all, and why it is not 1.

<details markdown="1"><summary>Check</summary>

Three of the four `GB` rows agree on `United Kingdom`, but the fourth spells it `Untied Kingdom`. `count(DISTINCT ...)` counts distinct spellings, not rows, so the result is 2.

</details>

2. ▢ `count(DISTINCT tags)` on the `products` table also breaks as a way of counting how many different tags exist. Predict whether it matches the number of distinct rows `unnest(string_to_array(tags, ','))` produces, and say why.

<details markdown="1"><summary>Hint</summary>

`red,small` and `red,large,fragile` are two different strings, and both contain `red`.

</details>

<details markdown="1"><summary>Check</summary>

No. `count(DISTINCT tags)` counts distinct whole strings, four, one per product, while unnesting produces one row per tag and lets `red` count once instead of twice. Only the second answers "how many distinct tags are there."

</details>

3. ▢ In `order_items`, predict the exact error and SQLSTATE of inserting a second row for `(1, 'A1')` with a different `qty`.

   ```sql
   INSERT INTO design.order_items (order_id, sku, sku_description, qty)
   VALUES (1, 'A1', 'Red widget', 9);
   ```

<details markdown="1"><summary>Check</summary>

The error is `ERROR: duplicate key value violates unique constraint`, with `DETAIL: Key (order_id, sku)=(1, A1) already exists.`, SQLSTATE `23505`. The key is `(order_id, sku)` together, and that pair already has a row, regardless of the new `qty` or `sku_description`.

</details>

4. ▢ After splitting `order_items` into `order_lines` and `skus`, predict what happens inserting into `order_lines` a row with `sku = 'C3'`, never seen in `skus`.

<details markdown="1"><summary>Hint</summary>

`order_lines.sku` was declared `REFERENCES design.skus (sku)`.

</details>

<details markdown="1"><summary>Check</summary>

The insert is rejected: a foreign key requires the value to already exist on the referenced side. The exact wording is lesson 23's subject; here it is enough that the split also stops an order line pointing at a product that does not exist.

</details>

5. ▢ Predict the row count and distinct `dept_head` values for `dept_id = 20` after `UPDATE design.employees SET dept_head = 'Someone Else' WHERE dept_id = 20`, given that department 20 only ever had one employee row.

<details markdown="1"><summary>Check</summary>

One row, one value, `Someone Else`. The anomaly needed a department with more than one row to reveal it; a single-row department can still record a wrong head, it just cannot record two different ones at once, so the anomaly is latent rather than absent.

</details>

6. ▢ In `class_assignments`, predict what `GROUP BY teacher HAVING count(DISTINCT subject) > 1` returns before the split, and say what a non-empty result would mean for the "one teacher, one subject" assumption the example rests on.

<details markdown="1"><summary>Check</summary>

Empty, here: every row for `Mr Smith` says `Math`, every row for `Ms Jones` says `Science`, and `Mr Lee` appears only once. A non-empty result would mean the assumption had already failed, some teacher genuinely teaching two subjects, and neither the anomaly shown nor its fix would still apply.

</details>

## Real-world reps

- [ ] Find a table at work with several non-key columns, and check whether any two travel together, one determining the other, the way `country_code` and `country_name` did here.
- [ ] Pick a table that stores a comma-separated list in one column, and write the `LATERAL` query that would turn it into the second table it is missing, without running it against production data.
- [ ] Tomorrow: find one place where the same fact, a name, a price, a status label, is copied onto more than one row, and check by hand whether any two copies disagree.

## Going further

- [Boyce-Codd normal form](https://en.wikipedia.org/wiki/Boyce%E2%80%93Codd_normal_form): the formal definition behind this lesson's demonstration
- [Fourth normal form](https://en.wikipedia.org/wiki/Fourth_normal_form): named here as a boundary this lesson does not teach
- [Fifth normal form](https://en.wikipedia.org/wiki/Fifth_normal_form): named alongside fourth normal form for the same reason
- [Schema design](../reference/schema-design.md): the stage 4 reference sheet
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
