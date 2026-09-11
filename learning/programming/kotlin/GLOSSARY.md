---
title: Glossary
description: "Canonical terms for Kotlin"
type: glossary
---

# Kotlin Glossary

Canonical terms for owning Kotlin on the JVM, and for naming precisely where a Java habit produces Kotlin that compiles but reads badly.

## Terms

**@DslMarker**:
An annotation applied to every receiver type in a type-safe builder DSL, restricting implicit member access inside a nested lambda to only the nearest enclosing receiver. Reaching an outer receiver is still possible, but only by naming it explicitly (`this@outer.member { }`).
_Avoid_: sharing one marker across two unrelated DSLs (each DSL should define its own, so unrelated builder hierarchies can coexist and nest without one's scope restriction interfering with the other's)

**@Serializable**:
Marks a class for `kotlinx.serialization`'s compiler plugin, which generates the class's actual serialization logic (a "visitor") at compile time. Requires both the `kotlin("plugin.serialization")` Gradle plugin and the runtime dependency; the plugin alone missing leaves the annotation compiling with no generated code behind it.
_Avoid_: assuming the annotation alone does anything (without the compiler plugin, `@Serializable` compiles as an ordinary, unprocessed annotation, silently generating no serialization code at all)

**Configuration file (Ktor)**:
`application.conf` (HOCON) or `application.yaml`, loaded automatically by `EngineMain` from resources, supporting environment-variable substitution (`${ENV}`, or `${?ENV}` for an optional override of a prior default). Custom, application-specific sections can sit alongside Ktor's own reserved `ktor { }` block in the same file.
_Avoid_: a bare required substitution with no prior default (`value = ${ENV}` alone fails outright if the variable is absent; pair a default assignment with the optional `${?ENV}` form instead)

**Exposed**:
JetBrains' Kotlin SQL library on JDBC, offering a type-safe DSL (another instance of the type-safe builder mechanism) and a lighter DAO layer. Mostly blocking underneath, since JDBC itself is; `newSuspendedTransaction`/`suspendedTransactionAsync` (or `suspendTransaction()` with R2DBC) are the coroutine-friendly entry points, and always start a fresh transaction rather than joining one already in progress.
_Avoid_: calling an ordinary `transaction { }` block directly inside a suspending function (it runs synchronously on the calling thread, blocking it for the query's full duration)

**MDC (Mapped Diagnostic Context)**:
A per-request diagnostic value (`mdc("name") { call -> ... }` in Ktor's `CallLogging`), scoped to that specific call's lifetime and removed automatically afterward. Correctly computed the whole time, but invisible in actual log output unless the log pattern is separately updated to print MDC content (`%X` in Logback).
_Avoid_: assuming adding an `mdc(...)` block alone makes the value appear in logs (the pattern itself must also be updated to print MDC content, a second, easy-to-forget step)

**Not-null assertion (`!!`)**:
An operator that forces a nullable value to be treated as non-null, throwing a `NullPointerException` immediately if it's actually `null`. Routine use to silence a compile error, rather than backed by specific evidence, recreates the runtime crash null safety exists to prevent.
_Avoid_: bang-bang (informal; name the operator by what it does)

**Platform type**:
The type Kotlin assigns to a value returned from unannotated Java code, since it can't determine nullability from Java alone. Treat it as possibly null unless there's positive evidence otherwise.
_Avoid_: none in particular, but do not treat it as equivalent to a Kotlin non-nullable type

**Result&lt;T&gt;**:
A value holding either a successful result or a caught `Throwable`, returned by `runCatching` instead of letting an exception propagate. Best suited to a single, expected, recoverable failure mode; several genuinely distinct failure kinds a caller must tell apart are better served by a sealed hierarchy instead.
_Avoid_: wrapping every function in one reflexively (a genuine bug, an invariant violation, is often better left to crash loudly as an uncaught exception than quietly returned as a `Result.failure`)

**runCatching**:
Runs a block and wraps its outcome in a `Result<T>`, catching any `Throwable` the block throws, including `CancellationException`. Inside a coroutine, a caught `CancellationException` must be explicitly rethrown before treating anything else as an ordinary failure, since no stdlib variant does this automatically.
_Avoid_: using it unguarded inside a suspend function or coroutine builder (it can silently swallow a `CancellationException`, breaking structured concurrency's cancellation propagation)

**Server plugin (Ktor)**:
A capability (routing included) installed explicitly, never enabled by default, since Ktor activates no plugins on its own. Can be installed once, globally, or scoped to a specific subset of routes with its own separate configuration.
_Avoid_: assuming routing (or any other capability) is available without installing it (Ktor's default is nothing installed at all; every capability is opted into explicitly)

**SLF4J**:
The logging API Ktor uses on the JVM, decoupled from any specific implementation. With no real backend (Logback, Log4j) added as a dependency, it silently falls back to a no-operation implementation: logging calls compile and run, producing no output at all.
_Avoid_: assuming logging calls work just because they compile (SLF4J is only the API; a concrete backend dependency has to be present for anything to actually be written)

**Type-safe builder (DSL)**:
A builder function taking a receiver-style lambda parameter (`T.() -> R`), nested recursively, so a caller can write nested blocks that read like their own small, structured language while every call resolves against an ordinary receiver's members. The construct receiver-style function types (lesson 15) exist for.
_Avoid_: treating it as a distinct compiler feature (it's the same receiver-style function type mechanism used elsewhere, applied recursively, with no additional language support needed beyond `@DslMarker`'s scope restriction)

**value class (`@JvmInline`)**:
A class wrapping exactly one property, with no identity of its own, represented at runtime as either the plain underlying value (unboxed, no allocation) or a compiler-generated wrapper (boxed), boxed whenever it's used as another type (`Any`, a generic collection, an interface reference) or when both its underlying type and usage site are nullable at once.
_Avoid_: assuming it's always zero-cost (the unboxed representation holds only where the documented rule says it does; a generic collection or an interface reference boxes it like any other type)
