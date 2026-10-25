---
title: 7. The Processor API
description: When to drop below the DSL to a custom processor with its own store and punctuator, and what you then own
type: lesson
---

# Lesson 7. The Processor API

**Mission link:** Some stateful steps have no DSL operator: expiring keys that went quiet, deduplicating by ID, emitting on a timer. This lesson closes stage 3 by writing such a step yourself, choosing its store and the clock that drives it, and naming every guarantee the DSL was quietly providing.
**Primary source:** [Docs: "Processor API", Apache Kafka 4.3](https://kafka.apache.org/43/streams/developer-guide/processor-api/)
**Prerequisites:** [Lesson 6](0006-aggregations-ktables-and-the-record-cache.md), [Processor API](../GLOSSARY.md), [Punctuator](../GLOSSARY.md), [Stream time](../GLOSSARY.md)

## Warm-up

1. ▢ In a DSL aggregation with default settings, what decides the moment an updated value reaches the next processor?

<details markdown="1"><summary>Check</summary>

The record cache. The update waits in the cache until it is flushed, at the next commit (every 30 seconds under at-least-once) or earlier if cache pressure evicts it. With the cache at 0 every update is forwarded at once.

</details>

2. ▢ An app with application ID `pay-dedup` has a store named `seen-ids` with logging enabled. Name its changelog topic, and say what happens to the store's contents when the instance holding it dies.

<details markdown="1"><summary>Check</summary>

`pay-dedup-seen-ids-changelog`. The task moves to another instance, which restores the store by replaying that changelog before processing anything. With logging disabled it would start empty instead.

</details>

3. ▢ Name two DSL operations that mark a stream for repartitioning, and one that transforms records without doing so.

<details markdown="1"><summary>Check</summary>

`selectKey`, `map` and `flatMap` all may change the key, so they mark the stream, and the next stateful step writes a repartition topic. `mapValues`, `flatMapValues` and `filter` leave the key alone and mark nothing.

</details>

## Know this

### When the DSL is not enough

The DSL builds every topology out of processors; the **[Processor API](../GLOSSARY.md)** lets you write one yourself ([Processor API](https://kafka.apache.org/43/streams/developer-guide/processor-api/)). Reach for it when a step needs something no operator offers:

- **Acting on time, not records:** emit or delete state on a schedule, such as flagging a device that stopped reporting.
- **State access the DSL hides:** read a key before deciding whether to forward, scan a range, delete entries yourself.
- **Record metadata:** only the Processor API exposes the source topic, partition and offset of the record being processed.

If an operator can express the step, keep the operator. The DSL names and materializes its stores, wires serdes, inserts repartition topics, and emits through the record cache. Each of those becomes your job below it.

### The processor contract

A processor implements `Processor<KIn, VIn, KOut, VOut>` from `org.apache.kafka.streams.processor.api`: input key and value types, then the types it forwards ([Processor javadoc](https://kafka.apache.org/43/javadoc/org/apache/kafka/streams/processor/api/Processor.html)). Use `Void` for an output type the processor never forwards.

| Method | Called | Do here | Do not |
|---|---|---|---|
| `init(ProcessorContext<KOut, VOut>)` | Once per task, while the task is constructed | Fetch stores, schedule punctuators, keep the context | Assume it runs once per JVM: a processor may be reused with `init` called again after `close` |
| `process(Record<KIn, VIn>)` | For every input record | Read and write stores, forward results | Mutate the input record's headers before forwarding it |
| `close()` | When the task is closed | Release your own resources | Write to Kafka (the clients are already closed) or close stores (the library owns them) |

The topology takes a `ProcessorSupplier`, and its `get()` must return a new processor every time, because each task needs its own, holding its own context and store shard. Kafka Streams checks this as you wire the processor in and throws an `IllegalArgumentException` if two calls return the same object.

### Attaching a store

A processor's store is described by a `StoreBuilder`, from the same `Stores` factory lesson 5's engines came from, and connected by name:

```java
builder.addStateStore(Stores.keyValueStoreBuilder(
        Stores.persistentKeyValueStore("last-seen"), Serdes.String(), Serdes.Long()));
builder.stream("readings", Consumed.with(Serdes.String(), Serdes.String()))
       .process(IdleDeviceProcessor::new, "last-seen");
```

Alternatively the supplier can return its builders from `ConnectedStoreProvider#stores()`, so the processor brings its own store. Either way, `context.getStateStore("last-seen")` in `init` returns this task's shard, which no other task may use ([ProcessingContext javadoc](https://kafka.apache.org/43/javadoc/org/apache/kafka/streams/processor/api/ProcessingContext.html)).

A `StoreBuilder` has logging on, so the store gets a `<application.id>-last-seen-changelog` and restores like any DSL store. It has caching off until you call `withCachingEnabled()`. The Memory Management page describes the default ambiguously; the 4.3 source sets it explicitly ([`AbstractStoreBuilder`](https://github.com/apache/kafka/blob/4.3/streams/src/main/java/org/apache/kafka/streams/state/internals/AbstractStoreBuilder.java)). Even when enabled, a cache on a Processor API store compacts only writes to the store, never what you forward ([Memory Management](https://kafka.apache.org/43/streams/developer-guide/memory-mgmt/)). Close every iterator a store returns, with try-with-resources, or memory grows until the process dies.

### Forwarding, and the timestamp you choose

Nothing leaves a processor unless you call `context.forward(record)`, which sends the record to every child, or `forward(record, childName)` for one. `Record` is immutable: `record.withValue(v)` returns a copy that keeps the input's key, timestamp and headers, and the copy is shallow, so mutable keys, values and headers are still shared.

The output timestamp is whatever the forwarded `Record` carries. `withValue` keeps the input's event time, which is usually right inside `process()`. In a punctuator there is no input record, so you pick the timestamp, and `context.recordMetadata()` is empty there, since no source record exists.

### Punctuators: which clock fires them

`context.schedule(Duration interval, PunctuationType type, Punctuator callback)` registers a **[punctuator](../GLOSSARY.md)**, a callback that receives a timestamp, and returns a `Cancellable`. The type picks the clock ([Processor API](https://kafka.apache.org/43/streams/developer-guide/processor-api/), [PunctuationType javadoc](https://kafka.apache.org/43/javadoc/org/apache/kafka/streams/processor/PunctuationType.html)):

| | `STREAM_TIME` | `WALL_CLOCK_TIME` |
|---|---|---|
| Advanced by | Record timestamps: **[stream time](../GLOSSARY.md)** is the largest timestamp the task has seen | The machine's clock, checked as the processing loop polls |
| With no input | Never fires | Fires anyway |
| 60 records stamped 1 s to 60 s, interval 10 s | 6 calls, however long processing takes | 2 calls if processing takes 20 s, none if it takes 5 s |
| Reprocessing old data | Fires as the old timestamps pass, so results match the original run | Fires on today's clock, so results depend on how fast the replay ran |
| Precision | Exact in stream time | Best effort, limited by one loop iteration |

A punctuation that falls behind is not replayed once per missed interval: when one record moves stream time 25 minutes forward, a 1-minute punctuator fires once, with the new stream time.

### Worked example: flagging idle devices

Devices send readings keyed by device ID. A device that has sent nothing for 30 minutes of event time should be reported once as `idle` and forgotten. No DSL operator emits on the absence of records, so this is a processor with a store and a stream-time punctuator:

```java
public class IdleDeviceProcessor implements Processor<String, String, String, String> {
    static final String STORE = "last-seen";
    static final Duration IDLE_AFTER = Duration.ofMinutes(30);

    private ProcessorContext<String, String> context;
    private KeyValueStore<String, Long> lastSeen;

    @Override
    public void init(ProcessorContext<String, String> context) {
        this.context = context;
        this.lastSeen = context.getStateStore(STORE);
        context.schedule(Duration.ofMinutes(1), PunctuationType.STREAM_TIME, this::expire);
    }

    @Override
    public void process(Record<String, String> record) {
        lastSeen.put(record.key(), record.timestamp());
    }

    private void expire(long streamTime) {
        long cutoff = streamTime - IDLE_AFTER.toMillis();
        List<String> idle = new ArrayList<>();
        try (KeyValueIterator<String, Long> it = lastSeen.all()) {
            while (it.hasNext()) {
                KeyValue<String, Long> entry = it.next();
                if (entry.value < cutoff) idle.add(entry.key);
            }
        }
        for (String device : idle) {
            context.forward(new Record<>(device, "idle", streamTime));
            lastSeen.delete(device);
        }
    }
}
```

Three choices in it are yours, not the library's. The store holds one entry per device until the punctuator deletes it, so expiry is also what bounds the store's size. Keys are collected first and deleted after the iterator closes, rather than deleted mid-scan. The output is stamped with the stream time at which the idleness was detected.

`describe()` prints one sub-topology: source, `KSTREAM-PROCESSOR-0000000001 (stores: [last-seen])`, sink. Run it, and the app also gets a `last-seen` changelog, since logging is on.

### Mixing with the DSL: `process()` or `processValues()`

You rarely build a whole app from raw processors. `KStream#process` and `KStream#processValues` drop one into a DSL topology, and they differ in what they promise about the key ([KStream javadoc](https://kafka.apache.org/43/javadoc/org/apache/kafka/streams/kstream/KStream.html)):

| | `process(ProcessorSupplier, stores...)` | `processValues(FixedKeyProcessorSupplier, stores...)` |
|---|---|---|
| Processor type | `Processor`, may change the key | `FixedKeyProcessor`, the key cannot change |
| Marks the stream for repartitioning | Yes: a later aggregation or join writes a repartition topic | No |
| Repartitions its own input first | No, even after a key change; call `repartition()` before it if needed | No |
| Forward from a punctuator | Yes | No |

The idle detector forwards from its punctuator, so it needs `process()`. A processor that forwards only from `process()` and keeps the key belongs in `processValues()`, and putting it in `process()` instead costs a repartition topic downstream for nothing. Checked with `describe()`: the same `processValues(...).groupByKey().count()` chain is one sub-topology, while `process(...).groupByKey().count()` splits into two joined by a `-repartition` topic.

### What you own below the DSL

| Concern | The DSL did | Now you |
|---|---|---|
| Store | Created, named and sized it | Choose engine and name; delete what you no longer need, or it grows forever |
| Changelog | Logged every store | Keep logging on unless losing the store is harmless; it is on by default |
| Serdes | Took them from `Materialized`, `Grouped` and `Produced` | Pass them to the `StoreBuilder` and to the sink |
| Emitting | Forwarded every change, through the record cache | Call `forward` for each output; caching never compacts it |
| Timestamps | Derived output timestamps from inputs | Set the timestamp on every record you create, especially in punctuators |
| Partitioning | Repartitioned before stateful steps | Call `repartition()` before a stateful processor whose key changed upstream |
| Testing | Covered by its own tests | Drive punctuators yourself: stream time by piping records, wall-clock time with `advanceWallClockTime` |

### Predict, then run

Wire the idle detector to an output topic `idle-devices` and drive it with `TopologyTestDriver`, starting at `t0`. After each step, predict which `idle` records appear:

```java
in.pipeInput("a", "21.5", t0);
in.pipeInput("b", "19.0", t0);
in.pipeInput("a", "21.7", t0.plus(Duration.ofMinutes(20)));
in.pipeInput("c", "18.2", t0.plus(Duration.ofMinutes(45)));
driver.advanceWallClockTime(Duration.ofHours(2));
in.pipeInput("c", "18.3", t0.plus(Duration.ofMinutes(55)));
```

<details markdown="1"><summary>Hint</summary>

Track stream time after each line, compute the cutoff as stream time minus 30 minutes, and compare it with each device's last-seen time. Then ask which clock the punctuator was scheduled on.

</details>

<details markdown="1"><summary>Check</summary>

Nothing after the readings at `t0` and at 20 minutes: the cutoffs are negative and minus 10 minutes. At 45 minutes the cutoff is 15 minutes, `b` was last seen at 0, so `b` is reported idle, stamped `t0` plus 45 minutes; `a`, at 20, is not. Advancing the wall clock by two hours does nothing, because the punctuator runs on stream time and no record moved it. At 55 minutes the cutoff is 25, and `a`, last seen at 20, is reported. `a` actually crossed 30 minutes of silence at 50 minutes; with no record in between, nobody noticed. On a partition that goes quiet, a stream-time punctuator never fires at all.

</details>

## Practice

1. ▢ Name the three methods of `Processor`, when each is called, and one thing you must not do in `close()`.

<details markdown="1"><summary>Check</summary>

`init` once per task during construction, possibly again after `close` if the processor is reused; `process` for every input record; `close` when the task closes. In `close` you must not write to Kafka, because the clients are already closed, and must not close state stores, which the library manages.

</details>

2. ▢ Which statement about a `STREAM_TIME` punctuator is true?

    - a) It fires on schedule even while no new records arrive
    - b) It fires only when record timestamps move stream time forward
    - c) It fires once per missed interval after a long gap
    - d) It fires based on the time each record was processed

<details markdown="1"><summary>Check</summary>

**b)** Stream time is derived from record timestamps, so the punctuator depends on input. (a) describes `WALL_CLOCK_TIME`. (c) is wrong: a jump in stream time triggers one punctuation, not one per interval skipped. (d) describes processing time, which only the wall-clock type follows.

</details>

3. ▢ Interleave lesson 4. Write a processor that drops any payment whose key, a payment ID, it has already seen, and wire it in front of `groupByKey().count()` without creating a repartition topic. Say which DSL method you used and why.

<details markdown="1"><summary>Check</summary>

It forwards only from `process()` and never changes the key, so it is a `FixedKeyProcessor` wired with `processValues()`, which does not mark the stream for repartitioning:

```java
public class DedupProcessor implements FixedKeyProcessor<String, String, String> {
    private FixedKeyProcessorContext<String, String> context;
    private KeyValueStore<String, Long> seen;

    @Override
    public void init(FixedKeyProcessorContext<String, String> context) {
        this.context = context;
        this.seen = context.getStateStore("seen-ids");
    }

    @Override
    public void process(FixedKeyRecord<String, String> record) {
        if (seen.get(record.key()) == null) {
            seen.put(record.key(), record.timestamp());
            context.forward(record);
        }
    }
}
```

Wired as `builder.addStateStore(Stores.keyValueStoreBuilder(Stores.persistentKeyValueStore("seen-ids"), Serdes.String(), Serdes.Long()))` and `stream.processValues(DedupProcessor::new, "seen-ids").groupByKey().count()`. With `process()` the same logic would make `groupByKey()` write a repartition topic, because `process()` counts as a key change.

</details>

4. ▢ A colleague wires `stream.process(() -> sharedProcessor, "seen-ids")`, where `sharedProcessor` is one field created at startup, to save allocating objects. Building the topology throws `IllegalArgumentException: ... generates single reference ... must return a new object each time it is called`. Their input topic has one partition, so they argue only one processor is ever needed. What is wrong with the argument, and what is the fix?

<details markdown="1"><summary>Hint</summary>

Ask what a processor instance belongs to, and how that count changes when the topic or the topology grows.

</details>

<details markdown="1"><summary>Check</summary>

A processor belongs to a task, not to the application. Every task calls `get()` for its own instance, holding its own context and store shard, and the task count follows the partitions: the day the topic grows to six partitions, six tasks would share one processor and one store reference across threads. Kafka Streams refuses the shared supplier up front, whatever the partition count, so the bug cannot wait for that day. Pass `DedupProcessor::new`, or return `new DedupProcessor()` from `get()`.

</details>

5. ▢ The dedup store from item 3 is fine in testing, but after six months in production its disk use is still growing. Add expiry for IDs older than 24 hours, and choose the punctuation type, given that the team sometimes resets the app to reprocess a month of history.

<details markdown="1"><summary>Hint</summary>

Think about what each clock does during a reprocessing run that covers a month of timestamps in an hour.

</details>

<details markdown="1"><summary>Check</summary>

Nothing ever deletes an entry, so the store holds every ID ever seen. Schedule a `STREAM_TIME` punctuator in `init`, say every 10 minutes, that collects keys whose stored timestamp is below stream time minus 24 hours and deletes them after closing the iterator. Stream time is right because of the reprocessing: it replays the month's timestamps in order, so expiry happens exactly as in the original run and duplicates within 24 hours of event time are still caught. A wall-clock punctuator comparing with the current time would expire every replayed entry immediately and let duplicates through. A `FixedKeyProcessor` can still schedule and delete in a punctuator; it only cannot forward from one. Stream time has its own cost: with no input it never fires, but then the store is not growing either.

</details>

6. ▢ Interleave lesson 6. You call `withCachingEnabled()` on the `StoreBuilder` of a Processor API store and forward a record for every input. Does the processor downstream now see fewer records, as it would after a DSL aggregation? What does the cache change?

<details markdown="1"><summary>Check</summary>

No. In the Processor API the record cache compacts only writes to the store, and therefore to its changelog; every `forward` call still reaches the children at once. Fewer downstream records would have to come from your own logic, such as forwarding from a punctuator only the latest value per key.

</details>

## Real-world reps

- [ ] Today: build the idle detector, run the predict-then-run in `TopologyTestDriver`, and write each prediction down before reading the output.
- [ ] Switch the punctuator to `WALL_CLOCK_TIME`, comparing against `context.currentSystemTimeMs()` instead of stream time, and rerun with the same timestamps. Write down what changed, and which version you would trust on a reprocessing run.
- [ ] Tomorrow: build the dedup processor with `processValues()`, print `describe()`, then swap in `process()` and print it again. Name the topic that appeared and explain why it did.

## Going further

- [State Stores](../reference/state-stores.md)
- [Docs: "Processor API", Apache Kafka 4.3](https://kafka.apache.org/43/streams/developer-guide/processor-api/)
- [Docs: "Streams DSL", Apache Kafka 4.3](https://kafka.apache.org/43/streams/developer-guide/dsl-api/), the section "Applying processors (Processor API integration)" and its four worked examples
- [Docs: "Testing a Streams Application", Apache Kafka 4.3](https://kafka.apache.org/43/streams/developer-guide/testing/), for driving punctuators in a test
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
