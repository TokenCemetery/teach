---
title: 3. Values vs References
description: Why == means something different in Kotlin than in Java, and the specific bug the Java habit of writing == produces
type: lesson
---

# Lesson 3. Values vs References

**Mission link:** Lesson 2 established that `val` guarantees reference immutability, not object immutability, which only matters once "same object" and "same content" are two genuinely different questions, exactly what this lesson makes precise, and exactly where Java's `==` and Kotlin's `==` mean different things.
**Primary source:** [Docs: "Equality", Kotlin](https://kotlinlang.org/docs/equality.html)
**Prerequisites:** [Lesson 2](0002-val-var-and-immutability.md), [Platform type](../GLOSSARY.md)

## Warm-up

1. ▢ Does `val list = mutableListOf(1, 2, 3)` followed by `list.add(4)` violate `val`'s guarantee? Why or why not?

<details markdown="1"><summary>Check</summary>

No. `val` only guarantees `list` is never reassigned to point at a different list object; it says nothing about whether the object it currently points to can be mutated in place. Adding an element mutates the existing object rather than reassigning the reference.

</details>

2. ▢ What Java-habit pattern does reflexively declaring every local variable `var` mirror from lesson 1?

<details markdown="1"><summary>Check</summary>

It mirrors reflexively writing a redundant null check on an already-non-nullable type: defaulting to the more permissive option (`var`, or a defensive `if (x != null)`) out of habit, without asking whether the stricter option (`val`, trusting the type) actually fits.

</details>

## Know this

### `==` in Kotlin checks structural equality, not reference identity

In Java, `==` on reference types checks whether two variables point to the exact same object in memory; comparing two different `String` objects with equal content via `==` can return `false`, which is why every Java developer learns to use `.equals()` for content comparison instead. Kotlin inverts this by convention: `==` (**structural equality**) calls `a.equals(b)` under the hood, comparing content, and `===` (**referential equality**) is the operator that checks whether two references point to the same object. `a == b` in Kotlin is shorthand for `a?.equals(b) ?: (b === null)`, not a memory-address comparison.

### The Java habit this produces: reaching for `===` where `==` was meant

A developer carrying Java's `==`-means-identity assumption into Kotlin sometimes reaches for `===` reflexively, expecting to need it for a "real" equality check the way Java's `.equals()` was needed. This is backwards: Kotlin's `==` already does the content comparison Java required `.equals()` for, and `===` is the specialized operator, reserved for the genuinely rarer case of checking whether two references are the literal same object (useful for singleton checks, cache identity, or specific object-identity invariants), not the default comparison operator.

### `equals()` is inherited from `Any`, and defaults to referential equality unless overridden

Every Kotlin class inherits `equals()` from the `Any` superclass, and the *default* implementation `Any` provides is referential equality: an ordinary class with no custom `equals()` behaves identically under `==` and `===` until something overrides `equals()`. **Data classes** (lesson 8) and **value classes** are the two Kotlin constructs that automatically generate a structural `equals()` based on their properties; a plain class declared without `data` gets none of this for free; two instances with identical property values are still `==`-unequal unless `equals()` is overridden by hand.

### Overriding `equals()` correctly means overriding `hashCode()` too

Kotlin's documentation is explicit that overriding `equals()` without also overriding `hashCode()` breaks the contract between the two: any collection relying on hashing (a `HashSet`, a `HashMap` key) uses `hashCode()` to bucket objects before ever calling `equals()`, so two objects that are `==`-equal but have different `hashCode()` values can silently fail to be found in a hash-based collection, appearing "missing" even though an equal object was inserted. This is a real, production-relevant bug, not a theoretical inconsistency, and it's exactly the kind of subtle Java-adjacent trap this lesson exists to name.

## Practice

1. ▢ In Kotlin, `val a = "hello"` and `val b = "hello"` (two separately constructed strings with the same content). What does `a == b` evaluate to, and what does `a === b` evaluate to?

<details markdown="1"><summary>Check</summary>

`a == b` is `true`: `==` is structural equality, calling `equals()`, and `String`'s `equals()` compares content. `a === b` may be `true` or `false` depending on whether the Kotlin/JVM string pool happens to intern both literals to the same object; the point of the exercise is that `==` doesn't depend on this at all, only `===` does.

</details>

2. ▢ Why is reaching for `===` out of a Java habit, expecting it to be needed for "real" equality, backwards?

<details markdown="1"><summary>Hint</summary>

Consider which operator already does the job Java's `.equals()` was needed for.

</details>

<details markdown="1"><summary>Check</summary>

Kotlin's `==` already performs the content comparison Java required an explicit `.equals()` call for; `===` is the specialized, rarer operator for checking literal object identity. Reaching for `===` as if it were the "real" equality check gets the two operators' roles backwards relative to what a Java developer is used to.

</details>

3. ▢ A plain class (not a `data class`) with properties `x` and `y` is compared with `==` between two instances holding identical `x` and `y` values. What does `==` return, and why?

<details markdown="1"><summary>Check</summary>

It returns `false` (referential equality's answer), because a plain class inherits `Any`'s default `equals()`, which implements referential equality unless overridden; without an explicit `equals()` override or the `data` modifier (lesson 8), two separate instances are never `==`-equal regardless of their property values.

</details>

4. ▢ A class overrides `equals()` to compare its properties structurally but doesn't override `hashCode()`. Describe a concrete way this can go wrong in production.

<details markdown="1"><summary>Check</summary>

Storing an instance in a `HashSet` or as a `HashMap` key, then later checking whether an `==`-equal instance (different object, same property values) is present, can return "not found" even though it's logically equal, because hash-based collections bucket by `hashCode()` before checking `equals()`. If two `==`-equal objects have different `hashCode()` values, the lookup can look in the wrong bucket entirely and never call `equals()` at all.

</details>

5. ▢ Which claim correctly describes equality in Kotlin?

   - a) `==` and `===` are interchangeable in Kotlin, both checking object identity
   - b) `==` checks structural equality (calls `equals()`), `===` checks referential equality (same object), and a plain class gets referential equality by default unless it overrides `equals()` or uses `data`/`value`
   - c) Overriding `equals()` alone is sufficient; `hashCode()` is unrelated and can be left as the default
   - d) `data class` and `value class` are the only way to get structural equality in Kotlin; a plain class can never override `equals()`

<details markdown="1"><summary>Check</summary>

**b)** That's the precise pair of operators and the default behavior this lesson covers. (a) is false: `==` and `===` are Kotlin's distinct structural/referential pair, the opposite of treating them as the same thing. (c) is false: leaving `hashCode()` as the inherited default while overriding `equals()` breaks hash-based collection lookups, a real production bug. (d) is false: a plain class can override `equals()` (and should also override `hashCode()`) by hand; `data`/`value` classes just do it automatically.

</details>

## Real-world reps

- [ ] Find a Kotlin class in a codebase you have access to (or write one) that overrides `equals()`. Check whether it also overrides `hashCode()`, and if not, construct a `HashSet` test that demonstrates the lookup failure this lesson describes.
- [ ] Find a place in Kotlin code where `===` is used. Confirm it's genuinely checking object identity (a singleton, a cache hit) rather than being used where `==` was actually intended.
- [ ] Tomorrow: read the primary source's full explanation of `equals()`'s default behavior in `Any`, and note what specifically `data class` and `value class` generate for you automatically.

## Going further

- [Docs: "Equality", Kotlin](https://kotlinlang.org/docs/equality.html)
- [Docs: "Kotlin for Java developers", Kotlin](https://kotlinlang.org/docs/comparison-to-java.html)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
