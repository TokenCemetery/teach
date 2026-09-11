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

**Not-null assertion (`!!`)**:
An operator that forces a nullable value to be treated as non-null, throwing a `NullPointerException` immediately if it's actually `null`. Routine use to silence a compile error, rather than backed by specific evidence, recreates the runtime crash null safety exists to prevent.
_Avoid_: bang-bang (informal; name the operator by what it does)

**Platform type**:
The type Kotlin assigns to a value returned from unannotated Java code, since it can't determine nullability from Java alone. Treat it as possibly null unless there's positive evidence otherwise.
_Avoid_: none in particular, but do not treat it as equivalent to a Kotlin non-nullable type

**Type-safe builder (DSL)**:
A builder function taking a receiver-style lambda parameter (`T.() -> R`), nested recursively, so a caller can write nested blocks that read like their own small, structured language while every call resolves against an ordinary receiver's members. The construct receiver-style function types (lesson 15) exist for.
_Avoid_: treating it as a distinct compiler feature (it's the same receiver-style function type mechanism used elsewhere, applied recursively, with no additional language support needed beyond `@DslMarker`'s scope restriction)
