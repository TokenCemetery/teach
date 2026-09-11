---
title: Null Safety and Mutability
description: Nullability as part of the type, val versus var and reference-vs-object mutability, and structural versus referential equality
type: reference
---

# Null Safety and Mutability

Predicting nullability and mutability without running the code. Built for lookup when reading or reviewing Kotlin.

## Nullability is part of the type

`String` is guaranteed by the compiler to never hold `null`, at every assignment and call site; `String?` may hold `null`, and the compiler forces handling that before it can be used as a plain `String`. This is enforced, not a convention.

| Operator | Does |
|---|---|
| Safe call, `?.` | `user?.name` evaluates to `null` immediately if `user` is `null`, instead of throwing; chains short-circuit at the first `null` link |
| Elvis, `?:` | `user?.name ?: "unknown"` supplies a default when the left side is `null` |
| Not-null assertion, `!!` | Forces treatment as non-null; throws `NullPointerException` immediately if actually `null` |

**Java habits that compile but signal unexamined defaults:**

- A redundant `if (name != null)` on an already-non-nullable `String`: the check can never be false, since the compiler already ruled the case out.
- Routine `!!` used to silence the compiler rather than backed by specific evidence: this recreates the exact runtime crash null safety exists to prevent.

**Platform types** (`String!`, unwritable syntax) appear when Kotlin calls an unannotated Java method: Kotlin can't determine nullability, so it lets the caller treat the result as either, trusting them to know which. Treat it as nullable unless there's positive evidence (a `@NotNull` annotation, documented behavior); this is exactly where null safety's guarantee stops being automatic.

## `val`/`var`: reference immutability, not object immutability

`val` declares a reference assigned exactly once (a compile error to reassign); `var` allows reassignment. This is enforced identically to nullability: not a lint rule, a type-system guarantee.

**The single most consequential distinction**: `val` guarantees the *reference* is fixed, not that the *object* it points to is immutable.

```text
val list = mutableListOf(1, 2, 3)
list.add(4)   // compiles and works: mutating the object, not reassigning the reference
```

| | `List` (read-only interface) | `MutableList` |
|---|---|---|
| `val` | Reference fixed, contents fixed | Reference fixed, contents mutable (the case people mistake for read-only) |
| `var` | Reference reassignable, contents fixed | Reference reassignable, contents mutable |

**A mutable collection held by `val` is still mutable, by design.** `val` protects the reference; the read-only (`List`/`Set`/`Map`) vs mutable (`MutableList`/`MutableSet`/`MutableMap`) interface pair controls object mutability, independently and compositionally.

**"Read-only" is not the same guarantee as "immutable".** A `List` reference has no mutating methods, but if the same underlying object is also reachable through a `MutableList` reference elsewhere, a mutation through that other reference is visible through the read-only one too, since it's the same object. Read-only restricts what *this reference's interface* permits, not that the data can never change from anywhere in the program.

**`String` is immutable regardless of `val`/`var`.** `.uppercase()`, `.replace(...)`, `+` all return a *new* `String`; there is nothing to mutate in place, so `val`/`var` on a `String` reference is purely about reassignment, never about the string's own contents.

## `==` vs `===`: structural vs referential equality

Kotlin inverts Java's `==`: `==` is **structural equality** (calls `a.equals(b)`, compares content); `===` is **referential equality** (same object in memory). `a == b` desugars to `a?.equals(b) ?: (b === null)`.

A Java habit of reaching for `===` expecting it to be needed for "real" equality is backwards: `==` already does what Java's `.equals()` was for; `===` is the rarer, specialized operator (singleton checks, cache identity).

**`equals()` defaults to referential equality** (inherited from `Any`) unless overridden. A plain class with no custom `equals()` behaves identically under `==` and `===`; two instances with identical property values are still `==`-unequal. Data classes and value classes generate a structural `equals()` automatically; a plain class needs one written by hand.

**Overriding `equals()` without `hashCode()` breaks hash-based collections.** A `HashSet`/`HashMap` buckets by `hashCode()` before ever calling `equals()`, so two `==`-equal objects with different `hashCode()` values can be looked up in the wrong bucket and never found, appearing "missing" even though an equal object was inserted.

## Related

- [Lesson 1](../lessons/0001-null-safety.md), [Lesson 2](../lessons/0002-val-var-and-immutability.md), [Lesson 3](../lessons/0003-values-vs-references.md), [Lesson 4](../lessons/0004-basic-types-and-string-templates.md), [Lesson 5](../lessons/0005-collections-basics.md)
