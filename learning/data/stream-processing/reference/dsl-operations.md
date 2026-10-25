---
title: DSL Operations
description: Every DSL operation by input and output type, whether it keeps state, and whether it repartitions
type: reference
---

# DSL Operations

Stages 1 and 2 compressed for lookup: [lesson 1](../lessons/0001-streams-and-tables.md) (streams and tables), [lesson 2](../lessons/0002-a-streams-app-is-a-library.md) (what an app runs), [lesson 3](../lessons/0003-the-dsl-and-topologies.md) (topologies and `describe()`) and [lesson 4](../lessons/0004-stateless-operations-and-repartitioning.md) (stateless operations and repartitioning). The stateful rows are taught in stages 3 to 5; they are here so one sheet answers "does this step keep state, and does it add a topic".

Read from the Apache Kafka 4.3 documentation, javadoc and source in October 2026. Each table names its page; check it for the current behaviour.

## How to read the columns

| Column value | Meaning |
|---|---|
| **State: none** | One record at a time, no state store |
| **State: store** | Owns a state store, backed by a changelog topic unless logging is disabled |
| **Repartition: never** | Never creates a repartition topic |
| **Repartition: marks** | Creates nothing itself, but marks the stream, so the next step that needs grouping by key repartitions |
| **Repartition: if marked** | Creates a repartition topic only when the incoming stream is marked |
| **Repartition: always** | Creates a repartition topic every time |

A mark passes unchanged through every operation that keeps the key. It is paid, once, by the first operation that needs records grouped by key in one task.

## Source operations

| Call | Output | State | Notes |
|---|---|---|---|
| `StreamsBuilder#stream(topics)` | KStream | none | Record stream: every record an event. Each instance reads only its assigned partitions |
| `StreamsBuilder#table(topic)` | KTable | store | Changelog stream: a non-null value is an upsert, a null value a delete. Give the store a name to make it queryable |
| `StreamsBuilder#globalTable(topic)` | GlobalKTable | store | Every instance reads every partition, and the table is bootstrapped before processing starts |

