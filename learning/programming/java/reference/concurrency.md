---
title: Concurrency
description: Which guarantee each construct gives, which model fits the workload, and what the symptom in front of you means
type: reference
---

# Concurrency

Lookup sheet for stage 4. The question it exists to answer: **what does this guarantee, and which guarantee did the failure in front of me break?**

## Happens-before edges

A read and a write connected by none of these edges have no ordering or visibility guarantee between them at all, whatever timing makes it look safe on any one run.

- Program order: within one thread, an earlier action happens-before a later one.
- A monitor unlock happens-before a later lock of the same monitor by another thread.
- A `volatile` write happens-before a later `volatile` read of the same field that sees it.
- `Thread.start` happens-before anything the started thread does.
- Everything a thread does happens-before another thread's successful `Thread.join` on it.
- Each `java.util.concurrent` utility publishes its own edge, such as a `put` on a `BlockingQueue` happening-before the matching `take`.

## Visibility against atomicity

| | Asks | Given by | Not given by |
|---|---|---|---|
| Visibility | whether a value one thread wrote is ever seen by another thread at all | a happens-before edge: `volatile`, a monitor, `Thread.start`/`Thread.join`, the `final` field freeze, or a `java.util.concurrent` utility's own edge | atomicity, since a value can be visible the instant it changes and still be one of several separate steps another thread can interleave with |
| Atomicity | whether an operation that looks like one step happens as one indivisible step from every other thread's point of view | a monitor (`synchronized`), a lock, or a hardware compare-and-swap (`Atomic*`) | visibility, since an atomic step still needs a happens-before edge before another thread is guaranteed to see its result |

A `volatile` increment still loses updates: `count++` on a `volatile int` is a read, an add and a write, three separate memory operations, and `volatile` guarantees each one is visible immediately, not that another thread cannot interleave between them. Four threads each incrementing a shared `volatile int` 100,000 times, expected total 400,000, measured on one machine across three runs: 189,903, 192,504 and 341,514, losing 210,097, 207,496 and 58,486 updates respectively; the absolute counts are one machine's numbers, the fact that a large, different amount was lost on every single run is what transfers. Switching the same increment to a `synchronized` block or to `AtomicInteger.incrementAndGet()` gave exactly 400,000 on every run measured, because both replace the three steps with something the specification treats as one.

## What each construct guarantees

| Construct | Guarantees | Does not give |
|---|---|---|
| `synchronized` | mutual exclusion inside the region it wraps, plus a happens-before edge: a monitor unlock happens-before a later lock of the same monitor | atomicity across two separate acquisitions; a check and an act split into two `synchronized` blocks can still be interleaved by another thread |
| `volatile` | visibility and ordering for that one field: a write happens-before a later read of it | atomicity of any operation that is more than a single read or a single write, such as `count++` or `x += n` |
| `final` field | the field-freeze: a thread that can only see a reference to an object after its constructor has finished sees the correctly initialised value of every `final` field, even if the reference itself arrived through a data race | safety for a non-`final` field of the same object, or safety for the publication of the reference itself, which still needs one of the safe-publication mechanisms below |
| `ReentrantLock` | the same mutual exclusion as `synchronized`, plus a timed or non-blocking `tryLock`, interruptible acquisition, optional fairness, and more than one wait queue per lock via `newCondition` | automatic release; there is no block scope to unlock it for you, so every acquisition needs a `finally` |
| `Atomic*` (`AtomicInteger`, `AtomicLong`, `AtomicReference`) | a read-modify-write such as `compareAndSet`, `incrementAndGet` or `updateAndGet` happens as one indivisible step no other thread can split | atomicity across two separate atomic calls; a `get` on one `Atomic*` followed by a decision and a `set` is check-then-act with the same gap as any other |
| `LongAdder` | a correct running total once `sum()` is called, at far less contention than `AtomicLong` for a simple accumulate-only counter | an exact value at any single instant while writes are still landing, and any `compareAndSet`, since it offers none |
| a concurrent collection (`ConcurrentHashMap` as the example) | each individual operation, `get`, `put`, `remove`, `size`, is atomic and visible on its own, with an iterator that is at least weakly consistent | atomicity across two separate calls; `get` then `put` is still a race, which is why `computeIfAbsent`, `putIfAbsent` and `merge` exist |
| `Thread.start` | a happens-before edge: everything visible to the starting thread up to the call is visible to the started thread | any guarantee about when the new thread actually runs, or about anything the new thread writes afterwards |
| `Thread.join` | a happens-before edge: everything the target thread did before finishing is visible to the joining thread's code after `join()` returns | bounded waiting; a plain `join()` can block indefinitely if the target never finishes, and a timed `join(millis)` that times out gives no guarantee at all |

