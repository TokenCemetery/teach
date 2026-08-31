---
title: 22. Threads
description: A thread is a scheduled call stack, and almost every mistake in this stage starts with treating one as free
type: lesson
---

# Lesson 22. Threads

**Mission link:** The mission asks you to reason about concurrency from the memory model rather than from experiment, and that reasoning has nothing to stand on until "thread" means something precise, an independently scheduled call stack over one shared heap, which is the fact this lesson establishes and the rest of the stage assumes you already have.
**Primary source:** [`Thread`, Java SE 25 API](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/Thread.html)
**Prerequisites:** [Lesson 15](0015-exceptions.md), [Lesson 9](0009-interfaces.md)

## Warm-up

1. ▢ A colleague writes `a.toLowerCase().equals(b.toLowerCase())` believing it is a locale-independent, case-insensitive comparison. Why isn't it, and what should the call be instead?

<details markdown="1"><summary>Check</summary>

`toLowerCase()` with no argument consults the JVM's default locale rather than any fixed rule, so the comparison can give a different answer on a machine whose default locale is, for example, Turkish. `equalsIgnoreCase`, or `toLowerCase(Locale.ROOT)` on both sides if the lower-cased value is needed afterwards, never consults a locale.

</details>

2. ▢ A method catches a `NumberFormatException` and throws a new exception without passing the original as the cause. What does the resulting stack trace lose?

<details markdown="1"><summary>Check</summary>

It loses the `Caused by:` section entirely: nothing in the trace names the `NumberFormatException`, or the line that actually threw it, so whoever reads the failure is left reconstructing what happened from the message string alone.

</details>

## Know this

### What a thread actually is

A thread is an independently scheduled call stack: its own program counter, its own local variables, its own pending method calls, running on whatever CPU the operating system hands it next, for however long the scheduler decides. What it does not have is its own heap. Every thread in a process sees the same objects, the same static fields, the same instance fields on anything reachable from more than one stack, and that single shared heap sitting underneath many independent call stacks is the entire reason concurrency is hard: two threads calling the same method at once get separate frames for their own locals, no conflict there, but the moment that method reads or writes a field, both threads are touching one piece of shared state, and nothing about the language stops them from doing it at the same instant. Hold onto that one sentence, an independently scheduled call stack over a shared heap, because every guarantee this stage introduces is a rule about what is safe to do with the shared half.

### Creating one, and the run() trap

```java
Thread t = new Thread(() -> System.out.println("body ran on: " + Thread.currentThread().getName()), "worker2");
t.start();
```

`Thread`'s constructor takes a `Runnable` (lesson 9's functional interface, one abstract method, `run()`) and an optional name. Calling `start()` asks the operating system for a new call stack and schedules the `Runnable`'s body to run on it; calling `run()` instead just calls the method, on whichever thread happened to make the call, with no new stack and no concurrency at all:

```java
Thread t = new Thread(() -> System.out.println("body ran on: " + Thread.currentThread().getName()), "worker");
t.run();     // no new thread
t.start();   // an actual second thread
```

```text
body ran on: main
body ran on: worker2
```

The two lines look identical at the call site, `t.run()` and `t.start()`, and the mistake compiles, runs, and prints something plausible either way, which is exactly why it survives in code: the first call reports `main`, because `run()` is an ordinary method call that executes wherever it is invoked from, and the second reports the thread's own name, because `start()` is the one that actually hands the body to a new, independently scheduled stack.

### `join`, and what it guarantees beyond waiting

```java
Thread worker = new Thread(() -> result = computeSomething());
worker.start();
worker.join();      // blocks until worker's run() returns
use(result);
```

`join()` blocks the calling thread until the target thread finishes, which is the part everyone already expects. What is easy to miss is that it also guarantees the calling thread sees every write the target thread made before it finished, with no separate synchronisation needed: `Thread.join` is one of the specification's happens-before edges (JLS chapter 17, along with `Thread.start`), a term this stage's next lesson gives a precise meaning to. For now, the practical version is enough: reading a value a worker thread set, after `join()` returned, is safe in a way that reading the same value some other way is not guaranteed to be, and the next section shows exactly what "some other way" can cost.

### `Thread.sleep` against waiting for a condition

`Thread.sleep(millis)` pauses the current thread for at least that long and guarantees nothing about what else has happened by the time it wakes up. Using it as a stand-in for "the other thread is probably done by now" is a race, not a wait, and it is straightforward to make it happen:

