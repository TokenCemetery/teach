---
title: 3. Bloat Diagnosis and Autovacuum Tuning
description: How to measure bloat, why autovacuum falls behind, and the diagnostic order that finds the actual cause instead of guessing
type: lesson
---

# Lesson 3. Bloat Diagnosis and Autovacuum Tuning

**Mission link:** This is stage 2's capstone: lesson 2 explained why dead tuples exist at all; this lesson is diagnosing when they've become a real problem, and finding which of several distinct causes is actually responsible before touching a setting.
**Primary source:** [Wiki: "Show database bloat", PostgreSQL Wiki](https://wiki.postgresql.org/wiki/Show_database_bloat)
**Prerequisites:** [Lesson 2](0002-mvcc-and-dead-tuples.md), [Write-ahead log (WAL)](../GLOSSARY.md)

## Warm-up

1. ▢ Why does a table under heavy `UPDATE` and `DELETE` traffic accumulate dead tuples, and why doesn't this resolve on its own?

<details markdown="1"><summary>Check</summary>

Every `UPDATE` and `DELETE` leaves the superseded row version in place until no transaction could still need to see it, and Postgres doesn't reclaim that space the instant it becomes dead. Nothing in ordinary read/write operation cleans it up; only vacuum does.

</details>

2. ▢ What does ordinary `VACUUM` do to a table's reclaimed space, and how does that differ from `VACUUM FULL`?

<details markdown="1"><summary>Check</summary>

Ordinary `VACUUM` marks dead tuples' space reusable within the table but doesn't shrink it on disk or return space to the OS. `VACUUM FULL` does return space to the OS, at the cost of an exclusive lock on the table for its duration.

</details>

## Know this

### Bloat is a gap that's normal in small amounts and a problem when it grows

**Bloat** is the gap between a table's actual live data and the storage it occupies on disk, caused by dead tuples accumulating faster than vacuum reclaims them. Some bloat is expected and harmless: space naturally builds up between vacuum runs and gets reclaimed on the next pass. The concern isn't bloat existing at all; it's bloat that keeps growing because vacuum genuinely isn't keeping pace with it.

### A quick smell test, then a real measurement

`pg_stat_user_tables` gives a fast, rough signal: `n_dead_tup` divided by `n_live_tup + n_dead_tup` is a directional bloat ratio, not an exact size measurement, but useful as a first check alongside `last_autovacuum`, when autovacuum last actually ran on that table. For an actual size-based estimate, a dedicated bloat-estimation query (this lesson's primary source provides one) measures the real gap between a table's live data size and its size on disk, which the dead-tuple ratio alone can't precisely capture.

### Three distinct causes, in a diagnostic order

A table with growing bloat has one of a few distinct root causes, and finding which one it is means checking in order, not tuning several settings at once:

1. **Is autovacuum even running and keeping pace?** Check `last_autovacuum` and whether the dead-tuple ratio is trending up over time or holding roughly steady. If autovacuum hasn't run recently at all, that's the first thing to fix.
2. **Is something holding back what vacuum can reclaim, even though it's running?** A single long-running transaction, an idle-in-transaction session, an uncommitted prepared transaction, or a stalled replication slot all hold back the oldest snapshot vacuum has to respect: vacuum cannot reclaim any dead tuple newer than that snapshot, no matter how many workers are configured or how aggressive the thresholds are. This is the case that looks the most confusing from the outside: autovacuum logs show it ran, on schedule, and bloat still climbs, because it genuinely couldn't reclaim anything held back by that older transaction. Checking `pg_stat_activity` for long-running or idle-in-transaction sessions, and `pg_replication_slots` for a stalled slot, is how this gets found.
3. **Is autovacuum triggering too late or running too slowly for this table's actual write rate?** The default trigger, `autovacuum_vacuum_scale_factor`, fires once roughly 20% of a table's rows have changed since the last vacuum. That percentage scales badly for a very large table: 20% of a million-row table is 200,000 dead tuples before autovacuum even considers it, by which point real bloat has already accumulated. Lowering the scale factor, or setting an absolute row-count threshold instead, for specifically large or high-churn tables is the fix once the first two causes are ruled out.

## Practice

1. ▢ A table shows `n_live_tup = 800,000` and `n_dead_tup = 200,000`. Compute the bloat ratio, and say whether this figure alone is alarming or merely worth watching.

<details markdown="1"><summary>Hint</summary>

`n_dead_tup / (n_live_tup + n_dead_tup)`.

</details>

<details markdown="1"><summary>Check</summary>

`200,000 / (800,000 + 200,000) = 0.20`, a 20% bloat ratio. On its own, this is a moderate figure worth watching, not necessarily alarming; what matters more is whether that ratio is climbing over time (autovacuum falling behind) or holding roughly steady (normal churn between vacuum runs).

</details>

2. ▢ A table's `n_dead_tup` is climbing steadily, but `last_autovacuum` shows it ran recently, meaning autovacuum is actually running. What's a likely cause that has nothing to do with autovacuum's own tuning, and how would you check for it?

<details markdown="1"><summary>Check</summary>

A long-running or idle-in-transaction session, an uncommitted prepared transaction, or a stalled replication slot holding back the oldest snapshot vacuum must respect, preventing it from reclaiming any dead tuple newer than that snapshot even though it ran on schedule. Check `pg_stat_activity` for long-running or idle-in-transaction sessions, and `pg_replication_slots` for a stalled slot.

</details>

3. ▢ Why does a single long-running transaction block vacuum from reclaiming dead tuples newer than it, regardless of how many autovacuum workers are configured or how aggressive the trigger thresholds are?

<details markdown="1"><summary>Check</summary>

Vacuum can only reclaim a dead tuple once no transaction could possibly still need to see it. A long-running transaction's snapshot may still be entitled to see row versions that later transactions have already superseded, so vacuum must leave those versions in place regardless of how many workers exist or how eagerly it's triggered; more workers or lower thresholds don't change what the oldest active snapshot still requires.

</details>

4. ▢ A large, high-churn table's default `autovacuum_vacuum_scale_factor` (roughly 20%) is too coarse to keep bloat under control. What's the fix, and why does a percentage-based trigger scale badly specifically for very large tables?

<details markdown="1"><summary>Check</summary>

Lower the scale factor for that table, or set an absolute row-count threshold instead of relying on the default percentage. A percentage-based trigger scales badly for large tables because the same 20% represents a much larger absolute number of dead tuples as the table grows; a million-row table has to accumulate 200,000 dead tuples before autovacuum even considers it, by which point substantial bloat has already built up.

</details>

5. ▢ Which claim is true of diagnosing table bloat?

    - a) A high dead-tuple ratio always means autovacuum's thresholds are misconfigured
    - b) A long-running transaction can prevent vacuum from reclaiming dead tuples even while autovacuum is running exactly on schedule
    - c) Autovacuum's default scale factor works equally well regardless of table size
    - d) The bloat ratio computed from pg_stat_user_tables is an exact measurement of disk space wasted

