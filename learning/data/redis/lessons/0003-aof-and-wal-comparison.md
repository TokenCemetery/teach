---
title: 3. AOF and the WAL Comparison
description: How AOF's fsync policy sets its data-loss window, and why even Redis's strongest common setting trades more durability for speed than Postgres does by default
type: lesson
---

# Lesson 3. AOF and the WAL Comparison

**Mission link:** This is stage 2's capstone: RDB's snapshot interval (lesson 2) is one durability window; AOF is Redis's other persistence mechanism, structurally similar to a WAL, and this lesson is the concrete comparison the mission's success criterion asks for.
**Primary source:** [Docs: "Persistence", Redis](https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/)
**Prerequisites:** [Lesson 2](0002-rdb-snapshotting.md), [maxmemory](../GLOSSARY.md)

## Warm-up

1. ▢ A Redis instance is configured to save every 5 minutes and crashes 4 minutes after the last successful snapshot. What has been lost?

<details markdown="1"><summary>Check</summary>

Every write from those 4 minutes since the last snapshot, since RDB's guarantee only covers data as of its last successful save, not anything written afterward.

</details>

2. ▢ Describe what an RDB snapshot actually captures, compared to logging every individual write.

<details markdown="1"><summary>Check</summary>

The entire dataset as it exists at one point in time, whenever the snapshot runs, not a record of every write as it happens.

</details>

## Know this

### AOF logs every write, structurally like a WAL

**AOF (append-only file)** persistence logs every write command Redis executes, appended to a file in order, rather than periodically snapshotting the whole dataset. On restart, Redis replays the log to reconstruct the dataset. Structurally, this is the same idea as a database's write-ahead log: a sequential, append-only record of operations, replayed to rebuild state after a crash, rather than a point-in-time picture of it.

### The fsync policy sets AOF's actual loss window

AOF's durability comes down to `appendfsync`, when the log is actually flushed to disk: `always` fsyncs after every single write command, the strongest guarantee, at the cost of a real latency hit on every write, since each one waits on a disk fsync. `everysec`, the default, batches up to a second's worth of writes into one fsync call, trading a bounded, predictable loss window, up to roughly one second of writes on a crash, for much better throughput than `always`. `no` leaves flushing entirely to the operating system's own buffering behavior, the fastest option, but with an unpredictable loss window that can be considerably larger than a second and isn't something Redis itself controls at all.

