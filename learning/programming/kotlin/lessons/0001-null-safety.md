---
title: 1. Null Safety
description: Moving "could this be null" from a runtime surprise to a compile-time question, and how the Java habit undoes it
type: lesson
---

# Lesson 1. Null Safety

**Mission link:** Null safety is named first in the mission for a reason: it's the single feature most responsible for Kotlin code that compiles but still reads (and behaves) like defensive Java, when the type system isn't trusted to do its job.
**Primary source:** [Docs: "Null safety", Kotlin](https://kotlinlang.org/docs/null-safety.html)
**Prerequisites:** none

## Know this

### The problem this replaces

In Java, every reference type can hold `null`, and the compiler gives you no help telling which references you actually need to check. A `NullPointerException` is a runtime surprise, not a compile-time one. The professional Java habit this produces is defensive: `if (x != null)` checks scattered wherever a reference *might* be null, because the type alone never tells you.

### Nullability is part of the type in Kotlin

Kotlin splits every type into two: `String` (never holds `null`, guaranteed by the compiler) and `String?` (may hold `null`, and the compiler forces you to handle that possibility before you can use it as a plain `String`). This isn't a convention or a lint rule; it's enforced at every assignment and function signature. A function that takes a `String` parameter is guaranteed, by the type system, to never receive `null` there, and the compiler will not compile code that tries to pass one.

This turns "could this be null here?" from a question you answer by reading carefully (or don't, and find out at runtime) into a question the compiler already answered for you before the code runs.

### The two operators that make this ergonomic

- **Safe call (`?.`)**: `user?.name` evaluates to `null` immediately if `user` is `null`, instead of throwing. It's the null-aware version of just calling `.name`, and it short-circuits: `user?.address?.city` stops at the first `null` link in the chain.
- **Elvis (`?:`)**: `user?.name ?: "unknown"` supplies a default when the left side is `null`. Together, these two cover the large majority of places a Java method would reach for an `if (x != null)` check.

### Where the Java habit shows up in otherwise-compiling Kotlin

Two Java-shaped anti-patterns show up constantly in code written by someone still thinking in Java, and both compile fine, which is exactly why they're worth naming explicitly:

- **Redundant null checks on already-non-nullable types.** Writing `if (name != null) { ... }` where `name` has type `String` (not `String?`) is checking something the compiler has already guaranteed can't happen. It compiles, because it's not wrong, just pointless: the check can never be false, and it signals the author doesn't trust (or hasn't noticed) that the type already rules this out.
- **Reaching for `!!` to make the compiler stop complaining.** The not-null assertion operator `!!` forces a nullable value to be treated as non-null, throwing a `NullPointerException` immediately if it turns out to actually be `null`. Using it as a routine way to silence a compile error, rather than in a spot where you have specific, positive evidence the value can't be null, reintroduces the exact runtime crash null safety exists to prevent. A codebase with `!!` scattered everywhere has recreated Java's problem inside Kotlin's syntax.

### Java interop introduces a subtler case: platform types

When Kotlin calls a Java method that has no nullability annotation, Kotlin can't know whether it returns a nullable or non-nullable value. It marks the result a **platform type** (written `String!` in error messages, though you can't write that syntax yourself), and lets you treat it as either nullable or non-nullable, trusting you to know which. Treat an unannotated Java method's return value as if it might be `null` unless you have positive evidence otherwise (a `@NotNull` annotation, or documented behavior); this boundary is exactly where null safety's guarantees stop being automatic.

## Practice

1. ▢ In one sentence, what is the fundamental difference between `String` and `String?` in Kotlin?

<details markdown="1"><summary>Check</summary>

`String` is guaranteed by the compiler to never hold `null`, at every assignment and function call site; `String?` may hold `null`, and the compiler requires you to handle that possibility (via a safe call, an Elvis default, a null check, or `!!`) before treating it as a plain `String`.

</details>

2. ▢ A developer with a Java background writes a Kotlin function `fun greet(name: String)`, and inside its body writes `if (name != null) { println("Hello, $name") }`. What's wrong with this, and what does it reveal?

<details markdown="1"><summary>Check</summary>

The check is redundant: `name`'s type is `String`, not `String?`, so the compiler already guarantees it can never be `null` at that point; the `if` can never evaluate to false. It reveals a Java habit carried over unchanged: writing a defensive null check reflexively, without trusting (or checking) that Kotlin's type system already ruled the case out.

</details>

3. ▢ A codebase has `!!` scattered throughout it, used any time the compiler complains about a possible null. Explain why this is worse than it looks, in terms of what null safety was supposed to prevent.

<details markdown="1"><summary>Hint</summary>

What does `!!` do at runtime if the value actually turns out to be `null`?

</details>

<details markdown="1"><summary>Check</summary>

`!!` throws a `NullPointerException` immediately if the value is actually `null` at that point, which is precisely the runtime crash Kotlin's null safety was designed to move to compile time. Using `!!` as a routine way to silence the compiler, rather than in a spot backed by specific evidence the value can't be null, recreates Java's exact failure mode inside Kotlin: a crash the type system had already flagged as possible, ignored rather than handled.

</details>

4. ▢ Kotlin code calls an unannotated Java method that returns `String`. What type does Kotlin actually give that return value?

   - a) `String`, since Java declared it non-generic and returning a reference type
   - b) `String?`, to be maximally safe by default
   - c) A platform type, which Kotlin lets you treat as either `String` or `String?`, trusting the caller to know which
   - d) A compile error, since Kotlin requires all Java interop to be annotated first

<details markdown="1"><summary>Check</summary>

**c)** A platform type. Kotlin can't determine nullability from unannotated Java code, so rather than guessing, it lets the caller decide how to treat it, which means the safety net isn't automatic at this boundary the way it is for pure Kotlin code.

</details>

## Real-world reps

- [ ] Find a Kotlin file you've written or have access to. Search it for `!!` and, for each occurrence, decide whether it's backed by real evidence the value can't be null, or whether it's silencing a check that should be handled properly instead.
- [ ] Find (or write) a Kotlin function that calls into an unannotated Java method. Check what type Kotlin infers for the result, and confirm whether your code is treating it as nullable or not.
- [ ] Tomorrow: rewrite one Java-habit null check you find (redundant `if (x != null)` on a non-nullable type, or a defensive check that could be a safe call plus Elvis instead) into idiomatic Kotlin.

## Going further

- [Docs: "Kotlin for Java developers", Kotlin](https://kotlinlang.org/docs/comparison-to-java.html)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