```java
Thread worker = new Thread(() -> {
    try { Thread.sleep(ThreadLocalRandom.current().nextInt(0, 20)); } catch (InterruptedException ignored) {}
    result = expected;
});
worker.start();
Thread.sleep(10);              // guessing the worker is done
int sleepSeen = result;        // sometimes read before result is set
worker.join();
int joinSeen = result;         // always read after
```

Run 2000 times, each with a fresh worker whose own delay is picked at random from 0 to 19 milliseconds against a fixed 10 millisecond guess, this reproduced on the very first run, no repeated attempts needed: the fixed sleep read the wrong value 943 times out of 2000, and `join` read the wrong value zero times out of 2000. The fix is not a longer guess, since no fixed duration is safe against a worker whose delay can exceed it; the fix is to wait for the actual event, `join`, a latch, a queue, rather than for a duration that merely makes the failure rare.

### Interruption: cooperative cancellation

Java has no way to force one thread to stop from another. **Interruption** is the cooperative alternative: calling `interrupt()` on a thread sets a flag on it, nothing more, and it is entirely up to that thread's own code to notice and react. The one place the flag becomes hard to ignore is inside a blocking call such as `Thread.sleep`, `wait`, or a blocking queue operation, each of which checks the flag, clears it, and throws `InterruptedException` instead of continuing to block:

```java
Thread swallower = new Thread(() -> {
    try {
        Thread.sleep(5000);
    } catch (InterruptedException e) {
        System.out.println("flag inside catch = " + Thread.currentThread().isInterrupted());
    }
});
swallower.start();
Thread.sleep(200);
swallower.interrupt();
```

```text
flag inside catch = false
```

Catching `InterruptedException` clears the flag as part of throwing it, which the output above confirms directly: by the time the `catch` block runs, `isInterrupted()` already reports `false`. That clearing is easy to miss and expensive when missed, because the flag was the only signal any other code had that cancellation was requested, and an empty `catch (InterruptedException e) {}` destroys it with nothing to show it ever existed.

### The two correct responses to an interrupt

There are exactly two acceptable reactions once `InterruptedException` is caught: propagate it, or restore the flag.

Propagating means not catching it at all, letting it travel up the `throws` clause to a caller better positioned to decide what cancellation means here, which is why the checked-exception mechanics from lesson 15 apply directly: a method that can declare `throws InterruptedException` should usually just do that instead of catching. Inside a `Thread`'s own body this option does not exist, because `Runnable.run()` declares no checked exceptions at all:

```java
Runnable r = () -> {
    Thread.sleep(100);
};
```

```text
error: unreported exception InterruptedException; must be caught or declared to be thrown
```

That is not a workaround waiting to be found; `run()`'s signature is fixed by the interface, so a `Runnable` body has no `throws` clause to propagate into. The remaining correct move is to restore the flag before the method returns, `Thread.currentThread().interrupt()`, so that any later code checking `isInterrupted()`, or any later blocking call further down the same thread, still sees that cancellation was requested:

```java
try {
    Thread.sleep(5000);
} catch (InterruptedException e) {
    Thread.currentThread().interrupt();
}
```

```text
flag inside catch = false
flag after restoring = true
```

Swallowing the exception, the shape with the empty `catch` block above, is the one response that is never correct: it leaves nothing behind for anyone to see, in either the flag or the logs, and the loop or wait it interrupted simply carries on as if nothing happened.

### Daemon threads and what keeps the process alive

A thread inherits its **daemon** status from the thread that created it, so anything started from `main` is non-daemon by default unless told otherwise:

```java
System.out.println("main isDaemon: " + Thread.currentThread().isDaemon());   // false
Thread t = new Thread(() -> {});
System.out.println("child isDaemon before start: " + t.isDaemon());         // false
```

The JVM exits once every non-daemon thread has finished, regardless of how many daemon threads are still running; a daemon thread never gets to finish its own work if that is the only thing left. Starting a thread that sleeps two seconds and then prints, with `main` returning immediately and doing nothing else, shows the difference directly:

```java
Thread t = new Thread(() -> {
    try { Thread.sleep(2000); } catch (InterruptedException ignored) {}
    System.out.println("worker finished sleeping");
});
t.setDaemon(daemon);
t.start();
// main returns right away
```

