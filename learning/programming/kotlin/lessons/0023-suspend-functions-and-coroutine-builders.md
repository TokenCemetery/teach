---
title: "23. Suspend Functions and Coroutine Builders"
description: "What suspend actually changes about a function, the three builders and what each one returns, and why suspending code still reads top to bottom"
type: lesson
---

# Lesson 23. Suspend Functions and Coroutine Builders

**Mission link:** The mission names writing and reasoning about coroutines. This is the entry point: what the keyword does, what starts a coroutine, and why concurrent Kotlin still reads sequentially.
**Primary source:** [Docs: "Coroutines basics", Kotlin](https://kotlinlang.org/docs/coroutines-basics.html)
**Prerequisites:** [Lesson 22](0022-threads-and-the-memory-model.md), [Lesson 15](0015-higher-order-functions-and-lambdas.md)

## Warm-up

1. ▢ A field is `@Volatile var counter = 0`. Is `counter++` safe from two threads, and why?

<details markdown="1"><summary>Check</summary>

No. `@Volatile` gives visibility, and atomicity of a single read or a single write of the backing field. `counter++` is a read and then a write, so two threads can read the same value and write the same increment, losing one. Visibility and atomicity are separate guarantees, and only one of them is on offer here.

</details>

2. ▢ Which thread-safety mode does `by lazy` use when you do not name one, and what does it promise?

<details markdown="1"><summary>Check</summary>

`LazyThreadSafetyMode.SYNCHRONIZED`. It uses a lock so that only a single thread initialises the value, and the initialised value is then visible to all threads. `PUBLICATION` and `NONE` are the opt-outs, and `NONE` gives no locks and unspecified behaviour across threads.

</details>

3. ▢ In a lambda with receiver, of type `A.(B) -> C`, what is `this` inside the lambda body, and what does that let the lambda call without qualifying it?

<details markdown="1"><summary>Check</summary>

`this` is the receiver, an instance of `A`, so the body can call `A`'s members and any extension function on `A` as if it were inside `A`. That is the mechanism the scope functions are built on, and it is about to explain why `launch` can be called with no qualifier inside one block and not compile at all outside it.

</details>

## Know this

**A coroutine is a suspendable computation.** The point of it is that concurrent code stays written in a clear, sequential style: coroutines can run concurrently with each other and potentially in parallel ([Coroutines basics](https://kotlinlang.org/docs/coroutines-basics.html)). Note where the line falls: `suspend` is part of the core language, while nearly everything else in this stage, the builders included, comes from the `kotlinx.coroutines` library.

**What `suspend` changes.** It marks a function that can pause and resume later without changing the shape of your code. The compiler then enforces one rule that shapes everything else: **a suspending function can only be called from another suspending function.** The entry point is `suspend fun main()`, and where a framework will not let you have one, `runBlocking()` is the way in.

That rule is why suspending code reads the way it does. There is no marker at the call site, no callback, no chained continuation: `val user = loadUser(id)` is a normal-looking line whose function happens to be able to suspend. Suspension is a property of the function, declared once, not a ceremony repeated by every caller.

**A coroutine is not a thread, and the difference is the reason for all of this.** A thread is managed by the operating system, needs a stack of a few megabytes, and a JVM typically handles a few thousand of them at once. A coroutine is not bound to a thread at all: it can suspend on one and resume on another, and when it suspends the thread is not blocked and stays free to run other work, which is why millions of coroutines fit in one process ([Coroutines basics](https://kotlinlang.org/docs/coroutines-basics.html)). Lesson 22's platform thread is still underneath, doing the running.

The immediate consequence is a rule you can act on: **suspend, do not block.** `delay()` suspends the coroutine and releases the thread; `Thread.sleep()` blocks the thread and takes it out of service for everything else scheduled on it. One blocking call inside a coroutine on a small pool stalls work that has nothing to do with it.

**The three builders.**

|Builder|Returns|Reach for it when|
|---|---|---|
|`runBlocking { }`|The block's value|You must call suspending code from non-suspending code and have no other way in. It creates a scope and **blocks the current thread** until everything launched inside finishes|
|`CoroutineScope.launch { }`|`Job`|You want work started alongside the rest of the scope and do not need its result. The `Job` is the handle for waiting on it or cancelling it|
|`CoroutineScope.async { }`|`Deferred`|You want a result later. `Deferred` is a light-weight non-blocking future; `await()` gets the value, and since `Deferred` is also a `Job` it can be cancelled ([Composing suspending functions](https://kotlinlang.org/docs/composing-suspending-functions.html))|

The docs are pointed about `runBlocking`: use it only when there is no other option, such as implementing a third-party interface you cannot change. Inside a suspending function you never need it, because there you can simply call the thing.

**Suspending is sequential by default.** Two suspending calls one after the other run one after the other, exactly as they read, so two operations of a second each take about two seconds. Nothing about `suspend` makes them concurrent. Concurrency is something you ask for: start both with `async`, then `await` both, and the same work takes about one second ([Composing suspending functions](https://kotlinlang.org/docs/composing-suspending-functions.html)). `async` can even be made lazy with `start = CoroutineStart.LAZY`, in which case it does not begin until `await()` or `Job.start()`.

![Two timelines for one-second suspending operations one and two. Top: calling them one after the other takes about two seconds, since two doesn't start until one finishes. Bottom: starting both with async before awaiting either runs them in parallel, about one second total.](images/sequential-vs-concurrent-async.svg)

**Why `launch` needs a receiver.** `launch` and `async` are extension functions on `CoroutineScope`, which is the warm-up's third answer arriving in practice: inside a block whose receiver is a `CoroutineScope`, they resolve with no qualifier. Move such a call into a helper function and it stops compiling unless that function declares the receiver, as `fun CoroutineScope.launchAll()`. So a builder call is never floating free; it always belongs to some scope.

Which scope, and what that scope guarantees about waiting for its children and cancelling them, is lesson 24's subject. For now, one fact from it is enough to read the examples: `coroutineScope { }` runs its block and does not return until every coroutine launched inside it has finished.

## Practice

1. ▢ A plain `fun saveAll()` calls `suspend fun save(item: Item)`. It does not compile. Why, and what are the three ways out?

<details markdown="1"><summary>Check</summary>

A suspending function can only be called from another suspending function. The three ways out: mark the caller `suspend` too, which is usually right and pushes the question up to its caller; call it inside a coroutine builder's block, `launch`, `async` or `withContext`, if you have a scope; or, at the very edge of the program where non-suspending code has to call in and cannot be changed, `runBlocking`. Reaching for `runBlocking` first is the Java-shaped instinct, and it blocks the thread that could have been running the work.

</details>

2. ▢ Two suspending functions each take about a second. Predict the elapsed time for calling them one after the other, and for `val a = async { one() }` and `val b = async { two() }` followed by `a.await() + b.await()`.

<details markdown="1"><summary>Check</summary>

About two seconds, then about one second. Suspending code is sequential by default: the second call does not start until the first returns, and `suspend` does nothing to change that. `async` is how you ask for concurrency, and the two `await` calls then just collect results that were being produced at the same time. Note the order of operations: starting both before awaiting either is what makes it concurrent. `async { one() }.await()` immediately followed by `async { two() }.await()` is the sequential version again, with extra machinery.

</details>

3. ▢ Inside `launch { }`, someone writes `Thread.sleep(1000)` where `delay(1000)` was meant. It compiles and the timing looks similar in a small test. What has actually changed?

<details markdown="1"><summary>Hint</summary>

Ask what the thread is doing during each of the two calls, not what the coroutine is doing.

</details>

<details markdown="1"><summary>Check</summary>

`delay` suspends the coroutine and releases the thread, which is then free to run other coroutines. `Thread.sleep` blocks the thread: the coroutine still occupies it and nothing else scheduled there runs for a second. In a small test with an idle pool the wall-clock time looks the same, which is exactly why this survives review. Under load on a pool sized to the core count, a handful of blocking calls can hold every thread and stall work unrelated to them. This is the single most common way a Java habit quietly removes the benefit of coroutines.

</details>

4. ▢ A suspending function's body wraps each of its own suspending calls in `runBlocking { }`. It works. What is wrong with it?

<details markdown="1"><summary>Check</summary>

`runBlocking` blocks the current thread until the work inside finishes, so this converts every suspension point back into a blocked thread and gives up the whole mechanism while keeping the syntax. Inside a suspending function the calls need no wrapper at all: call them directly. `runBlocking` is the bridge from non-suspending code that cannot be changed into suspending code, which is why the docs restrict it to the case where there is no other option.

</details>

5. ▢ Which claim about `launch` is correct?

    - a) `launch` returns a `Job` carrying the block's result, which `await` then unwraps
    - b) `launch` returns a `Job` with no result, while `async` returns a `Deferred`
    - c) `launch` returns a `Deferred`, so a fire-and-forget call must discard it explicitly
    - d) `launch` returns nothing at all, so a launched coroutine cannot be cancelled

<details markdown="1"><summary>Check</summary>

**b)** `launch` gives you a `Job`, a handle for waiting and cancelling that carries no value, and `async` gives you a `Deferred`, which is a `Job` that also promises a result. (a) puts a result on the wrong type: there is no `await` on a plain `Job`. (c) has them swapped. (d) is false, and the `Job` is precisely how a launched coroutine is cancelled, which is lesson 27's material.

</details>

## Real-world reps

- [ ] Find suspending code you have access to, or the coroutines documentation's own examples, and count the `runBlocking` calls. For each, decide whether non-suspending code really had to call in there, or whether the caller could have been `suspend` instead.
- [ ] Take one function in your own work that does two independent slow things in a row. Write down the two-line change that would make them concurrent, and the elapsed time you would expect before and after.
- [ ] Tomorrow: search for blocking calls sitting inside coroutine code, `Thread.sleep`, a synchronous HTTP client, a plain JDBC call. Pick the one with the widest reach and say which threads it takes out of service while it runs.

## Going further

- [Docs: "Coroutines basics", Kotlin](https://kotlinlang.org/docs/coroutines-basics.html)
- [Docs: "Composing suspending functions", Kotlin](https://kotlinlang.org/docs/composing-suspending-functions.html)
- [Docs: "Coroutines guide", Kotlin](https://kotlinlang.org/docs/coroutines-guide.html)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
