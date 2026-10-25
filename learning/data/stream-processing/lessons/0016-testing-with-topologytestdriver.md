---
title: 16. Testing with TopologyTestDriver
description: How to test a topology's output, state and time behaviour in a unit test with no broker
type: lesson
---

# Lesson 16. Testing with TopologyTestDriver

**Mission link:** The first half of the mission's testing bullet: test a topology with `TopologyTestDriver`. It is also where the mission's "right answer when records arrive late, out of order or twice" becomes something a build can check on every commit.
**Primary source:** [Docs: "Testing a Streams Application", Apache Kafka 4.3](https://kafka.apache.org/43/streams/developer-guide/testing/)
**Prerequisites:** [Lesson 15](0015-rebalancing-restoration-and-standby-replicas.md), [Stream time](../GLOSSARY.md), [Grace period](../GLOSSARY.md), [Punctuator](../GLOSSARY.md)

## Warm-up

1. ▢ A count uses `TimeWindows.ofSizeAndGrace(Duration.ofMinutes(1), Duration.ofSeconds(30))`. Stream time is 00:01:40 when a record stamped 00:00:20 arrives. Is it counted?

<details markdown="1"><summary>Check</summary>

No. It belongs to the window from 00:00 to 00:01, which closed when stream time passed its end plus the grace period, 00:01:30. It is a late record and is dropped.

</details>

2. ▢ A processor schedules one punctuator on `STREAM_TIME` and one on `WALL_CLOCK_TIME`. Input stops arriving for an hour. Which keeps firing?

<details markdown="1"><summary>Check</summary>

The wall-clock punctuator. Stream time only advances when records arrive, so the stream-time punctuator waits for the next record.

</details>

3. ▢ Why does a KTable count emit fewer updates than it receives records, and which two settings decide how many fewer?

<details markdown="1"><summary>Check</summary>

The record cache collapses consecutive updates to the same key and forwards only the latest when it flushes, which happens at least on every commit. `statestore.cache.max.bytes` and `commit.interval.ms` decide how much is collapsed.

</details>

## Know this

### A topology, a driver, and no broker

`TopologyTestDriver`, from the `kafka-streams-test-utils` artifact, runs a [topology](../GLOSSARY.md) inside a unit test. It "works without a real Kafka broker", simulating the consumers and producers that read and write bytes, so a test runs in milliseconds ([TopologyTestDriver javadoc](https://kafka.apache.org/43/javadoc/org/apache/kafka/streams/TopologyTestDriver.html)). The test-scoped dependency:

```xml
<dependency>
    <groupId>org.apache.kafka</groupId>
    <artifactId>kafka-streams-test-utils</artifactId>
    <version>4.3.1</version>
    <scope>test</scope>
</dependency>
```

The pieces ([Testing a Streams Application](https://kafka.apache.org/43/streams/developer-guide/testing/)):

| Piece | What it does |
|---|---|
| `new TopologyTestDriver(topology, props)` | Builds the topology with these properties. Close it after every test |
| `driver.createInputTopic(name, keySerializer, valueSerializer)` | A `TestInputTopic`; each `pipeInput` processes one record through the topology before returning |
| `driver.createOutputTopic(name, keyDeserializer, valueDeserializer)` | A `TestOutputTopic`; `readKeyValue`, `readRecord`, `readKeyValuesToList`, `readKeyValuesToMap`, `isEmpty` |
| `driver.getKeyValueStore(name)`, `getTimestampedKeyValueStore`, `getWindowStore`, `getSessionStore` | The named store, to read after processing or fill before it |
| `driver.advanceWallClockTime(duration)` | Moves the driver's mocked wall clock, firing wall-clock punctuators that are due |

### Records carry the time you give them

`pipeInput(key, value, Instant)` sets each record's timestamp, and that timestamp is the record's [event time](../GLOSSARY.md) under the default extractor. Stream time in the test therefore moves exactly as your timestamps say, which makes windows and grace periods deterministic. Without explicit timestamps an input topic stamps records with the system time at which it was created ([TopologyTestDriver javadoc](https://kafka.apache.org/43/javadoc/org/apache/kafka/streams/TopologyTestDriver.html)), so which window a record lands in, and any assertion about it, depends on when the test runs. Always pipe explicit timestamps from a fixed base when time matters.

Stream-time [punctuators](../GLOSSARY.md) fire as piped records advance stream time. Wall-clock punctuators never fire from piped records; only `advanceWallClockTime` fires them ([TopologyTestDriver javadoc](https://kafka.apache.org/43/javadoc/org/apache/kafka/streams/TopologyTestDriver.html)).

### Reading state

Name the store with `Materialized.as(...)` so the test can find it. Use the typed getter that matches the store: DSL stores are timestamped, and `getKeyValueStore` on one returns a value-only view, which is fine for asserting a value. `getStateStore` is for custom stores only and throws for the built-in types. Reading a store after processing proves what the topology remembers, not only what it emitted.

### A full JUnit example

The topology counts clicks per user per one-minute window, accepts records up to 30 seconds late, and writes each update keyed as `user@windowStart`:

```java
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.time.Duration;
import java.time.Instant;
import java.util.List;
import java.util.Properties;
import org.apache.kafka.common.serialization.Serdes;
import org.apache.kafka.common.utils.Bytes;
import org.apache.kafka.streams.KeyValue;
import org.apache.kafka.streams.StreamsBuilder;
import org.apache.kafka.streams.StreamsConfig;
import org.apache.kafka.streams.TestInputTopic;
import org.apache.kafka.streams.TestOutputTopic;
import org.apache.kafka.streams.Topology;
import org.apache.kafka.streams.TopologyTestDriver;
import org.apache.kafka.streams.kstream.Consumed;
import org.apache.kafka.streams.kstream.Materialized;
import org.apache.kafka.streams.kstream.Produced;
import org.apache.kafka.streams.kstream.TimeWindows;
import org.apache.kafka.streams.state.WindowStore;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class ClicksPerMinuteTest {

    static final Instant T0 = Instant.parse("2026-01-01T00:00:00Z");

    static Topology topology() {
        StreamsBuilder builder = new StreamsBuilder();
        builder.stream("clicks", Consumed.with(Serdes.String(), Serdes.String()))
            .groupByKey()
            .windowedBy(TimeWindows.ofSizeAndGrace(Duration.ofMinutes(1), Duration.ofSeconds(30)))
            .count(Materialized.<String, Long, WindowStore<Bytes, byte[]>>as("clicks-per-minute")
                .withKeySerde(Serdes.String())
                .withValueSerde(Serdes.Long())
                .withRetention(Duration.ofMinutes(10)))
            .toStream((windowedKey, count) -> windowedKey.key() + "@" + windowedKey.window().start())
            .to("clicks-per-minute", Produced.with(Serdes.String(), Serdes.Long()));
        return builder.build();
    }

    private TopologyTestDriver driver;
    private TestInputTopic<String, String> clicks;
    private TestOutputTopic<String, Long> counts;

    @BeforeEach
    void setUp() {
        Properties props = new Properties();
        props.put(StreamsConfig.APPLICATION_ID_CONFIG, "clicks-per-minute-test");
        driver = new TopologyTestDriver(topology(), props);
        clicks = driver.createInputTopic("clicks",
            Serdes.String().serializer(), Serdes.String().serializer());
        counts = driver.createOutputTopic("clicks-per-minute",
            Serdes.String().deserializer(), Serdes.Long().deserializer());
    }

    @AfterEach
    void tearDown() {
        driver.close();
    }

    @Test
    void countsPerWindowAndDropsRecordsPastGrace() {
        clicks.pipeInput("alice", "home", T0.plusSeconds(10));
        clicks.pipeInput("alice", "cart", T0.plusSeconds(50));
        clicks.pipeInput("bob", "home", T0.plusSeconds(95));
        clicks.pipeInput("alice", "late", T0.plusSeconds(20));

        String firstWindow = "@" + T0.toEpochMilli();
        String secondWindow = "@" + T0.plusSeconds(60).toEpochMilli();
        assertEquals(List.of(
                KeyValue.pair("alice" + firstWindow, 1L),
                KeyValue.pair("alice" + firstWindow, 2L),
                KeyValue.pair("bob" + secondWindow, 1L)),
            counts.readKeyValuesToList());
        assertTrue(counts.isEmpty());

        WindowStore<String, Long> store = driver.getWindowStore("clicks-per-minute");
        assertEquals(2L, store.fetch("alice", T0.toEpochMilli()));
    }
}
```

What each line is testing:

- **One update per record.** Alice's two clicks produce two updates, 1 then 2, because the driver behaves as if it committed after every record (see below).
- **Bob's click closes Alice's window.** At 95 seconds stream time is past the first window's end plus grace, 90 seconds, so the window from 0 to 60 seconds is closed.
- **The late click is dropped.** Alice's record stamped 20 seconds falls in the closed window: no output, and the store still holds 2.
- **`withRetention` is there for the assertion.** A window store's default retention is the window size plus grace ([Materialized javadoc](https://kafka.apache.org/43/javadoc/org/apache/kafka/streams/kstream/Materialized.html)), 90 seconds here. At a stream time of 95 seconds the first window, which ends at 60, is still kept, and the test passes without the line. Pipe one more record a few minutes later, though, and the default retention can expire the window the assertion reads. The longer retention keeps the assertion about the count, not about how far the test moved stream time.

### Testing a wall-clock punctuator

This processor forwards how many records it saw each minute of wall-clock time. It keeps the count in a field to stay short; lesson 7's version would keep it in a store so it survives a failure.

```java
class CountEveryMinute implements Processor<String, String, String, Long> {
    private long seen;

    @Override
    public void init(ProcessorContext<String, Long> context) {
        context.schedule(Duration.ofMinutes(1), PunctuationType.WALL_CLOCK_TIME, now -> {
            context.forward(new Record<>("seen", seen, now));
            seen = 0;
        });
    }

    @Override
    public void process(Record<String, String> record) {
        seen++;
    }
}
```

Wire it with `builder.stream("clicks", ...).process(CountEveryMinute::new).to("seen-per-minute", ...)`, read `seen-per-minute` through a `TestOutputTopic` called `perMinute`, then:

```java
clicks.pipeInput("alice", "home", T0);
clicks.pipeInput("bob", "home", T0.plusSeconds(3600));
assertTrue(perMinute.isEmpty());

driver.advanceWallClockTime(Duration.ofMinutes(1));
assertEquals(KeyValue.pair("seen", 2L), perMinute.readKeyValue());
```

An hour of event time fires nothing, because the punctuator follows [processing time](../GLOSSARY.md); one mocked minute of wall clock fires it once.

### What a passing driver test does not prove

| The driver | So it does not test |
|---|---|
| Processes each record synchronously, as if committing and flushing after every record; `commit.interval.ms` and the cache size "have no effect" ([TopologyTestDriver javadoc](https://kafka.apache.org/43/javadoc/org/apache/kafka/streams/TopologyTestDriver.html)) | How many intermediate KTable updates production emits. With the [record cache](../GLOSSARY.md) on, production usually emits fewer. Assert final values or stored state, or test through `suppress`, not the exact intermediate sequence |
| Simulates single-partitioned input topics | Per-partition stream time. In the driver every key shares one task and one stream time; in production a record only advances the stream time of its own partition's task. Also co-partitioning and partition counts |
| Runs one topology in one process | Tasks, threads, rebalancing, restoration, standby and warmup replicas: lessons 14 and 15 |
| Needs no broker | Transactions under `exactly_once_v2`: fencing, aborts, what a `read_committed` consumer sees. Also the creation and configuration of internal topics on a real cluster |

Those need an integration test against a real broker, and an operator who reads the running app's metrics, which is lesson 17.

### Predict, then run

Before running the example test, predict the exact list `readKeyValuesToList()` returns. Then change the grace period to `Duration.ofSeconds(60)` and predict again: does the late click now count, and which assertions fail?

With 60 seconds of grace the first window closes at 120 seconds, so at stream time 95 it is still open: Alice's late click counts, a fourth update `alice@...` with value 3 appears, and both the list assertion and the store assertion fail.

## Practice

1. ▢ Which `TestInputTopic` call gives a record an explicit event time, and which driver call fires a wall-clock punctuator?

<details markdown="1"><summary>Check</summary>

`pipeInput(key, value, Instant)` (or the overload taking a `long` of milliseconds) sets the timestamp. `driver.advanceWallClockTime(Duration)` moves the mocked wall clock and fires any wall-clock punctuator that is due.

</details>

2. ▢ A driver test pipes three records for key `a` into a KTable count and asserts three updates on the output topic. It passes. What does the same topology emit in production with default settings?

    - a) Exactly three updates, matching what the driver emitted
    - b) Possibly fewer updates, since the cache collapses them
    - c) Exactly one update, because counts emit only finals
    - d) More updates, one per partition the key touches

<details markdown="1"><summary>Check</summary>

**b)** The record cache collapses updates to the same key between flushes, so production may forward only the latest. (a) is wrong: the driver acts as if it commits after every record, which production does not. (c) is wrong: a count emits a stream of updates, and only `suppress` holds them back to a final result. (d) is wrong: one key lives in one partition and one task.

</details>

3. ▢ Interleave lesson 10: after the example test's four records, two more are piped: Alice at `T0.plusSeconds(55)` and Alice at `T0.plusSeconds(70)`. Predict what the output topic receives.

<details markdown="1"><summary>Hint</summary>

Work out each record's window before deciding whether it is late. Stream time is 95 seconds.

</details>

<details markdown="1"><summary>Check</summary>

One record, Alice's count of 1 for the window starting at 60 seconds. The 55-second click belongs to the window from 0 to 60 seconds, closed since stream time passed 90, so it is dropped. The 70-second click belongs to the window from 60 to 120 seconds, which closes at 150, so it is accepted and starts Alice's count there.

</details>

4. ▢ A test pipes Alice at 10 seconds, Bob at 95 seconds, then Alice at 20 seconds, and asserts the last record is dropped. It passes. In production, the late Alice click is counted. Nothing is wrong with the topology. Explain the difference, and fix the test so it states what production does.

<details markdown="1"><summary>Hint</summary>

Ask whose stream time Bob's record advances in production, and how many partitions the driver simulates.

</details>

<details markdown="1"><summary>Check</summary>

Stream time is per task, and a task owns one partition of the input. In production Alice and Bob hash to different partitions, so Bob's 95-second click advances only his task's stream time, and Alice's window is still open when her 20-second click arrives. The driver simulates one partition, so every key shares one stream time. Fix the test by advancing stream time with a record that would share Alice's partition in production, the simplest being another Alice record at 95 seconds, and keep a separate test documenting that another key does not close her window in production.

</details>

5. ▢ Write the pipes and assertions that prove `CountEveryMinute` resets its count after each punctuation, and say what it forwards in a minute with no records.

<details markdown="1"><summary>Check</summary>

Pipe two records, advance one minute, assert `("seen", 2L)`. Pipe one record, advance one minute, assert `("seen", 1L)`. Advance one more minute with nothing piped and assert `("seen", 0L)`: the punctuator fires on wall-clock time whether or not records arrived, so it forwards a zero every idle minute. If downstream should not see zeros, that is a bug this test just found.

</details>

## Real-world reps

- [ ] Today: run the example test, then change the grace period to 60 seconds and check your prediction from predict-then-run.
- [ ] Write one driver test for a topology you own that pipes a record after its window's grace period and asserts it is dropped, using explicit timestamps from a fixed base.
- [ ] Tomorrow: list which of your topology's behaviours the driver cannot check, using the last table in this lesson, and note which of them an integration test or a metric covers today.

## Going further

- [Configuration](../reference/configuration.md)
- [Docs: "Testing a Streams Application", Apache Kafka 4.3](https://kafka.apache.org/43/streams/developer-guide/testing/)
- [Javadoc: "TopologyTestDriver", Apache Kafka 4.3](https://kafka.apache.org/43/javadoc/org/apache/kafka/streams/TopologyTestDriver.html)
- [Javadoc: "TimeWindows", Apache Kafka 4.3](https://kafka.apache.org/43/javadoc/org/apache/kafka/streams/kstream/TimeWindows.html)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
