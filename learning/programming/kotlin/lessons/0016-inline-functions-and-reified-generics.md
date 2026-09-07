---
title: 16. Inline Functions and Reified Generics
description: Why inline exists to remove a real cost, why it enables non-local returns, and why reified type parameters only work because of inlining
type: lesson
---

# Lesson 16. Inline Functions and Reified Generics

**Mission link:** Lesson 15 covered lambdas as real values with real function types; this lesson is the cost that reality carries (an allocated object per lambda) and Kotlin's specific tool for removing it, which turns out to be the same mechanism that makes reified generics possible at all.
**Primary source:** [Docs: "Inline functions", Kotlin](https://kotlinlang.org/docs/inline-functions.html)
**Prerequisites:** [Lesson 15](0015-higher-order-functions-and-lambdas.md), [Platform type](../GLOSSARY.md)

## Warm-up

1. ▢ What does the function type `(String) -> Boolean` describe?

<details markdown="1"><summary>Check</summary>

A function taking one `String` parameter and returning a `Boolean`; a lambda like `{ s -> s.isNotEmpty() }` is one example of a value matching that type.

</details>

2. ▢ Why do `run` and `apply` expose the context object as `this`, while `let` and `also` expose it as `it`?

<details markdown="1"><summary>Check</summary>

`run` and `apply` are declared with a receiver-style function type (`T.() -> R`), where the receiver becomes an implicit `this`; `let` and `also` use an ordinary parameter-style function type (`(T) -> R`), where the object is just a regular lambda parameter, conventionally called `it`.

</details>

## Know this

### A higher-order function call has a real, measurable cost

Every lambda passed to a higher-order function is, underneath, an actual object: it captures a closure (the surrounding variables it references) and gets allocated, and calling it is a virtual call. This is a genuine runtime cost, not a theoretical one, and it adds up specifically at "megamorphic" call sites inside hot loops, where the same higher-order function gets called repeatedly with lambdas the JVM can't easily optimize away.

### `inline` removes that cost by pasting the function's body at the call site

Marking a function `inline fun <T> lock(lock: Lock, body: () -> T): T { ... }` tells the compiler to replace each call site with the function's actual code, and the lambda passed to it, directly, rather than generating a real function-object allocation and a call. `lock(l) { foo() }` compiles roughly as if you'd written `l.lock(); try { foo() } finally { l.unlock() }` yourself, no separate lambda object, no virtual call. This is a real trade-off, not a free win: inlining grows the generated code at every call site, so it's a net benefit specifically for small functions called often, not something to apply reflexively to every higher-order function.

### Inlining is what makes a non-local `return` from inside a lambda legal

Normally, a bare `return` inside a lambda is a compile error, since a lambda is its own separate function object and can't make the *enclosing* function return. But if the function the lambda is passed to is inlined, the lambda's code (return statement included) is pasted directly into the calling function's body, so the `return` genuinely does exit the enclosing function, a **non-local return**. This isn't a special case bolted onto `inline`; it's a direct, mechanical consequence of the lambda no longer being a separate function object by the time the return statement actually executes.

### `noinline` and `crossinline` give fine-grained control per lambda parameter

Not every lambda parameter of an inline function needs to be inlined: `noinline` marks a specific parameter as exempt, letting it be stored, passed around, or otherwise treated as an ordinary function value rather than pasted at the call site (useful when a lambda needs to escape the function, which an inlined one structurally can't). `crossinline` marks a lambda parameter as inlined but *forbidden* from using a non-local return, needed when the lambda's actual execution happens somewhere the non-local return can't safely reach (inside another object or nested function the inline function constructs internally).

### Reified type parameters only exist because inlining erases the usual boundary

Ordinary generic type parameters are erased at runtime (the JVM doesn't know, at runtime, what `T` was for a given `List<T>`), which is why `fun <T> findParentOfType(clazz: Class<T>): T?` needs an awkward `Class<T>` argument just to know what type to check against. `inline fun <reified T> findParentOfType(): T?` removes this need entirely: because the function's body (and its type parameter) gets pasted directly into each call site, the compiler knows the concrete type `T` was called with at that specific site, and operators like `is`/`as` work on `T` almost as if it were an ordinary class, no reflection or extra `Class<T>` parameter needed. `reified` is only legal on an inline function's type parameter specifically because inlining is what removes the erasure boundary that normally makes a type parameter opaque at runtime.

## Practice

1. ▢ What real, measurable cost does a higher-order function call have, absent `inline`?

<details markdown="1"><summary>Check</summary>

Each lambda passed is an actual allocated object capturing its closure, and calling it is a virtual call; both introduce genuine runtime overhead, most noticeable at hot, repeatedly-called ("megamorphic") call sites.

</details>

2. ▢ Why is a bare `return` inside a lambda normally a compile error, and why does marking the enclosing function `inline` make it legal?

<details markdown="1"><summary>Hint</summary>

Consider what "the lambda's code is pasted directly into the calling function" actually does to the meaning of `return` inside it.

</details>

<details markdown="1"><summary>Check</summary>

Normally, a lambda is its own separate function object, so a bare `return` inside it has no enclosing function to return from at that point, only its own lambda body, and Kotlin forbids exactly this ambiguity. When the function the lambda is passed to is inlined, the lambda's code is pasted directly into the calling function's actual body, so a `return` inside it genuinely does exit the enclosing function, a legal non-local return.

</details>

3. ▢ When would you mark an inline function's lambda parameter `noinline` instead of letting it inline normally?

<details markdown="1"><summary>Check</summary>

When that specific lambda needs to escape the function as an ordinary value, stored in a field, passed to something else, or otherwise treated as a real function object, which an inlined lambda structurally can't do, since it no longer exists as a separate object by the time the code runs.

</details>

4. ▢ Why does `reified` only work on a type parameter of an `inline` function, never on an ordinary function's type parameter?

<details markdown="1"><summary>Check</summary>

Ordinary generic type parameters are erased at runtime; the JVM has no record of what `T` actually was for a given call. Inlining removes this erasure by pasting the function's body directly into each specific call site, where the concrete type is known at compile time, which is exactly what lets `reified T` be used almost like a normal class (with `is`, `as`, and no extra `Class<T>` argument) inside the function body.

</details>

5. ▢ Which claim correctly describes inline functions and reified generics?

    - a) `inline` should be applied to every higher-order function by default, since it always improves performance
    - b) `inline` removes lambda-allocation and virtual-call overhead by pasting the function's (and its lambda's) code at the call site, which is also what enables non-local returns and reified type parameters, since both depend on the erasure boundary inlining removes
    - c) `reified` works on any generic function, inline or not, as long as the type parameter is used with `is` or `as`
    - d) `crossinline` and `noinline` do the same thing, just with different names

