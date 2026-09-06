---
title: Kotlin
description: "Own Kotlin on the JVM: null safety, coroutines, and idiomatic Kotlin from zero"
type: topic
---

# Learning: Kotlin

Become the engineer trusted to own Kotlin on a team, in a backend service or an Android app: able to model a domain idiomatically, write and reason about coroutines and `Flow`, ship a typed, tested Kotlin service or Android component, and review someone's Kotlin and name concretely what a construct is costing them.

**Latest lesson:** [1. Null Safety](lessons/0001-null-safety.md)

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

Eight stages, zero to senior. Not a lesson list: a stage takes several lessons, and the boundaries are soft.

| Stage | Lessons | Covers | Done when |
|---|---|---|---|
| 1. Foundations | 0001 to 0006 | Null safety, `val`/`var` and immutability, values vs references, basic types and string templates, collections basics (`List`/`Set`/`Map`, mutable vs read-only), control flow (`when`, ranges, `for`) | Can predict nullability and mutability without running the code |
| 2. Modelling | 0007 to 0012 | Classes and properties, data classes, sealed classes and exhaustive `when`, enums, object declarations and companion objects, interfaces with default methods | Models a domain without reaching for a class-per-thing hierarchy first |
| 3. Idiom | 0013 to 0018 | Extension functions, scope functions (`let`/`run`/`with`/`apply`/`also`), higher-order functions and lambdas, inline functions and reified generics, delegation (`by`), operator overloading | Writes Kotlin a reviewer would not describe as translated Java |
| 4. Collections and sequences | 0019 to 0021 | Kotlin's collection operators, lazy `Sequence` vs eager collections, grouping and folding | Chooses between a collection pipeline and a sequence and can defend the cost of each |
| 5. Concurrency | 0022 to 0027 | Threads and the JVM memory model basics, suspend functions and coroutine builders, structured concurrency, coroutine context and dispatchers, `Flow`, cancellation and exception handling | Can predict what a concurrent coroutine program does before running it, and compare the model to Java virtual threads |
| 6. Testing and build | 0028 to 0030 | Kotlin test frameworks, mocking, the Gradle Kotlin DSL and dependency management | Someone else can clone, build, test and run it |
| 7. Shipping a service | 0031 to 0033 | Structuring a typed, tested backend service, Android-specific idioms where the platform diverges, generics and variance (`in`/`out`) | Has shipped a typed, tested Kotlin backend service or Android component |
| 8. Judgment | 0034 to 0035 | Java interop, reviewing Kotlin and naming precisely what a construct is costing | Trusted to make the call and explain it to someone else |

## Lessons

Work through these in order.

| # | Lesson | Teaches |
|---|---|---|
| [0001](lessons/0001-null-safety.md) | Null Safety | Moving "could this be null" from a runtime surprise to a compile-time question, and how the Java habit undoes it |

## Reference

- [Glossary](GLOSSARY.md): canonical terms for this topic
- [Resources](RESOURCES.md): trusted sources

## How this works

Each lesson is short and self-contained. Answer keys are collapsed: recall first, then open them. The real-world reps matter more than the reading, and spacing them out is the point. Anything still unclear at the end of a lesson is worth chasing to its primary source before moving on.
