---
title: "17. The Task Model"
description: "A task as an asynchronous operation rather than a thread, the four ways one comes into existence, and the AggregateException that can terminate a process you thought had finished"
type: lesson
---

# Lesson 17. The Task Model

**Mission link:** Stage 4 opens, and the mission asks you to explain what happens to a method's execution at each `await`. That explanation is impossible until you know what the thing being awaited actually is, so this lesson is `Task` and nothing about the keywords.
**Primary source:** [Docs: "Task-based asynchronous programming", Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/standard/parallel-programming/task-based-asynchronous-programming)
**Prerequisites:** [Lesson 16](0016-expression-bodied-members.md), [Lesson 14](0014-delegates-and-events.md), [Lesson 13](0013-linq.md)

## Warm-up

1. ▢ Why does `void Log() => 42;` not compile?

<details markdown="1"><summary>Check</summary>

A `void` member's expression body must be a **statement expression**: an assignment, invocation, object creation, increment or decrement, or `await`. A literal computes a value with nowhere to put it, which is not a statement.

</details>

2. ▢ What is a delegate, in one sentence?

<details markdown="1"><summary>Check</summary>

A type that represents references to methods with a particular parameter list and return type, instantiated from a method name or a lambda, and invoked to call the method it wraps. Note that for a delegate, unlike for overloading, the signature includes the return type.

</details>

3. ▢ A LINQ query is stored in a variable. What does the variable hold?

<details markdown="1"><summary>Check</summary>

The query, not the results. It is a question rather than an answer, and nothing executes until it is iterated. Hold that shape in mind, because a task is the same kind of thing pointed at time rather than at data.

</details>

## Know this

**A task represents an asynchronous operation.** The documentation's own comparison is the right starting point: a task resembles a thread or a thread-pool work item, but **at a higher level of abstraction** ([Task-based asynchronous programming](https://learn.microsoft.com/en-us/dotnet/standard/parallel-programming/task-based-asynchronous-programming)). `Task` is the form with no result; `Task<TResult>` inherits from it and carries one.

The phrasing from the TAP walkthrough is the one worth memorising, because it contains both halves of the idea: a task represents the **ongoing process** of a call, with a **commitment to produce a value** when the work is complete. That is why holding a task and not yet asking for its value lets the caller carry on with work that does not depend on it.

**A task is not a thread, and this is the point of the whole model.** Tasks are queued to the `ThreadPool`, whose algorithms determine and adjust the number of threads and load-balance to maximise throughput, which makes tasks relatively lightweight and means you can create many of them. Two benefits are claimed and both matter: more efficient and scalable use of resources, and **more programmatic control** than a thread or work item gives you, in the form of waiting, cancellation, continuations, robust exception handling, detailed status and custom scheduling. That is why the library is described as the preferred API for asynchronous and parallel code in .NET.

And the strongest evidence that a task is not a piece of running code: a task need not have a delegate at all. `TaskCompletionSource<TResult>` wraps an operation performed by an **external component** in a task, gaining exception propagation and continuations for something your code is not executing. So a task is a **handle on a completion**, and sometimes there is no thread anywhere waiting for it. That is the fact that makes asynchronous I/O comprehensible rather than magical.

**The status is inspectable at any time.** The task object handles the infrastructure and exposes members usable from the calling thread throughout the task's lifetime, and its `Status` property, a `TaskStatus`, tells you whether it has started running, ran to completion, was canceled, or has thrown an exception.

**Four ways a task comes into existence.**

|Written|When to reach for it|
|---|---|
|`Task.Run(...)`|The ordinary case: run this delegate on the thread pool|
|`Task.Factory.StartNew(...)`|When creation and scheduling need not be separated and you want extra creation options or a specific scheduler, or need to pass state retrievable through `AsyncState`|
|`TaskCompletionSource<TResult>`|**No delegate**: wrap an operation an external component performs, so that it gains task semantics|
|`TaskFactory.FromAsync`|Wrapping an older Begin/End style asynchronous API|

Note that in the first two the thing you supply is a **user delegate**, expressed as a named delegate, an anonymous method, or a lambda. That is lesson 14's type arriving with a job.

**Three ways to observe one, and only one of them is the good one.**

- **Blocking**: `Wait`, `WaitAll`, `WaitAny`, and reading `Result`. These stop the calling thread until the task finishes. They exist for real reasons, including a console application that would otherwise terminate before its tasks complete, but each is a thread doing nothing.
- **Continuations**: `ContinueWith`, which starts a task when its **antecedent** finishes, passing the continuation a reference to the antecedent so it can inspect the status or take the `Result`. This is callback composition, and it is what the next lesson's keyword replaces.
- **Asynchronous composition**: `Task.WhenAll` and `Task.WhenAny`, which wait without blocking. `WhenAny` earns its own list of uses: redundant operations, where you take the first to finish and cancel the rest; interleaved operations, processing each result as it arrives; throttled operations, limiting concurrency; and expired operations, choosing between work and a timeout.

**Now the hazard, and it is a good one.** When a task throws, the exceptions are wrapped in an `AggregateException`, and that exception is propagated to the thread that **joins** with the task, typically the one waiting for it or reading its `Result`. Which raises the question of what happens when nobody joins.

