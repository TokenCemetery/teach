---
title: 28. Choosing a Model
description: One question picks the model, and the failure you are looking at names the guarantee it broke
type: lesson
---

# Lesson 28. Choosing a Model

**Mission link:** This closes stage 4 at the point the stage promised: given a broken concurrent program, name the guarantee it violated, and given a new one, pick platform threads, virtual threads, or neither before writing a line of it.
**Primary source:** [`StructuredTaskScope`, Java SE 25 API](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/concurrent/StructuredTaskScope.html)
**Prerequisites:** [Lesson 27](0027-virtual-threads.md), [Lesson 24](0024-mutual-exclusion.md)

## Warm-up

1. ▢ Why is a virtual-thread-per-task executor not a pool, and why does that matter for whether you should reuse the threads it hands out?

<details markdown="1"><summary>Check</summary>

A pool exists to amortise the cost of an expensive resource across many uses. A virtual thread is cheap enough that creating and discarding one per task costs less than the bookkeeping a pool would add, so there is nothing to amortise, and trying to reuse one the way you would a platform thread only reintroduces the state-leak and sizing problems pools exist to manage.

</details>

2. ▢ What does `volatile` guarantee, and what is the one thing people reach for it to fix that it does not fix?

<details markdown="1"><summary>Check</summary>

It guarantees visibility and ordering: a write becomes visible to a subsequent read, and the write cannot be reordered past it. It does not guarantee atomicity, so `count++` on a `volatile int` still loses updates under concurrent writers.

</details>

## Know this

### The decision

The shape of the workload picks the model before any measurement is needed.

| Workload | What dominates | Model |
|---|---|---|
| CPU-bound | computation, nothing ever blocks | a bounded platform-thread pool sized to the work, since there is no carrier to free by unmounting |
| Blocking I/O-bound | waiting on a socket, a disk, a lock held elsewhere | virtual threads, one per task, written in the plain blocking style |
| Mixed | some tasks block, some compute | virtual threads for the blocking parts, with the CPU-heavy parts handed to a bounded platform pool so they cannot starve the carriers everything else is unmounting onto |
| Coordination-heavy | contention on a shared lock or a shared resource, not on CPU or I/O | neither choice fixes contention by itself; measure both under the real lock, because the bottleneck is the coordination, not the thread type |

The first two rows follow from the definitions in lesson 27 and need no measurement to pick. The last two are where reasoning runs out and measurement has to settle it, which is what the numbers below are for.

Two workloads, each measured on one machine and each run several times rather than once: a CPU-bound task, thirty-two tasks each doing forty million iterations of pure arithmetic with nothing that blocks, against a blocking I/O-bound task, five thousand tasks that each just sleep for fifty milliseconds.

For the CPU-bound task, a platform pool sized to the machine's processor count finished in 232 ms on the first run, against 198 ms for a virtual-thread-per-task executor doing the same work. That looks like a win for virtual threads until the run is repeated: a second run gave 175 ms against 181 ms, a third gave 247 ms against 198 ms, and the two traded places more than once. The honest reading is a ratio of about 1: nothing here ever blocks a carrier, so there is no unmounting for a virtual thread to benefit from, and the small differences are noise from scheduling and warm-up rather than a real effect. This is the transferable part, not the millisecond figures themselves: virtual threads buy nothing for work that never blocks.

For the blocking task, the same platform pool, sized to two hundred threads this time, took 1357, 1365 and 1357 ms across three runs to get through five thousand sleeps of fifty milliseconds each, which is almost exactly what the arithmetic predicts for two hundred threads working through twenty-five batches of fifty milliseconds. The virtual-thread executor ran the same five thousand sleeps in 81, 82 and 83 ms across the same three runs, close to the floor set by the sleep itself. That is a ratio of about 17, and unlike the CPU-bound case it held steady across every run rather than moving around. However different the absolute numbers are on a different machine, that ratio is the transferable fact: a workload that spends its time blocked rather than computing is exactly the case virtual threads exist for, because every one of those five thousand sleeps unmounts its virtual thread and frees the carrier for another, where the platform pool had to make two hundred threads take turns.

### The two cheapest strategies

Before choosing a threading model at all, two answers are cheaper than either. The cheapest concurrency is none: a task that does not need to run at the same time as another should not be made to. The second cheapest is no shared mutable state, which is the recipe in [lesson 14](0014-immutability-as-a-default.md): an object nothing can change needs no lock, no `volatile`, and no happens-before edge to reason about, because there is nothing for a data race to disagree about. Reaching for a threading decision before asking whether the sharing can be removed is how straightforward code turns into code that needs this lesson.

### Structured concurrency, and its actual status

