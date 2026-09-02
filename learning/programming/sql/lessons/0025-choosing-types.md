---
title: 25. Choosing Types Deliberately
description: A type decides what the database will accept, what it will silently change, and what it can never take back
type: lesson
---

# Lesson 25. Choosing Types Deliberately

**Mission link:** A type decides what the database will accept, what it will change before storing it, and what a later migration can never safely undo. Confusing the second for the first is how a rounded price reaches production with nobody having chosen it on purpose.
**Primary source:** [PostgreSQL, Chapter 8 Data Types](https://www.postgresql.org/docs/current/datatype.html)
**Prerequisites:** [Lesson 1](0001-tables-rows-and-types.md), [Lesson 24](0024-constraints-that-hold.md)

## Warm-up

1. ▢ Lesson 1 picked `numeric` for money without saying what happens to a value with more digits after the point than the column keeps. A `CHECK` constraint only ever produces true, false or unknown, so its only behaviours are accept and reject. Does a type's own limit have to work the same way?

<details markdown="1"><summary>Check</summary>

No. A type's limit is conversion code that runs before storage, and conversion code is free to change a value rather than refuse it. Which a given type does is something to find by inserting a boundary value and reading back what landed, which is what the rest of this lesson does.

</details>

## Know this

Every example below runs in a schema created for it and dropped afterward:

```sql
CREATE SCHEMA design;
-- ... the tables in this lesson ...
DROP SCHEMA design CASCADE;
```

### Silent change against loud refusal

This is the question the warm-up raised, and `numeric(12, 2)` gives both answers depending on where a value goes wrong. A value with too many digits after the point is rounded, quietly:

```sql
CREATE TABLE design.nums (id int, amount numeric(12, 2));
INSERT INTO design.nums VALUES (1, 10.005);
SELECT amount::text FROM design.nums;
-- 10.01
```

No error, no warning, and the `10.005` the application thought it stored is gone. A value too large for the column's precision is a different failure entirely:

```sql
INSERT INTO design.nums VALUES (2, 12345678901.12);
-- ERROR:  numeric field overflow
-- DETAIL:  A field with precision 12, scale 2 must round to an absolute value less than 10^10.
-- SQLSTATE: 22003
```

`varchar(n)` behaves the second way for its whole domain: a value one character too long is refused outright, never truncated.

```sql
CREATE TABLE design.v (id int, code varchar(5));
INSERT INTO design.v VALUES (1, 'abcdef');
-- ERROR:  value too long for type character varying(5)
-- SQLSTATE: 22001
```

The principle to carry forward: a type that changes your value without telling you is more dangerous than one that stops you, because the loud failure surfaces the day it happens and the quiet one surfaces, if at all, the day someone reconciles a total against another system. The rounding is not a flaw, it is what a fixed scale means, which is why the scale has to be a decision, two places because the business rounds to the cent, not because the last table declared it.

### Exact against approximate

Lesson 1 already told you to use `numeric` for money rather than `double precision`. The arithmetic behind that advice:

```sql
SELECT (0.1::double precision + 0.2::double precision = 0.3::double precision) AS float_eq,
       (0.1::numeric + 0.2::numeric = 0.3::numeric) AS numeric_eq;
-- float_eq = f, numeric_eq = t
```

A single addition already disagrees with itself, and it compounds: summing ten copies of `0.1` gives `0.9999999999999999` as `double precision` and exactly `1.0` as `numeric`. A binary float stores `0.1` as the nearest value representable in base two, not `0.1` itself, and every later step carries that error forward; `numeric` stores decimal digits, so a decimal fraction is exact from the first assignment. One case a float is right rather than a shortcut: a measurement whose last digits were never exact to begin with, a sensor reading, loses nothing in a type built for approximation. A price or a balance, anything a business counts on being exact, is not that case.

### Time: one instant, or none

`timestamptz` and plain `timestamp` accept the identical literal and disagree about what they kept. With the session on UTC:

```sql
CREATE TABLE design.t (id int, tstz timestamptz, ts timestamp);
INSERT INTO design.t VALUES (1, '2026-03-01 12:00+03', '2026-03-01 12:00+03');
SELECT tstz::text, ts::text FROM design.t;
-- tstz = 2026-03-01 09:00:00+00, ts = 2026-03-01 12:00:00
```

`timestamptz` converted the offset away and kept the instant; `timestamp` kept the digits and threw the offset away. Reread from a session on `America/New_York`, with nothing written in between:

```sql
SELECT tstz::text, ts::text FROM design.t;
-- tstz = 2026-03-01 04:00:00-05, ts = 2026-03-01 12:00:00
```

`tstz` now prints a different clock time, the same instant rendered for a different zone. `ts` prints the same digits it always did, now meaning five hours later than it did to the first reader, and no query can recover the zone the writer intended, since that information was never kept. The rules that follow: store an instant in `timestamptz`, keep `date` for a day with genuinely no time of day, and expect `interval` arithmetic not always to stay in the type you started with, since `now() - interval '1 day'` returns a `timestamptz` but `current_date + interval '1 day'` returns a `timestamp`, a span carrying a time of day promoting a bare date into one.

### char(n), precisely

Lesson 1 already told you to avoid `char(n)`. Here is exactly what it does rather than a slogan about it. `char(5)` really does store the padding:

```sql
CREATE TABLE design.c (id int, code char(5));
INSERT INTO design.c VALUES (1, 'ab');
SELECT octet_length(code) AS oct, length(code) AS len, code::text AS cast_text, format('[%s]', code) AS shown FROM design.c;
-- oct = 5, len = 2, cast_text = ab, shown = [ab   ]
```

`octet_length` counts five stored bytes, so the padding is really there on disk. `length()` reports two, because `length()` for `character` types trims trailing blanks before counting, and a cast to `text` does the same, dropping the cast value's own `octet_length` to 2. `format`'s `%s` shows the padding, `[ab   ]`, printing `character` output rather than a trimmed one. So the padding is stored and mostly invisible, hidden by the two paths most code reads a column through, resurfacing only where something does not trim it: a client library reporting column length, or a fixed-width export. None of this contradicts avoiding the type; it explains why.

### The small closed set, decided

Lesson 1 named two alternatives to a native `enum` and left the choice between them open. Three designs answer the same question, a plan or a status from a small closed set, and all three refuse the same bad input before diverging on what changing the set costs.

An `enum` rejects an unlisted label at the boundary:

```sql
CREATE TYPE design.plan_t AS ENUM ('free', 'pro');
CREATE TABLE design.subs (id int, plan design.plan_t);
INSERT INTO design.subs VALUES (1, 'gold');
-- ERROR:  invalid input value for enum design.plan_t: "gold"
-- SQLSTATE: 22P02
```

That is the good half. Adding a value is not free: a label added by `ALTER TYPE ... ADD VALUE` cannot be used by an insert in the same transaction.

```sql
BEGIN;
ALTER TYPE design.plan_t ADD VALUE 'trial';
INSERT INTO design.subs VALUES (2, 'trial');
-- ERROR:  unsafe use of new value "trial" of enum type design.plan_t
-- HINT:  New enum values must be committed before they can be used.
-- SQLSTATE: 55P04
```

And a value can never be removed: `ALTER TYPE design.plan_t DROP VALUE 'trial'` fails with `ERROR: dropping an enum value is not implemented`, `SQLSTATE 0A000`. `text` with a `CHECK` rejects the same bad label with `23514`, and neither enum cost applies: adding a value to its list works inside one transaction, and removing one works too once no row still holds it, lesson 24's rule about a constraint added to violating rows. A lookup table rejects the bad label as `23503` instead of `22P02`; adding a value is a plain insert, usable immediately; removing one is a plain delete, blocked by that same `23503` while a row still references it.

That gap is the recommendation. Reach for a native `enum` when the set is fixed outside the business, a currency code, a day of the week, so its two costs never fall on your team. Reach for `text` with a `CHECK` or a lookup table when the business will plausibly add a value next quarter: a `CHECK` when nothing else references a row per value, a lookup table once something does.

### citext, and the schema decisions hiding inside a type

`citext`, from an extension that ships with PostgreSQL, makes a `UNIQUE` constraint case-insensitive by folding case before comparing:

```sql
CREATE EXTENSION citext;
CREATE TABLE design.people (id int, email citext UNIQUE);
INSERT INTO design.people VALUES (1, 'Ada@Example.com');
INSERT INTO design.people VALUES (2, 'ada@example.com');
-- ERROR:  duplicate key value violates unique constraint "people_email_key"
-- SQLSTATE: 23505
```

A second way to get the same guarantee exists, a `UNIQUE` index built on `lower(email)` rather than on `email` itself, and it belongs to stage 6 rather than here, because it is an index.

Two more types are schema decisions wearing a column declaration. A `text[]` column holds a tag list honestly: it prints as `{red,small}`, `= ANY (tags)` finds a row containing a given tag, and `unnest(tags)` turns one row into several. What it gives up is that no foreign key can point at one of its elements, only at the whole array, so nothing stops a tag being misspelled the way a lookup table would. Lesson 19's document column and lesson 21's repeating-groups argument apply here without re-teaching either: both put more than one fact in a single column, a cost lesson 21 already made the case against.

## Practice

1. ▢ Predict the exact error, its `DETAIL`, and its SQLSTATE for inserting `12.34` into a column declared `numeric(3, 2)`.

<details markdown="1"><summary>Hint</summary>

The `DETAIL` states the limit as a power of ten; work the exponent out from this column's own precision and scale.

</details>

<details markdown="1"><summary>Check</summary>

`ERROR: numeric field overflow`, `DETAIL: A field with precision 3, scale 2 must round to an absolute value less than 10^1.`, SQLSTATE `22003`. Three digits with two after the point leaves one before it, so nothing at or above ten fits.

</details>

2. ▢ Predict whether `'ab'::char(5) = 'ab '::char(5)` is true, and whether `'ab'::char(5) = 'ab'::text` is true.

<details markdown="1"><summary>Check</summary>

Both are true. `character` comparison treats trailing blanks as insignificant, so values padding out to the same content compare equal. The cross-type comparison is also true, because the cast to `text` strips the padding first, leaving `ab` on both sides.

</details>

3. ▢ Predict the type PostgreSQL reports for `current_date + interval '1 day'`, and say why it is not the type you started with.

<details markdown="1"><summary>Hint</summary>

Ask what a `date` would have to become if the interval carried a time of day rather than whole days.

</details>

<details markdown="1"><summary>Check</summary>

`timestamp without time zone`. An `interval` can carry hours and minutes, so PostgreSQL cannot promise the result still falls at midnight, and it widens a `date` into a `timestamp` to hold whatever time of day the arithmetic produces, even for an interval that happened to be a whole number of days.

</details>

4. ▢ A table `tags_lookup (tag text PRIMARY KEY)` already exists. Predict what happens when you declare `CREATE TABLE widgets (id int, tags text[] REFERENCES tags_lookup (tag))`.

<details markdown="1"><summary>Check</summary>

`ERROR: foreign key constraint "widgets_tags_fkey" cannot be implemented`, `DETAIL: Key columns "tags" of the referencing table and "tag" of the referenced table are of incompatible types: text[] and text.`, SQLSTATE `42804`. `tags_lookup.tag` holds one label per row, `widgets.tags` holds many, and PostgreSQL will not even create the constraint, the sharpest version of the claim that no foreign key reaches inside an array.

</details>

5. ▢ The `design.people` table from this lesson has one row for `Ada@Example.com`. Predict whether `SELECT email FROM design.people WHERE email LIKE 'ADA%'` returns it.

<details markdown="1"><summary>Check</summary>

Yes. `citext` folds case for every comparison it supports, not only `UNIQUE`, and `LIKE` is one of them, worth knowing before choosing it for a column that wants a case-sensitive `LIKE`.

</details>

6. ▢ Of a native `enum`, `text` with a `CHECK`, and a lookup table, predict which ones let a value added inside a transaction be used by an insert later in that same transaction, and which one refuses with `55P04`.

<details markdown="1"><summary>Check</summary>

`text` with a `CHECK` and the lookup table both allow it: dropping and re-adding a constraint, and inserting a lookup row, are ordinary statements with no special visibility rule. Only the native `enum` refuses, with `55P04`, because PostgreSQL treats a newly added label as unsafe to read until the transaction that added it is guaranteed to have happened.

</details>

## Real-world reps

- [ ] Find a table storing money in a float type, and check whether a report's total would change, even slightly, if recomputed from `numeric`.
- [ ] Find a column declared `char(n)` or its equivalent, and check whether any code reading it compares the raw value rather than a trimmed one.
- [ ] Tomorrow: find one status or category column, name which of the three closed-set designs it uses, and decide whether it is still the right one.

## Going further

- [8.5. Date/Time Types](https://www.postgresql.org/docs/current/datatype-datetime.html): the full rules for `timestamptz`, `timestamp` and `interval` arithmetic
- [8.7. Enumerated Types](https://www.postgresql.org/docs/current/datatype-enum.html): the complete rules for adding, renaming and ordering enum labels
- [8.15. Arrays](https://www.postgresql.org/docs/current/arrays.html): declaring, indexing and unnesting an array column
- [F.9. citext](https://www.postgresql.org/docs/current/citext.html): the extension behind a case-insensitive comparison
- [Schema design](../reference/schema-design.md): the stage 4 reference sheet
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
