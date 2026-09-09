---
title: 4. Streaming Replication and Replication Slots
description: How a standby actually connects and catches up, and what a replication slot guarantees that plain streaming doesn't
type: lesson
---

# Lesson 4. Streaming Replication and Replication Slots

**Mission link:** Stage 3 opens replication: lesson 1 established that a standby is permanently doing crash recovery from a live WAL stream; this lesson is the actual connection mechanics and the guarantee, and the risk, a replication slot adds.
**Primary source:** [Docs: "High Availability, Load Balancing, and Replication", PostgreSQL](https://www.postgresql.org/docs/current/high-availability.html)
**Prerequisites:** [Lesson 3](0003-bloat-diagnosis-and-autovacuum-tuning.md), [Write-ahead log (WAL)](../GLOSSARY.md)

## Warm-up

1. ▢ What does a Postgres standby actually receive from the primary during streaming replication?

<details markdown="1"><summary>Check</summary>

The WAL records the primary generates, which the standby replays the same way crash recovery replays them locally, not a copy of the data files or a re-run of the original SQL statements.

</details>

2. ▢ Why does a stalled replication slot prevent vacuum from reclaiming dead tuples, even when autovacuum is running on schedule?

<details markdown="1"><summary>Check</summary>

A stalled slot holds back the oldest position a consumer still needs, and vacuum cannot reclaim any dead tuple newer than what every active slot still requires, regardless of how aggressively autovacuum is tuned or triggered.

</details>

## Know this

### Physical replication: an exact copy, not a subset

**Physical (streaming) replication** ships raw WAL records, byte for byte, to a standby, which replays them exactly as crash recovery would. The result is an exact binary copy of the entire cluster; a physical standby can't selectively replicate a subset of tables, because it isn't reconstructing changes at the row level, it's replaying the same physical changes the primary made. **Logical replication** is a different mechanism: it decodes WAL into row-level changes (`INSERT`, `UPDATE`, `DELETE`) and can replicate a chosen subset of tables through a publication and subscription. This lesson's focus, and the more common default, is physical streaming replication, the direct extension of lesson 1's WAL-replay mechanism to a live, remote consumer.

### The connection: a WAL sender and a WAL receiver

A standby's **WAL receiver** process connects to the primary and requests WAL starting from a specific position, identified by an **LSN (log sequence number)**, WAL's position identifier. The primary's **WAL sender** process streams records to the standby as they're generated, or from whatever it still has retained in `pg_wal` if the standby reconnects after a gap. As long as the primary still has the WAL segments the standby needs, catching up after a disconnect is just replaying whatever was missed.

### Replication slots: a persistent retention guarantee

Without anything holding it back, the primary manages its own WAL retention independently of any standby: it can recycle (remove) WAL segments it no longer needs for its own crash recovery, on its own schedule, even if a standby hasn't received them yet. If a standby disconnects for a while and the primary discards a segment the standby still needed, that standby falls permanently behind; it needs a fresh base backup to catch up, since replaying WAL that no longer exists isn't possible.

A **replication slot** fixes this by giving a specific consumer a persistent marker on the primary recording exactly how far it has confirmed receiving WAL. As long as a slot is active, the primary will not remove any WAL segment older than what that slot still needs, regardless of its own checkpoint or retention settings. This guarantees a disconnected standby can always catch up, no matter how long it's gone, as long as the slot stays in place.

![Two rows of six WAL segments. On the left, with no replication slot, the primary has already recycled segments 1 and 2, marked with an X, even though the standby's last confirmed position is segment 2, so that standby can no longer catch up by replaying WAL and needs a fresh base backup. On the right, with an active replication slot, all six segments are still retained because the slot tells the primary not to remove anything the standby hasn't confirmed, so the standby can always catch up once it reconnects.](images/replication-slot-retention.svg)

### The cost of that guarantee

The same property that protects a temporarily disconnected standby becomes dangerous once a slot is abandoned. A slot for a standby that has permanently stopped consuming, decommissioned, crashed and never restarted, or simply forgotten, still tells the primary "don't remove WAL older than this position," and the primary keeps its promise: WAL segments accumulate in `pg_wal` without bound, since nothing is telling the primary it's safe to discard them, until either the standby reconnects and catches up or the slot is explicitly dropped. This is the classic abandoned-slot failure mode, and it's the same mechanism lesson 3 named as one cause of vacuum being unable to reclaim dead tuples: a stalled slot doesn't just grow `pg_wal`, it also holds back the oldest snapshot vacuum has to respect, tying an unbounded disk-growth problem and a bloat problem to the exact same root cause.

## Practice

1. ▢ Contrast what physical replication streams with what logical replication streams, and describe the practical consequence for what each kind of standby can do.

<details markdown="1"><summary>Check</summary>

Physical replication streams raw WAL records byte for byte, producing an exact copy of the entire cluster with no ability to select a subset of tables. Logical replication decodes WAL into row-level changes and can replicate a chosen subset of tables through a publication and subscription, since it reconstructs changes at the row level rather than replaying the same physical writes.

</details>

2. ▢ What problem does a replication slot solve that plain streaming replication without one doesn't?

<details markdown="1"><summary>Check</summary>

Without a slot, the primary manages its own WAL retention independently and can discard segments a temporarily disconnected standby still needs, forcing that standby to take a fresh base backup to catch up. A slot gives that standby a persistent marker guaranteeing the primary won't remove WAL older than what it still needs, letting it always catch up after a disconnect, however long it lasted.

</details>

3. ▢ A standby disconnects for six hours due to a network issue. Describe what happens to the primary's WAL retention with an active replication slot for that standby, versus without one.

<details markdown="1"><summary>Check</summary>

With an active slot, the primary retains every WAL segment the standby hasn't yet confirmed receiving, regardless of its own retention schedule, so the standby can reconnect after six hours and replay everything it missed. Without a slot, the primary may recycle WAL segments it no longer needs for its own purposes during those six hours; if it does, the standby can no longer catch up by replaying WAL and needs a fresh base backup instead.

</details>

4. ▢ A standby was decommissioned, but its replication slot on the primary was never dropped. Describe the failure mode that results, and connect it to lesson 3's stalled-slot bloat cause.

<details markdown="1"><summary>Hint</summary>

The slot keeps making the same promise to the primary regardless of whether anyone is still listening.

</details>

<details markdown="1"><summary>Check</summary>

The primary keeps retaining every WAL segment newer than the abandoned slot's last confirmed position, since nothing tells it that consumer is gone; `pg_wal` grows without bound until the slot is dropped or the disk fills up. This is exactly lesson 3's stalled-slot cause of runaway bloat: the same slot that prevents WAL cleanup also holds back the oldest snapshot vacuum must respect, so an abandoned slot causes unbounded WAL growth and unreclaimable dead tuples simultaneously, from one root cause.

</details>

5. ▢ Which claim is true of replication slots?

    - a) A slot guarantees a standby can catch up after any disconnect, with no downside
    - b) A slot makes the primary retain WAL until the corresponding consumer confirms receiving it, which protects a temporarily disconnected standby but risks unbounded WAL growth if the slot is abandoned
    - c) Logical replication and physical replication stream identical data, differing only in configuration
    - d) A replication slot only affects WAL retention, never vacuum's ability to reclaim dead tuples

<details markdown="1"><summary>Check</summary>

**b)** That's exactly the trade-off: real protection against a temporary disconnect, real risk if the slot is forgotten. (a) is false: the same guarantee that helps a live standby becomes a liability once abandoned. (c) is false: physical replication ships raw WAL byte for byte; logical replication decodes row-level changes and can select a subset of tables. (d) is false: lesson 3 already established a stalled slot blocks vacuum too, the same mechanism this lesson connects to WAL retention.

</details>

## Real-world reps

- [ ] On a Postgres instance you can access, run a query against `pg_replication_slots` and check whether any listed slot is inactive or far behind the current WAL position.
- [ ] Find the `pg_wal` directory's current size and compare it against what you'd expect given the server's checkpoint interval, to spot whether something might be holding retention back.
- [ ] Tomorrow: read the primary source's section distinguishing physical and logical replication in full, and note one situation where you'd specifically want logical replication's table-subset capability.

## Going further

- [Docs: "High Availability, Load Balancing, and Replication", PostgreSQL](https://www.postgresql.org/docs/current/high-availability.html)
- [Docs: "Reliability and the Write-Ahead Log", PostgreSQL](https://www.postgresql.org/docs/current/wal.html)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
