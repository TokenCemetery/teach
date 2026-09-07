---
title: 13. Extension Functions
description: Adding behavior to a type without inheritance, and the static-dispatch gotcha that trips people up the first time they hit it
type: lesson
---

# Lesson 13. Extension Functions

**Mission link:** Stage 3 opens idiom. Lesson 7 already named the extension function as the thing Kotlin's own docs recommend over a plain class for adding behavior; this lesson is that construct made concrete, and the first of several idioms (with scope functions, higher-order functions, and more to follow) a reviewer would recognize as actually Kotlin, not translated Java.
**Primary source:** [Docs: "Extensions", Kotlin](https://kotlinlang.org/docs/extensions.html)
**Prerequisites:** [Lesson 12](0012-interfaces-with-default-methods.md), [Platform type](../GLOSSARY.md)

## Warm-up

1. ▢ Why can't a Kotlin interface hold a property with a real backing field?

<details markdown="1"><summary>Check</summary>

Interfaces can't store state at all; a property declared in an interface must either be abstract (a required declaration with no value) or provide an accessor implementation, since there's no backing field for the accessor to read from or write to.

</details>

2. ▢ Why does Kotlin force an explicit resolution for a diamond conflict between two interfaces' default implementations, rather than picking one automatically?

<details markdown="1"><summary>Check</summary>

Silently picking one implementation over another would hide a real design decision inside code that merely compiles; forcing an explicit `override` with `super<Type>.method()` calls makes the decision visible and deliberate instead.

</details>

## Know this

### An extension function adds a callable, without adding a member

`fun String.truncate(maxLength: Int): String { ... }` declares an extension function on `String`: called with ordinary member syntax (`"hello".truncate(3)`), but it isn't actually added to the `String` class itself. The type the function is declared on is called the **receiver type**, and `this` inside the function body refers to the specific instance it's called on (the **receiver**). This is exactly the tool lesson 7's own documentation pointed to: adding behavior to an existing type, including one you don't own (a class from a library, or `String` itself), without inheritance, a wrapper class, or a Decorator-pattern workaround.

### Extensions genuinely don't modify the class; they only make new syntax callable

The documentation is explicit about this: an extension function or property never adds a real member to the class or interface it extends. Nothing about the class's own definition changes; the extension only makes a new function or property *callable* using member-access syntax, resolved by the compiler at the call site rather than by anything actually attached to the class. This is why extensions work on classes you have no ability to modify, including final classes and classes from external libraries, since nothing about the original class needs to change at all.

### The gotcha: extension functions resolve statically, by declared type, not the runtime instance

This is the one genuinely surprising behavior worth internalizing precisely: `fun Shape.getName() = "Shape"` and `fun Rectangle.getName() = "Rectangle"` (where `Rectangle` is a subclass of `Shape`), called through a variable declared as type `Shape` holding an actual `Rectangle` instance, resolves to `Shape.getName()`, not `Rectangle.getName()`. Extension functions are dispatched statically: the compiler picks which extension to call based on the variable's declared type at compile time, never the object's actual runtime type. This is the opposite of how overriding a member function works (a member override always dispatches to the actual runtime type, virtually), and it's exactly the kind of subtle difference that produces a real bug for anyone assuming extension functions behave like inherited, overridable methods.

### A member function always wins over an extension function with the same signature

If a class already has a member function, and an extension function is declared with the same receiver type, name, and compatible arguments, the member function takes precedence at every call site; the extension is simply never reached for that exact signature. An extension can still *overload* a member (same name, different parameters), in which case ordinary overload resolution picks whichever matches the actual arguments, but it can never shadow or replace an existing member with a matching signature.

## Practice

1. ▢ What does `fun String.truncate(maxLength: Int): String { ... }` actually change about the `String` class itself?

<details markdown="1"><summary>Check</summary>

Nothing: the `String` class's own definition is entirely unchanged. The extension only makes `truncate()` callable using member-access syntax (`"hello".truncate(3)`), resolved by the compiler at the call site, not by any actual member added to `String`.

</details>

2. ▢ `open class Shape`, `class Rectangle : Shape()`, `fun Shape.getName() = "Shape"`, `fun Rectangle.getName() = "Rectangle"`. A function takes a parameter `shape: Shape` and calls `shape.getName()`, but the actual argument passed in is a `Rectangle` instance. What does `shape.getName()` return, and why?

<details markdown="1"><summary>Hint</summary>

Consider whether extension function resolution looks at the variable's declared type or the object's actual runtime type.

</details>

<details markdown="1"><summary>Check</summary>

It returns `"Shape"`. Extension functions are dispatched statically, resolved by the compiler based on the variable's *declared* type (`Shape`) at compile time, not the actual runtime type of the object it holds (`Rectangle`), even though the object is genuinely a `Rectangle` instance.

</details>

3. ▢ Why is this static-dispatch behavior the opposite of how an overridden member function works?

<details markdown="1"><summary>Check</summary>

An overridden member function dispatches virtually, at runtime, based on the object's actual type, regardless of the variable's declared type; that's the entire point of overriding. Extension functions dispatch statically, at compile time, based purely on the declared type, so a subclass's same-named extension is never reached through a variable declared as the superclass's type, unlike a genuinely overridden member.

</details>

4. ▢ A class `Example` has a member function `printFunctionType()`, and an extension function `fun Example.printFunctionType()` is declared with the exact same name and parameters. Which one runs when `Example().printFunctionType()` is called?

<details markdown="1"><summary>Check</summary>

The member function runs. When a class already has a member with the same receiver type, name, and compatible arguments as an extension function, the member always takes precedence; the extension with that exact signature is never reached.

</details>

5. ▢ Which claim correctly describes extension functions?

    - a) An extension function is added as a real member of the class it extends, callable virtually like an inherited method
    - b) Extension functions add new callable syntax without modifying the extended class, and are resolved statically by the variable's declared type at compile time, not the object's actual runtime type
    - c) An extension function with the same signature as an existing member function always overrides that member
    - d) Extension functions can only be declared on classes you own; they don't work on final classes or classes from external libraries

<details markdown="1"><summary>Check</summary>

**b)** That's the precise mechanism and the precise gotcha this lesson covers. (a) is false: extensions never modify the class; they only make new syntax callable, resolved by the compiler rather than attached to the class. (c) is false: a member function with a matching signature always wins over an extension; the extension is simply never reached in that case. (d) is false: extensions work on any class, including final ones and library classes, precisely because nothing about the original class needs to change.

</details>

## Real-world reps

- [ ] Find an extension function you've written or have access to (or one from the Kotlin standard library, like `.filterNotNull()` or `.joinToString()`). Confirm you can explain why it's implemented as an extension rather than a member of the class it extends.
- [ ] Construct (or recall) a case with a superclass and subclass where an extension function is declared on both with the same name. Trace through what a call via a superclass-typed variable holding a subclass instance actually resolves to, and confirm it matches this lesson's static-dispatch rule.
- [ ] Tomorrow: read the primary source's section on extension properties in full, and note one meaningful difference between an extension property and an extension function beyond the obvious value-versus-function distinction.

## Going further

- [Docs: "Extensions", Kotlin](https://kotlinlang.org/docs/extensions.html)
- [Docs: "Classes", Kotlin](https://kotlinlang.org/docs/classes.html)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
