---
title: 2. Identity and Equality
description: == compares references, so it answers a different question for strings and boxed numbers
type: lesson
---

# Lesson 2. Identity and Equality

**Mission link:** `==` on objects is the bug that passes every test on small input and fails in production, because the values that make it work are the ones a test happens to use.
**Primary source:** [`Object.equals`, Java SE 25 API](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/Object.html)
**Prerequisites:** [Lesson 1](0001-references-are-values.md)

## Warm-up

1. ▢ A method takes a `List` and calls `clear()` on it. Can the caller see that? Can the caller's variable be made to refer to a different list?

<details markdown="1"><summary>Check</summary>

Yes to the first: the method reaches the caller's object. No to the second: the parameter is a copy of the reference, so assigning to it changes nothing outside.

</details>

2. ▢ What is a field of type `String` set to before anything assigns to it?

<details markdown="1"><summary>Check</summary>

`null`. Fields get defaults, and the default for every reference type is `null`.

</details>

## Know this

`==` compares what the variables hold ([JLS 15.21.3](https://docs.oracle.com/javase/specs/jls/se25/html/jls-15.html#jls-15.21.3)). For primitives that is the value. For references that is the reference, so `==` asks **"is this the same object"** and nothing else.

`equals` is an ordinary method. `Object`'s implementation is identity, so a class that does not override it gets `==` behaviour under a different name.

```java
String a = new String("svc");
String b = new String("svc");
a == b          // false, two objects
a.equals(b)     // true, String defines equality by content
```

### The string pool makes `==` look correct

String literals are **interned**: the compiler puts identical literals in a shared pool, so they are the same object.

```java
String x = "svc";
String y = "svc";
x == y                          // true, both refer to the pooled literal

String z = new String("svc");
x == z                          // false, new String forces a distinct object

String w = "s" + "vc";          // constant-folded at compile time
x == w                          // true

String part = "s";
String v = part + "vc";         // built at run time
x == v                          // false
```

Every one of those lines is `equals`-true. The `==` results depend on whether the string happened to be created at compile time, which is not a property of your program's logic. Code that uses `==` on strings works until a value arrives from a file, a socket, or a database, and then it stops.

### Integer caching makes `==` look correct too

Autoboxing turns an `int` into an `Integer` by calling `Integer.valueOf`, which is required to cache values from `-128` to `127`:

```java
Integer small1 = 127, small2 = 127;
small1 == small2        // true, same cached object

Integer big1 = 128, big2 = 128;
big1 == big2            // false, two objects

big1.equals(big2)       // true
```

So `==` on boxed integers is correct for small numbers and wrong for large ones. An `id` field is exactly where this bites, because ids grow past 127.

Mixing a boxed and a primitive type is different again: one operand is unboxed, so `==` compares numbers and behaves as you expect. That makes the rule harder to remember, not easier, so use the simple one: **never write `==` between two reference types unless you mean identity.**

### The idioms to use instead

```java
Objects.equals(a, b)                 // null-safe on both sides
"expected".equals(actual)            // constant first, so a null actual is false
status == Status.ACTIVE              // enums are singletons, so == is right here
```

`Objects.equals` returns `true` when both are `null`, `false` when exactly one is, and otherwise calls `a.equals(b)`. It is the default choice.

For primitives, `==` is correct and the only option. For `double`, be aware that `0.1 + 0.2 == 0.3` is `false`, which is floating-point arithmetic rather than a Java quirk, and that `Double.compare` is what a comparator should use.

## Practice

1. ▢ Predict all four.

   ```java
   String a = "config";
   String b = "config";
   String c = new String("config");
   String d = "con" + "fig";

   System.out.println(a == b);
   System.out.println(a == c);
   System.out.println(a == d);
   System.out.println(a.equals(c));
   ```

<details markdown="1"><summary>Check</summary>

`true`, `false`, `true`, `true`.

`b` and `d` are the pooled literal, since `"con" + "fig"` is folded by the compiler into a constant. `c` was explicitly constructed, so it is a distinct object with the same content.

The lesson is not the four answers. It is that three of them depend on how the string was built rather than on what it contains.

</details>

2. ▢ Predict both, then say which line you would flag in review.

   ```java
   Integer x = 127, y = 127;
   Integer p = 128, q = 128;
   System.out.println(x == y);
   System.out.println(p == q);
   ```

<details markdown="1"><summary>Hint</summary>

Autoboxing goes through `Integer.valueOf`, and that method has a documented cache with a documented range.

</details>

<details markdown="1"><summary>Check</summary>

`true`, then `false`.

Both lines get flagged. The first is worse than the second, because it works: a test written with small values passes, and the same code fails on real ids. Use `x.equals(y)`, or better keep the values as `int` where no boxing happens at all.

</details>

3. ▢ Which of these is safe when `input` may be `null`?

   - a) `input.equals("yes")`
   - b) `"yes".equals(input)`
   - c) `Objects.equals(input, "yes")`
   - d) `input == "yes"`

<details markdown="1"><summary>Check</summary>

**b)** and **c)** are safe.

Option a throws `NullPointerException`. Option d does not throw and is wrong for a different reason: it compares identity, so it is false for any string that was not the pooled literal.

Between b and c, prefer c when either side may be null or when the constant-first form reads as a trick. Prefer b when you want no import and the constant is genuinely a constant.

</details>

4. ▢ A cache is keyed by `Long` account ids and misses constantly in production, while the unit tests pass. The lookup is `if (key == cachedKey)`. Explain both halves of that: why the tests pass, and why production misses.

<details markdown="1"><summary>Check</summary>

The tests use small ids, in the range `-128` to `127`, where `Long.valueOf` returns cached objects, so `==` finds them equal.

Production ids are larger, so every boxing creates a distinct object and `==` is false however equal the numbers are. The fix is `key.equals(cachedKey)`, or `Objects.equals`, or keeping the id as a `long` and comparing with `==` on primitives.

This shape, working on small input and failing on real input, is the reason the cache range exists as a trap at all.

</details>

5. ▢ When is `==` between two reference-typed expressions the correct thing to write?

<details markdown="1"><summary>Check</summary>

When identity is genuinely the question. Three real cases: comparing against `null`, comparing enum constants, and checking whether two references are the same object on purpose, for example to detect self-assignment or to short-circuit an expensive `equals`.

Enums are the one place `==` is idiomatic and preferred, because constants are singletons and `==` is null-safe where `equals` would need a guard.

</details>

## Real-world reps

- [ ] Run the four string comparisons yourself, then add a fifth built by reading a line from standard input and compare it with `==` and `equals`. Watching it fail on real input is the version that sticks.
- [ ] Run the `Integer` pair at `127` and `128`. Then read the `valueOf` documentation and find where the cache range is stated.
- [ ] Tomorrow: search code you know for `== ` next to a `String` or a boxed type. Every hit is either a bug or an identity check that deserves a comment saying so.

## Going further

- [`Object.equals`](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/Object.html): the contract, which lesson 3 is entirely about
- [`Integer.valueOf`](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/Integer.html): where the cache range is specified
- [`String`](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/String.html): interning, and what `intern()` actually does
- [JLS 15.21.3, Reference Equality Operators](https://docs.oracle.com/javase/specs/jls/se25/html/jls-15.html#jls-15.21.3)
- [Equality, hashing and ordering](../reference/equality-hashing-and-ordering.md): the reference sheet for this stage
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