Set as a daemon, the process exited without ever printing the message, in a few hundred milliseconds; set as non-daemon, the process waited and printed it, taking a couple of seconds, matching the worker's own sleep. Both figures come from one run on one machine; the ratio between "returns almost immediately" and "waits for the worker" is the part worth remembering, not the exact millisecond counts. A background thread that must not block shutdown, a periodic housekeeping task, is the usual reason to mark one daemon; anything whose work has to complete, a write that must land, should stay non-daemon and be joined.

### The uncaught exception handler

An exception that escapes a thread's `run()` uncaught does not propagate anywhere else in the process, and it does not crash it either; the thread simply terminates, and the exception goes to that thread's **uncaught exception handler**, which by default prints it to the standard error stream:

```java
Thread t = new Thread(() -> { throw new RuntimeException("boom in worker"); }, "worker");
t.start();
t.join();
System.out.println("main still running after worker's uncaught exception");
```

```text
Exception in thread "worker" java.lang.RuntimeException: boom in worker
	at UncaughtDefault.lambda$main$0(UncaughtDefault.java:4)
	at java.base/java.lang.Thread.run(Thread.java:1474)
main still running after worker's uncaught exception
```

`main` never sees the exception and never stops; only the one thread that threw it goes away. Calling `setUncaughtExceptionHandler` on a thread before starting it replaces that default printing with whatever the handler does instead:

```java
t.setUncaughtExceptionHandler((thread, ex) ->
        System.out.println("custom handler caught " + ex + " from " + thread.getName()));
```

```text
custom handler caught java.lang.RuntimeException: boom in worker from worker
main still running after worker's uncaught exception
```

Nothing else about the program changed: the exception still never reaches `main`, the handler is the only thing that changes, from a stack trace on standard error to whatever logging, alerting, or cleanup the handler was written to do. A thread pool (lesson 26) that submits work via `execute` relies on exactly this handler; a pool that uses `submit` instead routes the exception somewhere else entirely, which is its own trap for that lesson.

### Naming threads

```java
Thread a = new Thread(() -> {});
Thread b = new Thread(() -> {});
a.getName();   // "Thread-0"
b.getName();   // "Thread-1"
```

An unnamed thread gets `Thread-0`, `Thread-1`, and so on, which is useless in a stack trace, a thread dump, or a log line once a program has more than a couple of threads running. The uncaught-exception output two sections up named the failing thread `"worker"` only because the constructor's second argument said so; the same failure from an unnamed thread would have named it `"Thread-4"` or whatever count it happened to reach, telling a reader nothing about what that thread was for. Passing a name to the constructor, or calling `setName` before `start()`, is close to free and is the cheapest debugging investment this stage has to offer.

### The cost of a platform thread

Every thread created this way, a **platform thread**, is backed by a real operating-system thread with its own stack, and that stack is not free. Starting platform threads in a tight loop, each one held open so it cannot finish and free its slot, eventually exhausts something:

```java
for (int created = 0; ; created++) {
    new Thread(() -> { /* blocks until told to stop */ }).start();
}
```

```text
failed after creating 4068 platform threads
failure: java.lang.OutOfMemoryError: unable to create native thread: possibly out of memory or process/resource limits reached
```

That count, 4068, is one observation on one machine and not a portable limit; a different machine with different resource limits will fail at a different count, sooner or later, and the failure itself, `OutOfMemoryError` for something that has nothing to do with heap memory, is as informative as the number, since it is the first clue that "just start more threads" has a ceiling. Executors (lesson 26) exist to reuse a bounded set of these instead of creating one per task; virtual threads (lesson 27) exist because a platform thread's real stack is precisely the cost they remove.

### The honest summary

Code that calls `new Thread(...).start()` directly inside a service, rather than inside the small number of places that manage concurrency on purpose, is almost always a defect waiting to be found in review: it has no bound on how many can exist at once, as the section above just showed the cost of, no shared handling for the exception it might throw, as the section before that showed, and no name, until someone remembers to give it one. Everything this lesson taught is what to check for when that defect turns up, and lessons 26 and 27 are what to suggest instead.

## Practice

1. ▢ Predict the output, and explain it.

   ```java
   Thread t = new Thread(() -> System.out.println(Thread.currentThread().getName()), "worker");
   t.run();
   t.start();
   ```

<details markdown="1"><summary>Check</summary>

`main`, then `worker`. `t.run()` is an ordinary method call, so it executes on whichever thread called it, `main` here; `t.start()` is the one call that actually hands the `Runnable` to a new, independently scheduled stack, which is why only the second line reports the thread's own name.

</details>

