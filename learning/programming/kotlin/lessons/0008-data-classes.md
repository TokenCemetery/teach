---
title: 8. Data Classes
description: What data class actually generates, and the subtle rule that only primary-constructor properties participate in any of it
type: lesson
---

# Lesson 8. Data Classes

**Mission link:** Lesson 7 named the data class as the thing Kotlin's own docs say to reach for before a plain class, when the goal is holding data. This lesson is that construct made concrete, and closes the loop back to lesson 3's equality distinction: a data class is exactly how a class gets structural `equals()` for free.
**Primary source:** [Docs: "Data classes", Kotlin](https://kotlinlang.org/docs/data-classes.html)
**Prerequisites:** [Lesson 7](0007-classes-and-properties.md), [Platform type](../GLOSSARY.md)

## Warm-up

1. ▢ Why does the Kotlin documentation recommend considering a data class or an extension function before writing a plain class from scratch?

<details markdown="1"><summary>Check</summary>

A data class already generates the boilerplate (equality, string representation, and more) a hand-written class holding data would need to add manually; an extension function adds behavior to an existing type without a new class at all. A plain class is the right tool specifically when neither fits, real behavior beyond storing values.

</details>

2. ▢ A plain class (not `data`) is compared with `==` between two instances holding identical property values. What does `==` return, and why?

<details markdown="1"><summary>Check</summary>

`false`, because a plain class inherits `Any`'s default `equals()`, which implements referential equality unless overridden; without an explicit override or the `data` modifier, two separate instances are never `==`-equal regardless of their property values.

</details>

## Know this

### `data class` generates four things automatically

Marking a class `data class User(val name: String, val age: Int)` makes the compiler derive, from the primary constructor's properties: an `equals()`/`hashCode()` pair implementing structural equality (lesson 3, resolved automatically); a `toString()` in the form `"User(name=John, age=42)"`, readable without writing one by hand; `componentN()` functions (`component1()`, `component2()`, ...) enabling destructuring (`val (name, age) = user`); and a `copy()` function, producing a new instance with some properties changed and the rest kept identical (`user.copy(age = 43)`). This is the concrete answer to lesson 7's "what does a data class buy you": four generated members, derived automatically, that a hand-written class would otherwise need written by hand and kept in sync manually.

### Only primary-constructor properties participate, a rule worth knowing precisely

The compiler only uses properties declared *inside the primary constructor* for all four generated members; a property declared in the class body (`data class Person(val name: String) { var age: Int = 0 }`) is invisible to `equals()`, `hashCode()`, `toString()`, `componentN()`, and `copy()`. This has a real, non-obvious consequence: two `Person` instances with the same `name` but different `age` values are considered `==`-equal, since `age` was never a primary-constructor property and never participates in equality at all. This is exactly the kind of precise rule worth internalizing rather than assuming "all the class's properties" are covered.

### Data classes have real requirements, not just the `data` keyword

The primary constructor must have at least one parameter, and every primary constructor parameter must be `val` or `var` (a plain, unmarked parameter, per lesson 7, isn't a property and couldn't participate in generation anyway). Data classes can't be `abstract`, `open`, `sealed`, or `inner`. Providing your own `componentN()` or `copy()` implementations isn't allowed; if you need genuinely custom `equals()`, `hashCode()`, or `toString()` behavior, you write those explicitly in the class body and the compiler skips generating them in favor of your version, but `componentN()` and `copy()` have no such override path.

### `copy()` makes an immutable data class practical, not just safe

Combining `data class` with `val` properties throughout (lesson 2's default) produces a genuinely immutable value: no property can be reassigned, and no generated method mutates the instance. `copy()` is what makes this practical rather than merely safe: `val updated = user.copy(age = user.age + 1)` produces a new instance with one property changed, without needing to manually re-specify every other property or reach for `var` just to allow in-place updates. This is the idiomatic Kotlin alternative to a mutable class with setters: immutable data plus a cheap way to produce a modified copy, rather than mutating shared state in place.

## Practice

1. ▢ List the four members `data class User(val name: String, val age: Int)` generates automatically, and what each one does.

<details markdown="1"><summary>Check</summary>

`equals()`/`hashCode()`: structural equality based on the properties. `toString()`: a readable `"User(name=..., age=...)"` representation. `componentN()` functions: enable destructuring (`val (name, age) = user`). `copy()`: produces a new instance with some properties changed and the rest identical.

</details>

2. ▢ `data class Person(val name: String) { var age: Int = 0 }`. Two instances have the same `name` but different `age`. Are they `==`-equal? Why?

<details markdown="1"><summary>Hint</summary>

Consider exactly which properties the compiler uses to generate `equals()`.

</details>

<details markdown="1"><summary>Check</summary>

Yes, they're `==`-equal, because only primary-constructor properties (`name`, here) participate in the generated `equals()`; `age`, declared in the class body, is invisible to it. Two instances differing only in `age` are considered structurally equal regardless.

</details>

3. ▢ Why can't a data class provide its own `componentN()` or `copy()` implementations, when it can provide its own `equals()`, `hashCode()`, or `toString()`?

<details markdown="1"><summary>Check</summary>

The documentation is explicit that providing explicit implementations of `componentN()` and `copy()` is disallowed entirely, unlike `equals()`/`hashCode()`/`toString()`, which fall back to an explicit implementation if you provide one. This keeps `componentN()` and `copy()` mechanically tied to the primary constructor's actual properties, guaranteeing they always reflect the real, current shape of the data rather than a hand-maintained version that could drift out of sync.

</details>

4. ▢ Why does combining `data class` with `val` properties throughout, plus `copy()`, serve as an alternative to a mutable class with setters?

<details markdown="1"><summary>Check</summary>

All-`val` properties make instances genuinely immutable, no property can be reassigned and no generated method mutates in place, while `copy()` still makes producing a "changed" version practical: `user.copy(age = user.age + 1)` creates a new instance with one property updated without manually re-specifying every other property or needing `var` to allow in-place mutation. This gets the ergonomics of mutation (an easy way to get an "updated" value) without any actual shared mutable state.

</details>

5. ▢ Which claim correctly describes what a data class generates and requires?

    - a) A data class generates `equals()`, `hashCode()`, `toString()`, `componentN()`, and `copy()` based on every property declared anywhere in the class, including the class body
    - b) A data class generates its four members based only on primary-constructor properties, requires at least one such property (all marked `val`/`var`), and disallows custom `componentN()`/`copy()` implementations while still allowing custom `equals()`/`hashCode()`/`toString()`
    - c) A data class can be `abstract` or `sealed` as long as it still has a primary constructor with at least one property
    - d) `copy()` mutates the original instance's properties in place and returns a reference to it

<details markdown="1"><summary>Check</summary>

**b)** That's the precise, complete rule set this lesson covers. (a) is false, exactly the subtle trap this lesson names: only primary-constructor properties participate, not properties declared in the class body. (c) is false: the documentation explicitly disallows `abstract`, `open`, `sealed`, or `inner` data classes. (d) is false: `copy()` produces an entirely new instance, leaving the original unchanged, which is what makes it compatible with all-`val`, genuinely immutable data classes.

</details>

## Real-world reps

- [ ] Find a data class you've written or have access to. Check whether any property is declared in the class body rather than the primary constructor, and if so, confirm you can explain precisely how that affects its equality and `copy()` behavior.
- [ ] Find a place using `copy()` to produce a modified instance. Confirm the original instance is genuinely left unchanged, and consider whether the pattern is being used in place of a mutable class with setters.
- [ ] Tomorrow: read the primary source's section on destructuring declarations in full, and write one small example using `componentN()` (via `val (a, b) = someDataClassInstance`) for a data class you define.

## Going further

- [Docs: "Data classes", Kotlin](https://kotlinlang.org/docs/data-classes.html)
- [Docs: "Equality", Kotlin](https://kotlinlang.org/docs/equality.html)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
