---
title: 43. Changing What Already Has Data
description: A constraint on a full table is two statements, and a backfill is a loop rather than one UPDATE
type: lesson
---

# Lesson 43. Changing What Already Has Data

**Mission link:** A senior engineer is asked to add a rule to a table that has already broken it, or move rows into a new shape, without the application going down; treating either as one statement rather than a sequence of cheap and expensive steps is how a routine change becomes an incident.
**Primary source:** [PostgreSQL, ALTER TABLE](https://www.postgresql.org/docs/current/sql-altertable.html)
**Prerequisites:** [Lesson 24](0024-constraints-that-hold.md), [Lesson 42](0042-migrations-without-downtime.md)

## Warm-up

1. ▢ Lesson 24 gave the three-step story for adding a `CHECK` constraint to a table that already has data: add it `NOT VALID`, which enforces the rule on new writes at once; then run `VALIDATE CONSTRAINT`, which scans the existing rows once. What does the `NOT VALID` statement itself never do to the rows already there?

<details markdown="1"><summary>Check</summary>

It never reads them. `NOT VALID` starts enforcing the rule against anything written from that moment on, but skips the scan that would check the rows already sitting in the table. That scan is exactly what `VALIDATE CONSTRAINT` does later, on its own.

</details>

## Know this

### A constraint on a table that already has data, priced as two statements

`add constraint balance_nonneg check (balance >= 0) not valid` succeeds at once, `pg_constraint.convalidated` reads `f`, and a violating insert is refused immediately, before anything is validated. `validate constraint balance_nonneg` then scans the table once and flips it to `t`. Holding each open and watching a second session showed why the split exists: `not valid` took `AccessExclusiveLock`, and an ordinary `select count(*)` blocked behind it until commit; `validate constraint` took `ShareUpdateExclusiveLock` instead, and an ordinary `update` went straight through while it ran. The statement that queues every reader and writer is also the fast, metadata-only one, so it fits in a deploy unnoticed; the one that walks the table and can take real time leaves reads and writes alone, so it runs separately, whenever suits.

### The same shape for a foreign key, with a lighter first lock

`add constraint ... foreign key (customer_id) references customers_ref (id) not valid`, then `validate constraint`, behave the same way: `convalidated` reads `f`, then `t`. The lock differs, and the documentation says why: "Although most forms of `ADD table_constraint` require an `ACCESS EXCLUSIVE` lock, `ADD FOREIGN KEY` requires only a `SHARE ROW EXCLUSIVE` lock." Holding the foreign key's `NOT VALID` open confirmed both halves: an ordinary `select` went through unblocked, but an `insert` into the referencing table blocked until commit. A lighter lock means fewer things wait, not nothing: `SHARE ROW EXCLUSIVE` still conflicts with an insert or update's lock, just not with a plain read the way `ACCESS EXCLUSIVE` does. `VALIDATE CONSTRAINT` again took the weaker `ShareUpdateExclusiveLock`, and an insert proceeded while it ran. Validation reads every row because the constraint promises something about every row, which cannot be taken on faith for rows that existed before the promise did.

### `SET NOT NULL` on a column that already has rows

`alter column email set not null`, against a column genuinely holding a null, fails at once: `ERROR: column "email" of relation "contacts" contains null values`, `SQLSTATE 23502`. The way through reuses the shape above: backfill the nulls, add `check (email is not null) not valid`, validate it, then run `set not null`, which now succeeds. Release 12's notes are worth quoting rather than paraphrasing: "Allow `ALTER TABLE ... SET NOT NULL` to avoid unnecessary table scans", because "this can be optimized when the table's column constraints can be recognized as disallowing nulls." Once a validated constraint already proves no row is null, `SET NOT NULL` need not scan the table again to prove it. This is the one claim taken from the notes rather than a run: showing a scan was skipped needs a timing, and stage 6's rule is that a timing is not a portable count. The technique is verified; the saving is quoted, not measured.

### The backfill, written as a loop rather than one statement

A single `update widgets set status = 'new', touched = touched + 1` across two hundred thousand rows, run inside an open transaction, held a lock on every row touched until commit: a second session's update on one row from the middle of the table, nowhere near a boundary, blocked for the full duration, lesson 32's row lock. `pg_stat_user_tables.n_dead_tup` read `0` before and `200000` right after committing, one dead row version per row touched, all at once, lessons 29 and 41's dead versions. Making one row fail a `CHECK` partway through a similar update rolled the whole statement back: every row read its original value afterwards, lesson 28's atomicity. A batched version avoids all three by touching a bounded key range and committing after each one:

```sql
update widgets3
   set status = 'new', touched = touched + 1
 where id > 40000 and id <= 60000;
```

Half-open, contiguous ranges, each starting where the last left off, cover every row once: a ten-batch run of twenty thousand rows each left all two hundred thousand rows with `touched` equal to `1`, none skipped or doubled. Three reasons follow. Locks last one batch's duration: the same blocking check against the batched version showed a row from an already-committed batch update immediately, while a row inside the open batch still blocked. Dead versions total the same, but arrive as smaller waves a vacuum clears between batches rather than one spike. If a batch fails, only that batch rolls back; the ones already committed keep their work.

### Renaming, and why it takes two deploys

`rename column full_name to display_name` is instant and takes `AccessExclusiveLock`, confirmed the same way: held open, it blocked an ordinary `select` until commit, though the hold is normally momentary since renaming touches only a catalog entry. The real cost is not the lock: a rename in one step changes what every running instance must call the column at the same moment, and a deploy never replaces every instance at once. Querying the old name afterwards failed with `ERROR: column "full_name" does not exist`, `SQLSTATE 42703`, the error whichever half of a mixed deploy is behind would hit. The safe sequence uses a new column as the compatibility layer instead, the same shape this stage's community catalogue documents, a secondary source since it is a Ruby library's own documentation:

1. Deploy 1 (database): add `display_name`, backfill it from `full_name` with the batched technique above, and add a trigger copying any write to `full_name` onto `display_name`, so undeployed code keeps writing the old column while the new one stays correct underneath. Lesson 42's version of this step has the application write both columns instead, and the choice between the two is about who you can change: a trigger needs no deploy and keeps working for code you do not control, and application dual-writes are easier to read and to remove, so reach for the trigger when clients are outside your release, and for dual-writes when they are not.
2. Application deploy: ship code reading and writing `display_name` only. Not a schema change; deploy 1 already keeps both columns identical, so old and new code run side by side safely, and this step rolls back on its own.
3. Deploy 2 (database): once nothing touches `full_name`, drop the sync trigger and the column.

Step 1 is reversible: dropping the trigger, its function and `display_name` again left `full_name` exactly as it was, verified directly. Step 3 is not: once `full_name` is gone, undoing it means re-adding it and repeating the backfill, not one statement.

### The rollback question

Some steps reverse cleanly: dropping a `NOT VALID` constraint, or the compatibility column and trigger above, returns the table to what it was. A completed backfill or a finished rewrite of a column's meaning mostly does not: once the old shape is gone, no single statement recreates the earlier state, only a restore or the batches run in reverse where the transform allows it. The honest plan is forward-only steps, each safe to stop after, rather than one change promising to be undone as a unit. Judging whether a sequence has that property is lesson 45's subject.

## Practice

1. ▢ A `CHECK` and a foreign key are each added `NOT VALID` in their own open, uncommitted transaction. A third session runs an ordinary `select` against each table. Predict which select blocks.

<details markdown="1"><summary>Check</summary>

Only the `CHECK` table's select blocks: plain `NOT VALID` takes `AccessExclusiveLock`, which conflicts with any lock. Adding a foreign key takes the weaker `ShareRowExclusiveLock`, which does not conflict with an ordinary read.

</details>

2. ▢ A colleague says adding a foreign key `NOT VALID` "won't block anything, reads go straight through." Say in one sentence what their check missed.

<details markdown="1"><summary>Hint</summary>

They tested a `SELECT`. What kind of statement takes the lock mode `SHARE ROW EXCLUSIVE` actually conflicts with?

</details>

<details markdown="1"><summary>Check</summary>

Reads go through, but writes do not: `ShareRowExclusiveLock` still conflicts with the lock an `INSERT`, `UPDATE` or `DELETE` takes, so any write queues until the constraint statement commits.

</details>

3. ▢ A column holds three null rows. Predict what `SET NOT NULL` does if run directly, without a backfill or a preceding validated constraint.

<details markdown="1"><summary>Check</summary>

It fails at once with `SQLSTATE 23502`, "contains null values". The column must be genuinely free of nulls, or already covered by a validated constraint that proves it, before `SET NOT NULL` succeeds.

</details>

4. ▢ An `UPDATE` touching every row of a large table is still open in an uncommitted transaction. A second session updates one row from the middle of the table, nowhere near any boundary. Predict whether it blocks.

<details markdown="1"><summary>Hint</summary>

The open transaction did not stop partway through any row; what does it hold on every row it already wrote a new version for?

</details>

<details markdown="1"><summary>Check</summary>

It blocks. The open transaction holds a row lock on every row it touched, not only the ones near wherever it currently is, so any already-rewritten row stays locked until commit.

</details>

5. ▢ A batched backfill of ten batches fails on batch eight. Say in one sentence how that differs from the same failure inside one single `UPDATE` covering all the rows.

<details markdown="1"><summary>Check</summary>

The first seven batches keep their committed work and only batch eight rolls back, whereas a single statement would have rolled all of it back, including the work equivalent to those seven.

</details>

6. ▢ A rename adds a new column, backfills it, adds a trigger keeping it in sync, then later drops the old column once every instance is off it. Predict which step, adding the column and trigger or dropping the old column, is reversible, and why.

<details markdown="1"><summary>Check</summary>

Adding the column and trigger is reversible: dropping them again returns the table to its original shape, since the old column was never touched. Dropping the old column is not: undoing it means re-adding it and repeating the backfill, not one statement.

</details>

## Real-world reps

- [ ] Find a column on a table you maintain that already holds rows, and write out the `NOT VALID` and `VALIDATE CONSTRAINT` pair you would run against it, without running either.
- [ ] Look at a migration that renamed a column or table directly, in one step, and say whether a mid-deploy instance on the previous code would have broken against it.
- [ ] Tomorrow: take a job that updates many rows in one statement, and rewrite it as a batched loop over a keyed range, checking the ranges cannot skip or repeat a row.

## Going further

- [ADD table_constraint [ NOT VALID ]](https://www.postgresql.org/docs/current/sql-altertable.html#SQL-ALTERTABLE-DESC-ADD-TABLE-CONSTRAINT): the lock note quoted above about `CHECK` versus foreign-key constraints
- [E.23. Release 12](https://www.postgresql.org/docs/12/release-12.html): the `SET NOT NULL` scan-avoidance note, taken from the notes rather than a run
- [53.13. pg_locks](https://www.postgresql.org/docs/current/view-pg-locks.html): the view used above to see which lock each statement took
- [Renaming a column](https://github.com/ankane/strong_migrations#renaming-a-column): the community catalogue's version of the same compatibility-column sequence, a secondary source since it documents a Ruby library
- [Operating](../reference/operating.md): the stage 7 reference sheet
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
