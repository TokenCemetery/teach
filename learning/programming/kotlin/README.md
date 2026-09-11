---
title: Kotlin
description: "Own Kotlin on the JVM: null safety, coroutines, and idiomatic Kotlin from zero"
type: topic
---

# Learning: Kotlin

Become the engineer trusted to own Kotlin on a team, in a backend service or an Android app: able to model a domain idiomatically, write and reason about coroutines and `Flow`, ship a typed, tested Kotlin service or Android component, and review someone's Kotlin and name concretely what a construct is costing them.

**Latest lesson:** [43. Persistence](lessons/0043-persistence.md)

## Success looks like

- Model a domain with data classes, sealed classes and enums, and know when null safety, not an exception, is the correct signal.
- Write and reason about coroutines and `Flow`, and compare the model to Java virtual threads.
- Ship a typed, tested Kotlin backend service or Android component, designed idiomatically.
- Given Kotlin written with a habit that merely compiles (defensive null checks instead of the type system, a callback instead of a coroutine), name the habit and rewrite it idiomatically.

## Constraints

- Assumes no prior Kotlin. Experience in Java or another JVM language shortens the early stages but is not required, and it brings habits Kotlin punishes quietly: defensive null checks instead of the type system, a class where a data class or sealed type would say it better.
- Covers both backend/server-side and Android contexts, touching each where they diverge.
- Needs only a JDK, the Kotlin toolchain and a terminal; Android Studio only where Android-specific material needs it.

## Out of scope

- JVM internals past what explains Kotlin's own compiled behaviour (full garbage-collector tuning, profiling, bytecode engineering): that is `programming/java`'s runtime stage, linked to for further depth rather than retaught.
- Other JVM languages (Java, Scala, Clojure, Groovy) as subjects in their own right, though a contrast appears where it clarifies a Kotlin idiom.

## The arc

Ten stages, zero to senior. Not a lesson list: a stage takes several lessons, and the boundaries are soft.

| Stage | Lessons | Covers | Done when |
|---|---|---|---|
| 1. Foundations | 0001 to 0006 | Null safety, `val`/`var` and immutability, values vs references, basic types and string templates, collections basics (`List`/`Set`/`Map`, mutable vs read-only), control flow (`when`, ranges, `for`) | Can predict nullability and mutability without running the code |
| 2. Modelling | 0007 to 0012 | Classes and properties, data classes, sealed classes and exhaustive `when`, enums, object declarations and companion objects, interfaces with default methods | Models a domain without reaching for a class-per-thing hierarchy first |
| 3. Idiom | 0013 to 0018 | Extension functions, scope functions (`let`/`run`/`with`/`apply`/`also`), higher-order functions and lambdas, inline functions and reified generics, delegation (`by`), operator overloading | Writes Kotlin a reviewer would not describe as translated Java |
| 4. Collections and sequences | 0019 to 0021 | Kotlin's collection operators, lazy `Sequence` vs eager collections, grouping and folding | Chooses between a collection pipeline and a sequence and can defend the cost of each |
| 5. Concurrency | 0022 to 0027 | Threads and the JVM memory model basics, suspend functions and coroutine builders, structured concurrency, coroutine context and dispatchers, `Flow`, cancellation and exception handling | Can predict what a concurrent coroutine program does before running it, and compare the model to Java virtual threads |
| 6. Testing and build | 0028 to 0030 | Kotlin test frameworks, mocking, the Gradle Kotlin DSL and dependency management | Someone else can clone, build, test and run it |
| 7. Shipping a service | 0031 to 0033 | Structuring a typed, tested backend service, Android-specific idioms where the platform diverges, generics and variance (`in`/`out`) | Has structured a typed, tested Kotlin backend service or Android component; stage 10 completes it with an HTTP layer, configuration, logging and persistence |
| 8. Judgment | 0034 to 0035 | Java interop, reviewing Kotlin and naming precisely what a construct is costing | Trusted to make the call and explain it to someone else |
| 9. Advanced Idiom | 0036 to 0039 | Type-safe builders and DSLs, `value class`/`@JvmInline`, `kotlinx.serialization`, `Result` and error-handling idioms | Writes a small type-safe builder DSL, a zero-cost wrapper type, and a `Result`-based error path idiomatically |
| 10. Completing the Service | 0040 to 0043 | An HTTP layer, configuration, logging, and persistence for the Kotlin backend service stage 7 started structuring | Ships a Kotlin backend service with a routed HTTP layer, externalized configuration, structured logging, and database access, not only a structured shell |

## Lessons

Work through these in order.

