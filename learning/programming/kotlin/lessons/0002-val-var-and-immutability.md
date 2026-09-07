---
title: 2. val/var and Immutability
description: Why val is the default worth defending, what it actually guarantees (and doesn't), and the Java habit of reaching for var out of reflex
type: lesson
---

# Lesson 2. val/var and Immutability

**Mission link:** Null safety (lesson 1) moved one Java habit into the type system; `val`/`var` is the second, and arguably more pervasive one, since Java's mutable-by-default local variables and fields shape a defensive coding style that Kotlin's default asks you to unlearn from the first line of every function.
**Primary source:** [Docs: "Basic syntax overview", Kotlin](https://kotlinlang.org/docs/basic-syntax.html)
**Prerequisites:** [Lesson 1](0001-null-safety.md), [Platform type](../GLOSSARY.md)

## Warm-up

1. ▢ What is the fundamental difference between `String` and `String?` in Kotlin?

<details markdown="1"><summary>Check</summary>

`String` is guaranteed by the compiler to never hold `null` at any assignment or function call site; `String?` may hold `null`, and the compiler requires handling that possibility (a safe call, an Elvis default, a null check, or `!!`) before treating it as a plain `String`.

</details>

2. ▢ Why does routine use of `!!` recreate the exact problem null safety was designed to prevent?

<details markdown="1"><summary>Check</summary>

`!!` throws a `NullPointerException` immediately if the value is actually `null`, the same runtime crash Kotlin's null safety moves to compile time. Using it reflexively to silence the compiler, rather than backed by real evidence the value can't be null, means a case the type system already flagged goes unhandled instead of being properly checked.

</details>

## Know this

### `val` declares a read-only reference, assigned exactly once

`val name = "Ada"` declares a reference that can be assigned once and never reassigned; attempting `name = "Grace"` afterward is a compile error, not a runtime warning. `var name = "Ada"` declares a reference that can be reassigned freely, the direct equivalent of a Java local variable or field with no `final` keyword. The compiler enforces this distinction at every use site, the same way it enforces nullability (lesson 1): a `val` isn't a convention that a linter checks, it's a guarantee the type system won't let you violate.

### `val` is the default worth defending, the same shape of argument as lesson 1's

Kotlin's idiomatic default is `val` unless a variable genuinely needs to change, the mirror image of `String` over `String?` unless a value genuinely can be null. Reaching for `var` reflexively, the way years of Java's mutable-by-default locals and fields train a habit, produces code that compiles fine but signals the author hasn't asked whether this value actually needs to change, or has defaulted to assuming it might, the same "compiles but reads badly" pattern lesson 1 named for null checks.

### `val` guarantees the reference is fixed, not that the referenced object is immutable

This is the single most consequential distinction in this lesson: `val list = mutableListOf(1, 2, 3)` means `list` can never be reassigned to point at a different list, but the list it points to can still be mutated in place (`list.add(4)` compiles and works fine). `val` is about the *reference*, not the *object*. A `val` holding a mutable collection, a mutable data class property, or any object with its own mutating methods is not, by itself, an immutability guarantee about that object's contents, only about which object the variable refers to.

### Kotlin's collection types make the object-level distinction explicit, separately from `val`/`var`

Because `val` alone doesn't guarantee an immutable object, Kotlin's standard library separates read-only interfaces (`List`, `Set`, `Map`) from their mutable counterparts (`MutableList`, `MutableSet`, `MutableMap`), covered fully in lesson 5. The two distinctions, reference reassignment (`val`/`var`) and object mutability (`List` vs `MutableList`), are independent and compose: a `var` holding a read-only `List` can point at a different list entirely but never grow the current one; a `val` holding a `MutableList` can never point elsewhere but can still be mutated in place.

## Practice

1. ▢ `val count = 0` followed by `count = 1`. What happens, and why?

<details markdown="1"><summary>Check</summary>

A compile error: `val` declares a reference assigned exactly once, and reassigning it afterward violates that guarantee at compile time, not at runtime.

</details>

2. ▢ `val scores = mutableListOf(90, 85)`, followed by `scores.add(100)`. Does this compile, and does it violate `val`'s guarantee? Explain.

<details markdown="1"><summary>Hint</summary>

Distinguish what `val` actually promises about `scores` from what it promises about the list `scores` points to.

</details>

<details markdown="1"><summary>Check</summary>

This compiles and works fine, and it doesn't violate `val`'s guarantee, because `val` only guarantees `scores` itself is never reassigned to point at a different list; it says nothing about whether the list object it points to can be mutated in place. Adding an element to the same list object is a mutation of the object, not a reassignment of the reference.

</details>

3. ▢ A developer with a Java background reflexively declares every local variable with `var`, even ones never reassigned after their initial value. What Java-habit pattern does this mirror from lesson 1, and why is it worth naming explicitly even though it compiles fine?

<details markdown="1"><summary>Check</summary>

It mirrors the reflexive-defensive-check pattern from lesson 1 (writing `if (x != null)` on an already-non-nullable type): defaulting to the more permissive option out of habit rather than asking whether the stricter one (`val`, or a non-nullable type) actually fits. It compiles fine either way, which is exactly why it's worth naming: the code doesn't fail, it just signals unexamined habit rather than a deliberate choice.

</details>

4. ▢ Distinguish `var list: List<Int>` from `val list: MutableList<Int>` in terms of what each allows and forbids.

<details markdown="1"><summary>Check</summary>

`var list: List<Int>` can be reassigned to point at an entirely different (read-only) list, but the list it currently points to has no methods to add or remove elements, so its contents can't be mutated in place through this reference. `val list: MutableList<Int>` can never be reassigned to point elsewhere, but the mutable list it points to can have elements added or removed in place. The two distinctions, reference reassignment and object mutability, are independent.

</details>

5. ▢ Which claim correctly describes `val` and immutability in Kotlin?

   - a) `val` guarantees both that the reference can't be reassigned and that the object it points to is immutable
   - b) `val` guarantees only that the reference can't be reassigned; whether the object itself is mutable depends on the object's own type (a `MutableList` stays mutable even held by a `val`)
   - c) `var` and `val` both allow reassignment, differing only in stylistic convention
   - d) A `val` holding a `List` (not `MutableList`) can still have elements added to it directly

<details markdown="1"><summary>Check</summary>

**b)** That's the precise, load-bearing distinction this lesson covers: reference immutability from `val`, object mutability as a separate, independent property of the object's own type. (a) is false, exactly the common misconception this lesson corrects. (c) is false: `val` specifically forbids reassignment; that's its entire enforced guarantee. (d) is false: `List` (read-only) has no mutating methods at all; only a `MutableList` does.

</details>

## Real-world reps

- [ ] Find a Kotlin file you've written or have access to. Count how many `var` declarations are actually reassigned anywhere in their scope, versus how many could be `val` without changing behavior.
- [ ] Find a `val` holding a mutable collection or mutable object. Confirm you can explain, without looking it up, exactly what `val` does and doesn't guarantee about it.
- [ ] Tomorrow: rewrite one unnecessary `var` you find into a `val`, and note whether the compiler accepts the change immediately or reveals a place the variable actually was reassigned.

## Going further

- [Docs: "Basic syntax overview", Kotlin](https://kotlinlang.org/docs/basic-syntax.html)
- [Docs: "Kotlin for Java developers", Kotlin](https://kotlinlang.org/docs/comparison-to-java.html)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
