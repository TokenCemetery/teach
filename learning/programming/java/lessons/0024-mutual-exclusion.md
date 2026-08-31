---
title: "24. Mutual Exclusion"
description: One thread at a time, the two ways to say it, and the deadlock you can find before it happens
type: lesson
---

# Lesson 24. Mutual Exclusion

**Mission link:** Owning a service means being able to look at a `synchronized` block or a `ReentrantLock` and say exactly what invariant it protects, find a deadlock in review before it reaches production, and say precisely what holding a lock across the wrong call costs, which is the mission's reviewing judgement applied to the oldest tool in the language.
**Primary source:** [`Lock`, Java SE 25 API](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/concurrent/locks/Lock.html)
**Prerequisites:** [Lesson 23](0023-the-memory-model.md), [Lesson 10](0010-inheritance-and-composition.md)

## Warm-up

1. ▢ A thread spins in a loop rereading a plain, non-volatile boolean field that another thread sets to end the loop. What guarantee is missing, and what is the one-word fix?

<details markdown="1"><summary>Check</summary>

Visibility. With no happens-before edge between the write and the read, the reader is never guaranteed to see the new value, and the loop can run forever with nothing in the source looking wrong. Marking the field `volatile` gives the write-then-read happens-before edge that fixes it.

</details>

2. ▢ A method catches `InterruptedException` with an empty catch block and carries on. What did it just destroy, and what are the two acceptable responses instead?

<details markdown="1"><summary>Check</summary>

It destroyed the only signal anyone had that cancellation was requested, since catching the exception clears the thread's interrupt flag. The two acceptable responses are to propagate the exception, by declaring it or wrapping it in an unchecked exception and rethrowing, or to restore the flag with `Thread.currentThread().interrupt()` before returning, so that a caller further up the call stack can still see that interruption happened.

</details>

## Know this

### `synchronized`, the monitor, and the lock you publish

Every object carries an intrinsic lock, its **monitor**, whether anything ever uses it or not. A `synchronized` method acquires the monitor of `this` for the whole method body; a `synchronized` block names the object explicitly:

```java
class Counter {
    private int value;

    synchronized void increment() {      // locks `this`
        value++;
    }

    void incrementViaBlock() {
        synchronized (this) {            // the same lock, written explicitly
            value++;
        }
    }
}
```

A `static synchronized` method locks the `Class` object instead, since there is no `this` at the class level. Whichever object you name is the lock, and any other code anywhere in the program that happens to synchronise on that same object contends for it too. Locking on `this` or on a public field therefore **publishes** your lock: a caller holding a reference to the object can synchronise on it directly, hold it across anything, and slow your method down for reasons visible nowhere near your class. A private `final` field created only to be a lock, `private final Object lock = new Object();`, is not reachable from outside and cannot be published by accident.

### Reentrancy

The same thread can re-acquire a monitor it already holds, which is what lets one `synchronized` method call another on the same object without the thread deadlocking against itself:

```java
class Reentrant {
    synchronized void outer() {
        System.out.println("outer holds the monitor, calling inner");
        inner();
    }

    synchronized void inner() {
        System.out.println("inner ran, so the same thread re-acquired the same monitor");
    }
}
```

Running `new Reentrant().outer()` prints both lines and returns normally:

```text
outer holds the monitor, calling inner
inner ran, so the same thread re-acquired the same monitor
```

A non-reentrant lock would block `inner()` forever, since as far as it knows the monitor is already held by someone. Java's monitors count acquisitions per thread and release only when the count returns to zero, which is why this just works. `ReentrantLock`, below, is reentrant for the same reason; `StampedLock`, also below, is not, and says so.

### The granularity decision

The lock should protect an invariant, not wrap a statement. A withdrawal that checks a balance and then decrements it needs both steps under the same acquisition, because the invariant, "the balance never goes below zero", spans both:

```java
// checks and decrements under two SEPARATE acquisitions
boolean ok;
synchronized (lock) {
    ok = balance >= amount;
}
if (ok) {
    // anything at all can happen here: a lookup, formatting, nothing
    synchronized (lock) {
        balance -= amount;
    }
}
```

The first version of a test for this split the lock exactly as shown, with nothing between the two blocks, run from twenty threads each trying to withdraw 50 from a balance of 100. It did not reproduce a wrong answer: five runs all finished at a correct 0, because the gap between the check and the decrement was too narrow for more than two threads to slip through before the balance ran out. Widening that gap with a five-millisecond sleep between the check and the act, standing in for the lookup or formatting that real code often does have there, reproduced the failure on every one of five further runs, one attempt each time:

