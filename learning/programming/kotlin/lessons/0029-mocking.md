---
title: "29. Mocking"
description: "Why final-by-default changes what mocking means in Kotlin, what MockK does for the constructs that are not methods on an object, and when finality is telling you a seam is missing"
type: lesson
---

# Lesson 29. Mocking

**Mission link:** A tested Kotlin service needs test doubles for its collaborators, and Kotlin's own constructs, final classes, `object` singletons, top-level and extension functions, are exactly the ones a Java-era mocking habit cannot reach.
**Primary source:** [Site: MockK, mocking library for Kotlin](https://mockk.io/)
**Prerequisites:** [Lesson 28](0028-test-frameworks.md), [Lesson 11](0011-object-declarations-and-companion-objects.md), [Lesson 13](0013-extension-functions.md)

## Warm-up

1. ▢ A project uses `kotlin.test`'s `@Test` and assertions. What does the artifact choice, `kotlin-test-junit5` rather than `kotlin-test-junit`, actually decide?

<details markdown="1"><summary>Check</summary>

Which framework the annotations are mapped onto, and which `Asserter` the assertions delegate to. `kotlin.test` is a façade that is deliberately independent of any framework, so the artifact is what binds it to a real one, and it has to match the runner actually executing the tests.

</details>

2. ▢ Inside `runTest`, a function does `withContext(Dispatchers.Default) { delay(1_000) }`. How long does the test take?

<details markdown="1"><summary>Check</summary>

A real second, and the test's virtual time afterwards is still zero. Virtual time comes from the test's `TestCoroutineScheduler`, and `Dispatchers.Default`, `IO` and `Main` do not use it. The remedy is a design change: make the dispatcher replaceable so the test can pass a `TestDispatcher`.

</details>

3. ▢ What is an `object` declaration in Kotlin, and how many instances of one exist?

<details markdown="1"><summary>Check</summary>

A singleton declared rather than implemented by hand: `object Registry { ... }` declares both the type and its single, lazily-initialised, thread-safe instance. Exactly one exists, and there is no constructor to call, which is why it replaces the Java singleton-pattern boilerplate and Java's static members.

</details>

## Know this

**Start with the language fact, because it is the whole reason Kotlin mocking looks different.** By default Kotlin classes **and their members** are final: they cannot be inherited from, or overridden, unless explicitly marked `open` ([Inheritance](https://kotlinlang.org/docs/inheritance.html)). A mocking library whose technique is "generate a subclass and override the methods" therefore has nothing to override in ordinary Kotlin code. That is why the Java-era instruction to just mock the class does not transfer, and why [MockK](https://mockk.io/) exists as a Kotlin-first library rather than a Kotlin wrapper over a Java one.

Note what this lesson is not. The taxonomy of doubles, dummy, stub, spy, mock and fake, the trap where an unstubbed mock's default return happens to match what the test expected, and the argument for asserting on state before verifying calls, are all written down once in the [Java workspace's testing and build sheet](../../java/reference/testing-and-build.md). They apply here unchanged. What follows is only the part that is Kotlin's.

**The constructs that are not methods on an object, and what each one needs.**

|What you are doubling|What it takes|
|---|---|
|A class or interface|`mockk<T>()`, then `every { ... } returns ...`. Finality is not an obstacle here|
|A **suspending** function|`coEvery` and `coVerify`, the coroutine forms. The library provides a co-variant of each part of the DSL: `coMatch`, `coAnswers`, `coInvoke` and the rest. `coJustAwait` simulates a suspending call that never returns|
|An `object` singleton|`mockkObject(Obj)` turns the real singleton into a mock, and `unmockkObject` or `unmockkAll` reverts it. There is a scoped form, `mockkObject(Obj) { ... }`, that unmocks itself at the end of the block|
|A **top-level** function|`mockkStatic(::function)`. Top-level functions belong to no class, so the JVM compiles them to static methods on a generated file class, and that class is what gets mocked|
|An **extension** function|Class-wide and object-wide ones come free with a normal `mockk` of the declaring type. A module-wide one needs `mockkStatic("pkg.FileKt")`, or `mockkStatic(Obj::extensionFunc)` on the JVM. Extension properties work the same way|
|A partly-real object|`spyk(obj)`, which is a **copy** of the object you passed. There is a known issue with using a spy on a suspending function|

**Three sharp edges, all documented rather than folklore.**

The blast radius of `mockkStatic` is a whole file, not a function. Mocking one top-level function clears any existing mocks of other functions declared in the same file, because what is really being mocked is the generated enclosing class. The extension-function case says the same thing outright: `mockkStatic(Obj::extensionFunc)` mocks all of `pkg.FileKt`, not just that one function. If the file is named by `@JvmName`, that is the name to use.

A relaxed mock, `mockk<T>(relaxed = true)`, returns some simple value for every function and chained mocks for reference types, which saves stubbing what the test does not care about. It works badly with generic return types, where it usually throws a class cast exception, so stub those by hand. If it is only the `Unit`-returning functions you want relaxed, `relaxUnitFun = true` says so precisely.

Mocking an `object`, a static or a constructor changes global state, so it has to be undone. Either use the scoped block form, or let the JUnit 5 integration do it: `@ExtendWith(MockKExtension::class)` initialises `@MockK`, `@RelaxedMockK` and `@SpyK` fields and calls `unmockkAll` and `clearAllMocks` in an `@AfterAll` callback.

**Now the judgement, which is the part worth keeping.** Every tool in that table makes it easier to mock something you should not have mocked. `mockkStatic` in particular will happily let you stub a top-level function in a library you do not own, which the Java sheet warns against for reasons that have not changed.

The Kotlin-specific version of the argument is this: when finality gets in your way, the language is usually telling you that the seam is missing. The move that follows is to introduce an interface the collaborator implements, or to write a small fake, not to mark a production class `open` so a test can subclass it. Marking it `open` changes the class's inheritance contract for everyone, permanently, in exchange for one test's convenience. That is an opinion rather than a rule, and what it rests on is that a seam expressed as a type survives refactoring while a mock pinned to a static call does not. What would change it: a codebase where the collaborator genuinely has one implementation and no plausible second, where an interface is ceremony and a `mockk` of the class is the honest, cheaper answer.

## Practice

1. ▢ A colleague asks whether a normal Kotlin class needs `open` before it can be mocked. Answer it, then say what the question is really about and what you would do instead of adding `open`.

<details markdown="1"><summary>Check</summary>

No: MockK mocks a final class fine. The question exists because Kotlin classes and their members are final unless marked `open`, so any technique based on generating a subclass and overriding methods has nothing to work with, which is exactly the situation Java-era advice assumes away. What not to do is add `open` for the test's benefit, since that permanently changes what the class promises about inheritance to buy one test some convenience. Introduce an interface for the collaborator, or write a fake, and the seam then exists in the type system where a refactor cannot silently remove it.

</details>

2. ▢ A test stubs a repository with `every { repo.load(id) } returns user`, where `load` is declared `suspend fun load(id: Id): User`. What is wrong, and what does the fix change about the verification too?

<details markdown="1"><summary>Check</summary>

`every` is the non-suspending stubbing block; a suspending function needs `coEvery { repo.load(id) } returns user`. The verification changes to match: `coVerify { repo.load(id) }`. The whole DSL has coroutine forms, `coMatch`, `coAnswers`, `coInvoke` and the ordered and sequence verifiers, so the rule is simply that a suspending call takes the `co` variant of whatever you were reaching for. `coJustAwait` is the specialised one worth knowing, for a suspending call that should never return, which is how you test what your code does while waiting.

</details>

3. ▢ One test mocks a top-level function `buildCar()` from `Cars.kt` with `mockkStatic(::buildCar)`. Another stub of `priceOf()`, declared in the same file, stops working. Why?

<details markdown="1"><summary>Hint</summary>

Ask what the JVM actually mocked, given that neither function belongs to a class.

</details>

<details markdown="1"><summary>Check</summary>

Because the unit of mocking is the file, not the function. Top-level functions belong to no class, so the JVM compiles them into static methods on a generated class for that file, and mocking one function clears any existing mocks of the other functions declared alongside it, equivalent to clearing the static mock of that enclosing class. Module-wide extension functions behave the same way: `mockkStatic(Obj::extensionFunc)` mocks the whole generated file class. So two tests stubbing different functions from one file are contending for the same object, and that is a reason to be reluctant about the technique rather than a detail to work around.

</details>

4. ▢ A relaxed mock of a repository works fine until it is used for a function returning a generic type, where the test fails with a class cast exception. What is happening, and what is the documented remedy?

<details markdown="1"><summary>Check</summary>

A relaxed mock invents a simple value for every function it was not told about, returning chained mocks for reference types, and that invention works badly for a generic return type, where it usually throws a class cast exception. The remedy is to stub that one function by hand, with `every { ... } returns` an appropriate value or another `mockk()`. Note the smaller tool for the common case: if the only thing you wanted relaxed was the `Unit`-returning functions, `relaxUnitFun = true` asks for exactly that instead of relaxing everything.

</details>

5. ▢ Which response to "this class is final and I need to double it" is the better default?

   - a) A final class is a mocking problem, so mark it open in tests
   - b) A final class with no seam is a design signal: introduce an interface
   - c) A final class cannot be mocked at all, so test it through callers
   - d) A final class needs mockkStatic, which is what that function was designed for

