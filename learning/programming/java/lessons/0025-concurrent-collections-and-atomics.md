---
title: 25. Concurrent Collections and Atomics
description: The collections that survive concurrent access, and the check-then-act that defeats every one of them
type: lesson
---

# Lesson 25. Concurrent Collections and Atomics

**Mission link:** A concurrent collection turns "thread-safe" from a hope into a documented contract, and every contract in this lesson refuses to promise that two of its own safe calls stay safe once you chain them, which is exactly the gap a reviewer expects you to have already closed.
**Primary source:** [`ConcurrentHashMap`, Java SE 25 API](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/concurrent/ConcurrentHashMap.html)
**Prerequisites:** [Lesson 23](0023-the-memory-model.md), [Lesson 5](0005-arrays-and-collections.md)

## Warm-up

1. ▢ What is the lock-ordering rule that prevents a deadlock before it happens, and why does reversing the acquisition order in just one of the two threads make the deadlock stop occurring?

<details markdown="1"><summary>Check</summary>

Every thread that needs to hold more than one lock at once acquires them in the same fixed order across the whole program. If thread A always takes lock X before lock Y, and thread B does too, neither thread can end up holding one lock while waiting for the other, so the circular wait that defines a deadlock never forms. Reversing the order in one thread breaks the deadlock because it removes that circular wait, not because either lock changed.

</details>

2. ▢ What is the difference between `List.of(1, 2, 3)` and `new ArrayList<>(List.of(1, 2, 3))`, in terms of what you can do to the result?

<details markdown="1"><summary>Check</summary>

`List.of(...)` returns a fixed-size, unmodifiable list: calling `add`, `remove` or `set` on it throws `UnsupportedOperationException`. Wrapping it in `new ArrayList<>(...)` copies the elements into a genuinely mutable list, so the copy can be grown and shrunk freely while the original `List.of(...)` list stays fixed.

</details>

## Know this

### A plain `HashMap` under concurrent writes

```java
Map<Integer, Integer> map = new HashMap<>();
// 8 threads, each putting 2000 distinct keys of its own
```

Running eight threads against one shared `HashMap`, each inserting 2000 keys nobody else touches, so there is no logical conflict about which value a key should hold, still loses entries. Across four separate runs of that exact program the discrepancy showed up on the first attempt every single time: expected sizes of 16000 came back as 15031, 9512, 12600 and 9807, with no exception thrown in any of the four. The number lost varies from run to run because it depends on exactly how the internal resize and bucket-chaining operations from different threads interleave, but the shape of the failure does not: `size()` reports a number smaller than the number of `put` calls, and nothing anywhere raises a flag. This is what "not thread-safe" means for `HashMap` in practice, and it is why the fix is never "add a `synchronized` here", but a collection built for the job.

### `ConcurrentHashMap`: what an operation guarantees, and where the guarantee stops

`ConcurrentHashMap` makes each individual operation atomic and visible: a `put`, a `get`, a `remove`, a `size` never corrupts internal state and never needs an external lock. What it does not do is make two calls atomic together. Getting a value and then deciding to put one, when nothing else could have changed the entry in between, is exactly the assumption a second thread breaks:

```java
Widget w = map.get("key");
if (w == null) {
    w = new Widget(id++);
    map.put("key", w);      // race: two threads can both see null from get
}
```

Running sixteen threads through that pattern against one key produced between two and four `Widget` instances across three runs, all overwriting each other into the same one surviving entry. Replacing it with `computeIfAbsent`, which the map itself makes atomic, produced exactly one `Widget` on every run:

```java
map.computeIfAbsent("key", k -> new Widget(id++));
```

`putIfAbsent` and `merge` exist for the same reason: each names a get-then-write pattern common enough to deserve its own atomic method, so the caller never has to hold anything for the gap between the read and the write. Reach for one of them instead of a hand-written check-then-act, on `ConcurrentHashMap` or on any concurrent collection that offers one.

### A `computeIfAbsent` mapping function must leave the map alone

The API documentation for `computeIfAbsent` says plainly that the mapping function must not attempt to update any other mapping of the map, and that some update operations by other threads may block while it runs, so a function that tries to update the same map is not just bad style, it is forbidden. Calling `computeIfAbsent` on the same key from inside its own mapping function reproduces the consequence directly:

```java
map.computeIfAbsent(1, k -> map.computeIfAbsent(1, j -> j * 2));
```

That throws `java.lang.IllegalStateException: Recursive update` every time it was run. A mapping function that touches a *different* key can appear to work, since it does not always land on the same internal bin, but relying on that is relying on an implementation detail the class explicitly reserves the right to change; the rule is "must not attempt to update any other mappings of this map", not "usually gets away with it".

### Iteration and size: weakly consistent, not a snapshot

`ConcurrentHashMap`'s iterator is weakly consistent: it will not throw while the map is being modified, and it does not promise to show every change, every original element, or any particular ordering, only that it will not corrupt itself and will not throw. Iterating a `ConcurrentHashMap` that starts at 1000 entries while another thread concurrently pushes it to 200000 entries never threw across three runs, and the count the iterator actually saw, 1536 or 2048 depending on the run, landed nowhere near either the starting size or the final one. A plain `HashMap` put through the identical stress, iterated while another thread mutates it, threw `java.util.ConcurrentModificationException` on every one of the same three runs. That contrast is the guarantee stated concretely: `ConcurrentHashMap` trades a snapshot for never throwing, and a plain `HashMap` throws instead of ever risking a silent bad answer during that specific operation, though as the first section showed, only during iteration; concurrent `put` calls corrupt it with no exception at all.

### `CopyOnWriteArrayList`: the one workload it actually fits

Every mutating call, `add`, `remove`, `set`, on a `CopyOnWriteArrayList` copies the entire backing array and swaps it in, which is why an iterator taken from it is a genuine, unmoving snapshot rather than a weakly consistent view. Starting a `CopyOnWriteArrayList` at five elements and mutating it mid-iteration (adding one element and removing another) confirmed the difference directly: the iterator visited exactly the five elements present when it started, no more and no fewer, while the list itself ended up different, `[1, 2, 3, 4, 100]`, from what the iterator saw. That copy-per-write cost is the entire trade-off: it is a bad choice for anything with frequent writes, since every one of them is an O(n) copy, and a good one for something read constantly and written rarely, a listener list or a configuration snapshot being the standard cases, where the readers vastly outnumber the writers and never want to block or retry.

### `BlockingQueue`: handing work between threads without a lock you wrote

A `BlockingQueue` is how one thread hands work to another with no lock either side has to manage: `put` blocks the producer while the queue is full, `take` blocks the consumer while it is empty. `ArrayBlockingQueue` is bounded at construction and enforces that bound with real blocking; `LinkedBlockingQueue` defaults to a capacity of `Integer.MAX_VALUE` when no bound is given, which is unbounded in every practical sense. Filling an `ArrayBlockingQueue` of capacity 2 from a producer thread that keeps calling `put` showed the block directly: the third `put` returned only after roughly 1002 milliseconds, which was exactly how long a separate thread slept before it started draining the queue with `take`; the first two `put` calls, into the still-empty slots, returned in under a millisecond. The same loop against an unbounded `LinkedBlockingQueue`, with no consumer at all, pushed 500000 elements straight through with no blocking, finishing in 43 milliseconds on one machine, one run; that number is not a claim about throughput in general, only evidence that nothing there was waiting on anything. That is exactly the risk an unbounded queue trades for never blocking a producer: it turns backpressure into unmonitored memory growth instead, which is why a bounded queue, one that will actually make a producer wait, is the safer default, and the case for `LinkedBlockingQueue`'s unbounded form has to be argued for specifically rather than assumed.

### The atomics: `compareAndSet` and the update family

`AtomicInteger`, `AtomicLong` and `AtomicReference` wrap a single value and expose operations that read, modify and write it as one step no other thread can split. `compareAndSet(expected, new)` writes `new` only if the current value still equals `expected`, and reports whether it won:

```java
AtomicInteger counter = new AtomicInteger(5);
counter.compareAndSet(5, 10);   // true, value now 10
counter.compareAndSet(5, 20);   // false, current value is 10, not 5; value stays 10
counter.updateAndGet(v -> v * 2); // 20
```