<details markdown="1"><summary>Check</summary>

**b)** That's the precise, connected mechanism this lesson traces: one feature (inlining) enabling two others (non-local return, reified generics) as direct consequences, not three unrelated features. (a) is false: inlining grows generated code at every call site, a real cost that only pays off for small, frequently-called functions. (c) is false: `reified` is only legal on an inline function's type parameter, precisely because only inlining removes the runtime erasure that would otherwise make the type parameter opaque. (d) is false: `noinline` exempts a lambda from inlining entirely; `crossinline` still inlines the lambda but forbids it from using a non-local return.

</details>

## Real-world reps

- [ ] Find an `inline` function in a codebase you've written or have access to (or in the Kotlin standard library, like `let` or `run` themselves, which are inline). Confirm you can explain what cost inlining it actually removes at its call sites.
- [ ] Find a generic function using a `Class<T>` or similar reflection-based workaround to know its type parameter at runtime. Consider whether making it an `inline fun <reified T>` would remove that workaround.
- [ ] Tomorrow: read the primary source's section on non-local returns in full, and construct a small example (on paper or in code) where a non-local return from inside a lambda passed to an inline function changes the calling function's actual control flow.

## Going further

- [Docs: "Inline functions", Kotlin](https://kotlinlang.org/docs/inline-functions.html)
- [Docs: "Higher-order functions and lambdas", Kotlin](https://kotlinlang.org/docs/lambdas.html)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