The idea: a task that forks subtasks should not be able to outlive the syntactic block that forked them. Cancellation and failure then come for free, because closing the block is the one place that has to wait for every subtask and the one place that can decide what a failure of one of them means for the rest, instead of that logic being reinvented at every call site that uses raw `Future`s.

Rather than trust a description of where this stands, including this one, compiling it settles it. This is the exact result of compiling the shape shown in the API documentation, on this release, with no `--enable-preview` flag:

```text
error: StructuredTaskScope is a preview API and is disabled by default.
  (use --enable-preview to enable preview APIs)
```

It is still a preview feature on this release. The shape it takes right now, run with the flag it demands:

```java
try (var scope = StructuredTaskScope.open()) {
    var a = scope.fork(() -> 1 + 1);
    var b = scope.fork(() -> 2 + 2);
    scope.join();
    System.out.println(a.get() + b.get());
}
```

That compiles and prints `6` under `--enable-preview`, but the shape is worth treating as unstable rather than learning by heart: this API has changed its constructor into a static factory and added a `Joiner` parameter across previews, and code written against an earlier preview's shape will not compile against this one. Until it finalises, the plain answer is to compose what lesson 26 already covers: an `ExecutorService` opened in try-with-resources, `invokeAll` where every subtask must finish before you continue, and an explicit unwrap of `ExecutionException` to decide what one subtask's failure means for the others. It is more code than the intended shape, and it is the version you can rely on today.

### Diagnosis: from symptom to guarantee

Every failure in this stage is a specific guarantee that something violated, and naming it is most of the fix.

| Symptom | Guarantee violated |
|---|---|
| The program hangs | a deadlock (lesson 24), or a lost signal from a `wait` with nobody left to `notify` it |
| A total comes out wrong, consistently low | a lost update: two threads read the same value before either writes it back |
| Code reads a value that is stale, sometimes forever | a visibility failure: no happens-before edge connects the write to the read |
| The answer is wrong only sometimes, under load | check-then-act: the check and the act are two operations with a window between them that another thread can land in |
| An exception disappears with no trace | a swallowed `Future`: a `submit`ted task's exception sits captured until something calls `get()`, and nothing did |

### Getting evidence

A thread dump is the first thing to pull from a hung or stuck program, and it does not need special tooling: any dump of a running JVM lists every thread with its state and, for a blocked one, what it is waiting on. Taken from a small program that starts five named worker threads and puts them to sleep, the dump held about two dozen threads in total, five of them the named workers, each reported as waiting on the condition the sleep created, and the rest the JVM's own housekeeping threads that every dump carries and that a reader learns to recognise and skip.

Deadlock detection does not need a dump at all, if the suspicion is specific: the same `ThreadMXBean` lookup lesson 24 used to detect one from inside a running program, asking it which threads are deadlocked, found a genuine deadlock between two threads acquiring the same two locks in opposite orders on the first check, a hundred milliseconds after the threads started.

The fact worth carrying into any of this: adding a print statement to narrow down a race changes the timing of the program being observed, since a print is I/O and can shift which thread gets scheduled next. A fix that only works with the diagnostic logging still in place has not been verified; it has been verified for a different program.

### The review checklist

Each row is a one-line restatement of a lesson already taught, kept short because the lesson is where the reasoning lives.

| Check | Lesson |
|---|---|
| Is a raw `Thread` being created here instead of handed to an executor or started as a virtual thread? | [Threads](0022-threads.md) |
| Is every field shared across threads either `volatile`, guarded by one documented lock, or never written after construction? | [The Memory Model](0023-the-memory-model.md) |
| Is the lock here the smallest region that keeps the invariant, and is it never held across I/O or a callback into code you do not control? | [Mutual Exclusion](0024-mutual-exclusion.md) |
| Does anything here read-then-write a concurrent collection in two steps where `computeIfAbsent`, `putIfAbsent` or `merge` would do it in one? | [Concurrent Collections and Atomics](0025-concurrent-collections-and-atomics.md) |
| Does every `submit`ted task's exception reach a `get()`, a `join()`, or an `exceptionally`, rather than a `Future` nobody ever asks? | [Executors and Futures](0026-executors-and-futures.md) |
| Are virtual threads used for the blocking work and never pooled, with pinning checked on the release actually being deployed rather than assumed from something written about an earlier one? | [Virtual Threads](0027-virtual-threads.md) |

### The honest closing point

A concurrency bug that will not reproduce is not fixed by a change that cannot be tested against it. The first move, every time, is to make it reproduce: more iterations, more contention, a smaller critical section timed to widen the window, or evidence from a thread dump about where it is actually stuck. A fix applied before that is a guess wearing the shape of a fix.

## Practice

1. ▢ Predict what happens if you compile the `StructuredTaskScope` example above on the current long-term-support release without `--enable-preview`, then explain why the fix is not simply "add the flag" for code that has to ship.

<details markdown="1"><summary>Check</summary>