Page: [Streams DSL: Creating source streams from Kafka](https://kafka.apache.org/43/streams/developer-guide/dsl-api/#creating-source-streams-from-kafka).

## KStream: stateless and terminal

| Operation | Input to output | State | Repartition | Notes |
|---|---|---|---|---|
| `filter`, `filterNot` | KStream to KStream | none | never | Keeps the mark if present |
| `mapValues` | KStream to KStream | none | never | Prefer over `map` whenever the key stays |
| `flatMapValues` | KStream to KStream | none | never | Prefer over `flatMap` whenever the key stays |
| `map` | KStream to KStream | none | marks | Marks even if the lambda returns the same key |
| `flatMap` | KStream to KStream | none | marks | Each output record inherits the input timestamp |
| `selectKey` | KStream to KStream | none | marks | Same as `map` that keeps the value |
| `split` | KStream to BranchedKStream | none | never | First matching predicate wins; then `defaultBranch` or `noDefaultBranch` (drop). Branches inherit the mark |
| `merge` | KStream, KStream to KStream | none | never | No order across the two inputs. Marked if either input was |
| `peek` | KStream to KStream | none | never | Side effect outside Kafka's guarantees |
| `foreach` | KStream to nothing | none | never | Terminal side effect |
| `print` | KStream to nothing | none | never | Debugging only; flushes on every record |
| `to` | KStream to nothing | none | never | Writes by key through the producer's partitioner. No internal topic, even on a marked stream |
| `repartition` | KStream to KStream | none | always | Clears the mark. `Repartitioned` sets name, partition count, Serdes and partitioner |
| `toTable` | KStream to KTable | store if materialized | if marked | Null keys dropped |
| `process` | KStream to KStream | store if you attach one | marks | Never repartitions its own input; call `repartition()` first if it needs grouping by key |
| `processValues` | KStream to KStream | store if you attach one | never | Key is fixed, so the mark is kept, not added |

Pages: [Streams DSL: Stateless transformations](https://kafka.apache.org/43/streams/developer-guide/dsl-api/#stateless-transformations), [Streams DSL: Applying processors](https://kafka.apache.org/43/streams/developer-guide/dsl-api/#operations-and-concepts), [KStream javadoc](https://kafka.apache.org/43/javadoc/org/apache/kafka/streams/kstream/KStream.html). Mark propagation through `filter`, `split`, `merge`, `peek` and `processValues`, and the cleared mark after `repartition`, are read from [KStreamImpl in the 4.3 source](https://github.com/apache/kafka/blob/4.3/streams/src/main/java/org/apache/kafka/streams/kstream/internals/KStreamImpl.java).

## Grouping and aggregation

| Operation | Input to output | State | Repartition | Notes |
|---|---|---|---|---|
| `groupByKey` | KStream to KGroupedStream | none | if marked | The repartition is created by the aggregation that follows, not by this call |
| `groupBy` | KStream to KGroupedStream | none | always | Shorthand for `selectKey(...).groupByKey()` |
| `groupBy` | KTable to KGroupedTable | none | always | Can change value and value type too |
| `cogroup` | KGroupedStream to CogroupedKStream | none | never | Inputs are already grouped, so already repartitioned where needed |
| `windowedBy` | KGroupedStream to a windowed grouped stream | none | never | Windowing applies at the aggregation (lesson 9) |
| `count`, `reduce`, `aggregate` | KGroupedStream to KTable | store | pays the mark | Null keys ignored. `count` also ignores null values |
| `count`, `reduce`, `aggregate` | KGroupedTable to KTable | store | pays the repartition | Needs a subtractor for `reduce` and `aggregate`; a tombstone calls only the subtractor |
| `count`, `reduce`, `aggregate` | Windowed grouped stream to `KTable<Windowed<K>, V>` | window or session store | pays the mark | Records after window end plus grace are dropped (lesson 10) |
| `aggregate` | CogroupedKStream to KTable | store | never | Aggregators were given in each `cogroup` call |

Pages: [Streams DSL: Stateless transformations](https://kafka.apache.org/43/streams/developer-guide/dsl-api/#stateless-transformations) (grouping rows), [Streams DSL: Aggregating](https://kafka.apache.org/43/streams/developer-guide/dsl-api/#aggregating).

## KTable

| Operation | Input to output | State | Repartition | Notes |
|---|---|---|---|---|
| `filter`, `filterNot` | KTable to KTable | store if materialized | never | A filtered-out update is forwarded as a delete for its key |
| `mapValues` | KTable to KTable | store if materialized | never | |
| `transformValues` | KTable to KTable | store if you attach one | never | The Processor API hook on a table |
| `toStream()` | KTable to KStream | none | never | The table's changelog as a record stream |
| `toStream(mapper)` | KTable to KStream | none | marks | Same as `toStream().selectKey(mapper)` |
| `suppress` | KTable to KTable | buffer store | never | Holds updates back (lesson 10) |
| `groupBy` | KTable to KGroupedTable | none | always | See grouping above |

Pages: [Streams DSL: Stateless transformations](https://kafka.apache.org/43/streams/developer-guide/dsl-api/#stateless-transformations), [KTable javadoc](https://kafka.apache.org/43/javadoc/org/apache/kafka/streams/kstream/KTable.html). The `toStream(mapper)` equivalence is read from [KTableImpl in the 4.3 source](https://github.com/apache/kafka/blob/4.3/streams/src/main/java/org/apache/kafka/streams/kstream/internals/KTableImpl.java).

## Joins

| Join | Inner, left, outer | Output | State | Repartition | Co-partitioning |
|---|---|---|---|---|---|
| KStream with KStream, windowed | all three | KStream | Window store per side; left and outer add a buffer store | if marked, each side | Required |
| KStream with KTable | inner, left | KStream | Reads the table's store | if marked, stream side | Required |
| KStream with GlobalKTable | inner, left | KStream | Reads the global store | never | Not required; join on any field via a key selector |
| KTable with KTable | all three | KTable | Reads both tables' stores | never | Required |
| KTable with KTable, foreign key | inner, left | KTable | Subscription store | Internal subscription and response topics | Not required |
| KTable with GlobalKTable | none | | | | Not supported |

Pages: [Streams DSL: Joining](https://kafka.apache.org/43/streams/developer-guide/dsl-api/#joining), [KStream javadoc](https://kafka.apache.org/43/javadoc/org/apache/kafka/streams/kstream/KStream.html), [KIP-213](https://cwiki.apache.org/confluence/display/KAFKA/KIP-213+Support+non-key+joining+in+KTable). The DSL guide's GlobalKTable rows say a marked stream is repartitioned; the javadoc states no co-partitioning requirement, and the 4.3 source adds no repartition step for that join.

Kafka Streams checks only that both sides of a co-partitioned join have the same partition count, and throws at assignment if not. It cannot check that both were written with the same partitioner.

## Naming a repartition topic

The broker name is always `<application.id>-<name>-repartition`.

| Repartition made by | `<name>` |
|---|---|
| Aggregation after `groupByKey(Grouped.as("x"))` or `groupBy(..., Grouped.as("x"))` | `x` |
| Aggregation with no `Grouped` name | The store name: the one in `Materialized.as(...)`, or a generated `KSTREAM-AGGREGATE-STATE-STORE-` name |
| `repartition(Repartitioned.as("x"))` | `x` |
| `toTable(Named.as("x"))` | `x` |
| A join of a marked stream | Set through `Joined` or `StreamJoined`, else generated |

`describe()` prints the name without the application ID prefix. A generated name shifts when an operator is added upstream, which renames the topic on the next deploy (lesson 20).

Pages: [KStream javadoc](https://kafka.apache.org/43/javadoc/org/apache/kafka/streams/kstream/KStream.html), [GroupedStreamAggregateBuilder in the 4.3 source](https://github.com/apache/kafka/blob/4.3/streams/src/main/java/org/apache/kafka/streams/kstream/internals/GroupedStreamAggregateBuilder.java).

## Internal topic defaults

| Topic | Cleanup policy | Retention |
|---|---|---|
| Repartition | `delete` | Infinite (`-1`); Kafka Streams purges records it has consumed |
| Changelog of a key-value store | `compact` | Not time bounded |
| Changelog of a window store | `delete,compact` | Window store retention plus 24 hours |
| Changelog of a versioned store | `compact`, with `min.compaction.lag.ms` set to history retention plus 24 hours | Not time bounded |

Every internal topic has `message.timestamp.type=CreateTime`. Override settings for all of them with the `topic.` prefix in the Streams config. Pages: [Managing Streams Application Topics](https://kafka.apache.org/43/streams/developer-guide/manage-topics/), [Configuring a Streams Application](https://kafka.apache.org/43/streams/developer-guide/config-streams/).

## Traps worth checking

- A `map` that keeps the key, followed by a grouping: a repartition topic for nothing. Use `mapValues`.
- `groupBy` where the stream is already keyed by the grouping key: use `groupByKey`.
- A key change before `process()` that needs grouping by key: `process()` will not repartition. Add `repartition()`.
- A stateful `process()` whose output then feeds a grouping: `process()` itself marks the stream, so expect a repartition.
- A count or table written with `to()` and no `Produced`: the default Serde meets a `Long` at run time.
- A KStream read from a compacted topic: compaction deletes events, and every count over it drifts.
- Unnamed groupings in a topology that will change: generated repartition and store names shift and orphan their topics.

## Sources

- [Docs: "Streams DSL", Apache Kafka 4.3](https://kafka.apache.org/43/streams/developer-guide/dsl-api/)
- [Javadoc: "KStream", Apache Kafka 4.3](https://kafka.apache.org/43/javadoc/org/apache/kafka/streams/kstream/KStream.html)
- [Javadoc: "KTable", Apache Kafka 4.3](https://kafka.apache.org/43/javadoc/org/apache/kafka/streams/kstream/KTable.html)
- [Javadoc: "Topology", Apache Kafka 4.3](https://kafka.apache.org/43/javadoc/org/apache/kafka/streams/Topology.html)
- [Docs: "Managing Streams Application Topics", Apache Kafka 4.3](https://kafka.apache.org/43/streams/developer-guide/manage-topics/)
- [Docs: "Configuring a Streams Application", Apache Kafka 4.3](https://kafka.apache.org/43/streams/developer-guide/config-streams/)
- [KIP: "KIP-213 Support non-key joining in KTable", Apache Kafka](https://cwiki.apache.org/confluence/display/KAFKA/KIP-213+Support+non-key+joining+in+KTable)
- [Source: Kafka Streams DSL internals, Apache Kafka 4.3 branch](https://github.com/apache/kafka/tree/4.3/streams/src/main/java/org/apache/kafka/streams/kstream/internals)
- [Resources](../RESOURCES.md)
