---
title: "31. Structuring a Service"
description: "Where Kotlin files actually go and what goes inside a class, and the four decisions from earlier stages that decide whether a service is testable"
type: lesson
---

# Lesson 31. Structuring a Service

**Mission link:** Shipping a typed, tested Kotlin service is the mission's concrete deliverable. This lesson is the shape of one: the decisions that are the language's rather than the framework's, and therefore the ones no framework guide will make for you.
**Primary source:** [Docs: "Coding conventions", Kotlin](https://kotlinlang.org/docs/coding-conventions.html)
**Prerequisites:** [Lesson 30](0030-gradle-and-dependency-management.md), [Lesson 28](0028-test-frameworks.md), [Lesson 24](0024-structured-concurrency.md)

## Warm-up

1. ▢ Under Gradle, your project depends directly on `guava:20.0` while a transitive dependency asks for `25.1-android`. Which wins, and how would Maven differ?

<details markdown="1"><summary>Check</summary>

Gradle takes `25.1-android`: it considers all requested versions in the graph and by default selects the highest, wherever it was requested. Maven takes `20.0`, because nearest wins and a direct dependency sits at depth zero. Declaring a version directly is a pin in Maven and not in Gradle, where a constraint is the tool.

</details>

2. ▢ Why does a hardcoded `Dispatchers.IO` inside a suspending function count as a testability defect?

<details markdown="1"><summary>Check</summary>

Because the test's virtual time does not follow you into `Dispatchers.IO`, `Default` or `Main`, so any `delay` inside that block is a real delay and the test's clock never advances. Making the dispatcher replaceable, by parameter or injection, lets a test supply a `TestDispatcher` that shares the test's scheduler.

</details>

3. ▢ What does `coroutineScope { }` guarantee to the caller of the function that used it?

<details markdown="1"><summary>Check</summary>

That when the function returns, nothing it launched is still running. The scope executes its block and does not return until the block and every coroutine launched inside it has completed, so the work is finished rather than merely started.

</details>

## Know this

**What this lesson does not do: pick a framework.** Routing, serialization and server startup belong to whichever framework you chose, and its own documentation is the right place for them. Kotlin's official orientation for the server side is worth reading once for context, including its point that a Kotlin service keeps full compatibility with existing Java-based stacks and that large codebases can migrate gradually ([Backend development with Kotlin](https://kotlinlang.org/docs/server-overview.html)). What follows is the part that is the same whichever framework is underneath, and where the real mistakes live.

**Where the files go, which is not what a Java background expects.** In a pure Kotlin project the recommended directory structure follows the package structure **with the common root package omitted**: if everything lives under `org.example.kotlin`, those files sit directly in the source root, and `org.example.kotlin.network.socket` goes in `network/socket` ([Coding conventions](https://kotlinlang.org/docs/coding-conventions.html)). Java's convention, a directory per package segment all the way down, applies in the mixed case: where Kotlin and Java share a project, Kotlin files live in the same source root and follow the same structure.

File naming has two rules and one prohibition. A file holding a single class or interface takes that class's name. A file holding several classes, or only top-level declarations, takes a name describing what it contains, in upper camel case, such as `ProcessDeclarations.kt`. And the name must describe what the code does, which rules out meaningless words: the convention names `Util` specifically. A `Utils.kt` in a service is almost always three unrelated concerns that have not been named yet.

**Inside a class, the order is prescribed and the sorting is not.** Contents go: property declarations and initializer blocks, secondary constructors, method declarations, companion object. Then the part people get wrong: do **not** sort methods alphabetically or by visibility, and do not separate regular methods from extension methods. Put related things together so that someone reading top to bottom can follow the logic, choose an order (higher-level first, or the reverse) and stick to it. Nested classes go next to the code that uses them, or after the companion object when they exist for external use.

Two small conventions that come up in every review. Prefer a property over a no-argument function when the underlying algorithm does not throw, is cheap or cached, and returns the same result while the object's state is unchanged. And prefer `if` for a binary condition, `when` from three options up.

**Four decisions from earlier stages that decide whether the service is testable.** None of these is framework-specific, and all four are visible in a signature.

|Decision|The shape it takes|Why|
|---|---|---|
|Errors are values|Model the outcome with a sealed hierarchy and handle it in an exhaustive `when`, rather than throwing across a layer boundary|Lesson 9: sealing turns "did I handle every case" from a promise into a compiler check|
|Nullability lives at the edge|Parse the request into non-nullable domain types once, at the boundary, and keep the nullable form out of the core|Lesson 1: a nullable type that travels inward becomes a defensive check at every layer|
|One request is one scope|`coroutineScope` per request, nothing launched into a scope that outlives it, no `GlobalScope`|Lesson 24: the request's lifetime then owns its work, and a disconnect cancels all of it|
|Dispatchers and clocks are parameters|`suspend fun handle(..., dispatcher: CoroutineDispatcher = Dispatchers.IO)`, and a clock rather than a call to the current time|Lesson 28: the test needs to replace both, and a default keeps production call sites unchanged|

Blocking calls are the fifth item and follow from lesson 25: wrap a blocking dependency in `withContext` on `Dispatchers.IO`, or on a `limitedParallelism` view per dependency where one slow backend must not consume the whole blocking budget.

**One structural trap worth knowing before it bites.** The JVM has no top-level members, so the compiler wraps each file's top-level declarations in a generated class whose name derives from the file name. Two files with the same name in the same package therefore produce two classes with the same fully qualified name and the build fails with a duplicate-class error, which is why multiplatform projects give platform files a suffix such as `Platform.jvm.kt`. That generated file class is the same one lesson 29 met from the other side, as the thing `mockkStatic` actually mocks.

## Practice

1. ▢ A pure Kotlin service has everything under the root package `com.acme.billing`. Where does the file for `com.acme.billing.invoice.pdf.Renderer` belong, and what would change if the project also contained Java?

<details markdown="1"><summary>Check</summary>

Under the source root at `invoice/pdf/Renderer.kt`: the recommended structure follows the package structure with the **common root package omitted**, so no `com/acme/billing` directories appear at all. With Java in the same project, Kotlin files live in the same source root as the Java files and follow the same directory structure, meaning the full `com/acme/billing/invoice/pdf/` path returns. So the answer depends on a fact about the project, not on taste, and mixing the two conventions within one repository is how a source tree ends up half-nested.

</details>

2. ▢ A service has a `Utils.kt` holding five unrelated top-level functions. Name what the conventions say about it, and what to do instead.

<details markdown="1"><summary>Check</summary>

A file of top-level declarations should take a name describing what it contains, in upper camel case, and the convention explicitly rules out meaningless words, naming `Util` as the example. So `Utils.kt` fails the rule twice: it describes nothing, and it is the specific word called out. What to do is not renaming but splitting: five unrelated functions are several concerns sharing a file because none of them was named, and each group gets a file named for what it does. The file name is a design prompt, which is why the convention bothers to mention it.

</details>

3. ▢ A code review asks you to sort a class's methods alphabetically and move all extension functions into a block at the bottom. What do the conventions actually say?

<details markdown="1"><summary>Check</summary>

Both requests contradict them. The prescribed order is properties and initializer blocks, then secondary constructors, then methods, then the companion object, and within the methods the guidance is explicitly not to sort alphabetically or by visibility, and not to separate regular methods from extension methods. What replaces sorting is grouping: related things together, in one consistent direction (high-level first or the reverse), so a reader going top to bottom follows the logic. An alphabetical class is easy to verify and tells a reader nothing about what matters.

</details>

4. ▢ A request handler does `GlobalScope.launch { auditLog.write(event) }`, calls a blocking JDBC query directly, and stamps the record with the current time read inside the function. Name the three defects and the fix for each.

<details markdown="1"><summary>Check</summary>

**The audit write escapes the request.** `GlobalScope.launch` starts work that the request's scope neither waits for nor cancels, so a disconnect leaves it running and a failure in it surfaces nowhere useful. Launch it into the request's own scope, or, if it genuinely must outlive the request, into a scope some component owns and cancels.

**The blocking query occupies the wrong pool.** Called directly, it holds whatever thread the handler was running on, which is a CPU-pool thread sized to the core count. Wrap it in `withContext(Dispatchers.IO)`, or a `limitedParallelism` view of it when that dependency needs its own budget.

**The clock is not replaceable.** Reading the current time inside the function makes the output untestable except by approximation. Take the clock as a constructor parameter or an argument, and a test then pins it.

All three are the same defect in different clothing: a dependency the function reaches out and grabs rather than one it declares. That is what makes them visible in a signature, which is where the review should catch them.

</details>

5. ▢ Which claim about a pure Kotlin project's directory structure is correct?

   - a) A pure Kotlin project mirrors the full package path, root package directories included
   - b) A pure Kotlin project mirrors the package structure, omitting the common root package
   - c) A pure Kotlin project puts every file under the source root, ignoring packages
   - d) A pure Kotlin project must follow Java's layout, since the JVM requires it

<details markdown="1"><summary>Check</summary>

**b)** is the recommendation: follow the package structure, but omit the common root package, so subpackages below it become directories and the root does not. (a) is what a Java background assumes and it is what the mixed-project rule asks for, not the pure-Kotlin one. (c) drops the structure entirely, which loses the correspondence between a package statement and a location. (d) is wrong about the requirement: Kotlin does not tie a file's location to its package declaration, which is exactly why a convention has to say what to do.

</details>

## Real-world reps

- [ ] Open a Kotlin service you have access to and check its source tree against the convention. Decide whether it is a pure Kotlin project following the pure rule, a mixed one following the mixed rule, or a project that has quietly adopted half of each.
- [ ] Pick one request handler and read its signature alone. List every dependency it needs that the signature does not mention, then decide which of those should have been a parameter.
- [ ] Tomorrow: find the file in your own work whose name describes the least. Write down the two or three things actually in it, and the file names those things would want.

## Going further

- [Docs: "Coding conventions", Kotlin](https://kotlinlang.org/docs/coding-conventions.html)
- [Docs: "Backend development with Kotlin", Kotlin](https://kotlinlang.org/docs/server-overview.html)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
