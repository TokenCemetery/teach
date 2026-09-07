---
title: 10. Defending an Operating Choice
description: A worked deployment design that cites a specific decision and cost from each stage, rather than assuming a default answer
type: lesson
---

# Lesson 10. Defending an Operating Choice

**Mission link:** This is the final lesson of the arc: designing storage, replication, and index maintenance for a real deployment, and defending managed versus self-hosted, means naming a specific decision and its cost from every stage this workspace covered, not picking a default.
**Primary source:** [Docs: "PostgreSQL on Amazon RDS", AWS](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_PostgreSQL.html)
**Prerequisites:** [Lesson 9](0009-what-managed-shields-you-from.md), [Write-ahead log (WAL)](../GLOSSARY.md)

## Warm-up

1. ▢ What changes about a database's operation when it moves to a managed service, and what doesn't?

<details markdown="1"><summary>Check</summary>

Access and tooling change: patching, backups, and failover automation get handled by the provider, through whatever interface it exposes. The underlying mechanisms, vacuum and bloat, replication lag, index maintenance cost, don't change at all; they still happen and still need understanding to operate the instance well.

</details>

2. ▢ What does an HNSW index need beyond just disk space for the raw vectors?

<details markdown="1"><summary>Check</summary>

Graph-structure overhead on disk that can exceed the raw vector data's own size, a meaningful amount of `maintenance_work_mem` at build time, and standing memory residency at query time to answer at its designed speed.

</details>

## Know this

### A defended design names a decision and its cost, for every stage

A deployment design that says "we chose Postgres, and RDS, because it's popular" hasn't defended anything. A defended design pulls one concrete decision, and the number or trade-off behind it, from each stage this workspace covered.

**Durability and replication (lessons 1, 4, 5):** state the workload's actual RPO (how much recently committed data is acceptable to lose) and choose synchronous or asynchronous replication accordingly, citing the commit-latency cost synchronous replication adds in exchange for bounding that loss to zero. Decide whether a replication slot is warranted for a given standby, and weigh that against lesson 4's abandoned-slot risk if that standby is ever decommissioned without dropping its slot.

**Vacuum and autovacuum (lessons 2, 3):** name the write and update pattern each major table actually has, and tune `autovacuum_vacuum_scale_factor` (or an absolute threshold) per table rather than leaving every table on one global default, since lesson 3 established that the same percentage represents wildly different absolute dead-tuple counts on a small table versus a very large one.

**Index strategy (lessons 7, 8):** for every planned index, name its type and the write-cost it imposes on the table it protects, and for a vector index specifically, size disk and `maintenance_work_mem` for its build, and confirm the standing memory it needs to stay resident actually fits the instance's budget alongside everything else running there.

**Managed versus self-hosted (lesson 9):** weigh the team's actual operational capacity to monitor and diagnose vacuum, replication lag, and index cost themselves against what a managed service would automate and what it would still leave them responsible for understanding, and check whether a required extension (pgvector, for a RAG-backed table) is actually supported by the specific managed offering being considered.

### A worked example, pulling from every stage

A small team is building a chat application backed by a pgvector-based RAG pipeline, with limited operations experience and no dedicated database administrator. They need near-zero data loss if the primary fails (a tight RPO), but they're also latency-sensitive, since users are waiting on a live chat response.

Their defended design: synchronous replication for the durability requirement, accepting the added commit latency it costs, since a chat response's total latency budget can absorb one extra network round trip better than the business can absorb losing a user's data. Given no dedicated DBA, a managed service, one confirmed to support pgvector specifically, since their RAG pipeline depends on it. They still need to actively monitor replication lag and bloat through whatever dashboard the managed service exposes, since lesson 9 established a managed service automates failover and patching, not the need to watch for a lagging replica or a table whose autovacuum has fallen behind. Their embeddings table, given heavy update traffic as documents get re-embedded, needs its autovacuum thresholds tuned tighter than the default, and, per lesson 8's version caveat, they check the specific pgvector version's current release notes for how gracefully it handles update-heavy HNSW workloads before committing to that design.

