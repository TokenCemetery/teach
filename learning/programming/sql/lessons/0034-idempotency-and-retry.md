---
title: 34. Idempotency and the Retry That Is Correct
description: A retry that replays the same statements reproduces the bug it was meant to fix, so it has to read again and decide again
type: lesson
---

# Lesson 34. Idempotency and the Retry That Is Correct

**Mission link:** A caller that catches a serialization failure and resends the same statements can commit and still land on the wrong number, since succeeding on retry is not the same as deciding again; this lesson separates a retry that repeats a mistake from one that reads and decides afresh.
**Primary source:** [PostgreSQL, 13.2.3 Serializable Isolation Level](https://www.postgresql.org/docs/current/transaction-iso.html)
**Prerequisites:** [Lesson 31](0031-the-anomalies.md), [Lesson 33](0033-deadlocks.md)

## Warm-up

1. ▢ Lesson 31 showed a Serializable commit fail with SQLSTATE `40001`, and lesson 33 shows two transactions each waiting on the other end with SQLSTATE `40P01`. Both mean the transaction that received the error never took effect. What must a caller do with either error that it does not have to do with an ordinary constraint violation?

<details markdown="1"><summary>Check</summary>

Decide whether to run the transaction again. Both codes mean it was refused for a reason unrelated to its own statements, only to what else was running at the same time, so running it again may simply succeed. A caller that only logs the error and gives up throws away work a retry would likely have finished.

</details>

## Know this

### Two errors worth retrying, and one that is not

A serialization failure, SQLSTATE `40001`, is the server protecting a rule it tracks, up to the read/write dependency lesson 31 named write skew. A deadlock, SQLSTATE `40P01`, is the server breaking a cycle of two transactions each waiting on the other's lock, lesson 33's subject. Both share what matters here: the transaction never landed, so nothing is unsafe about sending it again. A duplicate key violation differs in kind, as inserting a row, then a second colliding with it, then retrying the insert, shows:

```sql
INSERT INTO accounts (id, owner, balance) VALUES (3, 'irene', 50.00);
INSERT INTO accounts (id, owner, balance) VALUES (3, 'again', 50.00);
-- ERROR: duplicate key value violates unique constraint "accounts_pkey", DETAIL: Key (id)=(3) already exists., SQLSTATE 23505
INSERT INTO accounts (id, owner, balance) VALUES (3, 'again', 50.00);
-- ERROR: duplicate key value violates unique constraint "accounts_pkey", DETAIL: Key (id)=(3) already exists., SQLSTATE 23505
```

The third attempt fails exactly as the second did: row `3` still exists, so retrying a `23505` is a wasted round trip. Contrast a `40001` from two Serializable transactions that each read the combined balance as `200.00`, then each withdraw `60` from a different row, lesson 31's write skew shape:

```text
A: BEGIN ISOLATION LEVEL SERIALIZABLE;
B: BEGIN ISOLATION LEVEL SERIALIZABLE;
A: SELECT sum(balance) FROM accounts;                     -- 200.00
B: SELECT sum(balance) FROM accounts;                     -- 200.00
A: UPDATE accounts SET balance = balance - 60 WHERE id = 1;
B: UPDATE accounts SET balance = balance - 60 WHERE id = 2;
A: COMMIT;
B: COMMIT;                                                 -- fails, see below
```

```text
ERROR: could not serialize access due to read/write dependencies among transactions
SQLSTATE 40001
```

Session `B` needs no `ROLLBACK` first: the failed `COMMIT` already ended its transaction, unlike an ordinary failed statement, and a fresh `BEGIN` starts cleanly. Session `B` simply resends the update:

```text
B: BEGIN;
B: UPDATE accounts SET balance = balance - 60 WHERE id = 2;
B: COMMIT;                                                 -- succeeds
B: SELECT sum(balance) FROM accounts;                      -- 80.00
```

Unlike the `23505`, this retry succeeds: retrying can change the outcome of a `40001` or a `40P01`, never a `23505`.

### The retry that is wrong

Succeeding is not the same as being right. Both withdrawals were only safe if the combined balance stayed at or above `90.00` afterwards, a rule no row's `CHECK` can see. `A`'s withdrawal alone left `140.00`, well above that floor; `B`'s retry took another `60` without asking again, landing on `80.00`, below it, with no error anywhere: the same wrong total lesson 31 got from Repeatable Read, where nothing catches the rule. Replaying the statements after a `40001` reproduced the very bug the level had just refused.

The fix is a different shape of retry, not a different statement: reset the balances, run the same conflict, and let `B`'s retry ask its question again first:

```text
B: BEGIN;
B: SELECT sum(balance) FROM accounts;                       -- 140.00
B: COMMIT;
B: SELECT sum(balance) FROM accounts;                       -- 140.00, B chose not to withdraw
```

`140.00` minus another `60` is still `80.00`, below the floor, so the retry that re-reads refuses the withdrawal and writes nothing, leaving `140.00`, exactly what `A`'s withdrawal alone should leave. Both had the identical `UPDATE` available; one resent a decision, the other made one. A retry is a re-decision, not a replay.

### The shape of a correct retry

A retry loop that gets this right has four properties, none specific to any driver:

```
attempts = 0
while attempts < max_attempts:
    attempts += 1
    begin transaction
    read whatever the decision needs, inside this transaction
    decide what to write, from what was just read
    write it, and try to commit
    if commit succeeded: stop
    if this attempt's error is not 40001 and not 40P01: raise it, do not retry
    if attempts == max_attempts: raise it, out of attempts
    wait a little before looping, longer after each failure
```

A bounded attempt count stops endless looping against a conflict that never clears. Reads inside the loop, not just the final write, are what the wrong retry skipped, and that is the stale decision that landed on `80.00`. Checking the SQLSTATE first stops a `23505`, or anything resending cannot fix, from wasting an attempt. A growing delay stops two colliding callers retrying in lockstep and colliding again.

### Idempotency, the other half

Everything above is safe to retry because the transaction is atomic, lesson 28's promise, so there is no half-applied write to retry into. A caller talking to anything outside the database has no such promise: the far side may have succeeded while the reply never arrived, and it cannot tell that from a failure. Such an operation has to be written so that calling it twice is harmless, which is idempotency. `INSERT ... ON CONFLICT ... DO NOTHING RETURNING id` is the plainest version, returning the id when it inserted and nothing when it did not:

```sql
INSERT INTO accounts (id, owner, balance) VALUES (7, 'x', 5.00) ON CONFLICT (id) DO NOTHING RETURNING id;
-- id=7, one row: this call did the work
INSERT INTO accounts (id, owner, balance) VALUES (7, 'y', 9.00) ON CONFLICT (id) DO NOTHING RETURNING id;
-- 0 rows: someone, possibly this same caller retrying, already did it
```

`ON CONFLICT ... DO UPDATE` answers a related question, "make it match this," and is just as safe to call twice:

```sql
INSERT INTO accounts (id, owner, balance) VALUES (7, 'z', 40.00) ON CONFLICT (id) DO UPDATE SET owner = excluded.owner RETURNING id, owner, balance;
-- id=7, owner=z, balance=5.00: the row now reads z, and the balance this clause never mentioned was left alone
```

The general pattern is an idempotency key: a unique column holding an identifier the caller generates once and resends on every retry. A repeat then fails on the constraint itself, the same `23505` from the first section, or tells the caller plainly this attempt did not do the work; the safety lives in the schema, not in application code.

### Serialising work that has no row to lock yet

A row lock only works once a row exists, so it offers nothing the moment before that, when two workers are each deciding whether to create a row meant to exist exactly once. Lesson 32 named the tool for that gap, an advisory lock on a number rather than a row, and pointed here for where it gets used. Suppose row `9` is a nightly summary two workers might each try to build:

```text
A: BEGIN;
A: SELECT count(*) FROM accounts WHERE id = 9;               -- 0, does not exist yet
A: SELECT pg_advisory_xact_lock(42);
B: BEGIN;
B: SELECT count(*) FROM accounts WHERE id = 9;                -- 0, B sees the same nothing
B: SELECT pg_advisory_xact_lock(42);                           -- blocks here, waiting on A's advisory lock
A: INSERT INTO accounts VALUES (9, 'nightly', 0.00);
A: COMMIT;
B: SELECT count(*) FROM accounts WHERE id = 9;                 -- 1, now that B holds the lock and re-checks
B: COMMIT;
```

Both found nothing on their first check; without the lock, both would have built row `9`. Holding the same number as A makes B's check wait its turn, and the check B runs once that turn comes is the point: B decides again, sees the row A already built, and never inserts it. Acquiring the lock is not the fix; re-checking after acquiring it is, the same rule as the retry above, applied to a decision rather than a write.

### What no amount of care buys you

Every mechanism above makes one failure recoverable, and none makes the "it worked" message reliable, because that message crosses a boundary the database does not control: a crash between the commit returning and the reply arriving leaves no record of which side failed. Exactly-once delivery across that boundary is not on offer, since no observer sits on both sides to confirm it. What is available is at-least-once delivery paired with an operation that is safe to repeat, which is the whole reason the previous section exists.

### What the stage bought

Lesson 28 split one acronym into three promises kept outright, atomicity, consistency and durability, and one left for you to choose, isolation, and showed a failed transaction aborting outright rather than limping on. Lesson 29's multiversion mechanism gave a reader a snapshot consistent with one moment in a row's history, never shown a writer's unfinished work. Lesson 30 named which of PostgreSQL's three isolation behaviours each level permits. Lesson 31 turned a shape in application code into the name of the anomaly it risks. Lesson 32's row lock claimed a row on one writer's behalf so a second waits rather than races it. Lesson 33 showed why two such waits, each holding what the other wants, end with the database cancelling one rather than let both wait forever. This lesson adds what happens next: not a replay of a decision, but a caller that reads again, decides again, and costs nothing if called twice by accident. The next stage stops asking whether this is correct and asks why a query that already is correct takes as long as it does.

## Practice

1. ▢ The `23505` interleaving in this lesson failed identically twice. Predict what a fourth identical `INSERT` of the same row does, and what would have to change in the table for a retry of it to ever succeed.

<details markdown="1"><summary>Check</summary>

It fails the same way, with the same `23505` and `DETAIL`. Only deleting row `3` or choosing a different id changes that; retries never touch what actually went wrong.

</details>

2. ▢ Suppose the shared rule only required the total to stay at or above `50.00`, not `90.00`. Session `B` retries by resending its `UPDATE` without re-reading anything, and the balance lands on `80.00`, satisfying that looser rule. Predict whether this retry was actually correct.

<details markdown="1"><summary>Hint</summary>

Ask what the retry itself checked before writing, not what the number happened to come out to on this run.

</details>

<details markdown="1"><summary>Check</summary>

No, still wrong, even though the number happened to be safe. It never read the total or asked whether `60.00` was still safe to take; it got lucky. A rule change, or a third session withdrawing meanwhile, would let the same retry commit a forbidden total, with no error anywhere, because the method never checked at all.

</details>

3. ▢ A transaction fails with `40P01` rather than `40001`, and its only write was `UPDATE accounts SET balance = balance - 10 WHERE id = 1`, with no earlier read of `balance` in that transaction. Predict whether resending it unchanged is a safe retry.

<details markdown="1"><summary>Hint</summary>

The wrong retry in this lesson was wrong because a value read earlier in the transaction was reused after the world had moved on; ask whether this statement reuses any such value.

</details>

<details markdown="1"><summary>Check</summary>

Yes, safe to resend. `balance - 60` and `balance - 10` are expressions evaluated against whatever the row holds when the statement runs, not a value read earlier and carried forward, so there is no stale decision to replay. The danger here was never the SQLSTATE; it was a write depending on a fact read earlier in the same attempt.

</details>

4. ▢ Predict what `INSERT INTO accounts (id, owner, balance) VALUES (7, 'x', 5.00) ON CONFLICT (id) DO NOTHING RETURNING id` returns on a third call, after the first returned the id and the second returned no rows.

<details markdown="1"><summary>Check</summary>

No rows, exactly as the second call did. Nothing about row `7` changes between attempts, so the clause keeps reporting the same fact: something else already did this.

</details>

5. ▢ Session `A` holds `pg_advisory_xact_lock(42)`. Predict what session `B`'s `SELECT pg_try_advisory_xact_lock(43)` returns while `A`'s transaction is still open.

<details markdown="1"><summary>Check</summary>

It returns `t` immediately. An advisory lock is keyed on the number itself, not any table or row, so a lock on `42` says nothing about `43`; the two callers would have to agree on the same number to contend at all.

</details>

6. ▢ A payment commits on the server, but the network drops before the caller receives the reply, and the caller resends the identical call with the same idempotency key. Predict what it sees, given the `DO NOTHING RETURNING id` pattern.

<details markdown="1"><summary>Check</summary>

No rows back from the resend, telling the caller the payment already happened rather than leaving it to guess. The lost reply is exactly the gap idempotency covers: the caller cannot tell success from failure alone, so the schema answers the second call instead.

</details>

## Real-world reps

- [ ] Find a retry loop in code you maintain and check whether the whole transaction, reads included, sits inside the retried block, or only the final write does.
- [ ] Open two sessions of your own and run this lesson's write skew retry by hand, once resending the update unchanged and once re-reading the total first, to see the two final balances for yourself.
- [ ] Tomorrow: find one operation in your own code a caller might legitimately call twice, a payment, a webhook handler, a job worker, and check whether calling it twice does anything different from calling it once.

## Going further

- [13.2.3. Serializable Isolation Level](https://www.postgresql.org/docs/current/transaction-iso.html#XACT-SERIALIZABLE): the retry advice this lesson followed
- [ON CONFLICT Clause](https://www.postgresql.org/docs/current/sql-insert.html#SQL-ON-CONFLICT): the syntax behind every idempotent insert above
- [13.3.5. Advisory Locks](https://www.postgresql.org/docs/current/explicit-locking.html#ADVISORY-LOCKS): the mechanism used here for a row that does not exist yet
- [Appendix A. PostgreSQL Error Codes](https://www.postgresql.org/docs/current/errcodes-appendix.html): where `40001`, `40P01` and `23505` are catalogued
- [Transactions](../reference/transactions.md): the stage 5 reference sheet
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
