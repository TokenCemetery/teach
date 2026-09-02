---
title: 28. What a Transaction Promises
description: Four promises travel under one acronym, and only one of them is yours to negotiate
type: lesson
---

# Lesson 28. What a Transaction Promises

**Mission link:** A migration that dies on statement forty of eighty has either changed nothing or changed something quietly wrong, and "it's in a transaction" is not, by itself, a reason to trust either outcome. This lesson separates the four claims one acronym bundles, so a reader knows which the database keeps and which is theirs to adjust.
**Primary source:** [PostgreSQL, Chapter 13 Concurrency Control](https://www.postgresql.org/docs/current/mvcc.html)
**Prerequisites:** [Lesson 6](0006-keys-and-constraints.md), [Lesson 24](0024-constraints-that-hold.md)

## Warm-up

1. ▢ Lesson 24 established that a `CHECK` is checked against a row at one moment, the end of the statement that touched it. When an `UPDATE` runs inside a transaction that has not yet committed, does the `CHECK` for that statement see one moment, or wait to see how the transaction ends?

<details markdown="1"><summary>Check</summary>

Still one moment; it does not wait. The `CHECK` runs once, right after the statement, against the new value alone, and a later `COMMIT` or `ROLLBACK` never sends the row back through it. What a transaction changes is not how many moments a constraint checks, but which moments exist for anyone else to see: everything from a transaction's first statement to its last is one interval, invisible to other sessions until it closes, and this lesson is about that interval and its edges.

</details>

## Know this

### A unit of work, opened and closed

A transaction is a unit of work: a sequence of statements the database applies completely or not at all. `BEGIN` opens one explicitly; `COMMIT` closes it keeping everything done since, `ROLLBACK` closes it discarding it. What most readers never check: a statement with no `BEGIN` nearby is still an implicit transaction, closed automatically around it. A multi-row `INSERT` shows this, since "one statement" and "one row" differ:

```sql
INSERT INTO accounts (id, owner, balance) VALUES (3, 'irene', 50.00), (4, 'kate', 60.00), (1, 'dup', 10.00);
-- ERROR: duplicate key value violates unique constraint "accounts_pkey", SQLSTATE 23505
SELECT count(*) FROM accounts;
-- 2, neither irene's row nor kate's was added; the whole statement failed, not just its last row
```

No `BEGIN` appears anywhere, and the database still refused two good rows rather than keep them without the third: the whole `INSERT` is one implicit transaction, applied completely or not at all.

### Four promises, one acronym

The acronym that names this is ACID, and it hides that its four letters are not the same kind of claim. Atomicity is the all-or-nothing promise the previous section already showed without naming it, and the next section demonstrates it failing and recovering. Consistency is the promise that the database's rules still hold once a transaction ends, with no separate mechanism here: it is stage 4's constraints doing the work, lesson 24's `CHECK` and `NOT NULL` included. Durability is the promise that a committed transaction survives whatever happens next, including a server crash, and that cannot be demonstrated without crashing the machine, so it is asserted here from the documentation instead: PostgreSQL keeps a write-ahead log, every change flushed to disk before the data pages it describes, and a commit does not return until its record is safely logged, so recovery replays the log rather than trusting data files that might not yet be written. Isolation is the odd one out, not a fixed promise but a bound the reader chooses, an isolation level, and different levels let a transaction see different amounts of another's unfinished work. The other three are not negotiable from inside a transaction; isolation is the one dial on the acronym, and the rest of this stage spends six lessons on it.

### The aborted transaction, and what it means for application code

A transaction that fails does not fail quietly. Inside a transaction, a division by zero is an ordinary runtime error:

```sql
BEGIN;
UPDATE accounts SET balance = balance - 10 WHERE id = 1;
SELECT 1 / 0;
-- ERROR: division by zero, SQLSTATE 22012
```

That much is unsurprising. What is not: the transaction is now aborted, and every later statement, however unrelated to the one that failed, is refused outright with the same complaint:

```sql
SELECT balance FROM accounts WHERE id = 1;
-- ERROR: current transaction is aborted, commands ignored until end of transaction block, SQLSTATE 25P02
```

Only `ROLLBACK` gets out of that state, and running it discards the whole transaction, the `UPDATE` that succeeded included, exactly as atomicity requires:

```sql
ROLLBACK;
SELECT balance FROM accounts WHERE id = 1;
-- 100.00, the UPDATE never happened either
```

For application code, this is the real surprise: a failed statement inside a transaction is not like one outside it, where the caller reads the error and moves on. Every later statement gets `25P02` until the transaction ends, so code that catches the error, logs it, and keeps issuing statements on the same connection watches them all fail alike.

### Savepoints, and what they are not

A `SAVEPOINT` marks a point inside a transaction that a later `ROLLBACK TO SAVEPOINT` can return to, without discarding the work that came before the mark:

```sql
BEGIN;
UPDATE accounts SET balance = balance - 10 WHERE id = 1;
SAVEPOINT before_transfer;
SELECT 1 / 0;
-- ERROR: division by zero, SQLSTATE 22012
ROLLBACK TO SAVEPOINT before_transfer;
SELECT balance FROM accounts WHERE id = 1;
-- 90.00, the UPDATE survived; only the failed statement after the savepoint was discarded
COMMIT;
SELECT balance FROM accounts WHERE id = 1;
-- 90.00, still, now committed
```

`ROLLBACK TO SAVEPOINT` recovers a transaction from the aborted state without losing everything done since `BEGIN`, and the transaction is usable at once. What a savepoint is not is a nested transaction with a durability of its own: nothing inside it, before the mark or after, survives if the outer transaction never commits.

```sql
BEGIN;
UPDATE accounts SET balance = balance - 1 WHERE id = 2;
SAVEPOINT sp1;
UPDATE accounts SET balance = balance - 1 WHERE id = 2;
ROLLBACK TO SAVEPOINT sp1;
ROLLBACK;
SELECT balance FROM accounts WHERE id = 2;
-- 100.00, both updates gone, the one made before the savepoint included
```

### Two sessions, one convention

Everything after this lesson runs two sessions at once, since isolation is a question about what one transaction sees of another's unfinished work, and one session alone has nothing to ask it about. A demonstration from here on is a sequence of steps marked `A:` or `B:`, in the order they run; open two client sessions, type the `A:` lines into one and the `B:` lines into the other in order, and read each trailing comment as that step's value or error. A step that waits on the other session is called out on its own line, not shown as an ordinary result. The aborted-transaction idea again, across two sessions instead of one:

```text
A: BEGIN;
A: UPDATE accounts SET balance = balance - 10 WHERE id = 1;     -- uncommitted
B: SELECT balance FROM accounts WHERE id = 1;                   -- 100.00, A's change is not visible yet
A: ROLLBACK;
B: SELECT balance FROM accounts WHERE id = 1;                   -- 100.00, still; there was never anything for B to see
```

B's second read matters not because it repeats the first, but because A's `ROLLBACK` had nothing to change for B: an uncommitted `UPDATE` was never part of the database B could see, so undoing it is invisible from B's side, since doing it already was. Run the same steps with `COMMIT` in A's place, and B's second read returns `90.00`; the only difference between the two runs is which of `COMMIT` or `ROLLBACK` A chose, and that choice is atomicity as a second session experiences it.

### What the rest of this stage negotiates

Isolation is the one promise with room to negotiate, and this stage spends six lessons on that room, one question each. Lesson 29 asks what a transaction can see of a database that other, still-uncommitted transactions are changing. Lesson 30 asks which views PostgreSQL offers to ask for, and what choosing one costs. Lesson 31 asks what goes wrong when two transactions act on a view the other's write has since made stale. Lesson 32 asks how a transaction holds a row still on purpose, rather than trusting isolation alone. Lesson 33 asks what happens when two transactions each hold what the other is waiting for. Lesson 34 asks what a transaction does after isolation refuses it, rather than handing back a wrong answer. None of the answers is previewed here, only the question.

## Practice

1. ▢ `UPDATE accounts SET balance = balance + 1 WHERE id = 2;` runs twice in a row, no `BEGIN` anywhere. The connection drops right after the first run succeeds but before the second starts. Predict `id = 2`'s balance: no increment, one, or two.

<details markdown="1"><summary>Check</summary>

One. Each statement outside an explicit transaction is its own transaction, so the first `UPDATE` committed the moment it returned, independent of the second, which never started.

</details>

2. ▢ `accounts` holds rows `1` and `2` only. Predict `SELECT count(*) FROM accounts` right after `INSERT INTO accounts (id, owner, balance) VALUES (5, 'x', 10.00), (6, 'y', 10.00), (1, 'z', 10.00);` fails on its third row.

<details markdown="1"><summary>Check</summary>

Still `2`. A multi-row `INSERT` is one statement, still its own transaction outside `BEGIN`; the duplicate key on the third row aborts the whole statement, so rows `5` and `6` were never added.

</details>

3. ▢ A transaction has just failed with `division by zero` and took no `SAVEPOINT`. Predict what `ROLLBACK TO SAVEPOINT some_name` does next.

<details markdown="1"><summary>Hint</summary>

Needing a savepoint to return to is separate from the transaction already being aborted.

</details>

<details markdown="1"><summary>Check</summary>

A different error from the one that aborted the transaction: `ERROR: savepoint "some_name" does not exist`, SQLSTATE `3B001`. The transaction stays aborted, since no real savepoint existed to recover to; only an actual `ROLLBACK` gets out of that state now.

</details>

4. ▢ A transaction runs an `UPDATE`, a `SAVEPOINT`, a second `UPDATE`, `ROLLBACK TO SAVEPOINT` to undo the second one, then a plain `ROLLBACK` with no `COMMIT` ever issued. Predict whether the first `UPDATE`, made before the savepoint, is part of what the final `ROLLBACK` discards.

<details markdown="1"><summary>Hint</summary>

A savepoint only ever discards forward from its own mark; ask what discards backward from it.

</details>

<details markdown="1"><summary>Check</summary>

Yes. A savepoint is not a nested transaction with a durability of its own: it commits nothing by itself, so an outer `ROLLBACK` takes the pre-savepoint work down with it too.

</details>

5. ▢ In the two-session interleaving in this lesson, predict what session B's second read reports if session A issues `COMMIT` at the end instead of `ROLLBACK`, everything else unchanged.

<details markdown="1"><summary>Check</summary>

`90.00`, against `100.00` for `ROLLBACK`. Nothing B ran changed; the only variable is which of `COMMIT` or `ROLLBACK` A chose, and B's second read reports exactly that choice.

</details>

6. ▢ Atomicity, the aborted state, and savepoints were each demonstrated by running statements and reading back the result. Predict why durability could not be demonstrated the same way, by any query against this same server.

<details markdown="1"><summary>Check</summary>

Demonstrating it means crashing the server after a commit returns, then showing the data survived; no query on a server that never crashed stands in for that. Every other promise here showed up as a difference a `SELECT` could report; durability's evidence is the absence of one after an event this lesson cannot cause, which is why it was asserted from documentation instead.

</details>

## Real-world reps

- [ ] Find a statement in code you maintain with no explicit `BEGIN` nearby, and check what happens to it if the process is killed right after it succeeds but before whatever runs next.
- [ ] Open two sessions against a database you can write to, run `BEGIN` and an `UPDATE` in one without committing, confirm from the other that nothing has changed yet, then choose `COMMIT` or `ROLLBACK` and confirm the second session sees exactly that choice.
- [ ] Tomorrow: find code of yours that catches an exception mid-transaction and keeps issuing statements on the same connection, and check what those later statements actually do.

## Going further

- [3.4. Transactions](https://www.postgresql.org/docs/current/tutorial-transactions.html): a tutorial introduction to `BEGIN`, `COMMIT` and `ROLLBACK`
- [Chapter 28. Reliability and the Write-Ahead Log](https://www.postgresql.org/docs/current/wal.html): the mechanism behind the durability promise asserted above
- [SAVEPOINT](https://www.postgresql.org/docs/current/sql-savepoint.html): the command reference for savepoints
- [Appendix A. PostgreSQL Error Codes](https://www.postgresql.org/docs/current/errcodes-appendix.html): where every SQLSTATE above is catalogued
- [Transactions](../reference/transactions.md): the stage 5 reference sheet
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
