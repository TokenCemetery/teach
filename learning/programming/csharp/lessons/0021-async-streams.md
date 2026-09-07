---
title: "21. Async Streams"
description: "The three interfaces behind await foreach, the attribute that lets a consumer's token reach an async iterator's body, and the stage 4 capstone of predicting an async program"
type: lesson
---

# Lesson 21. Async Streams

**Mission link:** This closes stage 4, whose bar is explaining what `await` does to a method's execution and predicting an asynchronous program's behaviour. Async streams are the last piece because they are where a method can suspend more than once and still be a sequence, and the practice section is the capstone.
**Primary source:** [Docs: "Generate and consume async streams", Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/csharp/asynchronous-programming/generate-consume-asynchronous-stream)
**Prerequisites:** [Lesson 20](0020-cancellation-tokens.md), [Lesson 18](0018-async-and-await.md), [Lesson 5](0005-control-flow.md), [Lesson 4](0004-collections.md)

## Warm-up

1. ▢ What does `foreach` actually require of the thing it iterates?

<details markdown="1"><summary>Check</summary>

Only a public parameterless `GetEnumerator` method, which may even be an extension member, returning a type with a public `Current` property and a public parameterless `MoveNext`. It is a duck-typed contract, not an interface requirement, so a type can be iterable without implementing anything.

</details>

2. ▢ A cancelable delegate notices the request and returns. What is wrong with that?

<details markdown="1"><summary>Check</summary>

The task ends in `RanToCompletion` rather than `Canceled`, so the requester sees success and cannot tell that the work stopped because it asked. Throwing `OperationCanceledException` carrying the token, via `ThrowIfCancellationRequested`, is what makes the cancellation observable.

</details>

3. ▢ What does `await` do to the enclosing method, and to the thread?

<details markdown="1"><summary>Check</summary>

It suspends the enclosing async method and returns control to the caller, without blocking the thread. Hold on to that, because a sequence whose producer suspends in the middle is what this lesson is about.

</details>

## Know this

**Start from the shape being replaced.** The documentation's starter application creates a progress-reporting object and a cancellation token, calls a paged query to retrieve the most recent 250 issues, and then, **after that task has finished, displays the results** ([Generate and consume async streams](https://learn.microsoft.com/en-us/dotnet/csharp/asynchronous-programming/generate-consume-asynchronous-stream)). That is the `Task<IEnumerable<T>>` shape: the method accumulates everything into a collection, and the caller gets the whole set at once or nothing. The token and the progress object are both there to work around that, one to abandon the wait and one to hear about the middle of it.

**Async streams remove the reason for both.** The code generating the sequence can use `yield return` to return elements **in a method declared with the `async` modifier**, and you consume the result with an `await foreach` loop **just as you consume any sequence using a `foreach` loop**. The signature becomes `async IAsyncEnumerable<T>`, the accumulating collection and the trailing `return` statement both disappear, and the body's `yield return` sits inside the same loop that was already fetching pages.

**Three interfaces, and they are the ones you would guess.** The feature depends on three types added in .NET Standard 2.1 and implemented in .NET Core 3.0, behaving in a manner similar to their synchronous counterparts:

|Asynchronous|Synchronous counterpart|
|---|---|
|`IAsyncEnumerable<T>`|`IEnumerable<T>`|
|`IAsyncEnumerator<T>`|`IEnumerator<T>`|
|`IAsyncDisposable`|`IDisposable`|

Lesson 4 made `IEnumerable<T>` the abstraction the workspace leans on and lesson 6 introduced `await using` for `IAsyncDisposable`, so the row that matters is the middle one. The documentation notes that these interfaces use `ValueTask` **for performance reasons**, which is the one place in this stage where a type was chosen for allocation behaviour rather than expressiveness, and lesson 1's struct-versus-class material is what makes that sentence readable.

**`await foreach` is duck-typed too, and the parallel with lesson 5 is exact.** It consumes any type implementing `IAsyncEnumerable<T>`, and each iteration of the loop **can suspend while the next element is retrieved asynchronously**. But it also works with any type that has a public parameterless `GetAsyncEnumerator` method, which may be an extension member, whose return type has a public `Current` property and a public parameterless `MoveNextAsync` returning `Task<bool>`, `ValueTask<bool>`, or **any other awaitable type whose awaiter's `GetResult` method returns a `bool`** ([Iteration statements](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/statements/iteration-statements)).

So the asynchronous loop borrows the synchronous loop's design decision wholesale: a shape, not an interface. Knowing that is what stops you concluding that a type must implement `IAsyncEnumerable<T>` before it can be awaited over.

**What the change actually buys, in the documentation's own comparison.** Running the finished application against the starter one:

