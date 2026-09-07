---
title: 14. Scope Functions
description: Choosing among let, run, with, apply, and also by what each one returns and how it exposes the object, not by habit
type: lesson
---

# Lesson 14. Scope Functions

**Mission link:** Lesson 13 covered extension functions and their static-dispatch rule; three of the five scope functions this lesson covers (`let`, `run`, `apply`) are themselves extension functions, applying that same mechanism to a genuinely common idiom, running code in the context of an object.
**Primary source:** [Docs: "Scope functions", Kotlin](https://kotlinlang.org/docs/scope-functions.html)
**Prerequisites:** [Lesson 13](0013-extension-functions.md), [Platform type](../GLOSSARY.md)

## Warm-up

1. ▢ What does an extension function actually change about the class it extends?

<details markdown="1"><summary>Check</summary>

Nothing: the class's own definition is entirely unchanged. The extension only makes a new function callable using member-access syntax, resolved by the compiler at the call site, not attached to the class itself.

</details>

2. ▢ Why does `shape.getName()` resolve to `Shape.getName()` rather than `Rectangle.getName()`, when `shape` is declared as type `Shape` but actually holds a `Rectangle` instance?

<details markdown="1"><summary>Check</summary>

Extension functions are dispatched statically: the compiler picks which extension to call based on the variable's declared type at compile time, not the object's actual runtime type, the opposite of how an overridden member function dispatches.

</details>

## Know this

### All five scope functions do the same basic thing, differently

`let`, `run`, `with`, `apply`, and `also` all execute a lambda in the context of some object, letting you access that object without repeating its variable name inside the block. None of them add a new technical capability; the entire point is conciseness and readability over repeatedly naming a variable. What actually distinguishes them is two independent choices: how the object is exposed inside the lambda (as `it`, an ordinary parameter, or as `this`, the implicit receiver), and what the whole expression evaluates to (the lambda's own result, or the original object back again).

### Two axes, not five arbitrary names to memorize

Object reference: `let` and `also` expose the object as `it`; `run`, `with`, and `apply` expose it as `this` (accessible implicitly, member-style, with no name needed at all). Return value: `let`, `run`, and `with` return the lambda's result, whatever the last expression in the block evaluates to; `apply` and `also` return the original object itself, unchanged, regardless of what the lambda computes. Once these two axes are fixed in mind, the choice among the five becomes matching the actual need (transform and return something new, or configure and keep the object) to the right cell, rather than memorizing five names as unrelated facts.

### `let` and `also` fit side-effects and null-safe chaining; `run` and `apply` fit configuration

`let` is the natural fit for transforming a value into something else while keeping it nullable-safe (`user?.let { sendEmail(it) }`, running only if `user` isn't null) or for scoping a value to a narrow block without polluting the surrounding scope with a new named variable. `also` fits a side effect that doesn't transform anything (logging, a sanity-check assertion) while still wanting the original object back to keep chaining. `apply` fits configuring an object's own properties and getting that same object back (`Person().apply { name = "Ada"; age = 30 }`, useful for object initialization or builder-style code). `run` fits computing a result from an object's own members without needing the object itself afterward, or running a block of initialization logic and using its result directly.

### `with` is the odd one out: not an extension function at all

Unlike the other four, `with` takes the context object as an ordinary argument (`with(person) { ... }`) rather than being called as an extension on it (`person.let { ... }`); this is a real, non-cosmetic difference, since `with` genuinely cannot be used in a null-safe chain (`person?.with { ... }` isn't valid syntax) the way `let` or `also` can. `with` fits calling multiple methods on an object when you don't need the result to be that object itself, and you already have a non-null reference in hand, more of a grouping convenience than an extension-based transformation.

## Practice

1. ▢ Which scope functions expose the context object as `it`, and which expose it as `this`?

<details markdown="1"><summary>Check</summary>

`let` and `also` expose the object as `it` (an ordinary lambda parameter). `run`, `with`, and `apply` expose it as `this` (the implicit receiver, accessible without naming it).

</details>

2. ▢ Which scope functions return the lambda's result, and which return the original object?

<details markdown="1"><summary>Hint</summary>

Consider which functions fit "compute something new from this" versus "configure this and keep using it."

</details>

<details markdown="1"><summary>Check</summary>

`let`, `run`, and `with` return the lambda's own result (whatever its last expression evaluates to). `apply` and `also` return the original object itself, regardless of what the lambda computes, since they're meant for configuring or side-effecting on an object you want to keep using afterward.

</details>

3. ▢ Why is `apply` a natural fit for object configuration (`Person().apply { name = "Ada"; age = 30 }`), but a poor fit for computing a transformed value?

<details markdown="1"><summary>Check</summary>

`apply` always returns the original object, not the lambda's result, so it's suited exactly to "configure this object's own properties, then keep using the same object," which is what initialization-style configuration needs. It's a poor fit for computing something new, since whatever the lambda's last expression evaluates to is discarded; only the original, now-configured object comes back out.

</details>

4. ▢ Why can't `with` be used in a null-safe chain the way `user?.let { ... }` can?

<details markdown="1"><summary>Check</summary>

`with` takes the context object as an ordinary function argument (`with(person) { ... }`) rather than being called as an extension function on the object itself; there's no receiver to attach a safe-call `?.` to, since `with` isn't invoked in member-call position at all, unlike `let`, `also`, `run`, and `apply`, which are extension functions and can be chained with `?.`.

</details>

5. ▢ Which claim correctly describes choosing among the scope functions?

   - a) All five scope functions are functionally identical; the choice is purely a stylistic preference with no technical difference
   - b) The choice comes down to two independent axes, object reference (`it` vs `this`) and return value (lambda result vs original object), and matching those to the actual need (transform vs configure) rather than memorizing five arbitrary names
   - c) `with` is an extension function like `let`, `run`, and `apply`, just with a different name
   - d) `also` and `apply` both return the lambda's computed result

<details markdown="1"><summary>Check</summary>

**b)** That's the precise two-axis framework this lesson is built around. (a) is false: the differences (object reference, return value) are real, functional distinctions with concrete consequences for what code can and can't do (null-safe chaining, what the expression evaluates to). (c) is false: `with` takes the context object as an argument rather than being an extension function, which is exactly why it can't be used in a null-safe chain. (d) is false: `apply` and `also` both return the *original object*, not the lambda's computed result.

</details>

## Real-world reps

- [ ] Find a use of `let`, `run`, `with`, `apply`, or `also` in a codebase you've written or have access to. Confirm you can explain, without checking, which axis (object reference, return value) makes it the right choice over the other four.
- [ ] Find a place using a scope function purely out of habit, where a plain variable and a couple of statements would read just as clearly, or more clearly. Consider whether the scope function is adding real value there.
- [ ] Tomorrow: read the primary source's function-selection table in full, and rewrite one small piece of your own code using a different scope function than you'd normally reach for, to feel the actual difference in what changes.

## Going further

- [Docs: "Scope functions", Kotlin](https://kotlinlang.org/docs/scope-functions.html)
- [Docs: "Extensions", Kotlin](https://kotlinlang.org/docs/extensions.html)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