```text
final balance: -900
```

Twenty threads each saw `balance >= 50` while it was still 100, all queued past the check before any of them decremented, and all twenty decrements went through: `100 - 20 × 50 = -900`. Locking the check and the decrement in one acquisition instead settles at `0` on every run, because no thread can see a stale answer to "is there enough": the check and the act happen in the same critical section:

```text
final balance: 0
```

Not every real gap needs an artificial sleep to matter. Anything the code already does between a check and the act it licenses, a network call, a second collection lookup, another lock, is exactly this window.

### `ReentrantLock`

`ReentrantLock` (`java.util.concurrent.locks`, Java 5) is `synchronized` as an object instead of a keyword, and it adds what a keyword cannot: a timed, non-blocking acquisition attempt, interruptible acquisition, fairness, and more than one wait condition per lock. Because there is no block scope to release it for you, every acquisition needs a `finally`:

```java
ReentrantLock lock = new ReentrantLock();
lock.lock();
try {
    // critical section
} finally {
    lock.unlock();
}
```

`tryLock(timeout, unit)` returns `false` instead of blocking once the timeout elapses. With one thread holding the lock for a full second and a second thread calling `lock.tryLock(300, TimeUnit.MILLISECONDS)`:

```text
acquired=false after waiting about 300 ms
```

observed as 301 and 305 ms on two runs, close enough to the requested 300 that the method is clearly returning on the timeout rather than on some other event. `lockInterruptibly()` is the same idea for interruption: a thread blocked in it responds to `interrupt()` with `InterruptedException` instead of continuing to wait, which a plain `synchronized` block cannot do. `new ReentrantLock(true)` requests fairness, roughly first-come-first-served acquisition, at a real throughput cost, which is why it is a request and not the default. `lock.newCondition()` returns a `Condition`, and a single `ReentrantLock` can hand out several: a bounded buffer can wait on "not full" and "not empty" as two separate condition queues sharing one lock, where a monitor's built-in `wait`/`notify` gives you exactly one wait set per object.

### `wait`, `notify`, `notifyAll`, and why the check needs a loop

`wait()`, `notify()` and `notifyAll()` work on a monitor's own wait set rather than a `Condition`'s, and the same trap applies to both: the condition must be re-checked in a `while` loop after waking, never assumed true because `notify` happened. Two consumer threads waiting on one queue holding a single item show why. Both call `take()`; the version that checks with `if` does not re-check after waking:

```java
synchronized String take() throws InterruptedException {
    if (queue.isEmpty()) {   // BROKEN: checked once, not re-checked
        wait();
    }
    return queue.removeFirst();
}
```

A producer adds one item and calls `notifyAll()`, waking both consumers. Across five runs, exactly one of the two always threw:

```text
consumer-1 got: only-item
consumer-2 threw: java.util.NoSuchElementException
```

Whichever consumer's thread happened to run first took the only item; the other resumed from `wait()`, trusted its stale `if` check, and called `removeFirst()` on a queue that was empty by the time it got there. Changing the check to a `while` fixes it on every run: the second consumer re-checks, finds the queue empty again, and correctly waits for an item that never arrives, rather than crashing:

```text
consumer-1 got: only-item
consumer-2 state after 1s: WAITING
```

This is not a rare timing fluke: with `notifyAll()` waking every waiter and only one item to give out, some waiter is always going to find the condition false again, and only a loop protects it. `Condition.await()` needs the same loop for the same reason. `Condition` is the better default today over raw `wait`/`notify` mainly because a `ReentrantLock` can offer several of them, which turns "wait for one of these two different things" from two threads fighting over one wait set into two separate, named queues.

### `ReadWriteLock` and `StampedLock`

`ReadWriteLock` (Java 5), implemented by `ReentrantReadWriteLock`, splits one lock into a shared read side and an exclusive write side: any number of readers may hold the read lock together, but a writer excludes everyone, readers included. It earns the cost of two internal locks instead of one on a structure that is read far more often than written and expensive enough to protect coarsely that the split pays for itself; on a cheap operation the bookkeeping usually costs more than the plain lock it replaced ever did.

`StampedLock` (Java 8) adds a third mode on top of read and write: **optimistic reading**. `tryOptimisticRead()` hands back a stamp without taking any lock at all, and `validate(stamp)` checks afterwards whether a writer got in while the read was happening; if validation fails, the caller retries with a real read lock. Its own documentation states plainly that it is **not reentrant**, and warns against calling an unknown method while holding one, which is the same warning the two rules below give for every lock, stated by the API that most needs it.

