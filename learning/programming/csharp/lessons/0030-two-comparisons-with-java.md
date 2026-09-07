---
title: "30. Two Comparisons with Java"
description: "The same waiting problem solved at two different layers, why Java's answer removes the style C# requires rather than adopting it, and the expression tree that has no counterpart in a Stream"
type: lesson
---

# Lesson 30. Two Comparisons with Java

**Mission link:** Stage 7 is judgment, and judgment gets tested out loud. Someone will say that virtual threads prove `async`/`await` was over-engineering, or that a Java `Stream` is just LINQ with different spelling. Both claims are wrong in interesting ways, and being able to say why is the difference between having learned C# and having only learned to write it.
**Primary source:** [Docs: "Virtual Threads", Oracle Java SE 21](https://docs.oracle.com/en/java/javase/21/core/virtual-threads.html)
**Prerequisites:** [Lesson 28](0028-entity-framework-core.md), [Lesson 18](0018-async-and-await.md), [Lesson 13](0013-linq.md)

## Warm-up

1. ▢ What does `await` do to the method containing it, and what does it do to the thread?

<details markdown="1"><summary>Check</summary>

It suspends the enclosing method and returns control to the caller, and it does **not** block the thread. The method resumes later; the thread went and did something else in the meantime.

</details>

2. ▢ What decides whether a LINQ query compiles to a delegate or to an expression tree, and why does the difference matter?

<details markdown="1"><summary>Check</summary>

The type being queried. It matters because an expression tree is data describing the query, which a provider can translate into something else, such as SQL. That is what lets the same query text run against a database instead of a list.

</details>

3. ▢ Before reading on: what problem are `async`/`await` and a thread pool both trying to solve?

<details markdown="1"><summary>Check</summary>

A thread waiting on I/O is an expensive resource doing nothing. Every answer in this lesson is an answer to that one sentence, and the answers differ in **which layer** they change: the language, the compiler, or the runtime.

</details>

## Know this

**A note on sourcing before anything else.** No single document compares these platforms, so this lesson is assembled from each side's own primary documentation and is labelled as constructed rather than quoted. Every factual claim below is attributed to the side it comes from; the comparison itself is the part being argued.

**Both platforms are solving the sentence from the warm-up, and they change different layers.** C# changes the **method**: `await` suspends it, returns control to the caller, and the compiler rewrites the body into a state machine whose type is a `Task`. Java changes the **thread**: a virtual thread **is not tied to a specific OS thread**, and when code running in one **calls a blocking I/O operation, the Java runtime suspends the virtual thread until it can be resumed**, freeing the OS thread ([Virtual Threads](https://docs.oracle.com/en/java/javase/21/core/virtual-threads.html)). The Java runtime **mounts** a virtual thread onto a platform thread called a **carrier**, and the virtual thread **unmounts** from that carrier, usually when it performs a blocking I/O operation.

Read those two side by side and the shared idea is visible: release the expensive resource at the wait point. What differs is who does the releasing, and what it costs you.

|Question|C# `async`/`await`|Java virtual threads|
|---|---|---|
|What is made cheap|the wait: the method suspends and the thread is not blocked|the thread: it is plentiful, so blocking one is cheap|
|Who rewrites your code|the compiler, into a state machine|nobody; the runtime unmounts the thread from its carrier|
|What it costs the signature|`async` and `Task<T>` propagate through every caller|nothing; the code is ordinary blocking code|
|What you must not do|`async void`, unawaited tasks, tokens not threaded through|pin the carrier, pool virtual threads, cache expensive objects in thread-locals|

**The claim to be able to refute: "virtual threads prove `async`/`await` was unnecessary."** Two documented sentences settle it in the other direction. First: **virtual threads are not faster threads; they do not run code any faster than platform threads. They exist to provide scale (higher throughput), not speed (lower latency).** Second, and more pointed: the adoption guide tells you to **write simple, synchronous code employing blocking I/O APIs in the thread-per-request style**, and says explicitly that code written **in the non-blocking, asynchronous style will not benefit much from virtual threads**.

So Java's answer does not adopt the asynchronous style, it makes it **unnecessary**. That is a real difference in kind, and it cuts both ways. A Java developer arriving in C# should not read `async` as an optimisation they are entitled to skip: in C#, it is the mechanism, and there is no cheap thread underneath waiting to make blocking acceptable. A C# developer looking at Java 21 should not say Java got `async`/`await`: it got the opposite, a way to keep writing sequential code and have it scale.

**Each answer's cost lands in a different place, which is the useful part of the comparison.** C#'s cost is in the type system, and it is paid at every call site: `async` propagates upward, `async void` breaks the only mechanism a caller has to observe completion, and a `CancellationToken` has to be threaded through by hand. Java's cost is in runtime behaviour and in habits carried from platform threads. A virtual thread **cannot be unmounted while it is pinned to its carrier**, which happens inside a `synchronized` block or method and in native code, and the guide's advice is that this **may adversely affect throughput if the blocking operation is both long-lived and frequent**. Pooling is the other one: virtual threads are plentiful, so **each should represent a task rather than a shared, pooled resource**, and **the number of virtual threads is always equal to the number of concurrent tasks**.

Notice that C#'s traps are visible in the source and Java's are not. `async void` is in the signature; a `synchronized` block that pins a carrier looks exactly like correct code. Neither platform gave you concurrency for free; they charged in different currencies.

**Second comparison: a LINQ query and a Java `Stream` are both lazy, and only one of them survives being used.** Start with the agreement, because it is real. Java streams have **no storage**, being **not a data structure that stores elements** but something that **conveys elements from a source through a pipeline of computational operations**, and they are **functional in nature**, producing a result without modifying the source ([java.util.stream](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/stream/package-summary.html)). Intermediate operations **are always lazy** and **traversal of the pipeline source does not begin until the terminal operation is executed**. Every clause of that describes LINQ too, where nothing runs until you iterate.

The disagreements are these:

|Question|LINQ|Java `Stream`|
|---|---|---|
|What the variable holds|a query, which executes when it is enumerated|a pipeline, which is **consumed** by its terminal operation and **can no longer be used**|
|Running it twice|enumerate again and the query runs again|**return to the data source to get a new stream**|
|Where it can run|a delegate **or an expression tree**, so a provider can translate it into SQL|compiled code that runs in the JVM over its source|
|Going parallel|not covered by this arc|a property of the stream, requested with `parallelStream()` or `parallel()`, since the JDK **creates serial streams unless parallelism is explicitly requested**|

**The third row is the one worth arguing about.** The expression tree is why LINQ and `Stream` end up in different places despite looking alike. Because a C# query can compile to data describing itself, a provider can read it and emit SQL, which is the entire basis of lesson 28: the query you wrote is translated, and the boundary of translation is where `Where` throws and the last `Select` falls back to the client. A Java `Stream` has no such split. Its lambdas are compiled code, they run in the JVM, and the question of what the database can do with your `filter` never arises because the answer is nothing.

Which reframes what looked like a C# complication. Client-versus-server evaluation is not LINQ being awkward; it is the price of a query that can leave the process. The comparison also explains the shape of the two ecosystems: Java's data access grew a separate query language because the Stream API could not become one, and C# did not need to.

**How to use a comparison like this.** Stage 7 is not about winning the argument. It is about being able to say what each design bought and what it charged, and to notice when someone is comparing a mechanism in one language against a style in the other. Both claims this lesson opened with make that mistake in opposite directions.

**One forward pointer.** Lesson 31 closes the arc by turning this outward: reading C# and naming precisely what a construct is costing, including the constructs a Java habit produces.

## Practice

1. ▢ A colleague argues: "Java 21 has virtual threads, so `async`/`await` was over-engineering. C# made every signature worse for nothing." What is right and what is wrong in that?

<details markdown="1"><summary>Check</summary>

Right: the cost is real and it is exactly where they say it is. `async` propagates through callers, `Task<T>` shows up in every signature on the path, and `async void` breaks the caller's only means of observing completion. Nobody defending the design should pretend that is free.

Wrong: the conclusion. Virtual threads do not provide the asynchronous style more cheaply, they remove the need for it, and Oracle's own adoption guide says to **write simple, synchronous code employing blocking I/O APIs** and that non-blocking asynchronous code **will not benefit much from virtual threads**. The two are alternatives at different layers, not competing implementations of the same idea. There is no cheap thread under a .NET program that would make blocking acceptable, so removing `async` there does not leave you with Java's situation, it leaves you with a blocked thread pool.

Also wrong, and worth correcting because it is the most common version of the claim: virtual threads are not faster. The documentation is explicit that **they do not run code any faster than platform threads** and exist for **scale, not speed**.

</details>

2. ▢ Reverse it. A C# developer says "Java finally got `async`/`await` in 21." What did Java actually get, in one sentence, and what does that change about how the code looks?

<details markdown="1"><summary>Check</summary>

It got threads cheap enough to block: a virtual thread is not tied to an OS thread, and when it performs a blocking I/O operation the runtime suspends it and **unmounts** it from its **carrier**, freeing the platform thread for other virtual threads.

What that changes about the code is that nothing changes about the code. The method keeps its ordinary signature and its ordinary blocking calls, and the concurrency is a property of the thread it runs on rather than of the method. That is the precise opposite of `async`/`await`, where the concurrency is visible in the method's type and invisible in the thread.

The habit to distrust when moving in that direction is thread pooling. Platform threads are scarce and therefore pooled; virtual threads are plentiful, so **each should represent a task**, and **the number of virtual threads is always equal to the number of concurrent tasks**. Converting pooled platform threads to pooled virtual threads yields little, because it is the tasks that need converting.

</details>

3. ▢ You port a LINQ query to Java, then reuse the stream variable for a second aggregate. It compiles. What happens, and what is the C# behaviour you were relying on?

<details markdown="1"><summary>Hint</summary>

Both are lazy. Ask what the terminal operation does to the pipeline, and what enumerating a query does to the query.

</details>

<details markdown="1"><summary>Check</summary>

The second use fails, because **after the terminal operation is performed the stream pipeline is considered consumed and can no longer be used**, and **if you need to traverse the same data source again you must return to the data source to get a new stream**.

What you were relying on is that a LINQ query variable holds a query rather than a result. Deferred execution means nothing runs until you enumerate, so enumerating it a second time runs it a second time, which is convenient and is also the reason a query over a database can quietly cost two round trips.

Both languages are lazy in the middle and eager at the end. The difference is what the variable is: in C# it is a description that can be run again, and in Java it is a pipeline that has now been spent.

</details>

4. ▢ Which LINQ capability has no counterpart in the Stream API, and what does its absence explain about the two ecosystems?

<details markdown="1"><summary>Check</summary>

Compilation to an **expression tree**. A C# query can become data describing itself, which a provider reads and translates, and that is what lets the same query text reach a database.

A Java `Stream` conveys elements from a source through a pipeline of compiled operations that run in the JVM. There is nothing for a database to read, so the question of translating a `filter` into SQL does not arise.

Two things follow. First, EF Core's client-versus-server evaluation rule is not LINQ being difficult; it is the bill for a query that can leave the process, and the rule marks the boundary: untranslatable code in the final `Select` falls back to the client, and anywhere else it throws. Second, the ecosystems diverged for a reason rather than by taste. Java data access grew separate query languages because the Stream API could not become one; C# did not need to, because the language feature already crossed the boundary.

</details>

5. ▢ Which statement is correct?

    - a) Virtual threads run code faster than platform threads, which is what makes blocking them cheap
    - b) Virtual threads exist for scale rather than speed, and the documented guidance is to write straightforward synchronous blocking code rather than asynchronous code
    - c) A Java stream pipeline can be traversed repeatedly once built, in the way a LINQ query variable can be enumerated repeatedly
    - d) `async`/`await` and virtual threads both work by having the compiler rewrite a method into a state machine