<details markdown="1"><summary>Check</summary>

**b)** is the better default, and the reasoning is that a seam expressed as a type survives a refactor while a double pinned to a static call does not. (a) is the common move and it trades a permanent change to the class's inheritance contract for one test's convenience. (c) is simply false: MockK mocks final classes. (d) misreads what `mockkStatic` is for, which is top-level and module-wide functions that the JVM compiled into statics on a generated file class. Note that (b) is a default rather than a law: where the collaborator has one implementation and no plausible second, an interface is ceremony and a `mockk` of the class is the honest answer.

</details>

## Real-world reps

- [ ] Find a mock in a Kotlin test you have access to. Decide which row of this lesson's table it belongs to, and whether the thing being doubled is something the test owns.
- [ ] Find a `mockkStatic`, a `mockkObject`, or a mock of a type from a third-party library. Work out what would break if a second test in the same run mocked something else from the same file or object.
- [ ] Tomorrow: pick one collaborator in your own work that you have mocked more than twice. Write the interface or the fake that would replace those mocks, and compare the two tests side by side for what each one actually asserts.

## Going further

- [Site: MockK, mocking library for Kotlin](https://mockk.io/)
- [Docs: "Inheritance", Kotlin](https://kotlinlang.org/docs/inheritance.html)
- [Testing and build sheet, Java workspace](../../java/reference/testing-and-build.md)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
