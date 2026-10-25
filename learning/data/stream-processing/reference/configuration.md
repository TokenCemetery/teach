---
title: Configuration
description: The settings that decide guarantees, latency, parallelism and recovery, with their defaults
type: reference
---

# Configuration

Every Streams setting this track's lessons rely on, compressed for lookup: chiefly stage 6, [lesson 13](../lessons/0013-exactly-once-in-kafka-streams.md) (exactly-once), [lesson 14](../lessons/0014-tasks-threads-and-scaling-out.md) (tasks and threads) and [lesson 15](../lessons/0015-rebalancing-restoration-and-standby-replicas.md) (rebalancing and recovery), plus [lesson 17](../lessons/0017-operating-and-monitoring-a-streams-app.md) for the exception handlers and the earlier lessons named in each row.

Defaults were read from the generated [Kafka Streams Configs](https://kafka.apache.org/43/configuration/kafka-streams-configs/) reference for Apache Kafka 4.3 in October 2026. Where the developer guide's [Configuring a Streams Application](https://kafka.apache.org/43/streams/developer-guide/config-streams/) disagrees, the generated reference wins, since it is built from `StreamsConfig` itself. Check it for the current value before quoting one.

## Guarantees and latency

| Setting | Default | What it decides | Lesson |
|---|---|---|---|
| `processing.guarantee` | `at_least_once` | `exactly_once_v2` commits input offsets, changelog writes and output writes in one transaction; needs brokers 2.5 or later and, by default, at least three brokers. `exactly_once` and `exactly_once_beta` are deprecated | [13](../lessons/0013-exactly-once-in-kafka-streams.md) |
| `commit.interval.ms` | 30000; 100 under `exactly_once_v2` | How often progress is committed, and so how long the record cache holds updates back and, under exactly-once, how long output stays invisible to `read_committed` consumers | [6](../lessons/0006-aggregations-ktables-and-the-record-cache.md), [13](../lessons/0013-exactly-once-in-kafka-streams.md) |
| `statestore.cache.max.bytes` | 10485760 (10 MiB) | Record cache for the whole instance, split across its threads. 0 disables caching, so every update is forwarded | [6](../lessons/0006-aggregations-ktables-and-the-record-cache.md) |
| `replication.factor` | -1 (the broker's `default.replication.factor`) | Replication of changelog and repartition topics. The developer guide recommends 3, with `min.insync.replicas=2` set through `topic.`-prefixed config | [5](../lessons/0005-state-stores-and-changelog-topics.md), [13](../lessons/0013-exactly-once-in-kafka-streams.md) |

Pages: [Kafka Streams Configs](https://kafka.apache.org/43/configuration/kafka-streams-configs/); the resiliency recommendations are in [Configuring a Streams Application](https://kafka.apache.org/43/streams/developer-guide/config-streams/).

## Parallelism

| Setting or call | Default | What it decides | Lesson |
|---|---|---|---|
| `num.stream.threads` | 1 | Stream threads per instance. Threads beyond the app's total task count stay idle | [14](../lessons/0014-tasks-threads-and-scaling-out.md) |
| `KafkaStreams#addStreamThread()`, `removeStreamThread()` | | Change the thread count at run time, with a rebalance; add only while `RUNNING` or `REBALANCING`. The cache total is re-split over the new thread count | [14](../lessons/0014-tasks-threads-and-scaling-out.md) |
| `repartition(Repartitioned.numberOfPartitions(n))` | Derived from the upstream topics | Partition count, and so task count, of the sub-topology after a repartition | [4](../lessons/0004-stateless-operations-and-repartitioning.md), [14](../lessons/0014-tasks-threads-and-scaling-out.md) |

Pages: [Kafka Streams Configs](https://kafka.apache.org/43/configuration/kafka-streams-configs/), [KafkaStreams javadoc](https://kafka.apache.org/43/javadoc/org/apache/kafka/streams/KafkaStreams.html), [KStream javadoc](https://kafka.apache.org/43/javadoc/org/apache/kafka/streams/kstream/KStream.html).

## Recovery and rebalancing

| Setting | Default | What it decides | Lesson |
|---|---|---|---|
| `num.standby.replicas` | 0 | Standby copies of each task's state. 1 is the documented recommendation; n standbys need n + 1 instances and n + 1 times the disk | [15](../lessons/0015-rebalancing-restoration-and-standby-replicas.md) |
| `acceptable.recovery.lag` | 10000 | Changelog lag, in offsets, still counted as caught up for an active stateful task. Should mean well under a minute of restoring. `Long.MAX_VALUE` disables warmups | [15](../lessons/0015-rebalancing-restoration-and-standby-replicas.md) |
| `max.warmup.replicas` | 2 | Warmup replicas assigned at once, app-wide; at least 1 | [15](../lessons/0015-rebalancing-restoration-and-standby-replicas.md) |
| `probing.rebalance.interval.ms` | 600000 (10 minutes) | Longest wait before a probing rebalance promotes caught-up warmups; at least 60000 | [15](../lessons/0015-rebalancing-restoration-and-standby-replicas.md) |
| `task.assignor.class` | null, meaning the high-availability assignor | The task assignment algorithm. `StickyTaskAssignor`, the pre-KIP-441 default, moves fewer tasks at the cost of availability | [15](../lessons/0015-rebalancing-restoration-and-standby-replicas.md) |
| `state.dir` | A `kafka-streams` directory under `java.io.tmpdir` | Where local stores live, in a subdirectory per application ID. Must be unique per instance on a shared filesystem, and persistent if a restart should not restore everything | [5](../lessons/0005-state-stores-and-changelog-topics.md), [15](../lessons/0015-rebalancing-restoration-and-standby-replicas.md) |
| `group.protocol` | `classic` | `streams` switches to the broker-driven streams rebalance protocol; brokers and clients at 4.2 or later | [15](../lessons/0015-rebalancing-restoration-and-standby-replicas.md) |
| `group.instance.id` (consumer config) | null | Static membership on the classic protocol: a restart within `session.timeout.ms` causes no rebalance. Rejected under `group.protocol=streams` | [15](../lessons/0015-rebalancing-restoration-and-standby-replicas.md) |
| `session.timeout.ms` (consumer config) | 45000 | How long a crashed instance goes unnoticed on the classic protocol. Streams does not override the consumer default | [15](../lessons/0015-rebalancing-restoration-and-standby-replicas.md) |

Pages: [Kafka Streams Configs](https://kafka.apache.org/43/configuration/kafka-streams-configs/), [Configuring a Streams Application](https://kafka.apache.org/43/streams/developer-guide/config-streams/) (`state.dir` default and the `task.assignor.class` alternatives), [Consumer Configs](https://kafka.apache.org/43/configuration/consumer-configs/), [KIP-345](https://cwiki.apache.org/confluence/display/KAFKA/KIP-345%3A+Introduce+static+membership+protocol+to+reduce+consumer+rebalances). The generated reference prints the `state.dir` default as `${java.io.tmpdir}`.

## Under `group.protocol=streams`

| Client setting | What happens |
|---|---|
| `acceptable.recovery.lag`, `max.warmup.replicas`, `probing.rebalance.interval.ms`, `task.assignor.class` | Ignored: only the sticky assignor runs, so there are no warmup replicas |
| `rack.aware.assignment.tags`, `rack.aware.assignment.strategy`, `rack.aware.assignment.traffic_cost`, `rack.aware.assignment.non_overlap_cost` | Ignored: no rack-aware assignment |
| `num.standby.replicas` | Ignored on the client; set the group config `streams.num.standby.replicas` with `kafka-configs.sh` (broker default `group.streams.num.standby.replicas`) |
| `session.timeout.ms`, `heartbeat.interval.ms` | Ignored on the client; set `streams.session.timeout.ms` and `streams.heartbeat.interval.ms` per group |
| `group.instance.id` | Rejected |

```bash
bin/kafka-configs.sh --bootstrap-server localhost:9092 \
  --alter --entity-type groups --entity-name my-app \
  --add-config streams.num.standby.replicas=1
```

Page: [Streams Rebalance Protocol](https://kafka.apache.org/43/streams/developer-guide/streams-rebalance-protocol/).

## Topology, serdes and time

| Setting | Default | What it decides | Lesson |
|---|---|---|---|
| `default.key.serde`, `default.value.serde` | null | Serdes used wherever an operation is given none. With null, every source, store and sink needs explicit serdes | [3](../lessons/0003-the-dsl-and-topologies.md) |
| `default.timestamp.extractor` | `FailOnInvalidTimestamp` | Where event time comes from. The default reads the record's own timestamp and throws on a negative one | [8](../lessons/0008-event-time-processing-time-and-stream-time.md) |
| `topology.optimization` | `none` | `all`, or a list of `reuse.ktable.source.topics`, `merge.repartition.topics`, `single.store.self.join`. Takes effect only if the same properties are also passed to `StreamsBuilder#build(Properties)`. List specific optimizations in production, so a library upgrade cannot change the topology | [4](../lessons/0004-stateless-operations-and-repartitioning.md) |
| `ensure.explicit.internal.resource.naming` | false | When true, the app refuses to start if any internal topic or store has a generated name | [20](../lessons/0020-changing-a-topology-others-depend-on.md) |

Pages: [Kafka Streams Configs](https://kafka.apache.org/43/configuration/kafka-streams-configs/), [Configuring a Streams Application](https://kafka.apache.org/43/streams/developer-guide/config-streams/) (the two-step optimization rule), [Naming Operators](https://kafka.apache.org/43/streams/developer-guide/dsl-topology-naming/).

## Errors

| Setting | Default | What it decides | Lesson |
|---|---|---|---|
| `deserialization.exception.handler` | `LogAndFailExceptionHandler` | A record that cannot be deserialized: fail (stop) or continue (skip). The developer guide's table says `LogAndContinueExceptionHandler`; the generated reference and the source say fail | [17](../lessons/0017-operating-and-monitoring-a-streams-app.md) |
| `processing.exception.handler` | `LogAndFailProcessingExceptionHandler` | An exception thrown while processing a record. Applies to regular tasks, not global stores, unless `processing.exception.handler.global.enabled` (default false, deprecated) is set | [17](../lessons/0017-operating-and-monitoring-a-streams-app.md) |
| `production.exception.handler` | `DefaultProductionExceptionHandler` | A record the producer fails to write | [17](../lessons/0017-operating-and-monitoring-a-streams-app.md) |
| `errors.dead.letter.queue.topic.name` | null | When set, the built-in handlers write a dead letter record to this topic; the fail handlers then still fail, so pair it with a continue handler. Ignored by a custom handler, and not applied to global threads. Added in 4.2 | [17](../lessons/0017-operating-and-monitoring-a-streams-app.md) |

Page: [Kafka Streams Configs](https://kafka.apache.org/43/configuration/kafka-streams-configs/).

## Client defaults Streams changes

| Setting | Client | Streams default | Plain client default |
|---|---|---|---|
| `auto.offset.reset` | Consumer | `earliest` | `latest` |
| `max.poll.records` | Consumer | 1000 | 500 |
| `linger.ms` | Producer | 100 | 5 |
| `transaction.timeout.ms` | Producer, under exactly-once | 10000 | 60000 |
| `delivery.timeout.ms` | Producer, under exactly-once | `Integer.MAX_VALUE` | 120000 |

The Streams defaults are from the "Default Values" table of [Configuring a Streams Application](https://kafka.apache.org/43/streams/developer-guide/config-streams/). Pass any client setting through with a prefix: `StreamsConfig.consumerPrefix`, `producerPrefix`, `mainConsumerPrefix` or `topicPrefix`.

## Deprecated names

| Deprecated | Use |
|---|---|
| `cache.max.bytes.buffering` | `statestore.cache.max.bytes` |
| `default.deserialization.exception.handler` | `deserialization.exception.handler` |
| `default.production.exception.handler` | `production.exception.handler` |
| `processing.guarantee=exactly_once`, `exactly_once_beta` | `exactly_once_v2` |
| `default.dsl.store` | `dsl.store.suppliers.class` |

Page: [Configuring a Streams Application](https://kafka.apache.org/43/streams/developer-guide/config-streams/).

## Sizing arithmetic

| Quantity | How to get it |
|---|---|
| Tasks in a sub-topology | Largest partition count among its input topics |
| Tasks in the app | Sum over sub-topologies |
| Most threads with work | Tasks in the app |
| Tasks one thread can carry | Target records per second per thread ÷ peak records per second per task, rounded down |
| Threads needed | Tasks ÷ tasks per thread, then recheck with one instance lost |
| Restoration time | Records in the task's changelog partitions ÷ measured restore rate |
| Recovery after a crash | `session.timeout.ms` plus restoration time (near zero with a caught-up standby) |
| Fastest scale-out migration | `max.warmup.replicas` tasks per `probing.rebalance.interval.ms`: 2 per 10 minutes by default |

## Sources

- [Docs: "Kafka Streams Configs", Apache Kafka 4.3](https://kafka.apache.org/43/configuration/kafka-streams-configs/)
- [Docs: "Configuring a Streams Application", Apache Kafka 4.3](https://kafka.apache.org/43/streams/developer-guide/config-streams/)
- [Docs: "Streams Rebalance Protocol", Apache Kafka 4.3](https://kafka.apache.org/43/streams/developer-guide/streams-rebalance-protocol/)
- [Docs: "Running Streams Applications", Apache Kafka 4.3](https://kafka.apache.org/43/streams/developer-guide/running-app/)
- [Docs: "Architecture", Apache Kafka 4.3](https://kafka.apache.org/43/streams/architecture/)
- [Docs: "Consumer Configs", Apache Kafka 4.3](https://kafka.apache.org/43/configuration/consumer-configs/)
- [Resources](../RESOURCES.md)