Running that produced `firstTry=true secondTry=false value=10`, then `updateAndGet result=20`, exactly as the compare-and-set rule predicts. `incrementAndGet`, `getAndAdd` and `updateAndGet` are all built on a retry loop around `compareAndSet`: read the value, compute the new one, try to write it, and if another thread got there first, read again and recompute rather than overwriting a value that has already moved on. Plain `int++` has no such loop, which is why it loses updates under contention: eight threads each incrementing a shared plain `int` and an `AtomicInteger` 100000 times apiece landed the plain `int` at 404961 against an expected 800000, in one run, while the `AtomicInteger` landed on exactly 800000. The plain field is not merely "sometimes off"; it lost roughly half of its increments, because `count++` is itself a read, an add and a write with no atomicity between the three, the same shape of bug as the check-then-act above, just one instruction shorter.

### `LongAdder` versus `AtomicLong` under contention

`LongAdder` gives up an exact running total on every write in exchange for far less contention: it keeps a set of internal cells that different threads update independently when they collide, and only combines them into one number when `sum()` is called. Running sixteen threads, each incrementing a shared counter 5,000,000 times, against a plain `AtomicLong` and against a `LongAdder` gave, in one run on one machine: `AtomicLong` took 2137 milliseconds, `LongAdder` took 206 milliseconds, both reaching the correct total of 80000000. A second run gave 2345 milliseconds against 136 milliseconds. The absolute numbers moved between runs; the ratio did not move nearly as much, landing at roughly ten to seventeen times faster for `LongAdder` in this workload on this one machine. Treat that ratio, not the millisecond figures, as the transferable fact: under heavy contention on a simple counter, `LongAdder` wins by close to an order of magnitude, because threads stop fighting over one cache line, at the cost of `sum()` being a value that was never exact at any single instant while writes were still landing, and at the cost of `LongAdder` offering no `compareAndSet`. A counter that only needs a total, read occasionally, wants `LongAdder`; a value that other code needs to read exactly right now, or update conditionally, wants `AtomicLong`.

### `ConcurrentModificationException` is a fail-fast courtesy, not a safety guarantee

The exception a plain `HashMap` or `ArrayList` throws when it detects a structural change during iteration exists to surface a bug quickly and readably, not to make the collection safe. It is best-effort: the API documentation makes no promise it fires on every concurrent modification, only that when it does fire it is because the collection noticed its own bookkeeping had changed underneath it. `ConcurrentHashMap`'s weakly consistent iterator never throws that exception for exactly this reason, and that absence of an exception is not evidence of safety by itself, it is evidence that this particular class chose "keep going with a possibly stale view" over "detect and complain", which is a different design decision, not a stronger guarantee.

### A thread-safe part does not make a thread-safe whole

Every collection in this lesson is [thread-safe](../GLOSSARY.md) on its own terms, and the check-then-act sections above are the proof that assembling several thread-safe calls does not automatically produce a thread-safe sequence of them. A `ConcurrentHashMap` guarantees that `get` alone is safe and that `put` alone is safe; it says nothing about the gap between calling one and calling the other, and that gap is where every bug in this lesson actually lived. The practical rule is to ask, for any sequence of two or more operations on a shared collection, whether the collection itself has a single atomic method that already names that sequence, `computeIfAbsent`, `putIfAbsent`, `merge`, `compareAndSet`, before writing the two calls separately and hoping nothing lands between them.

## Practice

1. ▢ Predict the output.

   ```java
   List<Integer> list = new CopyOnWriteArrayList<>();
   for (int i = 0; i < 5; i++) list.add(i);
   int seen = 0;
   for (Integer v : list) {
       seen++;
       if (v == 2) {
           list.add(100);
           list.remove(0);
       }
   }
   System.out.println(seen);
   System.out.println(list);
   ```

<details markdown="1"><summary>Check</summary>

`5`, then `[1, 2, 3, 4, 100]`. The iterator was taken over a snapshot of the backing array at the moment iteration started, so it visits exactly the five elements that were there, no matter what the list underneath does during the loop. The list itself ends up different from what the loop saw, which is the whole point of copy-on-write: readers and writers never fight over the same array.

</details>