- the first page of results is **enumerated as soon as it is available**, with an observable pause as each new page is fetched;
- the `try`/`catch` block **is not needed to handle cancellation**, because **the caller can stop enumerating the collection**;
- progress is clearly reported because results are generated as each page downloads, so **you do not need a callback object to track progress**;
- no collection has to be allocated to store all the results before they are enumerated, and **the caller can determine how to consume the results and whether a storage collection is needed**.

The second and fourth are the interesting ones, because both move a decision from the producer to the consumer. Under the old shape the producer decided when you were allowed to see anything and what container it arrived in; under this one it decides neither. That is also why async streams can read from **never-ending streams** like a stock ticker or a sensor, where `MoveNextAsync` returns the next item as soon as it is available and there is no last element to wait for.

**Cancellation, and the attribute that looks like ceremony.** Async streams support cancellation using **the same protocol as other `async` methods**, which is lesson 20's protocol unchanged: a `CancellationToken` parameter that the body checks. The signature the documentation gives adds one thing:

```csharp
private static async IAsyncEnumerable<JToken> RunPagedQueryAsync(GitHubClient client,
    string queryText, string repoName, [EnumeratorCancellation] CancellationToken cancellationToken = default)
```

`EnumeratorCancellationAttribute` **causes the compiler to generate code for the `IAsyncEnumerator<T>` that makes the token passed to `GetAsyncEnumerator` visible to the body** of the async iterator.

Read that slowly, because it answers a question you would otherwise have to discover. A stream has **two** moments where a token could arrive: when the method is called, producing the `IAsyncEnumerable<T>`, and later when something starts enumerating it. Those can be far apart, and it is the consumer, not the producer's caller, that knows when to stop. Without the attribute the parameter only ever sees the token supplied at the call, and a token handed to the enumeration would have no way into the body. With it, the two paths join.

This is lesson 20's lesson again in a new place. There, the failure was passing the token to the delegate but not to the API that created the task, so a real cancellation was reported as a fault. Here, the failure is a parameter that is never connected to the enumeration that the consumer actually cancels. Both are plumbing, both compile, and both are invisible until someone cancels.

**One default worth knowing.** By default `await foreach` processes stream elements **in the captured context**; `TaskAsyncEnumerableExtensions.ConfigureAwait` is how you disable capturing it. That is the same context-capture question the task-based pattern raises, arriving here in the form of an extension method on the stream rather than on a task.

**Where `yield` is not allowed.** `yield` statements cannot be used in methods with `in`, `ref` or `out` parameters, nor in lambda expressions and anonymous methods ([yield statement](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/statements/yield)). Notice the overlap with lesson 18: an async method already cannot declare `in`, `ref`, `ref readonly` or `out` parameters. An async iterator is subject to both lists at once, which is worth knowing before you try to give one an `out` parameter and read the error as being about the wrong feature. And `yield break` ends the iteration explicitly, though iteration also finishes when control reaches the end of the iterator.

**Closing stage 4.** Four questions now cover most of what an unfamiliar piece of asynchronous C# is doing, and each one is a lesson: what is this task and who started it (17), where does this method suspend and where does control go (18), which of these operations overlap and which were serialised by accident (19), and what happens when someone stops caring about the result (20). Async streams are where the four meet, because a stream is a task-shaped thing that suspends repeatedly, hands control back each time, and can be abandoned by a consumer that simply stops asking.

## Practice

1. ▢ A method is declared `Task<IEnumerable<Order>> GetOrdersAsync(CancellationToken ct)` and fetches results a page at a time into a list. Rewrite the signature as an async stream and say what the caller gains.

<details markdown="1"><summary>Check</summary>

`async IAsyncEnumerable<Order> GetOrdersAsync(...)`, with the list and the `return` gone and a `yield return` inside the paging loop.

What the caller gains is the documentation's own list. The first page is available as soon as it arrives rather than after the last one; no collection is allocated to hold everything before enumeration, and the caller decides whether it wants one; progress needs no callback object, because receiving an element *is* the progress report; and stopping early needs no cancellation handling at the boundary, because the caller can simply stop enumerating.

The deeper change is about who decides. The old signature let the producer choose the container and the moment of delivery. The new one leaves both to the consumer, which is why the same method now serves a caller that wants a list, one that wants the first ten, and one that wants to react to each element as it lands.

</details>

2. ▢ An async iterator takes a `CancellationToken` parameter and checks it in the loop. A consumer writes `await foreach (var x in Stream().WithCancellation(ct))`. Without `[EnumeratorCancellation]`, why might the body never see that token?

<details markdown="1"><summary>Hint</summary>

Count the places a token can enter. The method call is one of them.

</details>

<details markdown="1"><summary>Check</summary>

