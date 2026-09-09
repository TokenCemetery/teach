---
title: 2. RDB Snapshotting
description: What an RDB snapshot actually captures, and the data-loss window its save interval leaves open
type: lesson
---

# Lesson 2. RDB Snapshotting

**Mission link:** Stage 2 opens persistence: lesson 1 already flagged that Redis's persistence isn't the same guarantee as a database's WAL; this lesson makes that concrete for RDB specifically, the point-in-time snapshot mechanism and the window of data it can lose.
**Primary source:** [Docs: "Persistence", Redis](https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/)
**Prerequisites:** [Lesson 1](0001-memory-and-eviction.md), [maxmemory](../GLOSSARY.md)

## Warm-up

1. ▢ Why is eviction even a concept Redis needs, when a typical disk-backed database doesn't delete data to make room for new writes?

<details markdown="1"><summary>Check</summary>

Redis keeps its entire dataset in RAM, so its capacity is bounded by available memory in a way a disk-backed database isn't; that hard ceiling is what makes eviction necessary.

</details>

2. ▢ Distinguish the `volatile-*` eviction policy family from `allkeys-*`.

<details markdown="1"><summary>Check</summary>

`volatile-*` policies only evict keys that have a TTL set; `allkeys-*` policies are eligible to evict any key regardless of whether it has a TTL.

</details>

## Know this

### RDB captures the whole dataset at a point in time, not every write

**RDB** persistence writes Redis's entire dataset to disk as a compact binary snapshot, either on a configured schedule (for example, save if at least 1,000 keys changed within 60 seconds) or on demand via `BGSAVE`. A snapshot is a **fork-based, non-blocking** operation: Redis forks a child process to write the snapshot to disk while the parent process keeps serving requests, relying on the operating system's copy-on-write memory semantics so the parent's ongoing writes don't corrupt the snapshot already in progress.

### The durability window this actually leaves

Because a snapshot only happens at discrete points in time, whatever the save schedule decides, anything written between the last successful snapshot and a crash is gone: RDB's guarantee is "as of the last snapshot," not "every committed write survives." This is a fundamentally different shape of guarantee than a write-ahead log that fsyncs a record before reporting a transaction committed (lesson 1's pointer toward `data/postgres`'s WAL, made concrete here): the size of RDB's data-loss window is set directly by however long the save interval actually is, not by anything resembling a per-write durability promise.

![A timeline with three scheduled snapshots, S1, S2, and S3, evenly spaced. A crash occurs between S2 and S3. The region between S2 and the crash is shaded, representing every write made in that interval, which is lost, since restoring after the crash only recovers the dataset as it existed at S2, the last successful snapshot.](images/rdb-snapshot-loss-window.svg)

### What the fork-based mechanism costs

Copy-on-write is what lets the snapshot proceed without blocking the parent process, but it has a real cost under heavy write traffic during the fork: pages the parent modifies after forking get duplicated rather than shared with the child, so a large dataset under heavy write load during a save can see a real memory usage spike, in a worst case approaching double, though typically far less in practice. This is the trade RDB makes for restoring quickly from a single, compact file: fast to load on startup, useful for backups, disaster recovery, and migration, but paid for with a real memory cost during the snapshot and a real data-loss window between snapshots.

### The save interval is a deliberate trade-off, not a free tuning knob

A wider save interval (saving less often) reduces how frequently the fork-and-copy-on-write cost is paid, but widens the window of data that could be lost if a crash happens shortly before the next scheduled snapshot. A narrower interval shrinks that loss window at the cost of paying the snapshot overhead more often. Neither direction is free; the right choice depends on how much data loss on an unplanned crash the workload can actually tolerate.

## Practice

1. ▢ Describe what an RDB snapshot actually captures, and at what granularity, compared to logging every individual write.

<details markdown="1"><summary>Check</summary>

It captures the entire dataset as it exists at one point in time, whenever the snapshot runs, not a record of every individual write as it happens. Anything that changes between snapshots is only reflected once the next snapshot captures it.

</details>

2. ▢ A Redis instance is configured to save every 5 minutes. It crashes 4 minutes after the last successful snapshot. What has been lost?

<details markdown="1"><summary>Check</summary>

Every write that happened in those 4 minutes since the last snapshot, since RDB's guarantee only covers data as of its last successful save, not anything written afterward. On restart, the instance reflects the dataset as it was 4 minutes before the crash.

</details>

3. ▢ Why does RDB's fork-based snapshot mechanism rely on copy-on-write, and what's the memory cost risk during a snapshot on a heavy-write workload?

<details markdown="1"><summary>Hint</summary>

Consider what has to happen to a memory page the parent process modifies after the fork.

</details>

<details markdown="1"><summary>Check</summary>

The forked child process needs a consistent view of the dataset as it was at fork time, while the parent keeps serving writes; copy-on-write lets both share the same memory pages until the parent actually modifies one, at which point that page gets duplicated rather than corrupting what the child is still reading. Under heavy write traffic during the fork, many pages get duplicated this way, which can cause a real memory usage spike, approaching double the dataset size in a worst case.

</details>

4. ▢ Contrast RDB's restore speed and simplicity against its data-loss-window cost. When would a team accept a longer save interval, and when would that be dangerous?

<details markdown="1"><summary>Check</summary>

A longer save interval is acceptable when the data Redis holds can tolerate losing several minutes of recent writes on an unplanned crash, since restoring from a single compact snapshot file is fast regardless of interval length. It's dangerous for data where losing that window would be unacceptable, at which point RDB alone isn't the right persistence choice and AOF (lesson 3) or a genuinely durable store becomes the actual requirement.

</details>

5. ▢ Which claim is true of RDB snapshotting?

    - a) RDB fsyncs every individual write to disk before acknowledging it, the same guarantee a WAL provides
    - b) RDB captures the entire dataset at discrete points in time, leaving a data-loss window between the last snapshot and a crash sized by the save interval
    - c) A shorter save interval has no cost beyond disk space
    - d) Copy-on-write during a fork guarantees memory usage never increases during a snapshot

<details markdown="1"><summary>Check</summary>

**b)** That's exactly RDB's guarantee shape and the trade-off its interval makes. (a) is false: RDB is a periodic, whole-dataset snapshot, not a per-write durability mechanism. (c) is false: a shorter interval pays the fork-and-copy-on-write cost more often. (d) is false: copy-on-write can cause a real memory spike under heavy write traffic during the fork, not a guarantee against one.

</details>

## Real-world reps

- [ ] On a Redis instance you can access, run `CONFIG GET save` and record the current snapshot schedule.
- [ ] Estimate, for a real workload you know of, how much data (in terms of writes) would be lost if a crash happened right before the next scheduled snapshot under that configuration.
- [ ] Tomorrow: read the primary source's section on RDB in full, and note what `BGSAVE` versus `SAVE` differ on, specifically regarding blocking behavior.

## Going further

- [Docs: "Persistence", Redis](https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/)
- [Docs: "Key eviction", Redis](https://redis.io/docs/latest/develop/reference/eviction/)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
