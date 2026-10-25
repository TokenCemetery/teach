---
title: Stream Processing
description: "Compute over a stream with Kafka Streams: topologies, state, windows and joins, and what a topology costs before it reaches production"
type: topic
---

# Learning: Stream Processing

Be able to build, test and run a Kafka Streams application that gives the right answer when records arrive late, out of order or twice, and to say from its topology what internal topics, state and recovery time it will cost before it reaches production.

**Latest lesson:** [20. Changing a Topology Others Depend On](lessons/0020-changing-a-topology-others-depend-on.md)

## Success looks like

- Explain from the stream-table duality how a topic, a changelog and a KTable relate, and predict what a topology emits for a stated input.
- Build a topology with the DSL, read its `describe()` output, and name every internal topic it creates and why.
- Choose a state store for a stateful operation and say how its state is rebuilt when the instance holding it dies.
- Pick a window and a grace period for a time-based question, and state which late records it drops and when it emits a result.
- Choose a join for two inputs, make them co-partitioned or say why a GlobalKTable avoids the need, and predict the join's output.
- Say what `exactly_once_v2` guarantees and what it leaves out, and size an app's tasks, threads, instances and standby replicas for a stated recovery time.
- Test a topology with `TopologyTestDriver`, and operate a running app from its metrics, states and exception handlers.
- Decide between Kafka Streams, a plain consumer, Flink and ksqlDB for a workload, review someone else's topology, and change a running topology without breaking its state or its downstream consumers.

## Constraints

- Assumes working Java and the log as [`data/kafka`](../../data/kafka/) teaches it: partitions, consumer groups, delivery guarantees, retention and compaction. These lessons link back there rather than re-derive any of it.
- Kafka Streams is the only engine taught. Examples use the Java DSL and the Processor API of Apache Kafka 4.3.
- Defaults and protocols move between releases. Where a lesson quotes one it names the documentation page or the KIP it came from, and the reader should check that page for the current value.

## Out of scope

- The log itself: partitions, consumer groups, delivery semantics, the cost of transactions, retention and compaction, Kafka Connect and Schema Registry. See [`data/kafka`](../../data/kafka/), which this track builds on.
- Partial failure and consistency as theory: see [`architecture/distributed-systems`](../../architecture/distributed-systems/). This track teaches only what state-store recovery and rebalancing change for a Streams app.
- Apache Flink, Spark Structured Streaming and ksqlDB as subjects. Stage 8 compares them with Kafka Streams as candidates for a workload; it does not teach running them.
- The Java language: see [`programming/java`](../../programming/java/).
- Loading a stream into an analytical warehouse: see [`data/warehouses`](../../data/warehouses/).

## The arc

Eight stages, from the stream-table duality to judgment. A stage takes several lessons and the boundaries are soft; what makes a stage done is the capability, not the lesson count.

| Stage | Lessons | Covers | Done when |
|---|---|---|---|
| 1. Streams and tables | 0001 to 0002 | The stream-table duality, compacted topics as tables, what a Streams app runs and where | Can say whether a topic is read as a stream or a table, and what a Streams app adds to a consumer |
| 2. Topologies | 0003 to 0004 | The DSL, sources, processors and sinks, `describe()`, Serdes, stateless operations, key changes and repartition topics | Can read a topology and name every internal topic it creates |
| 3. State | 0005 to 0007 | State stores, changelog topics, aggregations, KTable updates, the record cache, the Processor API and punctuators | Can choose a store for a stateful step and say how its state survives an instance dying |
| 4. Time and windows | 0008 to 0010 | Event time, processing time and stream time, timestamp extractors, tumbling, hopping, sliding and session windows, grace periods, suppression | Can pick a window and grace period for a question and say which records it drops |
| 5. Joins | 0011 to 0012 | Stream-table and GlobalKTable joins, co-partitioning, windowed stream-stream joins, table-table and foreign-key joins | Can choose a join for two inputs and predict what it emits |
| 6. Guarantees and scaling | 0013 to 0015 | `exactly_once_v2`, tasks, threads and instances, rebalancing, state restoration, standby and warmup replicas, the streams rebalance protocol | Can say what exactly-once covers and size an app for a stated recovery time |
| 7. Testing and operating | 0016 to 0017 | `TopologyTestDriver`, metrics, client and thread states, exception handlers, interactive queries, the operator tools | Can test a topology without a broker and tell from its metrics whether a running app is healthy |
| 8. Judgment | 0018 to 0020 | Streams against a plain consumer, Flink and ksqlDB, reviewing a topology, changing a topology others depend on, settling a dispute from the source | Trusted to make the call and to explain it to someone else |

## Lessons

Work through these in order.