Because there are two entry points and the parameter is only one of them. Calling the method supplies its arguments and produces an `IAsyncEnumerable<T>`; enumerating it later calls `GetAsyncEnumerator`, and that is where the consumer's token goes. The attribute is what bridges them: it causes the compiler to generate code for the `IAsyncEnumerator<T>` making the token passed to `GetAsyncEnumerator` **visible to the body** of the iterator.

Note the split of knowledge that makes this necessary. The producer's caller knows what it is asking for; only the consumer knows when it has stopped needing more. Since a stream's whole point is that those two moments are far apart, the token has to be able to arrive at the later one.

The symptom of getting it wrong is worse than a compile error: a stream that appears to be cancelable, checks its token diligently, and ignores every cancellation the consumer requests.

</details>

3. ▢ The stage 4 capstone. Read this method and answer all four questions below.

```csharp
public async Task ProcessAsync(IEnumerable<int> ids, CancellationToken ct)
{
    var fetched = new List<string>();
    foreach (int id in ids)
    {
        fetched.Add(await FetchAsync(id, ct));
    }
    await Task.WhenAll(fetched.Select(r => SaveAsync(r, ct)));
}
```

   - a) Which loop is needlessly serial, and which one is fine?
   - b) What is wrong with the argument to `WhenAll`?
   - c) A caller awaits `ProcessAsync` and wants to catch cancellation. What must its `catch` name, and how would that differ had it called `.Wait()`?
   - d) How would an async stream change the method's shape?

<details markdown="1"><summary>Check</summary>

**a)** The `foreach` serialises the fetches. Each `await` suspends the method before the next iteration begins, so `FetchAsync` for the second id is not even called until the first has returned, and the total is the sum of the latencies rather than the maximum. The `WhenAll` is the right shape for the saves. Unless the fetches depend on each other, or a rate limit or ordering constraint applies, this is lesson 19's defect: work serialised for no reason.

**b)** `Select` is deferred, so at the moment `WhenAll` is called no `SaveAsync` has been invoked and there are no tasks. It needs `.ToArray()` or `.ToList()`, which immediately evaluates the query and stores the tasks. A `Select` whose lambda returns a task and which is not immediately materialised is a defect on sight.

**c)** `catch (OperationCanceledException)`, because `await` **rethrows** the exception rather than wrapping it. Had the caller blocked with `.Wait()` it would have joined with the task instead, and joining delivers the failure inside an `AggregateException`, so the same clause would not match. Worth adding from lesson 20: arriving through `Wait` or `WaitAll`, a `TaskCanceledException` indicates **successful cancellation rather than a fault**, so a handler that logs every `AggregateException` as an error will report a clean shutdown as a failure.

**d)** Returning `async IAsyncEnumerable<string>` and yielding each fetched item lets the caller consume results as they arrive, which removes the accumulating list. But notice what it does not fix: consuming a stream with `await foreach` and saving inside the loop is still serial. Streaming changes *when* elements become available; whether the work on them overlaps is still lesson 19's question, and the honest answer here is that fetching wants concurrency and the shape you choose should not disguise that.

The thread through all four: `await` decides where a method suspends, the call decides when work starts, `Select` decides whether it starts at all, and the way you observe a task decides what shape its failure arrives in.

</details>

4. ▢ Which claim about async streams is correct?

   - a) An async iterator returns the whole sequence once its last element arrives
   - b) An async iterator yields elements as they arrive, consumed with await foreach
   - c) await foreach requires the source to implement IAsyncEnumerable and nothing else works
   - d) A cancellation token parameter on an async iterator needs no special attribute

<details markdown="1"><summary>Check</summary>

**b)** `yield return` in a method carrying the `async` modifier, consumed by a loop each iteration of which can suspend while the next element is retrieved. (a) is the `Task<IEnumerable<T>>` shape the feature replaces. (c) forgets that `await foreach` is duck-typed exactly as `foreach` is: a public parameterless `GetAsyncEnumerator`, possibly an extension member, returning a type with `Current` and `MoveNextAsync`. (d) is the plumbing trap, since `[EnumeratorCancellation]` is what makes the token passed to `GetAsyncEnumerator` visible to the iterator's body.

</details>

## Real-world reps

- [ ] Find a method returning `Task<IEnumerable<T>>` or `Task<List<T>>` that builds its result in a loop. Decide whether any caller needs the whole set before it can start, and what a stream would change.
- [ ] Find an `IProgress<T>` parameter or a progress callback alongside an asynchronous method. Ask whether the elements themselves would have been the progress report.
- [ ] Tomorrow: take one asynchronous method you did not write and answer stage 4's four questions about it, in order, out loud.

## Going further

- [Docs: "Generate and consume async streams", Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/csharp/asynchronous-programming/generate-consume-asynchronous-stream)
- [Docs: "Iteration statements", Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/statements/iteration-statements)
- [Docs: "yield statement", Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/statements/yield)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
