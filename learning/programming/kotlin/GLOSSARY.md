---
title: Glossary
description: "Canonical terms for Kotlin"
type: glossary
---

# Kotlin Glossary

Canonical terms for owning Kotlin on the JVM, and for naming precisely where a Java habit produces Kotlin that compiles but reads badly.

## Terms

**Not-null assertion (`!!`)**:
An operator that forces a nullable value to be treated as non-null, throwing a `NullPointerException` immediately if it's actually `null`. Routine use to silence a compile error, rather than backed by specific evidence, recreates the runtime crash null safety exists to prevent.
_Avoid_: bang-bang (informal; name the operator by what it does)

**Platform type**:
The type Kotlin assigns to a value returned from unannotated Java code, since it can't determine nullability from Java alone. Treat it as possibly null unless there's positive evidence otherwise.
_Avoid_: none in particular, but do not treat it as equivalent to a Kotlin non-nullable type
