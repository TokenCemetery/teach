---
title: Glossary
description: "Canonical terms for stream processing with Kafka Streams"
type: glossary
---

# Stream Processing Glossary

Canonical terms for how a Kafka Streams application reads, computes over, stores and writes a stream. Terms the log already owns, such as partition, consumer group, offset and compaction, are defined in the [Kafka glossary](../kafka/GLOSSARY.md) and used here with that meaning.

## Terms

**Application ID**:
The `application.id` setting that names a Streams application. Every instance sharing it forms one group that splits the work, and it prefixes the app's internal topics, its consumer group and its local state directory, so changing it starts the app from nothing.
_Avoid_: client ID, group ID (the group ID is derived from it, and a client ID names one instance)

**Changelog topic**:
An internal, compacted topic to which a state store's every update is written, so the store can be rebuilt on another instance by replaying it. Named `<application.id>-<store name>-changelog`.
_Avoid_: backup topic, state topic

**Co-partitioning**:
The requirement that two topics read together by a join, or by one task, have the same number of partitions and are keyed and partitioned the same way, so that a given key lands in the same partition number on both.
_Avoid_: aligned topics, same partitioning (the partition count alone is not enough; the key and the partitioner must match too)

**Commit interval**:
How often a stream thread commits its progress: input offsets, flushed state and pending output, set by `commit.interval.ms`. It also bounds how long the record cache holds updates back, so it trades output volume against latency.
_Avoid_: flush interval, checkpoint interval

**Dead letter queue**:
A topic to which records that failed deserialization, processing or production are copied, raw key and value, so the app can skip them without losing them. Set for the built-in exception handlers with `errors.dead.letter.queue.topic.name` since 4.2; it does not by itself keep the app running.
_Avoid_: quarantine topic, error topic

**Event time**:
The time an event happened, carried in the record as its timestamp and read by the timestamp extractor. Windows and joins in Kafka Streams follow event time.
_Avoid_: record time, creation time (both name where the timestamp came from, not what it means)

