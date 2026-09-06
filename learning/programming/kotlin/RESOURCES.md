---
title: Resources
description: "Trusted sources for Kotlin"
type: resources
---

# Kotlin Resources

## Knowledge

- [Docs: "Null safety", Kotlin](https://kotlinlang.org/docs/null-safety.html)
  Official docs for Kotlin's nullable/non-nullable type distinction, the safe-call and Elvis operators, and the platform types a Java interop boundary introduces. Use for: the primary mechanism behind writing null safety into the type system instead of into defensive checks.
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
