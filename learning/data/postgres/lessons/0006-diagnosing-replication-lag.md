---
title: 6. Diagnosing Replication Lag
description: Why receive lag and apply lag are different measurements, and the diagnostic order that finds which one is actually happening
type: lesson
---

# Lesson 6. Diagnosing Replication Lag

**Mission link:** This is stage 3's capstone: lessons 4 and 5 gave replication its mechanics and its failure-mode consequences; this lesson is measuring and diagnosing the everyday symptom, a standby falling behind, rather than guessing which of several distinct causes is responsible.
**Primary source:** [Docs: "High Availability, Load Balancing, and Replication", PostgreSQL](https://www.postgresql.org/docs/current/high-availability.html)
**Prerequisites:** [Lesson 5](0005-failover-mechanics.md), [Write-ahead log (WAL)](../GLOSSARY.md)

## Warm-up

1. ▢ What does synchronous replication bound, and what does it cost in exchange?

<details markdown="1"><summary>Check</summary>

It bounds data loss on failover to zero for genuinely committed transactions, by making the primary wait for a designated standby to confirm receiving the WAL before reporting commit success. The cost is added commit latency and reduced availability if that standby becomes unreachable.

</details>

2. ▢ Why can't a former primary simply rejoin as a standby immediately after a failover?

<details markdown="1"><summary>Check</summary>

Its own WAL may have continued past the point the new primary's history diverged from, risking split-brain if both accept writes independently. It needs to be reset onto the new primary's timeline, with a tool like `pg_rewind`, before rejoining.

</details>

## Know this

### Two different lags, not one

**Replication lag** isn't a single number. **Receive (or write) lag** measures how far behind, in WAL position, a standby is from the primary's current WAL: has the WAL even arrived at the standby yet? **Replay (or apply) lag** measures something different: how long after a transaction committed on the primary its effects actually became visible on the standby, that is, how long after the WAL arrived did the standby finish applying it. These can diverge sharply: a standby can have received essentially all the WAL bytes (receive lag near zero) while still being far behind on actually applying them (replay lag high), if it's CPU- or I/O-constrained, if a long-running query is holding back replay, or if it's deliberately configured with a delay.

### Where to measure both at once

`pg_stat_replication`, queried on the primary, gives a row per connected standby with `sent_lsn`, `write_lsn`, `flush_lsn`, and `replay_lsn` (WAL positions at each stage), alongside `write_lag`, `flush_lag`, and `replay_lag` as actual time intervals. Comparing `sent_lsn` against `replay_lsn` shows the byte-position gap directly; the lag time columns show the same gap converted into how much time it actually represents. `pg_stat_wal_receiver`, queried on the standby itself, gives that standby's own view of its connection status and what it has received.

### A diagnostic order, not a single check

A standby that appears to be lagging has one of a few distinct causes, checked in order:

1. **Is it even connected?** A missing row in `pg_stat_replication` for that standby means it's disconnected entirely, the most basic diagnosis, and not a subtle lag cause at all.
2. **Is WAL arriving slowly (a receive problem), or arriving fine but applying slowly (an apply problem)?** High `write_lag` or `flush_lag` alongside high `replay_lag` points at the network or the primary's own send rate; low `write_lag` and `flush_lag` with high `replay_lag` specifically means WAL is arriving but the standby can't keep up applying it.
3. **If it's specifically an apply problem**, check the standby's own CPU and I/O load, whether a long-running query on the standby is holding back replay, and whether `recovery_min_apply_delay` is deliberately configured (a delayed replica kept intentionally behind, for protection against accidental data loss on the primary, is not a bug).

### The read-query-versus-replay trade-off

A long-running query on a standby can conflict with replay, since applying a change (like a row deletion) that the running query still needs to see would break that query's consistent view. Postgres has to choose: `hot_standby_feedback` tells the primary to hold back cleanup the standby's queries still need, and `max_standby_streaming_delay` bounds how long replay will wait for a conflicting query before canceling that query instead. Which side of this trade-off a standby is configured for directly shapes whether long queries cause replay lag or get canceled to prevent it.

## Practice

1. ▢ Distinguish receive (write) lag from replay (apply) lag, and describe a scenario where one is high while the other is near zero.

<details markdown="1"><summary>Check</summary>

Receive lag measures how far behind the standby is in WAL position, whether the WAL has arrived at all; replay lag measures how long after it arrived (and after the original commit) the standby finished applying it. A CPU- or I/O-constrained standby can have received nearly all the WAL (low receive lag) while still being far behind on applying it (high replay lag), since receiving and applying are separate steps.

</details>

2. ▢ Where would you look first to check whether apparent replication lag is actually a connectivity problem rather than a genuine lag problem?

<details markdown="1"><summary>Check</summary>

`pg_stat_replication` on the primary: if there's no row at all for that standby, it isn't lagging, it's disconnected, which is a different and more basic problem than any of the lag-measurement questions.

</details>

3. ▢ A standby shows near-zero `write_lag` but high `replay_lag`. Name two plausible causes, and describe how you'd narrow down which one applies.

<details markdown="1"><summary>Hint</summary>

Think about what could slow down applying WAL that's already arrived.

</details>

<details markdown="1"><summary>Check</summary>

Two plausible causes: the standby is CPU- or I/O-constrained and genuinely can't apply WAL as fast as it arrives, or a long-running query on the standby is holding back replay to avoid disrupting that query's consistent view. Narrowing it down means checking the standby's own resource utilization (CPU, disk I/O) for saturation, and separately checking for any long-running or idle-in-transaction query on the standby that could be conflicting with replay.

</details>

4. ▢ Why might a long-running query on a standby cause replay lag specifically, and what two configuration options govern the trade-off Postgres makes when this happens?

<details markdown="1"><summary>Check</summary>

Applying a change that would remove data the running query still needs to see (such as a row deletion) would break that query's consistent view, so Postgres has to choose between delaying replay or canceling the query. `hot_standby_feedback` tells the primary to hold back cleanup the standby's queries still need; `max_standby_streaming_delay` bounds how long replay will wait for a conflicting query before canceling it instead.

</details>

5. ▢ Which claim is true of diagnosing replication lag?

   - a) A single lag number from pg_stat_replication is sufficient; receive and replay lag always move together
   - b) Receive lag and replay lag measure different things and can diverge, so distinguishing them is part of the diagnosis, not just a detail
   - c) A missing row in pg_stat_replication for a standby means it has extremely high lag
   - d) hot_standby_feedback and max_standby_streaming_delay both always cancel a conflicting query, with no trade-off between them

<details markdown="1"><summary>Check</summary>

**b)** That distinction is exactly what separates a receive problem from an apply problem, and misdiagnosing one as the other leads to fixing the wrong thing. (a) is false: a standby can be fine on one and behind on the other. (c) is false: a missing row means disconnected, not merely lagging, a different problem entirely. (d) is false: they represent opposite sides of a trade-off, holding back cleanup versus bounding how long replay waits before canceling a query.

</details>

## Real-world reps

- [ ] On a Postgres instance with at least one standby, query `pg_stat_replication` and compare `write_lag`, `flush_lag`, and `replay_lag` for each connected standby.
- [ ] Check whether `hot_standby_feedback` and `max_standby_streaming_delay` are configured on a standby you have access to, and what trade-off that configuration implies for long-running queries there.
- [ ] Tomorrow: if you have a standby showing any lag, walk this lesson's diagnostic order (connected, receive vs. apply, then resource or query cause) to find where it actually falls.

## Going further

- [Docs: "High Availability, Load Balancing, and Replication", PostgreSQL](https://www.postgresql.org/docs/current/high-availability.html)
- [Docs: "Reliability and the Write-Ahead Log", PostgreSQL](https://www.postgresql.org/docs/current/wal.html)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
