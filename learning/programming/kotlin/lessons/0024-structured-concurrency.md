---
title: "24. Structured Concurrency"
description: "The parent and child tree that makes cancellation predictable, why a scope you own is a scope you must cancel, and what GlobalScope actually costs"
type: lesson
---

# Lesson 24. Structured Concurrency

**Mission link:** Reasoning about coroutines means being able to say which coroutine owns which, who waits for whom, and what happens to the rest when one of them is cancelled. That is this lesson.
**Primary source:** [API: "CoroutineScope", kotlinx.coroutines](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/-coroutine-scope/)
**Prerequisites:** [Lesson 23](0023-suspend-functions-and-coroutine-builders.md), [Lesson 7](0007-classes-and-properties.md), [Lesson 22](0022-threads-and-the-memory-model.md)

## Warm-up

1. ▢ What single rule does the compiler enforce about calling a suspending function, and what are the ways to satisfy it?

<details markdown="1"><summary>Check</summary>

A suspending function can only be called from another suspending function. Satisfy it by marking the caller `suspend`, by calling it inside a coroutine builder's block, or, only where non-suspending code has to call in and cannot be changed, with `runBlocking`.

</details>

2. ▢ What does `launch` return, what does `async` return, and what is the relationship between the two types?

<details markdown="1"><summary>Check</summary>

`launch` returns a `Job`, a handle for waiting and cancelling that carries no value. `async` returns a `Deferred`, a light-weight non-blocking future whose result you take with `await()`. `Deferred` is itself a `Job`, so everything you can do to a `Job`, cancelling included, you can do to it.

</details>

3. ▢ In a class, what is the difference between `private val scope = build()` and `private val scope get() = build()`?

<details markdown="1"><summary>Check</summary>

The first has a backing field: `build()` runs once, and every read returns that same object. The second is a custom getter with no backing field at all, so `build()` runs on every single read and each read can hand back a different object. The syntax difference is one keyword and the semantic difference is total.

</details>

## Know this