## Practice

1. ▢ A team wants near-zero data loss on failover (a tight RPO) for a chat application, but is also latency-sensitive since users wait on live responses. What replication mode should they choose, and what concrete cost are they accepting in exchange?

<details markdown="1"><summary>Check</summary>

Synchronous replication, accepting the added commit latency (a network round trip to the synchronous standby on every commit) in exchange for bounding failover data loss to zero for committed transactions. The defense names both sides: the RPO requirement that forced the choice, and the latency cost paid for it.

</details>

2. ▢ The same team has limited operations experience and no dedicated DBA. Should they lean toward a managed service or self-hosting, and what would a managed service still require them to understand and monitor, per lesson 9?

<details markdown="1"><summary>Check</summary>

A managed service, given their limited operational capacity: it automates patching, backups, and failover detection and promotion, tasks they'd otherwise have to build and run themselves. It would still require them to monitor replication lag and bloat through whatever dashboard it exposes, since those mechanisms still exist and still need watching regardless of who patches the server or triggers a failover.

</details>

3. ▢ Their pgvector table has heavy update traffic, since embeddings get regenerated frequently. What autovacuum tuning consideration from lesson 3 applies, and what does lesson 8 say to check about their specific pgvector version?

<details markdown="1"><summary>Check</summary>

Lesson 3's consideration: the default `autovacuum_vacuum_scale_factor` may trigger too late for a table with this much churn, so tightening the threshold (or setting an absolute row-count trigger) for this specific table is warranted, rather than relying on a global default sized for a typical table. Lesson 8's check: how gracefully HNSW handles update-heavy workloads has genuinely changed across pgvector's version history, so the specific version's current release notes need checking before assuming it will hold up under this traffic pattern.

</details>

4. ▢ List what a complete, defended deployment design needs to name, pulling one decision from each of this workspace's five stages.

<details markdown="1"><summary>Check</summary>

Durability and replication (stages 1 and 3): the RPO target and the replication mode (sync or async) chosen to meet it, with its cost. Vacuum (stage 2): the per-table autovacuum tuning appropriate to each table's actual write pattern. Indexes (stage 4): each planned index's type and the write cost it imposes, and for a vector index, its disk, build-time, and standing-memory requirements. Managed versus self-hosted (stage 5): the team's operational capacity weighed against what a managed service would and wouldn't shield them from, and whether a required extension is actually supported.

</details>

5. ▢ Which claim is true of defending a Postgres deployment design?

    - a) Choosing a popular, well-known configuration is sufficient defense on its own
    - b) A defended design cites a specific decision and its measured or acknowledged cost from each relevant stage, not a default choice made without justification
    - c) Managed services remove the need to make any of these decisions, since the provider decides for you
    - d) RPO and replication mode are unrelated to index or vacuum strategy, so each can be decided independently with no shared context

<details markdown="1"><summary>Check</summary>

**b)** That's exactly the standard this lesson's worked example holds itself to. (a) is false: popularity says nothing about whether a specific choice fits a specific workload's requirements. (c) is false: a managed service still requires the operator to choose replication mode, monitor lag and bloat, and confirm extension support. (d) is false: the worked example ties them together under one workload's actual requirements, not as independent, contextless choices.

</details>

## Real-world reps

- [ ] For a Postgres deployment you run or are designing, write out a defended answer for each of this lesson's four areas: durability/replication, vacuum tuning, index strategy, and managed versus self-hosted.
- [ ] If you're using or considering pgvector, confirm your specific managed provider (if any) supports it, and check its current release notes for HNSW update-handling behavior.
- [ ] Tomorrow: revisit this workspace's mission in `README.md` and confirm, in your own words, that you can diagnose a bloated table or a lagging replica from first principles, and defend a full deployment design rather than guessing at one.

## Going further

- [Docs: "PostgreSQL on Amazon RDS", AWS](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_PostgreSQL.html)
- [Docs: "High Availability, Load Balancing, and Replication", PostgreSQL](https://www.postgresql.org/docs/current/high-availability.html)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
