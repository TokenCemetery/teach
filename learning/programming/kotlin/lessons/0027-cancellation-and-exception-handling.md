---
title: "27. Cancellation and Exception Handling"
description: "Why cancellation is cooperative and what makes code ignore it, why a CancellationException is not a failure, and how the coroutine model compares with Java virtual threads"
type: lesson
---

# Lesson 27. Cancellation and Exception Handling

**Mission link:** Stage 5 closes here. The done-when is predicting what a concurrent coroutine program does before running it, and comparing the model to Java 21 virtual threads, which is what the last two items ask for.
**Primary source:** [Docs: "Cancellation and timeouts", Kotlin](https://kotlinlang.org/docs/coroutines-cancellation.html)
**Prerequisites:** [Lesson 26](0026-flows.md), [Lesson 24](0024-structured-concurrency.md), [Lesson 22](0022-threads-and-the-memory-model.md)

## Warm-up

1. ▢ What does a cold flow do when it has two collectors, and what does that mean for the work in its builder block?

<details markdown="1"><summary>Check</summary>

Each new collector starts a new, independent execution of the flow, so the builder block runs twice. Work inside it, a query or a connection, happens once per collector rather than once per flow. That is what "cold" means, and it is why a stream that should exist independently of its collectors has to be a hot flow instead.

</details>

2. ▢ In `launch(Dispatchers.IO)` and `launch(Dispatchers.IO + Job())`, which coroutine is a child of the enclosing scope?

<details markdown="1"><summary>Check</summary>

Only the first. Passing a `Job` as part of the new coroutine's context overrides the parent's, so the second coroutine is not tied to the scope it was launched from and runs independently: the scope will neither wait for it nor cancel it.

</details>

3. ▢ Kotlin has no `synchronized` keyword. What does `@Synchronized` do, and when is `synchronized(lock) { }` the right form instead?

<details markdown="1"><summary>Check</summary>

`@Synchronized` marks the generated JVM method as synchronized, guarded by the monitor of the instance, or of the class for a static method. Use the `synchronized(lock) { }` function wherever you need to name the lock, and specifically on an extension function, which compiles to a static method and would otherwise lock the monitor of the compiled facade class rather than the receiver.

</details>

## Know this

**Cancellation runs through the `Job`, and it is cooperative.** Cancelling a coroutine means calling `cancel()` on its `Job`, either by hand or through propagation when a parent is cancelled. The coroutine then throws a `CancellationException` **the next time it checks for cancellation**, and the suspending functions in the library, `delay()` among them, check when they suspend ([Cancellation and timeouts](https://kotlinlang.org/docs/coroutines-cancellation.html)).

The word cooperative is the whole lesson: a coroutine reacts to cancellation only by suspending or by checking explicitly. A cancelled coroutine keeps running until it reaches a suspension point. And a `suspend` call is a suspension point without always suspending: awaiting an already-completed `Deferred` does not suspend, so it is not a cancellation check either.

So a tight computational loop with no suspension point ignores `cancel()` completely. Three ways to fix that, in order of preference:

|Tool|Behaviour|
|---|---|
|`yield()`|Suspends briefly, releasing the thread so other coroutines can run on it, and checks for cancellation. Throws `CancellationException` if cancelled. The default answer, because it fixes both problems a non-suspending loop has|
|`ensureActive()`|Throws `CancellationException` if cancelled. A check without a suspension, for when giving up the thread is genuinely not wanted|
|`isActive`|Returns `false` when cancelled. The Boolean form, for when you want to finish something first rather than throw|

**Prompt cancellation, and why cleanup needs help.** A suspended coroutine that gets cancelled resumes with a `CancellationException` rather than returning a value, **even when that value is already available**. The docs call this prompt cancellation, and its purpose is to stop your code continuing inside a cancelled scope, such as updating a screen that has already closed. `withContext` checks for cancellation both before entering its block and after it returns, which is what makes the line after a `withContext` safe to run.

That same promptness breaks cleanup. A suspending `close()` inside a `finally` will not complete, because the coroutine is already cancelled. The fix is `withContext(NonCancellable) { ... }` around the part that must finish. Note the warning attached to it: do not use `NonCancellable` with `launch` or `async`, because that disrupts structured concurrency by breaking the parent-child relationship. It belongs around a block, not around a coroutine.

A timeout is cancellation with a clock attached. `withTimeoutOrNull(duration)` returns `null` when the duration is exceeded, which makes the timed-out case an ordinary value to branch on rather than an exception to catch.

**Why `CancellationException` is not a failure.** This is the hinge between the two halves of the lesson. A child's failure makes its parent fail with the same exception only when all three of these hold ([CoroutineScope](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/-coroutine-scope/)):

1. The exception is not a `CancellationException`.
2. The failed child was not created with a lexically scoped builder such as `coroutineScope` or `withContext`.
3. The parent's `Job` is not a `SupervisorJob`.

Condition 1 is why cancelling one child does not take the family down, while one child throwing an `IOException` does: cancellation is a request travelling down the tree, and failure is news travelling up it. Condition 3 is the opt-out, and it has two spellings: build the scope with `SupervisorJob()`, or use `supervisorScope` in place of `coroutineScope`. That is what lesson 24 was pointing at when it used `SupervisorJob()` without explaining it.

**How exceptions reach you at all.** Builders come in two flavours: `launch` propagates exceptions automatically, while `async` exposes them to you ([Coroutine exceptions handling](https://kotlinlang.org/docs/exception-handling.html)). As a **root** coroutine, `launch` treats an exception as uncaught, in the manner of Java's `Thread.uncaughtExceptionHandler`, and `async` relies on you to consume it, through `await`. A `CoroutineExceptionHandler` in a root coroutine's context is the generic catch block for it and its children: you cannot recover in it, because the coroutine has already completed with that exception by the time it is called, so it is for logging, reporting, terminating or restarting. It runs only for genuinely uncaught exceptions, and children delegate handling to their parent all the way to the root, which is why a handler installed on a child is never used.

**The comparison this stage closes on.** Both models make blocking cheap, and they do it at different layers. A coroutine suspends at a suspension point the compiler produced; a virtual thread unmounts from its carrier when it blocks on a JDK blocking call. The Java workspace's [concurrency sheet](../../java/reference/concurrency.md) holds the virtual-thread side in detail, measured on one machine, including what still pins a carrier and why you do not pool them. Set against that, the axes that actually decide between them:

|Axis|Coroutines|Virtual threads|
|---|---|---|
|What the code looks like|Suspending functions are marked `suspend`, and the compiler enforces who may call them|Ordinary blocking code, unchanged signatures, so existing libraries work as they are|
|Unit of work|A coroutine, cheap enough to have millions, scheduled onto a pool|A thread per task, cheap enough not to pool, which the sheet is emphatic about|
|Lifetime and cancellation|Part of the model: a `Job` tree, cancellation that propagates, a scope that waits|Not a property of the thread type; grouping and cancellation come from a separate API or from your own bookkeeping|
|What still costs you|A blocking call holds a pool thread, so it needs `Dispatchers.IO` or a bounded view|Native calls and class initialisation still pin the carrier, per the sheet's measurements|
|Where it does not help|CPU-bound work: `Dispatchers.Default` is sized to the cores and computation never suspends|CPU-bound work, measured at a ratio of about 1 against a platform pool|

The honest summary is that the two answer different questions. Virtual threads make the existing blocking style scale without rewriting it. Coroutines make concurrency structured, cancellable and visible in the types, at the price of marking functions and choosing dispatchers. On the JVM you can have both, and the mission's own framing holds: know which question you are answering.

## Practice

1. ▢ `val job = launch { while (true) { computeChunk() } }`, where `computeChunk` is pure computation. Then `job.cancel()` runs. Predict what happens, and name three ways to fix it.

<details markdown="1"><summary>Hint</summary>

Cancellation is delivered at a particular kind of place in the code. Find one in this loop.

</details>

<details markdown="1"><summary>Check</summary>

Nothing happens: the loop keeps running. Cancellation is cooperative, and the coroutine only throws `CancellationException` when it next checks, which happens at a suspension point or an explicit check. This loop has neither, so `cancel()` sets the state and the work continues, possibly forever. The three fixes are `yield()` in the loop, which also lets other coroutines use the thread; `ensureActive()`, which throws without suspending; and `while (isActive)`, which lets the loop finish tidily instead. `yield()` is the default choice because a loop that never suspends is also monopolising its thread.

</details>

2. ▢ Inside `scope.launch { }`, code reads `val names = withContext(Dispatchers.IO) { readLines(file) }` and then `updateUi(names)`. The scope is cancelled while the read is in progress, and the read itself does not react to cancellation. Does `updateUi` run?

<details markdown="1"><summary>Check</summary>

No. The blocking read finishes, because it does not cooperate, but `withContext` checks for cancellation before entering its block and after it returns, so it does not return into the cancelled coroutine: it resumes with a `CancellationException` instead. This is prompt cancellation, and it is the reason it exists. A cancelled coroutine resumes with the exception rather than with a value even when the value is sitting there ready, precisely so that the next line, which touches something that may already be disposed, never runs.

</details>

3. ▢ A coroutine does its cleanup in `finally { connection.closeAndFlush() }`, where that function suspends. On cancellation, the cleanup never completes. Why, and what is the fix, including one thing not to do with it?

<details markdown="1"><summary>Hint</summary>

The `finally` block is running inside an already-cancelled coroutine, and the cleanup wants to suspend.

</details>

<details markdown="1"><summary>Check</summary>

The coroutine is already cancelled, so the first suspension point inside the `finally` throws `CancellationException` immediately and the cleanup abandons halfway. Wrap the part that must finish in `withContext(NonCancellable) { ... }`, which is exactly what that context element is for. What not to do: pass `NonCancellable` to `launch` or `async`. The documentation warns against it directly, because doing so breaks the parent-child relationship and so disrupts structured concurrency. It is a tool for a block of cleanup, not for a coroutine.

</details>

4. ▢ `coroutineScope { launch { throw IOException() }; launch { longRunningWork() } }`. Predict what happens to the second coroutine, and then say what changes if `coroutineScope` becomes `supervisorScope`.

<details markdown="1"><summary>Check</summary>

The `IOException` is not a `CancellationException`, the failing child was not created by a lexical builder, and the parent's `Job` is an ordinary one, so all three propagation conditions hold: the failure fails the parent, and the parent's cancellation then cancels the sibling. `longRunningWork()` is cancelled at its next suspension point, and the exception surfaces out of `coroutineScope`. With `supervisorScope`, condition 3 fails, so the child's failure does not cancel the scope and the sibling keeps running. That is a decision about whether these two pieces of work are one unit that fails together or two independent ones, and answering it is the actual design work.

</details>

5. ▢ Which claim about `CancellationException` is correct?

   - a) A CancellationException from a child fails its parent, exactly like any other exception
   - b) A CancellationException is how cancellation travels, and it does not fail the parent
   - c) A CancellationException is thrown once, at the moment cancel is called on it
   - d) A CancellationException can be caught and swallowed with no effect on the cancellation

<details markdown="1"><summary>Check</summary>

**b)** It is the mechanism cancellation uses, and the first propagation condition explicitly excludes it from failing the parent, which is what keeps a cancelled child from taking down its siblings. (a) misses that exclusion and would make cancellation indistinguishable from failure. (c) has the timing wrong: `cancel()` records the request, and the exception is thrown at the coroutine's next cancellation check, which is why a non-suspending loop never sees it. (d) is wrong in the more dangerous direction: swallowing it means the coroutine carries on past a cancellation request while looking like it completed normally, which is why the documentation's own examples catch it only to log and then rethrow.

