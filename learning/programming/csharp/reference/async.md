---
title: Async
description: The Task model, what await actually does, composing tasks correctly, cooperative cancellation, and async streams
type: reference
---

# Async

Lookup sheet for stage 4: predicting what an asynchronous C# program does.

## A task is not a thread

A `Task` represents an asynchronous operation "at a higher level of abstraction" than a thread: tasks are queued to the thread pool, and a task can exist with **no delegate at all** (`TaskCompletionSource<TResult>` wraps an external component's completion). A task is a handle on a completion, not a piece of running code.

| Created with | When |
|---|---|
| `Task.Run(...)` | The ordinary case |
| `Task.Factory.StartNew(...)` | Extra creation options, a specific scheduler, or state via `AsyncState` |
| `TaskCompletionSource<TResult>` | No delegate: wrap an operation an external component performs |
| `TaskFactory.FromAsync` | Wrapping an older Begin/End API |

| Observing it | How |
|---|---|
| Blocking | `Wait`, `WaitAll`, `WaitAny`, `.Result`: stops the calling thread |
| Continuations | `ContinueWith`: starts a new task when the antecedent finishes (callback composition, replaced by `await`) |
| Async composition | `Task.WhenAll`, `Task.WhenAny`: wait without blocking |

**The unobserved-fault hazard**: a faulted task's exception is wrapped in `AggregateException` and delivered to whatever thread joins it. If nothing ever joins, the exception is unhandled at finalization and **terminates the process**, unless something reads the task's `Exception` property first. Fire-and-forget is not free.

## async/await

`await` suspends the enclosing async method until its operand completes, **does not block the thread**, and returns control to the method's caller when it suspends. Not every `await` suspends: an already-completed operand returns immediately, so `async` marks a method that *may* yield, not one that does.

| `await t` where `t` is | Evaluates to | On failure |
|---|---|---|
| `Task<TResult>` / `ValueTask<TResult>` | `TResult` | Rethrows `t`'s exception directly |
| `Task` / `ValueTask` | `void` | Rethrows `t`'s exception directly |

Contrast with joining via `Wait`/`Result`: that delivers `AggregateException`. The same fault arrives in two different shapes depending on how it was observed; `await`'s `catch` clause matches the original exception type.

**`await` is forbidden**: in a synchronous local function's body, inside a `lock` block (you cannot hold a monitor across a suspension), and in an `unsafe` context.

**`async void` is a trap** (fine only for event handlers, whose signature is fixed by their delegate type): a caller has nothing to await, so a fault inside has nowhere to go but the unhandled-exception path.

## Composing tasks: overlap, don't accidentally serialize

Calling an async method **starts the work immediately**; awaiting only observes it. `await A(); await B();` serializes (B doesn't even start until A finishes). Starting both, then awaiting, overlaps them:

```text
serial:     A(0-1s) --await--> B(1-2s)           total ~2s
concurrent: A(0-1s) started; B(0-1s) started; await both   total ~1s
```

**The LINQ-deferred-execution trap**: a task is hot (work is running the moment you hold it); a LINQ query is cold (nothing runs until enumerated). Projecting a sequence into tasks with `.Select(id => GetAsync(id))` produces **no tasks at all** until enumerated:

```csharp
var tasks = userIds.Select(id => GetUserAsync(id)).ToArray();   // ToArray forces the calls now
return await Task.WhenAll(tasks);
```

Without `.ToArray()`/`.ToList()`, `Task.WhenAll(tasks)` sees zero tasks at the call, and re-enumerating a deferred sequence of async calls starts every call again.

**`Task.WhenAny` needs two awaits**: the first yields the completed *task*, not its value or exception; the second awaits that task to get the value (and to surface its exception, per `await`'s rethrow rule). Remove the completed task from the set, or the loop returns it forever.

| Need | Reach for |
|---|---|
| Every result, nothing to do until all arrive | `WhenAll` |
| First answer, cancel the rest | `WhenAny`, redundant operations |
| Every result, processed as each arrives | `WhenAny` in a loop, removing each completed task |
| A concurrency cap | `WhenAny`, throttled: start a new one as each finishes |
| Work or a timeout, whichever first | `WhenAny` against a delay task |

Not every `await` in a loop is a bug: sequential is correct when steps depend on each other, a service imposes ordering/rate limits, or unlimited concurrency would exhaust something scarce.

## Cancellation tokens: cooperative, one requester, many listeners

Only the object holding a `CancellationTokenSource` can request cancellation (`Cancel()`); every listener holding a copy of its `Token` is responsible for **noticing and responding**. A token is one-way: once `IsCancellationRequested` is `true` it can never reset, so a source is scoped to one cancelable operation, not reused.

**How a delegate stops determines what the task reports:**

| Delegate | Task status |
|---|---|
| Returns normally | `RanToCompletion` (**success**, indistinguishable from actually finishing) |
| Throws `OperationCanceledException` carrying the token (`ThrowIfCancellationRequested()`) | `Canceled` |

**The token must be passed twice**: once into the delegate body (so it can notice and throw) and once to `Task.Run`/`StartNew` (so the task compares the thrown exception's token against its own and recognizes it as cancellation rather than a fault). Omit the second and a correctly cancelled operation reports `Faulted`.

Joining a cancelled task via `Wait`/`WaitAll` delivers `TaskCanceledException` inside `AggregateException`; this **indicates successful cancellation, not a fault**, so logging every `AggregateException` as an error reports a clean shutdown as a failure.

For a blocking call that can't poll the token, register a callback with `CancellationToken.Register` to unblock it.

## Async streams

Replace `Task<IEnumerable<T>>` (accumulate everything, then hand it over) with `async IAsyncEnumerable<T>` plus `yield return`, consumed with `await foreach`, each iteration of which can suspend while the next element is fetched.

| Async | Sync counterpart |
|---|---|
| `IAsyncEnumerable<T>` | `IEnumerable<T>` |
| `IAsyncEnumerator<T>` | `IEnumerator<T>` |
| `IAsyncDisposable` | `IDisposable` |

`await foreach` is duck-typed like `foreach`: any type with a public parameterless `GetAsyncEnumerator` (possibly an extension member) returning something with `Current` and `MoveNextAsync` works, no interface required.

What moving to a stream buys: the first element is available as soon as it arrives (not after the last one); no accumulating collection needs allocating; progress needs no separate callback, since receiving an element *is* the progress; the consumer decides when to stop, so no `try`/`catch` is needed just to handle early cancellation. It doesn't automatically fix whether per-element work inside the loop is concurrent, only when elements become visible.

**`[EnumeratorCancellation]` bridges two separate token entry points**: the token passed when the method is *called* (producing the `IAsyncEnumerable<T>`) and the token passed later to `GetAsyncEnumerator` when something actually *enumerates* it (via `.WithCancellation(ct)`). Without the attribute on the token parameter, the iterator body never sees the consumer's cancellation token, even though it compiles and appears to check it correctly.

## Stage 4's four diagnostic questions

1. **Lesson 17**: what is this task, and who started it?
2. **Lesson 18**: where does this method suspend, and where does control go?
3. **Lesson 19**: which operations overlap, and which were serialized by accident?
4. **Lesson 20**: what happens when someone stops caring about the result?

## Related

- [Lesson 17](../lessons/0017-the-task-model.md), [Lesson 18](../lessons/0018-async-and-await.md), [Lesson 19](../lessons/0019-task-composition.md), [Lesson 20](../lessons/0020-cancellation-tokens.md), [Lesson 21](../lessons/0021-async-streams.md)
- [Idiom](idiom.md): LINQ's deferred execution, the mechanism behind the `Task.WhenAll(Select(...))` trap