The answer is in the documentation and it is not comfortable: this behaviour enforces the policy that unhandled exceptions terminate the process, and a joining thread can prevent that by accessing the task's `Exception` property **before the task is garbage-collected**. So a faulted task that nothing ever observed is not a silent no-op; it is an unhandled exception waiting for a finalizer. Fire-and-forget is not free, and this is the mechanism behind that advice.

**On Java, briefly.** `Future` and `CompletableFuture` are the nearest equivalents, and the arc's real comparison, against virtual threads, belongs to stage 7. The shape worth noting now is the same one this lesson has been making: a task is a handle on an operation rather than a thread, so asking how many threads your asynchronous code uses is usually the wrong question.

## Practice

1. ▢ Is a task a thread? Use `TaskCompletionSource<TResult>` in your answer.

<details markdown="1"><summary>Check</summary>

No. A task represents an asynchronous operation at a higher level of abstraction than a thread, and tasks are queued to the thread pool rather than being threads themselves, which is what makes them light enough to create in quantity.

`TaskCompletionSource<TResult>` settles it. It produces a task with **no delegate**, wrapping an operation carried out by an external component, so the task exists as a handle on someone else's completion with no code of yours running and possibly no thread involved at all. Once you see that, asynchronous I/O stops being mysterious: the task is not work in progress on a thread, it is a promise that something will finish.

</details>

2. ▢ A method starts a task, ignores the returned `Task`, and the task throws. Nobody waits on it or reads its result. What can happen, and what would prevent it?

<details markdown="1"><summary>Hint</summary>

Ask which thread the exception is delivered to, and what happens when no thread ever joins.

</details>

<details markdown="1"><summary>Check</summary>

The exception is wrapped in an `AggregateException` and propagated to the thread that joins with the task, and if no thread ever joins, nothing observes it. The documentation is explicit that this behaviour enforces the policy that unhandled exceptions terminate the process, and that accessing the task's `Exception` property **before the task is garbage-collected** is what prevents the unhandled exception from triggering that behaviour when the object is finalized.

So the failure mode is a process that dies later, at a finalization, for a task that failed somewhere the code was not looking. What prevents it is observing the outcome: join the task, or read `Exception`, or in modern code await it and handle the failure where it happened.

The general lesson is that ignoring a returned task is not the same as not caring about the operation. The type is telling you there is an outcome, and discarding it discards the error handling with it.

</details>

3. ▢ `Task.WaitAll(tasks)` and `await Task.WhenAll(tasks)` both wait for a set of tasks. What is the difference that matters?

<details markdown="1"><summary>Check</summary>

`WaitAll` **blocks** the calling thread until every task finishes; `WhenAll` waits **asynchronously**, returning a task that completes when they all do. So the first spends a thread on waiting and the second does not.

Both have a place. A console application whose `Main` would otherwise return before its work finished has a genuine reason to block, which is one of the documented reasons for waiting at all. In a server, a blocked thread is capacity taken out of service to do nothing, which is the same argument the whole model rests on.

The reading habit: `Wait`, `WaitAll`, `WaitAny` and `Result` are the blocking family, and seeing one in code that is otherwise asynchronous is worth a question in review.

</details>

4. ▢ You need to fetch the same data from three mirrors and use whichever answers first, cancelling the rest. Which documented `WhenAny` scenario is that, and what would the other three be?

<details markdown="1"><summary>Check</summary>

**Redundant operations**: perform the operation several ways, take the one that finishes first, and cancel the remainder. That is the case named for exactly this.

The other three, worth recognising because they look similar and are not: **interleaved operations**, where every operation must finish but you process each result as it arrives; **throttled operations**, where you extend that to limit how many run concurrently; and **expired operations**, where you race the real work against a timeout and take whichever comes first.

Naming which one you are doing is worth the effort, because the four differ in whether the losers get cancelled, whether all results are needed, and whether the second completion is even interesting.

</details>

5. ▢ Which claim about a `Task` is correct?

   - a) A task is a thread, scheduled directly by the operating system scheduler
   - b) A task represents an asynchronous operation, and need not be running code
   - c) A task always occupies a thread-pool thread from creation until it completes
   - d) A task cannot exist without a delegate supplying the code it runs

<details markdown="1"><summary>Check</summary>

**b)** A task represents an asynchronous operation at a higher level of abstraction than a thread, and `TaskCompletionSource<TResult>` produces one with no delegate at all. (a) confuses the abstraction with the mechanism; tasks are queued to the thread pool rather than being threads. (c) is the model that makes asynchronous I/O look wasteful, and it is wrong for exactly the operations the model exists to serve. (d) is contradicted by the documented "tasks without delegates" case, and believing it makes wrapping an external operation look impossible.

</details>

## Real-world reps

- [ ] Search C# you have access to for `.Result` and `.Wait(`. For each, decide whether the calling thread had a good reason to stop, or whether it is a blocking call in otherwise asynchronous code.
- [ ] Find a place where a returned `Task` is discarded. Work out what would observe a failure in it, and what happens if nothing does.
- [ ] Tomorrow: find an operation in your own work performed by an external component, a callback, a message arriving, a device signalling. Sketch how `TaskCompletionSource` would turn it into something the rest of your code can await.

## Going further

- [Docs: "Task-based asynchronous programming", Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/standard/parallel-programming/task-based-asynchronous-programming)
- [Docs: "Task asynchronous programming model", Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/csharp/asynchronous-programming/task-asynchronous-programming-model)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