</details>

6. ▢ **Stage capstone.** A JVM service handles requests that each make three independent calls to slow HTTP dependencies, then combine the results, and it must abandon the whole request if the client disconnects. Argue for coroutines or for virtual threads. Name what each model gives you here, what each costs, and one thing you would need to know about the codebase before deciding.

<details markdown="1"><summary>Check</summary>

Both models handle the fan-out well, and the cost model is the same shape: three blocking waits that must not hold three real threads.

Coroutines fit the cancellation requirement natively. `coroutineScope` with three `async` calls gives one unit of work whose lifetime is a `Job` tree, so a disconnect is one `cancel()` that propagates to all three and to anything they launched, and the scope will not return until they have finished unwinding. The costs: every function on the path has to be `suspend`, blocking library calls need `Dispatchers.IO` or a bounded view of it, and any non-suspending stretch has to cooperate for the cancellation to arrive at all.

Virtual threads fit the code you already have. Three tasks in the plain blocking style, no signature changes, and existing blocking clients work unchanged, which the Java sheet measured at roughly seventeen times the throughput of a platform pool on blocking work. The cost is that lifetime and cancellation are not part of the thread type, so abandoning the request means either a separate structured-concurrency API or your own bookkeeping, and the sheet's caveats still apply: do not pool them, and native calls and class initialisation still pin a carrier.

