---
title: 10. Late Data, Grace Periods and Suppression
description: How long a window accepts out-of-order records, what happens to the ones after, and how to emit only a final result
type: lesson
---

# Lesson 10. Late Data, Grace Periods and Suppression

**Mission link:** This lesson closes stage 4 and the mission bullet it serves: pick a window and a grace period for a time-based question, and state which late records it drops and when it emits a result. Lesson 9 gave you the window; this one gives you the grace period, the drop rule and the emit rule, all measured in stream time.
**Primary source:** [Javadoc: "TimeWindows", Apache Kafka 4.3](https://kafka.apache.org/43/javadoc/org/apache/kafka/streams/kstream/TimeWindows.html)
**Prerequisites:** [Lesson 9](0009-windowed-aggregations.md), [Grace period](../GLOSSARY.md), [Late record](../GLOSSARY.md), [Suppression](../GLOSSARY.md), [Stream time](../GLOSSARY.md)

## Warm-up

1. ▢ A dashboard shows the error count over the last 5 minutes and refreshes every minute. Which window type, and with what size and advance?

<details markdown="1"><summary>Check</summary>

A hopping window, size 5 minutes, advance 1 minute: `TimeWindows.ofSizeWithNoGrace(Duration.ofMinutes(5)).advanceBy(Duration.ofMinutes(1))`, or `ofSizeAndGrace` with a grace period, which this lesson is about. Each record falls into five windows. A tumbling window would refresh only every 5 minutes.

</details>

2. ▢ Two tasks of the same app have stream times of 10:42 and 09:15 at the same wall-clock moment. Is something broken? Say what can cause it.

<details markdown="1"><summary>Check</summary>

Not necessarily. Stream time is tracked per task and advances only when that task processes a record with a newer timestamp. A task whose input partitions have received no recent records, or only old ones, stays behind however busy the other task is.

</details>

## Know this

### The grace period, and when a window closes

A window's end does not stop it accepting records. Its **[grace period](../GLOSSARY.md)** is how long after the end it still admits out-of-order ones, and both are read on stream time, never on the wall clock. `TimeWindows.ofSizeAndGrace(size, afterWindowEnd)` sets it, and "the window close, after which any incoming records are considered late and will be rejected, is defined as windowEnd + afterWindowEnd" ([TimeWindows](https://kafka.apache.org/43/javadoc/org/apache/kafka/streams/kstream/TimeWindows.html)). `ofSizeWithNoGrace` sets it to zero: any record that arrives after stream time has passed the window's end is dropped. `SlidingWindows` and `SessionWindows` have the same pair of constructors.

There is no default to fall back on. Until KIP-633 an unset grace meant 24 hours, which surprised users of `suppress` who then waited a day for results; the explicit constructors replaced it, so grace is always a choice you wrote down ([KIP-633](https://cwiki.apache.org/confluence/display/KAFKA/KIP-633%3A+Deprecate+24-hour+Default+Grace+Period+for+Windowed+Operations+in+Streams)).

The exact close test differs by window, because their ends differ. From the 4.3 javadoc and source:

| Window | Accepts a record while | Source |
|---|---|---|
| Tumbling and hopping (end exclusive) | window end > stream time − grace | [KStreamWindowAggregate](https://github.com/apache/kafka/blob/4.3/streams/src/main/java/org/apache/kafka/streams/kstream/internals/KStreamWindowAggregate.java) |
| Sliding (end inclusive) | stream time ≤ window end + grace | [SlidingWindows](https://kafka.apache.org/43/javadoc/org/apache/kafka/streams/kstream/SlidingWindows.html) |
| Session | session end, after merging the record in, + inactivity gap + grace ≥ stream time | [KStreamSessionWindowAggregate](https://github.com/apache/kafka/blob/4.3/streams/src/main/java/org/apache/kafka/streams/kstream/internals/KStreamSessionWindowAggregate.java) |

The session row has the extra gap because a session can still be extended by a record within the gap of its end, so it cannot be final before that time has passed too. The `SessionWindows` javadoc warns of the odd result an aggressive close gives: an out-of-order record rejected, then a later record moving the boundary anyway.

### What happens to a late record

A **[late record](../GLOSSARY.md)** belongs to a window that has already closed. It is not processed: the aggregation logs a warning, "Skipping record for expired window", with the record's topic, partition, offset and the stream time ([4.3 source](https://github.com/apache/kafka/blob/4.3/streams/src/main/java/org/apache/kafka/streams/kstream/internals/AbstractKStreamTimeWindowAggregateProcessor.java)), and counts it in the task metrics `dropped-records-total` and `dropped-records-rate`, which record at the info level and so are on by default ([Streams Monitoring: task metrics](https://kafka.apache.org/43/operations/monitoring/#task-metrics)). The same counter also counts records dropped for other reasons, such as a null key into an aggregation, so a rising value tells you to look, not what you will find.

An out-of-order record that is still within grace is not late. It updates its window, and the KTable emits a corrected result. That is why the glossary keeps "out-of-order record" and "late record" apart.

### Worked example: one window from open to closed

Tumbling windows of 10 s with 5 s of grace, `TimeWindows.ofSizeAndGrace(Duration.ofSeconds(10), Duration.ofSeconds(5))`, counting one key. Window `[10,20)` closes when stream time reaches 25. Records arrive in this order:

| Arrival | Timestamp | Stream time | Lands in | What happens | Update emitted without suppression |
|---|---|---|---|---|---|
| 1 | 12 | 12 | `[10,20)` | Counted | `[10,20)` = 1 |
| 2 | 16 | 16 | `[10,20)` | Counted | `[10,20)` = 2 |
| 3 | 23 | 23 | `[20,30)` | Counted; `[10,20)` still open, 23 < 25 | `[20,30)` = 1 |
| 4 | 14 | 23 | `[10,20)` | Out of order but within grace: counted | `[10,20)` = 3 |
| 5 | 27 | 27 | `[20,30)` | Counted; stream time passes 25, so `[10,20)` closes | `[20,30)` = 2 |
| 6 | 13 | 27 | `[10,20)` | Late: dropped, `dropped-records-total` + 1 | None |
| 7 | 31 | 31 | `[30,40)` | Counted; `[20,30)` closes only at 35 | `[30,40)` = 1 |

Records 4 and 6 are both out of order, by 9 and 14 seconds. Only the window's state at the moment each arrives decides their fate, not how late each is in isolation.

### Why a quiet partition holds windows open

Window `[20,30)` above closes when stream time reaches 35. If the partition then goes quiet, stream time stays at 31 indefinitely: it moves only when a record arrives ([Core Concepts](https://kafka.apache.org/43/streams/core-concepts/)). The window stays open, accepts any straggler stamped 20 to 29, and its final result is never declared.

This bites in three places. A low-traffic key range or partition can hold a window open for hours. A test that sends a handful of records and waits sees no final result, because nothing after the last record advances time. And since stream time is per task, one quiet partition delays only the windows of the task reading it, while the rest of the app looks healthy. Kafka Streams has no built-in way to advance stream time without records, so the usual remedies work around it: produce periodic records to every input partition so time keeps moving, or, in the Processor API, emit from a wall-clock punctuator (lesson 7) and accept that the result then depends on when the app ran.

### Suppression: one final result per window

A windowed KTable emits every update, as the last column of the worked example shows. For an alert or a sink that cannot take corrections, you want only the final value. **[Suppression](../GLOSSARY.md)** holds updates back ([Suppressed](https://kafka.apache.org/43/javadoc/org/apache/kafka/streams/kstream/Suppressed.html)):

```java
grouped.windowedBy(TimeWindows.ofSizeAndGrace(Duration.ofHours(1), Duration.ofMinutes(10)))
       .count()
       .suppress(Suppressed.untilWindowCloses(Suppressed.BufferConfig.unbounded()))
       .filter((windowedUser, count) -> count < 3)
       .toStream()
       .foreach((windowedUser, count) -> sendAlert(windowedUser, count));
```

This is the DSL guide's own example, shortened: the 09:00 to 10:00 window accepts records until stream time reaches 10:10, and only then does the filter receive exactly one count for it ([Streams DSL: Window Final Results](https://kafka.apache.org/43/streams/developer-guide/dsl-api/#window-final-results)). Without suppression the filter would see a count of 1, then 2, and alert on users who were about to reach 3.

The two modes:

| Mode | Emits | Buffer configs it accepts |
|---|---|---|
| `untilWindowCloses(StrictBufferConfig)` | One final result per key per window, when the window closes (end plus grace, in stream time) | Strict only, since emitting early would break the "final" promise |
| `untilTimeLimit(Duration, BufferConfig)` | The latest value for a key once the duration has passed since its first buffered update; a newer update replaces the buffered one without restarting the timer | Strict or eager |

`untilTimeLimit` works on any KTable, windowed or not, and is a rate limiter rather than a final-results guarantee. Its duration is measured in stream time too: KIP-328's worked examples evict a buffered record once stream time has moved past its timestamp plus the limit ([KIP-328](https://cwiki.apache.org/confluence/display/KAFKA/KIP-328%3A+Ability+to+suppress+updates+for+KTables)).

### When the buffer fills

Suppression keeps every pending result in an in-memory buffer, backed by its own changelog topic unless you call `withLoggingDisabled()`, which loses the buffer on a rebalance. You bound it with `BufferConfig.maxRecords(n)` or `maxBytes(n)` and then say what happens when the bound is hit ([Suppressed.BufferConfig](https://kafka.apache.org/43/javadoc/org/apache/kafka/streams/kstream/Suppressed.BufferConfig.html)):

| Buffer config | When full | Strict? |
|---|---|---|
| `unbounded()` | Never full; uses as much heap as the time bound demands, and an `OutOfMemoryError` may end the app ungracefully | Yes |
| `maxRecords(n).shutDownWhenFull()` | Shuts the application down gracefully; in the source, a `StreamsException` naming the buffer | Yes |
| `maxRecords(n).emitEarlyWhenFull()` | Emits the oldest records early, so a later update for the same window can follow | No: reduces duplicates, does not eliminate them |

So the choice is between correctness and availability, and it is yours to make: a strict buffer never emits a non-final result and stops the app instead, an eager one keeps running and may send a correction. `untilWindowCloses` accepts only the strict ones. Watch `suppression-buffer-size-*` and `suppression-buffer-count-*` to size the bound before it bites ([Streams Monitoring](https://kafka.apache.org/43/operations/monitoring/#streams-monitoring)); like other store metrics they are recorded at the debug level.

### `emitStrategy(EmitStrategy.onWindowClose())`

4.3 has a second way to get final results, for windowed aggregations only:

```java
grouped.windowedBy(TimeWindows.ofSizeAndGrace(Duration.ofHours(1), Duration.ofMinutes(10)))
       .emitStrategy(EmitStrategy.onWindowClose())
       .count();
```

The aggregation then emits a window's result only when the window closes, meaning stream time is past window end plus grace ([EmitStrategy](https://kafka.apache.org/43/javadoc/org/apache/kafka/streams/kstream/EmitStrategy.html)). It exists on the time-windowed stream, which covers tumbling, hopping and sliding windows, and on the session-windowed stream. KIP-825 added it because `suppress` keeps a second buffer and a second changelog for information the window store already holds ([KIP-825](https://cwiki.apache.org/confluence/display/KAFKA/KIP-825%3A+introduce+a+new+API+to+control+when+aggregated+results+are+produced)). Its own metrics are `emit-final-records-total` and `emit-final-latency-max` on the aggregation node.

Prefer it for final windowed results: no extra buffer, no extra changelog, no buffer-full policy to pick. Keep `suppress` for what it alone does: rate limiting with `untilTimeLimit`, and suppressing a KTable that did not come from a windowed aggregation.

### Grace is not retention

Two durations, two jobs. Grace decides how long a window **accepts** records. Retention, from lesson 9, decides how long the store **keeps** a window, so it can be queried; it must be at least size plus grace, and it defaults to exactly that. Raising retention to a week keeps closed windows readable for a week and does not reopen them: a record for a closed window is dropped whatever the retention. The glossary entry for grace period lists retention as the term to avoid for this reason.

### Predict, then run

The worked example as a test. Pipe the seven records for key `u1`, at `12_000L`, `16_000L`, `23_000L`, `14_000L`, `27_000L`, `13_000L` and `31_000L`, through:

```java
builder.stream("readings", Consumed.with(Serdes.String(), Serdes.String()))
       .groupByKey()
       .windowedBy(TimeWindows.ofSizeAndGrace(Duration.ofSeconds(10), Duration.ofSeconds(5)))
       .count()
       .suppress(Suppressed.untilWindowCloses(Suppressed.BufferConfig.unbounded()))
       .toStream((wk, count) -> wk.key() + "@" + wk.window().start() + "-" + wk.window().end())
       .to("final-counts", Produced.with(Serdes.String(), Serdes.Long()));
```

Before running it, write down every record `final-counts` receives, and after which input each appears. Then read `dropped-records-total` from `driver.metrics()` and check it against your prediction.

## Practice

1. ▢ Tumbling windows of 5 minutes with 2 minutes of grace. At what stream time does the window starting 10:00 close, and is a record stamped 10:03 accepted when stream time is 10:06:30?

<details markdown="1"><summary>Check</summary>

It closes at 10:07, window end 10:05 plus 2 minutes of grace. At 10:06:30 it is still open, so the record at 10:03 is accepted, 3 minutes 30 seconds out of order, and the window emits a corrected count.

</details>

2. ▢ A suppression uses `untilWindowCloses(BufferConfig.maxRecords(10_000).shutDownWhenFull())`, and a burst of new keys pushes the buffer past 10,000 records. What happens?

    - a) The oldest results are emitted early, and later updates may follow them
    - b) The application shuts down instead of emitting any result before its window closes
    - c) New records for the full buffer are dropped and counted as late records
    - d) The buffer spills to the changelog topic and keeps every pending result

<details markdown="1"><summary>Check</summary>

**b)** A strict buffer will not break the final-results promise, so it stops the app instead. (a) is what `emitEarlyWhenFull()` does, and `untilWindowCloses` does not accept it. (c) confuses a full buffer with a closed window; only a closed window drops records. (d) misreads the changelog, which makes the buffer durable across a rebalance but does not raise its bound.

</details>

3. ▢ Tumbling windows of 10 s with 3 s of grace. Records for one key arrive stamped 4, 9, 12, 8, 14, 7, 21, 19. Which records are dropped, and what is the final count of `[0,10)`?

<details markdown="1"><summary>Hint</summary>

Track stream time arrival by arrival. `[0,10)` closes when stream time reaches 13, and `[10,20)` when it reaches 23.

</details>

<details markdown="1"><summary>Check</summary>

Stream time runs 4, 9, 12, 12, 14, 14, 21, 21. The 8 arrives at stream time 12, before `[0,10)` closes at 13, so it is counted. The 7 arrives at stream time 14, after the close, so it is dropped. The 19 arrives at stream time 21, before `[10,20)` closes at 23, so it is counted. One drop, the 7, and `[0,10)` finishes at 3: the 4, the 9 and the 8.

</details>

4. ▢ In staging, an hourly count with `untilWindowCloses` and 5 minutes of grace has run all afternoon. A tester sent 200 records stamped between 13:00 and 13:40 to a one-partition topic at 13:45, then nothing. At 17:00, `final-counts` is empty. Diagnose it, and say what would make the 13:00 window emit.

<details markdown="1"><summary>Hint</summary>

Ask what the task's stream time is at 17:00, and which clock the window close is measured on.

</details>

<details markdown="1"><summary>Check</summary>

Stream time is 13:40, the largest timestamp seen, and it has not moved since 13:45 because no record has arrived. The 13:00 window closes at stream time 14:05, so it is still open and suppression is still holding it. Nothing is broken. A record stamped 14:05 or later on that partition would close it, which is why a test must advance stream time past window end plus grace, and why a quiet production partition needs periodic records if its windows must close on time.

</details>

5. ▢ Each sensor reports a reading every 10 seconds but buffers up to 2 minutes of readings when offline and then sends them. Operations wants one alert per sensor per hour if the hourly reading count is below 300. Write the windowing, say what it drops, and say when each alert can fire.

<details markdown="1"><summary>Hint</summary>

Size the grace from how far behind stream time a reading can arrive, then pick a final-results mechanism.

</details>

<details markdown="1"><summary>Check</summary>

`groupByKey().windowedBy(TimeWindows.ofSizeAndGrace(Duration.ofHours(1), Duration.ofMinutes(2))).emitStrategy(EmitStrategy.onWindowClose()).count()`, then a filter on `count < 300` (or `count()` then `suppress(untilWindowCloses(...))`). It drops readings that arrive after stream time has passed their window's end plus 2 minutes, which a sensor offline longer than 2 minutes across an hour boundary will produce. Each alert fires once, when stream time on that sensor's task reaches the hour's end plus 2 minutes; a task whose sensors all go quiet will not fire until a reading arrives. Since each task's stream time comes from all the sensors on its partitions, one sensor that sends far-future timestamps can close windows early for its partition-mates, which is worth an extractor that rejects them.

</details>

6. ▢ Interleave lesson 6: a colleague says the record cache already reduces a windowed count to one update per window, so `suppress` is redundant. What is right and wrong about that?

<details markdown="1"><summary>Check</summary>

Right that the cache collapses consecutive updates to the same key, so far fewer intermediate counts reach the output. Wrong that it gives one per window: it flushes on every commit and when it fills, whether or not the window has closed, so a window spanning several commit intervals still emits several updates. Only `suppress(untilWindowCloses(...))` or `emitStrategy(onWindowClose())` ties emission to the window closing.

</details>

## Real-world reps

- [ ] Today: run the predict-then-run test with your predicted output and drop count written first. Then remove the `suppress` line and predict the six updates it emits instead.
- [ ] Find a windowed aggregation in a codebase you can read, or write one, and state for it in one sentence each: the grace period, which records it drops, and when it emits. If it uses neither `suppress` nor `emitStrategy`, say what its consumers must do with updates.
- [ ] Tomorrow: from memory, write the three buffer configs, what each does when full, and which `untilWindowCloses` accepts. Check against this lesson.

## Going further

- [Time and Windows](../reference/time-and-windows.md)
- [Docs: "Streams DSL", Window Final Results, Apache Kafka 4.3](https://kafka.apache.org/43/streams/developer-guide/dsl-api/#window-final-results)
- [Javadoc: "Suppressed", Apache Kafka 4.3](https://kafka.apache.org/43/javadoc/org/apache/kafka/streams/kstream/Suppressed.html)
- [KIP: "KIP-328: Ability to suppress updates for KTables", Apache Kafka](https://cwiki.apache.org/confluence/display/KAFKA/KIP-328%3A+Ability+to+suppress+updates+for+KTables)
- [KIP: "KIP-633: Deprecate 24-hour Default Grace Period for Windowed Operations in Streams", Apache Kafka](https://cwiki.apache.org/confluence/display/KAFKA/KIP-633%3A+Deprecate+24-hour+Default+Grace+Period+for+Windowed+Operations+in+Streams)
- [Article: "Streaming 102: The world beyond batch", Tyler Akidau, O'Reilly (2016)](https://www.oreilly.com/radar/the-world-beyond-batch-streaming-102/), for watermarks and allowed lateness, the general form of what grace periods do
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