### Deadlock, reproduced and detected

Two threads, each locking the same two objects in opposite order, is the classic shape:

```java
// thread 1
synchronized (lockA) {
    Thread.sleep(200);
    synchronized (lockB) { ... }
}

// thread 2
synchronized (lockB) {
    Thread.sleep(200);
    synchronized (lockA) { ... }
}
```

The 200-millisecond sleep held inside the first lock exists to guarantee the interleaving: it gives the other thread time to grab its own first lock before either one reaches for the second. Run five times, both threads deadlocked on the first attempt every time, no retries needed. `ThreadMXBean.findDeadlockedThreads()` (`java.lang.management`, Java 6) found the cycle from inside the same running program on all five runs:

```text
deadlocked thread count: 2
t1 waiting for lock java.lang.Object@... owned by t2
t2 waiting for lock java.lang.Object@... owned by t1
```

The hexadecimal identity changes between runs; the shape does not. `findDeadlockedThreads` checks cycles over both monitors and `Lock`-style ownable synchronizers, so it catches a `ReentrantLock` deadlock the same way, and its documentation is explicit that a cycle made of virtual threads is not one it finds, a limit worth remembering once virtual threads arrive in lesson 27. `findMonitorDeadlockedThreads()` is the older, monitor-only version.

Changing thread 2 to acquire the same two locks in the same order as thread 1, `lockA` then `lockB` instead of `lockB` then `lockA`, removes the cycle entirely: three runs of the reordered version all finished cleanly, with `findDeadlockedThreads()` reporting nothing. A fixed global order for any set of locks a program can hold at once is the rule this generalises to, and it is checkable by inspection, which is what makes it worth stating as a rule rather than a case-by-case judgement call.

### Livelock and starvation

**Livelock** is two or more threads that stay busy, each repeatedly backing off to let the other proceed, with neither ever actually finishing, the classic shape being two threads that each release a lock and retry on detecting contention, in lockstep, forever. A thread dump of a livelock shows every thread `RUNNABLE`, not blocked, which is exactly what makes it harder to spot than a deadlock. **Starvation** is a thread that is never denied a lock outright but is consistently passed over in favour of others, so it does make progress, just never enough of it; an unfair lock under heavy contention from other threads is a common cause, which is what `ReentrantLock`'s fairness mode exists to bound, at a real throughput cost.

### The two rules

**Never hold a lock across I/O or an unknown callback.** A lock held across a blocking call serialises every other thread that wants it for the full duration of that call, not just for the memory operation the lock was meant to protect. Timing eight threads doing twenty operations each, where each operation is a five-millisecond simulated call, gave this on one machine:

```text
lock held across the fake I/O call: 990 ms
lock released before the fake I/O call: 121 ms
```

Three runs put the ratio at roughly eight times, and it is the ratio that is the transferable part of this number, not the millisecond counts, which are one run on one machine and will differ on another. Releasing the lock before the slow call and re-acquiring it only for the shared state serialises just the part that needs it.

**Hold the smallest region that keeps the invariant.** "Smallest" is a consequence of correctness here, not the goal in itself: the granularity example above shows the failure mode of a region that is too small, one that lets an invariant spanning two operations be checked and acted on separately. The rule is to draw the region around exactly what the invariant needs, no less, and then stop, since anything held past that point is pure cost with nothing left to protect.

## Practice

1. ▢ Predict the final value, and explain it.

   ```java
   // balance starts at 60, ten threads, each tries to withdraw 20
   boolean ok;
   synchronized (lock) {
       ok = balance >= 20;
   }
   if (ok) {
       Thread.sleep(5);              // widens the window between check and act
       synchronized (lock) {
           balance -= 20;
       }
   }
   ```

<details markdown="1"><summary>Check</summary>

`-140`, observed on every one of five runs. With the check and the decrement in separate acquisitions and a five-millisecond gap between them, all ten threads pass the check while the balance is still 60, none of them see any other thread's decrement before deciding, and all ten decrements go through: `60 - 10 × 20 = -140`. Locking the check and the decrement together instead would settle at `0`, since no thread could act on a stale answer.

</details>

2. ▢ Find the bug, and name the fix.

   ```java
   class Accounts {
       void transferAtoB(Account a, Account b, int amount) {
           synchronized (a) {
               synchronized (b) {
                   a.debit(amount);
                   b.credit(amount);
               }
           }
       }
   }
   ```

   Two threads call `transferAtoB(x, y, 10)` and `transferAtoB(y, x, 5)` at the same time.

