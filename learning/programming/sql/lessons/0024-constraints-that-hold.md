---
title: 24. Constraints That Actually Hold
description: A CHECK fails only when its condition is false, so an absent value satisfies almost every rule you wrote
type: lesson
---

# Lesson 24. Constraints That Actually Hold

**Mission link:** A `CHECK` that reads as an obvious rule can still let the one row nobody tested straight through, and a senior engineer needs to spot that gap before a null-shaped bug ships as valid data.
**Primary source:** [PostgreSQL, 5.5 Constraints](https://www.postgresql.org/docs/current/ddl-constraints.html)
**Prerequisites:** [Lesson 3](0003-null-and-three-valued-logic.md), [Lesson 23](0023-foreign-keys.md)

## Warm-up

1. ▢ Lesson 3 established that a comparison involving `NULL` evaluates to unknown rather than to true or false, and that `WHERE` keeps a row only when its condition is true, discarding unknown exactly like false. What happens to a row whose `WHERE` condition evaluates to unknown?

<details markdown="1"><summary>Check</summary>

It is dropped, precisely as if the condition had evaluated to false. Unknown and false produce the same outcome in `WHERE`. Whether every other clause that evaluates a condition agrees with that is worth checking rather than assuming.

</details>

## Know this

### A `CHECK` fails only when its condition is false

A `CHECK` constraint is violated only when its condition evaluates to **false**. True passes, and so does unknown.

```sql
CREATE SCHEMA design;

CREATE TABLE design.c_demo (
    id     bigint PRIMARY KEY,
    amount numeric(12,2) CHECK (amount >= 0)
);
INSERT INTO design.c_demo VALUES (1, 10.00);  -- ok
INSERT INTO design.c_demo VALUES (2, -1);
```

```
ERROR:  new row for relation "c_demo" violates check constraint "c_demo_amount_check"
DETAIL:  Failing row contains (2, -1.00).
SQLSTATE: 23514
```

`-1` fails because `-1 >= 0` is false. Now the row the rule was apparently guarding against slips through:

```sql
INSERT INTO design.c_demo VALUES (3, NULL);  -- accepted
```

`NULL >= 0` is unknown, not false, so the constraint has nothing to object to, and a row with no amount passes as if it were "zero or more". The same shape appears with a closed list: `CHECK (tier IN ('free', 'pro'))` rejects `'gold'` with the identical `23514`, and accepts a `NULL` tier for the same reason, `tier IN (...)` over `NULL` is unknown. This is not a special rule about `CHECK`; it is lesson 3's rule arriving somewhere new: "not false" is a lower bar than "true", so any column that can be absent quietly claims an exemption from every rule written about its present value.

Two fixes answer different questions. `NOT NULL` closes the gap outright: with `tier text NOT NULL CHECK (tier IN ('free', 'pro'))`, inserting `NULL` fails with `ERROR: null value in column "tier" of relation "tier_fixed1" violates not-null constraint`, SQLSTATE `23502`, before the `CHECK` even runs. Naming the absent case in the condition leaves `NULL` legal but makes that a decision rather than an accident: `CHECK (tier IS NULL OR tier IN ('free', 'pro'))` still accepts `NULL` and still rejects `'gold'` with `23514`, now reading "no tier yet, or one of these" instead of quietly relying on it.

Reach for `NOT NULL` when the absence itself is the bug: an amount, a tier, anything that must exist for the row to mean anything. Reach for the explicit `IS NULL` branch only when "not yet known" is a real state the column may hold, and say so rather than leaning on unknown happening to pass.

### `NOT NULL`, the constraint that costs one word

`NOT NULL` is the cheapest constraint available and, row for row, removes the most possible states: no expression, just a value or an immediate failure. Most of what a `CHECK` seems to promise and fails to deliver, `NOT NULL` delivers by itself, which is why the previous section reached for it.

One place it does not reach: a column declared `NOT NULL` can still arrive as `NULL` in a query's result, once an outer join is involved.

```sql
CREATE TABLE design.plans (id bigint PRIMARY KEY, name text NOT NULL);
CREATE TABLE design.accounts (id bigint PRIMARY KEY, plan_id bigint REFERENCES design.plans (id));
INSERT INTO design.plans VALUES (1, 'starter');
INSERT INTO design.accounts VALUES (1, 1), (2, NULL);

SELECT a.id AS account_id, p.name AS plan_name
FROM design.accounts a LEFT JOIN design.plans p ON p.id = a.plan_id;
```

Account 2 comes back with `plan_name` equal to `NULL`, even though `plans.name` has never held one. Lesson 8 already explained why: a left join manufactures a row of all-`NULL` for the side that found no match, and that manufactured row owes nothing to a constraint written for stored rows. The constraint held; the join, not the table, produced the `NULL` a reader is looking at.

### `UNIQUE` beyond one column

Lesson 6 covered a single nullable `UNIQUE` column accepting many `NULL`s. A composite `UNIQUE` extends the same rule across several columns, comparing the pair of values rather than each column alone.

```sql
CREATE TABLE design.u_demo (a text, b text, UNIQUE (a, b));
INSERT INTO design.u_demo VALUES ('x', 'y');
INSERT INTO design.u_demo VALUES ('x', 'y');
```

```
ERROR:  duplicate key value violates unique constraint "u_demo_a_b_key"
DETAIL:  Key (a, b)=(x, y) already exists.
SQLSTATE: 23505
```

Repeat with a `NULL` in the second column and both rows are accepted:

```sql
INSERT INTO design.u_demo VALUES ('x', NULL);
INSERT INTO design.u_demo VALUES ('x', NULL);  -- also accepted
```

Two `NULL`s are not equal for `UNIQUE`'s purposes, so `(a, b)` never repeats as far as the constraint can tell, however many rows share `a = 'x'`. `UNIQUE NULLS NOT DISTINCT`, added in PostgreSQL 15, changes that comparison: `unique nulls not distinct (a, b)` rejects the second `('x', NULL)` with the identical `23505` and a `DETAIL` reading `Key (a, b)=(x, null) already exists.`

The question deciding between the two forms is what the absence means. If `NULL` means "not yet known", several pending rows really are different facts and ordinary `UNIQUE` is correct. If `NULL` means "there is no such thing", two such rows are the same fact told twice, and `NULLS NOT DISTINCT` says so.

### A `CHECK` on a table that already has bad rows

"We can't add that constraint, the data is already dirty" turns out to have three honest steps rather than one blunt failure.

```sql
CREATE TABLE design.nv (id bigint PRIMARY KEY, amount numeric(12,2));
INSERT INTO design.nv VALUES (1, 10.00), (2, -5.00);
ALTER TABLE design.nv ADD CONSTRAINT amount_positive CHECK (amount > 0);
```

```
ERROR:  check constraint "amount_positive" of relation "nv" is violated by some row
SQLSTATE: 23514
```

The plain form checks every existing row first, and row 2 fails it. `NOT VALID` skips that check and succeeds immediately:

```sql
ALTER TABLE design.nv ADD CONSTRAINT amount_positive CHECK (amount > 0) NOT VALID;
INSERT INTO design.nv VALUES (3, -1.00);
```

```
ERROR:  new row for relation "nv" violates check constraint "amount_positive"
DETAIL:  Failing row contains (3, -1.00).
SQLSTATE: 23514
```

`NOT VALID` does not mean "not enforced": every new write is checked from the moment the constraint exists, so `-1.00` fails just as it would without the qualifier. Only row 2, already in the table, is left alone for now. `VALIDATE CONSTRAINT` checks it, and fails with the same `23514` until row 2 is fixed:

```sql
ALTER TABLE design.nv VALIDATE CONSTRAINT amount_positive;  -- fails while row 2 is still -5.00
UPDATE design.nv SET amount = 5.00 WHERE id = 2;
ALTER TABLE design.nv VALIDATE CONSTRAINT amount_positive;  -- succeeds
```

That is the honest answer to "the data is already dirty": stop new bad rows today, and clean up the old ones on a schedule that need not be today. Doing this against a live table without blocking traffic is stage 7's concern, not this lesson's.

### Domains

A domain is a named type with its own `CHECK`, usable wherever a base type is.

```sql
CREATE DOMAIN design.email_address AS text
    CHECK (value LIKE '%@%' AND length(value) BETWEEN 3 AND 320);

CREATE TABLE design.signups (id bigint PRIMARY KEY, email design.email_address);
INSERT INTO design.signups VALUES (2, 'not-an-email');
```

```
ERROR:  value for domain design.email_address violates check constraint "email_address_check"
SQLSTATE: 23514
```

A domain buys reuse: one definition, checked once, so fixing the rule means altering one domain rather than every table that copied it. What it cannot do is see past its own value: a domain's `CHECK` only ever has `value`, never a sibling column, so a rule comparing two columns still belongs on the table. Whether a domain, a lookup table or a native `enum` fits a closed set of values best is lesson 25's question.

### Exclusion constraints, and the shortcut new in PostgreSQL 18

Every constraint so far compares a row against itself or one other value. An exclusion constraint compares a row against every other row in the table, using an operator that need not be equality.

```sql
CREATE TABLE design.bookings (
    room   text,
    during daterange,
    EXCLUDE USING gist (room WITH =, during WITH &&)
);
```

On a fresh database, this fails:

```
ERROR:  data type text has no default operator class for access method "gist"
HINT:  You must specify an operator class for the index or define a default operator class for the data type.
SQLSTATE: 42704
```

`CREATE EXTENSION btree_gist`, which ships with PostgreSQL, supplies that operator class, and the same `CREATE TABLE` then succeeds. Two bookings for the same room with overlapping ranges now collide:

```
ERROR:  conflicting key value violates exclusion constraint "bookings_room_during_excl"
DETAIL:  Key (room, during)=(101, [2026-01-04,2026-01-09)) conflicts with existing key (room, during)=(101, [2026-01-01,2026-01-05)).
SQLSTATE: 23P01
```

while the adjacent range `[2026-01-05,2026-01-09)` is accepted, because a `daterange`'s upper bound is exclusive and `2026-01-05` does not belong to the first booking at all.

PostgreSQL 18 adds a shorter spelling of the common case, a range column inside a primary key:

```sql
CREATE TABLE design.reservations (
    room   text,
    during daterange,
    PRIMARY KEY (room, during WITHOUT OVERLAPS)
);
INSERT INTO design.reservations VALUES ('101', daterange('2026-01-01', '2026-01-05'));
INSERT INTO design.reservations VALUES ('101', daterange('2026-01-04', '2026-01-09'));
```

```
ERROR:  conflicting key value violates exclusion constraint "reservations_pkey"
DETAIL:  Key (room, during)=(101, [2026-01-04,2026-01-09)) conflicts with existing key (room, during)=(101, [2026-01-01,2026-01-05)).
SQLSTATE: 23P01
```

It behaves exactly like the exclusion constraint above, because that is what it is underneath. Two things trip a reader up the first time. It needs at least two columns; a single range column alone gives `ERROR: constraint using WITHOUT OVERLAPS needs at least two columns`, SQLSTATE `42601`, since the clause pairs a range against something else that must also match. It still needs `btree_gist` the moment a non-range column, here `text`, sits beside the range, failing with the identical `42704` where the extension is missing. PostgreSQL 18's release notes list the feature outright: "Temporal constraints, or constraints over ranges, for PRIMARY KEY, UNIQUE, and FOREIGN KEY constraints."

This is also where the chapter runs out of road. Every constraint above looks at one row, or, for an exclusion constraint, one row against the rest of one table, at one moment. A rule holding across several rows at once, which an exclusion constraint answers, or one that must keep holding over several statements, which needs stage 5's transactions, are two shapes a single `CHECK` was never going to cover.

```sql
DROP SCHEMA design CASCADE;
```

## Practice

1. ▢ A column is declared `email text CHECK (email LIKE '%@%')` with no `NOT NULL`. Predict whether inserting `NULL` succeeds.

<details markdown="1"><summary>Check</summary>

It succeeds. `NULL LIKE '%@%'` is unknown, not false, so the `CHECK` has nothing to reject, the same pattern as `amount >= 0` and `tier IN (...)`, just with a different operator producing the unknown.

</details>

2. ▢ A table has a plain `UNIQUE (a, b)`, `NULLS DISTINCT` by default. Predict whether two rows both holding `(NULL, NULL)` can coexist.

<details markdown="1"><summary>Hint</summary>

The rule that lets `('x', NULL)` repeat under a plain `UNIQUE` does not care which columns are `NULL`, only that at least one of them is.

</details>

<details markdown="1"><summary>Check</summary>

Yes, both insert without error. Two `NULL`s are never equal for `UNIQUE`'s comparison, so `(NULL, NULL)` never collides with itself, however often it repeats. `NULLS NOT DISTINCT` is the only way to make that pair count as one value.

</details>

3. ▢ A `CHECK` was added `NOT VALID` on a table already holding one bad row, and nobody has run `VALIDATE CONSTRAINT` yet. Predict whether an `UPDATE` that sets a different row to another bad value succeeds.

<details markdown="1"><summary>Check</summary>

It fails with `23514`, same as a fresh `INSERT`. `NOT VALID` only excuses rows that existed when the constraint was added; every write after that, insert or update, is checked as if `NOT VALID` had never been written.

</details>

4. ▢ A domain is declared `CREATE DOMAIN email_address AS text CHECK (value LIKE '%@%' AND length(value) BETWEEN 3 AND 320)` with no `NOT NULL` anywhere. Predict whether a column typed with it accepts `NULL`.

<details markdown="1"><summary>Check</summary>

Yes. A domain's `CHECK` is still a `CHECK`, and `value LIKE '%@%'` over `NULL` is unknown, not false, so the same rule that let a `NULL` amount and a `NULL` tier through lets a `NULL` email through too. A domain changes where the rule lives, not what it does with an absent value.

</details>

5. ▢ `EXCLUDE USING gist (room WITH =, during WITH &&)` rejected two overlapping bookings for room `101`. Predict what happens inserting an overlapping range for a different room, `102`.

<details markdown="1"><summary>Hint</summary>

The constraint has two parts joined by `AND`: rooms must be equal and ranges must overlap before it objects to anything.

</details>

<details markdown="1"><summary>Check</summary>

It is accepted. The exclusion fires only when every paired condition holds at once, so `room = 101 AND overlap` and `room = 102 AND overlap` are unrelated facts; an overlap spanning different rooms is not what the constraint was asked to forbid.

</details>

6. ▢ `PRIMARY KEY (room, during WITHOUT OVERLAPS)` is in place. Predict the exact error inserting a row with `during` set to `NULL`.

<details markdown="1"><summary>Check</summary>

`ERROR: null value in column "during" of relation "..." violates not-null constraint`, SQLSTATE `23502`. A primary key is `UNIQUE` plus `NOT NULL` on every one of its columns, `WITHOUT OVERLAPS` or not, so the ordinary `NOT NULL` check runs and rejects the row before the exclusion logic gets a turn.

</details>

## Real-world reps

- [ ] Find a `CHECK` constraint at work whose column is nullable and confirm, by reading the schema rather than guessing, whether `NULL` there is a deliberate allowance or an oversight nobody has hit yet.
- [ ] Pick a table someone has called "too dirty to constrain" and run the `NOT VALID` and `VALIDATE CONSTRAINT` sequence against a copy, to see how many rows validation would need fixed.
- [ ] Tomorrow: find one column-level `CHECK` repeated across more than one table and decide whether it earns being pulled into a domain.

## Going further

- [8.18. Domain Types](https://www.postgresql.org/docs/current/domains.html): the full syntax for `CREATE DOMAIN`
- [5.5.6. Exclusion Constraints](https://www.postgresql.org/docs/current/ddl-constraints.html#DDL-CONSTRAINTS-EXCLUSION): the constraint kind behind the booking example and the `WITHOUT OVERLAPS` shortcut
- [E.6. Release 18](https://www.postgresql.org/docs/release/18.0/): the notes naming temporal constraints among that release's changes
- [Appendix A. PostgreSQL Error Codes](https://www.postgresql.org/docs/current/errcodes-appendix.html): where 23514, 23505, 23P01 and 42704 are catalogued
- [Schema design](../reference/schema-design.md): the stage 4 reference sheet
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
