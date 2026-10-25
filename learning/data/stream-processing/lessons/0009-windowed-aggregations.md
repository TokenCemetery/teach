---
title: 9. Windowed Aggregations
description: How tumbling, hopping, sliding and session windows group records by time, and which question each one answers
type: lesson
---

# Lesson 9. Windowed Aggregations

**Mission link:** The mission asks you to pick a window and a grace period for a time-based question. This lesson is the first half of that: the four window types Kafka Streams offers, what each one groups together, and how to tell from the question which one it is asking for. Lesson 10 adds the grace period.
**Primary source:** [Docs: "Streams DSL", Apache Kafka 4.3](https://kafka.apache.org/43/streams/developer-guide/dsl-api/) (the Windowing section)
**Prerequisites:** [Lesson 8](0008-event-time-processing-time-and-stream-time.md), [Tumbling window](../GLOSSARY.md), [Hopping window](../GLOSSARY.md), [Sliding window](../GLOSSARY.md), [Session window](../GLOSSARY.md)

## Warm-up

1. ▢ One task reads a record stamped 10:00:09 and then one stamped 10:00:04. What is the task's stream time after the second record, and is the second record dropped?

<details markdown="1"><summary>Check</summary>

10:00:09. Stream time is the maximum timestamp seen so far and never moves backward. The second record is out of order but not dropped: stream time alone drops nothing. Only a window that has already closed drops a record, which is lesson 10.

</details>

2. ▢ A stream keyed by `orderId` is regrouped with `groupBy((k, v) -> v.customerId())` before a `count()`. What does the topology gain that `groupByKey()` would not create, and why?

<details markdown="1"><summary>Check</summary>

A repartition topic. The new key, `customerId`, may live on any partition, so Streams writes every record back to Kafka keyed by customer and reads it again, which puts each customer's records in one task before they are counted. `groupByKey()` keeps the existing key and partitioning, so it needs none.

</details>

## Know this

### A windowed aggregation is a grouped aggregation with a time key

Windowing sub-groups each key's records by time, and windows are tracked per key ([Streams DSL: Windowing](https://kafka.apache.org/43/streams/developer-guide/dsl-api/#windowing)). In code it is one call between grouping and aggregating:

```java
KTable<Windowed<String>, Long> clicksPerWindow = clicks
        .groupByKey()
        .windowedBy(TimeWindows.ofSizeWithNoGrace(Duration.ofMinutes(5)))
        .count();
```

`count()`, `reduce()` and `aggregate()` all work after `windowedBy`. Grouping rules from lesson 4 still apply, so a `groupBy` to a new key still writes a repartition topic first. The result is a KTable that, as lesson 6 showed, emits an update every time a window's value changes, not one final answer per window. Getting one final answer is lesson 10.

Every window boundary is an event-time boundary, measured on the timestamps your extractor returned in lesson 8. Times in the DSL are milliseconds; the examples below use seconds to stay readable.

### Tumbling windows: one bucket per record

A **[tumbling window](../GLOSSARY.md)** is fixed-size, gap-less and non-overlapping, so every record falls into exactly one. `TimeWindows.ofSizeWithNoGrace(size)` and `TimeWindows.ofSizeAndGrace(size, grace)` both define one. Boundaries are aligned to the epoch: the N-th window covers `[N * size, N * size + size)`, start inclusive and end exclusive, so 5-minute windows always start on :00, :05, :10, never at the first record ([TimeWindows](https://kafka.apache.org/43/javadoc/org/apache/kafka/streams/kstream/TimeWindows.html)).

### Hopping windows: fixed size, overlapping

A **[hopping window](../GLOSSARY.md)** adds an advance smaller than the size: `TimeWindows.ofSizeWithNoGrace(Duration.ofMinutes(5)).advanceBy(Duration.ofMinutes(1))` starts a new 5-minute window every minute. Windows overlap, so a record falls into several, `size / advance` of them when the advance divides the size. They are epoch-aligned too: size 5000 ms with advance 3000 ms gives `[0;5000), [3000;8000), ...` ([Streams DSL: Hopping time windows](https://kafka.apache.org/43/streams/developer-guide/dsl-api/#hopping-time-windows)). A tumbling window is the hopping window whose advance equals its size.

Other tools call this a "sliding window". Kafka Streams does not, and the DSL guide warns about exactly that confusion.

### Sliding windows: one window per distinct set of records

A **[sliding window](../GLOSSARY.md)** is defined by the largest time difference two records in it may have: `SlidingWindows.ofTimeDifferenceWithNoGrace(Duration.ofSeconds(5))`. Its windows are not aligned to the epoch but to record timestamps, and both ends are inclusive. A new window is created when a record enters the sliding window and when one drops out, and each distinct combination of records appears in exactly one window ([SlidingWindows](https://kafka.apache.org/43/javadoc/org/apache/kafka/streams/kstream/SlidingWindows.html)). KIP-450 added it because a hopping window with a tiny advance, the old way to approximate this, produced huge numbers of redundant overlapping windows ([KIP-450](https://cwiki.apache.org/confluence/display/KAFKA/KIP-450%3A+Sliding+Window+Aggregations+in+the+DSL)).

### Session windows: as long as the activity lasts

A **[session window](../GLOSSARY.md)** has no fixed size. `SessionWindows.ofInactivityGapWithNoGrace(Duration.ofMinutes(5))` groups a key's records until five minutes pass with none, so each key's sessions have their own start, end and length. A record that falls within the gap of an existing session joins it, and one that bridges two sessions merges them ([SessionWindows](https://kafka.apache.org/43/javadoc/org/apache/kafka/streams/kstream/SessionWindows.html)). That is why `aggregate()` on a session-windowed stream takes a third argument, a `Merger`, that combines two sessions' aggregates; `count()` and `reduce()` know how to merge already.

A merge is visible downstream. In the 4.3 source, the aggregation removes each session it absorbed and forwards a tombstone for it, then forwards the merged session under its new window ([KStreamSessionWindowAggregate](https://github.com/apache/kafka/blob/4.3/streams/src/main/java/org/apache/kafka/streams/kstream/internals/KStreamSessionWindowAggregate.java)). A consumer that ignores tombstones keeps counting the old sessions.

### Worked example: four records, four window types

One key, records at 12, 16, 19 and 27 seconds, arriving in that order:

| Window | Definition | Windows and counts |
|---|---|---|
| Tumbling | Size 10 s | `[10,20)`: 3; `[20,30)`: 1 |
| Hopping | Size 10 s, advance 5 s | `[5,15)`: 1; `[10,20)`: 3; `[15,25)`: 2; `[20,30)`: 1; `[25,35)`: 1 |
| Sliding | Time difference 5 s | `[7,12]`: 1; `[11,16]`: 2; `[14,19]`: 2; `[22,27]`: 1; plus `[12.001,17.001]`: 1 and `[16.001,21.001]`: 1, created as 12 and 16 drop out |
| Session | Gap 5 s | `[12,19]`: 3; `[27,27]`: 1 |

The hopping row is the tumbling row plus the windows offset by half a size: each record is in two windows, because 10 / 5 = 2. The sliding row has a window ending at each record, holding everything within 5 s before it, and a window starting just after each record drops out, when what is left is a new combination. The record at 19 drops out too, but nothing is left after it before 27, so no window is created. The session row splits at the 8-second silence between 19 and 27.

Now a record stamped 23 arrives late. It is 4 s after 19 and 4 s before 27, so it bridges both sessions: the session row becomes one session `[12,27]` holding 5 records, and downstream sees tombstones for `[12,19]` and `[27,27]` before the new result.

![Four records at 12, 16, 19 and 27 seconds on a time axis. Tumbling windows of 10 seconds: 10 to 20 holds 3, 20 to 30 holds 1. Hopping windows of 10 advancing by 5: 5 to 15 holds 1, 10 to 20 holds 3, 15 to 25 holds 2, 20 to 30 holds 1, 25 to 35 holds 1. Sliding windows with a 5 second difference: six windows holding 1, 2, 1, 2, 1 and 1. Session windows with a 5 second gap: 12 to 19 holds 3 and 27 holds 1, merging into 12 to 27 holding 5 once a late record at 23 arrives.](images/four-window-types-on-a-timeline.svg)

### Which question each window answers

| Window | The question it answers | Example |
|---|---|---|
| Tumbling | How many, or how much, in each fixed period? | Orders per hour for a report; each order counted once |
| Hopping | What is the total over the last N, refreshed every M? | Error rate over the last 5 minutes, published every minute |
| Sliding | Did any span of length N contain this pattern? | Three failed logins within 60 seconds of each other, wherever they fall |
| Session | How long was each burst of activity, and what was in it? | Pages per visit, where a visit ends after 30 idle minutes |

The tell in the question: a calendar period is tumbling; "the last N, every M" is hopping; "within N of each other" is sliding, since tumbling or hopping windows can split a burst across a boundary; "until they stop" is session.

### The key is now `Windowed<K>`

A windowed aggregation returns `KTable<Windowed<K>, V>`, because the same key has a different value in each window. `Windowed#key()` returns the original key and `Windowed#window()` the window, with `start()` and `end()` in milliseconds ([Windowed](https://kafka.apache.org/43/javadoc/org/apache/kafka/streams/kstream/Windowed.html)). To write the result to a topic, either map the key to something plain with `toStream((wk, v) -> ...)`, or give the sink a serde from `WindowedSerdes.timeWindowedSerdeFrom(String.class, windowSizeMs)` or `sessionWindowedSerdeFrom(String.class)` ([WindowedSerdes](https://kafka.apache.org/43/javadoc/org/apache/kafka/streams/kstream/WindowedSerdes.html)). Consumers of that topic then need the same serde.

### Window stores and retention

The aggregation keeps each window's current value in a window store, or a session store for sessions, backed by a changelog topic like any store from lesson 5. Old windows are purged after the store's retention period, set with `Materialized#withRetention`.

The default is a place where the documentation disagrees with itself. The DSL guide says the default retention is one day. The `Materialized` javadoc says that when unset it is the window size plus the grace period, and that it "must be at least long enough to contain the windowed data's entire life cycle, from window-start through window-end, and for the entire grace period" ([Materialized#withRetention](https://kafka.apache.org/43/javadoc/org/apache/kafka/streams/kstream/Materialized.html)). The 4.3 source settles it for the javadoc: it uses size plus grace when no retention is given, and throws `IllegalArgumentException` when a retention shorter than size plus grace is ([WindowStoreMaterializer](https://github.com/apache/kafka/blob/4.3/streams/src/main/java/org/apache/kafka/streams/kstream/internals/WindowStoreMaterializer.java)). Set a longer retention when you want closed windows to stay queryable, through the interactive queries of stage 7, after they stop accepting records.

### Predict, then run

Hopping counts of 10 seconds advancing by 5, keys flattened to text so the output is readable:

```java
StreamsBuilder builder = new StreamsBuilder();
builder.stream("clicks", Consumed.with(Serdes.String(), Serdes.String()))
       .groupByKey()
       .windowedBy(TimeWindows.ofSizeWithNoGrace(Duration.ofSeconds(10))
                              .advanceBy(Duration.ofSeconds(5)))
       .count()
       .toStream((wk, count) -> wk.key() + "@" + wk.window().start() + "-" + wk.window().end())
       .to("click-counts", Produced.with(Serdes.String(), Serdes.Long()));
```

In a `TopologyTestDriver` test, pipe four records for key `u1` at `12_000L`, `16_000L`, `19_000L` and `27_000L` and print `readKeyValuesToList()` from `click-counts`. The driver processes each record synchronously, so the record cache collapses nothing ([TopologyTestDriver](https://kafka.apache.org/43/javadoc/org/apache/kafka/streams/TopologyTestDriver.html)). Write down every output record, key and count, before running it.

## Practice

1. ▢ Tumbling windows of 1 hour. A record is stamped 14:59:59.999 and the next 15:00:00.000. Which windows do they fall in, and why can't a tumbling window start at 14:30?

<details markdown="1"><summary>Check</summary>

`[14:00, 15:00)` and `[15:00, 16:00)`. The end is exclusive, so the first instant of 15:00 belongs to the next window. Windows are aligned to the epoch, starting at multiples of the size from timestamp zero, so 1-hour windows start on the hour; a window starting at 14:30 would need an advance, which makes it hopping.

</details>

2. ▢ A fraud rule fires when one card makes three purchases within 60 seconds of each other. Which window fits?

    - a) Tumbling windows of 60 seconds, counting purchases per card
    - b) Hopping windows of 60 seconds advancing every 30 seconds
    - c) Sliding windows with a time difference of 60 seconds
    - d) Session windows with an inactivity gap of 60 seconds

<details markdown="1"><summary>Check</summary>

**c)** A sliding window exists for every distinct set of purchases within 60 seconds of each other, wherever they fall. (a) misses three purchases at :50, :55 and 1:05, split across a boundary. (b) narrows the gap but still misses spans that straddle the hop, and creates two windows per purchase. (d) asks something else: a session keeps growing while purchases are under 60 seconds apart, so ten purchases spread over ten minutes form one session without any three falling within 60 seconds.

</details>

3. ▢ Write the output of the predict-then-run topology: every record, with key and count, in order.

<details markdown="1"><summary>Hint</summary>

Each record lands in two windows, and the driver emits one update per window per record. Start from the hopping row of the worked example, then ask which windows each record touches.

</details>

<details markdown="1"><summary>Check</summary>

```text
u1@5000-15000   1
u1@10000-20000  1
u1@10000-20000  2
u1@15000-25000  1
u1@10000-20000  3
u1@15000-25000  2
u1@20000-30000  1
u1@25000-35000  1
```

Eight updates for four records, two per record, earlier window first. `[10000,20000)` is emitted three times with a rising count: the KTable emits updates, not final results. On a real broker the record cache could collapse some of them.

</details>

4. ▢ Session windows, gap 10 minutes, one user. Records arrive stamped 09:00, 09:05, 09:30, 09:38, then a late one stamped 09:21. List the sessions after the first four records, then what downstream receives when the fifth arrives.

<details markdown="1"><summary>Hint</summary>

For the fifth record, measure its distance to the nearest record on each side and compare both with the gap.

</details>

<details markdown="1"><summary>Check</summary>

After four records: `[09:00, 09:05]` with 2 and `[09:30, 09:38]` with 2. The record at 09:21 is 16 minutes after 09:05, more than the gap, and 9 minutes before 09:30, less than the gap. So it joins only the second session: downstream receives a tombstone for `[09:30, 09:38]` and a new result for `[09:21, 09:38]` with 3. The first session is untouched. No single record could have bridged both here: it would have to be within 10 minutes of 09:05 and of 09:30, which are 25 minutes apart.

</details>

5. ▢ This fails at startup with `IllegalArgumentException`. Explain why, and give two fixes.

    ```java
    grouped.windowedBy(TimeWindows.ofSizeAndGrace(Duration.ofHours(1), Duration.ofMinutes(10)))
           .count(Materialized.<String, Long, WindowStore<Bytes, byte[]>>as("hourly-counts")
                   .withRetention(Duration.ofMinutes(30)));
    ```

<details markdown="1"><summary>Hint</summary>

Compare the retention with the whole time a window must be kept to accept every record it can still take.

</details>

<details markdown="1"><summary>Check</summary>

Retention must be at least the window size plus the grace period, here 1 hour 10 minutes, and 30 minutes is shorter: the store would purge a window while it can still accept records. Fix it by setting retention to 70 minutes or more, for example `Duration.ofHours(2)` to keep closed windows queryable for longer, or by removing `withRetention` so it defaults to size plus grace.

</details>

6. ▢ Interleave lesson 5: the `hourly-counts` store above is backed by a changelog topic. Name the topic, and say what restoring it on another instance rebuilds.

<details markdown="1"><summary>Check</summary>

`<application.id>-hourly-counts-changelog`. Replaying it rebuilds the window store: the current count of every window still within retention, for every key of the task that moved. Windows older than retention are gone from the store and are not brought back.

</details>

## Real-world reps

- [ ] Today: run the predict-then-run test with your eight predicted lines written down first. Then change it to tumbling windows and predict again.
- [ ] Take three time-based questions from your own work, such as a dashboard, an alert or a report, and name the window each needs, using the "which question" table.
- [ ] Tomorrow: draw the worked example's timeline from memory for a 6-second sliding window instead of 5, then check each window against the rule that every distinct combination of records appears once.

## Going further

- [Time and Windows](../reference/time-and-windows.md)
- [Docs: "Streams DSL", Windowing, Apache Kafka 4.3](https://kafka.apache.org/43/streams/developer-guide/dsl-api/#windowing)
- [Javadoc: "TimeWindows", Apache Kafka 4.3](https://kafka.apache.org/43/javadoc/org/apache/kafka/streams/kstream/TimeWindows.html)
- [KIP: "KIP-450: Sliding Window Aggregations in the DSL", Apache Kafka](https://cwiki.apache.org/confluence/display/KAFKA/KIP-450%3A+Sliding+Window+Aggregations+in+the+DSL)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
