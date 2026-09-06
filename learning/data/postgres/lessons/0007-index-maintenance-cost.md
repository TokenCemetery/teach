---
title: 7. B-Tree, GiST, and GIN Maintenance Cost
description: Why every index makes writes more expensive, and how B-tree, GiST, and GIN each pay that cost differently
type: lesson
---

# Lesson 7. B-Tree, GiST, and GIN Maintenance Cost

**Mission link:** Stage 4 opens indexes and their upkeep: an index isn't a free read-speed lever, it's a real, ongoing write-time cost, and this lesson is what shape that cost takes for the three most common index types.
**Primary source:** [Docs: "Indexes", PostgreSQL](https://www.postgresql.org/docs/current/indexes.html)
**Prerequisites:** [Lesson 6](0006-diagnosing-replication-lag.md), [Write-ahead log (WAL)](../GLOSSARY.md)

## Warm-up

1. ▢ What does ordinary `VACUUM` do to a table's reclaimed space, and how does that differ from `VACUUM FULL`?

<details markdown="1"><summary>Check</summary>

Ordinary `VACUUM` marks dead tuples' space reusable within the table but doesn't shrink it on disk or return space to the OS. `VACUUM FULL` does return space to the OS, at the cost of an exclusive lock on the table for its duration.

</details>

2. ▢ Name the three-step order for diagnosing why a table's bloat keeps growing.

<details markdown="1"><summary>Check</summary>

Check whether autovacuum is running and keeping pace at all; if so, check for a long-running transaction or stalled replication slot holding back what it can reclaim; only then, check whether the trigger thresholds themselves are miscalibrated for the table's size.

</details>

## Know this

### An index makes every write more expensive, not just reads cheaper

Every `INSERT`, `UPDATE`, or `DELETE` on a table has to update every index defined on it, not only the table's own storage. An index that speeds up a `SELECT` does so at a direct, unavoidable cost paid on every write to that table, and that cost is paid again for each additional index, since each one is maintained independently. Adding an index is a real, ongoing cost decision, not a free lever that only helps.

### B-tree: cheap per write, until a page splits

**B-tree** is the default index type, built for equality and range queries with a balanced tree structure. Ordinary inserts are cheap: find the right leaf page and insert the entry there. The cost spikes when that leaf page is full: a **page split** allocates a new page and redistributes entries between the two, a more expensive operation than an ordinary insert. B-tree indexes also bloat the same way lesson 2's tables do: a deleted index entry isn't immediately compacted, just marked, so a page half full of dead entries still occupies the same space and still gets read on every lookup that touches it.

### GiST: flexible structure, more expensive per operation

**GiST (generalized search tree)** is a framework for building index structures for data that doesn't fit B-tree's assumption of a single total ordering, geometric data and certain full-text configurations among them. Its tree shape is conceptually similar to a B-tree, but the operations that decide how to descend into it or combine regions during an insert are custom, data-type-specific functions, generally more expensive per operation than a B-tree's simple comparison. GiST indexes built on overlapping regions (bounding boxes, for instance) can also degrade over time as those regions grow and overlap more, reducing search efficiency in a way ordinary vacuum doesn't fully reverse; a periodic `REINDEX` is what actually rebuilds the structure cleanly.

### GIN: expensive inserts, deliberately deferred

**GIN (generalized inverted index)** is built for values that decompose into many indexed elements: every word in a text search document, every element of an array, every key in a JSON document. It stores a mapping from each element back to the rows containing it, which means a single inserted row can require touching many separate entries in the index, an inherently more expensive insert than B-tree's single-leaf-page write. Postgres mitigates this with **fastupdate**: new entries go into a small pending list first, batched together, and get merged into the main GIN structure in bulk later, rather than updating the main structure entry by entry on every single insert. This trades some read cost (the pending list has to be checked alongside the main structure until it's cleaned up) for much cheaper writes, and the pending list itself needs periodic cleanup, via vacuum or an inline cleanup once it grows past `gin_pending_list_limit`, the same vacuum machinery from stage 2 now maintaining GIN's own internal structure rather than the table's dead tuples.