<details markdown="1"><summary>Check</summary>

**b)** Both halves are stated by Oracle's documentation, and together they are the whole answer to the "over-engineering" argument.

(a) is contradicted directly: virtual threads **are not faster threads** and do not run code any faster; blocking them is cheap because they are plentiful, not because they are quick. (c) inverts the consumption rule, since a terminal operation consumes the pipeline and you must go back to the data source for a new stream. (d) is true of C# only; Java's source code is not rewritten, and the release happens when the runtime unmounts the virtual thread from its carrier.

</details>

## Real-world reps

- [ ] Find an `async` method chain in C# and count the signatures that changed because of it. That count is the design's price, and it is the number to have ready when someone argues about it.
- [ ] Find a LINQ query variable that is enumerated more than once. Work out how many times its work is performed.
- [ ] Tomorrow: if you have access to Java code, find a `synchronized` block containing a blocking call, and decide whether it would pin a carrier long enough to matter.

## Going further

- [Docs: "Virtual Threads", Oracle Java SE 21](https://docs.oracle.com/en/java/javase/21/core/virtual-threads.html)
- [Docs: "java.util.stream", Oracle Java SE 21](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/stream/package-summary.html)
- [Docs: "Task asynchronous programming model", Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/csharp/asynchronous-programming/task-asynchronous-programming-model)
- [Docs: "Language Integrated Query (LINQ)", Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/csharp/linq/)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
