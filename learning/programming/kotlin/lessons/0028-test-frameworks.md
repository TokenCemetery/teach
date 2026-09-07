---
title: "28. Test Frameworks"
description: "The layers a Kotlin test actually sits on, why runTest's virtual time stops at the dispatcher boundary, and what that forces on the design of the code under test"
type: lesson
---

# Lesson 28. Test Frameworks

**Mission link:** Stage 6 opens here, and "typed, tested" is half the mission. Stage 5 produced code that a plain unit test cannot check honestly, so the test tooling comes before the service.
**Primary source:** [API: "kotlinx-coroutines-test", kotlinx.coroutines](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-test/)
**Prerequisites:** [Lesson 27](0027-cancellation-and-exception-handling.md), [Lesson 26](0026-flows.md), [Lesson 25](0025-coroutine-context-and-dispatchers.md)

## Warm-up

1. ▢ A coroutine runs a tight computational loop with no suspending call in it. What does `cancel()` do to it, and why?

<details markdown="1"><summary>Check</summary>

Nothing visible: the loop runs on. Cancellation is cooperative, so the coroutine only throws `CancellationException` when it next checks, which happens at a suspension point or an explicit `ensureActive()` or `isActive` check. A loop with none of those never checks, so `cancel()` records the request and the work continues.

</details>

2. ▢ Code already running on `Dispatchers.Default` wraps a blocking call in `withContext(Dispatchers.IO)`. Given that those two share threads, what did the wrapper actually change?

<details markdown="1"><summary>Check</summary>

Typically not the thread: `IO` shares threads with `Default` and the implementation keeps execution where it is on a best-effort basis. What changes is the accounting. The call now runs against IO's blocking-task parallelism budget instead of occupying a slot in the CPU pool that is sized to the core count.

</details>

3. ▢ A cold flow has two collectors. How many times does its builder block run?

<details markdown="1"><summary>Check</summary>

Twice. Each new collector starts a new, independent execution of the flow, so any work in the builder, a query or a subscription, happens once per collector. A stream that should exist independently of its collectors has to be a hot flow instead.

</details>

## Know this

**A Kotlin test sits on layers, and knowing which layer a problem belongs to saves most of the confusion.**

