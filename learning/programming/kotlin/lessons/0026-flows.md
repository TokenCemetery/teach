---
title: "26. Flows"
description: "A flow as the asynchronous third option after a list and a sequence, what cold actually means for each collector, and the context rule a flow builder enforces at runtime"
type: lesson
---

# Lesson 26. Flows

**Mission link:** The mission names `Flow` alongside coroutines. A suspending function returns one value; a service that streams pages, events or state changes needs many over time, and this is the type for it.
**Primary source:** [Docs: "Flows", Kotlin](https://kotlinlang.org/docs/coroutines-flow.html)
**Prerequisites:** [Lesson 25](0025-coroutine-context-and-dispatchers.md), [Lesson 20](0020-sequences-and-laziness.md), [Lesson 8](0008-data-classes.md)

## Warm-up

1. ▢ What makes a `Sequence` chain actually run, and what is the name for the operations that do not?

<details markdown="1"><summary>Check</summary>

A terminal operation, such as `toList()` or `sum()`. Everything that returns another lazily-produced sequence, `map` and `filter` included, is intermediate and runs nothing by itself. Elements come out only through a terminal operation.

</details>

2. ▢ What does `withContext(other)` do, and what does it cost when `other` names a different dispatcher?

<details markdown="1"><summary>Check</summary>

It may suspend the current coroutine and switch to the new context, provided that context actually differs from the current one. When the difference is the dispatcher, extra dispatches are involved: the block is scheduled on the new dispatcher, and afterwards execution returns to the original one. It is the tool for "run this part elsewhere and come back".

</details>

3. ▢ What does `data class` generate for you, and which properties take part in it?

<details markdown="1"><summary>Check</summary>

`equals()` and `hashCode()`, `toString()`, `componentN()` functions for destructuring, and `copy()`. Only properties declared in the primary constructor participate: one declared in the class body is invisible to all of it, which is the subtle rule worth remembering.

</details>

## Know this

**The third option.** A flow represents a sequential stream of values that can be produced asynchronously. Where a suspending function returns one value, a flow gives you multiple values over time, which is what you want for loading data progressively, reacting to event streams, and modelling subscription-style APIs ([Flows](https://kotlinlang.org/docs/coroutines-flow.html)). Put it beside what stage 4 already taught:

|Type|Produces values|Can suspend while producing|
|---|---|---|
|`List`|All of them, eagerly, before the next step sees any|No|
|`Sequence`|One at a time, lazily, on demand|No|
|`Flow`|One at a time, lazily, and asynchronously|Yes|

**Three roles and a direction.** A flow pipeline has an emitter that produces values, optional intermediate operators that consume values and return another flow, and a collector that consumes them. Values move from the emitter toward the collector, which the documentation calls **upstream** to **downstream**, and an intermediate operator is simply something that collects an upstream flow and returns a new downstream one. That vocabulary is worth adopting, because every operator's documentation is written in it.

**Cold means per collector.** Like sequences, cold flows are lazy: the code block of a cold flow builder does not run until a collector collects it, and **each new collector starts a new execution of the flow**. So a cold flow is not a stream you join. It is a recipe that runs again, from the top, for every collector. Two collectors on a cold flow that reads a database means two reads.

**What a flow can do that a sequence cannot.** Inside a `flow { }` builder you can call suspending functions, which is exactly what a sequence cannot do and the reason this type exists. But there is one restriction, and it fails at runtime rather than at compile time: a `flow()` builder must emit from the same coroutine context it runs in. You cannot start another coroutine that calls `emit()`, and you cannot wrap an `emit()` in `withContext()`. Doing so throws, and the collector never sees a value.

The two sanctioned ways round it are worth knowing together, because the error message sends people to the wrong one. To move the producing work to another context, use `.flowOn()`. To genuinely emit from several coroutines at once, use `channelFlow()`, whose block uses `send()` in place of `emit()`.

**`.flowOn()` is context-preserving, and that phrase is precise.** By default a cold flow runs in the same coroutine context as its collector. `.flowOn()` changes the context of the **upstream** flow only, leaving everything downstream in the caller's context. So in `flow { ... }.map { ... }.flowOn(Dispatchers.IO).collect { ... }`, the builder and the `map` run on IO, while the `collect` lambda runs wherever the caller was. A collector never has its context changed underneath it by an operator, which is what makes the guarantee usable on Android, where the collector may have to be on `Dispatchers.Main`.

**Hot flows, in one paragraph.** A hot flow emits independently of collectors: it keeps emitting when nobody is listening, and multiple collectors share the same emissions instead of each starting a new execution. Its collectors are called **subscribers**. There are two kinds. `SharedFlow` broadcasts values to many subscribers, for events that happen over time such as messages or notifications, and can be configured with a `replay` count so a new subscriber immediately receives that many past emissions. `StateFlow` is a specialised `SharedFlow` that always holds the latest state value, which is what you want for state rather than events. A cold flow can be turned into a hot one with `shareIn`.

The choice between them is the one to get right, and it is not about performance. It is a question about the values: does each collector need its own run of the work, or are they all looking at one stream of things that happen whether or not anyone is looking?

What happens when a flow fails, how `catch` differs from a `try` around the collector, and the `retry` operators are lesson 27's material, along with cancellation.

## Practice

1. ▢ `val pages = flow { println("loading"); emit(1) }` is assigned and nothing else happens. Then, later, two separate `collect` calls run on it. What is printed, and how many times?

<details markdown="1"><summary>Check</summary>

Nothing at all at the point of assignment: a cold flow's builder block does not run until a collector collects it, so creating the flow is free. Then `loading` prints twice, once per `collect`, because each new collector starts a new, independent execution of the flow. If that block had opened a connection or run a query, you would have done it twice. This is the same laziness as a sequence, with the extra consequence that the work is per collector rather than per pipeline.

</details>

2. ▢ Inside a `flow { }` builder, someone writes `withContext(Dispatchers.IO) { emit(value) }` to keep the blocking read off the caller's thread. It compiles, and at runtime the collector never receives anything. Why, and what are the two correct fixes?

<details markdown="1"><summary>Hint</summary>

The rule this breaks is about where `emit` is called from, not about what `emit` does.

</details>

<details markdown="1"><summary>Check</summary>

A `flow()` builder must emit values from the same coroutine context in which it runs, so changing the context around an `emit()` is illegal and throws instead of emitting. The compiler cannot catch it, which is why it reaches production. The fixes: `.flowOn(Dispatchers.IO)` on the flow, which moves the whole upstream to IO without touching where `emit` is called from relative to its builder; or `channelFlow()` with `send()` instead of `emit()`, if the real requirement was to produce values from more than one coroutine. Reaching for `channelFlow` when `flowOn` would do adds a channel and a buffer you did not need.

</details>

3. ▢ A suspending function running under `withContext(Dispatchers.Default)` collects `flow { ... }.map { ... }.flowOn(Dispatchers.IO).collect { ... }`. Say which of the three lambdas runs on which dispatcher.

<details markdown="1"><summary>Check</summary>

The `flow { }` builder and the `map { }` run on `Dispatchers.IO`, because both are upstream of the `.flowOn()` call. The `collect { }` lambda runs on `Dispatchers.Default`, the caller's context, because `.flowOn()` is context-preserving and changes the upstream only. Downstream is never moved by an upstream operator, which is the property that makes it safe to collect on a context you care about, `Dispatchers.Main` being the obvious case.

</details>

4. ▢ Three parts of an application need to react to incoming chat messages. One design exposes a cold `Flow<Message>` that opens a subscription in its builder; the other exposes a `SharedFlow<Message>`. What actually differs, and which is right here?

<details markdown="1"><summary>Check</summary>

With the cold flow, each of the three collectors starts its own execution, so you open three subscriptions and each collector sees only what arrives after it starts collecting. With the `SharedFlow`, the stream exists independently of collectors and all three subscribers receive the same emissions from the one active stream. The hot flow is right here: the messages happen whether or not anyone is listening, and nobody wants three connections for one chatroom. If new subscribers should also see the last few messages, that is the `replay` parameter, and if what they need is the current state rather than each event, that is `StateFlow`.

</details>

5. ▢ Which claim describes a cold flow correctly?

    - a) A cold flow runs once, and every collector after that receives replayed values
    - b) A cold flow does nothing until collected, and each collector starts an execution
    - c) A cold flow emits continuously, so a collector joins the stream in progress
    - d) A cold flow runs on collection, and all collectors then share one execution

