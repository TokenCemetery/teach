---
title: 1. The Write-Ahead Log
description: The durability mechanism everything else in this workspace builds on
type: lesson
---

# Lesson 1. The Write-Ahead Log

**Mission link:** Crash recovery and replication both work the way they do because of one mechanism. Understanding it first is what turns the rest of this mission from memorized facts into things you can derive.
**Primary source:** [Docs: "Reliability and the Write-Ahead Log", PostgreSQL](https://www.postgresql.org/docs/current/wal.html)
**Prerequisites:** none

## Know this

### The problem the WAL solves

A committed transaction has to survive a crash. But the data pages it changed live in memory (in shared buffers) and only get flushed to disk periodically, for performance: flushing every changed page to disk on every commit would make every transaction pay a full random-write disk cost. So there's a gap between "the transaction is committed" and "every page it touched is safely on disk."

The **write-ahead log (WAL)** closes that gap. Before a transaction is allowed to report success, Postgres writes a compact record of the change to the WAL, a sequential append-only file, and fsyncs it to disk. The actual data pages can be flushed later, lazily, because if a crash happens first, Postgres can **replay the WAL** to reconstruct exactly what those pages should look like. The rule that makes this work, and gives the mechanism its name, is: the log record for a change is always durable on disk *before* that change is considered committed.

Sequential writes to one log file are far cheaper than random writes scattered across many data pages, which is the other reason this design wins on performance as well as safety.

### Crash recovery

On startup after a crash, Postgres finds the last consistent point it knows about, then **replays** every WAL record written after that point, reapplying each change to the data pages exactly as it would have applied it the first time. This is why a Postgres crash doesn't (ordinarily) lose a committed transaction: the transaction's WAL record was fsynced before commit was reported, so it's there to replay even if the data page itself never made it to disk before the crash.

### Checkpoints bound how far back recovery has to look

Replaying WAL from the beginning of time would make recovery take longer with every day the server runs. A **checkpoint** periodically flushes all currently-dirty data pages to disk and records the WAL position at that moment. Recovery then only has to replay WAL from the most recent checkpoint forward, not from the start of the log.

This is a real trade-off, not a free optimization: checkpointing more often bounds recovery time more tightly but costs more I/O while the server is running; checkpointing less often costs less I/O day-to-day but makes a crash's recovery replay longer.

### The same log drives replication

Streaming replication doesn't ship a copy of the database's data files to a standby server. It ships the **WAL records themselves**, as they're generated, and the standby replays them exactly the way crash recovery replays them locally. That's why replication and crash recovery share so much machinery: a standby is, in effect, permanently doing crash recovery from a live stream of WAL instead of from a file on disk.

## Practice

1. ▢ In one sentence, why must a transaction's WAL record be durable on disk before that transaction is reported as committed?

<details markdown="1"><summary>Check</summary>

Because the data pages the transaction changed may not be flushed to disk yet, so the WAL record is the only durable evidence of the change; without it being safely on disk first, a crash right after "commit" would silently lose that transaction.

</details>

2. ▢ A team disables synchronous WAL flushing (`synchronous_commit = off`) to raise throughput. The server crashes one second after a client received "commit successful" for a transaction. What happens to that transaction, and why?

<details markdown="1"><summary>Hint</summary>

The write-ahead rule this lesson describes assumes the WAL record was fsynced before commit was reported. What changes when that fsync is made asynchronous?

</details>

<details markdown="1"><summary>Check</summary>

The transaction may be lost. With `synchronous_commit = off`, Postgres can report a commit as successful before that transaction's WAL record is actually fsynced to disk. If the crash happens in that window, the WAL record for it was never durably written, so there's nothing to replay, and the transaction the client was told succeeded is gone. This is the throughput-versus-durability trade the setting makes explicit.

</details>

3. ▢ A server is configured to checkpoint only once every 24 hours instead of every few minutes. What does this cost, and when does the cost show up?

<details markdown="1"><summary>Check</summary>

It costs recovery time after a crash: since the last checkpoint bounds how far back WAL replay must start, a checkpoint 24 hours in the past means recovery may need to replay up to a full day's worth of WAL before the server can come back up. The cost is invisible during normal operation and only shows up exactly when it matters most, during a crash.

</details>

4. ▢ What does Postgres streaming replication actually send from primary to standby?

   - a) Periodic full copies of the changed data files
   - b) The WAL records generated by the primary, which the standby replays
   - c) The SQL statements that were executed, re-run on the standby
   - d) A snapshot of shared buffers taken at each checkpoint

<details markdown="1"><summary>Check</summary>

**b)** The WAL records generated by the primary, which the standby replays the same way crash recovery would. (a) and (d) describe data-file or memory snapshots, not what's actually streamed. (c) describes statement-based replication, which is a different (and, for Postgres's built-in streaming replication, not how it works) approach.

</details>

## Real-world reps

- [ ] On a Postgres instance you can access, run `SHOW wal_level;` and `SHOW checkpoint_timeout;` and record what they're currently set to.
- [ ] Find that instance's WAL directory (`pg_wal/`) and note how large it currently is. Compare it against the checkpoint interval you found above.
- [ ] Tomorrow: read the primary source's section on checkpoints in full, and write down, in your own words, what you'd change about your instance's checkpoint settings and why.

## Going further

- [Docs: "Routine Vacuuming", PostgreSQL](https://www.postgresql.org/docs/current/routine-vacuuming.html)
- [Docs: "High Availability, Load Balancing, and Replication", PostgreSQL](https://www.postgresql.org/docs/current/high-availability.html)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
