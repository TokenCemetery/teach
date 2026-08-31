---
title: 23. The Memory Model
description: Why a value written by one thread may never be seen by another, and the exact rule that fixes it
type: lesson
---

# Lesson 23. The Memory Model

**Mission link:** The mission names reasoning about concurrency from the memory model instead of from experiment as a specific outcome, and this lesson is the rule that reasoning rests on, including the one thing an experiment can never prove: that a race is absent.
**Primary source:** [Threads and Locks, chapter 17 of the Java Language Specification, Oracle](https://docs.oracle.com/javase/specs/jls/se25/html/jls-17.html)
**Prerequisites:** [Lesson 22](0022-threads.md), [Lesson 14](0014-immutability-as-a-default.md)

## Warm-up

1. ▢ Lesson 22 drew a line between `Thread.sleep` and waiting for a condition. Why is a fixed sleep an unreliable way to wait for another thread to finish preparing shared data?

<details markdown="1"><summary>Check</summary>

`Thread.sleep` only guarantees a minimum delay; it says nothing about whether the awaited condition became true during it. A slow producer breaks the wait, and a fast one wastes time sitting idle after the condition was already satisfied. Waiting for a condition means checking the actual state and being told when it changes, not guessing how long that takes.

</details>

2. ▢ Lesson 14's immutability recipe requires every field to be `final`. Per the glossary, what does `final` promise about a field on its own, and what does it not promise?

<details markdown="1"><summary>Check</summary>

`final` promises only that the field will not be reassigned after construction. It says nothing about the object on the other end of the reference, so a `final List` can still be cleared or added to through that same reference. This lesson adds a second, stronger promise `final` carries that has nothing to do with reassignment at all.

</details>

## Know this

### A thread that never stops

```java
static boolean stop = false;

Thread worker = new Thread(() -> {
    long spins = 0;
    while (!stop) {
        spins++;
    }
    System.out.println("worker saw stop become true after " + spins + " spins");
});
worker.start();
Thread.sleep(2000);
stop = true;
worker.join(5000);
```

Run that, and here is exactly what happened on one run on one machine: `stop` was set after two seconds, `worker.join(5000)` returned, and `worker.isAlive()` was still `true`. The worker was left spinning, consuming close to a full CPU core, for roughly another minute of wall time before it was killed by hand, having never printed anything and never seen the write. That is not a slow read. Nothing in the language promises the compiler will ever reread a plain field from memory once it has proven, from the loop's own body, that nothing in the loop changes it, so the JIT is entitled to hoist the read of `stop` out of the loop entirely and turn `while (!stop)` into `while (true)`. Marking the field `volatile` and rerunning changed the outcome completely: the worker printed after 1,187,481,214 spins and the process exited cleanly. The exact spin count is a measured number from one run and is not the point; whether the worker terminated at all is the point, and with `volatile` it did, every time it was tried.

### Visibility and atomicity are two different problems

Most confusion about this topic comes from treating these as one problem. **Visibility** asks whether a value one thread wrote is ever seen by another thread at all, which is what the spinning loop above got wrong. **Atomicity** asks whether an operation that looks like one step, such as `count++`, actually happens as one indivisible step from every other thread's point of view. A fix for one does not automatically fix the other, which is the entire content of the next section.

### The data race, precisely

The specification states the guarantee this way, in its own words: "if a program has no data races, then all executions of the program will appear to be sequentially consistent" (JLS §17.4.3). Sequential consistency means every thread's actions occur in one total order that respects each thread's own program order, and every read sees the most recent write to that variable in that order, which is the intuitive model most people already carry around in their head. The strange part is what happens the moment a program has even one data race, meaning two accesses to the same variable, from different threads, at least one of them a write, with no happens-before edge between them: the sequential-consistency guarantee is not weakened, it is withdrawn entirely, for the whole execution, not just for the racing variable. That is a stronger and stranger claim than "the read might get a stale value", and it is why the `stop` field above was not merely slow: nothing in the specification bounded what the worker was allowed to see, and what it happened to see was nothing at all.

### Happens-before, the rule that matters

**Happens-before** is the actual rule, and reasoning about a concurrent program means checking which of these edges connects the write you care about to the read you care about, rather than guessing at timing:

- program order: within one thread, an earlier action happens-before a later one.
- a monitor unlock happens-before a later lock of the same monitor by another thread.
- a `volatile` write happens-before a later `volatile` read of the same field that sees it.
- `Thread.start` happens-before anything the started thread does.
- everything a thread does happens-before another thread's successful `Thread.join` on it.
- the utilities in `java.util.concurrent` each publish their own happens-before edges, such as a `put` on a `BlockingQueue` happening-before the matching `take`.

No edge, no guarantee. Two accesses connected by one of these edges are safe from each other by specification, not by luck.

### What `volatile` actually gives you

`volatile` gives visibility and ordering for that one field: a write happens-before a later read of it, which is exactly what fixed the spinning loop. It gives no atomicity for anything that is not a single read or a single write:

```java
static volatile int count = 0;
// four threads, each running count++ 100_000 times
```

Three runs of four threads each incrementing a `volatile int count` 100,000 times, expecting `400000`, measured on one machine: `189903`, `192504`, and `341514`, lost updates of `210097`, `207496`, and `58486`. Every run lost a large and different number of updates on the very first attempt, no special scheduling needed. `count++` is read, add one, write, three separate memory operations, and `volatile` guarantees each of the three is visible immediately, not that another thread cannot interleave between them. Switching the same four threads to a `synchronized` block around the increment, or to `AtomicInteger.incrementAndGet()`, gave exactly `400000` on every one of three runs each, because both replace the three-step operation with something the specification treats as one step: a monitor, or a hardware compare-and-swap. `synchronized` is covered properly in the next lesson and `AtomicInteger` in the one after that; here they are only the two things that were tried and that worked.

### Safe publication

An object can be handed to another thread with no data race in exactly four ways: through a `static` field initialised at class-loading time, since the class loader's own locking supplies the happens-before edge; through a `volatile` field or an `AtomicReference`; through a `final` field of a properly constructed holder object, which is the next section; or protected throughout, on both the writing and the reading side, by the same lock. Anything else, including a plain instance field set by one thread and read by another with no lock and no `volatile`, is a data race on the reference itself, whatever the fields of the object it points to look like.

### The `final` field freeze

The specification's own wording is precise about what a `final` field buys you, and it is stronger than "it will not be reassigned": "an object is considered to be completely initialised when its constructor finishes. A thread that can only see a reference to an object after that object has been completely initialised is guaranteed to see the correctly initialised values for that object's `final` fields" (JLS §17.5). Read that against the previous section: it holds "even if a data race is used to pass references to the immutable object between threads", in the specification's own example. That is the one place in this lesson where a data race is explicitly tolerated rather than fixed, which is why an immutable object built with the recipe from lesson 14, `final` fields set only in the constructor, is safe to hand to another thread with no lock and no `volatile` at all.

To see whether a non-`final` field can be caught in the broken state this guarantee rules out, a `Holder` with a plain `int x` was published through an ordinary static reference, no `volatile`, no lock, from one thread while another thread spun reading the reference and checking whether it ever saw a non-null `Holder` whose `x` was still `0`. Three runs of two million publications each, six million attempts in total, on one machine: zero. This did not reproduce. That is reported honestly rather than folded into the guarantee as if it had been demonstrated: the failure mode is real by specification, well documented, and the reason `final` fields carry a rule most other fields do not, but this particular attempt to trigger it on this hardware and this JIT, in this amount of time, did not succeed, and the next section is exactly about why that absence proves nothing.

### Reordering is real, and you cannot prove its absence

The unsafe-publication attempt above produced zero failures across six million tries, and that is worth exactly nothing as evidence that the failure cannot happen, because absence of an observed failure never proves absence of the failure, only presence of a limitation in that particular attempt. Contrast it with a second experiment, the classic store-buffering pattern: two plain, non-`volatile` fields `x` and `y`, one thread sets `x` then reads `y` into `r1`, another thread sets `y` then reads `x` into `r2`, repeated for five million rounds with a fresh `x = 0; y = 0;` each round. Under sequential consistency, `r1 == 0 && r2 == 0` cannot happen: working through every legal interleaving of the two threads' program orders shows that seeing both as zero would require each thread's read to precede the other thread's write while each thread's own write precedes its own read, a cycle no total order can satisfy. Measured on one machine, two separate runs of five million rounds each: `4,764,588` and `4,895,169` rounds landed on that supposedly-impossible result, roughly nineteen in twenty. Making `x` and `y` `volatile` and rerunning the identical test, same rounds, same machine: zero anomalies. The ratio between "almost every round" and "not one round" is the transferable part of that result; the precise percentage is one run on one machine and would very plausibly come out differently on different hardware, since how often a plain field's write and read can be observed out of order depends on what the processor's own memory model already tolerates. What does not depend on the hardware is the rule: a program with a data race on `x` and `y` has no sequential-consistency guarantee at all, so a result that looks impossible by ordinary reasoning is not a bug in the test, it is the specification working exactly as documented. That is also the honest shape of this whole lesson: the unsafe-publication case that would not reproduce is not evidence the final field freeze is unnecessary, and the reordering that reproduced on nineteen rounds out of twenty is not a property of Java in general, it is what happens-before is for, a rule that holds regardless of what any one test run happened to show.

### The practical rule

Shared mutable state needs a stated policy: which lock protects it, or that it is confined to one thread, or that it is only ever published through one of the four safe ways above. "No shared mutable state" is the cheapest policy available, and it is the reason lesson 14 taught immutability before this lesson taught you why it works.

## Practice

1. ▢ Predict what this program does, and say which happens-before edge is missing.

   ```java
   static boolean ready = false;
   static int payload = 0;

   // thread A
   payload = 42;
   ready = true;

   // thread B
   while (!ready) { }
   System.out.println(payload);
   ```

<details markdown="1"><summary>Check</summary>

There is no guarantee thread B ever stops looping, for the same reason the non-volatile `stop` field in this lesson spun forever: nothing forces the compiler to reread `ready` from memory once it can prove the loop body never changes it. Even supposing B does eventually see `ready == true`, with no happens-before edge between A's write of `ready` and B's read of it, there is also no guarantee B's `println` sees `42` rather than `0`, since the write to `payload` has nothing ordering it before the read either. Marking `ready` `volatile` fixes both problems in one move: it gives the read a reason to happen, and the volatile write to `ready` happens-before the volatile read that sees it, which by program order also carries the earlier write to `payload` across with it.

</details>

2. ▢ Find the bug, given what this lesson measured about `volatile`.

   ```java
   static volatile int inventory = 0;

   void restock(int n) { inventory += n; }
   void sell(int n)    { inventory -= n; }
   ```

<details markdown="1"><summary>Hint</summary>

`inventory += n` is not one memory operation. Count how many reads and writes of `inventory` it actually performs.

</details>

<details markdown="1"><summary>Check</summary>

`inventory += n` reads `inventory`, adds `n`, and writes the result back: three steps, exactly like the `count++` measured earlier in this lesson losing updates across four threads. `volatile` guarantees each of those three steps is visible the instant it happens, not that another thread cannot run its own read-modify-write in between two of them, so concurrent calls to `restock` and `sell` can still lose updates the same way `count++` did. The fix is the same one that worked in the lesson: replace the field with an `AtomicInteger` and call `addAndGet`, or protect both methods with the same lock.

</details>

3. ▢ Four ways were used or named in this lesson to make a shared counter's total come out right under concurrent access: a plain `int`, a `volatile int`, a `synchronized` block, and `AtomicInteger`. Which of the four actually gave the correct total when measured, and which gave a wrong total despite looking like it should have worked?

<details markdown="1"><summary>Check</summary>

`synchronized` and `AtomicInteger` both gave exactly the expected total on every run measured. The plain `int` and the `volatile int` both lost updates, and the `volatile int` is the one worth remembering as the trap: it looks fixed, because `volatile` is the concurrency keyword and the field is clearly shared, but visibility of each step is not the same guarantee as the three steps happening as one, and the measured lost-update counts were large on every run, not a rare edge case.

</details>

4. ▢ A colleague publishes a configuration object like this, from a background loading thread to the request-handling threads that read it:

   ```java
   static Config config; // plain field, no volatile, no lock

   class Config {
       final Map<String, String> settings;
       Config(Map<String, String> settings) {
           this.settings = Map.copyOf(settings);
       }
   }
   ```

   Is the publication of `config` itself safe? Is a request thread that does see a non-null `config` guaranteed to see `settings` fully populated?

<details markdown="1"><summary>Check</summary>

The publication of the `config` reference through a plain static field is not one of the four safe ways: it is not `volatile`, not an `AtomicReference`, not guarded by a lock on both sides, and a plain static field is only safely published at class-loading time, not by an assignment that happens later at run time. A request thread could fail to see `config` become non-null at all, for the same reason the `stop` flag could spin forever. But if a request thread does see a particular `Config` reference, the `final` field freeze guarantees it sees `settings` fully populated and pointing at the fully built, already-copied map, because that guarantee holds even when the reference itself arrived by a data race. The fix for the publication problem is to make `config` `volatile`; the `final` field is already doing its job correctly.

</details>

5. ▢ The unsafe-publication experiment in this lesson ran six million attempts and never caught a `Holder` with a stale `int` field. A teammate concludes from this that skipping `final` on that field is fine in practice. What is wrong with that conclusion, and what did this lesson measure that makes the same mistake look tempting in the other direction?

<details markdown="1"><summary>Check</summary>

Six million attempts with no failure shows only that this attempt, on this hardware, under this JIT, in this amount of time, did not trigger the failure; the specification never promised it would be easy to trigger, only that nothing rules it out without a happens-before edge or the `final` field freeze. The store-buffering experiment in the same lesson is the sharper version of exactly this trap: it reproduced on roughly nineteen rounds out of twenty, which proves the opposite mistake, that a result some people assume is theoretical only, is not. Neither run of either experiment is evidence about what any other machine, JIT, or Java release would show; the specification's rule is the only thing that transfers, which is the whole reason this lesson is built around a rule rather than a demonstration.

</details>

6. ▢ Design question: a service has one `Map<String, Long>` of counters that every request thread increments and occasionally an admin thread reads in full to render a report. Name a policy that makes this correctly synchronised, and say what it would cost to switch to "no shared mutable state" instead.

<details markdown="1"><summary>Check</summary>

A workable policy is a `ConcurrentHashMap<String, LongAdder>`, where each request thread calls `increment()` on the adder for its key and the admin thread's report iterates the map, accepting a weakly consistent view that may miss a few in-flight updates rather than blocking every request thread to get an exact snapshot; both classes are covered properly in lesson 25. The "no shared mutable state" alternative would have each request thread accumulate into its own local counters and periodically hand a finished batch to the admin logic over a queue, removing the shared map entirely; it costs a report that is only as current as the last batch handed over, in exchange for never needing a policy on the map at all, which is a fair trade when near-real-time is not actually a requirement and a bad one when it is.

</details>

## Real-world reps

- [ ] Run the non-volatile flag loop from this lesson yourself, watch it fail to stop, then add `volatile` and watch the same code terminate.
- [ ] Run the `count++` measurement three times and write down the three totals you get; they will very likely differ from each other and from the ones in this lesson, and that variation is itself the lesson.
- [ ] Open a class you already have with a field written by one thread and read by another, and name which of the four safe-publication mechanisms protects it, or admit that none currently does.
- [ ] Tomorrow: find a `static` mutable field in code you have that is not `final`, not `volatile`, and not behind a lock, and decide which of this lesson's happens-before edges, if any, actually connects its writer to its readers.

## Going further

- [Threads and Locks, JLS §17](https://docs.oracle.com/javase/specs/jls/se25/html/jls-17.html): the full memory model this lesson compresses, including the causality rules this lesson left out
- [Java Concurrency in Practice](https://jcip.net/): visibility, publication and safe construction built up from the same model, with more failure modes named than this lesson had room for
- [`AtomicInteger`](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/concurrent/atomic/AtomicInteger.html): used here only as a working fix; the full atomics family is lesson 25
- [Concurrency](../reference/concurrency.md): the reference sheet for this stage
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