## Safe publication

An object reaches another thread with no data race in exactly four ways: through a `static` field initialised at class-loading time, since the class loader's own locking supplies the edge; through a `volatile` field or an `AtomicReference`; through a `final` field of a properly constructed holder object, relying on the field-freeze above; or guarded throughout, on both the writing and the reading side, by the same lock. Anything else, including a plain instance or `static` field set by one thread and read by another with no lock and no `volatile`, is a data race on the reference itself, whatever the fields of the object it points to look like.

## Locks

| | `synchronized` | `ReentrantLock` | `ReadWriteLock` | `StampedLock` |
|---|---|---|---|---|
| Adds over the previous | the language's own monitor, one per object, reentrant, released automatically even by an exception | a timed or non-blocking `tryLock`, interruptible acquisition, optional fairness, more than one wait queue via `newCondition` | a shared read side any number of readers can hold together, and an exclusive write side that excludes everyone, readers included | a third mode, optimistic reading: `tryOptimisticRead()` hands back a stamp with no lock taken at all, and `validate(stamp)` checks afterwards whether a writer got in |
| Reentrant | yes | yes | yes (`ReentrantReadWriteLock`) | no, by its own documentation |
| Release | automatic at block or method exit, exception or not | manual, `unlock()` in a `finally` | manual, per side held | manual; never assume reentrancy and never call unknown code while holding the stamp |
| Earns its keep when | it is the default until something below is genuinely needed | the timeout, the interruptibility, or more than one condition is actually used; fairness costs real throughput | the structure is read far more than written and expensive enough to protect coarsely; on a cheap operation the bookkeeping usually costs more than the plain lock it replaced | contention is heavy enough that even a `ReadWriteLock`'s read side is a bottleneck, in exchange for validate-and-retry discipline at every call site |

**Deadlock prevention.** A fixed global order for any set of locks a program can hold at once removes the circular wait a deadlock needs: if every thread that acquires more than one lock always takes them in the same order, no thread can end up holding one while waiting on another thread that is waiting on it. This is checkable by inspection rather than by testing.

**Never hold a lock across I/O or an unknown callback.** Doing so serialises every other thread that wants the lock for the full duration of that call, not just for the memory operation the lock was meant to protect. Measured on one machine against a simulated blocking call: holding the lock across it took roughly eight times as long, under contention, as releasing it first and re-acquiring only for the shared state; the ratio, not the millisecond counts, is what transfers.

**Hold the smallest region that keeps the invariant, no less.** A region too small lets an invariant spanning two operations be checked and acted on separately, which is the check-then-act failure a reader should already be watching for. A region held past what the invariant needs is pure cost with nothing left to protect.

## Concurrent collections

| Shape of access | Reach for | Why |
|---|---|---|
| A general-purpose map under concurrent reads and writes | `ConcurrentHashMap` | every individual operation is atomic and visible on its own; a plain `HashMap` under concurrent `put` calls silently loses entries with no exception thrown at all |
| Read constantly, written rarely (a listener list, a configuration snapshot) | `CopyOnWriteArrayList` | every mutation copies the whole backing array, so an iterator taken from it is a genuine, unmoving snapshot; a poor choice once writes are frequent, since each one is an O(n) copy |
| Handing work from one thread to another with no lock to write | `BlockingQueue` (`ArrayBlockingQueue` bounded, `LinkedBlockingQueue` unbounded by default) | `put` blocks the producer while full, `take` blocks the consumer while empty; an unbounded queue does not resist overload, it hides it as unmonitored memory growth, so a bounded queue is the safer default |

