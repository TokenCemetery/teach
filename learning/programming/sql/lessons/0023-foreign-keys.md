---
title: 23. Foreign Keys and What Happens on Delete
description: A foreign key is a promise about rows that exist, and the action you choose decides who pays when one goes
type: lesson
---

# Lesson 23. Foreign Keys and What Happens on Delete

**Mission link:** Every table referencing another one needs an answer to "what happens when the referenced row is deleted", and a schema that never chose leaves the answer to whichever migration ran last, discovered the day a cleanup either orphans rows silently or blocks on data nobody remembered.
**Primary source:** [PostgreSQL, 5.5.5 Foreign Keys](https://www.postgresql.org/docs/current/ddl-constraints.html)
**Prerequisites:** [Lesson 8](0008-outer-joins-and-missing-rows.md), [Lesson 22](0022-choosing-a-key.md)

## Warm-up

1. ▢ Lesson 8 established that an inner join to a missing row produces nothing, and an outer join keeps the row with `NULL`s standing in for it. If `orders.customer_id` could hold a value with no matching row in `customers`, what would an inner join quietly do to that order, and why would that be worse than an outer join simply showing it as missing?

<details markdown="1"><summary>Check</summary>

The inner join would drop the order from the result with no error and no sign anything had gone missing, and a report built on that join would come in short by exactly that many orders, with nothing to say why. An outer join showing the row as missing is a fact the reader can act on; a row whose customer reference was never real is a fact the reader cannot even see. This is why `orders.customer_id` carries a foreign key rather than a plain column: it makes "missing after the join" mean one thing only, that no customer placed that order, not that the reference itself was hollow.

</details>

## Know this

### What the constraint promises, and when it checks it

A foreign key says every value in the referencing column must equal some value in the referenced table's key, nothing more: not that it is the correct row for the business, only that the row exists. The check runs on insert, and on update of either side, since both are moments the promise could stop holding. A plain foreign key refuses a value the parent does not have:

```sql
CREATE TABLE parent0 (id bigint PRIMARY KEY, name text);
CREATE TABLE child0 (id bigint PRIMARY KEY, parent_id bigint NOT NULL REFERENCES parent0 (id));
INSERT INTO parent0 (id, name) VALUES (1, 'a');
INSERT INTO child0 (id, parent_id) VALUES (1, 999);
```

```
ERROR:  insert or update on table "child0" violates foreign key constraint "child0_parent_id_fkey"
DETAIL:  Key (parent_id)=(999) is not present in table "parent0".
SQLSTATE: 23503
```

The message says "insert or update" because the same check fires for both, and `DETAIL` names the exact value with nowhere to land. This is precisely the shape `orders.customer_id bigint NOT NULL REFERENCES customers (id)` already has in the fixture, which is what the warm-up was pointing at: because that constraint exists, a `customers` outer join can only add a customer with no orders, never lose an order to a reference that was never good. Lesson 8's vocabulary of "kept" and "dropped" only means something because a foreign key decided in advance which side of a join is allowed to be absent.

### Five ways to answer "what happens on delete"

Deleting a referenced row forces a choice about the rows still pointing at it, and PostgreSQL names five answers in `ON DELETE`. One parent, one child with three columns, plain, `SET NULL` and `CASCADE`, all pointing at the same parent:

```sql
CREATE TABLE parentA (id bigint PRIMARY KEY, name text);
INSERT INTO parentA (id, name) VALUES (1, 'no-action-parent'), (2, 'set-null-parent'), (3, 'cascade-parent');

CREATE TABLE childA (
    id bigint PRIMARY KEY,
    na_id bigint REFERENCES parentA (id),
    sn_id bigint REFERENCES parentA (id) ON DELETE SET NULL,
    ca_id bigint REFERENCES parentA (id) ON DELETE CASCADE
);
INSERT INTO childA (id, na_id, sn_id, ca_id) VALUES (1, 1, 2, 3);
```

Deleting parent 1 refuses:

```
ERROR:  update or delete on table "parenta" violates foreign key constraint "childa_na_id_fkey" on table "childa"
DETAIL:  Key (id)=(1) is still referenced from table "childa".
SQLSTATE: 23503
```

Deleting parent 2 succeeds and leaves `sn_id` as `NULL`. Deleting parent 3 succeeds and removes the child row entirely: `CASCADE` turns one delete into two. `NO ACTION`, spelled out or left as the default, is the strictest in effect though not in name, since it simply refuses the delete.

`RESTRICT` also refuses the delete, but with a different SQLSTATE:

```sql
CREATE TABLE parentB (id bigint PRIMARY KEY, name text);
INSERT INTO parentB (id, name) VALUES (4, 'restrict-parent'), (5, 'set-default-parent'), (6, 'the-default-row');
CREATE TABLE childB (
    id bigint PRIMARY KEY,
    re_id bigint REFERENCES parentB (id) ON DELETE RESTRICT,
    sd_id bigint NOT NULL DEFAULT 6 REFERENCES parentB (id) ON DELETE SET DEFAULT
);
INSERT INTO childB (id, re_id, sd_id) VALUES (1, 4, 5);
DELETE FROM parentB WHERE id = 4;
```

```
ERROR:  update or delete on table "parentb" violates RESTRICT setting of foreign key constraint "childb_re_id_fkey" on table "childb"
DETAIL:  Key (id)=(4) is referenced from table "childb".
SQLSTATE: 23001
```

`23001` is `restrict_violation`, its own code, not `23503`. Deleting parent 5 next succeeds and sets `sd_id` to the column's `DEFAULT`, 6, since `SET DEFAULT` copies in the default expression rather than `NULL`. That only works because 6 is itself still there: deleting it afterwards fails with the ordinary `23503`, because the value `SET DEFAULT` just wrote now has nowhere to point either. The default has to name a row the table actually holds, or it only postpones the failure `NO ACTION` would have given immediately; with no `DEFAULT` clause, the implicit default is `NULL`, so an undeclared `SET DEFAULT` behaves like `SET NULL`.

### `NO ACTION` and `RESTRICT` differ only in timing

Both refuse a delete that would leave a dangling reference, so the distinction is easy to state and easy to disbelieve without seeing it: `RESTRICT` checks immediately, `NO ACTION` checks at the end of the statement by default and, declared `DEFERRABLE INITIALLY DEFERRED`, can be pushed to the end of the transaction. That gap lets a `NO ACTION` delete succeed even though the deleted row briefly has no replacement, provided something puts a valid one back before the transaction ends:

```sql
CREATE TABLE parentC (id bigint PRIMARY KEY);
CREATE TABLE childC (id bigint PRIMARY KEY, parent_id bigint REFERENCES parentC (id) ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED);
INSERT INTO parentC (id) VALUES (1);
INSERT INTO childC (id, parent_id) VALUES (1, 1);

BEGIN;
DELETE FROM parentC WHERE id = 1;
INSERT INTO parentC (id) VALUES (1);
COMMIT;
```

Both statements succeed and commit: at commit time `childC.parent_id = 1` finds a row again, so the deferred check never sees the gap. The identical two statements against a `RESTRICT` column never get that far:

```sql
CREATE TABLE parentD (id bigint PRIMARY KEY);
CREATE TABLE childD (id bigint PRIMARY KEY, parent_id bigint REFERENCES parentD (id) ON DELETE RESTRICT DEFERRABLE INITIALLY DEFERRED);
INSERT INTO parentD (id) VALUES (1);
INSERT INTO childD (id, parent_id) VALUES (1, 1);
BEGIN;
DELETE FROM parentD WHERE id = 1;
```

```
ERROR:  update or delete on table "parentd" violates RESTRICT setting of foreign key constraint "childd_parent_id_fkey" on table "childd"
SQLSTATE: 23001
```

The `DELETE` itself fails, `DEFERRABLE` clause and all, because `RESTRICT` refuses to wait even when asked. That is the whole difference: `NO ACTION` lets a statement succeed that `RESTRICT` refuses, a delete a later statement in the same transaction repairs before anyone outside looks.

### `ON UPDATE`, and why it earns its place mainly on a natural key

The same five actions apply to `ON UPDATE`, firing when the referenced key's value changes rather than its row disappearing. It matters less than `ON DELETE` for the reason lesson 22 already argued: a surrogate key is not meant to change, so `ON UPDATE CASCADE` sits on a column never supposed to move. A natural key is where it earns its keep, since a value doing double duty as identity is exactly what a business renames:

```sql
CREATE TABLE categoryE (code text PRIMARY KEY, name text);
CREATE TABLE productE (id bigint PRIMARY KEY, category_code text REFERENCES categoryE (code) ON UPDATE CASCADE, name text);
INSERT INTO categoryE (code, name) VALUES ('BOOK', 'Books');
INSERT INTO productE (id, category_code, name) VALUES (1, 'BOOK', 'Atlas');
UPDATE categoryE SET code = 'BOOKS' WHERE code = 'BOOK';
```

`productE.category_code` reads back as `BOOKS`, carried along automatically. Without `CASCADE`, the same rename fails with the ordinary `23503`, since the old code the product still holds would no longer exist.

### Deferring the promise, and a self-reference on its own terms

A pair of rows referencing each other cannot be inserted under an ordinary foreign key, because whichever row goes first names a value the other has not supplied yet:

```sql
CREATE TABLE friendF (id bigint PRIMARY KEY, best_friend_id bigint REFERENCES friendF (id));
INSERT INTO friendF (id, best_friend_id) VALUES (1, 2);
```

```
ERROR:  insert or update on table "friendf" violates foreign key constraint "friendf_best_friend_id_fkey"
DETAIL:  Key (best_friend_id)=(2) is not present in table "friendf".
SQLSTATE: 23503
```

Declared `DEFERRABLE INITIALLY DEFERRED`, the identical pair inserts and commits, because neither row is checked until the transaction ends and both exist by then:

```sql
CREATE TABLE friendG (id bigint PRIMARY KEY, best_friend_id bigint REFERENCES friendG (id) DEFERRABLE INITIALLY DEFERRED);
BEGIN;
INSERT INTO friendG (id, best_friend_id) VALUES (1, 2);
INSERT INTO friendG (id, best_friend_id) VALUES (2, 1);
COMMIT;
```

The cost is real, not theoretical: between the two inserts, row 1 references a friend not there yet, violating the promise the constraint exists to keep. Querying `friendG` from a second, independent connection during that window, before the first connection's `COMMIT`, returns no rows at all for either id: nothing outside the transaction can see the gap.

A self-reference need not be mutual to be useful; a parts table, one row per part naming its own assembly, is the ordinary case lesson 18's hierarchy walk already assumed:

```sql
CREATE TABLE partH (id bigint PRIMARY KEY, parent_id bigint REFERENCES partH (id), name text);
INSERT INTO partH (id, parent_id, name) VALUES (1, NULL, 'bicycle');
INSERT INTO partH (id, parent_id, name) VALUES (2, 1, 'wheel');
INSERT INTO partH (id, parent_id, name) VALUES (3, 2, 'spoke');
```

The root, the bicycle itself, has no assembly above it, so its `parent_id` is `NULL`. That is not stylistic: declaring the column `NOT NULL` makes a root impossible to insert, since a root has nothing real to reference and `NULL` is the only value a foreign key never checks:

```sql
CREATE TABLE partI (id bigint PRIMARY KEY, parent_id bigint NOT NULL REFERENCES partI (id), name text);
INSERT INTO partI (id, parent_id, name) VALUES (1, NULL, 'bicycle');
```

```
ERROR:  null value in column "parent_id" of relation "parti" violates not-null constraint
DETAIL:  Failing row contains (1, null, bicycle).
SQLSTATE: 23502
```

### What a foreign key does not promise

It promises the row exists, not that it is the right row. A shipment attributed to the wrong customer satisfies the constraint completely as long as the id it names belongs to somebody:

```sql
CREATE TABLE shipmentJ (id bigint PRIMARY KEY, customer_id bigint NOT NULL REFERENCES customers (id), courier text);
INSERT INTO shipmentJ (id, customer_id, courier) VALUES (1, 3, 'Speedy Post');
```

That insert succeeds and joins cleanly to customer 3, `alan@example.com`, whether or not Alan actually ordered it; nothing in the constraint tells a correct reference from a merely valid one. Nor does it reach past a column boundary: lesson 19 already showed an `events.payload` document whose `order_id` pointed at a real order with nothing enforcing the connection, and a foreign key cannot check a key buried inside a `jsonb` column, only a column holding the value directly. Catching a valid-but-wrong reference, or a value trapped where no constraint can see it, is lesson 24's material; whether the referencing column needs an index for speed is stage 6's question, left unanswered here.

## Practice

1. ▢ A table `review (id, customer_id NOT NULL REFERENCES customers (id))` exists. Predict the exact error, `DETAIL` and SQLSTATE of inserting a row with `customer_id = 500`, a value no customer has.

<details markdown="1"><summary>Check</summary>

`ERROR: insert or update on table "review" violates foreign key constraint "review_customer_id_fkey"`, `DETAIL: Key (customer_id)=(500) is not present in table "customers".`, SQLSTATE `23503`. Only the constraint name and the value in `DETAIL` change from any other foreign key failure.

</details>

2. ▢ `partH` from this lesson still has its three rows, bicycle, wheel and spoke, linked with a plain self-referencing foreign key. Predict what `DELETE FROM partH WHERE id = 1` does.

<details markdown="1"><summary>Hint</summary>

The default `ON DELETE` action applies here exactly as it does to any other foreign key.

</details>

<details markdown="1"><summary>Check</summary>

It fails with `23503`, since the wheel's `parent_id` still names it. A plain self-reference gives a hierarchy no more permission to lose its root than any other foreign key gives a parent permission to disappear from under a child.

</details>

3. ▢ The same three rows are rebuilt as `partK`, with `parent_id bigint REFERENCES partK (id) ON DELETE CASCADE`. Predict the row count of `partK` after `DELETE FROM partK WHERE id = 1`.

<details markdown="1"><summary>Check</summary>

Zero. Deleting the bicycle cascades to the wheel referencing it, and that delete cascades again to the spoke referencing the wheel, so one statement removes the whole subtree, verified by running it.

</details>

4. ▢ `childL (id, parent_id NOT NULL REFERENCES parentL (id) ON DELETE SET NULL)` holds one row referencing `parentL`'s only row. Predict what deleting that parent row does, and say which constraint actually fires.

<details markdown="1"><summary>Hint</summary>

`SET NULL` and `NOT NULL` are both real constraints on the same column, and only one of them can win.

</details>

<details markdown="1"><summary>Check</summary>

The delete fails, with `ERROR: null value in column "parent_id" of relation "childl" violates not-null constraint`, SQLSTATE `23502`, not the foreign key's `23503`. `ON DELETE SET NULL` tries to write `NULL` into `parent_id`, and the column's own `NOT NULL` constraint rejects that write, so the parent survives by accident of a second constraint, not the foreign key's own design.

</details>

5. ▢ `childM (id, parent_id REFERENCES parentM (id) ON DELETE SET DEFAULT)` has no `DEFAULT` clause written on `parent_id` at all. Predict what deleting the referenced parent row leaves in `childM.parent_id`.

<details markdown="1"><summary>Check</summary>

`NULL`. A column with no declared `DEFAULT` has an implicit default of `NULL`, so `SET DEFAULT` without one written behaves exactly like `SET NULL`: the row survives with `parent_id` empty rather than erroring.

</details>

6. ▢ `childN` references `parentN` with `ON DELETE NO ACTION DEFERRABLE INITIALLY IMMEDIATE`, not `INITIALLY DEFERRED`. Predict whether the delete-then-reinsert sequence from this lesson's `NO ACTION` demonstration still succeeds.

<details markdown="1"><summary>Check</summary>

No. `DEFERRABLE` only makes deferring possible; `INITIALLY IMMEDIATE` means the check still runs at the end of each statement unless something later asks for it to be deferred. The `DELETE` alone fails with `23503` before the `INSERT` that would have repaired it ever runs.

</details>

## Real-world reps

- [ ] Pick a foreign key you maintain and find out, without guessing, which of the five `ON DELETE` actions it has, since the unwritten default is `NO ACTION` and a bare column still made a choice.
- [ ] Find code that deletes a parent row then its children in a separate statement, and check whether `ON DELETE CASCADE` would remove the second statement entirely.
- [ ] Tomorrow: find one self-referencing table you know, a category tree, an org chart, a comment thread, and check by hand whether its root row's parent column is nullable.

## Going further

- [SET CONSTRAINTS](https://www.postgresql.org/docs/current/sql-set-constraints.html): defer or immediately check a constraint mid-transaction rather than only at declaration
- [CREATE TABLE](https://www.postgresql.org/docs/current/sql-createtable.html): the full syntax for `REFERENCES` and the constraint clauses this lesson used only a slice of
- [Appendix A. PostgreSQL Error Codes](https://www.postgresql.org/docs/current/errcodes-appendix.html): where 23503, 23001 and 23502 are catalogued
- [Schema design](../reference/schema-design.md): the stage 4 reference sheet
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
