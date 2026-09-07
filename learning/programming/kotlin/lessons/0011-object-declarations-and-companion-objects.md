---
title: 11. Object Declarations and Companion Objects
description: Singletons declared, not implemented by hand, and companion objects as Kotlin's actual replacement for Java's static members
type: lesson
---

# Lesson 11. Object Declarations and Companion Objects

**Mission link:** Lesson 10 covered enum constants as singleton objects, without covering the standalone `object` keyword itself. This lesson is that keyword, and companion objects, the construct most directly replacing a Java habit: reaching for `static` out of reflex.
**Primary source:** [Docs: "Object declarations and expressions", Kotlin](https://kotlinlang.org/docs/object-declarations.html)
**Prerequisites:** [Lesson 10](0010-enums.md), [Platform type](../GLOSSARY.md)

## Warm-up

1. ▢ Why can `enum class Color(val rgb: Int) { RED(0xFF0000), ... }` give each constant its own distinct value?

<details markdown="1"><summary>Check</summary>

Because each Kotlin enum constant is a real object, an instance of the enum class, it can be constructed with its own constructor arguments the same way any class instance can.

</details>

2. ▢ What signal suggests a set of enum constants would actually fit a sealed class better?

<details markdown="1"><summary>Check</summary>

Constants needing genuinely different data shapes (extra fields relevant only to some constants, not all) signal the variants aren't really the same *kind* of thing; a sealed class, where each variant can carry its own distinct data, fits better than forcing awkward, sparsely-relevant fields onto an enum.

</details>

## Know this

### `object` declares a class and creates its one instance, in one step

`object DataProviderManager { ... }` does two things at once: it defines a class, and it creates the single instance of that class that will ever exist, both in one declaration. This is Kotlin's built-in way to implement the **singleton pattern** (exactly one instance of a class, globally accessible) without the manual boilerplate Java requires (a private constructor, a static instance field, a static accessor method, and often extra care to make it thread-safe). Referring to the object uses its name directly, `DataProviderManager.registerDataProvider(...)`, no separate instantiation step anywhere.

### The singleton's initialization is thread-safe and lazy, by the language itself

An `object` declaration's initialization happens on first access and is guaranteed thread-safe by Kotlin itself; this is exactly the kind of correctness detail a hand-written Java singleton has to get right deliberately (double-checked locking, an eagerly-initialized static field, or an enum-based singleton trick), and Kotlin provides it as a language guarantee instead of a pattern to implement correctly by hand.

### A companion object replaces Java's `static` members

Kotlin has no `static` keyword at all; a class's members are always instance members. What replaces Java's static fields and methods is a **companion object**: `class MyClass { companion object { fun create(): MyClass = MyClass() } }` declares an object tied to the class itself (at most one companion object per class), whose members are accessed via the class name directly (`MyClass.create()`), the same call-site syntax Java's static methods use. This is a deliberate design choice, not an oversight: a companion object is a real object, meaning it can implement interfaces, have its own supertype, and be passed around as a value where a static member never could be.

### Companion objects are commonly used for factory functions

A very common use of a companion object is a **factory function**, a function that constructs and returns an instance, standing in for (or alongside) a constructor: `class User private constructor(val name: String) { companion object { fun create(name: String): User? = if (name.isNotBlank()) User(name) else null } }`. This lets construction include logic a plain constructor can't (validation that might fail, returning a cached instance instead of a new one, choosing between subclasses), while still reading at the call site (`User.create("Ada")`) almost exactly like calling a constructor.

## Practice

1. ▢ What two things does an `object` declaration do in one step, and how does this compare to Java's manual singleton pattern?

<details markdown="1"><summary>Check</summary>

It defines a class and creates its single instance simultaneously. Java's manual equivalent requires a private constructor, a static instance field, and a static accessor method, with extra care needed to make initialization thread-safe; Kotlin's `object` provides all of this, including thread-safe lazy initialization, as a single language construct.

</details>

2. ▢ Why is a companion object described as a real object, and why does that matter compared to Java's `static` members?

<details markdown="1"><summary>Hint</summary>

Consider what a companion object can do that a Java static method or field structurally can't.

</details>

<details markdown="1"><summary>Check</summary>

A companion object is an actual object instance, not merely a namespace for members the way Java's `static` is; this means it can implement interfaces, have its own supertype, and be passed around as a value (assigned to a variable, used as an argument), none of which is possible with Java's static members, which aren't objects at all.

</details>

3. ▢ Why does construction via a companion object factory function (`User.create("Ada")`) sometimes fit better than a plain public constructor?

<details markdown="1"><summary>Check</summary>

A factory function can include logic a plain constructor can't cleanly express: validation that might fail and return `null` (or throw) instead of always producing an instance, returning a cached or shared instance instead of always constructing a new one, or choosing among subclasses to return. It still reads at the call site almost exactly like calling a constructor, while allowing this extra logic.

</details>

4. ▢ A team writes `object Logger { fun log(message: String) { println(message) } }` and calls `Logger.log("started")` from many places in their codebase. What does the `object` declaration guarantee here that a plain class with a `log` method wouldn't?

<details markdown="1"><summary>Check</summary>

It guarantees exactly one `Logger` instance exists throughout the application, created lazily and thread-safely on first access, with no separate instantiation step anywhere; a plain class would require callers to either share one manually-managed instance (risking accidental duplicate instances or unsafe concurrent initialization) or create a new instance per use, neither of which the `object` declaration requires anyone to get right by hand.

</details>

5. ▢ Which claim correctly describes object declarations and companion objects?

    - a) Kotlin has a `static` keyword, used the same way Java's is
    - b) `object` declares a class and its single instance together, with thread-safe lazy initialization guaranteed by the language; a companion object is Kotlin's replacement for Java's static members, and unlike a static member, it's a real object that can implement interfaces or be passed as a value
    - c) A companion object can only contain factory functions, no other kind of member
    - d) Every class must have exactly one companion object

<details markdown="1"><summary>Check</summary>

**b)** That's the precise pair of facts this lesson covers. (a) is false: Kotlin has no `static` keyword at all; companion objects and top-level declarations fill that role instead. (c) is false: a companion object can contain any kind of member (properties, regular functions, constants), factory functions are just a common pattern, not the only allowed content. (d) is false: a companion object is entirely optional, and a class has at most one, not exactly one.

</details>

## Real-world reps

- [ ] Find an `object` declaration in a codebase you've written or have access to. Confirm you can explain why a singleton is the right fit for it (a shared resource, a stateless utility) rather than an ordinary class.
- [ ] Find a companion object, especially one used as a factory function. Check whether it does something a plain constructor couldn't (validation, caching, subclass selection), or whether it's just a stylistic wrapper around a constructor call.
- [ ] Tomorrow: read the primary source's section on object expressions (anonymous, one-time objects) in full, and note how they differ from a named `object` declaration, particularly around whether they create a shared singleton or a fresh instance each time.

## Going further

- [Docs: "Object declarations and expressions", Kotlin](https://kotlinlang.org/docs/object-declarations.html)
- [Docs: "Classes", Kotlin](https://kotlinlang.org/docs/classes.html)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
