---
title: 45. Reviewing a Schema Change
description: Ask what the migration locks, what it rewrites, and what runs while both versions of the code are live
type: lesson
---

# Lesson 45. Reviewing a Schema Change

**Mission link:** A senior engineer is the one asked to approve someone else's migration before it reaches a table with real traffic on it, and the difference between approving it and causing the next outage is five specific questions asked before it runs, not a feeling that the diff looks fine.
**Primary source:** [PostgreSQL, ALTER TABLE](https://www.postgresql.org/docs/current/sql-altertable.html)
**Prerequisites:** [Lesson 42](0042-migrations-without-downtime.md), [Lesson 43](0043-changing-what-has-data.md)

## Warm-up

1. ▢ Lesson 42 showed one long-running transaction plus one `ALTER TABLE` statement enough to queue every later read behind it, and that the statement itself never had to be slow. If a migration's statement completes in ten milliseconds once it starts running, does that rule out an outage?

<details markdown="1"><summary>Check</summary>

No. It rules out only the statement being slow to execute once it holds its lock; it says nothing about how long it waited to acquire that lock, or how long everything else queued behind it while it held one. Ten milliseconds of execution can sit inside minutes of queueing on either side, which is why this lesson's first question is about the lock, not the statement's speed.

</details>

## Know this

### The five questions, and why five

A migration review answers five questions, in this order: what lock does each statement take, and for how long; does anything rewrite the table or scan it; what happens while both the old and the new application code are running against it; what is the rollback, and is each step safe to stop after; and what does this cost at the size the table will actually be. Five, not fifteen, because each has produced an outage the other four would have let through: a statement that rewrites nothing can still queue every reader behind a lock it holds for an hour, which is question one and lesson 42's subject; one with the mildest lock available can still stall a pool by scanning ten million rows, question two; one that runs perfectly can still break the half of the fleet still running yesterday's code, question three; one that rolls forward cleanly can leave a table half backfilled with no way back if it is killed partway, question four; and one that passed review against a thousand rows can hold an exclusive lock for forty minutes against the table it actually ships to, question five. Longer checklists exist; this one fits in your head while reading someone else's pull request, which is the only place it does any good. None of the five is about whether the query behind the change is any good, which is lesson 44's job; every example below changes the schema itself, never a query against it.

### Three migrations, and what each one breaks

Three migrations follow, each with one defect, each run against a real table so the evidence is a count or an error rather than a guess.

```sql
-- Migration 1: add a column that records when each row was created
1. ALTER TABLE accounts ADD COLUMN created_at timestamptz NOT NULL DEFAULT clock_timestamp();  -- one deploy, one statement
```
```text
pg_relation_filenode('accounts') before this statement, then after: changed
-- a rewrite, exactly as ALTER TABLE's own documentation warns for a volatile default such as
-- clock_timestamp(), which has to be evaluated separately for every row rather than stored once;
-- every row was copied under the ACCESS EXCLUSIVE lock ALTER TABLE always takes, for as long as the copy took
```

Review: this rewrites the table for the volatile default; the lock is brief on a small table, but the review is written for the table this becomes. Split the column out instead: add it nullable in one deploy, backfill it the way lesson 43 backfills any populated column, and add the default and constraint in a second deploy once every row has a value.

```sql
-- Migration 2: index a column that a report now filters on
1. CREATE INDEX idx_payments_status ON payments (status);  -- one deploy, inside the migration framework's default transaction
```
```text
a second session's concurrent UPDATE against payments: blocked until this statement's transaction commits
-- matches CREATE INDEX's own documentation on what CONCURRENTLY exists to avoid: "a standard index
-- build locks out writes (but not reads) on the table until it's done"; bolting CONCURRENTLY onto the
-- same statement without telling the framework to skip its transaction wrapper fails instead of blocking:
ERROR:  CREATE INDEX CONCURRENTLY cannot run inside a transaction block
SQLSTATE: 25001
```

Review: either this blocks every write to `payments` for as long as the build takes, or it never runs at all. This needs to be its own deploy, outside a transaction, the way lesson 42 covers.

```sql
-- Migration 3: a plan a customer must always have gets enforced
1. ALTER TABLE subscriptions ALTER COLUMN plan_id SET NOT NULL;  -- one deploy, one statement
```
```text
ERROR:  column "plan_id" of relation "subscriptions" contains null values
SQLSTATE: 23502
-- against a column where a cohort of legacy rows still holds nulls; clean those up and it succeeds,
-- but a concurrent SELECT is blocked until it commits, since it takes the same ACCESS EXCLUSIVE lock
-- as any other ALTER TABLE by default, whether or not it fails, and its documentation says why:
-- "adding a CHECK or NOT NULL constraint requires scanning the table to verify that existing rows meet the constraint"
```

Review: this either fails outright or holds a table-wide lock for as long as the scan takes, and neither is a step to run in one shot against a live table. Validate the invariant first, the way lesson 43 does it, and flip the column only once nothing can disagree with the flip.

### The same three, made safe

```sql
-- Migration 1, rewritten
1. ALTER TABLE accounts ADD COLUMN created_at timestamptz;             -- deploy 1, nullable, confirmed no rewrite
2. UPDATE accounts SET created_at = now() WHERE created_at IS NULL;    -- background, batched per lesson 43; both code versions run here
3. ALTER TABLE accounts ALTER COLUMN created_at SET DEFAULT now();
   ALTER TABLE accounts ALTER COLUMN created_at SET NOT NULL;          -- deploy 2, once step 2 has reached every row
```

Step 1 does not rewrite anything, since there is no default to evaluate. Step 2 is the batched backfill lesson 43 covers, not repeated here. Step 3 is safe only once step 2 has genuinely reached every row.

```sql
-- Migration 2, rewritten
1. CREATE INDEX CONCURRENTLY idx_payments_status ON payments (status);  -- its own deploy, run outside any transaction
```

Run this way, `pg_index` reports the index valid and ready. Nothing here touches application code, so no window exists where two versions of it disagree.

```sql
-- Migration 3, rewritten
1. ALTER TABLE subscriptions ADD CONSTRAINT plan_id_not_null CHECK (plan_id IS NOT NULL) NOT VALID;  -- deploy 1
2. ALTER TABLE subscriptions VALIDATE CONSTRAINT plan_id_not_null;                                    -- background
3. ALTER TABLE subscriptions ALTER COLUMN plan_id SET NOT NULL;
   ALTER TABLE subscriptions DROP CONSTRAINT plan_id_not_null;                                        -- deploy 2
```
```text
step 1: a concurrent SELECT returns the moment this statement's own transaction closes -- ACCESS EXCLUSIVE,
        but held for an instant, since NOT VALID skips checking existing rows, not a scan
step 2: blocks neither a concurrent SELECT nor UPDATE at all -- a weaker lock than either other step,
        the entire point of splitting the work this way, and lesson 43's mechanic, cited rather than re-taught
```

Step 3 still takes the same lock the unsafe version did; whether it still has to scan once the constraint is validated is a claim this lesson takes from lesson 43 and the release note it cites, not from a run, since proving it needs a timing rather than a count.

### What to ask for when you cannot run it

Most reviews are read, not run against a copy of production. Four questions cover most of what running the five would tell you, each a sentence to paste directly into a review:

- What is the row count and on-disk size of this table today, and what will it be by the time this migration runs?
- What lock does each statement here take, and roughly how long will it hold that lock?
- Does any statement rewrite the table or scan it?
- If this has to stop halfway through, what state does that leave things in, and what is the plan to resume or roll back?

An author usually knows all four already, and a reviewer who cannot get an answer to the fourth has found a defect regardless of the other three.

### A migration that is fine

Not every migration needs this treatment, and a review method that never approves anything has stopped discriminating between safe and unsafe. Take `ALTER TABLE accounts ADD COLUMN note text;`: question one, the usual `ACCESS EXCLUSIVE` lock, but for the length of a catalogue update, confirmed because the table's filenode is exactly what it was before, since a nullable column with no default touches no existing row. Question two, no rewrite and nothing to scan, for the same reason. Question three, old code ignores a column it has never heard of, and new code can write to it the moment it deploys, with no row either version reads wrongly. Question four, the rollback is `DROP COLUMN note`, with no partial state to land in, since the statement either finishes or it does not. Question five, the cost at any size is the same catalogue update, proportional to nothing about the row count. Five harmless answers, not a feeling that the change looks simple, is what makes a migration fine, and this one is approved.

### The reviewer's own failure mode

The failure mode on the other side is blocking a migration because it is unfamiliar rather than unsafe: a syntax the reviewer has not seen, a constraint type they have not used, a name that does not match house style. The discipline against it is the one used throughout this lesson, refusing to write a review comment that does not name a concrete thing. "This makes me uneasy" blocks nothing worth blocking and lets through what actually is unsafe; "this takes `ACCESS EXCLUSIVE` and the table is forty million rows" is a comment its author can act on, and a reviewer who cannot write that sentence has no basis yet for saying no.

## Practice

1. ▢ A migration adds a column with `DEFAULT gen_random_uuid()`. Predict, using this lesson's second question, whether it rewrites the table, and say what you would check to confirm it.

<details markdown="1"><summary>Hint</summary>

A function that must return something different on every call cannot be marked anything other than volatile.

</details>

<details markdown="1"><summary>Check</summary>

It rewrites the table. A UUID generator produces a fresh value per row, volatile exactly as `clock_timestamp()` is, and `ALTER TABLE`'s documentation treats any volatile default the same way. Checking `pg_relation_filenode` before and after, or the function's listed volatility in `pg_proc`, confirms it without timing anything.

</details>

2. ▢ A migration framework wraps every migration in a transaction by default. A colleague submits `CREATE INDEX CONCURRENTLY idx_orders_status ON orders (status);` as the entire migration, run through that framework unchanged. Predict what happens, and name the SQLSTATE.

<details markdown="1"><summary>Check</summary>

It fails immediately with `ERROR: CREATE INDEX CONCURRENTLY cannot run inside a transaction block`, SQLSTATE `25001`, since `CONCURRENTLY` cannot run inside a transaction block and the framework wraps every migration in one. The fix is telling the framework to run this migration outside that wrapper, not merely adding `CONCURRENTLY`.

</details>

3. ▢ Two migrations add a `NOT NULL` column to a live table. Migration A gives it `DEFAULT 0`; migration B gives it `DEFAULT random()`. Predict which rewrites the table, using this lesson's second question, and say what evidence would confirm it without timing anything.

<details markdown="1"><summary>Hint</summary>

`0` is a constant; `random()` has to be evaluated separately for every row.

</details>

<details markdown="1"><summary>Check</summary>

Migration B rewrites the table. A constant default such as `0` is stored once in the table's metadata and applied lazily when a row is read, so nothing is rewritten, while `random()` must be computed per row immediately, forcing a rewrite. `pg_relation_filenode`, taken before and after each statement, confirms it: unchanged for A, changed for B.

</details>

4. ▢ A migration renames a column in one deploy: `ALTER TABLE customers RENAME COLUMN email TO email_address;`. Say, in one sentence, what breaks and why, using this lesson's third question.

<details markdown="1"><summary>Check</summary>

Whichever instances still run the previous version break, since they still query `email`, which stops existing the instant this statement commits; a rename needs two deploys, adding the new name and moving every reader and writer across before dropping the old one, lesson 43's mechanic for it.

</details>

5. ▢ A migration backfills a new column with one unbatched `UPDATE accounts SET tier = 'standard' WHERE tier IS NULL;` against a table with several million rows. Without repeating lesson 43's own measurement of this, say what this lesson's fourth and fifth questions would flag.

<details markdown="1"><summary>Hint</summary>

One statement that touches millions of rows either finishes in full or it does not; there is no statement half-run in a log.

</details>

<details markdown="1"><summary>Check</summary>

Question five flags the cost: writing millions of new row versions inside one transaction takes however long that takes. Question four flags the rollback: it is one all-or-nothing statement, with no safe point to stop after partway, only before it starts or after it entirely finishes.

</details>

6. ▢ Predict which of the five questions a migration that only adds a nullable column with no default answers harmlessly on every count, and say why a review method needs at least one migration like this to be worth trusting.

<details markdown="1"><summary>Check</summary>

All five: a brief `ACCESS EXCLUSIVE` lock, no rewrite or scan, nothing for either code version to disagree about, a clean single-statement rollback, and a cost that does not grow with the table's size. A review method that never says yes has stopped discriminating between safe and unsafe, so it needs cases exactly like this one to prove it can approve as well as block.

</details>

## Real-world reps

- [ ] Pick a migration you or a teammate wrote recently and answer this lesson's five questions about it in writing, even if it already shipped.
- [ ] Find one `ALTER TABLE` or `CREATE INDEX` statement in a pending change and check what lock it takes and whether it rewrites or scans before you approve it.
- [ ] Tomorrow: the next time you review a schema change, write the review comment before deciding whether to approve it, and check that it names a lock, a row count or a deploy boundary rather than a feeling.

## Going further

- [13.3.1. Table-Level Locks](https://www.postgresql.org/docs/current/explicit-locking.html#LOCKING-TABLES): the lock modes behind this lesson's first question, and which statement takes which
- [Building Indexes Concurrently](https://www.postgresql.org/docs/current/sql-createindex.html#SQL-CREATEINDEX-CONCURRENTLY): the note behind the second migration's defect, that a standard index build locks out writes but not reads
- [strong_migrations](https://github.com/ankane/strong_migrations): the maintained catalogue this lesson's three defects are drawn from, a Ruby library's documentation whose catalogue travels though its code does not
- [Operating](../reference/operating.md): the stage 7 reference sheet
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