## Practice

1. ▢ Why does adding an index to a table make every `INSERT`, `UPDATE`, and `DELETE` on it more expensive, not just make `SELECT` queries cheaper?

<details markdown="1"><summary>Check</summary>

Every index defined on a table has to be updated whenever a row is inserted, changed, or removed, since the index's own structure needs to stay consistent with the table's data. That maintenance is paid on every write, independent of and in addition to whatever benefit the index provides to reads.

</details>

2. ▢ Describe what a B-tree page split is, and why it's the primary source of B-tree index bloat over time.

<details markdown="1"><summary>Check</summary>

When a leaf page is full and a new entry needs to be inserted there, a page split allocates a new page and redistributes the existing entries between the old and new pages. Bloat accumulates the same way it does in tables: a deleted index entry is marked but not immediately compacted, so pages can end up holding a mix of live and dead entries, still occupying and being read from the same space regardless of how much of it is actually live.

</details>

3. ▢ Why is GiST's per-operation maintenance generally more expensive than B-tree's, and what failure mode can degrade GiST search performance over time until a `REINDEX` is run?

<details markdown="1"><summary>Hint</summary>

Consider what GiST's insert operation has to compute that a B-tree's doesn't.

</details>

<details markdown="1"><summary>Check</summary>

GiST's insert relies on custom, data-type-specific comparison and combination functions to decide how to descend the tree and update regions, which are more expensive to compute than a B-tree's simple ordering comparison. Over time, overlapping regions (such as bounding boxes) can grow and overlap more, degrading search efficiency in a way ordinary vacuum doesn't fully reverse; a `REINDEX` rebuilds the structure cleanly instead.

</details>

4. ▢ Describe GIN's fastupdate/pending-list mechanism, the trade-off it makes, and vacuum's role in it.

<details markdown="1"><summary>Check</summary>

New entries are written to a small pending list first, batched together, rather than updating the main GIN structure entry by entry on every insert; the pending list is later merged into the main structure in bulk. This trades some read cost (queries have to check the pending list alongside the main structure until it's cleaned) for much cheaper writes. Vacuum (or an inline cleanup once the pending list exceeds `gin_pending_list_limit`) is what periodically merges and clears it, the same vacuum machinery from stage 2 applied to GIN's own internal structure.

</details>

5. ▢ Which claim is true of B-tree, GiST, and GIN index maintenance?

   - a) Adding an index only ever benefits a table, since reads get faster and writes are unaffected
   - b) Each index type trades some write cost for its particular read benefit, and that cost takes a different shape for each type (page splits for B-tree, expensive per-operation comparisons for GiST, deferred bulk inserts for GIN)
   - c) GIN's pending list eliminates the need for vacuum on GIN indexes entirely
   - d) GiST indexes never require anything beyond ordinary vacuum to maintain search performance

<details markdown="1"><summary>Check</summary>

**b)** Each type pays its maintenance cost differently, but none of them avoids paying it. (a) is false: every index adds write-time cost, regardless of type. (c) is false: the pending list itself needs vacuum (or an inline cleanup) to merge and clear it. (d) is false: overlapping-region degradation in GiST needs a `REINDEX`, not just ordinary vacuum, to fully recover.

</details>

## Real-world reps

- [ ] For a table you have access to, list its indexes and their types (B-tree, GiST, GIN), and note which ones are on columns with heavy write traffic.
- [ ] Check a GIN index's pending-list size (via `pg_stat_user_indexes` or a similar view) and whether `fastupdate` is enabled for it.
- [ ] Tomorrow: for one index you found, estimate whether its read benefit is worth the write cost it imposes, given the table's actual read and write patterns.

## Going further

- [Docs: "Indexes", PostgreSQL](https://www.postgresql.org/docs/current/indexes.html)
- [Docs: "Routine Vacuuming", PostgreSQL](https://www.postgresql.org/docs/current/routine-vacuuming.html)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
