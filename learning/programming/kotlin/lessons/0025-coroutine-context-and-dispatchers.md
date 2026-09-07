---
title: "25. Coroutine Context and Dispatchers"
description: "The context as a set of elements combined with plus, which dispatcher belongs to which kind of work, and the one context element that silently breaks structured concurrency"
type: lesson
---

# Lesson 25. Coroutine Context and Dispatchers

**Mission link:** Owning coroutines in a service means answering "which threads is this actually running on" and "why did that coroutine outlive its scope". Both answers live in the context.
**Primary source:** [Docs: "Coroutine context and dispatchers", Kotlin](https://kotlinlang.org/docs/coroutine-context-and-dispatchers.html)
**Prerequisites:** [Lesson 24](0024-structured-concurrency.md), [Lesson 23](0023-suspend-functions-and-coroutine-builders.md), [Lesson 18](0018-operator-overloading.md)

## Warm-up

1. ▢ What does `coroutineScope { }` guarantee about the line of code directly after its closing brace?

<details markdown="1"><summary>Check</summary>

That every coroutine launched inside the block has completed. `coroutineScope` executes its suspending block and does not return until the block and everything launched within it has finished, so nothing of its own can still be running when the next line executes.

</details>

2. ▢ Inside a coroutine, what is the difference between `delay(1000)` and `Thread.sleep(1000)`?

<details markdown="1"><summary>Check</summary>

`delay` suspends the coroutine and releases the thread, which is then free to run other coroutines. `Thread.sleep` blocks the thread, so the coroutine keeps it and nothing else scheduled on it runs. On a pool sized to the core count, a few blocking calls can hold every thread.

</details>

3. ▢ What has to be true of a type for `a + b` to compile on it?

<details markdown="1"><summary>Check</summary>

It needs a function named `plus`, with the `operator` modifier, taking the right-hand operand. The symbol maps to that one fixed name, and without the modifier a same-named function is never picked up by operator syntax.

</details>

## Know this

**A context is a set of elements.** Every coroutine runs in a `CoroutineContext`, a type that lives in the Kotlin standard library rather than in the coroutines library. It is a set, and its main two elements are the coroutine's `Job` and its dispatcher ([Coroutine context and dispatchers](https://kotlinlang.org/docs/coroutine-context-and-dispatchers.html)). Others exist: a `CoroutineExceptionHandler` for failures that cannot be propagated anywhere else, a `CoroutineName` for debugging, and on the JVM a `ThreadContextElement` that sets a thread-local on whichever thread ends up executing the coroutine.

Those elements combine with `+`, which is warm-up 3 arriving in a library you did not write: `SupervisorJob() + CoroutineExceptionHandler { _, e -> log(e) }` is one context holding two elements. Every builder takes an optional context parameter, so `launch(Dispatchers.IO)` and `launch(Dispatchers.IO + CoroutineName("import"))` are the same mechanism with one and two elements.

**Two axes, and keeping them apart is most of this lesson.** The scope governs lifecycle, and the dispatcher governs which threads run the code. A coroutine launched inside another inherits the parent's context, and its `Job` becomes a child of the parent's `Job`. For the dispatcher specifically: builders inherit it from the parent scope, and if the context contains no dispatcher at all, they use `Dispatchers.Default` ([Coroutines basics](https://kotlinlang.org/docs/coroutines-basics.html)).

**The four dispatchers.**

|Dispatcher|What it is|
|---|---|
|`Default`|What every standard builder uses when the context specifies no dispatcher. A shared pool for CPU work, sized up to the number of available cores with a minimum of two threads|
|`IO`|Designed for offloading blocking IO to a shared pool whose threads are created and shut down on demand. Parallelism is capped by the `kotlinx.coroutines.io.parallelism` property, defaulting to 64 threads or the core count, whichever is larger ([IO](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/-dispatchers/-i-o.html))|
|`Main`|Confined to the main thread that operates with UI objects, and usually single-threaded. Android's half of this mission|
|`Unconfined`|Not confined to any thread: it runs the coroutine's initial continuation in the current call frame and then lets it resume on whatever thread the suspending function used. An advanced tool, not a default|

**Switching, and what it costs.** `withContext(other)` may suspend the current coroutine and switch to the new context, provided the new context actually differs from the current one. Where the difference is the dispatcher, extra dispatches are involved: the block is scheduled on the new dispatcher, and afterwards execution returns to the original one. That round trip is exactly why `withContext` is the tool for "run this part somewhere else and come back", and why it, rather than `launch`, is how a suspending function offloads a blocking call without changing its own contract.

Two facts about `Dispatchers.IO` that correct the obvious mental model, both from its own documentation. It shares threads with `Default`, so a `withContext(Dispatchers.IO)` issued while already running on `Default` typically does **not** switch threads at all; the implementation keeps execution where it is on a best-effort basis. And its parallelism limit is a limit on blocking tasks running in parallel, not a hard cap on threads: more threads than the limit can exist, but the extras are guaranteed to be starting up or shutting down rather than working.

**Partitioning IO.** `Dispatchers.IO.limitedParallelism(n)` gives you a view with its own budget, and the elasticity is the point: views are not carved out of IO's own 64. The documentation's example takes 100 threads for MySQL and 60 for MongoDB, so at peak the system may run 64 plus 100 plus 60 blocking tasks in parallel, while at steady state those views share a small number of threads with each other and with `IO`. This is how one slow dependency is stopped from eating the whole blocking budget.

**The element that quietly undoes lesson 24.** The parent-child relation can be overridden, and one of the two ways is to pass a different `Job` as part of the new coroutine's context. Do that and the coroutine is no longer tied to the scope it was launched from: it operates independently ([Coroutine context and dispatchers](https://kotlinlang.org/docs/coroutine-context-and-dispatchers.html)). The other way is launching in a different scope explicitly, which is what `GlobalScope.launch` is.

So `launch(Dispatchers.IO)` and `launch(Dispatchers.IO + Job())` look like the same kind of edit, one adding a second element to a context. The first is a child of its scope, cancelled with it and waited for by it. The second is not, and nothing about the call site says so.

## Practice

1. ▢ Inside `suspend fun main()`, a `coroutineScope { }` block calls `launch { }` with no arguments. Which dispatcher runs that coroutine, and what decides it?

<details markdown="1"><summary>Check</summary>

It inherits the dispatcher from its parent scope, because a coroutine launched inside another inherits that coroutine's context. If nothing in the inherited context specifies a dispatcher, which is the case for a bare `suspend fun main`, the builder falls back to `Dispatchers.Default`. Two separate rules, and the second only applies once the first has found nothing.

</details>

2. ▢ A suspending function already running on `Dispatchers.Default` wraps a blocking JDBC call in `withContext(Dispatchers.IO) { }`. Predict whether the code moves to a different thread, and say what the wrapper achieved either way.

<details markdown="1"><summary>Hint</summary>

Ask which pool each of the two dispatchers draws its threads from.

</details>

<details markdown="1"><summary>Check</summary>

Typically it does not move: `Dispatchers.IO` shares threads with `Default`, and the implementation tries on a best-effort basis to keep execution on the same thread. What the wrapper still achieves is the accounting. The call now runs as a blocking task under IO's parallelism budget rather than occupying a CPU-pool slot indefinitely, which is what protects the `Default` pool's core-count-sized capacity. Predicting "no thread switch, but a different budget" is the useful mental model; predicting "IO means a different thread" is the one that leads to surprise in a profiler.

</details>

3. ▢ Two lines differ by one element: `launch(Dispatchers.IO) { work() }` and `launch(Dispatchers.IO + Job()) { work() }`. What changes, and which of the two breaks when the enclosing scope is cancelled?

<details markdown="1"><summary>Hint</summary>

One of these two elements is the one the scope uses to own its children.

</details>

<details markdown="1"><summary>Check</summary>

The first inherits the parent's `Job`, so the coroutine is a child: the scope waits for it and cancelling the scope cancels it. The second passes its own `Job`, which overrides the parent's, so the coroutine is not tied to the scope it was launched from and runs independently. Cancelling the scope leaves it running, and the scope will not wait for it either. Adding a dispatcher to a context is routine; adding a `Job` opts out of structured concurrency, and the syntax gives no hint of the difference in kind.

</details>

4. ▢ A service makes blocking calls to both MySQL and MongoDB, all through `Dispatchers.IO`. Mongo starts responding slowly under load and MySQL-backed endpoints get slow too, though the database itself is healthy. Explain the coupling, and what `limitedParallelism` changes.

<details markdown="1"><summary>Check</summary>

Both workloads draw on the same parallelism budget, so a pile-up of slow Mongo calls occupies the slots that MySQL work needed, and the queue is shared even though the two dependencies are not. `Dispatchers.IO.limitedParallelism(n)` gives each dependency its own budget, and because views of `IO` are elastic rather than carved out of its 64, giving Mongo 60 does not take 60 away from anything else. What they do share is threads and resources at steady state, so this partitions the queueing, not the machine.

</details>

5. ▢ Which claim divides the responsibilities correctly?

    - a) The dispatcher decides a coroutine's lifetime, and the scope decides its thread
    - b) The scope decides a coroutine's lifetime, and the dispatcher decides its threads
    - c) The context holds one element, the dispatcher, chosen when a builder runs
    - d) The context is fixed per thread, so every coroutine there shares it

