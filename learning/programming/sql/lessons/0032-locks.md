---
title: 32. Locks You Take on Purpose
description: A row lock is how you hold a decision still, and every one of them has a failure mode worth choosing
type: lesson
---

# Lesson 32. Locks You Take on Purpose

**Mission link:** A lost update found in a postmortem is a bug that already shipped and cost something; the same bug found in review is one line, a lock strength and a wait policy chosen on purpose, and this lesson is what makes that line available before the postmortem rather than after it.
**Primary source:** [PostgreSQL, 13.3 Explicit Locking](https://www.postgresql.org/docs/current/explicit-locking.html)
**Prerequisites:** [Lesson 29](0029-mvcc.md), [Lesson 31](0031-the-anomalies.md)

## Warm-up

1. ▢ Lesson 29 established that a read is never made to wait for a write in progress, because a `SELECT` only ever looks at whichever version its own snapshot says is current, and that this is exactly why two sessions can both read the same balance and both decide something from it without either ever being made to wait for the other. Given that, what stops two sessions reading a row, both deciding a withdrawal is safe, and both writing, with neither write ever erroring?

<details markdown="1"><summary>Check</summary>

Nothing, by default. Lesson 31 named this the lost update: the read never blocked, so both decisions were made from the same stale value, and the second write lands on top of the first once its own row lock clears, with no error to say so. Fixing it means changing what the read means, which is what an explicit lock is for.

</details>

## Know this

### Why a row lock exists at all

An ordinary read is a look, not a claim: it reports what a row held at one moment and promises nothing about what it holds next. `SELECT ... FOR UPDATE` also says that no other session may end this row's current version until the transaction holding the lock ends, turning a look into a claim the next writer has to queue behind. Run lesson 31's read-modify-write shape with that claim in place, and the difference lands not in A's step but in when B's read is allowed to happen.

```text
A: BEGIN;
A: SELECT balance FROM accounts WHERE id = 1 FOR UPDATE;     -- 100.00, and now nobody else may end this row until A ends
B: BEGIN;
B: SELECT balance FROM accounts WHERE id = 1 FOR UPDATE;     -- blocks here, waiting on A's row lock
A: UPDATE accounts SET balance = 100.00 - 10 WHERE id = 1;
A: COMMIT;
B: UPDATE accounts SET balance = 90.00 - 20 WHERE id = 1;    -- B's blocked read had already landed at 90.00, A's committed change, the moment A released the row
B: COMMIT;
A: SELECT balance FROM accounts WHERE id = 1;     -- 70.00, both withdrawals counted, nothing lost
A: COMMIT;
```

Without the lock, B's read runs immediately, sees the same 100.00 A saw, and computes a withdrawal from a value already stale by the time it lands. With the lock, B's read itself waits, so the number B's application eventually decides from is A's committed 90.00, not the 100.00 that existed before either session touched the row.

### The four row-lock strengths, and which conflicts with which

PostgreSQL has four strengths of row lock, weakest to strongest: `FOR KEY SHARE` (a foreign key check confirming a row still exists), `FOR SHARE` (a read that must still hold at commit), `FOR NO KEY UPDATE` (an ordinary `UPDATE` leaving a foreign key's target columns alone), and `FOR UPDATE` (a write or delete guarded against any other claim). The difference is which locks they refuse to sit beside, not what they let a session read. Every cell below came from holding one strength in A and asking B to request another, with `NOWAIT` so a non-conflicting pair returns at once instead of looking like a conflict:

| Held by A | Requested by B: `FOR UPDATE` | `FOR NO KEY UPDATE` | `FOR SHARE` | `FOR KEY SHARE` |
|---|---|---|---|---|
| `FOR UPDATE` | conflict | conflict | conflict | conflict |
| `FOR NO KEY UPDATE` | conflict | conflict | conflict | no conflict |
| `FOR SHARE` | conflict | conflict | no conflict | no conflict |
| `FOR KEY SHARE` | conflict | no conflict | no conflict | no conflict |

`FOR SHARE` behind `FOR UPDATE` is worth seeing block and unblock, the shape a reporting query hits against a row someone else is about to change:

```text
A: BEGIN;
A: SELECT balance FROM accounts WHERE id = 1 FOR UPDATE;     -- 100.00
B: BEGIN;
B: SELECT balance FROM accounts WHERE id = 1 FOR SHARE;      -- blocks here, waiting on A's row lock
A: COMMIT;
B: COMMIT;                                                    -- B's FOR SHARE had already landed at 100.00 the moment A released the row
```

The table is not simply "everything waits": with A holding `FOR NO KEY UPDATE` on row 1, B's `SELECT balance FROM accounts WHERE id = 1 FOR KEY SHARE` returns at once, 100.00, because a plain update never has to queue behind a session only confirming the row still exists.

### Three ways to handle a wait

A row lock decides what a second session may not do, not how long it waits. Waiting is the default and has no ceiling: fine when the holder commits promptly, a liability when it does not. `NOWAIT` refuses to queue at all, failing the instant the lock is unavailable:

```text
A: BEGIN;
A: SELECT balance FROM accounts WHERE id = 1 FOR UPDATE;     -- 100.00
B: BEGIN;
B: SELECT balance FROM accounts WHERE id = 1 FOR UPDATE NOWAIT;
A: COMMIT;
B: ROLLBACK;
```

```
ERROR: could not obtain lock on row in relation "accounts"
```

That is SQLSTATE `55P03`, worth recognising since two other mechanisms below raise it for the same reason. `SKIP LOCKED` takes a third path: it quietly drops any row it cannot lock and returns what is left, the whole mechanism behind a queue table, where several workers each claim a different pending row without agreeing among themselves who gets which.

```text
A: BEGIN;
A: SELECT id FROM accounts ORDER BY id FOR UPDATE SKIP LOCKED LIMIT 1;     -- 1
B: BEGIN;
B: SELECT id FROM accounts ORDER BY id FOR UPDATE SKIP LOCKED LIMIT 1;     -- 2, skipping A's claimed row
B: SELECT id FROM accounts ORDER BY id FOR UPDATE SKIP LOCKED LIMIT 1;     -- 2 again, B is not blocked by its own claim
A: COMMIT;
B: COMMIT;
```

B's second attempt lands on the row it already holds rather than skipping past it, because a session never waits for a lock it already has.

### `lock_timeout`, and why it is the setting to reach for

Between waiting forever and refusing outright sits a bound worth naming: `lock_timeout` gives a fixed patience for a lock specifically, then cancels the one statement waiting on it, no more.

```text
A: BEGIN;
A: UPDATE accounts SET balance = balance - 1 WHERE id = 1;
B: SET lock_timeout = '150ms';
B: BEGIN;
B: UPDATE accounts SET balance = balance - 5 WHERE id = 1;
B: ROLLBACK;
A: ROLLBACK;
```

```
ERROR: canceling statement due to lock timeout
```

Also `55P03`, the same class `NOWAIT` raises, since both mean the row lock could not be got. `statement_timeout` is the setting most teams already reach for, but it bounds the whole statement's running time for any reason, a slow scan as readily as a lock wait:

```text
B: SET statement_timeout = '150ms';
B: BEGIN;
B: SELECT pg_sleep(1);
B: ROLLBACK;
```

```
ERROR: canceling statement due to statement timeout
```

That one is `57014`. From a log line alone the two are easy to tell apart: `55P03` says a lock was the problem, `57014` says the statement ran out of time for any reason, lock included. `lock_timeout` is the better default on a write path, since it fails fast on exactly this risk without cutting off a statement that is merely slow.

### Seeing who is waiting for whom

While a wait like B's is in progress, `pg_stat_activity` names the waiting backend: a row with `wait_event_type` of `Lock` and `state` of `active` is a statement still "running" but not let through, and `pg_blocking_pids()`, called with that backend's pid, returns the pids of whatever it is waiting on.

```text
A: BEGIN;
A: SELECT balance FROM accounts WHERE id = 1 FOR UPDATE;     -- 100.00
B: BEGIN;
B: SELECT balance FROM accounts WHERE id = 1 FOR UPDATE;     -- blocks here, waiting on A's row lock
C: SELECT pid, wait_event_type, state FROM pg_stat_activity WHERE wait_event_type = 'Lock';
C: SELECT pid, pg_blocking_pids(pid) AS blocked_by FROM pg_stat_activity WHERE wait_event_type = 'Lock';
A: COMMIT;
B: COMMIT;                                                    -- B's read had already landed the moment A released the row
```

C's first query names exactly one row, B's, stuck in that state; the second query's `blocked_by` column, for that row, names the session holding the lock B wants, and is empty once A commits. `pg_locks` tells the same story from the lock's side: a row there with `granted` false is B's request, and its `locktype` reads `transactionid` rather than a lock on the row, since a row-lock wait is really a wait for the holding transaction to end. Every pid here differs on every run, so what a reviewer reads off this shape is a structure, not a value: a waiting backend, with pids in `blocked_by` resolving, through the same view, to whichever session holds what it wants.

### Table-level locks, briefly

Every statement takes a lock on the table it touches as well as on any row, from an ordinary `SELECT`'s weakest lock to `ALTER TABLE`'s strongest, which conflicts with every other table lock, including a plain read's.

```text
A: BEGIN;
A: SELECT balance FROM accounts WHERE id = 1;
B: BEGIN;
B: ALTER TABLE accounts ADD COLUMN note text;     -- blocks here, waiting on A's table lock
A: COMMIT;
B: COMMIT;                                         -- B's ALTER TABLE had already landed the moment A released the table
```

A single open read was enough to make a schema change wait, and because that change then holds the strongest lock the table has until it finishes, everything else queues up behind it in turn. Doing this safely against a table taking live traffic is stage 7's subject.

### Advisory locks

Every lock so far has been on a row or a table that already exists. An advisory lock is on a number instead, one the application chooses, held for the length of a transaction with no row or table behind it.

```text
A: BEGIN;
A: SELECT pg_advisory_xact_lock(42);
B: BEGIN;
B: SELECT pg_try_advisory_xact_lock(42) AS got_it;     -- f, A already holds lock 42
A: COMMIT;
B: SELECT pg_try_advisory_xact_lock(42) AS got_it_after;     -- t, now that A's transaction ended
B: COMMIT;
```

That is the tool for serialising work that has no row to hang a lock on yet, such as making sure only one session builds a given report before any row naming that report exists. Lesson 34 is where an advisory lock actually gets used for that.

## Practice

1. ▢ A holds `FOR NO KEY UPDATE` on row 1. Predict whether B's `FOR KEY SHARE` on the same row blocks.

<details markdown="1"><summary>Hint</summary>

Find the pair in this lesson's table.

</details>

<details markdown="1"><summary>Check</summary>

No, it does not block. `FOR KEY SHARE` only cares whether the row's key columns still exist, and `FOR NO KEY UPDATE` promises it is not touching them, so the two coexist by design.

</details>

2. ▢ B runs `SELECT ... FOR UPDATE NOWAIT` on a row A already holds with `FOR UPDATE`. Predict the SQLSTATE and the first words of the message, without running it.

<details markdown="1"><summary>Check</summary>

The SQLSTATE is `55P03`, and the message begins `ERROR: could not obtain lock on row in relation`. It fails at once, never joining a queue.

</details>

3. ▢ A and B have each already claimed one row with `SELECT id FROM accounts ORDER BY id FOR UPDATE SKIP LOCKED LIMIT 1`, both transactions still open. Predict what a third session C's identical statement returns.

<details markdown="1"><summary>Check</summary>

Nothing, zero rows. Every row is already claimed, so `SKIP LOCKED` has nothing left to offer, and C's statement succeeds on an empty result rather than waiting for A or B to finish.

</details>

4. ▢ A log line shows a cancelled statement with `SQLSTATE 57014`. Predict whether a lock wait could have caused it.

<details markdown="1"><summary>Hint</summary>

Ask which of the two timeouts bounds only a lock wait, and which bounds the statement regardless of what it was doing.

</details>

<details markdown="1"><summary>Check</summary>

No. `57014` is `statement_timeout`'s code, raised for running out of time for any reason, a lock wait among them, while a lock-specific cutoff always reports `55P03`. Seeing `57014` alone rules out a lock as the reported cause, even though a lock wait could still be part of what made the statement slow.

</details>

5. ▢ B opens an uncommitted `ALTER TABLE` on `accounts`, then A opens a transaction and runs a plain `SELECT` on the same table. Predict whether A's `SELECT` blocks.

<details markdown="1"><summary>Check</summary>

Yes, it blocks. `ALTER TABLE` holds its lock until its transaction ends, and that lock conflicts with a plain read's regardless of which session asked first: every read behind an open schema change, not only every write, waits its turn.

</details>

6. ▢ A already holds `pg_advisory_xact_lock(42)`. Predict what A's own second call to `pg_try_advisory_xact_lock(42)`, in the same transaction, returns.

<details markdown="1"><summary>Hint</summary>

The same rule `SKIP LOCKED` relied on: a session meeting a lock it already holds itself.

</details>

<details markdown="1"><summary>Check</summary>

It returns true. A session is never made to wait for, or refused, a lock it already holds, whether that lock is on a row or on a number of its own choosing.

</details>

## Real-world reps

- [ ] Take one read-modify-write in code you maintain, add `FOR UPDATE` to its read, then open two sessions of your own and confirm the second session's read genuinely waits until the first commits.
- [ ] Find a table that several processes claim rows from, and decide whether `SKIP LOCKED` already does what a bespoke "claimed by" column was built to do.
- [ ] Tomorrow: pick one row lock strength you have never written by name, and find a place in your own schema where it would stop a read queuing behind a write it never actually conflicted with.

## Going further

- [13.3 Explicit Locking](https://www.postgresql.org/docs/current/explicit-locking.html): the whole chapter this lesson compresses, including page-level locks this lesson never needed
- [Appendix A. PostgreSQL Error Codes](https://www.postgresql.org/docs/current/errcodes-appendix.html): where every SQLSTATE quoted above is catalogued
- [53.13 pg_locks](https://www.postgresql.org/docs/current/view-pg-locks.html): every column `pg_locks` exposes, not only the ones this lesson queried
- [19.12 Lock Management](https://www.postgresql.org/docs/current/runtime-config-locks.html): `deadlock_timeout` and the other settings `lock_timeout` sits beside
- [Transactions](../reference/transactions.md): the stage 5 reference sheet
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
