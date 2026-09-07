---
title: "20. Cancellation Tokens"
description: "Cooperative cancellation with one requester and many listeners, why returning early reports success, and the token comparison that decides whether a task says it was canceled"
type: lesson
---

# Lesson 20. Cancellation Tokens

**Mission link:** Predicting what an asynchronous program does includes predicting what it does when someone stops caring about the answer. Cancellation in .NET is cooperative, which means the answer depends on code you write rather than on a mechanism you invoke.
**Primary source:** [Docs: "Cancellation in Managed Threads", Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/standard/threading/cancellation-in-managed-threads)
**Prerequisites:** [Lesson 19](0019-task-composition.md), [Lesson 17](0017-the-task-model.md)

## Warm-up

1. ▢ Why does `await A(); await B();` take twice as long as starting both and awaiting afterwards?

<details markdown="1"><summary>Check</summary>

Because the first `await` suspends the method before the second call has been reached, so `B` does not start until `A` finishes. Starting both first puts them in flight together. It is about when the call happens, not about threads.

</details>

2. ▢ What is wrong with `await Task.WhenAll(ids.Select(id => GetAsync(id)));`?

<details markdown="1"><summary>Check</summary>

`Select` is deferred, so at the moment `WhenAll` is called no tasks exist and no call has been made. `ToArray` or `ToList` immediately evaluates the query and stores the tasks, which is what starts the work.

</details>

3. ▢ What does a task's `Status` tell you?

<details markdown="1"><summary>Check</summary>

Whether it has started running, ran to completion, was canceled, or threw an exception, as a `TaskStatus` value, readable at any point in the task's lifetime. This lesson is about the difference between two of those states.

</details>

## Know this