<details markdown="1"><summary>Check</summary>

**b)** Nothing runs until a collector arrives, and each new collector starts a new, independent execution. (a) describes a `SharedFlow` configured with a `replay` count. (c) describes a hot flow, which emits whether or not anyone is collecting. (d) is the tempting one, because sharing one execution among collectors is a real thing you can ask for: it is what `shareIn` does, and asking for it is precisely what makes the flow hot rather than cold.

</details>

## Real-world reps

- [ ] Find a function in code you have access to that returns a `List` of something loaded remotely. Decide whether its caller would rather have the values as they arrive, and what that would change about the caller.
- [ ] Find a cold flow with more than one collector, or a `Flow` exposed as a public property. Work out how many times its builder block runs in practice, and whether whoever wrote it knew.
- [ ] Tomorrow: read the primary source's hot flows section and pick one `StateFlow` or `SharedFlow` in a codebase you can reach. Say what its `replay` value is and what a subscriber therefore sees on subscribing.

## Going further

- [Docs: "Flows", Kotlin](https://kotlinlang.org/docs/coroutines-flow.html)
- [Docs: "Sequences", Kotlin](https://kotlinlang.org/docs/sequences.html)
- [Docs: "Coroutine context and dispatchers", Kotlin](https://kotlinlang.org/docs/coroutine-context-and-dispatchers.html)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