|Layer|What it gives you|
|---|---|
|`kotlin.test`|Annotations to mark test functions, and assertion functions, **independently of the test framework being used** ([kotlin-test](https://kotlinlang.org/api/core/kotlin-test/))|
|A runner|What actually finds and executes tests. On the JVM, normally JUnit 5|
|`kotlinx-coroutines-test`|`runTest`, a scope built for tests, and control over virtual time|
|Turbine|Assertions for what a `Flow` emitted, in order, and when it finished|

`kotlin.test` is a façade, not a framework. Its assertions delegate to an `Asserter`, and you choose the implementation by artifact: `kotlin-test-junit5` provides an `Asserter` on top of JUnit 5 **and maps the test annotations onto JUnit 5's**, while `kotlin-test-junit` does the same for JUnit 4 and `kotlin-test-testng` for TestNG. So the same `@Test` in your source can mean different things depending on a dependency, and the artifact has to match the runner you are actually using.

Everything about the runner itself, which test to write, the lifecycle annotations, choosing an assertion, parameterised sources, is Java's material and is written down once, in the [Java workspace's testing and build sheet](../../java/reference/testing-and-build.md). This lesson does not repeat it.

One alternative worth knowing by name: [Kotest](https://kotest.io/docs/framework/framework.html) replaces the first two layers together, with tests written in one of several styles (a class extending `FunSpec` holding `test("...") { }` blocks) and infix matchers such as `shouldBe`. Pick it deliberately or not at all; mixing it in halfway is how a codebase ends up with two ways to write every test.

**`runTest` and its scope.** `TestScope` is a coroutine scope built for testing, and `runTest` creates one and uses it as the receiver of the test body. Two properties of it are worth knowing before you hit them. `TestScope` on its own does not run the code launched in it, and it is stateful, because it tracks executing coroutines and uncaught exceptions, so a `TestScope` you build by hand in a `@BeforeTest` still has to reach `runTest` eventually.

Virtual time belongs to a `TestCoroutineScheduler`, which the docs call the shared source of virtual time. Several test dispatchers can be created against the same scheduler and will then share their view of the clock, `TestScope.testScheduler` reaches it, and `currentTime` reads it. That is what lets a test with a `delay(3_000)` in it finish instantly and still assert on the timing.

**The boundary that decides how you write production code.** Virtual time does not follow you across a dispatcher change. `withContext(Dispatchers.IO)`, `withContext(Dispatchers.Default)` and `withContext(Dispatchers.Main)` do not use the test's virtual time source, so delays inside them are **not** skipped. The documentation's example is blunt about it: a function that does `withContext(Dispatchers.Default) { delay(1_000) }` takes a whole real-time second inside `runTest`, and the virtual time afterwards is still zero.

The remedy the docs give is not a test trick, it is a design rule: make the dispatcher replaceable, through dependency injection, a service locator, or a default parameter, so a test can pass a `TestDispatcher` instead. This is the clearest case in the whole arc of testability dictating a production signature, and it is why "do not hardcode a dispatcher" is engineering advice rather than taste.

**The two test dispatchers, and a trap in choosing between them.** `StandardTestDispatcher` is a plain dispatcher linked to a scheduler, so a coroutine you `launch` in a test does not run until the test yields or advances the clock. With `UnconfinedTestDispatcher`, child coroutines launched at the top level are entered **eagerly**, running until their first suspension without a dispatch, so an assertion written straight after a `launch` sees the effect already applied.

That difference makes `UnconfinedTestDispatcher` tempting for the wrong reason. Reaching for it because a test failed removes the dispatching that production will impose, so the test stops being able to catch an ordering bug. The docs' own suggestion, when you want eagerness in general but accuracy somewhere specific, is to keep the unconfined dispatcher and `launch` that part with a `StandardTestDispatcher`.

For `Dispatchers.Main`, which has no platform implementation in a unit test, `Dispatchers.setMain` installs a replacement and `Dispatchers.resetMain` puts it back. On the JVM this works because a `ServiceLoader` mechanism already substitutes a testable `Main` that delegates to the real one where there is one.

**Flows need their own assertions.** A `Flow` has no return value to compare, so a test has to say what was emitted, in what order, and whether the flow completed. [Turbine](https://github.com/cashapp/turbine) is the library the Kotlin flow documentation itself points at: `flow.test { }` gives you `awaitItem()`, `awaitComplete()` and `awaitError()` inside the block, and `testIn` assigns a turbine to a `val` when you need several flows at once.

One footgun comes with it, and the README states the consequence plainly. `testIn` cannot clean up its own coroutine, so either give it `runTest`'s `backgroundScope`, which handles that for you, or call `cancel()`, `awaitComplete()` or `awaitError()` before the scope ends. Otherwise your test will hang, which is a considerably worse failure than a red assertion.

## Practice

1. ▢ A test file imports `kotlin.test.Test` and `kotlin.test.assertEquals`, and the project runs its tests on JUnit 5. What makes that work, and what has to be true of the dependencies?

<details markdown="1"><summary>Check</summary>

`kotlin.test` provides the annotations and assertions independently of any framework: assertions delegate to an `Asserter`, and the annotations are mapped onto a real framework's by the artifact you depend on. With `kotlin-test-junit5` on the classpath, `kotlin.test.Test` maps to JUnit 5's annotation and the assertions run through a JUnit 5 `Asserter`. So the requirement is that the artifact matches the runner: `kotlin-test-junit` is the JUnit 4 mapping, and pairing it with a JUnit 5 engine means your annotations are being mapped for a framework that is not the one looking for them.

</details>

2. ▢ `suspend fun veryExpensiveFunction() = withContext(Dispatchers.Default) { delay(1_000); 1 }`, called inside `runTest`. Predict how long the test takes and what `currentTime` reads afterwards.

<details markdown="1"><summary>Hint</summary>

Ask which scheduler is providing the clock inside that `withContext` block.

</details>

<details markdown="1"><summary>Check</summary>

A real second, and `currentTime` still reads zero. Virtual time comes from the test's `TestCoroutineScheduler`, and `Dispatchers.Default` does not use it, so the `delay` inside that block is a real delay and the test's clock never advances. Multiply that by a suite and you have a slow test run that nobody can explain. The fix is in the signature of the function under test, not in the test: take the dispatcher as a parameter or inject it, so the test can supply a `TestDispatcher` sharing the test's scheduler.

</details>

3. ▢ A test does `launch { state = "loaded" }` and then immediately asserts `state == "loaded"`. It fails under `runTest` as written and passes with `runTest(UnconfinedTestDispatcher())`. What is the real difference, and why is switching the dispatcher the wrong reason to switch it?

<details markdown="1"><summary>Check</summary>

With the standard test dispatcher the launched coroutine is dispatched and does not run until the test yields or advances the clock, so the assertion runs first and sees the old value. `UnconfinedTestDispatcher` enters top-level children eagerly, running them until their first suspension, so the assignment has already happened. Both are honest behaviours, but choosing the eager one because the test failed removes the dispatching production will actually do, and with it the test's ability to catch an ordering bug. Either advance the clock and assert deliberately, or keep the unconfined dispatcher and `launch` the parts that need real dispatching with a `StandardTestDispatcher`.

</details>

4. ▢ A test collects two flows with `testIn`, asserts one item from each, and then ends. It does not fail; it hangs forever. Why, and what are the two ways to fix it?

<details markdown="1"><summary>Check</summary>

`testIn` cannot clean up the coroutine it started, so a flow that never terminates keeps the test waiting. Either pass `runTest`'s `backgroundScope` to `testIn`, which takes care of the cleanup, or terminate each turbine explicitly before the scope ends with `cancel()`, `awaitComplete()` or `awaitError()`. Worth recognising by symptom: a hanging test rather than a failing one usually means an outstanding coroutine nobody cancelled, which is the same diagnosis as an uncancelled scope in lesson 24.

</details>

5. ▢ Which claim about `runTest` and virtual time is correct?

    - a) runTest skips every delay in the test, including delays inside other dispatchers
    - b) runTest skips delays on its own scheduler, but not inside other dispatchers
    - c) runTest skips no delays, and virtual time only reports what really elapsed
    - d) runTest skips delays by running the test body on Dispatchers.Unconfined by default