**One model, one requester, many listeners.** .NET uses a **unified model for cooperative cancellation** of asynchronous or long-running synchronous operations, built on a lightweight object called a **cancellation token** ([Cancellation in Managed Threads](https://learn.microsoft.com/en-us/dotnet/standard/threading/cancellation-in-managed-threads)). The object starting the cancelable work passes the token to each operation, those operations may pass copies onward, and later the creator can use it to ask them all to stop.

Two clauses of that model do the real work. **Only the requesting object can issue the cancellation request**, and **each listener is responsible for noticing the request and responding in an appropriate and timely manner**. So a token is not a switch that stops anything; it is a message, and whether it is honoured is a property of the code that received it.

The pattern is four steps: create a `CancellationTokenSource`, pass its `Token` to everything that should listen, give each listener a way to respond, and call `Cancel` on the source when you want them to stop.

**Cancellation is about operations, not objects, and it is not an abort.** A request means the operation should stop **as soon as possible after any required cleanup has been performed**, and one token should refer to one cancelable operation. If you need to cancel an *object* rather than an operation, you build that on top, using `CancellationToken.Register`.

**And it is one-way.** Once a token's `IsCancellationRequested` is `true`, **it cannot be reset to `false`**, so tokens cannot be reused after they have been canceled. A token is a latch, and a source that has been cancelled is finished: the next operation needs a new one.

**Two ways for a listener to stop, and they are not equivalent.** In the task classes, cancellation is a cooperation between the user delegate and the requesting code, and the delegate can terminate in either of two ways ([Task cancellation](https://learn.microsoft.com/en-us/dotnet/standard/parallel-programming/task-cancellation)):

|How the delegate stops|The task's resulting state|
|---|---|
|**Returning** from the delegate|`RanToCompletion`, **not** `Canceled`|
|**Throwing `OperationCanceledException`**, passing it the token on which cancellation was requested, preferably via `ThrowIfCancellationRequested`|`Canceled`, which the calling code can use to verify that the task responded to its request|

That table is the sharpest point in the lesson. Returning early is often enough for the operation itself, but it reports **success**, so the requester cannot distinguish "finished the work" from "stopped because I asked". Throwing is what makes the cancellation observable, which is why the documentation calls `ThrowIfCancellationRequested` the preferred way.

The idiomatic body follows from that: call `ThrowIfCancellationRequested` on entry, in case cancellation was requested before you even started; poll `IsCancellationRequested` where you have cleanup to do before throwing; and throw at the end of that cleanup.

**The token comparison, which explains an instruction that otherwise looks redundant.** When a task observes an `OperationCanceledException` thrown by the user code, it **compares the exception's token to its own associated token**, the one passed to the API that created the task. If they are the same token and its `IsCancellationRequested` is `true`, the task treats this as acknowledging cancellation and transitions to `Canceled`.

So passing the token both **into** the delegate and **to** `Task.Run` or `StartNew` is not duplication. The copy inside the delegate is what lets your code notice the request; the copy given to the task is what lets the task recognise the resulting exception as a cancellation rather than a failure. Omit the second and a correctly cancelled operation is reported as a fault.

On the joining side, waiting on a cancelled task through `Wait` or `WaitAll` produces a `TaskCanceledException` inside an `AggregateException`, and the documentation is careful to say this **indicates successful cancellation rather than a faulty situation**. Read alongside lessons 17 and 18: the shape of what you receive still depends on how you observed the task, and now the *meaning* does too.

**When a listener cannot poll.** Some operations block in a way that prevents checking the token in a timely manner. For those, register a callback that unblocks the operation when cancellation is requested. `Register` returns a `CancellationTokenRegistration`, and the documentation's example uses it to cancel pending HTTP requests from inside a token callback.

**One forward pointer.** A `CancellationToken` parameter is the most-threaded parameter in a modern C# service: it arrives at the boundary and is passed down through every layer that might take time. Stage 6 will build that, and the argument to have ready now is that a method with no way to be cancelled has made a decision on its caller's behalf rather than declined a feature.

## Practice

1. ▢ Two implementations of the same cancelable loop: one checks `IsCancellationRequested` and `return`s, the other calls `ThrowIfCancellationRequested`. What does the requester see in each case?

<details markdown="1"><summary>Check</summary>

The returning version leaves the task in `RanToCompletion`, so the requester sees a task that **succeeded**. The operation did stop, but nothing distinguishes that from having finished the work, and code awaiting the task carries on as though the result were complete.

The throwing version leaves the task in `Canceled`, which the calling code can use to verify that the task responded to its cancellation request.

The consequence is not stylistic. A pipeline that treats a cancelled step as a successful one will happily write a partial result, report success to its own caller, or advance a cursor past work that never happened. If cancellation means anything to your callers, the delegate has to throw.

</details>

2. ▢ A method passes its `CancellationToken` into the delegate it gives `Task.Run` but does not pass the token to `Task.Run` itself. Cancellation is requested, the delegate throws through `ThrowIfCancellationRequested`, and the task ends up `Faulted` rather than `Canceled`. Why?

<details markdown="1"><summary>Hint</summary>

The task performs a comparison when it sees that exception. Ask what it compares against.

</details>

<details markdown="1"><summary>Check</summary>

Because the task compares the exception's token against **its own associated token**, the one passed to the API that created it, and there is not one. Without a matching token the task cannot conclude that the exception acknowledges *its* cancellation, so the `OperationCanceledException` is treated as an ordinary failure.

That is why the token appears twice in the idiomatic call: once inside the delegate, so your code can notice the request, and once as an argument to `Task.Run` or `StartNew`, so the task can recognise the resulting exception as cancellation. The symptom of getting it wrong is a log full of faults for operations that were cancelled on purpose, which is the kind of noise that trains a team to ignore its own error reporting.

</details>

3. ▢ An operation completes, its `CancellationTokenSource` was cancelled, and the next request arrives. Can you reuse the source and its token?

<details markdown="1"><summary>Check</summary>

No. Once `IsCancellationRequested` is `true` it cannot be reset to `false`, so a token cannot be reused after cancellation, and any listener handed it would see a request that had already happened and stop immediately.

The design rule the documentation gives is the useful form of this: one token should refer to **one cancelable operation**. So a token source belongs to the lifetime of the operation, not to the object performing it, and a long-lived component that cancels work needs a new source per unit of work rather than a field it cancels once.

</details>

4. ▢ A listener spends its time inside a call that blocks and cannot check the token. What is the documented mechanism?

<details markdown="1"><summary>Check</summary>

Register a callback with `CancellationToken.Register`, which returns a `CancellationTokenRegistration`. The callback runs when cancellation is requested and its job is to **unblock** the operation, as in the documentation's example, where the callback cancels the pending HTTP requests so the blocked call returns.

Worth noticing what this does not change: the model is still cooperative. The callback is code you wrote, doing something the blocked API supports, and if the blocked operation offers no way to be interrupted then no token can help. Cancellation is a conversation, and both sides have to be able to speak.

</details>

5. ▢ Which claim about cancellation in .NET is correct?

    - a) Cancellation aborts the operation immediately, so cleanup code might not run
    - b) Cancellation is a request; the listener must notice it and stop cooperatively
    - c) Cancellation is reversible, so a token can be reset and reused later
    - d) Cancellation is issued by any holder of the token, including the listeners

<details markdown="1"><summary>Check</summary>

**b)** The model is cooperative: only the requester issues the request, and each listener is responsible for noticing it and responding appropriately and in a timely manner. (a) inverts the design, since a request means stop as soon as possible **after any required cleanup**. (c) is contradicted directly: `IsCancellationRequested` cannot be reset and tokens cannot be reused after cancellation. (d) confuses the token with its source, and the distinction matters, because handing out tokens is safe precisely because a holder cannot cancel with one.

</details>

## Real-world reps

- [ ] Find an asynchronous method in C# you have access to that takes no `CancellationToken`. Decide whether it can take time, and what a caller who no longer needs the result can currently do.
- [ ] Find a cancelable loop and check how it stops. If it returns rather than throwing, work out whether any caller distinguishes cancellation from completion.
- [ ] Tomorrow: find a `Task.Run` whose delegate uses a token, and check whether the same token was also passed to `Task.Run`. Note what the task's status would be on cancellation.

## Going further

- [Docs: "Cancellation in Managed Threads", Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/standard/threading/cancellation-in-managed-threads)
- [Docs: "Task cancellation", Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/standard/parallel-programming/task-cancellation)
- [Docs: "Task-based asynchronous programming", Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/standard/parallel-programming/task-based-asynchronous-programming)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
