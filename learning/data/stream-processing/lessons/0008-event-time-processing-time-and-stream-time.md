---
title: 8. Event Time, Processing Time and Stream Time
description: Which clock a Streams operation follows, where a record's timestamp comes from, and why stream time only moves forward
type: lesson
---

# Lesson 8. Event Time, Processing Time and Stream Time

**Mission link:** Stage 4 delivers the mission's promise to pick a window and a grace period for a time-based question and to say which late records it drops and when it emits. Every one of those answers is measured on a clock, so this lesson settles which clock, and where its readings come from, before the next two lessons build windows on it.
**Primary source:** [Docs: "Core Concepts", Apache Kafka 4.3](https://kafka.apache.org/43/streams/core-concepts/) (the Time section)
**Prerequisites:** [Lesson 7](0007-the-processor-api.md), [Event time](../GLOSSARY.md), [Stream time](../GLOSSARY.md), [Timestamp extractor](../GLOSSARY.md)

## Warm-up

1. ▢ A `count()` on a grouped stream receives three records for key `A` within one commit interval. With the record cache on, how many updates for `A` might reach the output topic, and what decides it?

<details markdown="1"><summary>Check</summary>

Anywhere from one to three. A KTable emits a stream of updates, and the record cache collapses consecutive updates to the same key until it is flushed, which happens on every commit or when the cache fills. So `commit.interval.ms` and `statestore.cache.max.bytes` decide how many intermediate counts survive, not the logic of the count.

</details>

2. ▢ In the Processor API, a punctuator can be scheduled on one of two kinds of time. Name them, and say which one fires when no records arrive at all.

<details markdown="1"><summary>Check</summary>

Stream time (`PunctuationType.STREAM_TIME`) and wall-clock time (`PunctuationType.WALL_CLOCK_TIME`). Only the wall-clock punctuator fires with no input, because stream time advances only when a record arrives. That difference is the subject of this lesson.

</details>

## Know this

### Three clocks a record can be measured on

The Core Concepts page names three notions of time ([Core Concepts](https://kafka.apache.org/43/streams/core-concepts/)):

- **[Event time](../GLOSSARY.md):** when the event happened at its source. A sensor reading taken at 10:00:02 has that event time whether it reaches Kafka a millisecond later or after a day offline.
- **Ingestion time:** when a broker appended the record to a partition. A record that is never processed still has one.
- **[Processing time](../GLOSSARY.md):** the wall-clock time of the machine running your processor when it handles the record. Reprocess the same topic tomorrow and every processing time changes.

Windows and joins in Kafka Streams follow the timestamp each record carries, so the choice between these is really a choice of what that timestamp means. For why no machine's clock can be trusted to order events across machines in the first place, see [Time and Order: physical clocks](../../../architecture/distributed-systems/reference/time-and-order.md#physical-clocks).

### Where the timestamp comes from

Every Kafka record carries a timestamp in its metadata. Which of the first two clocks it holds is decided by the broker, not by your application: the broker setting `log.message.timestamp.type`, or the topic setting `message.timestamp.type` ([Configuring a Streams Application](https://kafka.apache.org/43/streams/developer-guide/config-streams/)).

| Setting value | The record's timestamp is | Semantics you get |
|---|---|---|
| `CreateTime` (the default) | What the producer put there, which the Java producer fills with its own clock when the caller leaves it unset | Event time, if the producer set it from the event |
| `LogAppendTime` | Overwritten by the broker on append | Ingestion time |

So `CreateTime` is only as good as the producer. A producer that leaves the timestamp unset stamps the moment it sent the record, which is close to event time for a live sensor and nowhere near it for a batch job replaying last week's orders.

### The timestamp extractor decides what Streams believes

Kafka Streams does not use the metadata timestamp directly. It asks a **[timestamp extractor](../GLOSSARY.md)**, an implementation of `TimestampExtractor`, whose one method is `long extract(ConsumerRecord<Object, Object> record, long partitionTime)`. The returned value must be milliseconds since the epoch; a negative return makes Streams skip the record silently, and throwing an exception stops the application ([TimestampExtractor](https://kafka.apache.org/43/javadoc/org/apache/kafka/streams/processor/TimestampExtractor.html)). `partitionTime` is the highest valid timestamp extracted so far from the record's partition, or -1 if there is none yet.

The built-ins, set application-wide with `default.timestamp.extractor` ([Configuring a Streams Application](https://kafka.apache.org/43/streams/developer-guide/config-streams/)):

| Extractor | Returns | On a negative (invalid) metadata timestamp |
|---|---|---|
| `FailOnInvalidTimestamp` (the default) | The metadata timestamp | Throws, and the application stops |
| `LogAndSkipOnInvalidTimestamp` | The metadata timestamp | Logs a warning; the record is dropped |
| `UsePartitionTimeOnInvalidTimestamp` | The metadata timestamp | Uses `partitionTime` instead; throws if there is none |
| `WallclockTimestampExtractor` | `System.currentTimeMillis()`, ignoring the record | Not applicable |

`WallclockTimestampExtractor` is how you get processing-time semantics: every timestamp becomes "now". It also makes every result depend on when the app happened to run, so a replay produces different windows.

When the event time lives in the payload, as `placedAt` on an order usually does, write your own. The extractor sees the deserialized value, and can be set per source with `Consumed#withTimestampExtractor`, so one topic can use it while the rest keep the default:

```java
public class OrderTimeExtractor implements TimestampExtractor {
    @Override
    public long extract(ConsumerRecord<Object, Object> record, long partitionTime) {
        if (record.value() instanceof Order order && order.placedAtMillis() >= 0) {
            return order.placedAtMillis();
        }
        // No usable event time: borrow the partition's progress rather than drop the order.
        return partitionTime >= 0 ? partitionTime : record.timestamp();
    }
}

KStream<String, Order> orders = builder.stream("orders",
        Consumed.with(Serdes.String(), orderSerde)
                .withTimestampExtractor(new OrderTimeExtractor()));
```

The extractor must be stateless, and its value can become the timestamp of records Streams writes to changelogs and output topics, where brokers use it for retention and log rolling. A nonsense timestamp there costs broker performance, not just a wrong window ([TimestampExtractor](https://kafka.apache.org/43/javadoc/org/apache/kafka/streams/processor/TimestampExtractor.html)).

### Stream time: the clock windows actually read

Kafka Streams never asks the wall clock whether a window is over. It keeps **[stream time](../GLOSSARY.md)**: "the maximum observed record timestamp so far (including the currently processed record)", tracked "on a per-task basis and is preserved across restarts and during task migration" ([ProcessingContext#currentStreamTimeMs](https://kafka.apache.org/43/javadoc/org/apache/kafka/streams/processor/api/ProcessingContext.html)). Three consequences follow from "maximum", and lessons 9 and 10 lean on all of them:

1. **It only moves forward.** A record older than stream time is processed, but it does not pull stream time back. That is what makes "late" well defined: a record is out of order exactly when its timestamp is below the current stream time.
2. **It moves only when records arrive.** No input, no progress, however much wall-clock time passes. Core Concepts calls it "data-driven time" for this reason.
3. **It is per task.** Two tasks of one app can be hours apart in stream time if one reads a busy partition and the other a quiet one.

Within a task that reads several partitions, as a join does, Streams picks the next record from the partition whose buffered head has the lowest timestamp, and `max.task.idle.ms` (default 0) controls how long it waits for an empty partition before going on without it ([Configuring a Streams Application](https://kafka.apache.org/43/streams/developer-guide/config-streams/)). Lesson 11 returns to that for joins.

This is where Kafka Streams differs from Flink, which tracks event-time progress with a separate signal called a watermark, which a watermark generator inserts into the stream. Stream time has no such signal; it is derived from record timestamps alone. If you need the comparison, Flink's own [Timely Stream Processing](https://nightlies.apache.org/flink/flink-docs-stable/docs/concepts/time/) page describes watermarks; lesson 18 weighs it.

### Timestamps on what Streams writes

Every output record gets a timestamp too, by these rules from [Core Concepts](https://kafka.apache.org/43/streams/core-concepts/):

| Output produced by | Its timestamp |
|---|---|
| A stateless operation, `flatMap` and its siblings included | The input record's, passed through |
| `forward()` inside `process()` | Inherited from the input record, unless you set one with `Record#withTimestamp` |
| A punctuator | The task's current internal time when it fires, read with `context.timestamp()` |
| An aggregation | The maximum timestamp of the input records contributing to that result, per key (per window, for a windowed one) |
| A stream-stream or table-table join | `max(left.ts, right.ts)` |
| A stream-table join | The stream record's |

These matter because the output becomes someone else's input: a downstream Streams app using the default extractor will window your results by the timestamps chosen here.

### Worked example: stream time over five records

One task, default extractor, `CreateTime` topic. Records arrive in offset order with these timestamps (seconds past 10:00:00):

| Arrival | Record timestamp | Stream time after it | Out of order? |
|---|---|---|---|
| 1 | 05 | 05 | No |
| 2 | 02 | 05 | Yes, 3 s behind |
| 3 | 09 | 09 | No |
| 4 | 07 | 09 | Yes, 2 s behind |
| 5 | 08 | 09 | Yes, 1 s behind |

Stream time ends at 09 even though five records were processed and the wall clock may say 10:42. The "behind" column is what the task metrics `record-lateness-avg` and `record-lateness-max` report, stream time minus record timestamp, at the debug recording level ([Streams Monitoring](https://kafka.apache.org/43/operations/monitoring/#streams-monitoring)). Nothing was dropped: dropping is what a window does with a record that is too far behind, and that is lesson 10.

### Predict, then run

This topology forwards each value replaced by its own timestamp and the task's stream time at that moment. It runs in a unit test with `TopologyTestDriver` (lesson 16 covers the driver properly):

```java
StreamsBuilder builder = new StreamsBuilder();
builder.stream("in", Consumed.with(Serdes.String(), Serdes.String()))
       .processValues(() -> new ContextualFixedKeyProcessor<String, String, String>() {
           @Override
           public void process(FixedKeyRecord<String, String> record) {
               context().forward(record.withValue(
                       "ts=" + record.timestamp() + " streamTime=" + context().currentStreamTimeMs()));
           }
       })
       .to("out", Produced.with(Serdes.String(), Serdes.String()));

Properties props = new Properties();
props.put(StreamsConfig.APPLICATION_ID_CONFIG, "clocks");
try (TopologyTestDriver driver = new TopologyTestDriver(builder.build(), props)) {
    TestInputTopic<String, String> in =
            driver.createInputTopic("in", new StringSerializer(), new StringSerializer());
    TestOutputTopic<String, String> out =
            driver.createOutputTopic("out", new StringDeserializer(), new StringDeserializer());
    in.pipeInput("k", "a", 5_000L);
    in.pipeInput("k", "b", 2_000L);
    in.pipeInput("k", "c", 9_000L);
    in.pipeInput("k", "d", 7_000L);
    out.readValuesToList().forEach(System.out::println);
}
```

Before running it, write down the four lines it prints. Then run it. Predicted correctly, it shows the output timestamps inherited from the input and stream time standing still on the two older records.

## Practice

1. ▢ Name the three notions of time from Core Concepts, and for each say what in the system records it.

<details markdown="1"><summary>Check</summary>

Event time: the source, through the producer setting the record timestamp (or a field in the value). Ingestion time: the broker, when the topic uses `LogAppendTime`. Processing time: the wall clock of the machine running the processor, which is what `WallclockTimestampExtractor` returns.

</details>

2. ▢ A topic uses `LogAppendTime`, and the app keeps the default extractor. Which semantics does the app get?

    - a) Event time, because the default extractor reads the record timestamp
    - b) Ingestion time, because the broker has overwritten the record timestamp
    - c) Processing time, because the default extractor reads the wall clock
    - d) Stream time, because the default extractor computes the running maximum

<details markdown="1"><summary>Check</summary>

**b)** The default `FailOnInvalidTimestamp` returns the metadata timestamp, and under `LogAppendTime` the broker wrote that at append. (a) is wrong because the producer's value was replaced. (c) describes `WallclockTimestampExtractor`, not the default. (d) confuses an extractor with stream time, which Streams derives from extracted timestamps; no extractor computes it.

</details>

3. ▢ The predict-then-run topology above prints four lines. Write them.

<details markdown="1"><summary>Hint</summary>

Stream time is a running maximum that includes the record being processed. The output timestamp of a `processValues` step is inherited.

</details>

<details markdown="1"><summary>Check</summary>

```text
ts=5000 streamTime=5000
ts=2000 streamTime=5000
ts=9000 streamTime=9000
ts=7000 streamTime=9000
```

Each record keeps its own timestamp, because a stateless step passes it through. Stream time takes the maximum including the current record, so it rises on the first and third records and stays put on the two older ones.

</details>

4. ▢ An app sets `default.timestamp.extractor` to `WallclockTimestampExtractor` "because the producer clocks are unreliable". It counts orders per hour. Last night it was down from 01:00 to 03:00 and caught up on restart. What do the 01:00 and 02:00 hourly counts show, and what does the 03:00 count show?

<details markdown="1"><summary>Hint</summary>

Ask what timestamp each caught-up order received, and which hour that places it in.

</details>

<details markdown="1"><summary>Check</summary>

The 01:00 and 02:00 counts show nothing, or only what was processed before the outage, and the 03:00 count holds every order from the outage as well as its own. Wall-clock time stamps each order with the moment the app processed it, so two hours of orders all land in the hour of the catch-up. A reprocess from the start of the topic would produce yet another answer. The fix for an untrustworthy producer clock is an event time field in the payload and a custom extractor, not the wall clock.

</details>

5. ▢ Interleave lesson 6: a windowed count's result record goes to an output topic. A downstream app reads that topic with the default extractor and windows it again. What timestamp does it see on each result, and why can that differ from the time the result was written?

<details markdown="1"><summary>Check</summary>

The maximum timestamp of the input records that contributed to that window's result, because that is the rule for aggregation output. It is an event-time reading, so a result written at 11:00 for a window whose latest input was stamped 10:07 carries 10:07. The record cache from lesson 6 changes how many updates are written, not the timestamp each one carries.

</details>

## Real-world reps

- [ ] Today: run the predict-then-run test with your four predicted lines written down first. Then pipe a fifth record at `1_000L` and predict its line before you look.
- [ ] Find a topic you produce to and check its timestamp type with `kafka-configs.sh --describe --all` on the topic (look for `message.timestamp.type`), then read the producer code and decide whether its `CreateTime` is really event time.
- [ ] Tomorrow: without notes, write the four built-in extractors and what each does with a negative timestamp, then check against the table in this lesson.

## Going further

- [Time and Windows](../reference/time-and-windows.md)
- [Docs: "Core Concepts", Apache Kafka 4.3](https://kafka.apache.org/43/streams/core-concepts/)
- [Docs: "Configuring a Streams Application", Apache Kafka 4.3](https://kafka.apache.org/43/streams/developer-guide/config-streams/) (`default.timestamp.extractor` and `max.task.idle.ms`)
- [Article: "Streaming 101: The world beyond batch", Tyler Akidau, O'Reilly (2015)](https://www.oreilly.com/radar/the-world-beyond-batch-streaming-101/)
- [Time and Order](../../../architecture/distributed-systems/reference/time-and-order.md), for why physical clocks cannot order events across machines
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