<details markdown="1"><summary>Check</summary>

**b)** That's exactly the confusing case this lesson names: vacuum runs, but a held-back snapshot means it can't reclaim anything. (a) is false: a held-back transaction can cause the same symptom with no threshold misconfiguration at all, which is why checking for one comes before retuning thresholds. (c) is false: the same percentage represents a much larger absolute dead-tuple count as a table grows. (d) is false: it's a directional estimate, not an exact size measurement; a dedicated bloat query is needed for that.

</details>

## Real-world reps

- [ ] On a Postgres instance you can access, compute the dead-tuple ratio for a few tables from `pg_stat_user_tables`, and check `pg_stat_activity` for any long-running or idle-in-transaction sessions that might be holding back vacuum.
- [ ] Run the primary source's bloat-estimation query against a table you suspect is bloated, and compare its estimate to the rough dead-tuple ratio.
- [ ] Tomorrow: find one table's `autovacuum_vacuum_scale_factor` setting (its own, or the server default) and decide whether it's appropriate for that table's actual size and churn rate.

## Going further

- [Wiki: "Show database bloat", PostgreSQL Wiki](https://wiki.postgresql.org/wiki/Show_database_bloat)
- [Docs: "Routine Vacuuming", PostgreSQL](https://www.postgresql.org/docs/current/routine-vacuuming.html)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
