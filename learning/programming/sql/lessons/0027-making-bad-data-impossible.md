---
title: 27. Making Bad Data Impossible
description: Take a schema that permits a wrong row and close every gap, then say what the design still cannot promise
type: lesson
---

# Lesson 27. Making Bad Data Impossible

**Mission link:** A schema review that only reads the DDL and feels uneasy has found nothing; the useful version names the exact row a colleague will insert next quarter and shows the schema takes it without complaint. This lesson runs that review once, against one schema built to fail every way the last six lessons taught, then closes every gap and says what closing them still does not buy.
**Primary source:** [PostgreSQL, 5.5 Constraints](https://www.postgresql.org/docs/current/ddl-constraints.html)
**Prerequisites:** [Lesson 24](0024-constraints-that-hold.md), [Lesson 26](0026-denormalising-on-purpose.md)

## Warm-up

1. ▢ Lesson 24 established that a `CHECK` is violated only when its condition evaluates to false, and that a `NULL` argument makes most conditions unknown rather than false, so an absent value passes a rule written about the present one. Given that, what has to be true of a column before its `CHECK` can be trusted to have ruled anything out?

<details markdown="1"><summary>Check</summary>

The column has to be `NOT NULL` first, or the `CHECK` has to name the absent case itself, `IS NULL OR ...`. Otherwise a review that reads the `CHECK` and concludes the column is safe is trusting a rule that a merely missing value already satisfies without the condition ever running against it.

</details>

## Know this

### One schema, every gap the stage taught

A booking system for subscriptions, three tables, built the way a first pass usually is: a plan's details typed straight onto the subscription, a customer named by the value on their business card, and nothing joining anything a busy afternoon left out.

```sql
CREATE SCHEMA design;

CREATE TABLE design.customers (
    email text PRIMARY KEY,
    name  text
);

CREATE TABLE design.subscriptions (
    id             bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_email text NOT NULL,
    plan_code      text,
    plan_name      text,
    plan_price     numeric(12,2),
    status         text,
    tags           text
);

CREATE TABLE design.invoices (
    id              bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    subscription_id bigint REFERENCES design.subscriptions (id),
    invoice_number  text,
    amount          numeric(12,2) CHECK (amount >= 0),
    customer_name   text
);
```

Eight gaps, one apiece. `subscriptions.tags` packs a list into one column, a repeating group. `plan_code` determines `plan_name` and `plan_price`, a transitive dependency nothing enforces. `customers.email` is the primary key, a natural key the business can and does edit. `subscriptions.customer_email` names a customer with no `REFERENCES` at all. `invoices.amount` carries a `CHECK` that, per the warm-up, an absent value satisfies. `subscriptions.status` is nullable with no reason to be. `invoices.invoice_number` is a candidate key with no `UNIQUE`. `invoices.customer_name` copies a fact `customers.name` already holds, with nothing keeping the two equal. Two customers and one subscription seed it:

```sql
INSERT INTO design.customers (email, name) VALUES
    ('ada@example.com', 'Ada'), ('grace@example.com', 'Grace');
INSERT INTO design.subscriptions (customer_email, plan_code, plan_name, plan_price, status, tags) VALUES
    ('ada@example.com', 'pro', 'Pro', 20.00, 'active', 'trial,priority');
INSERT INTO design.invoices (subscription_id, invoice_number, amount, customer_name) VALUES
    (1, 'INV-1000', 20.00, 'Ada');
```

### Eight rows the schema should never have accepted

Each of the following is a couple of lines against the schema above, and each succeeds: naming the row that gets in and running the insert is the review, not reading the DDL and feeling uneasy about it.

`industrial` shares no meaning with `trial`, only three letters in a row:

```sql
INSERT INTO design.subscriptions (customer_email, plan_code, plan_name, plan_price, status, tags)
  VALUES ('grace@example.com', 'free', 'Free', 0.00, 'active', 'industrial');
SELECT id, tags FROM design.subscriptions WHERE tags LIKE '%trial%';
-- ids 1 and 2, the second one wrongly, exactly lesson 21's doohickey again
```

A second `'pro'` row disagrees with the first about what `'pro'` costs, and both stand:

```sql
INSERT INTO design.subscriptions (customer_email, plan_code, plan_name, plan_price, status, tags)
  VALUES ('grace@example.com', 'pro', 'PRO', 25.00, 'active', NULL);
-- accepted; plan_code 'pro' now spans two plan_name and two plan_price values
```

Renaming the one column a subscription actually keys off breaks the link and says nothing:

```sql
UPDATE design.customers SET email = 'ada@newmail.com' WHERE email = 'ada@example.com';
SELECT s.id FROM design.subscriptions s LEFT JOIN design.customers c ON c.email = s.customer_email WHERE c.email IS NULL;
-- subscription 1, orphaned by the rename, silently
```

`'ghost@example.com'` never existed:

```sql
INSERT INTO design.subscriptions (customer_email, plan_code, plan_name, plan_price, status, tags)
  VALUES ('ghost@example.com', 'free', 'Free', 0.00, 'active', NULL);
-- accepted; no customer named that address, ever
```

An invoice with no amount at all, because `NULL >= 0` is unknown, not false:

```sql
INSERT INTO design.invoices (subscription_id, invoice_number, amount, customer_name)
  VALUES (1, 'INV-1001', NULL, 'Ada');
-- accepted
```

A subscription with no status:

```sql
INSERT INTO design.subscriptions (customer_email, plan_code, plan_name, plan_price, status, tags)
  VALUES ('grace@example.com', 'pro', 'Pro', 20.00, NULL, NULL);
-- accepted
```

The same invoice number, twice:

```sql
INSERT INTO design.invoices (subscription_id, invoice_number, amount, customer_name)
  VALUES (1, 'INV-1000', 20.00, 'Ada');
SELECT invoice_number, count(*) FROM design.invoices GROUP BY invoice_number HAVING count(*) > 1;
-- INV-1000, count 2
```

And a bill that names a customer by a spelling that never matched the row it billed:

```sql
INSERT INTO design.invoices (subscription_id, invoice_number, amount, customer_name)
  VALUES (2, 'INV-1002', 20.00, 'A. Smith');
-- accepted, against a customer actually named Grace
```

### The fixed schema, and every wrong row re-run

One rewrite, six mechanisms already taught.

```sql
CREATE TABLE design.customers (
    id    bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    email text NOT NULL UNIQUE,
    name  text
);

CREATE TABLE design.plans (
    plan_code  text PRIMARY KEY,
    plan_name  text NOT NULL,
    plan_price numeric(12,2) NOT NULL
);

CREATE TABLE design.subscriptions (
    id          bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_id bigint NOT NULL REFERENCES design.customers (id) ON DELETE RESTRICT,
    plan_code   text NOT NULL REFERENCES design.plans (plan_code),
    status      text NOT NULL CHECK (status IN ('active', 'trial', 'cancelled'))
);

CREATE TABLE design.subscription_tags (
    subscription_id bigint REFERENCES design.subscriptions (id),
    tag              text,
    PRIMARY KEY (subscription_id, tag)
);

CREATE TABLE design.invoices (
    id              bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    subscription_id bigint NOT NULL REFERENCES design.subscriptions (id),
    invoice_number  text NOT NULL UNIQUE,
    amount          numeric(12,2) NOT NULL CHECK (amount >= 0),
    customer_name   text
);
```

`subscription_tags` and `plans` are lesson 21's normalisation, splitting the repeating group and the transitive dependency into a table each. `customers.id` is lesson 22's chosen key, a surrogate the business never edits, with `email` kept as a `UNIQUE` candidate key rather than the primary one. `subscriptions.customer_id` is lesson 23's foreign key, declared `ON DELETE RESTRICT`. `status` and `amount` pair a `CHECK` with `NOT NULL`, lesson 24's fix for a condition an absent value used to satisfy. `invoices.invoice_number` gets the `UNIQUE` its candidate key never had. `customer_name` stays, since lesson 26 says a second copy can be kept on purpose; what it lacked was anything checking the copy, and a generated column cannot, since it only ever computes from its own row, and this fact lives two tables away. An audit query does the job instead:

```sql
SELECT i.id FROM design.invoices i
  JOIN design.subscriptions su ON su.id = i.subscription_id
  JOIN design.customers c ON c.id = su.customer_id
 WHERE i.customer_name IS DISTINCT FROM c.name;
```

Every one of the eight rows above, run again:

```sql
SELECT DISTINCT subscription_id FROM design.subscription_tags WHERE tag = 'trial';
-- 1 only; 'industrial' is a different row entirely, not a substring match
INSERT INTO design.plans (plan_code, plan_name, plan_price) VALUES ('pro', 'PRO', 25.00);
-- ERROR: duplicate key value violates unique constraint "plans_pkey", SQLSTATE 23505
UPDATE design.customers SET email = 'ada@newmail.com' WHERE id = 1;
-- succeeds and touches nothing else; subscriptions never named the email at all
INSERT INTO design.subscriptions (customer_id, plan_code, status) VALUES (999, 'free', 'active');
-- ERROR: insert or update on table "subscriptions" violates foreign key constraint "subscriptions_customer_id_fkey", SQLSTATE 23503
INSERT INTO design.invoices (subscription_id, invoice_number, amount, customer_name) VALUES (1, 'INV-2001', NULL, 'Ada');
-- ERROR: null value in column "amount" of relation "invoices" violates not-null constraint, SQLSTATE 23502
INSERT INTO design.subscriptions (customer_id, plan_code, status) VALUES (2, 'pro', NULL);
-- ERROR: null value in column "status" of relation "subscriptions" violates not-null constraint, SQLSTATE 23502
INSERT INTO design.invoices (subscription_id, invoice_number, amount, customer_name) VALUES (1, 'INV-1000', 20.00, 'Ada');
-- ERROR: duplicate key value violates unique constraint "invoices_invoice_number_key", SQLSTATE 23505
INSERT INTO design.invoices (subscription_id, invoice_number, amount, customer_name) VALUES (2, 'INV-2002', 0.00, 'A. Smith');
-- succeeds; nothing at insert time compares customer_name against customers.name, only the audit query above catches it afterward
```

Six fail with a named SQLSTATE, and two still succeed on purpose: the tag search, corrected by structure rather than a firing rule, and the invoice name, which no constraint here was ever going to catch, only a query run on a schedule.

### What the fixed schema still cannot promise

Every one of those six mechanisms looks at one row, or one table checked against one other value, at one moment. One thing to hold lightly before the two shapes below: every guarantee in this lesson is the engine's rather than the schema's, so the same `CREATE TABLE` enforces less on an engine with weaker typing, which lesson 46 demonstrates by running this stage's own guarantees against SQLite. Two shapes of rule fall outside that reach. A rule spanning two tables at once is the customer name case exactly: nothing at the instant of the `INSERT` compared `invoices.customer_name` to `customers.name`, because a `CHECK` never sees a second table and an audit query only runs when asked. A rule that has to hold as several statements happen over time, a subscription that must never go from `cancelled` back to `active`, is the same limit from a different angle: a `CHECK` re-evaluates the new row in isolation each time, with no memory of the row's own history, and stage 5's transactions are what let several statements be reasoned about together rather than one at a time. Neither gap is a defect here; both are the edge of what a row-level constraint was built to check. A third kind of rule sits outside constraints altogether: who is allowed to write which row is a question about the writer, not the row, and it is outside this arc.

### The review, as a procedure

Run in this order, each question one this schema just answered in practice, not advice offered in the abstract. What does one row of this table mean, and does the key say so: a subscription named its customer by an email address, a value someone edits, and the rename above broke the link the moment it ran. Which column can be absent, and what does absent mean there: `status` and `amount` could both be `NULL`, and neither absence meant anything, which is exactly what `NOT NULL` paired with the `CHECK` was for. Which rule is written in a comment or in application code rather than in the schema: `customer_email` pointed nowhere in particular until a `REFERENCES` clause said it had to point somewhere real. Which fact appears twice, and who keeps the copies equal: `plan_name` and `plan_price` disagreed the moment a second `'pro'` row was inserted, and `customer_name` disagreed the moment a customer's own row moved on without it, one closed by splitting the fact out, the other by a query that watches the copy rather than trusting it. Last, the question that is the whole stage at once: what would this schema accept today that the domain forbids. Every gap above answers it, found by trying the insert rather than reading the column list and guessing. A schema never asked this question on purpose has not been reviewed, whatever else has been done to it.

### What the stage bought

Lesson 21's normalisation removes the row that could disagree with itself, by giving every fact one home. Lesson 22's key choice trades a rename touching every referencing table for an identifier that never has to move. Lesson 23's foreign key promises a referenced row exists, nothing about whether it is the right one. Lesson 24's `CHECK` needs `NOT NULL` beside it because a condition merely not false still passes, and absence is not false. Lesson 25's type refuses a value outside a closed set before a row is ever built from it. Lesson 26 says a second copy is safe exactly when something, a generated column or an audit query, is watching it. None of these six mechanisms sees more than one row, or one table against one other, at one instant; what happens when two writes race against that same row at once is what the next stage is for.

## Practice

1. ▢ The fixed `subscription_tags` table holds `(1, 'trial')` already. Predict the exact error and SQLSTATE of inserting `(1, 'trial')` again.

<details markdown="1"><summary>Check</summary>

`ERROR: duplicate key value violates unique constraint "subscription_tags_pkey"`, `DETAIL: Key (subscription_id, tag)=(1, trial) already exists.`, SQLSTATE `23505`. The key is the pair, and normalising the tags added only the rule that one subscription never lists the same tag twice.

</details>

2. ▢ Predict whether the fixed `plans` table stops a second plan, a different `plan_code` such as `'pro-annual'`, from also being named `'Pro'`.

<details markdown="1"><summary>Hint</summary>

The transitive dependency this table closed ran from `plan_code` to `plan_name`, not the other way round.

</details>

<details markdown="1"><summary>Check</summary>

It does not, and the insert succeeds. Splitting the dependency out enforces that one `plan_code` names exactly one `plan_name`, never the reverse; two plans sharing a display name is not the anomaly lesson 21 closed.

</details>

3. ▢ Predict the exact error and SQLSTATE of inserting into the fixed `invoices` table with `subscription_id = 999`, a value no subscription has.

<details markdown="1"><summary>Check</summary>

`ERROR: insert or update on table "invoices" violates foreign key constraint "invoices_subscription_id_fkey"`, `DETAIL: Key (subscription_id)=(999) is not present in table "subscriptions".`, SQLSTATE `23503`. The rule that stopped a subscription naming a nonexistent customer stops an invoice the same way.

</details>

4. ▢ Predict what `DELETE FROM design.plans WHERE plan_code = 'free'` does while a subscription still uses that code, given that `subscriptions.plan_code` was declared `REFERENCES design.plans (plan_code)` with no `ON DELETE` clause at all.

<details markdown="1"><summary>Hint</summary>

A bare `REFERENCES` with no `ON DELETE` clause still chose one.

</details>

<details markdown="1"><summary>Check</summary>

It fails: `ERROR: update or delete on table "plans" violates foreign key constraint "subscriptions_plan_code_fkey" on table "subscriptions"`, `DETAIL: Key (plan_code)=(free) is still referenced from table "subscriptions".`, SQLSTATE `23503`. An unwritten `ON DELETE` is `NO ACTION`, lesson 23's strictest default, and it refuses just as a written `RESTRICT` would, only under the ordinary foreign key SQLSTATE rather than `23001`.

</details>

5. ▢ Invoice 1 recorded `customer_name = 'Ada'` when it was written. Predict what the audit query in this lesson finds after `UPDATE design.customers SET name = 'Ada Lovelace' WHERE id = 1`, and say what that reveals about the audit query itself.

<details markdown="1"><summary>Check</summary>

It now flags invoice 1 too, `customer_name` reading `'Ada'` against a current name of `'Ada Lovelace'`. That is the audit query's own limit: it compares a copy against the row's current state, not the state when the copy was written, so a customer who legitimately renames themselves after a bill exists looks exactly like the mismatch the query was built to catch.

</details>

6. ▢ Predict whether `ON DELETE RESTRICT` on `subscriptions.customer_id` blocks deleting a customer who has never had a subscription at all.

<details markdown="1"><summary>Check</summary>

No, the delete succeeds. `RESTRICT` only refuses when a row in `subscriptions` actually names the customer being deleted; a customer with zero matching rows gives the constraint nothing to object to.

</details>

## Real-world reps

- [ ] Take a table you did not design and run this lesson's procedure against it in order, writing down which of the five questions the table fails first.
- [ ] Find a column in a schema you maintain that copies a fact another table already holds, and check whether anything, a generated column, a trigger, or a query someone actually runs, keeps the two equal.
- [ ] Tomorrow: pick one foreign key in a schema you own and try to state, from the column definition alone, which `ON DELETE` action it has; then check, because a bare `REFERENCES` still made a choice.

## Going further

- [5.5 Constraints](https://www.postgresql.org/docs/current/ddl-constraints.html): the full chapter behind every mechanism this lesson only re-applied
- [Appendix A. PostgreSQL Error Codes](https://www.postgresql.org/docs/current/errcodes-appendix.html): where every SQLSTATE quoted above is catalogued
- [5.5.5 Foreign Keys](https://www.postgresql.org/docs/current/ddl-constraints.html#DDL-CONSTRAINTS-FK): `ON DELETE` and `ON UPDATE` actions, lesson 23's subject, referenced rather than retaught here
- [Schema design](../reference/schema-design.md): the stage 4 reference sheet
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
