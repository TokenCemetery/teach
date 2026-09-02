---
title: 35. Reading a Plan
description: The plan tells you what the database did and what it expected, and the gap between them is where the work is
type: lesson
---

# Lesson 35. Reading a Plan

**Mission link:** A plan is the only honest answer to "why is this slow", and every optimisation in this stage starts by reading one correctly rather than guessing at it.
**Primary source:** [PostgreSQL, 14.1 Using EXPLAIN](https://www.postgresql.org/docs/current/using-explain.html)
**Prerequisites:** [Lesson 2](0002-select-and-evaluation-order.md), [Lesson 9](0009-aggregation-and-group-by.md)

## Warm-up

1. ▢ Lesson 2 gave the order a `SELECT` is actually evaluated in, `FROM`/`JOIN`, `WHERE`, `GROUP BY`, `HAVING`, `SELECT`, `DISTINCT`, `ORDER BY`, `LIMIT`, regardless of how the query is written. For `SELECT count(*) FROM orders WHERE customer_id = 4242`, which of those two steps runs first, the filter on `customer_id` or the counting?

<details markdown="1"><summary>Check</summary>

The filter runs first: `WHERE` is step two and the aggregate that produces the count happens later, between `HAVING` and `SELECT`. A plan for this query keeps that same order, it just draws it as a tree with the filter at the bottom and the count above it, which is what the rest of this lesson reads.

</details>

## Know this

### What the two commands are for

`EXPLAIN` asks the planner what it would do and prints that plan with its cost estimates, nothing runs and nothing is measured. `EXPLAIN ANALYZE` runs the statement for real and adds what actually happened, actual row counts and actual buffer counts, at every node. The catch: the statement is actually executed, so `EXPLAIN ANALYZE` on an `UPDATE` performs the update, which PostgreSQL's own reference page flags under a heading called Important, with the fix given right there, `BEGIN; EXPLAIN ANALYZE ...; ROLLBACK;`. Run `update orders set amount = amount + 1 where id = 500000` inside `BEGIN` and the row's `amount` changes immediately, visible to a `SELECT` in the same transaction, with the plan's `Update on orders` node reporting `Buffers: shared hit=20 dirtied=2`, that `dirtied` count is pages the write touched; `ROLLBACK` undoes it and the row reads back to what it was. Make that wrapper a habit before running `EXPLAIN ANALYZE` on anything other than a `SELECT`.

### Reading the tree

A plan is a tree printed as indented text, and every line that starts a node describes one step. Indentation shows parent and child: a child is indented under the parent it feeds rows into, and a plan can have several children at one level or a single chain of them. Execution runs from the leaves upward, the most-indented node runs first and hands its output to the node above it, so the last thing that happens is whatever sits at the top with no indentation, which is also the first line printed. Here is the plan for the warm-up's query, with costs and counts stripped so only the shape shows:

```text
Finalize Aggregate
  ->  Gather
        Workers Planned: 2
        ->  Partial Aggregate
              ->  Parallel Seq Scan on orders
                    Filter: (customer_id = 4242)
```

Read it bottom to top. `Parallel Seq Scan on orders` runs first, checking `customer_id = 4242` row by row, the `WHERE` step from the warm-up. `Partial Aggregate` runs next, folding whatever each worker scanned into a running count per worker. `Gather` collects those partial counts from the two workers the plan asked for. `Finalize Aggregate`, printed first but executed last, adds the partial counts into the single number `count(*)` returns. Four lines, four steps, and execution runs in the reverse of the order they print in.

### The numbers that matter, and the ones you cannot reproduce

Add `ANALYZE` to that same plan and the tree fills in with what actually happened:

```text
Finalize Aggregate (actual rows=1.00 loops=1)
  Buffers: shared hit=7608
  ->  Gather (actual rows=3.00 loops=1)
        Workers Planned: 2
        Workers Launched: 2
        Buffers: shared hit=7608
        ->  Partial Aggregate (actual rows=1.00 loops=3)
              Buffers: shared hit=7608
              ->  Parallel Seq Scan on orders (actual rows=2.33 loops=3)
                    Filter: (customer_id = 4242)
                    Rows Removed by Filter: 349970
                    Buffers: shared hit=7608
```

`Rows Removed by Filter: 349970` is the count of rows this worker read and discarded because they failed `customer_id = 4242`, and it only ever appears on the node holding the filter, never above it. `rows` and `loops` read `2.33` and `3`: the scan ran three times, once per worker plus the leader, and `2.33` is the mean per run rather than the total, which accounts for the seven orders that customer actually has. `Buffers: shared hit=7608` repeats on every node, because a buffer the scan touched is counted by every node above it; `shared hit` is a page found in the server's cache and a `read` beside it would be one fetched from disk. `Workers Planned: 2` is what the planner asked for, matching this server's default `max_parallel_workers_per_gather` of `2`; `Workers Launched: 2` is what it actually got, and the two can differ when the server has no spare background worker process to hand over, a fact only `ANALYZE` can report since planning happens before execution. None of those numbers are timings, and that is deliberate: five runs of this exact query gave execution times spread by roughly five percent while `Buffers: shared hit=7608` came back identical on every one. A cost is in units the planner invented for comparing plans of one query against each other, never a promise about milliseconds, and a timing is a fact about the machine that ran it rather than a number to match. The counts are what reproduce on your own copy of this data, so this stage quotes counts and treats a timing as a ratio at most.

### Estimate against actual

`EXPLAIN` without `ANALYZE` prints the same shape with estimates in place of measurements, `cost=0.00..13076.31 rows=5 width=0` on that scan node instead of `actual rows=2.33 loops=3`, and reading a plan well means comparing the two. Walk the tree from the leaves up, as before, and at each node compare the estimated `rows` against the actual `rows` (`loops` multiplied out where a node ran more than once); the first node where the two disagree badly is where the planner's information about the data stopped matching the data. On `amount > 100` the planner estimated `rows=841386` for the scan and the run measured `actual rows=842067`, within a tenth of a percent:

```text
Seq Scan on orders  (cost=0.00..20826.45 rows=841386 width=0) (actual rows=842067.00 loops=1)
  Filter: (amount > '100'::numeric)
  Rows Removed by Filter: 212849
```

On `amount > 900` the same kind of scan estimated `rows=10` and the run measured `actual rows=1.00`:

```text
Seq Scan on orders  (cost=0.00..20826.45 rows=10 width=0) (actual rows=1.00 loops=1)
  Filter: (amount > '900'::numeric)
```

Ten times over what the query actually returned, on the same table, the same column, the same kind of node. That gap is the tell: something about what the planner believes `amount` looks like above `900` does not match this table, and a plan with more nodes above this one would carry that wrong number upward into every estimate built on it. Why the two queries land so differently is a question about the statistics the planner works from, and fixing that is lesson 37's subject; this lesson only teaches you to find the node where the disagreement starts.

### The options worth knowing

`EXPLAIN` takes a parenthesised list of options, and six are worth naming. `ANALYZE` runs the statement and adds actual counts, the subject of most of this lesson. `BUFFERS` adds the `Buffers` lines, and on release 18 you do not have to ask, `EXPLAIN ANALYZE` includes them automatically, a change release 18's own release notes describe as "Automatically include BUFFERS output in EXPLAIN ANALYZE". `COSTS OFF` removes the `cost=..` and estimated `rows=` figures, for when you want the shape rather than the estimates. `TIMING OFF` drops the per-node timings and keeps the counts. `SUMMARY OFF` drops the `Planning Time` and `Execution Time` lines, though a `Planning: Buffers` line still prints, being a count rather than a timing. `VERBOSE` adds each node's output columns and schema-qualifies names. `FORMAT JSON` renders the same tree as structured data for a program to parse rather than a person to read, nested the same way the indentation is:

```json
[{"Plan": {"Node Type": "Aggregate", "Plans": [
  {"Node Type": "Gather", "Workers Planned": 2, "Plans": [
    {"Node Type": "Aggregate", "Plans": [
      {"Node Type": "Seq Scan", "Relation Name": "orders", "Filter": "(amount > '900'::numeric)"}
    ]}
  ]}
]}}]
```

This stage's own habit for a plan meant to be read rather than parsed is `EXPLAIN (ANALYZE, COSTS OFF, TIMING OFF, SUMMARY OFF)`, dropping costs because an estimate is not the point once you have the actual counts, and dropping timings because a reader cannot reproduce them and should not try.

### What a plan does not tell you

A plan, even one with `ANALYZE`, is a report on one run against this data, under this server's current settings, at this moment, nothing more. Run it again after a large `DELETE`, after `ANALYZE` refreshes the statistics, or under a different `work_mem`, and the numbers can change without anything about the query changing. It also does not tell you whether the query was worth running in the first place: a plan can accurately and cheaply describe a query nobody needed, and confusing "the plan looks fine" with "this is not a problem" skips the question lesson 41 asks properly. What a plan reliably tells you is what this run did and what the planner expected before it ran, and the gap between those two is information about right now, not a permanent fact about the query.

## Practice

1. ▢ Two unrelated queries print costs of `445.00` and `20826.45`. Predict whether the second is slower to run than the first.

<details markdown="1"><summary>Check</summary>

No prediction is possible from cost alone. A cost is in units the planner invented for comparing plans of the *same* query against each other, and two different queries have no shared scale, so `20826.45` being a bigger number says nothing about wall-clock time.

</details>

2. ▢ A plan node reads `Parallel Seq Scan on orders (actual rows=2.33 loops=3)`. Predict the total number of rows this node returned across all three runs, and say what you would multiply to get it.

<details markdown="1"><summary>Check</summary>

About seven, from `2.33 * 3`. `rows` on a node with `loops` greater than one is the average per run, not a running total, so the total is always `rows` times `loops`, rounded to a whole row count.

</details>

3. ▢ You need to see why an `UPDATE` is slow, so you consider running `EXPLAIN ANALYZE` on it directly against production data. Predict what happens to the data, and name the three statements that make it safe.

<details markdown="1"><summary>Hint</summary>

`ANALYZE` on a `SELECT` only reads. What is different about a statement that writes?

</details>

<details markdown="1"><summary>Check</summary>

The update actually happens, exactly as running the statement plainly would, because `EXPLAIN ANALYZE` executes rather than simulates. `BEGIN`, `EXPLAIN ANALYZE`, `ROLLBACK` runs it, measures it, and undoes it.

</details>

4. ▢ A scan node's `Filter` condition removed `212849` rows and its `actual rows` came to `842067.00` over one loop. Predict how many rows that node read from the table in total.

<details markdown="1"><summary>Hint</summary>

Every row a scan touches either passes the filter or gets removed by it.

</details>

<details markdown="1"><summary>Check</summary>

`1054916`, from `842067 + 212849`. `Rows Removed by Filter` and `actual rows` between them account for every row the node examined, since a row that reaches the filter has no third outcome.

</details>

5. ▢ One plan shows `Buffers: shared hit=6244 read=1364` and a second run of the identical query moments later shows `Buffers: shared hit=7608`, no `read` at all. Predict what changed about the query between the two runs.

<details markdown="1"><summary>Check</summary>

Nothing about the query changed. The first run needed pages the cache did not yet hold, so `1364` were `read` from disk; by the second run those pages were cached, so they counted as `shared hit` instead, `6244 + 1364 = 7608` either way. The total is stable, only where the pages came from differs.

</details>

6. ▢ Walking a plan from the leaves up, the estimate on the bottom scan node is close to its actual, but the estimate on the node directly above it is far off. Predict where the wrong number in the plan first appears, and what you would do next.

<details markdown="1"><summary>Hint</summary>

The rule in this lesson is about the *first* node where estimate and actual disagree, read from the bottom.

</details>

<details markdown="1"><summary>Check</summary>

The bad estimate starts at that second node, not the leaf below it, since the leaf's own numbers already agreed. What to do about it, adjusting the planner's information, is lesson 37's subject, not this one; here the job stops at finding the node.

</details>

## Real-world reps

- [ ] Take a query you run often and run `EXPLAIN` on it with no `ANALYZE`, then read the tree bottom to top and say out loud what runs first.
- [ ] Run `EXPLAIN (ANALYZE, BUFFERS, COSTS OFF, TIMING OFF, SUMMARY OFF)` on the same query and compare its estimated `rows` against the actual `rows` at each node, noting the first node where they disagree.
- [ ] Tomorrow: find a slow `UPDATE` or `DELETE` in something you maintain and diagnose it with `BEGIN; EXPLAIN (ANALYZE); ROLLBACK;` rather than guessing from the query text alone.

## Going further

- [14.1.2. EXPLAIN ANALYZE](https://www.postgresql.org/docs/current/using-explain.html#USING-EXPLAIN-ANALYZE): the section behind this lesson's warning about writes
- [EXPLAIN](https://www.postgresql.org/docs/current/sql-explain.html): the reference page for every option this lesson used
- [E.6. Release 18](https://www.postgresql.org/docs/current/release-18.html): what changed in EXPLAIN's output that this lesson relies on
- [Performance](../reference/performance.md): the stage 6 reference sheet
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
