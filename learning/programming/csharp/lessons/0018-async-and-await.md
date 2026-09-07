---
title: "18. async and await"
description: "What await does to the enclosing method, the three places it is forbidden, and why async void breaks the only mechanism a caller has"
type: lesson
---

# Lesson 18. async and await

**Mission link:** This is the mission's own success criterion: write `async`/`await` code and explain what happens to a method's execution at each `await`. The answer is one sentence from the reference, and the rest of the lesson is its consequences.
**Primary source:** [Docs: "await operator", Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/operators/await)
**Prerequisites:** [Lesson 17](0017-the-task-model.md), [Lesson 16](0016-expression-bodied-members.md), [Lesson 14](0014-delegates-and-events.md)

## Warm-up

1. ▢ Is a task a thread? What settles it?

<details markdown="1"><summary>Check</summary>

No. A task represents an asynchronous operation at a higher level of abstraction than a thread, and `TaskCompletionSource<TResult>` produces a task with no delegate at all, wrapping an operation an external component performs. A task is a handle on a completion.

</details>

2. ▢ A task faults and nothing ever waits on it or reads its result. What is the risk?

<details markdown="1"><summary>Check</summary>

The exception is wrapped in an `AggregateException` and delivered to the thread that joins with the task, so if nothing joins, nothing observes it, and the documented behaviour is that unhandled exceptions terminate the process. Reading the task's `Exception` property before garbage collection is what prevents that at finalization.

</details>

3. ▢ Which bodies are legal for a `void` expression-bodied member?

<details markdown="1"><summary>Check</summary>

A statement expression: an assignment, a method invocation, an object creation, an increment or decrement, or an **`await`** expression. That last one is why an expression-bodied asynchronous member is possible, and this lesson is what makes it useful.

</details>

## Know this

**The whole mechanism is one paragraph from the reference, and it is worth reading slowly.** The `await` operator **suspends evaluation of the enclosing async method** until the asynchronous operation represented by its operand completes; when the operation completes, `await` returns its result, if any; **`await` does not block the thread** that evaluates the async method; and **when `await` suspends the enclosing method, control returns to the caller of the method** ([await operator](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/operators/await)).

Read the last two clauses together and the mission's question is answered. The method stops; the thread does not. Control goes back to whoever called the method, which is free to carry on, and the remainder of the async method runs later, when the operation it was waiting for has finished.

**Not every `await` suspends.** Applied to an operand representing an **already completed** operation, `await` returns the result **immediately, without suspending** the enclosing method. So `async` marks a method that *may* yield, not one that does, and an async method whose awaits all happen to complete synchronously runs start to finish like an ordinary method. That is worth knowing before you try to reason about ordering from the presence of the keyword.

**The type of an `await` expression, and what it does with failure.**

|If `t` is|`await t` is|
|---|---|
|`Task<TResult>` or `ValueTask<TResult>`|`TResult`|
|`Task` or `ValueTask`|`void`|

And in both cases, **if `t` throws an exception, `await t` rethrows it**. Set that against lesson 17: joining a task through `Wait` or `Result` hands you an `AggregateException` wrapping the failure, while `await` rethrows the exception itself. The same fault therefore arrives in two different shapes depending on how you observed it, and `await` is the one that delivers the exception your `catch` block was actually written for.

**Three places `await` is forbidden**, and the second is a design statement rather than a restriction. You may use `await` only inside a method, lambda expression or anonymous method carrying the `async` modifier, and within an async method you may not use it:

- in the body of a **synchronous local function**,
- inside the block of a **`lock` statement**,
- in an **`unsafe`** context.

The `lock` prohibition is the interesting one: you cannot hold a monitor across a suspension. Since the method may resume on a different thread and arbitrary other work may run in between, a lock held across an `await` would be a lock whose owner has walked away. The language refuses rather than letting you find out.

The operand is usually a `Task`, `Task<TResult>`, `ValueTask` or `ValueTask<TResult>`, but any **awaitable** expression works, which is the same extensibility that lets `async` methods return custom task-like types.

**Return types, and the one that breaks the contract.** An async method may return `Task`, `Task<TResult>`, `void`, or any type with an accessible `GetAwaiter` method, of which `ValueTask<TResult>` is one ([async](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/keywords/async)). Use `Task<TResult>` when the method returns a value, and `Task` when it does not: the call still returns a `Task`, and an `await` of that task evaluates to `void`.

Then the guidance on `void`, which is the most consequential sentence in the lesson: generally **avoid `async void` for anything other than event handlers**, because **callers cannot `await` those methods** and must implement some other mechanism to report successful completion or error conditions.

Put that beside the two facts you already have. Lesson 14 established that an event handler's signature is fixed by its delegate type, which is why the exception exists at all. Lesson 17 established that a faulted task nobody observes is an unhandled exception waiting for a finalizer. An `async void` method returns nothing to observe, so its failure has nowhere to go by construction. That is the whole argument, and it does not need embellishing.