**Check-then-act is not one operation**, and each of these closes a specific version of the gap:

| Pattern that is two operations | Atomic replacement |
|---|---|
| `get`, then `put` only if the key was absent | `computeIfAbsent` |
| `get`, then `put` unconditionally if the key was absent | `putIfAbsent` |
| `get`, combine with a new value, then `put` | `merge` |
| read, compute, write on an `Atomic*` | `compareAndSet`, or the update family built on it (`incrementAndGet`, `getAndAdd`, `updateAndGet`) |

A `computeIfAbsent` mapping function must never touch the same map, including the same key reentrantly: doing so throws `IllegalStateException: Recursive update` rather than deadlocking or silently corrupting the map.

**Iteration guarantees:**

| Collection | What its iterator promises |
|---|---|
| plain `HashMap` / `ArrayList` | best-effort `ConcurrentModificationException` on a detected structural change; a courtesy for surfacing a bug quickly, not a safety guarantee, and not promised to fire on every concurrent modification |
| `ConcurrentHashMap` | weakly consistent: never throws, never corrupts itself, but promises no snapshot, no fixed element count, and no particular ordering |
| `CopyOnWriteArrayList` | a genuine, unmoving snapshot of the backing array at the moment iteration started |

## Executors

| Factory | Builds | The honest note |
|---|---|---|
| `Executors.newFixedThreadPool(n)` | fixed core and max threads, backed by an unbounded `LinkedBlockingQueue` | a burst larger than the pool queues instead of running, and nothing is ever rejected, so overload shows up as growing memory and latency rather than an error |
| `Executors.newCachedThreadPool()` | zero core threads, `Integer.MAX_VALUE` max, threads created on demand and reused | the opposite failure mode: an effectively unbounded number of threads instead of an unbounded queue |
| `Executors.newSingleThreadExecutor()` | exactly one thread, unbounded queue, restarted if it dies | the same unbounded-queue caveat as the fixed pool, with a pool of one |
| `Executors.newScheduledThreadPool(n)` | fixed core threads, for delayed and periodic tasks | `schedule` runs once after a delay; `scheduleAtFixedRate` measures its period from each execution's start; `scheduleWithFixedDelay` measures it from each execution's end |

When a service actually needs a bounded queue and a stated rejection policy, construct `ThreadPoolExecutor` directly rather than reaching for a factory method.

| | `execute` | `submit` |
|---|---|---|
| Takes | `Runnable` only | `Runnable` or `Callable`, returns a `Future` |
| A thrown exception | reaches the worker thread's own uncaught exception handler, printed to standard error by default | captured inside the returned `Future`; never surfaces anywhere unless something calls `get()` |
| The trap | none; the exception is visible somewhere by default | a `Future` nobody ever calls `get()` on is exactly as silent as if the exception had never been thrown |

| Call | Does |
|---|---|
| `shutdown()` | stops accepting new tasks; lets queued and running tasks finish |
| `shutdownNow()` | additionally interrupts every running task and drains the queue, returning the tasks that never started |
| `awaitTermination(timeout, unit)` | blocks until the pool has actually finished shutting down, or the timeout elapses; neither shutdown call blocks by itself |
| `close()` (`ExecutorService` is `AutoCloseable`, Java 19) | calls `shutdown()`, then waits repeatedly for termination, escalating to `shutdownNow()` if the waiting thread is itself interrupted |

A pool's worker threads are non-daemon by default, so the JVM will not exit while any of them is alive, including an idle one waiting for more work.

**Rejection policies**, once a bounded queue actually rejects:

| Policy | Does |
|---|---|
| `AbortPolicy` | throws `RejectedExecutionException` at the call site |
| `CallerRunsPolicy` | runs the rejected task on the thread that tried to submit it, slowing that caller rather than failing it, which also throttles the rate new work arrives at |
| `DiscardPolicy` | drops the task silently |
| `DiscardOldestPolicy` | drops the oldest queued task to make room for the new one |