**The principle.** Coroutines form a tree of parent and child tasks whose lifecycles are linked, where a lifecycle runs from creation to completion, failure, or cancellation ([Coroutines basics](https://kotlinlang.org/docs/coroutines-basics.html)). Two rules come out of that, and between them they are most of what structured concurrency means:

- A parent waits for its children before it finishes. Put precisely, a coroutine cannot reach its final state until all of its children have reached theirs ([CoroutineScope](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/-coroutine-scope/)).
- If a parent fails or is cancelled, all of its children are recursively cancelled. The same holds for a scope: cancel it, explicitly or because its coroutine failed, and every child goes with it.

That is what makes cancellation and error handling predictable rather than a matter of remembering which handles you kept. It is also why a coroutine can only be launched in a `CoroutineScope`: the scope is the thing that defines and manages the lifecycle. A builder called inside another builder's block becomes a child automatically, because that block's receiver is itself a nested scope.

**Two ways to get a scope, and they are not interchangeable.**

The first is lexical: `coroutineScope { }`. It creates the root of a subtree, is the direct parent of what the block launches and the indirect parent of what those launch in turn, and it runs the suspending block and does not return until the block **and everything launched inside it** has completed. This is the default answer, and it buys a guarantee worth naming: a suspending function that fans work out through `coroutineScope` can promise its caller that when it returns, the work is finished. Nothing escapes it.

The second is owned, for when the lifetime is not a block but an object: the `CoroutineScope()` constructor function, stored as a field on the entity whose lifetime it follows. The docs are blunt about what this costs you: the key part of using a custom scope is cancelling it at the end of that lifecycle, with `scope.cancel()`, which cancels everything still running on its behalf ([CoroutineScope](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/-coroutine-scope/)). A scope you own is a scope you must cancel, and the place to do it is the same place you already close everything else the object holds. Such a scope is usually built with a `SupervisorJob`, for reasons that belong to lesson 27.

**The one-word bug the docs warn about in their own example.** Write the field as `private val scope get() = CoroutineScope(...)` instead of `private val scope = CoroutineScope(...)` and you have a custom getter: a fresh scope on every read. Work launched through one read is not in the scope that a later `cancel()` reaches, so the cancellation does nothing and reports nothing, and the coroutines run on past the lifetime they were supposed to end with. Warm-up 3 is this bug, and lesson 7's backing field is the reason it exists.

**`GlobalScope`, and why it is marked delicate.** It is annotated `@DelicateCoroutinesApi`, so using it takes an explicit `@OptIn(DelicateCoroutinesApi::class)`, which is the library telling you to justify it in writing. The pitfall the documentation leads with is that computations can happen when they have no right to or are no longer needed: its example fetches data for a screen the user has already left, then touches a component that may no longer exist ([GlobalScope](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/-global-scope/)). The legitimate case is narrow and specific: a top-level background process that must stay active for the whole duration of the application's lifetime, a statistics logger being the docs' own example.

There is a shape here worth recognising from the JVM side. `GlobalScope.launch` is the coroutine version of handing a task to an executor you never shut down and never kept a handle to: it runs somewhere, for as long as it likes, and nobody owns it. Structured concurrency exists to make that shape hard to write by accident.

**Where failure fits.** A child's failure normally fails its parent with the same exception, which then cancels the siblings, and that propagates up the tree. The exact conditions, the reason a `CancellationException` is treated differently, and the `SupervisorJob` opt-out are lesson 27's material. For now the useful half is the direction of travel: cancellation flows down the tree, and failure flows up it.

## Practice

1. ▢ Predict the order of the three prints: inside `coroutineScope { }`, one `launch` waits two seconds then prints A, another waits one second then prints B, and C is printed on the line after the closing brace.

<details markdown="1"><summary>Check</summary>

B, then A, then C. The two launches run concurrently, so the shorter delay prints first. C comes last and this is the whole point: `coroutineScope` executes its block and does not return until every coroutine launched inside has completed, so the line after it cannot run early. If C printed first, you would be looking at an unstructured scope.

</details>

2. ▢ `suspend fun loadPage(): Page` opens a `coroutineScope`, starts two `async` fetches inside it, and returns a `Page` built from both. Its caller uses the returned `Page` and assumes all the work is over. Is that assumption safe, and what would break it?

<details markdown="1"><summary>Check</summary>

Safe, and by construction rather than by luck. The lexical scope cannot complete until its children have, so by the time `loadPage` returns there is nothing of its still running. What breaks it is launching into a scope that outlives the call: a field-held scope, or `GlobalScope`. Then the function returns while its work continues, and the caller's assumption is wrong in a way nothing in the signature reveals.

</details>

3. ▢ A service holds `private val scope get() = CoroutineScope(SupervisorJob())`, launches background work through it, and calls `scope.cancel()` in `close()`. The work keeps running after `close()`. Why, and what is the fix?

<details markdown="1"><summary>Hint</summary>

Count how many scope objects this class creates over its lifetime.

</details>

<details markdown="1"><summary>Check</summary>

`get() =` makes it a custom getter with no backing field, so every read builds a new scope. The work was launched in one scope object and `close()` cancels a different, freshly created one, which has no children and so does nothing. Nothing fails and nothing is logged. The fix is to delete the `get()`: `private val scope = CoroutineScope(SupervisorJob())`, one object, stored in a backing field, cancelled at the end of the lifetime. The documentation's own example carries a comment warning about exactly this.

</details>

4. ▢ A screen's data is loaded with `GlobalScope.launch { val data = fetch(); component.display(data) }`. Name two separate things that go wrong when the user leaves the screen mid-fetch, and say what should own this work instead.

<details markdown="1"><summary>Check</summary>

First, the fetch continues after nobody needs its result, spending network and CPU on a screen that is gone, and nothing will ever cancel it because nothing owns it. Second, it then calls into a component that may have been destroyed, which in a UI framework can crash the application. Both are the same root cause: the computation's lifetime is not tied to the entity's lifetime. The work belongs in a scope owned by the component, created with the `CoroutineScope()` constructor function, stored as a field, and cancelled when the component is destroyed, which cancels the fetch with it.

</details>

5. ▢ Which claim describes structured concurrency correctly?

    - a) A parent finishes as soon as its own body ends, children continuing
    - b) A parent finishes only once every child has reached a final state
    - c) A parent cancels itself as soon as any child is cancelled early
    - d) A parent and its children have independent lifecycles, linked by dispatchers

<details markdown="1"><summary>Check</summary>

**b)** is the rule, stated in the API documentation as a coroutine not reaching its final state until all its children have reached theirs. (a) describes the unstructured world that `GlobalScope` puts you back in. (c) has the direction wrong: cancellation flows down from parent to children, and a child being cancelled does not take its parent with it, which is precisely why cancellation is distinguished from failure. (d) confuses the two axes: the scope governs lifecycle, the dispatcher governs which threads run the code, and lesson 25 is about the second one.

</details>

## Real-world reps

- [ ] Find a `CoroutineScope` held as a field in code you have access to, in an Android view model, a server component, anything. Follow it to the line that cancels it. If there is no such line, you have found a leak.
- [ ] Take one suspending function in your own work that fans work out concurrently. Decide whether it promises its caller that the work is done when it returns, and whether the scope it uses actually keeps that promise.
- [ ] Tomorrow: search for `GlobalScope` in any Kotlin codebase you can reach. For each hit, decide whether it is the narrow legitimate case, a process that must live as long as the application, or work that belongs to something with a shorter life.

## Going further

- [API: "CoroutineScope", kotlinx.coroutines](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/-coroutine-scope/)
- [API: "GlobalScope", kotlinx.coroutines](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/-global-scope/)
- [Docs: "Coroutines basics", Kotlin](https://kotlinlang.org/docs/coroutines-basics.html)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