**Exactly-once processing**:
The Streams guarantee, enabled with `processing.guarantee=exactly_once_v2`, that each input record's effect on state stores and output topics is committed once, by committing the input offsets, the changelog writes and the output writes in one Kafka transaction. It covers only effects that are writes to the same Kafka cluster.
_Avoid_: exactly-once delivery (delivery is the log's concern; this is about the effect of processing)

**Foreign-key join**:
A join between two KTables where each record on the left side names the key of a record on the right side through a value field, rather than sharing its key. Kafka Streams implements it with internal subscription and response topics.
_Avoid_: lookup join, non-key join

**GlobalKTable**:
A table that every instance of the application reads in full from all partitions of its topic, so a stream can join it on any field without co-partitioning. It costs a full copy of the table on every instance.
_Avoid_: broadcast table, replicated KTable

**Grace period**:
How long after a window's end it still accepts out-of-order records, measured in stream time. Once stream time passes the window end plus the grace period, the window is closed and a record that falls into it is dropped as late.
_Avoid_: allowed lateness, retention (retention is how long a closed window stays queryable)

**Hopping window**:
A fixed-size window that advances by a step smaller than its size, so consecutive windows overlap and one record falls into several. Window boundaries align to the epoch, not to records.
_Avoid_: sliding window (in Kafka Streams that names a different window)

**Ingestion time**:
The time a broker appended a record to a partition, which the record's timestamp holds when the topic's `message.timestamp.type` is `LogAppendTime`. Reading it as the timestamp gives ingestion-time semantics rather than event time.
_Avoid_: broker time, append time (both name where the timestamp came from), processing time (that is the processor's wall clock)

**Interactive query**:
Reading a running application's state store directly, from inside the app or through an endpoint it exposes, instead of writing the state to a topic and reading it from there.
_Avoid_: state lookup, store API

**Internal topic**:
A topic a Streams application creates and manages for itself: a changelog topic or a repartition topic, named with the application ID as prefix. Other applications should not write to it.
_Avoid_: system topic, private topic

**Join window**:
The `JoinWindows` bound on a stream-stream join: two records with the same key join only if their timestamps differ by no more than its before and after limits, with a grace period after which a record is late. A sliding window aligned to each record.
_Avoid_: join interval, join timeout

**KStream**:
The DSL abstraction for a record stream: every record is an independent event, and a second record with the same key is another event, not a replacement.
_Avoid_: event stream, message stream

**KTable**:
The DSL abstraction for a changelog stream read as a table: each record is the latest value for its key, a later record replaces it, and a tombstone deletes it. Each instance holds the partitions it is assigned.
_Avoid_: materialized view (a KTable need not be materialized), table topic

**Late record**:
A record that arrives after the window it belongs to has closed, meaning stream time has already passed that window's end plus its grace period. Kafka Streams drops it and counts it in a metric.
_Avoid_: out-of-order record (an out-of-order record within the grace period is accepted)

**Processing time**:
The wall-clock time of the machine running the processor at the moment it handles a record. Used by wall-clock punctuators, never by windows.
_Avoid_: system time, ingestion time (ingestion time is the broker's append time)

**Processor API**:
The lower-level Kafka Streams API in which you write processors that receive each record, read and write state stores directly, forward records explicitly and schedule punctuators. The DSL is built on it.
_Avoid_: low-level DSL, custom transformer

**Punctuator**:
A callback a processor schedules to run periodically, on stream time or on wall-clock time, typically to emit or expire state independently of incoming records.
_Avoid_: timer, scheduled task

**Record cache**:
The in-memory cache in front of a state store that collapses consecutive updates to the same key before they are forwarded downstream and written to the changelog. Sized per instance by `statestore.cache.max.bytes`, and flushed on every commit.
_Avoid_: buffer, RocksDB cache (RocksDB has its own block cache, which is separate)

**Repartition topic**:
An internal topic a Streams application writes records to and reads them back from, so that records are redistributed by a new key before a stateful operation or a join. Named `<application.id>-<name>-repartition`.
_Avoid_: shuffle topic, rekey topic

**Restoration**:
Rebuilding a state store on an instance by replaying its changelog topic, which happens before the task holding it can process new records.
_Avoid_: recovery (recovery covers the whole failover, of which restoration is one step), rehydration

**Serde**:
A paired serializer and deserializer for one type, which Kafka Streams uses wherever it reads from or writes to a topic, a changelog or a repartition topic included.
_Avoid_: codec, converter (a converter is the Kafka Connect name)

**Session window**:
A window per key that groups records separated by less than an inactivity gap. A record that bridges two sessions merges them, so sessions have no fixed size or boundaries.
_Avoid_: activity window, gap window

**Sliding window**:
In Kafka Streams aggregations, a fixed-size window defined by the largest time difference between records it may contain, with windows created at record timestamps rather than at fixed boundaries.
_Avoid_: hopping window, rolling window

**Standby replica**:
A copy of a task's state store kept up to date on another instance by reading the changelog, without processing records, so the task can move there with little or no restoration. Count set by `num.standby.replicas`.
_Avoid_: hot standby, follower

**State store**:
Local storage attached to a processor, usually RocksDB or in memory, holding the state a stateful operation needs: an aggregate, a table, a window's contents or a join buffer. Backed by a changelog topic unless logging is disabled.
_Avoid_: cache, local database

**Stream thread**:
A thread inside a Streams instance that runs one or more tasks, each with its own consumer position and state. Count set by `num.stream.threads`.
_Avoid_: worker, processor thread

**Stream time**:
The largest record timestamp a task has seen so far. It advances only when a record with a newer timestamp arrives, never moves backward, and is what closes windows and fires stream-time punctuators.
_Avoid_: watermark (a watermark in Flink is a separate signal; stream time is derived only from record timestamps), current time

**Stream-table duality**:
The fact that a table can be turned into a stream of its changes and that stream replayed back into the table, so a stream and a table are two views of the same data.
_Avoid_: event sourcing (event sourcing is one application of the duality, not the duality)

**Streams group**:
The broker-coordinated group a Streams application forms under `group.protocol=streams`, for which the broker computes the task assignment and which `kafka-streams-groups.sh` manages.
_Avoid_: consumer group (that is the group the classic protocol forms)

**Sub-topology**:
A connected part of a topology that shares no processor with another part. Sub-topologies are connected only through topics, typically repartition topics, and each one is split into its own set of tasks.
_Avoid_: stage, subgraph

**Suppression**:
Holding back a KTable's intermediate updates and emitting only some of them: one per key per time limit, or one final result per window once it closes. Added with `suppress()`.
_Avoid_: deduplication, debouncing

**Task**:
The unit of parallelism in Kafka Streams: one task per input partition of a sub-topology, owning those partitions, its processors and its state stores. Tasks, not threads, are what move between instances on a rebalance.
_Avoid_: job, partition (a task may read one partition from each of several co-partitioned topics)

**Timestamp extractor**:
The component that sets each input record's event time, from the record's own timestamp by default or from a field in its value when configured.
_Avoid_: time parser

**Tombstone**:
A record with a key and a null value. Read as a table it deletes the key, and a compacted topic eventually removes the key entirely.
_Avoid_: delete record, null record

**Topology**:
The directed graph of source processors, stream processors, state stores and sink processors that defines what a Streams application computes, built by the DSL or the Processor API and printed by `Topology#describe()`.
_Avoid_: pipeline, job graph

**Tumbling window**:
A fixed-size window with no gaps and no overlap, so each record falls into exactly one window. A hopping window whose step equals its size.
_Avoid_: fixed window, batch window

**Versioned table**:
A KTable materialized with a versioned state store, which keeps past values per key for a history retention, so a lookup returns the value as of a given timestamp rather than the latest by offset. A stream-table join against it follows event time.
_Avoid_: temporal table, history table

**Warmup replica**:
A temporary standby replica that Kafka Streams places on an instance it wants to move a task to, so the task moves only once its state has caught up. Count bounded by `max.warmup.replicas`.
_Avoid_: shadow task, pre-standby