Both discard policies throw work away with no signal at all and belong nowhere the missing work would matter.

## Virtual threads

A virtual thread is a thread the JVM schedules itself, mounting it onto a platform thread that becomes its carrier for as long as it runs there; blocking on ordinary I/O or another blocking JDK call unmounts it from the carrier instead of occupying it, so a virtual thread blocked on I/O costs nothing while it waits beyond its own small stack, and the thread-per-request style scales to however many requests are actually in flight. Virtual threads became a permanent part of the platform in Java 21, after two rounds as a preview feature.

**Do not pool them.** A thread pool exists to share an expensive resource, a real operating-system thread, across many tasks; a virtual thread is cheap enough that there is nothing to share, so `Executors.newVirtualThreadPerTaskExecutor()` starts a fresh virtual thread per task and lets it end with the task, and pooling virtual threads on top of it buys nothing but extra bookkeeping. Where a pool's size was really being used to cap concurrency against some other resource rather than to share threads, a database connection pool being the standard example, a `Semaphore` sized for that resource states the limit directly, independent of how many threads exist.

**What still pins a carrier on this release, against what no longer does**, stated as measured on one machine rather than quoted from the JEP that introduced the feature:

| Blocking inside | On this release |
|---|---|
| `synchronized` (a method, a block, or a `wait` made from inside one) | no longer pins the carrier, as of [JEP 491](https://openjdk.org/jeps/491) in JDK 24; against a two-carrier control where genuine pinning cost roughly twenty-five times as long, both the `synchronized`-plus-sleep and `synchronized`-plus-`wait` cases came in near the unpinned floor |
| A blocking native call (through the Foreign Function & Memory API, finalised Java 22) | still pins exactly as before; measured elapsed time matched the fully-pinned platform-thread control almost exactly |
| Class loading, a class's static initialiser, or waiting for another thread to finish initialising a class | still pins, per JEP 491, because of a native VM frame the JVM itself puts on the stack, not because of anything application code wrote |

**The diagnostic caveat.** The `jdk.VirtualThreadPinned` JFR event fires only on a *failed attempt* to unmount, so it correctly recorded zero occurrences for the two `synchronized` cases that no longer pin, but it also recorded zero occurrences for the still-pinning native call, since a blocking native call never attempts to unmount at all: it simply occupies the carrier for the call's whole duration, with nothing for that specific event to catch even though the carrier was genuinely unavailable to every other virtual thread the entire time. A wall-clock comparison against a known-carrier-count control caught what the purpose-built diagnostic did not. `-Djdk.tracePinnedThreads` is now inert for the same reason: the case it traced, pinning inside `synchronized`, no longer occurs.

## Choosing a model

| Workload | What dominates | Model | Measured ratio |
|---|---|---|---|
| CPU-bound | computation, nothing ever blocks | a bounded platform-thread pool sized to the work, since there is no carrier to free by unmounting | about 1, measured on one machine: three runs each had a platform pool and a virtual-thread-per-task executor doing identical arithmetic trade places, confirming virtual threads buy nothing here |
| Blocking I/O-bound | waiting on a socket, a disk, a lock held elsewhere | virtual threads, one per task, written in the plain blocking style | about 17, measured on one machine and held steady across three runs, because every blocked virtual thread unmounts and frees its carrier for another where a platform pool must make threads take turns |
| Mixed | some tasks block, some compute | virtual threads for the blocking parts; the CPU-heavy parts go to a bounded platform pool so they cannot starve the carriers everything else is unmounting onto | not separately measured; follows from the two rows above |
| Coordination-heavy | contention on a shared lock or resource, not on CPU or I/O | neither choice fixes contention by itself; measure both under the real lock | not measured; the bottleneck is the coordination, not the thread type, so no ratio transfers between workloads |

## Symptom to violated guarantee

| Symptom | Guarantee violated |
|---|---|
| The program hangs | a deadlock, or a lost signal from a `wait` with nobody left to `notify` it |
| A total comes out wrong, consistently low | a lost update: two threads read the same value before either writes it back |
| Code reads a value that is stale, sometimes forever | a visibility failure: no happens-before edge connects the write to the read |
| The answer is wrong only sometimes, under load | check-then-act: the check and the act are two operations with a window between them that another thread can land in |
| An exception disappears with no trace | a swallowed `Future`: a `submit`ted task's exception sits captured until something calls `get()`, and nothing did |

## Review checklist

Each row is checked against the lesson it names rather than assumed, since this sheet was written after all seven of them existed on disk.

| Check | Lesson |
|---|---|
| Is a raw `Thread` being created here instead of handed to an executor or started as a virtual thread? | [Threads](../lessons/0022-threads.md) |
| Is every field shared across threads either `volatile`, guarded by one documented lock, or never written after construction? | [The Memory Model](../lessons/0023-the-memory-model.md) |
| Is the lock here the smallest region that keeps the invariant, and is it never held across I/O or a callback into code you do not control? | [Mutual Exclusion](../lessons/0024-mutual-exclusion.md) |
| Does anything here read-then-write a concurrent collection in two steps where `computeIfAbsent`, `putIfAbsent` or `merge` would do it in one? | [Concurrent Collections and Atomics](../lessons/0025-concurrent-collections-and-atomics.md) |
| Does every `submit`ted task's exception reach a `get()`, a `join()`, or an `exceptionally`, rather than a `Future` nobody ever asks? | [Executors and Futures](../lessons/0026-executors-and-futures.md) |
| Are virtual threads used for the blocking work and never pooled, with pinning checked on the release actually being deployed rather than assumed from something written about an earlier one? | [Virtual Threads](../lessons/0027-virtual-threads.md) |

## Release table

| Feature | Finalised in |
|---|---|
| `ReentrantLock`, `java.util.concurrent.locks` | Java 5 |
| `ReadWriteLock`, implemented by `ReentrantReadWriteLock` | Java 5 |
| `ThreadMXBean.findDeadlockedThreads` (`java.lang.management`) | Java 6 |
| `StampedLock` | Java 8 |
| `ExecutorService` as `AutoCloseable`, usable in try-with-resources | Java 19 |
| Virtual threads, permanent after two preview rounds | Java 21 |
| Foreign Function & Memory API | Java 22 |
| Synchronising virtual threads without pinning ([JEP 491](https://openjdk.org/jeps/491)) | JDK 24 |
| `StructuredTaskScope` | still preview on this baseline, JDK 25; requires `--enable-preview`, and its shape has already changed across previews |

## Sources

- [JLS Chapter 17, Threads and Locks](https://docs.oracle.com/javase/specs/jls/se25/html/jls-17.html)
- [`Thread`](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/Thread.html)
- [`Runnable`](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/Runnable.html)
- [`Object`](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/Object.html)
- [`Lock`](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/concurrent/locks/Lock.html)
- [`ThreadMXBean`](https://docs.oracle.com/en/java/javase/25/docs/api/java.management/java/lang/management/ThreadMXBean.html)
- [`ConcurrentHashMap`](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/concurrent/ConcurrentHashMap.html)
- [`BlockingQueue`](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/concurrent/BlockingQueue.html)
- [`LongAdder`](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/concurrent/atomic/LongAdder.html)
- [`AtomicInteger`](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/concurrent/atomic/AtomicInteger.html)
- [`ExecutorService`](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/concurrent/ExecutorService.html)
- [`ThreadPoolExecutor`](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/concurrent/ThreadPoolExecutor.html)
- [`ScheduledExecutorService`](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/concurrent/ScheduledExecutorService.html)
- [`CompletableFuture`](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/concurrent/CompletableFuture.html)
- [`StructuredTaskScope`](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/concurrent/StructuredTaskScope.html)
- [JEP 444, Virtual Threads](https://openjdk.org/jeps/444)
- [JEP 491, Synchronize Virtual Threads without Pinning](https://openjdk.org/jeps/491)
- [Java Concurrency in Practice](https://jcip.net/)
