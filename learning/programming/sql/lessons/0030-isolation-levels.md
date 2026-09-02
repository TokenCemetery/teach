---
title: 30. Isolation Levels
description: PostgreSQL gives you three distinct levels under four names, and each one permits a different set of surprises
type: lesson
---

# Lesson 30. Isolation Levels

**Mission link:** An incident report blaming "a race condition" is unfinished until it names the isolation level the transaction ran at and which of PostgreSQL's three behaviours that level permits; this lesson supplies both.
**Primary source:** [PostgreSQL, 13.2 Transaction Isolation](https://www.postgresql.org/docs/current/transaction-iso.html)
**Prerequisites:** [Lesson 3](0003-null-and-three-valued-logic.md), [Lesson 29](0029-mvcc.md)

## Warm-up

1. ▢ The SQL standard defines four isolation levels, Read Uncommitted, Read Committed, Repeatable Read and Serializable, weakest to strongest, and most descriptions say the weakest permits a dirty read, one transaction seeing another's uncommitted write. Before reading on, predict which name PostgreSQL defaults to when a transaction states none, and whether Read Uncommitted actually lets a reader see an uncommitted write.

<details markdown="1"><summary>Check</summary>

The default is Read Committed, confirmed by `SHOW transaction_isolation` outside any transaction. The false part of the usual belief is the dirty read itself: PostgreSQL accepts the name Read Uncommitted but runs it exactly as Read Committed, so there is no dirty read to see, at any level, ever. Four names exist; only three behaviours do.

</details>

## Know this

### Four names, three behaviours

PostgreSQL's `BEGIN` and `SET TRANSACTION` accept all four standard names, Read Uncommitted, Read Committed, Repeatable Read and Serializable, but implement only three behaviours: Read Uncommitted runs exactly as Read Committed, so a dirty read cannot be demonstrated at all. The default, confirmed by `SHOW transaction_isolation` outside any transaction, is `read committed`, so a transaction stating no level gets it unasked. Every interleaving below runs by opening two client sessions and typing the lines marked `A:` in one and `B:` in the other, in order.

```text
A: BEGIN ISOLATION LEVEL READ UNCOMMITTED;
B: BEGIN;
B: UPDATE accounts SET balance = 999 WHERE id = 1;
A: SELECT balance FROM accounts WHERE id = 1;                    -- 100.00, B's uncommitted write is invisible
A: SELECT current_setting('transaction_isolation');              -- read uncommitted, the name A asked for
B: ROLLBACK;
A: COMMIT;
```

The last line is the nuance worth keeping: `current_setting('transaction_isolation')` reports `read uncommitted` inside A's own transaction, echoing the name asked for, while every read A performs behaves as Read Committed regardless. The setting reports what was requested, not what will happen.

### Read Committed: one statement, one snapshot

Read Committed is the level lesson 29's vocabulary makes exact: each statement takes its own snapshot, current when it starts, rather than the transaction taking one and keeping it. Note where the transaction-wide snapshot of the stricter levels actually begins, since it is easy to assume: it is taken at the transaction's **first statement**, not at `BEGIN`, so a commit that lands between the two is visible, verified by running exactly that. Two `SELECT`s of the same row in one transaction can return different values if something commits between them, and neither read is wrong; each was consistent when it ran.

```text
A: BEGIN ISOLATION LEVEL READ COMMITTED;
B: BEGIN;
A: SELECT balance FROM accounts WHERE id = 1;                    -- 100.00
B: UPDATE accounts SET balance = 150 WHERE id = 1;
B: COMMIT;
A: SELECT balance FROM accounts WHERE id = 1;                    -- 150.00, same transaction, same row, a different answer
A: COMMIT;
```

That is a non-repeatable read, and it only shows up across several statements: code that reads and writes back in one statement never sees it, since there is no second statement for the snapshot to move on. That is why Read Committed is safe for code shaped that way, and a trap for code that reads in one statement and acts in a later one.

### Repeatable Read: the same read twice, and what it does to a writer

Repeatable Read closes that gap with one snapshot for the whole transaction rather than one per statement, so the interleaving that gave A two different balances now gives the same one twice.

```text
A: BEGIN ISOLATION LEVEL REPEATABLE READ;
A: SELECT balance FROM accounts WHERE id = 1;                    -- 100.00
B: UPDATE accounts SET balance = 150 WHERE id = 1;
A: SELECT balance FROM accounts WHERE id = 1;                    -- 100.00, unchanged
A: COMMIT;
A: SELECT balance FROM accounts WHERE id = 1;                    -- 150.00, once A starts a fresh transaction
```

The same fix closes a phantom read too: counting rows while another session inserts a matching one gives Read Committed a different count mid-transaction, and Repeatable Read the same count twice, since the later `SELECT` reuses the transaction's original snapshot instead of a fresh one that would see the insert.

```text
A: BEGIN ISOLATION LEVEL READ COMMITTED;
A: SELECT count(*) FROM accounts WHERE balance >= 100;           -- 2
B: INSERT INTO accounts VALUES (3, 'alan', 100.00);
A: SELECT count(*) FROM accounts WHERE balance >= 100;           -- 3
A: COMMIT;
```

```text
A: BEGIN ISOLATION LEVEL REPEATABLE READ;
A: SELECT count(*) FROM accounts WHERE balance >= 100;           -- 2
B: INSERT INTO accounts VALUES (4, 'kay', 100.00);
A: SELECT count(*) FROM accounts WHERE balance >= 100;           -- 2, unchanged
A: COMMIT;
```

Repeatable Read also changes what happens when two transactions write the same row: at Read Committed, two transactions that each read a balance and subtract from it do not conflict as expected, since the second `UPDATE` blocks on the first's row lock, then proceeds once it commits, still using its stale read, overwriting the first's change with no error anywhere.

```text
A: BEGIN ISOLATION LEVEL READ COMMITTED;
B: BEGIN ISOLATION LEVEL READ COMMITTED;
A: SELECT balance FROM accounts WHERE id = 1;                    -- 100.00
B: SELECT balance FROM accounts WHERE id = 1;                    -- 100.00
A: UPDATE accounts SET balance = 100.00 - 10 WHERE id = 1;
B: UPDATE accounts SET balance = 100.00 - 20 WHERE id = 1;       -- blocks here, waiting on A's row lock
A: COMMIT;
B: UPDATE accounts SET balance = 100.00 - 20 WHERE id = 1;       -- unblocks, and lands
B: COMMIT;
A: SELECT balance FROM accounts WHERE id = 1;                    -- 80.00, A's -10 is gone with no error anywhere
```

At Repeatable Read the same interleaving instead makes the second `UPDATE` fail the instant the first commits:

```text
A: BEGIN ISOLATION LEVEL REPEATABLE READ;
B: BEGIN ISOLATION LEVEL REPEATABLE READ;
A: SELECT balance FROM accounts WHERE id = 1;                    -- 100.00
B: SELECT balance FROM accounts WHERE id = 1;                    -- 100.00
A: UPDATE accounts SET balance = 90 WHERE id = 1;
B: UPDATE accounts SET balance = 80 WHERE id = 1;                -- blocks here, waiting on A's row lock
A: COMMIT;
B: UPDATE accounts SET balance = 80 WHERE id = 1;                -- unblocks, and fails
B: ROLLBACK;
A: SELECT balance FROM accounts WHERE id = 1;                    -- 90.00, A's change stands
```

```text
ERROR: could not serialize access due to concurrent update
SQLSTATE: 40001
```

The anomaly became an error you must handle: Repeatable Read detects the collision and refuses the loser instead of letting it through, trading an unnoticed wrong balance for a failure a caller must catch and retry.

### Serializable: the promise and the price

Serializable adds a check neither earlier level attempts: whether committed results could have come from running the transactions one at a time, rather than only watching for two writing the same row. Two transactions can each read data neither writes, act correctly on it, and still leave the database in a state no such ordering could produce; write skew is that shape.

Two transactions each read the total of both rows as `200.00` and each withdraw 60 from a different row. At Repeatable Read both commit and the total ends at `80.00`, wrong, while every per-row `CHECK` still holds. Lesson 31 runs that in full and names it; what belongs here is what the level above does with it. At Serializable the identical interleaving lets the first commit and refuses the second's outright:

```text
A: BEGIN ISOLATION LEVEL SERIALIZABLE;
B: BEGIN ISOLATION LEVEL SERIALIZABLE;
A: SELECT sum(balance) FROM accounts;                              -- 200.00
B: SELECT sum(balance) FROM accounts;                              -- 200.00
A: UPDATE accounts SET balance = balance - 60 WHERE id = 1;
B: UPDATE accounts SET balance = balance - 60 WHERE id = 2;
A: COMMIT;
B: COMMIT;                                                          -- fails, and the transaction is over
A: SELECT sum(balance) FROM accounts;                               -- 140.00, only A's withdrawal landed
```

```text
ERROR: could not serialize access due to read/write dependencies among transactions
DETAIL: Reason code: Canceled on identification as a pivot, during commit attempt.
HINT: The transaction might succeed if retried.
SQLSTATE: 40001
```

What Serializable promises is exactly that: the result is one some serial execution of the transactions could have produced. It does not promise every transaction succeeds, only that the database never ends up somewhere no ordering could explain, at the price of a commit that can fail for a reason neither did wrong, leaving a caller who must be ready to retry.

### Which anomaly, which level

Four anomaly names cover the table below, dirty read, nonrepeatable read, phantom read and serialization anomaly; lesson 31 defines each, and this lesson's job is only which level permits which.

| Isolation level | Dirty read | Nonrepeatable read | Phantom read | Serialization anomaly |
|---|---|---|---|---|
| Read Committed (Read Uncommitted runs identically) | Not possible | Possible | Possible | Possible |
| Repeatable Read | Not possible | Not possible | Not possible | Possible |
| Serializable | Not possible | Not possible | Not possible | Not possible |

Every "Not possible" cell is a demonstration already run: dirty reads never happen at any level; nonrepeatable and phantom reads are the interleavings that gave Repeatable Read the same value and count twice; Serializable's empty column is the write skew Repeatable Read let through. Read Committed's "Possible" serialization anomaly is the lost update earlier in this lesson, lost silently, the same anomaly Repeatable Read turns into the `40001` error instead.

### Choosing a level, and setting it

The honest default is not choosing: Read Committed is what a transaction gets by stating nothing, and most application code belongs there, since it reads and writes back in one statement, where a per-statement snapshot never goes stale. Repeatable Read suits a report running several queries needing one consistent instant, with no conflicting write in the picture. Serializable suits a rule spanning several rows that must hold regardless of interleaving, at the cost of a commit that can fail for reasons its own logic never reveals, which is why choosing it means writing the retry loop lesson 34 covers.

A level can be set three ways. `BEGIN ISOLATION LEVEL SERIALIZABLE` sets it for the one transaction `BEGIN` starts. `SET TRANSACTION ISOLATION LEVEL REPEATABLE READ`, as the first statement after a plain `BEGIN`, does the same. `SET default_transaction_isolation = 'repeatable read'` changes what every later transaction gets by default, leaving one already open at its original level.

```text
BEGIN;
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;
SHOW transaction_isolation;                                        -- repeatable read
COMMIT;
```

None of the three can rewrite a transaction already reading: calling `SET TRANSACTION ISOLATION LEVEL` after one query fails outright:

```text
BEGIN;
SELECT balance FROM accounts WHERE id = 1;
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;
```

```text
ERROR: SET TRANSACTION ISOLATION LEVEL must be called before any query
SQLSTATE: 25001
```

because the snapshot the new level needs may already be taken under the old one, with no way back.

## Practice

1. ▢ Inside one Repeatable Read transaction, A counts rows with `balance >= 100`, getting `2`, then inserts a new row that also qualifies, then repeats the count. Predict the second result.

<details markdown="1"><summary>Check</summary>

The second count is `3`: Repeatable Read's snapshot holds other transactions' commits fixed, not A's own writes, since a transaction always sees its own changes immediately, without needing anything to commit first.

</details>

2. ▢ Session A begins at Repeatable Read, reading row 1 as `100.00`. Session B updates it to `500.00`, commits, deletes it, and commits again. Predict A's next read, and whether its `count(*)` for that id agrees.

<details markdown="1"><summary>Hint</summary>

A's snapshot is not a cached copy of values already read; it is a promise about which rows exist.

</details>

<details markdown="1"><summary>Check</summary>

It returns `100.00`, and the count is `1`. A's snapshot predates both of B's changes, so row 1 still exists for A at its original value, as if B's update and delete had not happened yet.

</details>

3. ▢ Two sessions, neither opening an explicit transaction, run one bare statement each against a row holding `100.00`: `UPDATE accounts SET balance = balance - 10 WHERE id = 1` in A, `UPDATE accounts SET balance = balance - 20 WHERE id = 1` in B. Predict the final balance, and why the earlier lost-update interleaving does not repeat.

<details markdown="1"><summary>Check</summary>

It is `70.00`, both subtractions applied. Each bare statement is its own complete transaction: by the time B's `UPDATE` runs, A's has already committed, so B computes its subtraction from A's result rather than a value read earlier and held onto. The earlier lost update needed a read and a later write in one transaction; a single statement never holds a stale value.

</details>

4. ▢ A session sets `default_transaction_isolation = 'read committed'`, opens a transaction with `BEGIN`, and immediately runs `SET TRANSACTION ISOLATION LEVEL SERIALIZABLE` before any query. Predict what `SHOW transaction_isolation` reports.

<details markdown="1"><summary>Check</summary>

It reports `serializable`. A session's default only supplies the level a transaction starts with when nothing else says otherwise; an explicit `SET TRANSACTION`, run before the first query, overrides it for that transaction, without touching the default for the next.

</details>

5. ▢ Two Serializable transactions each read a different row, `id = 1` in A and `id = 2` in B, then each update the row they read. Predict whether both commit.

<details markdown="1"><summary>Hint</summary>

Serializable refuses only a result no serial ordering could produce; ask whether either transaction's outcome depends on the other's.

</details>

<details markdown="1"><summary>Check</summary>

Both commit. Serializable refuses only results no one-at-a-time ordering could reproduce; A and B never read or write a row the other touches, so either order gives the same outcome, and there is nothing to refuse.

</details>

6. ▢ A session is inside a transaction where `SHOW transaction_isolation` reports `read committed`, then runs `SET default_transaction_isolation = 'serializable'`. Predict what the same command reports immediately afterwards, still inside that transaction, and what it reports in the session's next transaction.

<details markdown="1"><summary>Check</summary>

Still `read committed` inside the transaction already running, then `serializable` in the next one. The setting only supplies the level a transaction gets when it starts, and cannot reach back into one already under way, the same rule that stops `SET TRANSACTION` from changing a level mid-transaction, seen from the session's default rather than a single statement.

</details>

## Real-world reps

- [ ] Open two sessions against a table you use at work, start a Repeatable Read transaction in one, read a row, let the other update and commit it, then read again and confirm it did not change.
- [ ] Find one place in code you maintain that reads a value in one statement and writes it back in a later statement of the same transaction, and check which isolation level it runs at.
- [ ] Tomorrow: check which isolation level your framework, driver or connection pool opens transactions at by default, and confirm it with `SHOW transaction_isolation` rather than trusting the documentation.

## Going further

- [13.2. Transaction Isolation](https://www.postgresql.org/docs/current/transaction-iso.html): the chapter this lesson compresses
- [SET TRANSACTION](https://www.postgresql.org/docs/current/sql-set-transaction.html): its full syntax and interaction with a session's default
- [BEGIN](https://www.postgresql.org/docs/current/sql-begin.html): BEGIN's own isolation-level clause
- [Appendix A. PostgreSQL Error Codes](https://www.postgresql.org/docs/current/errcodes-appendix.html): where `40001` and `25001` are catalogued
- [Transactions](../reference/transactions.md): the stage 5 reference sheet
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
