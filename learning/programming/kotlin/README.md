---
title: Kotlin
description: "Own Kotlin on the JVM: null safety, coroutines, and idiomatic Kotlin from zero"
type: topic
---

# Learning: Kotlin

Become the engineer trusted to own Kotlin on a team, in a backend service or an Android app: able to model a domain idiomatically, write and reason about coroutines and `Flow`, ship a typed, tested Kotlin service or Android component, and review someone's Kotlin and name concretely what a construct is costing them.

**Latest lesson:** [22. Threads and the Memory Model](lessons/0022-threads-and-the-memory-model.md)

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

## Reference

- [Glossary](GLOSSARY.md): canonical terms for this topic
- [Resources](RESOURCES.md): trusted sources

## How this works

Each lesson is short and self-contained. Answer keys are collapsed: recall first, then open them. The real-world reps matter more than the reading, and spacing them out is the point. Anything still unclear at the end of a lesson is worth chasing to its primary source before moving on.
