---
title: 5. Failover Mechanics
description: What happens when a standby is promoted, why a former primary can't just rejoin, and the data-loss trade-off synchronous replication bounds
type: lesson
---

# Lesson 5. Failover Mechanics

**Mission link:** Lesson 4 gave replication its plumbing; this lesson is what happens when the primary at the other end of that plumbing fails, and the durability trade-off that determines how much committed work survives the switch.
**Primary source:** [Docs: "High Availability, Load Balancing, and Replication", PostgreSQL](https://www.postgresql.org/docs/current/high-availability.html)
**Prerequisites:** [Lesson 4](0004-streaming-replication-and-slots.md), [Write-ahead log (WAL)](../GLOSSARY.md)

## Warm-up

1. ▢ What does a replication slot guarantee, and what's the risk if it's abandoned?

<details markdown="1"><summary>Check</summary>

It guarantees the primary won't discard WAL a specific consumer still needs, letting a disconnected standby always catch up. If the slot is abandoned (its standby gone for good), the primary keeps retaining WAL for a consumer that will never claim it, growing `pg_wal` without bound.

</details>

2. ▢ Contrast what physical replication streams with what logical replication streams.

<details markdown="1"><summary>Check</summary>

Physical replication streams raw WAL records byte for byte, producing an exact copy of the entire cluster. Logical replication decodes WAL into row-level changes and can replicate a chosen subset of tables.

</details>

## Know this

### Switchover and failover are not the same event

A **switchover** is a planned, coordinated role swap: the current primary is told to stop, its final WAL is confirmed as received by the standby being promoted, and the roles trade in a controlled sequence with no data loss. A **failover** is a reactive, unplanned promotion, triggered because the primary has already failed or become unreachable, with no chance to coordinate a clean handoff first. That difference is exactly why failover carries real data-loss risk that a switchover doesn't: a failover promotes whichever standby is available based on whatever WAL it happened to have already received, not on a confirmed, final state from the primary.

### What promotion actually changes

**Promotion** (triggered by an administrator or an external tool, since Postgres itself does not automatically detect failure and promote on its own) stops a standby from replaying incoming WAL and makes it begin accepting write transactions as an ordinary primary. It stops being, in lesson 1's words, "permanently doing crash recovery," and starts being a normal read-write server.

### Why a former primary can't just rejoin

If the original primary comes back online after a failover, it cannot simply resume as if nothing happened. Its own WAL may have continued past the point the new primary's history diverged from, meaning the old primary and the new primary can disagree about what happened after that point, a **split-brain** risk if both try to accept writes independently. Postgres tracks this with a **timeline ID**, which increments every time a promotion occurs. A former primary rejoining after a failover has to be explicitly reset onto the new primary's timeline (a tool like `pg_rewind` does this) rather than being allowed to continue advancing its own, now-divergent history.

### Synchronous replication bounds how much committed data failover can lose

By default, replication is **asynchronous**: the primary reports a transaction as committed to the client without waiting for any standby to confirm it received that transaction's WAL. This is fast, but it means a transaction the client was told succeeded can be entirely missing from every standby if the primary fails before that WAL was shipped; after failover, that transaction doesn't exist anywhere, not because it was rolled back, but because it was never replicated at all.

**Synchronous replication** (`synchronous_standby_names`, paired with `synchronous_commit`) changes this: the primary waits for at least one designated standby to confirm receiving (and optionally applying) a transaction's WAL before reporting commit success to the client. This bounds failover's data loss to zero for genuinely committed transactions, at the cost of added commit latency (a network round trip to the synchronous standby on every commit) and reduced availability (commits can stall if that standby becomes unreachable, depending on configuration). This is the concrete trade-off failover mechanics force a decision on: how much committed-but-unreplicated data is acceptable to lose versus how much commit latency and availability risk is acceptable to prevent it.

## Practice

1. ▢ Distinguish a switchover from a failover, and explain why that difference affects data-loss risk.

<details markdown="1"><summary>Check</summary>

A switchover is planned and coordinated: the primary is stopped deliberately, its final WAL is confirmed received, and roles swap with no data loss. A failover is reactive, triggered by an already-failed or unreachable primary with no chance to coordinate first, so the promoted standby's data-loss exposure depends on whatever WAL it happened to have received already, not on a confirmed final state.

</details>

2. ▢ Describe what happens to a standby's role and behavior at the moment of promotion.

<details markdown="1"><summary>Check</summary>

It stops replaying incoming WAL (it's no longer following a primary's stream) and begins accepting write transactions itself, becoming an ordinary read-write primary rather than the WAL-replaying standby it was.

</details>

3. ▢ Why can't a former primary simply rejoin the cluster as a standby after a failover without special handling? What could go wrong if it just resumed as if nothing happened?

<details markdown="1"><summary>Hint</summary>

Consider what the old primary's own WAL might contain that the new primary knows nothing about.

</details>

<details markdown="1"><summary>Check</summary>

The former primary's WAL may have continued past the point where the new primary's history diverged, so the two disagree about what happened afterward. If it simply resumed, both could end up accepting writes independently on incompatible histories, a split-brain scenario. Postgres's timeline ID tracks this divergence, and a tool like `pg_rewind` is needed to reset the former primary onto the new primary's timeline rather than continuing its own.

</details>

4. ▢ Under asynchronous replication, a primary commits and reports success to the client for transaction T. The standby hadn't yet received T's WAL when the primary crashed, and that standby is then promoted. What happened to T from the client's perspective, and how would synchronous replication have changed the outcome, at what cost?

<details markdown="1"><summary>Check</summary>

T is gone: the client was told it succeeded, but it never made it to any standby, so after failover it doesn't exist anywhere. Synchronous replication would have prevented this by making the primary wait for the standby to confirm receiving T's WAL before reporting commit success at all, bounding this kind of loss to zero, at the cost of added commit latency (waiting on that confirmation) and the availability risk of commits stalling if the synchronous standby becomes unreachable.

</details>

5. ▢ Which claim is true of failover in Postgres?

    - a) Postgres automatically detects a failed primary and promotes a standby with no external tooling required
    - b) A former primary can always safely rejoin as a standby immediately after a failover, with no special handling
    - c) Asynchronous replication can lose committed transactions on failover; synchronous replication bounds that loss at the cost of commit latency and availability
    - d) Switchover and failover carry identical data-loss risk, since both result in a new primary

<details markdown="1"><summary>Check</summary>

**c)** That's the central trade-off this lesson establishes. (a) is false: Postgres itself doesn't automatically detect failure and promote; external tools handle that. (b) is false: timeline divergence means a former primary needs explicit handling (such as `pg_rewind`) before rejoining. (d) is false: a switchover is coordinated with no data loss, while a failover is reactive and can lose whatever wasn't yet replicated.

</details>

## Real-world reps

- [ ] On a test Postgres setup with a standby, check whether `synchronous_standby_names` is configured, and if not, what the practical data-loss exposure would be on an unplanned failover.
- [ ] Find the current timeline ID on a primary (`SELECT timeline_id FROM pg_control_checkpoint();` or equivalent) and note what it would become after a promotion.
- [ ] Tomorrow: read about `pg_rewind` in the primary source or its own documentation, and note what it needs available to resynchronize a former primary onto a new timeline.

## Going further

- [Docs: "High Availability, Load Balancing, and Replication", PostgreSQL](https://www.postgresql.org/docs/current/high-availability.html)
- [Docs: "Reliability and the Write-Ahead Log", PostgreSQL](https://www.postgresql.org/docs/current/wal.html)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
