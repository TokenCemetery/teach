---
title: 33. Deadlocks
description: Two transactions each holding what the other needs, and the only cure is agreeing on an order in advance
type: lesson
---

# Lesson 33. Deadlocks

**Mission link:** A deadlock is a bug in the order two transactions took the same locks, not in either one's own logic, so an engineer paged for one needs to recognise the shape at once rather than hunt for a defect that is not there.
**Primary source:** [PostgreSQL, 13.3.4 Deadlocks](https://www.postgresql.org/docs/current/explicit-locking.html)
**Prerequisites:** [Lesson 31](0031-the-anomalies.md), [Lesson 32](0032-locks.md)

## Warm-up

1. ▢ Lesson 32 established that a session waiting for a row lock waits by default with no timeout. What happens when A waits for a lock B holds while B, at the same moment, waits for one A holds?

<details markdown="1"><summary>Check</summary>

Nothing does, on its own: both sessions wait forever, each correctly waiting for the other to finish, neither able to finish first. That mutual, permanent wait is a deadlock, and since an indefinite wait cannot resolve itself, something outside it has to break it.

</details>

## Know this

### One deadlock, built deliberately

Two sessions against `accounts`, each in its own transaction. A updates row 1. B updates row 2, no conflict yet, since the two hold locks on different rows. Then A tries row 2 and blocks, waiting on B's lock, and B tries row 1, closing the cycle.

```text
A: BEGIN;
B: BEGIN;
A: UPDATE accounts SET balance = balance - 1 WHERE id = 1;
B: UPDATE accounts SET balance = balance - 1 WHERE id = 2;
A: UPDATE accounts SET balance = balance - 1 WHERE id = 2;   -- blocks here, waiting on B's row lock
B: UPDATE accounts SET balance = balance - 1 WHERE id = 1;   -- fails, see below
A: COMMIT;                                                    -- A's blocked update lands, then this commits
B: ROLLBACK;
A: SELECT balance FROM accounts WHERE id = 1;                -- 99.00
A: SELECT balance FROM accounts WHERE id = 2;                -- 99.00
```

```
ERROR: deadlock detected
SQLSTATE 40P01
```

B is the one that fails here. Its `DETAIL` names both processes and the transaction each is waiting for, with numbers that differ on every run, and a `HINT` pointing at the server log. The moment B's statement is refused, A's blocked update lands and A commits both decrements; B has nothing left to roll back but the failed statement itself. What the server did is detect a cycle in the wait graph, which session is waiting on which, and cancel one of the two transactions in it, the only way to let the other proceed.

### What the server promises and what it does not

The primary source promises two things: a cycle will be detected, and one of the transactions that formed it will be cancelled to break it. It promises nothing about which one. Running the exact interleaving above again can fail A instead of B; the primary source itself says which transaction is aborted is difficult to predict and should not be relied upon. A lesson cannot tell a reader whose transaction dies, and neither can their application; code that assumes "the second statement always loses" trusts a pattern the server never signed up to. The message shape is stable even though its numbers are not: `ERROR: deadlock detected`, SQLSTATE `40P01`, a `DETAIL` naming two processes and the transactions they wait for, and a `HINT` pointing at the log. `SHOW deadlock_timeout` reports `1s`: a waiting session only looks for a cycle after waiting that long, so a real deadlock costs at least a second of silence before anyone finds out.

### The cause, stated as a rule rather than as bad luck

The cycle above was not bad luck. It happened because A and B took the same two locks in a different order: A went row 1 then row 2, B went row 2 then row 1. Swap B's order so both sessions take the rows the same way and the cycle has nowhere to form.

```text
A: BEGIN;
B: BEGIN;
A: UPDATE accounts SET balance = balance - 1 WHERE id = 1;
B: UPDATE accounts SET balance = balance - 1 WHERE id = 1;   -- blocks here, waiting on A's row lock
A: UPDATE accounts SET balance = balance - 1 WHERE id = 2;
A: COMMIT;                                                    -- releases both locks; B's blocked update lands
B: UPDATE accounts SET balance = balance - 1 WHERE id = 2;
B: COMMIT;
A: SELECT balance FROM accounts WHERE id = 1;                -- 98.00
A: SELECT balance FROM accounts WHERE id = 2;                -- 98.00
```

No error anywhere. B waits for A to finish with row 1, then proceeds through both updates and commits, exactly the ordinary lock wait lesson 32 already covered. Same two sessions, same two rows, same net effect on the balances; only the order one session took its locks in changed. That contrast is the whole lesson: a deadlock is a property of two pieces of code that disagree about lock order, not of concurrency itself.

### A second deadlock that does not look like one

A unique index makes a second inserter of the same key wait, verified here, since the index cannot tell yet whether the first, uncommitted insert will commit or roll back. That wait alone builds a cycle, with no explicit lock in the statements. A inserts a row with one key, B a row with another, neither conflicting. Then A inserts B's key and waits on B's uncommitted insert, and B inserts A's key and waits on A's, closing the cycle exactly as the row locks did above.

```text
A: BEGIN;
B: BEGIN;
A: INSERT INTO accounts VALUES (3, 'a-first', 10.00);
B: INSERT INTO accounts VALUES (4, 'b-first', 10.00);
A: INSERT INTO accounts VALUES (4, 'a-second', 10.00);   -- blocks here, waiting on B's uncommitted key
B: INSERT INTO accounts VALUES (3, 'b-second', 10.00);   -- fails, see below
A: COMMIT;
B: ROLLBACK;
A: SELECT owner FROM accounts WHERE id = 3;               -- a-first
A: SELECT owner FROM accounts WHERE id = 4;               -- a-second
```

```
ERROR: deadlock detected
SQLSTATE 40P01
```

B fails with the same `40P01`, the same message shape, the same unpredictable choice of victim. It means a deadlock needs no explicit lock at all, only two waits pointing at each other, and a unique index can supply both, just as a row lock can. A foreign key check can do the same, since it too makes a writer wait on another transaction's uncommitted row. The family is wider than `SELECT ... FOR UPDATE`; wherever two sessions wait on each other, in either direction, is a candidate.

### What to do about it in application code

Three options, in the order worth reaching for. Order the work: if every transaction touching two or more of the same rows takes them in the same order, id order for `accounts`, a cycle cannot form, since a cycle needs a pair disagreeing about the order; this is prevention, the only one of the three that removes the cause. Keep transactions short: the deadlock above needed both sessions still holding their first lock when reaching for the second, so a shorter gap shrinks that window, though it only reduces how often the cause fires rather than removing it. Retry on `40P01`: the server promises to cancel one side of any cycle it finds, so an application must retry its own cancelled transaction, but that is recovery, not prevention, and the loop belongs to lesson 34. One clause on how this differs from lesson 31's write skew: `40001` is a commit refused after the fact; `40P01` is two transactions stuck waiting on each other before either commits, and retrying does not touch the ordering that caused it.

### How to investigate one after the fact

A deadlock found in production, unlike the one above, was not built to fail on purpose, and the two statements behind its cycle are usually not sitting in front of whoever is debugging it. The `DETAIL` names the processes and transactions, but the actual statements are what matter, and the `HINT` line, pointing at the server log, is where they are: PostgreSQL logs the query text for each side of a deadlock it cancels, and the log is the only place the losing transaction's second statement appears, since the client only sees the error. Look for two entries close together in time, each naming a different process, each blocked on a lock the other held: the cause is always a pair, one statement from each side, that together took the same two things in a different order.

## Practice

1. ▢ Predict which of A or B is cancelled if the first interleaving in this lesson is run again from a fresh start.

<details markdown="1"><summary>Check</summary>

There is no way to predict it, and that is the point: the primary source says which transaction is aborted is difficult to predict and should not be relied upon. An answer naming a side with confidence is wrong regardless of which side it names.

</details>

2. ▢ Predict whether a deadlock's SQLSTATE is the same code lesson 31's write skew fails with under Serializable.

<details markdown="1"><summary>Check</summary>

No. A deadlock is `40P01`. Write skew under Serializable fails at commit with `40001`, a different failure, and a retry loop written for one does not address the other.

</details>

3. ▢ Predict whether two sessions inserting the same two keys in the same order, rather than opposite orders, can deadlock the way the unique-index example above did.

<details markdown="1"><summary>Hint</summary>

A cycle needs two waits pointing at each other, one from each side.

</details>

<details markdown="1"><summary>Check</summary>

No. The second session waits on the first's uncommitted key as before, but the first never turns around and waits on the second, so there is one wait, not a cycle: an ordinary wait, resolved the moment the first session ends, with no error at all.

</details>

4. ▢ `deadlock_timeout` is `1s` in this lesson. Predict roughly how long the deadlock in the first interleaving takes to surface if the setting were `5s` instead, all else unchanged.

<details markdown="1"><summary>Check</summary>

At least five seconds of silence before either session even checks for a cycle, since the setting controls how long a session waits before looking, not how fast the cycle is found once it looks.

</details>

5. ▢ Predict whether an application that retries a transaction unchanged after a `40P01`, without reordering anything, is protected against deadlocking again on the same workload.

<details markdown="1"><summary>Hint</summary>

The retry recovers this one transaction. Did it change the order the two transactions take locks in?

</details>

<details markdown="1"><summary>Check</summary>

No. Retrying only re-runs the same statements in the same order, so nothing stops the same two transactions colliding into the same cycle next time the timing lines up. It recovers from this deadlock; only reordering the locking removes the cause.

</details>

6. ▢ A workload always locks rows in ascending id order: some transactions lock rows 1 and 2, others lock rows 2 and 3, never a higher id before a lower one. Predict whether it can deadlock on those locks alone.

<details markdown="1"><summary>Check</summary>

No. Any two transactions sharing a row both take the lower id first, so they always agree on the order, and a cycle needs a pair that disagrees. Consistent ascending order rules out a cycle regardless of how many rows or transactions are involved.

</details>

## Real-world reps

- [ ] Take a transaction in a codebase you maintain that touches two or more rows, and check whether every other transaction touching those rows does so in the same order.
- [ ] Open two sessions against `accounts` and reproduce this lesson's first interleaving yourself, then run the same-order version and confirm which one errors and which one only waits.
- [ ] Tomorrow: find where your application logs a failed statement, and check whether a `40P01` alone would tell you which two statements collided.

## Going further

- [13.3.4. Deadlocks](https://www.postgresql.org/docs/current/explicit-locking.html#LOCKING-DEADLOCKS): the primary source's own account of the cycle and how it is broken
- [19.12. Lock Management](https://www.postgresql.org/docs/current/runtime-config-locks.html): where `deadlock_timeout` is documented in full, referenced rather than retaught here
- [Appendix A. PostgreSQL Error Codes](https://www.postgresql.org/docs/current/errcodes-appendix.html): where `40P01` and `40001` sit one class apart
- [Transactions](../reference/transactions.md): the stage 5 reference sheet
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
