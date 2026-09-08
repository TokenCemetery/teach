---
title: Persistence
description: "What RDB and AOF each promise, the exact loss window every fsync policy leaves, and what Redis's own documentation says about matching a database's durability"
type: reference
---

# Persistence: RDB, AOF, and the Comparison with a WAL

Stage 2 compressed for lookup. [Lesson 2](../lessons/0002-rdb-snapshotting.md) covers snapshots and [lesson 3](../lessons/0003-aof-and-wal-comparison.md) covers the append-only file and the WAL comparison; this sheet is the settings, the windows and the operational procedures.

Values are from the current Redis documentation.

## Two mechanisms

| | RDB | AOF |
|---|---|---|
| Stores | The whole dataset, at a point in time | Every write command, in order |
| Restores by | Loading one compact file | Replaying the log |
| Restart speed | Faster on a big dataset | Slower |
| File size | Smaller | Usually bigger |
| Loss window | Everything since the last snapshot | Set by the fsync policy |
| Forks | Often | Less often, and tunable **without a durability trade-off** |

The documentation's own summary of the last row is worth keeping: you can tune how often the AOF is rewritten without giving up durability, which is not true of lengthening a save interval.

## RDB

Configured as save points, for example `save 60 1000`, meaning dump if at least 1000 keys changed in 60 seconds. Or on demand with `SAVE` or `BGSAVE`.

The mechanism: Redis forks, the child writes a temporary file, and the child replaces the old one when finished. Copy-on-write is what lets the parent keep serving.

### The word "non-blocking" needs one qualification

Writing the snapshot does not block. **The `fork()` itself can.** The documentation is explicit: `fork()` can be time consuming if the dataset is big, and may result in Redis stopping serving clients for some milliseconds, or even for one second if the dataset is very big and the CPU is not fast.

So a large instance pays a latency spike at the start of every snapshot, before any copy-on-write benefit applies. That is separate from the memory spike lesson 2 describes, which arrives afterwards as the parent dirties pages.

The documentation's own verdict is blunt: RDB is the wrong choice where minimising data loss matters, and with a typical save point you should expect to lose the most recent minutes of data.

## AOF

`appendonly yes` turns it on. Durability is then entirely a question of `appendfsync`.

| Policy | fsync | Loss window | Note |
|---|---|---|---|
| `always` | After each batch of appended commands | Smallest | "Very very slow" per the docs, though it supports **group commit**, so parallel writes may share one fsync |
| `everysec` | Once a second, from a **background thread** | Up to one second | The default. The main thread tries to write while no fsync is in progress |
| `no` | Never, left to the kernel | **Typically about 30 seconds on Linux**, and not under Redis's control | Fastest, and the window is the kernel's to decide |

The `no` row is the one worth quantifying. Lesson 3 calls its window "considerably larger than a second"; the documentation puts a number on the usual case, roughly 30 seconds, while noting it depends on kernel tuning.

The `always` row is finer than "fsync per command": commands are appended after a batch from multiple clients or a pipeline has executed, so it is one write and one fsync before the replies go out.

### Multi-part AOF, since Redis 7.0

The single file is gone. There is now a **base** file, at most one, holding a snapshot in RDB or AOF format, plus one or more **incremental** files with the changes since it. They live in the directory named by `appenddirname` and are tracked by a **manifest**.

Rewriting compacts the history into the minimal set of commands that reproduce the current data, and it is safe by construction: Redis keeps appending to the old file while the new one is built, then switches.

### Copying the AOF directory is not safe during a rewrite

The documented procedure, which is the kind of thing discovered the hard way:

1. `CONFIG SET auto-aof-rewrite-percentage 0` to stop automatic rewrites, and do not run `BGREWRITEAOF`.
2. Check `INFO persistence` and confirm `aof_rewrite_in_progress` is `0`, waiting if it is `1`.
3. Copy the files in `appenddirname`.
4. Restore the previous `auto-aof-rewrite-percentage`.

### The `BACKUP` command family, since Redis 8.10

A self-contained restorable backup without stopping writes or hand-managing rewrites, producing a base, an increment and a manifest in the multi-part AOF format.

The operationally interesting part: creation is separated from finalization, so a control plane can **stagger `BACKUP START` across the nodes of a cluster so they do not all fork at the same time.** Given the fork cost above, simultaneous snapshots across a cluster are a self-inflicted latency event, and this is the mechanism for avoiding it.

## The comparison the arc asks for

Redis's own documentation makes it directly. Its guidance is that reaching "a degree of data safety comparable to what PostgreSQL" provides means running **both** persistence methods, not AOF alone. It discourages AOF by itself, wanting an RDB snapshot around for backups, for faster restarts, and in case of a bug in the AOF engine.

| | Redis, default | Redis, strongest common | A WAL, by default |
|---|---|---|---|
| Guarantee | As of the last snapshot | Up to one second of writes may be lost | The record is flushed before the commit is acknowledged |
| Set by | The save interval | `appendfsync everysec` | The commit path itself |

The structural point: AOF and a WAL are the same shape, a sequential log replayed to rebuild state. The difference is **when the flush happens relative to the acknowledgement.** A WAL flushes before saying yes; `everysec` says yes and flushes within the second. That is why the default settings differ in safety even though the mechanisms rhyme.

## Choosing

| Requirement | Configuration |
|---|---|
| A cache whose loss is a cold start | Neither, or RDB for faster warm restarts |
| A few minutes of loss is survivable | RDB alone |
| Bounded, sub-second loss | AOF `everysec`, plus RDB for backups |
| Loss unacceptable | Reconsider whether this belongs in Redis at all |

The last row is the one lesson 3 is really pointing at. `always` exists, and choosing it to make Redis behave like a database is usually a sign the data wants a database.

## Before relying on it

- The save points in the config are the loss window, stated in seconds. Somebody has read them.
- The `appendfsync` policy is a decision, not the default inherited by accident.
- If the answer to "how much can we lose" is "nothing", that is a signal about the storage choice, not about tuning.
- Fork latency is accounted for on a large instance, and cluster-wide snapshots are staggered.
- Any file-level backup of the AOF directory disables rewrites first and checks `aof_rewrite_in_progress`.
- RDB is kept even when AOF is on, which is what the documentation recommends.

## Sources

- [Docs: "Persistence", Redis](https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/)
- [Resources](../RESOURCES.md)
