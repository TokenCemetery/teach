---
title: 1. Structs and Classes
description: The type-system choice Java never gave you, and what the CLR actually does with each
type: lesson
---

# Lesson 1. Structs and Classes

**Mission link:** "The type system" and "what the CLR does with what you wrote" both start here: struct versus class is the first place a Java instinct (everything is a class) actively misleads, because Java never offered this choice for a user-defined type.
**Primary source:** [Docs: "Types (C# reference)", Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/types/)
**Prerequisites:** none

## Know this

### The choice Java doesn't have

Java has exactly two kinds of type: primitives (`int`, `double`, `boolean`, and a handful of others, all built into the language) and everything else, which is a reference type (a class). You cannot define your own value type in Java; if you want a new type, you write a class, full stop. That habit, "a new type means a class," is the correct and only option in Java.

C# gives you a second option for a user-defined type: a **struct**. This isn't a minor syntax variant of a class; it changes what actually happens in memory and at every assignment.

### Value types versus reference types

- A **struct** is a **value type**. Assigning one struct-typed variable to another copies the entire value. Passing a struct to a method copies it into the parameter. Two struct-typed variables holding "the same" data are two entirely independent copies; mutating one can never affect the other.
- A **class** is a **reference type**. Assigning one class-typed variable to another copies the *reference*, not the object. Two class-typed variables can point at the very same object, and mutating through either one is visible through both. This is the behavior every reference in Java already has, since every Java object is accessed this way.

The Java habit of reaching for a class for any new type carries an implicit assumption: that assignment and parameter-passing always mean "share a reference." In C#, that assumption is only true for classes. A struct silently breaks it, in a way that either helps you (independent copies, no aliasing bugs) or surprises you (a mutation you expected to propagate doesn't), depending on whether you knew which one you were using.

### What the CLR actually does differently

This isn't just a language-level abstraction. A struct's data is typically stored inline, wherever it's used: inside a containing object, inside an array slot, or on the stack, rather than as a separate object on the managed heap. A class instance always lives on the managed heap, and what you hold is a reference (effectively a pointer) to it. This is why passing a small struct around can avoid heap allocations a class of the same shape would require, and it's also exactly why copying a struct copies real data rather than a cheap pointer.

### When a struct is actually the right call

Microsoft's own guidance, and the practical rule this lesson is built around: reach for a `struct` when a type is **small, logically immutable, and represents a single value** (a 2D point, a money amount, an RGB color), the same role Java's primitives play, extended to your own types. Default to a `class` for anything else, especially anything with identity that matters, anything large, or anything meant to be mutated through shared references.

**Mutable structs are a specific, well-known footgun**, and worth naming directly: because a struct copies on every access, mutating a struct returned from a property or method often mutates a temporary copy, not the object you thought you were changing, and the compiler doesn't always warn you. This is different from, and easy to confuse with, the class-aliasing surprise above; it's the mirror-image mistake, expecting a mutation to be independent (correct, for a true copy) when you actually wanted it to be shared, and reached for a struct without realizing that meant giving up sharing.

## Practice

1. ▢ In one sentence, what does assigning one struct-typed variable to another actually do, compared to assigning one class-typed variable to another?

<details markdown="1"><summary>Check</summary>

Assigning a struct copies its entire value, producing two fully independent copies; assigning a class copies only the reference, so both variables end up pointing at the same underlying object.

</details>

2. ▢ A developer with a pure Java background defines a C# type the way they always would: `class Point { public int X; public int Y; }`. They pass a `Point` into a method that modifies its `X`, and are confused that the caller's `Point` changed too, since "I only passed it in, I didn't ask to modify the original." What's actually happening, and is it a bug?

<details markdown="1"><summary>Check</summary>

It's not a bug; it's exactly how a reference type is supposed to work, and it's the same behavior every Java object reference already has. `class` in C# is a reference type, so passing a `Point` instance passes a reference to the same object; a modification inside the method is visible to the caller because there's only ever one `Point` object involved. If independent copies were wanted, `Point` should have been a `struct`.

</details>

3. ▢ `Rectangle` is defined as a `struct` with a mutable `Size` property (also a `struct`). Code does `myRectangles[0].Size.Width = 10;` (or the equivalent through a method), expecting to update the rectangle stored in the list. Why might this not work the way they expect?

<details markdown="1"><summary>Hint</summary>

What gets copied every time a struct is accessed through a property or an indexer?

</details>

<details markdown="1"><summary>Check</summary>

Accessing `myRectangles[0]` and then `.Size` can each produce a copy of the struct data being accessed, rather than a direct handle to the original storage location, depending on exactly how the access is expressed. The mutation can end up applied to a temporary copy that's immediately discarded, leaving the original `Rectangle` in the list unchanged. This is the mutable-struct footgun this lesson names directly: it's easy to write code that looks like it mutates shared state when a struct's copy semantics mean it doesn't.

</details>

4. ▢ Which of these is the best candidate for a `struct` rather than a `class`, per the guidance in this lesson?

   - a) A `Customer` type representing a specific customer record with a database identity, potentially large, mutated throughout a request's lifetime
   - b) A `Money` type holding a currency code and a decimal amount, small, logically immutable, compared by value
   - c) A `Connection` type wrapping a network socket, with a lifecycle that must be explicitly closed
   - d) A `ShoppingCart` type holding a mutable, potentially large list of items, shared across several parts of a request

<details markdown="1"><summary>Check</summary>

**b)** `Money` fits the profile directly: small, logically immutable, representing a single value compared by its contents rather than by identity. (a), (c), and (d) all have identity, size, or lifecycle characteristics that call for reference-type semantics instead.

</details>

## Real-world reps

- [ ] Find (or write) a small C# type you'd use to represent a single value (a point, a money amount, a date range). Check whether it's currently a `class` or a `struct`, and decide which it should be using this lesson's guidance.
- [ ] Write a short C# snippet that demonstrates the aliasing behavior of a `class`: two variables referencing the same object, where a mutation through one is visible through the other. Then rewrite it using a `struct` and confirm the mutation no longer propagates.
- [ ] Tomorrow: read the Structure types reference doc in full, and find one rule about structs (default constructors, `readonly struct`, boxing) you hadn't already accounted for in how you think about them.

## Going further

- [Docs: "Structure types (C# reference)", Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/builtin-types/struct)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
