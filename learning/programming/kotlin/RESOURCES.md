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
