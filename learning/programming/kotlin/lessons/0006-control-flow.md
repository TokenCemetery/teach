---
title: 6. Control Flow
description: if and when as expressions that produce values, what a range actually is, and the stage 1 capstone of predicting nullability and mutability without running code
type: lesson
---

# Lesson 6. Control Flow

**Mission link:** This is stage 1's capstone. Every prior lesson (null safety, val/var, equality, basic types, collections) built the vocabulary for reasoning about a value without running it; this lesson is `if`, `when`, ranges, and `for`, the constructs that route which value gets produced, closing stage 1's "predict nullability and mutability without running the code."
**Primary source:** [Docs: "Conditions and loops", Kotlin](https://kotlinlang.org/docs/control-flow.html)
**Prerequisites:** [Lesson 5](0005-collections-basics.md), [Platform type](../GLOSSARY.md)

## Warm-up

1. ▢ Why does declaring `val nums: MutableList<Int> = mutableListOf(1, 2, 3)` still allow `nums.add(4)` to compile?

<details markdown="1"><summary>Check</summary>

`val` only guarantees `nums` is never reassigned to a different list object; the mutable interface (`MutableList`) is what permits mutating the object itself. The two guarantees are independent and both apply here.

</details>

2. ▢ Why is "read-only" not the same guarantee as "immutable" for a `List` reference?

<details markdown="1"><summary>Check</summary>

A `List` reference only restricts what that specific reference's interface permits; if the same underlying object is also reachable through a `MutableList` reference elsewhere, mutations made there are visible through the read-only reference too, since it's the same object. Read-only describes the reference's permissions, not an unbreakable guarantee about the data.

</details>

## Know this

### `if` is an expression in Kotlin, not just a statement

In Java, `if` only controls which statements execute; producing a value conditionally needs the separate ternary `?:` operator. In Kotlin, `if` itself is an expression that evaluates to a value: `val max = if (a > b) a else b` requires no separate ternary syntax, since `if`/`else` already produces one. This matters beyond style: because it's an expression, every branch has to produce a compatible type, and the compiler enforces that an `if` used as an expression has an `else` branch (otherwise there's no value to produce when the condition is false).

### `when` replaces a long `if`/`else if` chain, and can be exhaustive

`when` matches a value against multiple branches, functioning like a more powerful `switch`: branches can match multiple values, ranges, types (`is String`), or arbitrary boolean conditions, not just exact constants. Used as an expression (assigned to a variable, returned from a function), the compiler requires it to be **exhaustive**, covering every possible case, either explicitly or via an `else` branch; sealed classes and enums (lessons 9-10) get compiler-checked exhaustiveness without needing `else` at all, since the compiler knows every possible subtype or value up front. Used as a statement (not assigned anywhere), exhaustiveness isn't enforced, which is itself a signal worth noticing: a `when` whose result you're not using is a different, weaker guarantee than one whose result the compiler is forced to account for completely.

### A range is a real value, not loop syntax

`1..10` isn't special `for`-loop syntax; it's an actual `IntRange` value, constructed via the `rangeTo()` function that the `..` operator calls, and it can be stored in a variable, checked with `in` (`5 in 1..10`), or iterated directly. `1..<10` (or `until`) produces a range excluding the upper bound, the equivalent of the common `i < 10` loop condition. `for (i in 1..10)` works because `for` iterates over anything that exposes an iterator, and a range is exactly such a value, not a special case the `for` loop hardcodes.

### `for` iterates anything iterable; it isn't specialized per collection type

Kotlin's `for (item in collection)` works identically over a `List`, a `Set`, a `Map` (destructuring each entry into a key and value), a range, or any custom type exposing the right iteration protocol. There's no separate "for-each" syntax distinct from a plain `for`, the way some languages distinguish an index-based loop from an enhanced one; ranges and collections both satisfy the same iteration contract, which is why `for (i in 1..10)` and `for (item in list)` look identical despite iterating over structurally different things.

## Practice

1. ▢ Why does an `if` used as an expression require an `else` branch, while an `if` used purely as a statement doesn't?

<details markdown="1"><summary>Check</summary>

As an expression, `if` must produce a value regardless of which branch runs; without an `else`, there's no value to produce when the condition is false, so the compiler requires both branches when the result is actually used as a value. As a plain statement (result discarded), there's no value being produced at all, so an unmatched condition just means nothing happens, which is fine.

</details>

2. ▢ Why does the compiler enforce exhaustiveness on a `when` used as an expression but not on one used as a statement?

<details markdown="1"><summary>Hint</summary>

Consider what "exhaustive" is actually protecting against: an unhandled case producing no value, or an unhandled case simply doing nothing.

</details>

<details markdown="1"><summary>Check</summary>

As an expression, every possible input has to map to some value, since the result is actually used; an unhandled case would mean there's no value to produce, which the compiler refuses to allow silently. As a statement, an unhandled case just means nothing happens for that input, which is a much weaker requirement the compiler doesn't need to enforce.

</details>

3. ▢ What is `1..10` actually, as a Kotlin value, and how does `1..<10` differ from it?

<details markdown="1"><summary>Check</summary>

`1..10` is an actual `IntRange` value (constructed via the `rangeTo()` function `..` calls), not special loop syntax; it can be stored, checked with `in`, or iterated. `1..<10` produces a range excluding the upper bound (equivalent to `until`), covering 1 through 9 rather than 1 through 10.

</details>

4. ▢ Why does `for (i in 1..10)` and `for (item in list)` use the exact same `for` syntax despite iterating over structurally different things (a range versus a list)?

<details markdown="1"><summary>Check</summary>

`for` iterates over anything exposing the right iteration protocol (an iterator), and both a range and a `List` satisfy that same protocol; Kotlin has no separate index-based versus enhanced-for distinction, since the loop construct itself is uniform across any iterable value.

</details>

5. ▢ Which claim correctly describes Kotlin's control flow constructs?

    - a) `if` is only a statement in Kotlin; producing a conditional value still requires a separate ternary operator
    - b) `if` and `when` are both usable as expressions that produce values, with `when`-as-expression requiring compiler-enforced exhaustiveness; a range like `1..10` is a real value, not special loop syntax
    - c) `when` requires an `else` branch in every case, even when matching an enum or sealed class
    - d) `for` loops have a different syntax for iterating a range versus iterating a collection

<details markdown="1"><summary>Check</summary>

**b)** That's the precise set of facts this lesson covers. (a) is false: Kotlin's `if` is itself an expression, with no separate ternary operator needed. (c) is false: sealed classes and enums (lessons 9-10) get compiler-checked exhaustiveness without an `else`, since the compiler knows every possible case already. (d) is false: `for` uses the same syntax uniformly over any iterable, ranges and collections included.

</details>

## Real-world reps

- [ ] Find a Kotlin file you've written or have access to. Look for a place using the classic `if`/`else if`/`else` chain that could be a `when` instead, and consider whether rewriting it would be clearer.
- [ ] Find a `when` used as an expression. Confirm it's actually exhaustive (has an `else`, or matches an enum/sealed type completely), and note what the compiler would say if you removed a branch.
- [ ] Tomorrow: read the primary source's section on ranges and progressions in full, and note the difference between a range's default step and a `step` value you supply explicitly.

## Going further

- [Docs: "Conditions and loops", Kotlin](https://kotlinlang.org/docs/control-flow.html)
- [Docs: "Ranges and progressions", Kotlin](https://kotlinlang.org/docs/ranges.html)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
