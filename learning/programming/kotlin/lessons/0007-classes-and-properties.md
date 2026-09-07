---
title: 7. Classes and Properties
description: Properties as the replacement for Java's getter/setter boilerplate, and why the Kotlin docs themselves say to reach for a class last
type: lesson
---

# Lesson 7. Classes and Properties

**Mission link:** Stage 2 opens modelling. Before data classes, sealed classes, and enums give the mission's actual domain-modelling vocabulary, this lesson is the plain class and its properties, the foundation those later constructs build on and specialize.
**Primary source:** [Docs: "Classes", Kotlin](https://kotlinlang.org/docs/classes.html)
**Prerequisites:** [Lesson 6](0006-control-flow.md), [Platform type](../GLOSSARY.md)

## Warm-up

1. ▢ Why does an `if` used as an expression require an `else` branch, while an `if` used purely as a statement doesn't?

<details markdown="1"><summary>Check</summary>

As an expression, `if` must produce a value for every possible outcome, so an unmatched condition with no `else` would leave no value to produce. As a plain statement, an unmatched condition simply means nothing happens, which doesn't require a value at all.

</details>

2. ▢ What is `1..10` actually, as a Kotlin value?

<details markdown="1"><summary>Check</summary>

A real `IntRange` value, constructed via the `rangeTo()` function the `..` operator calls, not special loop syntax; it can be stored in a variable, checked with `in`, or iterated directly.

</details>

## Know this

### A property is a declared field plus its accessors, in one line

Java's convention for exposing a field safely is a private field plus a public getter (and setter, if mutable), boilerplate repeated for every field on every class. Kotlin's **property** collapses this: `class Person(val name: String, var age: Int)` declares two properties directly in the primary constructor, and both get default getters (and, for `age`, a setter) generated automatically, callable as `person.name` and `person.age = 30` with ordinary field-access syntax, no explicit `getName()`/`setAge()` calls anywhere. This is the same shape of leverage lesson 4 described for basic types being real classes: syntax that looks like direct field access is actually a method call underneath, just without Java's boilerplate to write it by hand.

### The Kotlin docs themselves say to reach for a class last

The primary source opens with an explicit recommendation: before writing a class from scratch, consider a data class if the goal is just storing data (lesson 8), or an extension function (lesson 13) if the goal is adding behavior to an existing type. This isn't a stylistic footnote; it's the mission's "reaching for a class-per-thing hierarchy" habit named directly by Kotlin's own documentation as something to actively avoid defaulting to. A plain class is the right tool specifically when a type needs real, non-generated behavior beyond storing values, not the default starting point for every new type.

### A custom getter or setter replaces the default without changing how it's called

A property's default getter/setter can be overridden to run custom logic: `val area: Int get() = width * height` computes a value on every access rather than storing it, and `var name: String = ""; set(value) { field = value.trim() }` validates or transforms on assignment. `field` inside a custom accessor refers to the **backing field**, the actual storage location; using it explicitly (rather than referring to the property name itself, which would recurse infinitely into the accessor) is what lets a custom accessor still store or read the underlying value. Crucially, the call site (`person.area`, `person.name = "Ada "`) looks identical whether the property is a simple stored value or backed by custom logic, exactly the same "syntax stays uniform, behavior underneath can differ" pattern lesson 4 described for basic types.

### Primary constructor parameters, class body properties, and plain parameters are three different things

`class Point(val x: Int, val y: Int)` declares two real properties, visible and accessible from outside the class as `point.x`. `class Point(x: Int, y: Int) { val doubled = x * 2 }` uses `x` and `y` only as constructor parameters (available inside the class body, including property initializers, but not exposed as properties themselves), while `doubled` is a real property computed once at construction. Confusing a constructor parameter for a property (expecting `point.x` to work when `x` was declared without `val`/`var`) is a common early mistake, since both look similar in the constructor's parentheses but mean structurally different things.

## Practice

1. ▢ What does `class Person(val name: String, var age: Int)` actually generate, beyond the two parameters it declares?

<details markdown="1"><summary>Check</summary>

It generates two real properties: `name` (read-only, with a default getter) and `age` (mutable, with a default getter and setter), both accessible as ordinary field-access syntax (`person.name`, `person.age = 30`) even though a getter/setter call happens underneath.

</details>

2. ▢ Why does the Kotlin documentation itself recommend considering a data class or an extension function before writing a plain class from scratch?

<details markdown="1"><summary>Hint</summary>

Consider what a plain class actually adds beyond what a data class or extension function already covers for their respective purposes.

</details>

<details markdown="1"><summary>Check</summary>

If the goal is just storing data, a data class (lesson 8) already generates the boilerplate (equality, string representation, and more) a hand-written class would need to add manually. If the goal is adding behavior to an existing type, an extension function (lesson 13) does that without creating an entirely new class. A plain class is the right tool specifically when neither of those fits, real behavior beyond storing values, not the default starting point.

</details>

3. ▢ In `var name: String = ""; set(value) { field = value.trim() }`, why does the setter assign to `field` rather than `name`?

<details markdown="1"><summary>Check</summary>

`field` refers to the property's backing field, the actual storage location; assigning to `name` directly inside its own setter would call the setter again, recursing infinitely. `field` is the mechanism that lets a custom accessor still read or write the underlying stored value without re-invoking itself.

</details>

4. ▢ `class Point(x: Int, y: Int) { val doubled = x * 2 }`. Can external code access `point.x`? Can it access `point.doubled`? Explain the difference.

<details markdown="1"><summary>Check</summary>

`point.x` does not compile: `x` is declared as a plain constructor parameter (no `val`/`var`), so it's only available inside the class body (including property initializers like `doubled`'s), not exposed as a property. `point.doubled` does work, since `doubled` is declared with `val` inside the class body, making it a real, externally-visible property.

</details>

5. ▢ Which claim correctly describes Kotlin classes and properties?

    - a) A property is purely syntactic sugar with no underlying accessor methods at all
    - b) Properties replace Java's manual getter/setter boilerplate with uniform field-access syntax backed by (possibly customized) accessors, and Kotlin's own docs recommend a data class or extension function before a plain class, where either fits better
    - c) A constructor parameter declared without `val` or `var` is still accessible as a property from outside the class
    - d) Referring to the property name itself inside its own custom setter is the correct way to update its backing field

<details markdown="1"><summary>Check</summary>

**b)** That's the precise leverage properties provide and the documented guidance on when a plain class is actually the right tool. (a) is false: properties do compile to real getter/setter calls underneath; they're not merely cosmetic. (c) is false, exactly the constructor-parameter-vs-property confusion this lesson warns about; a plain parameter without `val`/`var` isn't exposed outside the class. (d) is false: referring to the property name inside its own accessor recurses infinitely; `field` is the correct way to reach the backing storage.

</details>

## Real-world reps

- [ ] Find a Kotlin class you've written or have access to. Check whether any of its properties would be better served by a data class instead, per the documentation's own guidance, and if so, note what specifically the data class would generate for free.
- [ ] Find (or write) a property with a custom getter or setter. Confirm you can explain exactly what `field` refers to inside it, and what would happen if the accessor referred to the property name instead.
- [ ] Tomorrow: read the primary source's section on primary and secondary constructors in full, and note one case where a secondary constructor is actually necessary rather than a primary constructor with default parameter values.

## Going further

- [Docs: "Classes", Kotlin](https://kotlinlang.org/docs/classes.html)
- [Docs: "Properties", Kotlin](https://kotlinlang.org/docs/properties.html)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
