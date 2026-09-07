---
title: Resources
description: "Trusted sources for Kotlin"
type: resources
---

# Kotlin Resources

## Knowledge

- [Docs: "Null safety", Kotlin](https://kotlinlang.org/docs/null-safety.html)
  Official docs for Kotlin's nullable/non-nullable type distinction, the safe-call and Elvis operators, and the platform types a Java interop boundary introduces. Use for: the primary mechanism behind writing null safety into the type system instead of into defensive checks.
- [Docs: "Types overview", Kotlin](https://kotlinlang.org/docs/types-overview.html)
  Official docs explaining that Kotlin's basic types (numbers, characters, booleans) behave like regular classes despite an optimized primitive representation at runtime. Use for: exactly why `Int`, `Boolean`, and similar types have member functions, unlike Java's primitives.
- [Docs: "Strings", Kotlin](https://kotlinlang.org/docs/strings.html)
  Official docs on Kotlin's immutable `String` type and string templates (`$variable`, `${expression}`). Use for: string interpolation as a language feature, not string concatenation with extra syntax.
- [Docs: "Flows", Kotlin](https://kotlinlang.org/docs/coroutines-flow.html)
  Official docs on `Flow`: the emitter, intermediate operator and collector roles with the upstream and downstream vocabulary, cold flows (lazy, one execution per collector) against hot flows (`SharedFlow` and `StateFlow`, whose collectors are subscribers), the rule that a `flow()` builder must emit from its own coroutine context, `.flowOn()` as a context-preserving upstream switch, `channelFlow()` with its buffered channel for emitting from several coroutines, and the `catch` and `retry` operators. Use for: streaming many values over time instead of returning one, and for deciding between a cold and a hot flow. Note that `flow.html` redirects here.
- [Docs: "Coroutine context and dispatchers", Kotlin](https://kotlinlang.org/docs/coroutine-context-and-dispatchers.html)
  Official docs on the `CoroutineContext` as a set of elements, the dispatchers and what each confines execution to, `withContext` for switching and the extra dispatches a dispatcher change costs, context inheritance by children, and the two ways the parent-child relation gets overridden. Use for: reading which threads a coroutine runs on, and for why passing a `Job` into a builder detaches it from its scope.
- [API: "Dispatchers", kotlinx.coroutines](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/-dispatchers/)
  Reference for the four standard dispatchers, including the exact wording of what `Main` is confined to and what `Unconfined` does with the initial continuation. Use for: choosing a dispatcher, and for the fact that `Default` is what every builder falls back to.
- [API: "Dispatchers.IO", kotlinx.coroutines](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/-dispatchers/-i-o.html)
  Reference for the blocking-IO dispatcher: the parallelism property and its default of 64 threads or the core count, the elasticity of `limitedParallelism` views (with a worked MySQL and MongoDB example), and two facts that correct the obvious model, that `IO` shares threads with `Default` so switching to it often does not change thread, and that its limit bounds blocking tasks rather than threads. Use for: sizing and partitioning blocking work in a service.
- [API: "CoroutineScope", kotlinx.coroutines](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/-coroutine-scope/)
  Reference with a "Structured concurrency in detail" section: that a coroutine cannot reach its final state until all its children have, that cancelling a scope cancels every child, the exact conditions under which a child's failure fails its parent, and the `CoroutineScope()` constructor function for a scope tied to an entity's lifetime (with the warning that cancelling it is the caller's job). Use for: deciding between a lexical scope and an owned one, and for the precise propagation rules.
- [API: "GlobalScope", kotlinx.coroutines](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/-global-scope/)
  Reference for the `@DelicateCoroutinesApi` global scope, with the pitfalls stated as the library sees them (computations running when they are no longer needed or have no right to) and the narrow legitimate case of a process that must live as long as the application. Use for: arguing about a `GlobalScope.launch` in review, in the library authors' own terms.
- [Docs: "Coroutines basics", Kotlin](https://kotlinlang.org/docs/coroutines-basics.html)
  Official docs on the `suspend` keyword and the rule that a suspending function can only be called from another one, the three coroutine builders with what each returns, and a direct comparison of a coroutine against a JVM thread (stack size, how many of each a process holds, what happens to the thread when a coroutine suspends). Use for: the entry point to the concurrency stage, and for why `delay` and `Thread.sleep` are not interchangeable.
- [Docs: "Composing suspending functions", Kotlin](https://kotlinlang.org/docs/composing-suspending-functions.html)
  Official docs on combining suspending calls: sequential by default, `async` and `await` for genuine concurrency with the elapsed times measured, lazily started `async` via `CoroutineStart.LAZY`, and the difference between `Job` and `Deferred`. Use for: making two independent slow operations concurrent, and for seeing that `suspend` alone never does it for you.
- [Spec: "Threads and Locks", Java Language Specification, Java SE 21](https://docs.oracle.com/javase/specs/jls/se21/html/jls-17.html)
  Chapter 17 of the JLS: the memory model itself, happens-before, and the `final` field semantics whose freeze action happens when a constructor exits. Use for: the model Kotlin on the JVM actually runs under, since the language defines no memory model of its own on this platform. Dense; the [Java workspace's concurrency sheet](../java/reference/concurrency.md) is the lookup-shaped companion to it.
- [API: "Volatile", Kotlin](https://kotlinlang.org/api/core/kotlin-stdlib/kotlin.concurrent/-volatile/)
  Reference for the `@Volatile` annotation, including the distinction the name hides: operations on the annotated **backing field** are atomic, while a property operation through a custom accessor that touches the field several times is not. Use for: what `@Volatile` guarantees, and the read-modify-write case it does not cover.
- [API: "Synchronized", Kotlin](https://kotlinlang.org/api/core/kotlin-stdlib/kotlin.jvm/-synchronized/)
  Reference for `@Synchronized`: which monitor the generated JVM method takes, why the annotation is wrong on an extension function (the facade class's monitor, not the receiver's), and the deprecation of the common declaration, an error since Kotlin 2.1. Use for: choosing between the annotation and the `synchronized(lock) { }` function.
- [API: "LazyThreadSafetyMode", Kotlin](https://kotlinlang.org/api/core/kotlin-stdlib/kotlin/-lazy-thread-safety-mode/)
  Reference for the three modes `lazy` takes: `SYNCHRONIZED` (the default, one initialising thread and a visible result), `PUBLICATION` (the initializer may run more than once, one value wins), and `NONE` (no locks, unspecified across threads). Use for: why `by lazy` is thread-safe without being asked, and what the opt-outs actually cost.
- [API: "thread", Kotlin](https://kotlinlang.org/api/core/kotlin-stdlib/kotlin.concurrent/thread.html)
  Reference for the standard library's `thread` function, which creates and by default starts a `java.lang.Thread`, with `isDaemon`, `name` and `priority` as named arguments. Use for: starting a platform thread from Kotlin without the `Thread` subclass or `Runnable` ceremony.
- [Docs: "Aggregate operations", Kotlin](https://kotlinlang.org/docs/collection-aggregate.html)
  Official docs on the operations that reduce a collection to a single value: `count`, `sum`, `average`, the min and max family with its `OrNull` and `By` variants, and `fold`/`reduce` with the initial-value difference between them spelled out on a worked example. Use for: choosing between a named aggregate and a hand-written fold, and for why the same lambda gives different answers to `fold` and `reduce`.
- [Docs: "Grouping", Kotlin](https://kotlinlang.org/docs/collection-grouping.html)
  Official docs on `groupBy()`, which materialises a `Map` of key to member list, and `groupingBy()`, which returns a `Grouping` that operations such as `eachCount()` consume without building those lists. Use for: the difference that decides whether a per-group aggregation allocates in proportion to the input.
- [Docs: "Sequences", Kotlin](https://kotlinlang.org/docs/sequences.html)
  Official docs on `Sequence<T>`: lazy multistep processing, the intermediate/terminal operation split, the four ways to construct one, stateless versus stateful operations, and the explicit warning that laziness has an overhead of its own. Use for: deciding between a collection pipeline and a sequence, and for the element-by-element execution order that lets a bound like `take` cut the work short.
- [Docs: "Collection operations overview", Kotlin](https://kotlinlang.org/docs/collection-operations.html)
  Official docs on how collection operations are declared: essential behaviour as member functions of the collection interfaces, everything else as extension functions, none of them touching the receiver. Use for: why `map` and `filter` are not members of `List`, and why an operation whose result nobody keeps still does all its work.
- [Docs: "Collection transformation operations", Kotlin](https://kotlinlang.org/docs/collection-transformations.html)
  Official docs on `map`, `mapNotNull`, `zip`, `associate`, `flatten`/`flatMap` and `joinToString`, each building a new collection from an existing one. Use for: the transformation half of a collection pipeline, and the fact that every step in a chain materialises a collection of its own.
- [Docs: "Filtering collections", Kotlin](https://kotlinlang.org/docs/collection-filtering.html)
  Official docs on `filter` and its variants, `partition`, and the `any`/`none`/`all` predicate tests, including `all()` returning `true` on an empty collection by vacuous truth. Use for: narrowing a collection, and the empty-input edge case a validation guard written with `all` gets wrong.
- [Docs: "Operator overloading", Kotlin](https://kotlinlang.org/docs/operator-overloading.html)
  Official docs on the fixed set of operator symbols (`+`, `*`, `[]`, comparisons, and more) and the exact function name and `operator` modifier each maps to. Use for: implementing an operator only where it means what the symbol already means to a reader, not as a way to write terse but surprising code.
- [Docs: "Delegation", Kotlin](https://kotlinlang.org/docs/delegation.html)
  Official docs on class delegation via `by`: implementing an interface by forwarding to a held object, with zero boilerplate, and the subtlety that overrides in the derived class aren't seen by the delegate's own internal calls. Use for: the delegation pattern as a language feature instead of hand-written forwarding methods.
- [Docs: "Delegated properties", Kotlin](https://kotlinlang.org/docs/delegated-properties.html)
  Official docs on property delegation (`by lazy { ... }` and custom delegates via `getValue()`/`setValue()`). Use for: reusable property behavior (lazy initialization, change observation) without repeating the same accessor logic on every property that needs it.
- [Docs: "Inline functions", Kotlin](https://kotlinlang.org/docs/inline-functions.html)
  Official docs on the `inline` modifier's actual cost/benefit trade-off, non-local returns, `noinline`/`crossinline`, and reified type parameters, which only work because inlining erases the usual generics-erasure boundary. Use for: why `inline` and `reified` are paired, not two unrelated features.
- [Docs: "Higher-order functions and lambdas", Kotlin](https://kotlinlang.org/docs/lambdas.html)
  Official docs on function types, lambda syntax, trailing-lambda convention, and function literals with receiver (`A.(B) -> C`), the mechanism scope functions like `run` and `apply` are built on. Use for: functions as real values, not just something a lambda is loosely shorthand for.
- [Docs: "Scope functions", Kotlin](https://kotlinlang.org/docs/scope-functions.html)
  Official docs on `let`, `run`, `with`, `apply`, and `also`: the object reference each provides (`it` vs `this`), what each returns (the lambda's result vs the context object), and the function-selection table distinguishing them. Use for: choosing the right scope function by what it actually returns, not by habit or resemblance to another one.
- [Docs: "Extensions", Kotlin](https://kotlinlang.org/docs/extensions.html)
  Official docs on extension functions and properties: called as if they were members, but resolved statically and never actually modifying the extended class or interface. Use for: adding behavior to a type you don't own (including one from a library) without inheritance or a wrapper class.
- [Docs: "Interfaces", Kotlin](https://kotlinlang.org/docs/interfaces.html)
  Official docs on interfaces with default method bodies, abstract versus implemented properties (and why interfaces can't hold backing-field state), and resolving a diamond conflict with `super<Type>.member()`. Use for: modelling shared behavior across unrelated types without inheritance.
- [Docs: "Object declarations and expressions", Kotlin](https://kotlinlang.org/docs/object-declarations.html)
  Official docs on `object` declarations (thread-safe, lazily-initialized singletons), companion objects, and object expressions for anonymous, one-time instances. Use for: what replaces Java's static members and singleton-pattern boilerplate.
- [Docs: "Enum classes", Kotlin](https://kotlinlang.org/docs/enum-classes.html)
  Official docs on enum classes: each constant as a real object, optional per-constant anonymous class bodies, and the `entries`/`valueOf()`/`name`/`ordinal` machinery every enum gets for free. Use for: what an enum actually is beyond a list of names, and how it differs from a sealed class covering the same kind of fixed set.
- [Docs: "Sealed classes and interfaces", Kotlin](https://kotlinlang.org/docs/sealed-classes.html)
  Official docs on sealed hierarchies: every direct subclass known at compile time, and the compiler-enforced exhaustiveness this gives a `when` expression over one, with no `else` branch needed. Use for: type-safe state modelling where an exception or a runtime check would otherwise stand in for the type system.
- [Docs: "Data classes", Kotlin](https://kotlinlang.org/docs/data-classes.html)
  Official docs on what `data class` generates automatically (`equals()`/`hashCode()`, `toString()`, `componentN()`, `copy()`), its requirements, and the subtle rule that only primary-constructor properties participate. Use for: what a data class actually buys over a hand-written class, precisely.
- [Docs: "Classes", Kotlin](https://kotlinlang.org/docs/classes.html)
  Official docs on Kotlin classes: the primary constructor, properties declared directly in the class header, and when the docs themselves recommend a data class or an extension function instead of a plain class. Use for: what a class actually needs to encapsulate, before reaching for one reflexively.
- [Docs: "Properties", Kotlin](https://kotlinlang.org/docs/properties.html)
  Official docs on Kotlin properties: backing fields, custom getters and setters, and why properties replace the getter/setter boilerplate a Java class needs by hand. Use for: what a property actually compiles to, and where a custom accessor is worth writing.
- [Docs: "Conditions and loops", Kotlin](https://kotlinlang.org/docs/control-flow.html)
  Official docs on `if` as an expression, `when` and its exhaustiveness, and Kotlin's `for` loop over ranges and collections. Use for: control flow as expressions producing values, not just statements.
- [Docs: "Ranges and progressions", Kotlin](https://kotlinlang.org/docs/ranges.html)
  Official docs on Kotlin's range operators (`..`, `..<`) and the progressions a `for` loop actually iterates over. Use for: what a range literally is, before treating `for (i in 1..10)` as unexplained syntax.
- [Docs: "Collections overview", Kotlin](https://kotlinlang.org/docs/collections-overview.html)
  Official docs on `List`/`Set`/`Map`, and the read-only/mutable interface pair behind each, including why a mutable collection held by a `val` is still mutable. Use for: the collection-level counterpart to lesson 2's reference-vs-object mutability distinction.
- [Docs: "Equality", Kotlin](https://kotlinlang.org/docs/equality.html)
  Official docs distinguishing structural equality (`==`, calls `equals()`) from referential equality (`===`, same object identity), and which Kotlin types override `equals()` by default. Use for: exactly what `==` means in Kotlin, since it is not Java's `==`.
- [Docs: "Basic syntax overview", Kotlin](https://kotlinlang.org/docs/basic-syntax.html)
  Official overview of Kotlin's core syntax elements, including `val`/`var`, basic types, and control flow, each linked to its own detailed page. Use for: the language's basic building blocks, before idiom (stage 3) asks for more than syntax.
- [Docs: "Coroutines guide", Kotlin](https://kotlinlang.org/docs/coroutines-guide.html)
  Official guide to coroutines: suspending functions, structured concurrency, and dispatchers. Use for: how Kotlin's concurrency model actually works, before comparing it to anything else.
- [JEP 444: "Virtual Threads", OpenJDK](https://openjdk.org/jeps/444)
  The official specification for Java 21's virtual threads: what problem they solve and how they're scheduled under the hood. Use for: the specific comparison point the mission names, coroutines against Java 21 virtual threads.
- [Docs: "Kotlin for Java developers", Kotlin](https://kotlinlang.org/docs/comparison-to-java.html)
  Official docs naming, directly, what's different (and what's deliberately similar) between Kotlin and Java. Use for: locating exactly where a Java habit stops applying.
- [Docs: "Coding conventions", Kotlin](https://kotlinlang.org/docs/coding-conventions.html)
  The official style guide for idiomatic Kotlin: naming, formatting, and idioms the language expects, as opposed to code that merely compiles. Use for: recognizing Kotlin written with a Java accent versus Kotlin written idiomatically.
- [Site: "Kotlin on Android", Android Developers](https://developer.android.com/kotlin)
  Official entry point for Kotlin's Android-specific idioms and libraries (coroutines with lifecycle-aware scopes, Android KTX). Use for: the Android half of this mission's coverage, where it diverges from a backend/server context.

## Gaps

- No source yet specifically contrasting Kotlin coroutines against Java 21 virtual threads side by side (as opposed to reading the two official specs separately and inferring the comparison); worth closing once lesson design reaches that stage.