2. ▢ Find the bug. This loop is meant to stop as soon as the thread is interrupted.

   ```java
   while (true) {
       try {
           Thread.sleep(1000);
           doWork();
       } catch (InterruptedException e) {
       }
   }
   ```

<details markdown="1"><summary>Hint</summary>

Catching `InterruptedException` clears the flag. What does the `while (true)` condition see afterwards?

</details>

<details markdown="1"><summary>Check</summary>

The empty `catch` swallows the exception and leaves no trace of it: the flag is cleared the moment it is caught, so `while (true)` has nothing to check and loops straight back into another `sleep`, forever. Either return or break out of the loop right there, or restore the flag with `Thread.currentThread().interrupt()` and check `Thread.currentThread().isInterrupted()` in the loop condition instead of `true`.

</details>

3. ▢ A pull request adds `new Thread(() -> sendWelcomeEmail(user)).start()` inside a request-handling method, with the comment "runs it in the background so the response doesn't wait." What would you say in review?

<details markdown="1"><summary>Check</summary>

Nothing bounds how many of these can exist at once under load, since a burst of requests starts a burst of platform threads with no ceiling; nothing catches an exception `sendWelcomeEmail` might throw, so a failing send disappears into the default uncaught-exception handler with no retry and no alert; and the thread is unnamed, so a leak or a pile-up shows up in a thread dump as an anonymous crowd of `Thread-N` entries. A bounded executor (lesson 26), submitted to rather than started directly, fixes the first two problems by construction and makes the third easy to fix by naming the pool's threads once.

</details>

4. ▢ A worker thread sets a shared field and the reader calls `Thread.sleep(50)` before reading it instead of `join()`. Why does this sometimes read the right value anyway, and what does that make the bug worse, not better?

<details markdown="1"><summary>Check</summary>

It reads the right value whenever the worker happens to finish inside those 50 milliseconds, which on a lightly loaded machine is often, so the code passes casual testing and even a fair amount of production traffic before a slower run, a loaded machine, or a larger input makes the worker take longer than the guess. A bug that is usually invisible is worse than one that fails every time, because it survives review and testing and only turns up as an intermittent, hard-to-reproduce wrong answer in the field, exactly the shape this stage keeps coming back to.

</details>

5. ▢ Two threads both call an uncaught, unhandled `RuntimeException` inside their own `run()` methods, with no custom handler set on either. What happens to the process, and what happens to each thread?

<details markdown="1"><summary>Check</summary>

The process keeps running; an uncaught exception terminates only the one thread it escaped from, it does not propagate to any other thread and does not crash the JVM. Each exception is printed to standard error by the default handler, tagged with the name of the thread that threw it, and both threads are simply gone afterwards, with nothing to show for it beyond that printed trace unless a custom handler was set to do something else.

</details>

6. ▢ A one-shot command-line tool starts a background thread to flush a write-ahead log every second, and never calls `join()` on it or shuts it down explicitly. The tool never exits on its own. Why, and what is the one-line fix?

<details markdown="1"><summary>Check</summary>

A newly created thread inherits daemon status from its creator, and `main` is non-daemon, so the flushing thread is non-daemon too by default; the JVM only exits once every non-daemon thread has finished, and a thread looping every second never finishes on its own. Marking it a daemon with `t.setDaemon(true)` before `start()` lets the process exit as soon as `main` returns, at the cost of the last, in-flight flush possibly never running, which is exactly the trade daemon status makes.

</details>

## Real-world reps

- [ ] Write the `run()` versus `start()` snippet from practice 1 yourself, predict both lines before running, then run it and check.
- [ ] Write a thread that sleeps, interrupt it from the main thread, and print `isInterrupted()` inside the `catch` block; then add the one line that restores the flag and print it again to see the difference.
- [ ] Start a daemon thread and a non-daemon thread doing the same delayed print with nothing else in `main`, and watch which run prints the message and which one the process exits without waiting for.
- [ ] Tomorrow: find a place in code you have that calls `new Thread(...)` directly, and check whether it is named, whether anything calls `join()` on it or otherwise waits for it, and what happens if the body it runs throws.

## Going further

- [`Thread`](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/Thread.html): `interrupt`, daemon status, and the uncaught exception handler, all on one page
- [`Runnable`](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/Runnable.html): the functional interface every thread body implements
- [JLS Chapter 17, Threads and Locks](https://docs.oracle.com/javase/specs/jls/se25/html/jls-17.html): where `join`'s guarantee beyond waiting actually comes from
- [Concurrency](../reference/concurrency.md): the reference sheet for this stage
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