![Four horizontal bars, not to a strict numeric scale, comparing loss windows. appendfsync=always has essentially no loss window, fsyncing every write, at the cost of per-write latency. appendfsync=everysec, Redis's default, has a bounded window of up to roughly one second. appendfsync=no has an unpredictable window, potentially much larger, shown with a jagged edge since it depends entirely on operating-system buffering. Postgres's default synchronous_commit=on has essentially no loss window for a reported-committed transaction, comparable to Redis's always setting, not its default.](images/fsync-policy-loss-windows.svg)

### AOF also needs periodic rewriting, and pays the same cost RDB does

Because AOF logs every command, it grows without bound over time: a key set and reset a thousand times leaves a thousand log entries even though only its current value matters. Redis periodically rewrites the AOF, replacing the full command history with the minimal set of commands needed to reconstruct the current dataset, either automatically based on file-growth triggers or on demand. This rewrite uses the same fork-based, copy-on-write mechanism as RDB's snapshot (lesson 2), and carries the same memory-spike risk under heavy write traffic during the rewrite.

### The comparison the mission actually asks for

Even at `appendfsync=always`, Redis's strongest common durability setting, the comparison to Postgres isn't in Redis's favor by default: Postgres's default `synchronous_commit=on` effectively fsyncs the WAL record before every transaction is reported committed, a per-transaction guarantee out of the box. Redis's *default* `appendfsync` is `everysec`, an explicit, bounded loss window of up to about a second, not a per-write guarantee, even before considering that `always` costs real per-write latency to reach something closer to Postgres's default behavior. The structural parallel goes further: Postgres's WAL is bounded by checkpoints the same way AOF is bounded by rewrites, the same shape of trade-off (how far back does recovery, or replay, have to look) showing up in both systems independently.

This is the actual decision the mission's success criterion asks for, not a vague sense that "Redis is less safe": can a given use case tolerate a quantified loss window, RDB's save interval or AOF's fsync-policy window, or does it need something closer to Postgres's default, tighter, per-transaction guarantee? A shopping cart, where losing the last second of additions is an inconvenience, is a defensible fit for Redis's persistence as-is. A payment-processing ledger, where losing even one committed transaction is unacceptable, needs Postgres's guarantee, not Redis's, regardless of which `appendfsync` setting is chosen.

## Practice

1. ▢ Contrast `appendfsync always`, `everysec`, and `no`. Which has a bounded, predictable loss window, and which doesn't?

<details markdown="1"><summary>Check</summary>

`always` has essentially no loss window, fsyncing after every write, at the cost of per-write latency. `everysec` has a bounded, predictable loss window of up to roughly one second. `no` has an unpredictable loss window, potentially much larger than a second, since it depends entirely on the operating system's own flushing behavior rather than anything Redis controls.

</details>

2. ▢ Why does AOF need periodic rewriting, and what mechanism (and cost) does that rewrite share with RDB's snapshot?

<details markdown="1"><summary>Check</summary>

AOF logs every write command, so it grows unbounded over time even for keys whose value has long since changed again; rewriting replaces the full history with the minimal commands needed to reconstruct the current dataset. This rewrite uses the same fork-based, copy-on-write mechanism as RDB's snapshot, and so carries the same memory-spike risk under heavy write traffic during the rewrite.

</details>

3. ▢ Compare Postgres's default `synchronous_commit=on` against Redis's default `appendfsync=everysec`. Which gives a stronger per-write or per-transaction durability guarantee by default, and roughly by how much?

<details markdown="1"><summary>Hint</summary>

Consider what each default actually promises about a single write or transaction that just completed.

</details>

<details markdown="1"><summary>Check</summary>

Postgres's default gives the stronger guarantee: `synchronous_commit=on` fsyncs the WAL record before a transaction is even reported as committed, a per-transaction guarantee with essentially no loss window for anything the client was told succeeded. Redis's default `appendfsync=everysec` instead carries an explicit, bounded loss window of up to roughly one second of writes on a crash, not a per-write guarantee at all, even before matching Postgres's default would require switching to `appendfsync=always` and paying its per-write latency cost.

</details>

4. ▢ A shopping cart service and a payment-processing ledger both need persistence. Which is a defensible fit for Redis's persistence guarantees, and which needs Postgres instead? Defend the choice using the actual loss-window reasoning from this lesson.

<details markdown="1"><summary>Check</summary>

The shopping cart is a defensible fit for Redis: losing up to a second of recent additions (under `everysec`) or a few minutes (under RDB's save interval) is an inconvenience a customer can recover from by re-adding an item, not a correctness failure. A payment-processing ledger needs Postgres: losing even one committed transaction is unacceptable, and neither RDB's snapshot interval nor AOF's `everysec` default, nor even `always`'s per-write fsync, is designed as a primary durability guarantee the way Postgres's WAL-backed commit is.

</details>

5. ▢ Which claim is true of comparing Redis's persistence to Postgres's WAL?

    - a) AOF at any fsync setting provides the same per-transaction guarantee Postgres's default does
    - b) Even Redis's strongest common durability setting is an operational choice layered onto a system designed to be fast-first, and the actual decision is whether a use case can tolerate a quantified loss window or needs Postgres's tighter default guarantee
    - c) RDB and AOF have identical data-loss windows, since both eventually get rewritten or snapshotted
    - d) Postgres's WAL and Redis's AOF share no structural similarity at all

<details markdown="1"><summary>Check</summary>

**b)** That's the actual, quantified decision this lesson holds the comparison to. (a) is false: even `appendfsync=always` costs real per-write latency and still isn't automatically equivalent to Postgres's default behavior. (c) is false: RDB's loss window is its save interval (often minutes), while AOF's is set by its fsync policy (often a second or less), genuinely different windows. (d) is false: both are sequential, append-only logs of operations replayed to reconstruct state, a real structural parallel.

</details>

## Real-world reps

- [ ] On a Redis instance you can access, run `CONFIG GET appendonly` and `CONFIG GET appendfsync` and record the current persistence configuration.
- [ ] For a real use case you know of that's backed by Redis, decide, from its actual loss-window tolerance, whether its current persistence configuration (or lack of one) is a defensible fit or a hidden risk.
- [ ] Tomorrow: read the primary source's section comparing RDB and AOF (including using both together) in full, and note what trade-off combining them is meant to address.

## Going further

- [Docs: "Persistence", Redis](https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/)
- [Docs: "Key eviction", Redis](https://redis.io/docs/latest/develop/reference/eviction/)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