What to know before deciding: whether the HTTP client on the path is a suspending client or a blocking one. That single fact decides whether the coroutine version is idiomatic or a `Dispatchers.IO` wrapper around blocking calls, and it usually settles the argument faster than any reasoning about the models.

An answer that only names a winner has not done the work. The done-when for this stage is being able to state what each model gives and costs on the specific workload in front of you.

</details>

## Real-world reps

- [ ] Find a long-running loop inside a coroutine in code you have access to. Decide whether cancellation can actually reach it, and if not, which of `yield`, `ensureActive` or `isActive` belongs there.
- [ ] Find a `finally` or a `use` block on a suspending resource. Work out what happens to that cleanup when the coroutine is cancelled mid-block, and whether it needs `NonCancellable`.
- [ ] Tomorrow: read the Java workspace's concurrency sheet sections Virtual threads and Choosing a model, then pick one concurrent piece of your own work and write the two-paragraph argument from the capstone item for it.

## Going further

- [Docs: "Cancellation and timeouts", Kotlin](https://kotlinlang.org/docs/coroutines-cancellation.html)
- [Docs: "Coroutine exceptions handling", Kotlin](https://kotlinlang.org/docs/exception-handling.html)
- [Concurrency sheet, Java workspace](../../java/reference/concurrency.md)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
