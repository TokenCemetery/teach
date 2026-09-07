---
title: 4. Basic Types and String Templates
description: Why Kotlin has no primitives at the language level, and string templates as a language feature rather than concatenation with extra syntax
type: lesson
---

# Lesson 4. Basic Types and String Templates

**Mission link:** Lesson 3 established that `==` calls `equals()` on objects; this lesson is why that's true even for numbers and booleans in Kotlin, unlike Java's primitives, and the string templates already used without comment since lesson 1.
**Primary source:** [Docs: "Types overview", Kotlin](https://kotlinlang.org/docs/types-overview.html)
**Prerequisites:** [Lesson 3](0003-values-vs-references.md), [Platform type](../GLOSSARY.md)

## Warm-up

1. ▢ What does `==` check in Kotlin, and how does that differ from what `==` checks in Java for reference types?

<details markdown="1"><summary>Check</summary>

Kotlin's `==` checks structural equality, calling `equals()` to compare content; Java's `==` on reference types checks whether two variables point to the same object, requiring an explicit `.equals()` call for content comparison instead.

</details>

2. ▢ What concrete bug can result from overriding `equals()` without also overriding `hashCode()`?

<details markdown="1"><summary>Check</summary>

A hash-based collection (`HashSet`, `HashMap`) buckets objects by `hashCode()` before ever calling `equals()`; if two `==`-equal objects have different `hashCode()` values, a lookup can look in the wrong bucket and never find an object that's logically present, appearing "missing" even though it was inserted.

</details>

## Know this

### Kotlin has no primitive types at the language level, unlike Java

Java splits types into primitives (`int`, `boolean`, `char`, with no methods and no null) and reference types (objects, which can be null and have methods). Kotlin doesn't make this split visible to you: `Int`, `Boolean`, `Char`, and the other basic types are ordinary classes with member functions and properties, the same as any other type, even though the compiler optimizes them to the JVM's primitive representation at runtime whenever it can. `5.toString()` and `5.plus(3)` are real method calls on `Int`, not special syntax; this is what makes Kotlin's "everything is an object" description literal rather than a simplification.

### This is why generic type parameters work uniformly with numbers

Because Kotlin's basic types are real classes, they can be used as generic type arguments directly: `List<Int>` works the same way `List<String>` does, with no boxing-related asymmetry to reason about at the language level (`Int` still gets boxed to `java.lang.Integer` on the JVM where a generic type erases to `Object`, but that's a runtime detail the language design hides from you, not something you write different code to work around).

### String templates: interpolation is a language feature, not concatenation

A **string template** embeds an expression directly inside a string literal: `"$name"` substitutes the value of `name`, and `"${expr}"` substitutes the result of evaluating any expression (`"${user.name.uppercase()}"`, `"${a + b}"`). This isn't syntactic sugar over `+`-based concatenation bolted on afterward; it's Kotlin's actual way of building a string from parts, and it's why every lesson so far has written `"Hello, $name"` rather than `"Hello, " + name`. The simple `$name` form only works for a bare identifier; anything more than that (a property access, a method call, an expression) needs the `${...}` braces.

### `String` is immutable, the same shape of guarantee as `val`

Kotlin's `String` type is immutable: once created, its contents never change, and every operation that looks like it modifies a string (`.uppercase()`, `.replace(...)`, `+`) actually returns a new `String` rather than mutating the original. This is independent of whether the reference holding it is `val` or `var` (lesson 2): a `var name: String` can be reassigned to point at a different string, but neither `val` nor `var` ever makes the string object itself mutable, since `String` simply has no mutating methods to call.

## Practice

1. ▢ Why can you call `.toString()` or `.plus()` directly on an `Int` literal in Kotlin, when Java's `int` primitive has no methods at all?

<details markdown="1"><summary>Check</summary>

Kotlin's basic types, including `Int`, are ordinary classes at the language level with real member functions, unlike Java's primitives; the compiler optimizes them to a primitive representation at runtime where possible, but that's an implementation detail hidden from the code you write.

</details>

2. ▢ Why does `"${a + b}"` need braces while `"$name"` doesn't?

<details markdown="1"><summary>Hint</summary>

Consider what the simple `$identifier` form is actually able to parse versus a general expression.

</details>

<details markdown="1"><summary>Check</summary>

The bare `$identifier` form only recognizes a simple identifier reference; anything beyond that, an expression, an operation, a method call, or a property access, needs the `${...}` form so the template can parse and evaluate the full expression rather than just substituting a single variable's value.

</details>

3. ▢ `val name = "Ada"` followed by `name.uppercase()`. Does this mutate `name`'s value? What does `name` hold afterward if the result isn't captured?

<details markdown="1"><summary>Check</summary>

No: `String` is immutable, so `.uppercase()` returns a new `String` ("ADA") rather than modifying the original. If the result isn't captured into a variable, it's simply discarded, and `name` still holds `"Ada"` afterward, unchanged.

</details>

4. ▢ Why does the fact that Kotlin's basic types are real classes matter for how `List<Int>` and `List<String>` behave from the language's perspective?

<details markdown="1"><summary>Check</summary>

Because `Int` is a real class rather than a primitive, it can be used as a generic type argument exactly the same way `String` can, with no special-casing needed at the language level; the JVM's boxing of `Int` to `java.lang.Integer` for generics is a runtime detail Kotlin's design hides rather than something the code has to account for explicitly.

</details>

5. ▢ Which claim correctly describes Kotlin's basic types and string templates?

   - a) `Int` and other basic types are primitives with no methods, exactly like Java, for runtime performance
   - b) Kotlin's basic types are real classes with member functions, optimized to a primitive representation at runtime where possible; string templates (`$name`, `${expr}`) are the language's actual mechanism for building strings from parts, not sugar over concatenation
   - c) String templates only work with the `${...}` braces; the bare `$name` form is deprecated
   - d) `String`'s immutability depends on whether it's held by a `val` or a `var`

<details markdown="1"><summary>Check</summary>

**b)** That's the precise pair of facts this lesson covers. (a) is false: Kotlin's basic types have real methods at the language level, unlike Java's primitives. (c) is false: the bare `$name` form is the standard shorthand for a simple identifier; braces are needed only for a fuller expression. (d) is false: `String` immutability is a property of the type itself, independent of whether the holding variable is `val` or `var` (lesson 2's reference-vs-object distinction again).

</details>

## Real-world reps

- [ ] Find a Kotlin file you've written or have access to. Count how many string concatenations use `+` versus a string template, and consider whether any `+`-based ones would read more clearly as a template.
- [ ] Find a place where a basic type (`Int`, `Boolean`, `Double`) is used as a generic type argument (in a `List<Int>`, a `Map<String, Int>`, or similar). Confirm you can explain why this doesn't need special handling the way Java's primitive-vs-boxed distinction sometimes does.
- [ ] Tomorrow: read the primary source's overview of Kotlin's number types in full, and note one thing that surprised you about how they behave compared to Java's primitives.

## Going further

- [Docs: "Types overview", Kotlin](https://kotlinlang.org/docs/types-overview.html)
- [Docs: "Strings", Kotlin](https://kotlinlang.org/docs/strings.html)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