| # | Lesson | Teaches |
|---|---|---|
| [0001](lessons/0001-streams-and-tables.md) | Streams and Tables | Why a stream of changes and a table of current values are two views of the same data, and how a topic holds either |
| [0002](lessons/0002-a-streams-app-is-a-library.md) | A Streams App Is a Library | What runs when a Kafka Streams application starts: consumers, producers and local state inside your own process, with no cluster of its own |
| [0003](lessons/0003-the-dsl-and-topologies.md) | The DSL and Topologies | How DSL calls build a topology of sources, processors and sinks, and how to read one from `describe()` |
| [0004](lessons/0004-stateless-operations-and-repartitioning.md) | Stateless Operations and Repartitioning | Which operations transform one record at a time, and which key change makes the next stateful step write a repartition topic |
| [0005](lessons/0005-state-stores-and-changelog-topics.md) | State Stores and Changelog Topics | Where a stateful operation keeps its state, and how a compacted changelog topic lets another instance rebuild it |
| [0006](lessons/0006-aggregations-ktables-and-the-record-cache.md) | Aggregations, KTables and the Record Cache | Why a KTable emits a stream of updates rather than final answers, and how the record cache and commit interval decide how many |
| [0007](lessons/0007-the-processor-api.md) | The Processor API | When to drop below the DSL to a custom processor with its own store and punctuator, and what you then own |
| [0008](lessons/0008-event-time-processing-time-and-stream-time.md) | Event Time, Processing Time and Stream Time | Which clock a Streams operation follows, where a record's timestamp comes from, and why stream time only moves forward |
| [0009](lessons/0009-windowed-aggregations.md) | Windowed Aggregations | How tumbling, hopping, sliding and session windows group records by time, and which question each one answers |
| [0010](lessons/0010-late-data-grace-periods-and-suppression.md) | Late Data, Grace Periods and Suppression | How long a window accepts out-of-order records, what happens to the ones after, and how to emit only a final result |
| [0011](lessons/0011-stream-table-joins-and-co-partitioning.md) | Stream-Table Joins and Co-Partitioning | How a stream enriches each record from a table, why both sides must be co-partitioned, and when a GlobalKTable removes that need |
| [0012](lessons/0012-stream-stream-and-table-table-joins.md) | Stream-Stream and Table-Table Joins | How a windowed join pairs events from two streams, and how table joins, foreign-key joins included, keep a result current |
| [0013](lessons/0013-exactly-once-in-kafka-streams.md) | Exactly-Once in Kafka Streams | What `exactly_once_v2` makes atomic across reads, state and writes, and which side effects it cannot cover |
| [0014](lessons/0014-tasks-threads-and-scaling-out.md) | Tasks, Threads and Scaling Out | How partitions become tasks, how tasks spread over threads and instances, and what caps an app's parallelism |
| [0015](lessons/0015-rebalancing-restoration-and-standby-replicas.md) | Rebalancing, Restoration and Standby Replicas | What happens to state when a task moves, and how standby and warmup replicas shorten the time it is unavailable |
| [0016](lessons/0016-testing-with-topologytestdriver.md) | Testing with TopologyTestDriver | How to test a topology's output, state and time behaviour in a unit test with no broker |
| [0017](lessons/0017-operating-and-monitoring-a-streams-app.md) | Operating and Monitoring a Streams App | The metrics, states and exception handlers that tell you whether a running app is healthy, and what to do when it is not |
| [0018](lessons/0018-when-kafka-streams-is-the-wrong-tool.md) | When Kafka Streams Is the Wrong Tool | When a plain consumer, Flink or ksqlDB fits a workload better than a Streams app, and how to defend the call |
| [0019](lessons/0019-reviewing-someone-elses-topology.md) | Reviewing Someone Else's Topology | How to review a Streams topology and name what each choice costs in internal topics, state and correctness |
| [0020](lessons/0020-changing-a-topology-others-depend-on.md) | Changing a Topology Others Depend On | How to change a running app's topology without corrupting its state or breaking downstream consumers, and how to settle a disputed claim from the source |

## Reference

- [Glossary](GLOSSARY.md): canonical terms for this topic
- [Resources](RESOURCES.md): trusted sources, each annotated with what it covers
- [DSL Operations](reference/dsl-operations.md): every DSL operation by input and output type, whether it keeps state, and whether it repartitions
- [State Stores](reference/state-stores.md): store types, changelog settings, the record cache, and how state is restored
- [Time and Windows](reference/time-and-windows.md): the three clocks, the four window types, grace periods and when each emits
- [Joins](reference/joins.md): the join matrix, with windowing, co-partitioning and what each join emits
- [Configuration](reference/configuration.md): the settings that decide guarantees, latency, parallelism and recovery, with their defaults
- [Operations](reference/operations.md): the metrics to watch, client and thread states, exception handlers and the operator tools
- [Topology Review](reference/topology-review.md): a checklist for reviewing a topology, the tool decision, and safe and unsafe topology changes

## How this works

Each lesson is short and self-contained. Answer keys are collapsed: recall first, then open them. The real-world reps matter more than the reading, and spacing them out is the point. Anything still unclear at the end of a lesson is worth chasing to its primary source before moving on.