It fails to compile, reporting that `StructuredTaskScope` is a preview API disabled by default and naming `--enable-preview` as the way to turn it on. `--enable-preview` is not a fix for shipping code because a preview API can change shape between releases, as this one already has, and a build that requires the flag commits every consumer of that build to matching the same preview release, which is a much larger promise than using one finished feature.

</details>

2. ▢ Find the bug, and say which checklist row would have caught it in review.

   ```java
   ExecutorService pool = Executors.newFixedThreadPool(4);
   pool.submit(() -> {
       if (!validate(request)) {
           throw new IllegalArgumentException("bad request");
       }
       process(request);
   });
   ```

<details markdown="1"><summary>Check</summary>

Nobody calls `get()` on the `Future` that `submit` returned, so if `validate` throws, the exception is captured inside that `Future` and never surfaces anywhere: no log line, no crash, nothing. The request is silently dropped. The checklist row for lesson 26 catches it: every submitted task's exception needs to reach a `get()`, a `join()`, or an `exceptionally`, and this one reaches none of them. Switching to `execute` would at least send the exception to the uncaught handler; calling `get()` on the stored `Future`, or checking it later, is the fix that keeps the result too.

</details>

3. ▢ Three symptom reports come in from the same service. For each, name the guarantee most likely violated: (a) a counter that should equal the number of requests processed comes out a little low, every time, under load; (b) a background thread that reads a configuration flag set by the main thread at startup sometimes acts on the old value, seemingly forever; (c) two maintenance jobs each hold the same two resources and the process never exits.

<details markdown="1"><summary>Check</summary>

(a) is a lost update: two threads read the counter before either had written its increment back. (b) is a visibility failure: nothing establishes a happens-before edge between the write and every thread that might read it, so a `volatile` field or safe publication is missing. (c) is a deadlock: two resources acquired in opposite orders by two threads, each waiting on what the other holds.

</details>

4. ▢ A service has a request handler that briefly holds an in-memory lock to update a shared cache, and profiling under real load shows most request time going to threads waiting on that lock rather than to the database call the requests also make. Virtual threads have already been adopted for the database call. Should more of the handler move to virtual threads, and how would you actually decide rather than guess?

<details markdown="1"><summary>Check</summary>

No, not on the strength of that profile: this is coordination-heavy, not blocking-I/O-bound, and virtual threads do nothing about contention on a lock, since the wait there is for another thread to release it, not for a carrier to unmount onto. The threading model is not the lever here. The decision is made by measuring, under the same real load, what shrinking the locked region or removing the shared cache's need for a lock at all does to the wait time, since the two cheapest strategies from earlier in this lesson (do less concurrently, share less mutable state) are the candidates that actually address contention.

</details>

5. ▢ A colleague wants to add a debug `System.out.println` inside a suspected race to see which thread gets there first, planning to remove it once the bug is understood. What is the risk in trusting what that print shows, and what should they do instead if the race stops reproducing once the print is added?

<details markdown="1"><summary>Check</summary>

The print statement is I/O, and I/O can change which thread the scheduler runs next, so adding it can make a race reproduce less often, more often, or not at all, which is evidence about the instrumented program rather than about the original one. If the race stops reproducing with the print in place, that is not a sign the bug is understood, since removing the print could bring it back; the safer path is to gather evidence that does not perturb timing as much, such as a thread dump taken from outside the process, or to accept that the print changed the experiment and treat any conclusion drawn from it as provisional until it is confirmed another way.

</details>

## Real-world reps

- [ ] Run a CPU-bound comparison and a blocking-I/O comparison like the ones in this lesson against a workload you actually have, and see whether your ratios land anywhere near 1 and 17 or somewhere else entirely.
- [ ] Try compiling a small `StructuredTaskScope` snippet without `--enable-preview` on whatever current release you have installed, and read the exact message it gives you.
- [ ] Take one piece of concurrent code you have written or reviewed and run it down all six checklist rows, stopping at the first one that does not clearly pass.
- [ ] Tomorrow: find a concurrency bug report, yours or a team's, that never got a confirmed root cause, and try to name, from the symptom alone, which guarantee it most likely violated.

## Going further

- [`StructuredTaskScope`](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/concurrent/StructuredTaskScope.html): the preview API this lesson could name but not teach as current
- [`ThreadMXBean`](https://docs.oracle.com/en/java/javase/25/docs/api/java.management/java/lang/management/ThreadMXBean.html): the deadlock detection this lesson reused from lesson 24
- [Book: "Java Concurrency in Practice", Goetz, Peierls, Bloch, Bowbeer, Holmes, Lea](https://jcip.net/): the mental model behind this stage's diagnosis table, when the table itself is not enough
- [Concurrency](../reference/concurrency.md): the reference sheet for this stage
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
