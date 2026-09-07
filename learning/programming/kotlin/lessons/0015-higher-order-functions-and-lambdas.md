---
title: 15. Higher-Order Functions and Lambdas
description: Function types as real types, trailing-lambda syntax, and the receiver mechanism scope functions are actually built on
type: lesson
---

# Lesson 15. Higher-Order Functions and Lambdas

**Mission link:** Lesson 14's scope functions were used without explaining the mechanism underneath them; this lesson is that mechanism, function types and lambdas as first-class values, which is also what makes `run`/`apply`'s `this`-style access (versus `let`/`also`'s `it`) actually work.
**Primary source:** [Docs: "Higher-order functions and lambdas", Kotlin](https://kotlinlang.org/docs/lambdas.html)
**Prerequisites:** [Lesson 14](0014-scope-functions.md), [Platform type](../GLOSSARY.md)

## Warm-up

1. ▢ What are the two independent axes distinguishing `let`, `run`, `with`, `apply`, and `also`?

<details markdown="1"><summary>Check</summary>

Object reference (exposed as `it` for `let`/`also`, or as `this` for `run`/`with`/`apply`) and return value (the lambda's result for `let`/`run`/`with`, or the original object for `apply`/`also`).

</details>

2. ▢ Why can't `with` be used in a null-safe chain the way `let` can?

<details markdown="1"><summary>Check</summary>

`with` takes the context object as an ordinary function argument rather than being called as an extension function on it, so there's no receiver in member-call position to attach a safe-call `?.` to.

</details>

## Know this

### Functions are first-class values in Kotlin

A function in Kotlin can be stored in a variable, passed as an argument, or returned from another function, exactly like any other value (an `Int`, a `String`, an object). A **higher-order function** is simply a function that takes another function as a parameter, or returns one; `fold` is the canonical example, taking a `combine` function parameter and calling it once per element. This isn't a special case bolted onto the language; it follows directly from functions being real values with real types, the same as everything else lesson 4 covered for Kotlin's basic types.

### A function type describes a function's shape, the same way any type describes a value's shape

`(Int, Int) -> Int` is a real type: a function taking two `Int` parameters and returning an `Int`. `() -> Unit` takes nothing and returns nothing meaningful. A variable, parameter, or property can be declared with a function type exactly like any other type (`val onClick: () -> Unit = { println("clicked") }`), and a lambda expression (`{ acc, i -> acc + i }`) is how you write a literal value of that type, the functional equivalent of writing `42` for an `Int` or `"hello"` for a `String`.

### Trailing-lambda syntax is why chained, LINQ-style code reads the way it does

If a function's last parameter is itself a function type, a lambda passed for that parameter can be written outside the parentheses: `items.fold(1) { acc, e -> acc * e }` instead of `items.fold(1, { acc, e -> acc * e })`. If the lambda is the *only* argument, the parentheses can be omitted entirely (`run { ... }`, exactly how lesson 14's scope functions are typically called). This convention, combined with a lambda's last expression being its implicit return value, is what makes chains like `strings.filter { it.length == 5 }.sortedBy { it }.map { it.uppercase() }` read as a fluent pipeline rather than a series of nested, parenthesis-heavy calls.

### Function types with a receiver are what makes `run`/`apply`'s `this` work

A function type can optionally specify a receiver type before the arrow: `A.(B) -> C` is a function callable *on* a receiver of type `A`, taking a `B` parameter, returning `C`. Inside a function literal of this type, the receiver becomes an implicit `this`, accessible without qualification, exactly the same mechanism extension functions (lesson 13) use to expose the receiver inside their body. This is the actual, concrete answer to how `run` and `apply` expose the context object as `this` while `let` and `also` expose it as `it`: the former are declared with a receiver-style function type (`T.() -> R`), the latter with an ordinary parameter-style function type (`(T) -> R`); the difference in lesson 14's table isn't arbitrary convention, it's two genuinely different function type shapes.

## Practice

1. ▢ What makes `fold` a higher-order function, specifically?

<details markdown="1"><summary>Check</summary>

It takes a function (the `combine` parameter) as one of its own parameters, which is exactly the definition of a higher-order function: a function that takes a function as a parameter, or returns one.

</details>

2. ▢ What does the function type `(String) -> Boolean` describe, and give an example of a lambda that could be a value of that type.

<details markdown="1"><summary>Check</summary>

It describes a function taking one `String` parameter and returning a `Boolean`. `{ s -> s.isNotEmpty() }` is one example: a lambda taking a string and returning whether it's non-empty, matching the shape `(String) -> Boolean` exactly.

</details>

3. ▢ Rewrite `items.fold(1, { acc, e -> acc * e })` using trailing-lambda syntax, and explain the rule that permits it.

<details markdown="1"><summary>Hint</summary>

Consider which parameter of `fold` the lambda is filling, and its position among `fold`'s parameters.

</details>

<details markdown="1"><summary>Check</summary>

`items.fold(1) { acc, e -> acc * e }`. The rule: if a function's last parameter is itself a function type, a lambda passed for that parameter can be written outside the parentheses; here, `combine` (the lambda parameter) is `fold`'s last parameter, so it qualifies.

</details>

4. ▢ Why do `run` and `apply` expose the context object as `this`, while `let` and `also` expose it as `it`, in terms of the actual function type each is declared with?

<details markdown="1"><summary>Check</summary>

`run` and `apply` are declared using a receiver-style function type (`T.() -> R`), where the receiver becomes an implicit `this` inside the lambda body, the same mechanism extension functions use. `let` and `also` are declared using an ordinary parameter-style function type (`(T) -> R`), where the object is just a regular lambda parameter, conventionally named `it`. The `this` versus `it` distinction isn't a stylistic choice; it directly reflects which of these two function type shapes each scope function actually uses.

</details>

5. ▢ Which claim correctly describes higher-order functions and lambdas?

    - a) A higher-order function is any function with more than one parameter
    - b) Function types are real types describing a function's parameter and return shape; a receiver-style function type (`T.() -> R`) exposes the receiver as `this`, while an ordinary function type (`(T) -> R`) passes it as an explicit parameter, which is exactly what distinguishes scope functions like `run` from `let`
    - c) Trailing-lambda syntax only works when a lambda is the sole argument to a function
    - d) A lambda's return value must always be specified with an explicit `return` statement

<details markdown="1"><summary>Check</summary>

**b)** That's the precise mechanism this lesson traces from lambdas down to lesson 14's scope-function distinctions. (a) is false: a higher-order function is defined by taking or returning a function, not by its parameter count. (c) is false: trailing-lambda syntax applies whenever the lambda fills the *last* parameter, whether or not other arguments precede it; omitting parentheses entirely only requires the lambda to be the sole argument. (d) is false: a lambda's last expression is implicitly its return value unless a qualified return is used instead.

</details>

## Real-world reps

- [ ] Find a higher-order function call in a codebase you've written or have access to (a `map`, `filter`, `fold`, or a custom one). Write out its function type explicitly (parameter types and return type) without looking at the signature, then check yourself against it.
- [ ] Find a use of `run` or `apply` and a use of `let` or `also`. Confirm you can explain, using this lesson's receiver-versus-parameter distinction, why each exposes the context object the way it does.
- [ ] Tomorrow: read the primary source's section on function literals with receiver in full, and sketch a small example of your own using the `A.(B) -> C` type notation.

## Going further

- [Docs: "Higher-order functions and lambdas", Kotlin](https://kotlinlang.org/docs/lambdas.html)
- [Docs: "Scope functions", Kotlin](https://kotlinlang.org/docs/scope-functions.html)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
