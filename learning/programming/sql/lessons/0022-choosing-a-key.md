---
title: 22. Choosing a Key
description: A surrogate key buys stability and gives up meaning, and the generator you pick decides what else it costs
type: lesson
---

# Lesson 22. Choosing a Key

**Mission link:** Every table answers this question once: a key built from data the business edits ties every foreign key to that edit, while a generated key costs meaning and, depending how it is made, bytes or ordering guarantees you may not need.
**Primary source:** [PostgreSQL, 5.5 Constraints](https://www.postgresql.org/docs/current/ddl-constraints.html)
**Prerequisites:** [Lesson 6](0006-keys-and-constraints.md), [Lesson 21](0021-normalisation.md)

## Warm-up

1. ▢ Lesson 6 showed that a `customers` table usually gets a generated `bigint` primary key plus a `UNIQUE` constraint on `email`, giving it two candidate keys with only one chosen as primary. What does the surrogate buy that email alone would not?

<details markdown="1"><summary>Check</summary>

Stability. The surrogate id never has to change when a customer edits their address, so nothing referencing it changes either; email still identifies the row, as a candidate key, it is simply not the one every foreign key points at.

</details>

## Know this

### The trade, not the rule

A **natural key** is data the domain already has: an ISO country code, an email address, a national identifier. It carries meaning of its own and enforces uniqueness of the real-world thing it names, so a `countries` table keyed on `code` gets a free guarantee that the same country never appears twice. A **surrogate key** is invented for the sole purpose of naming a row, and the glossary's point stands: it carries no meaning of its own, which is exactly why it does not have to change when the meaning does. The fixture makes both cases concrete. `countries.code` is genuinely stable: `GB` has meant the United Kingdom since the standard was drafted, and no ordinary business change touches it. `customers.id` is the opposite: a surrogate sitting beside `email`, a **candidate key** in the glossary's exact sense, and the one column here a person can and does change. Neither choice is universally right; the question is whether the identifying column is also one someone outside the database has reason to edit. When yes, a surrogate earns its keep; when genuinely no, as with a country code, a natural key costs nothing extra and gives a free constraint besides.

### What a natural key costs when the domain moves

A schema of your own holds the rest of this lesson's tables.

```sql
CREATE SCHEMA design;

CREATE TABLE design.suppliers_nat (
    code text PRIMARY KEY,
    name text NOT NULL
);
CREATE TABLE design.parts_nat (
    id            bigint PRIMARY KEY,
    supplier_code text NOT NULL REFERENCES design.suppliers_nat (code)
);
INSERT INTO design.suppliers_nat (code, name) VALUES ('ACME', 'Acme Fasteners');
INSERT INTO design.parts_nat (id, supplier_code) VALUES (1, 'ACME'), (2, 'ACME');
```

Renaming the supplier's code looks like a single statement and is not one:

```sql
UPDATE design.suppliers_nat SET code = 'ACME-CORP' WHERE code = 'ACME';
```

`ERROR: update or delete on table "suppliers_nat" violates foreign key constraint "parts_nat_supplier_code_fkey" on table "parts_nat"`, `DETAIL: Key (code)=(ACME) is still referenced from table "parts_nat".`, SQLSTATE `23503`. Renaming for real takes three statements in this order, since a child row can no more point at a code not yet created than be left pointing at one just deleted:

```sql
INSERT INTO design.suppliers_nat (code, name) VALUES ('ACME-CORP', 'Acme Fasteners');
UPDATE design.parts_nat SET supplier_code = 'ACME-CORP' WHERE supplier_code = 'ACME';
DELETE FROM design.suppliers_nat WHERE code = 'ACME';
```

Every one of those statements is a place the rename can be interrupted, and every referencing table has to be found first; a lone insert against the vanished code still fails with the same `23503`. Now build the same relationship with a surrogate: `code` becomes an ordinary column, and the reference points at a generated `id` instead.

```sql
CREATE TABLE design.suppliers_sur (
    id   bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    code text NOT NULL,
    name text NOT NULL
);
CREATE TABLE design.parts_sur (
    id          bigint PRIMARY KEY,
    supplier_id bigint NOT NULL REFERENCES design.suppliers_sur (id)
);
INSERT INTO design.suppliers_sur (code, name) VALUES ('ACME', 'Acme Fasteners');
INSERT INTO design.parts_sur (id, supplier_id) VALUES (1, 1), (2, 1);
UPDATE design.suppliers_sur SET code = 'ACME-CORP' WHERE code = 'ACME';
```

That `UPDATE` reports one row changed and nothing else moves: `parts_sur` never mentioned the code, so there is nothing downstream to find. That is the whole cost of a natural key: identity and meaning are the same column, so a change to the meaning is a change to every table that referenced it.

### A composite natural key

Some real identities are two columns together rather than one.

```sql
CREATE TABLE design.enrolments (
    student_id integer NOT NULL,
    course_id  integer NOT NULL,
    grade      text,
    PRIMARY KEY (student_id, course_id)
);
INSERT INTO design.enrolments (student_id, course_id, grade) VALUES (1, 100, 'B');
INSERT INTO design.enrolments (student_id, course_id, grade) VALUES (1, 100, 'A');
```

The second insert is correctly rejected: `ERROR: duplicate key value violates unique constraint "enrolments_pkey"`, `DETAIL: Key (student_id, course_id)=(1, 100) already exists.`, SQLSTATE `23505`; a student is not enrolled twice in the same course. The width does not stay contained to this table, though: any child naming one enrolment has to carry both columns:

```sql
CREATE TABLE design.assignments (
    id         integer PRIMARY KEY,
    student_id integer NOT NULL,
    course_id  integer NOT NULL,
    FOREIGN KEY (student_id, course_id) REFERENCES design.enrolments (student_id, course_id)
);
```

That works, and rejects a pair absent from the parent with the same `23503`. Referencing only `student_id` fails outright at `CREATE TABLE` time instead: `ERROR: there is no unique constraint matching given keys for referenced table "enrolments"`, SQLSTATE `42830`, since one column of a two-column key identifies nothing alone. A composite natural key can be exactly the right model, but every downstream table inherits its width, two columns where a surrogate key would have needed one.

### Identity columns, the surrogate generator this engine prefers

A surrogate key still has to come from somewhere, and on this engine an identity column is the mechanism to write in new code, not `serial`.

```sql
CREATE TABLE design.by_default_ids (
    id   bigint GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    note text
);
INSERT INTO design.by_default_ids (note) VALUES ('a'), ('b');
INSERT INTO design.by_default_ids (id, note) VALUES (100, 'explicit');
INSERT INTO design.by_default_ids (note) VALUES ('c');
```

`GENERATED BY DEFAULT AS IDENTITY` lets that explicit `100` straight through, so the four ids come back `1, 2, 3, 100`: the sequence was never told about the value that bypassed it and keeps counting from where it stood. Advancing the sequence to `99` and inserting once more reproduces the collision this leaves waiting: `ERROR: duplicate key value violates unique constraint "by_default_ids_pkey"`, `DETAIL: Key (id)=(100) already exists.`, SQLSTATE `23505`, the moment the sequence catches up. `GENERATED ALWAYS AS IDENTITY` closes that door instead:

```sql
CREATE TABLE design.always_ids (
    id   bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    note text
);
INSERT INTO design.always_ids (note) VALUES ('a');
INSERT INTO design.always_ids (id, note) VALUES (50, 'explicit');
```

The explicit insert is refused: `ERROR: cannot insert a non-DEFAULT value into column "id"`, `DETAIL: Column "id" is an identity column defined as GENERATED ALWAYS.`, `HINT: Use OVERRIDING SYSTEM VALUE to override.`, SQLSTATE `428C9`. The hinted escape works when a migration restoring old rows, not an ordinary insert, is what is asking:

```sql
INSERT INTO design.always_ids (id, note) OVERRIDING SYSTEM VALUE VALUES (50, 'explicit');
```

`serial` looks like the same idea and is not: it is sugar for an ordinary column with a `nextval()` default, and `information_schema.columns` reports its `data_type` as `integer`, four bytes, and `is_identity` as `NO`, against `YES` and eight bytes for the identity column above. Write `GENERATED ALWAYS AS IDENTITY` in new code: it is the mechanism the engine tracks as an identity, `serial` an older shorthand predating it, and lesson 1's advice to make an identifier `bigint` is the same advice arriving with a generator attached.

### UUID keys, and what the version buys

A UUID is a surrogate key generated as a value rather than counted by a sequence, and this release offers two ways to make one with no extension required. `gen_random_uuid()` produces sixteen bytes of pure randomness: three successive calls share no prefix, for example `15c4b061-c90d-4b62-...`, `6435fb38-8743-40f6-...` and `6ee77620-0b80-4900-...`. `uuidv7()` is new in PostgreSQL 18, named in that release's own notes as the "uuidv7() function for generating timestamp-ordered UUIDs", and three successive calls show exactly that, a shared leading prefix and strictly increasing values: `01a062fb-cf7d-7de6-...`, `01a062fb-cf7d-7df3-...` and `01a062fb-cf7d-7df8-...`. On an older supported major, 14 to 17, there is no such function and `gen_random_uuid()` is the only built-in generator. The honest comparison stops short of a performance claim. A UUID of either kind can be generated anywhere, including by a client before the row exists, which a sequence-backed identity column cannot do, and it costs more either way: `pg_column_size()` reports sixteen bytes against eight for a `bigint`. A time-ordered UUID keeps rows inserted together near each other in the key's own order, where a random one scatters them; whether that scattering costs anything is a question about index structure for stage 6, and nothing measured here answers it.

### The rule that survives all of it

Whichever of the above ends up as a table's primary key, every other candidate key still needs its own constraint, because a primary key only enforces uniqueness of the column it names.

```sql
CREATE TABLE design.customers_nounique (
    id    bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    email text NOT NULL
);
INSERT INTO design.customers_nounique (email) VALUES ('ada@example.com');
INSERT INTO design.customers_nounique (email) VALUES ('ada@example.com');
```

Both inserts succeed, two rows with different ids and the identical email, with nothing in the schema noticing. That is lesson 21's duplicate-row anomaly again, arriving through a different door: not a denormalised report table with no keys at all, but a properly surrogate-keyed one that never declared `email` as the candidate key it actually is. The fix is the pairing lesson 6 already recommended, a surrogate primary key plus a `UNIQUE` constraint on every column meant to identify a row on its own; choosing a good primary key is only half the design, and forgetting a table can have more than one key worth enforcing is the other half of getting it wrong.

```sql
DROP SCHEMA design CASCADE;
```

## Practice

1. ▢ Using `suppliers_nat` and `parts_nat` above, predict the exact error and SQLSTATE of updating a supplier's code while a part still references the old value.

<details markdown="1"><summary>Hint</summary>

The failure is the same shape as deleting a referenced parent row: both leave a child row pointing at a value that no longer exists.

</details>

<details markdown="1"><summary>Check</summary>

`ERROR: update or delete on table "suppliers_nat" violates foreign key constraint "parts_nat_supplier_code_fkey" on table "parts_nat"`, `DETAIL: Key (code)=(ACME) is still referenced from table "parts_nat".`, SQLSTATE `23503`. To the constraint, updating the referenced value is indistinguishable from deleting it.

</details>

2. ▢ Predict the exact error and SQLSTATE of inserting a `parts_nat` row whose `supplier_code` is `'GLOBEX'`, a code `suppliers_nat` does not hold.

<details markdown="1"><summary>Check</summary>

`ERROR: insert or update on table "parts_nat" violates foreign key constraint "parts_nat_supplier_code_fkey"`, `DETAIL: Key (supplier_code)=(GLOBEX) is not present in table "suppliers_nat".`, SQLSTATE `23503`. Same SQLSTATE as before: a foreign key value must exist on the other side, whether it vanished afterward or was never there.

</details>

3. ▢ Using the composite-keyed `enrolments (student_id, course_id)` table, predict the exact error and SQLSTATE of declaring a foreign key against `student_id` alone from a new table.

<details markdown="1"><summary>Hint</summary>

The failure happens at `CREATE TABLE`, before any row is inserted, because the problem is with what the reference names rather than with any data.

</details>

<details markdown="1"><summary>Check</summary>

`ERROR: there is no unique constraint matching given keys for referenced table "enrolments"`, SQLSTATE `42830`. `student_id` alone is not a key of `enrolments`, only the pair is, so there is nothing unique for a single-column reference to point at.

</details>

4. ▢ A `GENERATED BY DEFAULT AS IDENTITY` column has produced ids 1, 2 and 3, then accepted an explicit insert of 100. Predict what happens once further default inserts bring the sequence up to 100, and name the SQLSTATE.

<details markdown="1"><summary>Check</summary>

The default insert that would produce 100 fails instead: `ERROR: duplicate key value violates unique constraint "by_default_ids_pkey"`, `DETAIL: Key (id)=(100) already exists.`, SQLSTATE `23505`. `BY DEFAULT` let 100 through without telling the sequence, which keeps counting as though 100 were still free.

</details>

5. ▢ Predict whether three successive calls to `gen_random_uuid()` share any structural pattern the way three calls to `uuidv7()` do.

<details markdown="1"><summary>Check</summary>

No. Three `gen_random_uuid()` values come back with no shared prefix and no ordering between them, since every bit is random. `uuidv7()` shares a leading prefix and increases across calls because part of the value is a timestamp; `gen_random_uuid()` carries no timestamp to share.

</details>

6. ▢ A table has a `bigint identity` primary key and an `email` column with no constraint on it at all. Predict whether two rows can hold the same email, and name the earlier lesson whose anomaly this reproduces.

<details markdown="1"><summary>Hint</summary>

The primary key only says the id column is unique; ask what, if anything, it says about any other column.

</details>

<details markdown="1"><summary>Check</summary>

Yes: two rows with different ids and the identical email insert without complaint, since the primary key enforces uniqueness of `id` alone. This is lesson 21's duplicate-row anomaly, reached this time through a properly surrogate-keyed table that never gave its natural candidate key a `UNIQUE` constraint of its own.

</details>

## Real-world reps

- [ ] Pick a table you work with and identify every column, or column combination, unique in practice; check how many actually carry a `UNIQUE` constraint rather than being unique by convention.
- [ ] Find a primary key in a schema you maintain that is a natural key, such as a code or an email, and trace how many other tables would need a change if that value were ever edited.
- [ ] Tomorrow: check which surrogate key generator a table you own uses, `serial`, an identity column, or a UUID function, and whether that choice was made on purpose or inherited from an older example.

## Going further

- [5.3. Identity Columns](https://www.postgresql.org/docs/current/ddl-identity-columns.html): the `GENERATED ... AS IDENTITY` syntax and how `ALWAYS` and `BY DEFAULT` differ
- [9.14. UUID Functions](https://www.postgresql.org/docs/current/functions-uuid.html): `gen_random_uuid()`, `uuidv4()` and `uuidv7()`, with their signatures side by side
- [E.6. Release 18](https://www.postgresql.org/docs/release/18.0/): where `uuidv7()` and virtual generated columns were introduced
- [Appendix A. PostgreSQL Error Codes](https://www.postgresql.org/docs/current/errcodes-appendix.html): where SQLSTATEs 23503, 23505, 428C9 and 42830 are catalogued
- [Schema design](../reference/schema-design.md): the stage 4 reference sheet
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
