---
title: 8. What a pgvector Index Costs to Keep
description: The disk, build-time, and standing-memory cost a vector index adds beyond the raw vectors it indexes
type: lesson
---

# Lesson 8. What a pgvector Index Costs to Keep

**Mission link:** This is stage 4's capstone: `llm/rag` derives why HNSW behaves the way it does and how to tune it for retrieval quality; this workspace's job is naming what that structure actually costs the Postgres instance operating it, day to day, not just at query time.
**Primary source:** [Repo: pgvector, pgvector](https://github.com/pgvector/pgvector)
**Prerequisites:** [Lesson 7](0007-index-maintenance-cost.md), [Write-ahead log (WAL)](../GLOSSARY.md)

## Warm-up

1. ▢ Why does adding an index to a table make every write to it more expensive, regardless of the index's type?

<details markdown="1"><summary>Check</summary>

Every index defined on a table has to be updated whenever a row is inserted, changed, or removed, to keep the index's structure consistent with the table. That maintenance is paid on every write, in addition to whatever an index type's specific mechanics cost.

</details>

2. ▢ What trade-off does GIN's fastupdate/pending-list mechanism make, and what cleans up the pending list?

<details markdown="1"><summary>Check</summary>

It defers new entries into a small pending list, batching them for a later bulk merge instead of updating the main structure on every insert, trading some read cost (checking the pending list too) for much cheaper writes. Vacuum, or an inline cleanup once the list exceeds a configured limit, merges and clears it.

</details>

## Know this

### The index itself can be larger than the vectors it stores

An HNSW index doesn't just store a copy of the vectors it indexes; it stores the graph structure connecting them, edges linking each vector to a bounded number of neighbors across multiple layers. Unlike a B-tree index, which is typically much smaller than the table it indexes, an HNSW index's graph overhead can make the index substantially larger than the raw vector data alone, since every vector carries connections to potentially dozens of neighbors, all of which need to be stored and kept updated.

### Build time is a real planning concern, not an afterthought

Building an HNSW index scales with the size of the data and grows further with the parameters chosen for it (larger `m` or `ef_construction` mean more, and more expensive, work per vector during the build). For a large table, this build can take a long time and requires a meaningful amount of `maintenance_work_mem`; too little configured for the build can force a much slower fallback path. Sizing this correctly, and planning for how long a rebuild will actually take, is an operational decision the same way lesson 7's index types each demanded their own maintenance planning.

### It still interacts with vacuum, and the details have genuinely changed across versions

Deleted or updated rows still leave index entries that need reclaiming, the same underlying concern as every other index type this workspace has covered. How gracefully pgvector's HNSW implementation handles this has changed across its own version history; earlier versions handled update-heavy workloads on HNSW less gracefully than more recent ones. This is a case where checking the specific pgvector version's current release notes matters directly, rather than assuming behavior documented once stays fixed: the mechanics an operator needs to plan around here are exactly the kind of thing that changes between releases of an actively developed extension.

### The cost that matters most in production: staying resident in memory

An HNSW index has to be resident in memory (Postgres's shared buffers, or read from disk otherwise, far slower) to answer queries at the speed it's built for. For a large vector table, the index alone can require a substantial fraction of the instance's available memory, competing directly with everything else that same Postgres instance is running: other tables' data, other indexes, WAL buffers, and any other workload sharing the server. This is the operational question the mission's success criterion is actually asking: not just what it costs to build a vector index once, but what it costs to keep it fast, continuously, alongside everything else the instance has to do.

## Practice

1. ▢ Why can an HNSW index be substantially larger on disk than the raw vector data it indexes, unlike a typical B-tree index relative to its table?

<details markdown="1"><summary>Check</summary>

HNSW stores a graph structure connecting vectors to their neighbors across multiple layers, not just the vectors themselves. Each vector carries edges to potentially many neighbors, and all of that connectivity has to be stored and maintained, which can add up to more space than the raw vectors alone, unlike a B-tree, which is typically much smaller than the table it indexes.

</details>

2. ▢ What operational concern does HNSW's build time interact with, and why does `maintenance_work_mem` matter for it?

<details markdown="1"><summary>Check</summary>

Building an HNSW index for a large table can take a long time, and it needs a meaningful amount of working memory to build efficiently; too little `maintenance_work_mem` configured for the build can force a much slower fallback path. Planning how long a build or rebuild will actually take, and sizing that memory correctly ahead of time, is a real operational decision, not something to discover partway through a build.

</details>

3. ▢ Why does a large HNSW index's need to stay memory-resident for fast queries create a real trade-off with everything else the same Postgres instance is running?

<details markdown="1"><summary>Hint</summary>

Think about what else is competing for the same memory.

</details>

<details markdown="1"><summary>Check</summary>

An HNSW index answers queries at its designed speed only while resident in memory; falling back to disk reads is far slower. A large vector table's index can require a substantial fraction of the instance's available memory to stay resident, competing directly with everything else sharing that memory: other tables, other indexes, WAL buffers, and any other workload on the same server, which is a standing cost, not a one-time build expense.

</details>

4. ▢ Why should an operator check the specific pgvector version's release notes rather than assume update and delete behavior on an HNSW index is fixed and documented once?

<details markdown="1"><summary>Check</summary>

How gracefully pgvector's HNSW implementation handles updates and deletes has genuinely changed across its version history; earlier versions handled update-heavy workloads less gracefully than more recent ones. Assuming a fixed, once-documented behavior risks planning around mechanics that no longer match the version actually running, which is exactly the kind of thing that changes between releases of an actively developed extension.

</details>

5. ▢ Which claim is true of what a pgvector HNSW index costs to keep?

    - a) Its disk footprint is always smaller than the raw vectors it indexes, the same as a typical B-tree
    - b) It costs disk space beyond the raw vectors (graph structure), a real build-time resource requirement, and a standing memory cost that competes with everything else the instance runs
    - c) Once built, an HNSW index requires no further interaction with vacuum
    - d) pgvector's update and delete handling for HNSW has been identical across every version of the extension

<details markdown="1"><summary>Check</summary>

**b)** All three costs, disk, build-time, and standing memory, are real and ongoing. (a) is false: HNSW's graph overhead can make it larger than the raw vectors, unlike a typical B-tree. (c) is false: deleted or updated rows still leave entries that need reclaiming. (d) is false: this behavior has genuinely changed across pgvector's version history, which is why checking current release notes matters.

</details>

## Real-world reps

- [ ] For a pgvector table you have access to, or a hypothetical one sized to a real workload, estimate the HNSW index's disk footprint relative to the raw vector data, using pgvector's documented parameters.
- [ ] Check what `maintenance_work_mem` is currently configured to on an instance you operate, and whether it's sized for building or rebuilding a vector index of the size you expect.
- [ ] Tomorrow: check the release notes for the pgvector version you're running (or planning to run) for anything about HNSW update or delete handling that's changed recently.

## Going further

- [Repo: pgvector, pgvector](https://github.com/pgvector/pgvector)
- [RAG](../../../llm/rag/README.md): `llm/rag`'s workspace, which derives why HNSW behaves the way it does and how to tune it for retrieval quality
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