Two smaller rules worth having. An async method cannot declare `in`, `ref`, `ref readonly` or `out` parameters, nor return by reference, though it may call methods that do. And `Main` may return `Task` or `Task<int>`, which makes it async so that `await` works in its body; before that was possible, the way to make `Main` wait was reading `Result` or calling `Wait`, which is exactly the blocking pattern lesson 17 taught you to be suspicious of.

**One convention.** Asynchronous methods are named with an `Async` suffix, as in `GetStringAsync` and `GetUrlContentLengthAsync`. It is a convention rather than a rule, and following it is how a caller knows there is a task to await before reading the signature.

## Practice

1. ▢ In this method, say what has already run when the `await` suspends it, and where control goes:

```csharp
public async Task<int> GetUrlContentLengthAsync()
{
    using var client = new HttpClient();
    Task<string> getStringTask = client.GetStringAsync("https://example.com");
    DoIndependentWork();
    string contents = await getStringTask;
    return contents.Length;
}
```

<details markdown="1"><summary>Check</summary>

Everything above the `await` has run: the client was created, `GetStringAsync` was **called** and returned a task representing its ongoing work, and `DoIndependentWork` ran to completion synchronously. That is the point of assigning the task to a variable rather than awaiting it immediately, since the method can do work that does not depend on the result.

At the `await`, if the task has not completed, the method suspends and **control returns to the caller**, which continues with whatever it does next. The thread is not blocked. When the string arrives, the remainder of the method runs, computes the length, and completes the `Task<int>` this method returned to its own caller.

</details>

2. ▢ Does every `await` suspend the enclosing method?

<details markdown="1"><summary>Check</summary>

No. When the operand represents an operation that has **already completed**, `await` returns the result immediately without suspending. So an async method all of whose awaits complete synchronously never yields at all, and runs like an ordinary method.

The consequence for reasoning about code: the presence of `async` tells you a method *may* suspend, not that it will, and you cannot infer ordering or thread behaviour from the keyword alone. It also explains why adding a cache in front of an asynchronous call can change a program's observable ordering without any code around it changing.

</details>

3. ▢ The same task faults. One caller writes `await t;` and another writes `t.Wait();`. What does each one catch?

<details markdown="1"><summary>Hint</summary>

One of these two joins with the task in lesson 17's sense. The other is this lesson's operator.

</details>

<details markdown="1"><summary>Check</summary>

`await t` **rethrows the exception itself**, so a `catch (IOException)` around it works as written. `t.Wait()` joins with the task, and joining delivers the failure wrapped in an `AggregateException`, so the same `catch (IOException)` does not match and the handler has to unwrap.

That is a real source of confusion when the two styles are mixed in one codebase, and it is worth stating as a rule: the exception's shape depends on how you observed the task, not on what went wrong. Preferring `await` is not only about not blocking a thread; it is also the option that preserves the exception type your error handling was written against.

</details>

4. ▢ Why is `async void` a trap, and what is the one case it exists for?

<details markdown="1"><summary>Check</summary>

Because a caller has nothing to await. The documentation's own reason is that callers cannot `await` such methods and must implement a different mechanism to report successful completion or error conditions, so both the completion and the failure of the operation become unobservable at the call site. Combined with lesson 17, an exception in it has nowhere to be delivered, which is the unhandled-exception path rather than a caught one.

The case it exists for is an **event handler**, whose signature is fixed by its delegate type, as lesson 14 established, and therefore cannot return a task. There the trap is unavoidable and the mitigation is to catch inside the handler, since nothing outside it can.

The review habit: `async void` on anything that is not an event handler is worth a comment every time, and the fix is usually as simple as returning `Task` and having the caller await it.

</details>

5. ▢ Which claim about `await` is correct?

   - a) An await blocks the current thread until the awaited operation finishes running
   - b) An await suspends the enclosing method and returns control to its caller
   - c) An await always suspends, even when the awaited operation has already completed
   - d) An await starts the awaited operation, which does not begin until awaited

<details markdown="1"><summary>Check</summary>

**b)** The reference says both halves: `await` suspends the enclosing async method and does not block the thread, and when it suspends, control returns to the caller. (a) is the model the whole feature exists to avoid. (c) misses that an already-completed operation returns immediately without suspension.

(d) deserves a longer answer, because it is the mistake lesson 13 makes tempting. A LINQ query really is cold: nothing runs until you iterate. A task is **not**: by the time you hold one, the operation it represents is already under way, which is precisely why the method in practice item 1 can call `GetStringAsync` and then do other work. Tasks are hot, queries are cold, and the two are easy to conflate because both are values representing something that has not finished yet.

</details>

## Real-world reps

- [ ] Search C# you have access to for `async void`. For each hit, decide whether it is an event handler, and if it is not, what a caller currently does about failure.
- [ ] Find an async method and mark the point where control returns to its caller. Then check what the caller does immediately afterwards, and whether it depends on the result.
- [ ] Tomorrow: find a `catch` clause around an awaited call and around a `.Result` call in the same codebase. Confirm the exception types they catch are the ones each one can actually receive.

## Going further

- [Docs: "await operator", Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/operators/await)
- [Docs: "async keyword", Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/keywords/async)
- [Docs: "Task asynchronous programming model", Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/csharp/asynchronous-programming/task-asynchronous-programming-model)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
