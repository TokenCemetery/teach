---
title: 5. Collections Basics
description: List, Set, and Map as read-only-by-interface collections, and why a mutable collection held by a val is still mutable
type: lesson
---

# Lesson 5. Collections Basics

**Mission link:** Lesson 2 established that `val` guarantees reference immutability, not object immutability, using a mutable list as the example without covering collections properly; this lesson is that coverage, and where Kotlin makes the object-mutability question explicit at the interface level instead of leaving it implicit.
**Primary source:** [Docs: "Collections overview", Kotlin](https://kotlinlang.org/docs/collections-overview.html)
**Prerequisites:** [Lesson 2](0002-val-var-and-immutability.md), [Platform type](../GLOSSARY.md)

## Warm-up

1. ▢ `val list = mutableListOf(1, 2, 3)` followed by `list.add(4)`. Does this violate `val`'s guarantee?

<details markdown="1"><summary>Check</summary>

No. `val` only guarantees `list` is never reassigned to point at a different list object; it says nothing about whether the object it points to can be mutated in place. Adding an element mutates the existing object rather than reassigning the reference.

</details>

2. ▢ Why can Kotlin's basic types like `Int` be used as generic type arguments (`List<Int>`) the same way `String` can?

<details markdown="1"><summary>Check</summary>

Because `Int` and the other basic types are real classes at the language level, not primitives, so they work as generic type arguments uniformly with `String` and any other type, with the JVM's boxing to `java.lang.Integer` hidden as a runtime detail.

</details>

## Know this

### Three collection shapes: List, Set, Map

**List** is an ordered collection accessed by integer index, and elements can repeat (a phone number's digits: ordered, repeats allowed). **Set** is a collection of unique elements with no significant order (lottery numbers: no duplicates, order doesn't matter). **Map** is a set of key-value pairs, with unique keys each mapping to exactly one value, though values themselves can repeat (an employee ID mapping to a position). Each shape fits a different question about the data: does order matter, can items repeat, do I need to look something up by a key.

### Every collection type has a read-only interface and a mutable interface

Kotlin represents each of the three shapes as a pair of interfaces: a **read-only interface** (`List`, `Set`, `Map`) providing only element-access operations, and a **mutable interface** (`MutableList`, `MutableSet`, `MutableMap`) that extends the read-only one with write operations (adding, removing, updating elements). `listOf(...)` produces a read-only `List`; `mutableListOf(...)` produces a `MutableList`. This split is what makes "can this collection be mutated" a property of its declared type, checkable at the interface level, rather than something you have to infer from how a variable happens to be used elsewhere in the code.

### A mutable collection held by `val` is still mutable, by design

The Kotlin documentation is explicit about this, since it's a common point of confusion: a mutable collection doesn't need a `var` to remain mutable, and assigning one to `val` doesn't make its contents read-only. `val` protects the *reference* (this variable will always point to the same collection object); the mutable interface controls whether the *object itself* can be modified. The actual benefit of `val nums: MutableList<Int> = mutableListOf(1, 2, 3)` is narrower than it might look: it guarantees nobody reassigns `nums` to point at an entirely different list, while still allowing `nums.add(4)` throughout the code, exactly the composition lesson 2 introduced.

### Read-only is not the same guarantee as immutable

A `List` (read-only interface) has no methods to add, remove, or update elements through that reference, but this doesn't mean the underlying collection can never change: if the same underlying collection is also reachable through a `MutableList` reference elsewhere (the same object, exposed through two different interface views), changes made through the mutable reference are visible through the read-only one too, since they're the same object. "Read-only" describes what a given reference's interface permits you to do, not an unbreakable guarantee that the data behind it never changes from anywhere in the program.

## Practice

1. ▢ Which collection shape fits "a group of unique tags applied to a post, where order doesn't matter," and which fits "the ordered sequence of steps in a recipe, where a step could repeat"?

<details markdown="1"><summary>Check</summary>

Unique tags with no meaningful order: `Set`. An ordered sequence where repeats are allowed and order matters: `List`.

</details>

2. ▢ Why does declaring `val nums: MutableList<Int> = mutableListOf(1, 2, 3)` still allow `nums.add(4)` to compile and work?

<details markdown="1"><summary>Hint</summary>

Distinguish what `val` protects from what the mutable interface controls.

</details>

<details markdown="1"><summary>Check</summary>

`val` only guarantees `nums` is never reassigned to a different list object; whether the object's contents can be mutated is controlled entirely by its declared type being `MutableList`, which has an `add` method. The two are independent: `val` restricts reference reassignment, `MutableList` permits object mutation, and both apply simultaneously here.

</details>

3. ▢ A function takes a parameter of type `List<Int>` (read-only) and passes it around, relying on its contents never changing during the function's execution. Under what circumstance could this assumption still be wrong?

<details markdown="1"><summary>Check</summary>

If the same underlying collection object is also reachable through a `MutableList` reference elsewhere in the program (perhaps held by the caller, or another part of the code with access to the same object), a mutation made through that other reference is visible through the read-only `List` reference too, since they refer to the same object. The `List` interface only restricts what this particular reference can do; it doesn't guarantee the object itself is immutable everywhere.

</details>

4. ▢ Contrast what `val` guarantees with what the `List`/`MutableList` distinction guarantees.

<details markdown="1"><summary>Check</summary>

`val` guarantees a reference is never reassigned to point at a different object; it says nothing about the object's own mutability. `List` versus `MutableList` guarantees whether a given reference's interface exposes methods to mutate the underlying object; it says nothing about reference reassignment. The two guarantees are independent and compose in all four combinations (`val`/`var` crossed with `List`/`MutableList`).

</details>

5. ▢ Which claim correctly describes Kotlin's collection mutability model?

    - a) Assigning a mutable collection to a `val` makes its contents read-only, the same as declaring it a `List`
    - b) `val` restricts reference reassignment; `List` versus `MutableList` restricts object mutation through a given reference; the two guarantees are independent and can be combined in any pairing
    - c) A `List` reference guarantees the underlying data can never change from any part of the program
    - d) `Set` and `Map` don't have a mutable counterpart, only `List` does

<details markdown="1"><summary>Check</summary>

**b)** That's the precise, composable pair of guarantees this lesson covers. (a) is false, and is exactly the common misconception the primary source calls out explicitly: `val` doesn't affect object mutability at all. (c) is false: a `List` reference only restricts what that specific reference can do, not whether the same underlying object is mutable via a different, `MutableList` reference to it. (d) is false: all three collection shapes have both a read-only and mutable interface pair (`Set`/`MutableSet`, `Map`/`MutableMap`).

</details>

## Real-world reps

- [ ] Find a Kotlin function you've written or have access to that takes a `List`, `Set`, or `Map` parameter. Confirm whether the read-only interface is actually sufficient for what the function does, or whether it secretly needs mutation and should take the mutable interface instead.
- [ ] Find a `val` holding a `MutableList`, `MutableSet`, or `MutableMap`. Confirm you can explain precisely what is and isn't guaranteed about it, without looking it up.
- [ ] Tomorrow: read the primary source's section distinguishing collection types in full, and note one operation available on the mutable interface that isn't available on the read-only one for each of `List`, `Set`, and `Map`.

## Going further

- [Docs: "Collections overview", Kotlin](https://kotlinlang.org/docs/collections-overview.html)
- [Docs: "Basic syntax overview", Kotlin](https://kotlinlang.org/docs/basic-syntax.html)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