| # | Lesson | Teaches |
|---|---|---|
| [0001](lessons/0001-null-safety.md) | Null Safety | Moving "could this be null" from a runtime surprise to a compile-time question, and how the Java habit undoes it |
| [0002](lessons/0002-val-var-and-immutability.md) | val/var and Immutability | Why val is the default worth defending, what it actually guarantees (and doesn't), and the Java habit of reaching for var out of reflex |
| [0003](lessons/0003-values-vs-references.md) | Values vs References | Why == means something different in Kotlin than in Java, and the specific bug the Java habit of writing == produces |
| [0004](lessons/0004-basic-types-and-string-templates.md) | Basic Types and String Templates | Why Kotlin has no primitives at the language level, and string templates as a language feature rather than concatenation with extra syntax |
| [0005](lessons/0005-collections-basics.md) | Collections Basics | List, Set, and Map as read-only-by-interface collections, and why a mutable collection held by a val is still mutable |
| [0006](lessons/0006-control-flow.md) | Control Flow | if and when as expressions that produce values, what a range actually is, and the stage 1 capstone of predicting nullability and mutability without running code |
| [0007](lessons/0007-classes-and-properties.md) | Classes and Properties | Properties as the replacement for Java's getter/setter boilerplate, and why the Kotlin docs themselves say to reach for a class last |
| [0008](lessons/0008-data-classes.md) | Data Classes | What data class actually generates, and the subtle rule that only primary-constructor properties participate in any of it |
| [0009](lessons/0009-sealed-classes-and-exhaustive-when.md) | Sealed Classes and Exhaustive when | How sealing a hierarchy turns a when's exhaustiveness from a manual promise into a compiler-checked guarantee |
| [0010](lessons/0010-enums.md) | Enums | Each enum constant as a real object with its own state and behavior, and precisely where an enum fits over a sealed class |
| [0011](lessons/0011-object-declarations-and-companion-objects.md) | Object Declarations and Companion Objects | Singletons declared, not implemented by hand, and companion objects as Kotlin's actual replacement for Java's static members |
| [0012](lessons/0012-interfaces-with-default-methods.md) | Interfaces with Default Methods | Why a Kotlin interface can implement behavior but never hold state, and how to resolve a diamond conflict explicitly |
| [0013](lessons/0013-extension-functions.md) | Extension Functions | Adding behavior to a type without inheritance, and the static-dispatch gotcha that trips people up the first time they hit it |
| [0014](lessons/0014-scope-functions.md) | Scope Functions | Choosing among let, run, with, apply, and also by what each one returns and how it exposes the object, not by habit |
| [0015](lessons/0015-higher-order-functions-and-lambdas.md) | Higher-Order Functions and Lambdas | Function types as real types, trailing-lambda syntax, and the receiver mechanism scope functions are actually built on |
| [0016](lessons/0016-inline-functions-and-reified-generics.md) | Inline Functions and Reified Generics | Why inline exists to remove a real cost, why it enables non-local returns, and why reified type parameters only work because of inlining |
| [0017](lessons/0017-delegation.md) | Delegation | Implementing an interface by forwarding to a held object with zero boilerplate, and reusable property behavior via by lazy and custom delegates |
| [0018](lessons/0018-operator-overloading.md) | Operator Overloading | Operators as ordinary named functions with a fixed symbol mapping, and the actual discipline of implementing one only where it means what the symbol already means |
| [0019](lessons/0019-collection-operators.md) | Collection Operators | The collection operators as extension functions that return a new collection eagerly, and the Java Stream habit that misprices a chain of them |
| [0020](lessons/0020-sequences-and-laziness.md) | Sequences and Laziness | Why the same operator chain behaves differently on a Sequence, what a terminal operation is actually for, and when laziness costs more than it saves |
| [0021](lessons/0021-grouping-and-folding.md) | Grouping and Folding | Aggregating with fold and reduce, grouping without building the groups, and the stage 4 capstone of defending what a pipeline costs |
| [0022](lessons/0022-threads-and-the-memory-model.md) | Threads and the Memory Model | Why Kotlin has no memory model of its own on the JVM, the three constructs it spells as annotations instead of keywords, and the two guarantees a val does not give you |
| [0023](lessons/0023-suspend-functions-and-coroutine-builders.md) | Suspend Functions and Coroutine Builders | What suspend actually changes about a function, the three builders and what each one returns, and why suspending code still reads top to bottom |
| [0024](lessons/0024-structured-concurrency.md) | Structured Concurrency | The parent and child tree that makes cancellation predictable, why a scope you own is a scope you must cancel, and what GlobalScope actually costs |
| [0025](lessons/0025-coroutine-context-and-dispatchers.md) | Coroutine Context and Dispatchers | The context as a set of elements combined with plus, which dispatcher belongs to which kind of work, and the one context element that silently breaks structured concurrency |
| [0026](lessons/0026-flows.md) | Flows | A flow as the asynchronous third option after a list and a sequence, what cold actually means for each collector, and the context rule a flow builder enforces at runtime |
| [0027](lessons/0027-cancellation-and-exception-handling.md) | Cancellation and Exception Handling | Why cancellation is cooperative and what makes code ignore it, why a CancellationException is not a failure, and how the coroutine model compares with Java virtual threads |
| [0028](lessons/0028-test-frameworks.md) | Test Frameworks | The layers a Kotlin test actually sits on, why runTest's virtual time stops at the dispatcher boundary, and what that forces on the design of the code under test |
| [0029](lessons/0029-mocking.md) | Mocking | Why final-by-default changes what mocking means in Kotlin, what MockK does for the constructs that are not methods on an object, and when finality is telling you a seam is missing |
| [0030](lessons/0030-gradle-and-dependency-management.md) | Gradle and Dependency Management | The Kotlin DSL's type-safe accessors and where they run out, why a Gradle configuration is not a Maven scope, and the resolution rule that decides which version reaches the classpath |
| [0031](lessons/0031-structuring-a-service.md) | Structuring a Service | Where Kotlin files actually go and what goes inside a class, and the four decisions from earlier stages that decide whether a service is testable |
| [0032](lessons/0032-android-divergences.md) | Android Divergences | The scopes Android owns on your behalf, main-safety as a contract the callee keeps, and why composition lifetime is not lifecycle lifetime |
| [0033](lessons/0033-generics-and-variance.md) | Generics and Variance | Declaration-site variance in place of wildcards, what out and in actually promise about a type parameter, and how to read a projected signature |
| [0034](lessons/0034-java-interop.md) | Java Interop | Why the boundary is asymmetric, what a platform type costs you and how to pay it back, and which annotations you owe a Java caller |
| [0035](lessons/0035-reviewing-kotlin.md) | Reviewing Kotlin | Turning the arc into a review instrument: the cost each habit hides, the shape of a comment that names it, and what not to review |
| [0036](lessons/0036-type-safe-builders-and-dsls.md) | Type-Safe Builders and DSLs | Lesson 15 taught the receiver-style function type that lets run and apply expose this; a type-safe builder is that exact mechanism nested recursively, and @DslMarker is the one attribute that keeps a nested builder from silently reaching the wrong receiver |
| [0037](lessons/0037-value-classes.md) | value class and @JvmInline | A value class is the fix for primitive obsession that the JVM usually lets you have for free, represented as its own underlying value with no wrapper object at all, except in the specific, documented cases where the compiler still has to box it |
| [0038](lessons/0038-kotlinx-serialization.md) | kotlinx.serialization | A Java habit reaches for a library that inspects a class's shape through reflection at runtime; kotlinx.serialization generates that same logic at compile time instead, through a compiler plugin, which is exactly what lets it work on Kotlin targets that have no runtime reflection API at all |
| [0039](lessons/0039-result-and-error-handling.md) | Result and Error-Handling Idioms | runCatching wraps any Throwable into a Result, which is exactly the problem inside a coroutine, since lesson 27's cooperative cancellation depends on CancellationException propagating uncaught, and runCatching swallows it into an ordinary failure unless a caller explicitly rethrows it first |
| [0040](lessons/0040-http-layer.md) | HTTP Layer | Lesson 31 deliberately deferred routing to whichever framework you chose; Ktor's own routing block turns out to be lesson 36's type-safe builder DSL applied to HTTP, nothing installed by default, and request-parameter extraction that fails loudly rather than silently binding the wrong thing |
| [0041](lessons/0041-configuration.md) | Configuration | A service's actual behavior, its port, its database URL, its secrets, has to change across environments without recompiling a single line, and Ktor's configuration file plus one specific, easy-to-miss substitution idiom is how a default and an environment override live in exactly one place |
| [0042](lessons/0042-logging.md) | Logging | SLF4J silently does nothing until a real logging backend is added as a dependency, and CallLogging's per-request MDC values are silently invisible until the log pattern itself is updated to print them, the same shape of trap appearing twice in the same lesson |
| [0043](lessons/0043-persistence.md) | Persistence | Exposed's DSL is another type-safe builder, and it is mostly blocking underneath, since it wraps JDBC; the stage 10 capstone is dispatching that blocking work correctly instead of stalling whatever thread happened to be running the request, and revisiting what stage 7's shipped service actually needed all along |

## Reference

- [Glossary](GLOSSARY.md): canonical terms for this topic
- [Resources](RESOURCES.md): trusted sources

## How this works

Each lesson is short and self-contained. Answer keys are collapsed: recall first, then open them. The real-world reps matter more than the reading, and spacing them out is the point. Anything still unclear at the end of a lesson is worth chasing to its primary source before moving on.