2. ▢ This class compiles, runs, and is built on `ConcurrentHashMap`, yet a load test shows the cache occasionally builds the same expensive `Connection` twice for one key. Find the bug.

   ```java
   private final ConcurrentHashMap<String, Connection> cache = new ConcurrentHashMap<>();

   Connection get(String key) {
       Connection c = cache.get(key);
       if (c == null) {
           c = openConnection(key);   // expensive
           cache.put(key, c);
       }
       return c;
   }
   ```

<details markdown="1"><summary>Hint</summary>

`ConcurrentHashMap` makes `get` and `put` each atomic on their own. What does it guarantee about the two of them run back to back by two different threads?

</details>

<details markdown="1"><summary>Check</summary>

Nothing stops two threads from both calling `get` and both seeing `null` before either has called `put`, so both go on to open a connection and both write one, with the second write winning silently. `ConcurrentHashMap` never promised the pair was atomic, only that each call was. The fix is `cache.computeIfAbsent(key, this::openConnection)`, which the map performs as a single atomic step per key.

</details>

3. ▢ Predict what this throws, and name the exact exception.

   ```java
   ConcurrentHashMap<Integer, Integer> map = new ConcurrentHashMap<>();
   map.computeIfAbsent(1, k -> map.computeIfAbsent(1, j -> j * 2));
   ```

<details markdown="1"><summary>Check</summary>

`java.lang.IllegalStateException: Recursive update`. The outer call has not finished updating the mapping for key `1` when the mapping function tries to call `computeIfAbsent` on that same key again, which is exactly the "must not attempt to update any other mapping" restriction the API documentation states; the map detects that reentry and refuses it rather than deadlocking or silently corrupting itself.

</details>

4. ▢ A single producer thread parses files faster than three consumer threads can process the parsed records, and an unbounded `LinkedBlockingQueue` between them is why memory keeps climbing during a long run. Would `ArrayBlockingQueue` fix it, and what would change about the producer's behaviour if it did?

<details markdown="1"><summary>Check</summary>

Yes: a bounded `ArrayBlockingQueue` caps the number of unconsumed records in memory at the chosen capacity, because `put` blocks once the queue is full. What changes is that the producer now spends time waiting on `put` whenever consumers fall behind, instead of racing ahead and piling records up; that waiting is backpressure made visible, trading unbounded memory growth for the producer occasionally being slower, which is the trade a bounded queue is for.

</details>

5. ▢ Given that `LongAdder` measured roughly ten to seventeen times faster than `AtomicLong` under heavy contention in one run on one machine, name a situation where you would still choose `AtomicLong` for a hot counter.

<details markdown="1"><summary>Check</summary>

Any situation that needs an exact value right now rather than an eventual total, or needs `compareAndSet`: a counter gating whether to let one more request through, a retry count a single thread reads and acts on immediately, or any value another thread must be able to update conditionally. `LongAdder.sum()` combines its internal cells at the moment it is called and is not guaranteed exact while other threads are still adding, and `LongAdder` has no `compareAndSet` at all, so anywhere the code needs to read-and-decide rather than accumulate-and-report-later, `AtomicLong` is the correct tool even though it is measurably slower here.

</details>

## Real-world reps

- [ ] Write the eight-thread `HashMap` program from this lesson yourself, run it three times, and note whether it loses entries on the first attempt for you too.
- [ ] Find a get-then-put or get-then-compute pattern in code you have, on a `Map` of any kind, and decide whether it is actually reachable from more than one thread; if it is, replace it with `computeIfAbsent`, `putIfAbsent` or `merge`.
- [ ] Swap a hot `AtomicLong` counter you have for a `LongAdder`, run both under whatever load you can generate, and see whether the order-of-magnitude gap from this lesson shows up on your machine too.
- [ ] Tomorrow: find a queue, buffer, or in-memory list in code you have that is shared between threads, and check whether it is one of the collections from this lesson or a plain one standing in for it by accident.

## Going further

- [`ConcurrentHashMap`](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/concurrent/ConcurrentHashMap.html): every operation's atomicity guarantee, stated exactly, including `computeIfAbsent`'s restriction against updating the same map
- [`BlockingQueue`](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/concurrent/BlockingQueue.html): the family of implementations and which of them is bounded
- [`LongAdder`](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/concurrent/atomic/LongAdder.html): the striped-counter design, and why `sum()` is a snapshot rather than a lock
- [Concurrency](../reference/concurrency.md): the reference sheet for this stage
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