<details markdown="1"><summary>Hint</summary>

Each call locks whichever account is passed first, then whichever is passed second. What happens when the two calls disagree about which account that is?

</details>

<details markdown="1"><summary>Check</summary>

The first call locks `x` then `y`; the second locks `y` then `x`, the reversed-order shape from this lesson's deadlock demonstration, and the two calls can deadlock exactly the way `lockA`/`lockB` did. The fix is a fixed order independent of argument order, for instance always locking the account with the smaller `identityHashCode` (or a stable account ID) first, so every thread that transfers between the same two accounts locks them in the same sequence regardless of which one is named first in the call.

</details>

3. ▢ Find the bug in this consumer, using the two-consumer queue from this lesson as the reference case.

   ```java
   synchronized String take() throws InterruptedException {
       if (queue.isEmpty()) {
           wait();
       }
       return queue.removeFirst();
   }
   ```

<details markdown="1"><summary>Check</summary>

The condition is checked once, before waiting, and never re-checked after waking. With two waiters and a single item added, `notifyAll()` wakes both; whichever runs first takes the item, and the other resumes trusting a check it made before the item ever existed, then throws `NoSuchElementException` from `removeFirst()` on an empty queue, exactly as observed in this lesson's demonstration. Changing `if` to `while` re-checks the condition after every wakeup, so the second consumer sees the queue empty again and correctly waits rather than proceeding.

</details>

4. ▢ A cache is read on every request and written perhaps once an hour. Reads currently take a plain `synchronized` block. A colleague proposes `StampedLock`'s optimistic read mode instead of `ReentrantReadWriteLock`. What should the code actually do, and what does each alternative cost?

<details markdown="1"><summary>Check</summary>

`ReentrantReadWriteLock` is the safer default here: many readers proceed together, a writer excludes everyone, and the API is reentrant with no extra discipline required at call sites. `StampedLock`'s optimistic mode goes further, letting a reader proceed with no lock taken at all and only checking afterwards whether a write happened, which pays off only under contention heavy enough that even the read-side of a `ReadWriteLock` is a bottleneck, and it demands that every read be structured to validate and retry, plus the discipline `StampedLock` itself warns about: no calling unknown code while holding it, and no assuming it is reentrant. An hourly write against constant reads is unlikely to need that second, harder-to-use tier; measuring the `ReadWriteLock` version first, per lesson 14's cost rule, is the honest next step before reaching for `StampedLock`.

</details>

5. ▢ A code review turns up this method. What rule does it break, and what should change?

   ```java
   synchronized void publish(Event event) {
       subscribers.add(event.subscriber());
       httpClient.post(webhookUrl, event.toJson());   // network call
   }
   ```

<details markdown="1"><summary>Check</summary>

It holds the monitor across a network call, breaking the rule against holding a lock across I/O or an unknown callback, the same shape this lesson measured at roughly eight times slower under contention than releasing the lock first. Every other thread that wants this monitor, including one only trying to read `subscribers`, waits for the full round trip. The fix is to shrink the critical section to exactly the shared mutation, `subscribers.add(event.subscriber())`, and make the HTTP call outside any lock.

</details>

## Real-world reps

- [ ] Write the deadlock demonstration from this lesson, or a two-lock version of your own, and read what `ThreadMXBean.findDeadlockedThreads()` reports about your own threads.
- [ ] Find a `synchronized` block in code you know and ask what it locks on: `this`, a field, or a dedicated private lock, and who else in the codebase could reach that same object.
- [ ] Find a lock in code you know that spans more than the mutation it needs to, a network call, a second lookup, another lock, and estimate its cost using the measured ratio from this lesson as a first guess before you profile it.
- [ ] Tomorrow: find a `wait()` call in code you have, or in a library whose source you can read, and check whether the condition it waits for sits inside a `while` loop.

## Going further

- [`Lock`](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/concurrent/locks/Lock.html): the interface `ReentrantLock` implements, and what it adds over `synchronized`
- [`Object`](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/Object.html): the `wait`, `notify` and `notifyAll` contract, including the spurious-wakeup warning that is the reason `wait` belongs in a loop
- [`ThreadMXBean`](https://docs.oracle.com/en/java/javase/25/docs/api/java.management/java/lang/management/ThreadMXBean.html): `findDeadlockedThreads`, `findMonitorDeadlockedThreads`, and the thread information behind a dump
- [Concurrency](../reference/concurrency.md): the reference sheet for this stage
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