<details markdown="1"><summary>Check</summary>

**b)** The scheduler is the source of virtual time, and code that has moved to `Dispatchers.IO`, `Default` or `Main` is not using it, so those delays are real. (a) is the comfortable wrong model, and it is why suites get slow without anyone being able to point at a cause. (c) discards the feature entirely. (d) mixes up two mechanisms: virtual time comes from the scheduler, while unconfined behaviour is something you opt into by passing `UnconfinedTestDispatcher()`, and it changes when coroutines start rather than how the clock works.

</details>

## Real-world reps

- [ ] Find a test suite in Kotlin you have access to and identify which of the four layers each import belongs to. Note anything that turns out to be a fifth thing you did not expect.
- [ ] Find a suspending function in your own work that hardcodes a dispatcher. Write the one-line signature change that would let a test pass a `TestDispatcher`, and decide whether you would actually make it.
- [ ] Tomorrow: time your test suite, then look for `withContext(Dispatchers.IO)` or `Dispatchers.Default` on paths that tests exercise. Estimate how much of the runtime is real delays that virtual time never got to skip.

## Going further

- [API: "kotlinx-coroutines-test", kotlinx.coroutines](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-test/)
- [API: "kotlin-test", Kotlin](https://kotlinlang.org/api/core/kotlin-test/)
- [Turbine, Cash App](https://github.com/cashapp/turbine)
- [Testing and build sheet, Java workspace](../../java/reference/testing-and-build.md)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