<details markdown="1"><summary>Check</summary>

**b)** The scope controls the lifecycle, through the `Job` in its context, and the dispatcher controls which thread or threads execute the code. (a) swaps them, which is the mix-up that produces both of this lesson's bugs. (c) undercounts: a context is a set, and its two main elements are the `Job` and the dispatcher, with more available. (d) has the ownership backwards: the context belongs to the coroutine and travels with it, which is how a coroutine can suspend on one thread and resume on another.

</details>

## Real-world reps

- [ ] Find every explicit dispatcher argument in Kotlin you have access to. For each, say which of the four it is and whether the work it wraps is CPU-bound, blocking, or UI, then whether those two agree.
- [ ] Search for a `Job()` or `SupervisorJob()` passed into a `launch` or `async` call, as opposed to into a scope's own construction. Each one is a coroutine that has left its parent's tree; decide whether that was intended.
- [ ] Tomorrow: for one service you work on, write down the blocking dependencies it has and whether they share a parallelism budget. Decide what you would set with `limitedParallelism` and what you would need to measure to pick the numbers.

## Going further

- [Docs: "Coroutine context and dispatchers", Kotlin](https://kotlinlang.org/docs/coroutine-context-and-dispatchers.html)
- [API: "Dispatchers", kotlinx.coroutines](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/-dispatchers/)
- [API: "Dispatchers.IO", kotlinx.coroutines](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/-dispatchers/-i-o.html)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
