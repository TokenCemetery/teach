---
title: 31. The Anomalies, and How to Recognise Yours
description: Every concurrency bug has a name, and naming it tells you which level or lock would have prevented it
type: lesson
---

# Lesson 31. The Anomalies, and How to Recognise Yours

**Mission link:** A review that spots a race only after production loses an update has found the bug the expensive way; the useful version recognises the shape in the diff before it ships, because every anomaly here has a name, a known cause, and a known fix. This lesson is the lookup table: read the shape, name the anomaly, pick the defence.
**Primary source:** [PostgreSQL, 13.2.3 Serializable Isolation Level](https://www.postgresql.org/docs/current/transaction-iso.html)
**Prerequisites:** [Lesson 30](0030-isolation-levels.md), [Lesson 29](0029-mvcc.md)

## Warm-up

1. ▢ Lesson 30 ran a lost update at Read Committed, where two sessions read the same balance and one write vanishes with no error, then ran the same statements at Repeatable Read, where the second write fails with a SQLSTATE the moment the first session commits. Only the level changed. What does that say about where the fix for a lost update lives?

<details markdown="1"><summary>Check</summary>

Not in the application's arithmetic, since both runs sent the same `SELECT` then `UPDATE`; the fix is in which guarantee the transaction asked for. Raising the level turned a silent overwrite into a loud, catchable error, which is why this lesson is organised around levels and named defences rather than code changes.

</details>

## Know this

### The read-modify-write shape, and the lost update it hides

Almost every lost update starts as ordinary code: read a value, compute from it in the application, write the result back. Two sessions running that shape against the same row at Read Committed:

```text
A: BEGIN ISOLATION LEVEL READ COMMITTED;
B: BEGIN ISOLATION LEVEL READ COMMITTED;
A: SELECT balance FROM accounts WHERE id = 1;     -- 100.00
B: SELECT balance FROM accounts WHERE id = 1;     -- 100.00
A: UPDATE accounts SET balance = 100.00 - 10 WHERE id = 1;
B: UPDATE accounts SET balance = 100.00 - 20 WHERE id = 1;   -- blocks here, waiting on A's row lock
A: COMMIT;
B: UPDATE accounts SET balance = 100.00 - 20 WHERE id = 1;   -- unblocks, lands against A's committed row
B: COMMIT;
A: SELECT balance FROM accounts WHERE id = 1;     -- 80.00, A's -10 is gone
```

The dangerous part is not that B overwrites A, it is that nothing here raises an error: B's write blocks, then succeeds once A commits, landing a balance already stale. A reviewer looking for a crash or a message finds neither.

Four defences remove this shape; two are worth running here. The first turns the read-modify-write into one statement, leaving no read for a second write to go stale against:

```text
A: BEGIN;
B: BEGIN;
A: UPDATE accounts SET balance = balance - 10 WHERE id = 1;
B: UPDATE accounts SET balance = balance - 20 WHERE id = 1;   -- blocks here, waiting on A's row lock
A: COMMIT;
B: UPDATE accounts SET balance = balance - 20 WHERE id = 1;   -- unblocks, recomputes from the row A just committed
B: COMMIT;
A: SELECT balance FROM accounts WHERE id = 1;     -- 70.00, both decrements landed
```

`balance = balance - 10` is evaluated against whatever row is there once the lock is free, so B's decrement applies on top of A's, and 100 minus 10 minus 20 is exactly 70 with nothing lost. This is the strongest fix, because it deletes the shape rather than guarding it.

The second worth running is a version column, for when the application must stay in the loop. One column added once, `ALTER TABLE accounts ADD COLUMN version int NOT NULL DEFAULT 0`, and every write both checks and advances it:

```text
A: BEGIN;
B: BEGIN;
A: SELECT balance, version FROM accounts WHERE id = 1;   -- 100.00, 0
B: SELECT balance, version FROM accounts WHERE id = 1;   -- 100.00, 0
A: UPDATE accounts SET balance = 100.00 - 10, version = version + 1 WHERE id = 1 AND version = 0 RETURNING id;   -- id 1
A: COMMIT;
B: UPDATE accounts SET balance = 100.00 - 20, version = version + 1 WHERE id = 1 AND version = 0 RETURNING id;   -- 0 rows, version has already moved
B: COMMIT;
A: SELECT balance, version FROM accounts WHERE id = 1;   -- 90.00, 1: only A's write landed
```

B's `UPDATE` commits without error, but matches nothing, because `version` moved to `1` the instant A committed and B is still asking for `version = 0`. Zero rows updated is the signal that someone moved the row first, and the application must check that count rather than assume success. The other two defences are named, not re-run: Repeatable Read, which lesson 30 showed turns the update into `40001` instead, handled by retrying; and a row lock taken while reading, `SELECT ... FOR UPDATE`, lesson 32's subject, used here only by name.

### Read skew, the one without a familiar name

A non-repeatable read, lesson 30's subject, is one row read twice with different answers. Read skew is two different rows, each read once in the same transaction, each individually correct and mutually impossible: reading account 1 before a transfer and account 2 after it sees money that was never in both places at once.

```text
A: BEGIN ISOLATION LEVEL READ COMMITTED;
A: SELECT balance FROM accounts WHERE id = 1;     -- 100.00
B: BEGIN;
B: UPDATE accounts SET balance = balance - 50 WHERE id = 1;
B: UPDATE accounts SET balance = balance + 50 WHERE id = 2;
B: COMMIT;
A: SELECT balance FROM accounts WHERE id = 2;     -- 150.00
A: COMMIT;
```

A never queried a total, but adding these two reads gives 250.00, while the real total, throughout the transfer, is always 200.00. At Repeatable Read the same interleaving keeps A's pair consistent: the second read still returns 100.00, since A's snapshot is fixed at the transaction's start, and only a read after A commits shows 150.00.

```text
A: BEGIN ISOLATION LEVEL REPEATABLE READ;
A: SELECT balance FROM accounts WHERE id = 1;     -- 100.00
B: BEGIN;
B: UPDATE accounts SET balance = balance - 50 WHERE id = 1;
B: UPDATE accounts SET balance = balance + 50 WHERE id = 2;
B: COMMIT;
A: SELECT balance FROM accounts WHERE id = 2;     -- 100.00, still A's snapshot
A: COMMIT;
A: SELECT balance FROM accounts WHERE id = 2;     -- 150.00, now that A has committed
```

### Write skew, the anomaly no per-row rule could have caught

Lesson 24 closed with a limit it could not yet answer: a rule holding across several rows at once is a shape a single `CHECK` was never built to see. Write skew is that limit made concrete. Two transactions each read the total of both accounts, see 200.00, and each independently decides withdrawing 60 from a different row is safe, since the total covers it.

```text
A: BEGIN ISOLATION LEVEL REPEATABLE READ;
B: BEGIN ISOLATION LEVEL REPEATABLE READ;
A: SELECT sum(balance) FROM accounts;             -- 200.00
B: SELECT sum(balance) FROM accounts;             -- 200.00
A: UPDATE accounts SET balance = balance - 60 WHERE id = 1;
B: UPDATE accounts SET balance = balance - 60 WHERE id = 2;
A: COMMIT;
B: COMMIT;
A: SELECT sum(balance) FROM accounts;             -- 80.00
```

Both commit. Each row's own `CHECK (balance >= 0)` still holds, 40.00 each, so no per-row constraint had grounds to object; the broken rule was about the two rows together, which Repeatable Read cannot see. Serializable can, because it tracks read-write dependencies between transactions rather than row versions alone:

```text
A: BEGIN ISOLATION LEVEL SERIALIZABLE;
B: BEGIN ISOLATION LEVEL SERIALIZABLE;
A: SELECT sum(balance) FROM accounts;             -- 200.00
B: SELECT sum(balance) FROM accounts;             -- 200.00
A: UPDATE accounts SET balance = balance - 60 WHERE id = 1;
B: UPDATE accounts SET balance = balance - 60 WHERE id = 2;
A: COMMIT;
B: COMMIT;                                        -- fails, see below
A: SELECT sum(balance) FROM accounts;             -- 140.00, only A's withdrawal landed
```

```
ERROR: could not serialize access due to read/write dependencies among transactions
DETAIL: Reason code: Canceled on identification as a pivot, during commit attempt.
HINT: The transaction might succeed if retried.
```

SQLSTATE `40001`, the same code Repeatable Read raises for a lost update: catch it and retry.

### A phantom, briefly

A phantom is not a row that changed, it is a row not there to be read the first time: a count of matching rows taken twice in one transaction changes when a row is inserted and committed in between:

```text
A: BEGIN ISOLATION LEVEL READ COMMITTED;
A: SELECT count(*) FROM accounts WHERE balance >= 50;   -- 2
B: INSERT INTO accounts VALUES (3, 'irene', 60.00);
B: COMMIT;
A: SELECT count(*) FROM accounts WHERE balance >= 50;   -- 3
A: COMMIT;
```

A row lock cannot be the defence here: `SELECT ... FOR UPDATE` locks rows that exist, and the row ruining the count did not exist when A's first query ran, so it returns zero rows and takes no lock at all. The defence has to be about the predicate as a whole, `SERIALIZABLE`'s predicate locking, lesson 32's territory, rather than an ordinary row lock.

### The recognition table

| Anomaly | Shape in code | Interleaving, in one clause | Prevented by | Diagnostic if it errors |
|---|---|---|---|---|
| Lost update | read, compute, write back | B overwrites A's committed value | one statement, a version column, Repeatable Read, or a row lock | `40001`, at Repeatable Read or Serializable |
| Read skew | two rows, each read once | a transfer lands between the two reads | Repeatable Read | none; a wrong number only |
| Write skew | read a shared total, write different rows | each independently trusts the total to cover its write | Serializable | `40001`, with a `DETAIL` naming a pivot |
| Phantom | act on a count matching a predicate | a matching row appears between two reads | Repeatable Read for a repeat read, Serializable if a write depends on it | none, at Repeatable Read |

### The honest limit of naming

Two of these anomalies never raise an error at the level a team is likely running by default: a lost update at Read Committed and write skew at Repeatable Read both commit cleanly, leaving a wrong number with no log to show it, since nothing failed. Either is found only by reading the code, not the logs, and asking what happens if two of these run at once. So a read-modify-write in a diff, or a write depending on a total read earlier in the transaction, earns that question every time: the failure mode of both is silence, not noise.

## Practice

1. ▢ An inventory table has `stock int NOT NULL CHECK (stock >= 0)`, one row at `stock = 5`. Two sessions at Read Committed each read `stock = 5`, then both run `UPDATE inventory SET stock = stock - 5 WHERE id = 1`. Predict the final `stock`, and whether the `CHECK` fires.

<details markdown="1"><summary>Check</summary>

`stock` ends at `0`, not `-5`. Each session read `5`, but `stock = stock - 5` uses whatever is committed once the lock frees, not the value read. A's write commits first at `0`; B then recomputes from that `0`, tries `-5`, and the `CHECK` rejects it with SQLSTATE `23514` instead of landing silently. The fix removes the silent loss, not the wrong arithmetic; it makes the wrongness loud.

</details>

2. ▢ Predict whether the read skew interleaving above still happens if A's two reads are replaced with one `SELECT sum(balance) FROM accounts`, still at Read Committed.

<details markdown="1"><summary>Hint</summary>

Read skew needs two reads that disagree; one statement sees only one snapshot.

</details>

<details markdown="1"><summary>Check</summary>

No. One statement gets one snapshot under Read Committed, so its sum is internally consistent, only possibly stale against a later read. Read skew needs a second, later read in one transaction, which one statement removes.

</details>

3. ▢ Predict what SQLSTATE, if any, the write skew interleaving produces if both A and B run at Read Committed instead of Repeatable Read.

<details markdown="1"><summary>Check</summary>

None; the total still ends at `80.00`, as at Repeatable Read. The updates touch different rows, so neither level blocks the other, and both only track row versions, invisible to write skew. Only Serializable adds the tracking that catches it.

</details>

4. ▢ A team adds `SELECT ... FOR UPDATE` to the read half of a read-modify-write at Read Committed. Predict whether this closes the gap the version column closed, and name the lesson teaching its syntax.

<details markdown="1"><summary>Hint</summary>

The version column's fix was that B's write matched zero rows; a row lock works by a different mechanism.

</details>

<details markdown="1"><summary>Check</summary>

Yes: it holds the row from A's first read until A commits, so B's read blocks rather than running against a value about to change. The syntax and strengths of that lock are lesson 32's subject, named only in passing.

</details>

5. ▢ Predict whether the phantom above is prevented by wrapping A's two counts in `SELECT ... FOR SHARE` on the matching rows, instead of raising the isolation level.

<details markdown="1"><summary>Check</summary>

No. `FOR SHARE` only locks rows a query returns, and the row ruining the count does not exist when the first lock would be taken. Only Repeatable Read or Serializable, which constrain the predicate itself, can do it.

</details>

6. ▢ A review finds `SELECT status ...`, then, after an application check that status is `'paid'`, `UPDATE ... SET status = 'shipped'`, both at Read Committed. Predict the anomaly at risk and its visible symptom.

<details markdown="1"><summary>Check</summary>

The read-modify-write shape behind a lost update: two requests can both read `'paid'`, both pass the check, and both write `'shipped'`, the second landing on top of the first once its row lock clears. The symptom is not an error, since both writes succeed; it surfaces only downstream, such as an order shipped twice, with nothing in the logs pointing back to the race.

</details>

## Real-world reps

- [ ] Open two sessions of your own and run the lost-update interleaving by hand, once plain and once with the single-statement fix, to watch the blocked step land.
- [ ] Search a codebase you maintain for a `SELECT` followed by an `UPDATE` on the same row in one request handler, and name which anomaly it is exposed to and the smallest defence.
- [ ] Tomorrow: pick one write in your own code that depends on a `count` or `sum` read earlier in the same transaction, and ask out loud what happens if two of it run at once.

## Going further

- [13.2.3. Serializable Isolation Level](https://www.postgresql.org/docs/current/transaction-iso.html#XACT-SERIALIZABLE): the source for write skew and `40001` handling
- [13.4. Data Consistency Checks at the Application Level](https://www.postgresql.org/docs/current/applevel-consistency.html): behind the version column and locking defences
- [Appendix A. PostgreSQL Error Codes](https://www.postgresql.org/docs/current/errcodes-appendix.html): where `40001` and this lesson's other SQLSTATEs live
- [Transactions](../reference/transactions.md): the stage 5 reference sheet
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
