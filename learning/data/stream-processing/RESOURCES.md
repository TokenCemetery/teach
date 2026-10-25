---
title: Resources
description: "Trusted sources for stream processing with Kafka Streams"
type: resources
---

# Stream Processing Resources

## Knowledge

### Streams, tables and the shape of an application

- [Docs: "Core Concepts", Apache Kafka 4.3](https://kafka.apache.org/43/streams/core-concepts/)
  The project's own statement of the model: processor topologies with source and sink processors, event time, ingestion time and processing time, stream time, the stream-table duality, windowing with grace periods, processing guarantees and out-of-order handling. Use for: the vocabulary of stage 1 and the first definitions of stages 4 and 6, as the maintainers word them.
- [Docs: "Architecture", Apache Kafka 4.3](https://kafka.apache.org/43/streams/architecture/)
  How input partitions map to stream tasks, the threading model, local state stores, and fault tolerance through replicated changelog topics and standby replicas. Use for: why a Kafka Streams application is a library running consumers and producers, and the task as the unit of parallelism in stages 1 and 6.
- [Docs: "Writing a Streams Application", Apache Kafka 4.3](https://kafka.apache.org/43/streams/developer-guide/write-streams-app/)
  The Maven artifacts (`kafka-streams`, `kafka-clients`) and the skeleton of an application that builds a topology and starts a `KafkaStreams` instance. Use for: showing that Kafka Streams is a dependency in an ordinary Java program, with no cluster of its own.
- [Docs: "Kafka Streams Quickstart", Apache Kafka 4.3](https://kafka.apache.org/43/streams/quickstart/)
  Runs the bundled WordCount demo against a local broker and walks through its output topic as a stream of KTable updates. Use for: watching the stream-table duality in lesson 1 without writing any Java.
- [Docs: "Tutorial: Write a Kafka Streams Application", Apache Kafka 4.3](https://kafka.apache.org/43/streams/tutorial/)
  Builds Pipe, LineSplit and WordCount step by step and prints `Topology#describe()` after each, including a repartition topic between two sub-topologies. Its printed output uses an older layout and older repartition node names than 4.3 produces. Use for: the shape of a growing topology in lesson 3; check exact names against your own `describe()`.
- [Paper: "Streams and Tables: Two Sides of the Same Coin", Sax, Wang, Weidlich and Freytag, BIRTE (2018)](https://dl.acm.org/doi/10.1145/3242153.3242155)
  Open-access paper by Kafka Streams engineers and Humboldt-Universität researchers introducing the Dual Streaming Model, where an operator's result is a stream of successive updates, so physical and logical order can disagree without buffering and reordering. Use for: the formal account of stream-table duality behind lesson 1 and of why Kafka Streams emits updates instead of waiting.
- [Book: "Designing Data-Intensive Applications", Martin Kleppmann, O'Reilly (2017)](https://dataintensive.net/)
  Chapter 11, "Stream Processing", covers transmitting event streams, databases and streams (change data capture, event sourcing, state as the result of an immutable log), reasoning about time, stream joins, and fault tolerance. Use for: a vendor-neutral grounding for stages 1, 4, 5 and 6 that places Kafka Streams among the alternatives.

### DSL, topologies and repartitioning

- [Docs: "Streams DSL", Apache Kafka 4.3](https://kafka.apache.org/43/streams/developer-guide/dsl-api/)
  The reference for `KStream`, `KTable` and `GlobalKTable`, every stateless and stateful transformation, when an operation marks a stream for repartitioning (`groupByKey` versus `groupBy`, `selectKey`, `repartition()`), aggregations, joins, windowing and `suppress`. Use for: the exact semantics of any DSL operator in stages 2 to 5.
- [Javadoc: "Topology", Apache Kafka 4.3](https://kafka.apache.org/43/javadoc/org/apache/kafka/streams/Topology.html)
  The logical graph of sources, processors, sinks and stores, and `describe()`, which prints sub-topologies and the generated names of every node. Use for: reading a compiled topology in stage 2 and reviewing one in stage 8.
- [Docs: "Managing Streams Application Topics", Apache Kafka 4.3](https://kafka.apache.org/43/streams/developer-guide/manage-topics/)
  User topics versus internal topics, why input and output topics must be created ahead of time, and the default settings of internal repartition topics (delete policy, infinite retention) and changelog topics (compaction). Use for: what a repartition or changelog topic actually is on the broker.
- [Source: Kafka Streams DSL internals, Apache Kafka 4.3 branch](https://github.com/apache/kafka/tree/4.3/streams/src/main/java/org/apache/kafka/streams/kstream/internals)
  `KStreamImpl`, `KTableImpl`, `GroupedStreamAggregateBuilder`, `KStreamImplJoin` and `KStreamKStreamJoin`: which operations mark a stream for repartitioning, how generated names are numbered, join store retention, when unmatched left and outer join results are emitted, the foreign-key join's internal topic names, and the window, session and suppression processors with their exact close tests. Use for: settling behaviour the DSL guide leaves unstated or gets wrong; recheck on each release.

### State, caching and the Processor API

- [Docs: "Processor API", Apache Kafka 4.3](https://kafka.apache.org/43/streams/developer-guide/processor-api/)
  Writing a `Processor`, connecting state stores, scheduling punctuators on stream time or wall-clock time, and the persistent, in-memory, versioned and header-aware store types. Use for: lesson material on state stores, changelogs and punctuators when the DSL is not enough.
- [Docs: "Memory Management", Apache Kafka 4.3](https://kafka.apache.org/43/streams/developer-guide/memory-mgmt/)
  The record cache in the DSL and the Processor API, how it compacts updates to the same key before they are written to state stores or forwarded downstream, how cache size and commit interval interact, and RocksDB memory. Some examples still use the deprecated `CACHE_MAX_BYTES_BUFFERING_CONFIG`, whose replacement is `statestore.cache.max.bytes`. Use for: why a `KTable` aggregation emits fewer updates than it receives records.
- [Source: "AbstractStoreBuilder.java", Apache Kafka 4.3 branch](https://github.com/apache/kafka/blob/4.3/streams/src/main/java/org/apache/kafka/streams/state/internals/AbstractStoreBuilder.java)
  The base class of every `StoreBuilder`, which sets logging on and caching off by default. Use for: settling the Processor API store caching default, which the Memory Management page words ambiguously.

### Time, windows and late data

- [Javadoc: "TimeWindows", Apache Kafka 4.3](https://kafka.apache.org/43/javadoc/org/apache/kafka/streams/kstream/TimeWindows.html)
  `ofSizeWithNoGrace` and `ofSizeAndGrace`, epoch-aligned window boundaries, `advanceBy` for hopping windows, and the warning that no grace means any record arriving after the window end is dropped. Use for: the exact grace behaviour each constructor gives.
- [Javadoc: "Suppressed", Apache Kafka 4.3](https://kafka.apache.org/43/javadoc/org/apache/kafka/streams/kstream/Suppressed.html)
  `untilWindowCloses` and `untilTimeLimit`, each taking a `BufferConfig` that bounds the suppression buffer. Use for: emitting one final result per window in stage 4.
- [KIP: "KIP-328: Ability to suppress updates for KTables", Apache Kafka](https://cwiki.apache.org/confluence/display/KAFKA/KIP-328%3A+Ability+to+suppress+updates+for+KTables)
  The design behind `suppress`: rate-limiting `KTable` updates and emitting exactly one final result per window and key, with the definition of when a window result is final. Use for: why `suppress` exists and why it holds output until stream time passes the window end plus grace.
- [KIP: "KIP-633: Deprecate 24-hour Default Grace Period for Windowed Operations in Streams", Apache Kafka](https://cwiki.apache.org/confluence/display/KAFKA/KIP-633%3A+Deprecate+24-hour+Default+Grace+Period+for+Windowed+Operations+in+Streams)
  Why the old implicit 24-hour grace period confused users of `suppress`, and the explicit `...WithNoGrace` and `...AndGrace` constructors that replaced it. Use for: explaining that grace is now always a deliberate choice, and reading older code that relied on the default.
- [KIP: "KIP-450: Sliding Window Aggregations in the DSL", Apache Kafka](https://cwiki.apache.org/confluence/display/KAFKA/KIP-450%3A+Sliding+Window+Aggregations+in+the+DSL)
  The design of `SlidingWindows`, defined by a maximum time difference between records, proposed because hopping windows with a small advance create many redundant overlapping windows. Use for: how sliding windows differ from hopping windows.
- [KIP: "KIP-825: introduce a new API to control when aggregated results are produced", Apache Kafka](https://cwiki.apache.org/confluence/display/KAFKA/KIP-825%3A+introduce+a+new+API+to+control+when+aggregated+results+are+produced)
  The design of `emitStrategy(EmitStrategy.onWindowClose())` on time- and session-windowed streams, why it gives final windowed results without the second buffer and changelog `suppress` needs, and its `emit-final-*` metrics. Use for: choosing between `suppress` and an emit strategy in stage 4.
- [Javadoc: "EmitStrategy", Apache Kafka 4.3](https://kafka.apache.org/43/javadoc/org/apache/kafka/streams/kstream/EmitStrategy.html)
  `onWindowClose` and `onWindowUpdate`, with window close defined as event time past window end plus grace. Use for: the exact emit rule of a windowed aggregation.
- [Javadoc: "ProcessingContext", Apache Kafka 4.3](https://kafka.apache.org/43/javadoc/org/apache/kafka/streams/processor/api/ProcessingContext.html)
  `currentStreamTimeMs()`, defined as the largest observed record timestamp, tracked per task and preserved across restarts and task migration, and `currentSystemTimeMs()`. Use for: the primary definition of stream time.
- [Javadoc: "Materialized", Apache Kafka 4.3](https://kafka.apache.org/43/javadoc/org/apache/kafka/streams/kstream/Materialized.html)
  `withRetention` for window and session stores, with the rule that retention must cover window size plus grace and defaults to exactly that. Use for: settling the retention default, which the DSL guide still gives as one day.
- [Paper: "The Dataflow Model", Akidau et al., VLDB (2015)](https://www.vldb.org/pvldb/vol8/p1792-Akidau.pdf)
  The Google paper that separates what is computed, where in event time, when in processing time results are emitted, and how refinements relate, using windows, watermarks and triggers. Use for: the general theory of event time and completeness that stage 4 contrasts with Kafka Streams' stream time and grace periods.
- [Article: "Streaming 101: The world beyond batch", Tyler Akidau, O'Reilly (2015)](https://www.oreilly.com/radar/the-world-beyond-batch-streaming-101/)
  Bounded versus unbounded data, event time versus processing time and the skew between them, and the windowing patterns. Use for: a readable introduction to stage 4 before the Kafka Streams specifics.
- [Article: "Streaming 102: The world beyond batch", Tyler Akidau, O'Reilly (2016)](https://www.oreilly.com/radar/the-world-beyond-batch-streaming-102/)
  Watermarks as a notion of input completeness, triggers, allowed lateness and accumulation modes, worked through one example. Use for: what a watermark is, so learners can see what Kafka Streams does instead.

### Joins

- [Docs: "Joining", Streams DSL, Apache Kafka 4.3](https://kafka.apache.org/43/streams/developer-guide/dsl-api/#joining)
  The co-partitioning requirements, then every join: stream-stream windowed (with result tables for inner, left and outer), table-table, foreign-key table-table, stream-table, and stream-`GlobalKTable`. Use for: the semantics and the exact output of each join type in stage 5.
- [Javadoc: "JoinWindows", Apache Kafka 4.3](https://kafka.apache.org/43/javadoc/org/apache/kafka/streams/kstream/JoinWindows.html)
  `ofTimeDifferenceWithNoGrace`, `ofTimeDifferenceAndGrace`, `before` and `after` for asymmetric windows. Use for: defining a stream-stream join window precisely.
- [KIP: "KIP-213 Support non-key joining in KTable", Apache Kafka](https://cwiki.apache.org/confluence/display/KAFKA/KIP-213+Support+non-key+joining+in+KTable)
  The design of foreign-key joins between two tables: subscription messages sent to the right-hand side through internal topics, responses routed back, and the hashing that discards stale results when a foreign key changes rapidly. Use for: what a foreign-key join costs in internal topics and why it is more than a lookup.

### Exactly-once, scaling and rebalancing

- [Docs: "Configuring a Streams Application", Apache Kafka 4.3](https://kafka.apache.org/43/streams/developer-guide/config-streams/)
  Every Streams setting with its importance and default, including `application.id`, `processing.guarantee`, `commit.interval.ms`, `num.standby.replicas`, `num.stream.threads`, `acceptable.recovery.lag`, `max.warmup.replicas`, `group.protocol`, the exception handlers and `topology.optimization`, plus recommended settings for resiliency. Use for: configuration in every stage. Its table gives `LogAndContinueExceptionHandler` as the default `deserialization.exception.handler`, which disagrees with the source code and the generated reference below.
- [KIP: "KIP-129: Streams Exactly-Once Semantics", Apache Kafka](https://cwiki.apache.org/confluence/display/KAFKA/KIP-129%3A+Streams+Exactly-Once+Semantics)
  The original design for exactly-once in Kafka Streams: one transaction covering output records, changelog writes and the consumer offset commit. Use for: why read-process-write in Streams can be exactly-once when an arbitrary consumer and producer pair is not.
- [KIP: "KIP-447: Producer scalability for exactly once semantics", Apache Kafka](https://cwiki.apache.org/confluence/display/KAFKA/KIP-447%3A+Producer+scalability+for+exactly+once+semantics)
  The change behind `exactly_once_v2` (first called `exactly_once_beta`): fencing through consumer group metadata passed to `sendOffsetsToTransaction`, so one producer per thread replaces one producer per input partition. Use for: why EOS v2 is cheaper and why it needs brokers at version 2.5 or later.
- [Paper: "Consistency and Completeness: Rethinking Distributed Stream Processing in Apache Kafka", Wang et al., SIGMOD (2021)](https://dl.acm.org/doi/10.1145/3448016.3457556)
  Open-access paper by the Kafka Streams team: read-process-write cycles captured as log appends, idempotent and transactional writes for exactly-once, and revision-based speculative processing for out-of-order data, with measurements from large deployments. Use for: the primary account of how stages 4 and 6 fit together, separating consistency from completeness.
- [Docs: "Running Streams Applications", Apache Kafka 4.3](https://kafka.apache.org/43/streams/developer-guide/running-app/)
  Starting instances, adding and removing capacity, state restoration during a rebalance, how many instances to run, and handling crashes. Use for: scaling out and in, and what happens to tasks and state when an instance joins or leaves.
- [KIP: "KIP-441: Smooth Scaling Out for Kafka Streams", Apache Kafka](https://cwiki.apache.org/confluence/display/KAFKA/KIP-441%3A+Smooth+Scaling+Out+for+Kafka+Streams)
  The high-availability task assignor: warmup replicas, `acceptable.recovery.lag`, `max.warmup.replicas` and probing rebalances that move a stateful task only once its new owner has caught up. Use for: warmup replicas in stage 6.
- [KIP: "KIP-345: Introduce static membership protocol to reduce consumer rebalances", Apache Kafka](https://cwiki.apache.org/confluence/display/KAFKA/KIP-345%3A+Introduce+static+membership+protocol+to+reduce+consumer+rebalances)
  The design of `group.instance.id`, including its Kafka Streams section: each instance sets the ID, Streams derives one per thread, and a restart within the session timeout causes no rebalance. Use for: static membership for rolling restarts in stage 6.
- [Docs: "Consumer Configs", Apache Kafka 4.3](https://kafka.apache.org/43/configuration/consumer-configs/)
  The generated consumer reference, including `session.timeout.ms` (45000 by default, not overridden by Streams). Use for: how long a crashed instance goes unnoticed on the classic protocol.
- [Javadoc: "KafkaStreams", Apache Kafka 4.3](https://kafka.apache.org/43/javadoc/org/apache/kafka/streams/KafkaStreams.html)
  `addStreamThread`, `removeStreamThread`, `metadataForLocalThreads` and the restore and standby listeners. Use for: changing thread count at run time and watching task assignment and restoration.
- [Docs: "Streams Rebalance Protocol", Apache Kafka 4.3](https://kafka.apache.org/43/streams/developer-guide/streams-rebalance-protocol/)
  The broker-driven streams group of KIP-1071: what is and is not supported, enabling it on brokers (`streams.version` feature) and clients (`group.protocol=streams`), group-level settings that replace client ones, configurations it ignores (including the warmup and rack-aware settings), the `NOT_READY` state and offline migration. Use for: the new protocol in stage 6, read for the exact list of limits before recommending it.
- [KIP: "KIP-1071: Streams Rebalance Protocol", Apache Kafka](https://cwiki.apache.org/confluence/display/KAFKA/KIP-1071%3A+Streams+Rebalance+Protocol)
  The full design: streams groups, the `StreamsGroupHeartbeat` RPC, topology metadata and epochs held by the group coordinator, and broker-side assignment. Use for: why moving assignment to the broker changes rebalancing, beyond what the developer guide summarises.

### Testing and operations

- [Docs: "Testing a Streams Application", Apache Kafka 4.3](https://kafka.apache.org/43/streams/developer-guide/testing/)
  The `kafka-streams-test-utils` artifact, `TopologyTestDriver`, `TestInputTopic` and `TestOutputTopic`, stream-time and wall-clock punctuations, and reading state stores in a test. Use for: lesson material on testing a topology without a broker.
- [Javadoc: "TopologyTestDriver", Apache Kafka 4.3](https://kafka.apache.org/43/javadoc/org/apache/kafka/streams/TopologyTestDriver.html)
  The driver's contract, including that it processes records synchronously, so `commit.interval.ms` and the record cache size have no effect in a driver test. Use for: what a passing driver test does and does not prove.
- [Docs: "Streams Monitoring", Apache Kafka 4.3](https://kafka.apache.org/43/operations/monitoring/#streams-monitoring)
  The four-level metric hierarchy (client, thread, task, processor node) with state store, record cache and end-to-end latency metrics, and their recording levels. Use for: choosing what to alert on in stage 7.
- [Docs: "Kafka Streams Configs", Apache Kafka 4.3](https://kafka.apache.org/43/configuration/kafka-streams-configs/)
  The reference generated from `StreamsConfig` itself, with type, default and valid values for each setting. Use for: settling a default when the developer guide's prose disagrees, as it does for `deserialization.exception.handler` (this page and the source give `LogAndFailExceptionHandler`).
- [Docs: "Interactive Queries", Apache Kafka 4.3](https://kafka.apache.org/43/streams/developer-guide/interactive-queries/)
  Querying local state stores, discovering which instance holds a key through `application.server` metadata, and the RPC layer the application must supply itself. Use for: serving reads from Streams state in stage 7.
- [Docs: "Kafka Streams Groups Tool", Apache Kafka 4.3](https://kafka.apache.org/43/streams/developer-guide/kafka-streams-group-sh/)
  `kafka-streams-groups.sh` for streams groups: list, describe state, members and lag, reset or delete input offsets with `--dry-run` first, and delete a group with its internal topics. Use for: operating an application on the streams rebalance protocol.
- [Docs: "Application Reset Tool", Apache Kafka 4.3](https://kafka.apache.org/43/streams/developer-guide/app-reset-tool/)
  `kafka-streams-application-reset.sh` for the classic protocol: resetting input offsets, deleting internal topics, and what the tool leaves to the operator (local state, output topics). Use for: reprocessing from scratch on the classic protocol.

### Choosing a tool and changing a running topology

- [Docs: "Naming Operators in a Kafka Streams DSL Application", Apache Kafka 4.3](https://kafka.apache.org/43/streams/developer-guide/dsl-topology-naming/)
  How generated names shift when an operator is added, why that renames state stores, changelogs and repartition topics and blocks a rolling redeploy, and how `Named`, `Materialized` and `Grouped` names plus `ensure.explicit.internal.resource.naming` prevent it. Use for: changing a running topology without losing state, in stage 8.
- [Docs: "Upgrade Guide and API Changes", Apache Kafka 4.3](https://kafka.apache.org/43/streams/upgrade-guide/)
  Rolling upgrade steps, the compatibility notes for each release (including downgrade limits from 4.3's per-store changelog offsets), and the API changes per version. Use for: upgrading Kafka Streams and dating any claim about which version introduced what.
- [Docs: "Timely Stream Processing", Apache Flink](https://nightlies.apache.org/flink/flink-docs-stable/docs/concepts/time/)
  Flink's event time, processing time, watermarks, lateness and windowing. Use for: the time half of the Streams versus Flink comparison.
- [Docs: "Stateful Stream Processing", Apache Flink](https://nightlies.apache.org/flink/flink-docs-stable/docs/concepts/stateful-stream-processing/)
  Keyed state, state backends, checkpoint barriers and exactly-once recovery, and savepoints. Use for: the state and recovery half of the Streams versus Flink comparison, a cluster with checkpoints against a library with changelogs.
- [Docs: "Flink Architecture", Apache Flink](https://nightlies.apache.org/flink/flink-docs-stable/docs/concepts/flink-architecture/)
  The JobManager and TaskManager processes a Flink deployment runs. Use for: what "a separate cluster" costs in the Streams against Flink comparison.
- [Docs: "State Backends", Apache Flink](https://nightlies.apache.org/flink/flink-docs-stable/docs/ops/state/state_backends/)
  The HashMap, RocksDB and ForSt backends, and incremental checkpoints, available only with RocksDB among the stable backends. Use for: why very large state recovers differently in Flink.
- [Docs: "Connectors overview", Apache Flink](https://nightlies.apache.org/flink/flink-docs-stable/docs/connectors/datastream/overview/)
  The source and sink connectors the Flink project maintains (Kafka, Kinesis, Pulsar, Cassandra, JDBC, file systems and more). Use for: non-Kafka inputs and outputs as a reason to leave Kafka Streams.
- [Docs: "How it works", ksqlDB](https://docs.ksqldb.io/en/latest/operate-and-deploy/how-it-works/)
  ksqlDB's engine, server, REST interface and CLI, and that the engine compiles SQL statements into Kafka Streams topologies. Use for: placing ksqlDB in the comparison as SQL over the same runtime.
- [Article: "Questioning the Lambda Architecture", Jay Kreps, O'Reilly (2014)](https://www.oreilly.com/radar/questioning-the-lambda-architecture/)
  The argument against keeping a batch path and a streaming path in parallel, and for reprocessing by replaying the log through a new version of the job. Use for: why a stream processor's output can be authoritative, and the replay strategy behind resetting an application.
- [Book: "Kafka Streams in Action, Second Edition", Bill Bejeck, Manning (2024)](https://www.manning.com/books/kafka-streams-in-action-second-edition)
  A book-length treatment by an Apache Kafka committer: the DSL and the Processor API, stateful processing and windowing, interactive queries, and the surrounding platform (Schema Registry, Kafka Connect, ksqlDB). Use for: worked examples at greater length than the documentation; check version-specific details against the 4.3 docs.

## Gaps

- No vendor-neutral, primary source compares Kafka Streams, a plain consumer, Flink and ksqlDB for the same workload. Each project documents only itself, and published comparisons come from companies selling one of them. Lesson 18's comparison is built from each project's own concept pages above.
- No official checklist exists for reviewing a topology. The naming guide, `Topology#describe()` and the DSL reference each cover part of it; the review lesson assembles the checklist from them.
- The streams rebalance protocol has only its developer guide page and KIP-1071. No independent operational account of running it in production was found yet.
- Jay Kreps' essay "The Log: What every software engineer should know about real-time data's unifying abstraction" (LinkedIn Engineering, 2013) is not listed: its canonical URL now returns 404, and no stable copy by the author or LinkedIn was found.
- The SIGMOD 2021 paper's ACM page answers scripted requests with a bot check, so its claims were not quoted beyond what its abstract states; lesson 13 rests on the configuration documentation instead.
