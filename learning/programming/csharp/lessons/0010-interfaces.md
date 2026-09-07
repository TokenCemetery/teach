---
title: "10. Interfaces"
description: "What an interface may hold now that it can carry implementations, the auto-property that is not one, and the member you can only call through the interface"
type: lesson
---

# Lesson 10. Interfaces

**Mission link:** An interface is where a C# model states what it promises rather than what it stores, and since C# 8 it can also carry implementations, which changes both what belongs in one and how a caller reaches it.
**Primary source:** [Docs: "interface (C# Reference)", Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/keywords/interface)
**Prerequisites:** [Lesson 9](0009-pattern-matching.md), [Lesson 8](0008-record-types.md)

## Warm-up

1. ▢ A switch expression's arms are all list patterns and it compiles with no warnings. What have you not been told?

<details markdown="1"><summary>Check</summary>

That the arms cover every input. List patterns are the documented exception to the compiler's exhaustiveness warning, so an uncovered input compiles silently and throws at run time. A discard arm is the only guarantee there.

</details>

2. ▢ What does `x is { } value` do?

<details markdown="1"><summary>Check</summary>

Matches any non-null value and binds it to `value`. It is the empty property pattern, and it does in one step what `is not null` does without giving you the value.

</details>

3. ▢ A record has an init-only property of type `string[]`. Can a caller change the contents of that array?

<details markdown="1"><summary>Check</summary>

Yes. Init-only immutability is shallow: it freezes the reference, not the data behind it. A `with` expression copies the reference too, so the original and the copy then share one array.

</details>

## Know this

**An interface defines a contract, and now it can also carry implementations.** Any `class`, `record` or `struct` implementing an interface must provide implementations of its members, and since C# 8 the interface itself may supply a **default implementation** for a member, along with `static` members providing one shared implementation of common functionality ([interface](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/keywords/interface)).

The list of what an interface declaration may contain is longer than a Java background expects: methods, properties, indexers, events, constants, operators, a static constructor, nested types, and static fields, methods, properties, indexers and events. Access modifiers are explicit and any of them are allowed on interface members, with `public` the default for abstract methods.

**What it may not contain is instance state, and the rule has a trap in it.** Static fields are permitted; **instance** fields are not. Instance auto-properties are not supported either, because they would implicitly declare a hidden field. That produces the subtlest gotcha in this lesson:

`public string Name { get; set; }`

In a class or struct that declares an auto-implemented property with a compiler-generated field. In an **interface** it declares no such thing: it declares a property with **no default implementation**, which every implementing type must implement. Identical syntax, opposite meaning, and no diagnostic to tell you which one you wrote.

**Why default implementations exist: versioning.** The feature's purpose is adding a member to a published interface without breaking every existing implementer. Give the new member a default and code that already implements the interface keeps compiling, which is what makes an interface safe to extend at all.

The tutorial's own refinement is worth copying. Put the logic in a `protected static` helper on the interface and have the default member call it, so an implementing class that wants to *extend* the behaviour rather than replace it can call the same helper and add to its result. Without that, an implementer's only options are accepting the default or rewriting it from scratch.

Note what makes this workable given the no-instance-state rule: the interface may hold **private static** fields, which is how the tutorial parameterises its default implementation, with a public static method to set them. So a default implementation may use the interface's own statics plus whatever it can read through the interface's members, and nothing else.

**A default member is not automatically part of the class's own surface.** Start with the case the documentation spells out. If a class implements two interfaces declaring a member with the same signature, one class member serves both, and all three of `sample.Paint()`, `control.Paint()` and `surface.Paint()` call it. When you need the two interfaces to behave differently, you write an **explicit interface implementation**, prefixing the member name with the interface name, and the documentation states the consequence directly: such a member **is only called through the specified interface**. In its example, `sample.Paint()` is not accessible at all, and the call goes through `sample as IControl`.

The same shape governs default members. A class implementing the interface may override a default member either as a public method or as an explicit interface implementation. If it does neither, the implementation still lives on the interface rather than on the class, so calls reach it through an interface-typed reference rather than through the class. This is where the Java comparison matters most: a Java default method arrives on the implementing type as an inherited method you can just call, while in C# the useful mental model is that the class either declares the member or you talk to the interface.

**Interface inheritance, in two rules.** An interface may inherit from one or more base interfaces, and a type implementing the derived interface must implement the base interfaces' members as well as the derived one's. And when an interface **overrides** a method implemented in a base interface, it must use the explicit interface implementation syntax.

One forward pointer: an interface can also declare `static abstract` or `static virtual` members, requiring an implementing type to provide them, which is typically how an implementation is made to declare a set of overloaded operators. That belongs with generics, which is the next lesson.

## Practice

1. ▢ You write `public string Name { get; set; }` inside an interface. What have you declared, and what would the same line mean in a class?

<details markdown="1"><summary>Check</summary>

In the interface you have declared a property with **no default implementation**, which every implementing type must implement. You have not declared an auto-implemented property, because instance auto-properties are not supported in interfaces: they would implicitly declare a hidden field, and an interface cannot hold instance state.

In a class or struct the identical line declares an auto-implemented property with a compiler-generated backing field. Same characters, different meaning, decided entirely by what encloses them. Worth internalising as a reading habit rather than a rule to memorise: in an interface, a property declaration is a requirement unless it has a body.

</details>

2. ▢ `SampleClass` implements `IControl` and `ISurface`, both declaring `void Paint()`. First it declares one `public void Paint()`. Then you change it so each interface behaves differently. What changes for a caller holding a `SampleClass`?

<details markdown="1"><summary>Check</summary>

With one public method, both interfaces use it as their implementation and all three call sites, `sample.Paint()`, `control.Paint()` and `surface.Paint()`, invoke the same method.

Once you implement the members explicitly, prefixing each with its interface name, they become members that can only be called through the specified interface. `sample.Paint()` is then not accessible at all, and a caller must go through an interface-typed reference, as in `sample as IControl`. So the fix for the ambiguity has a cost: the method leaves the class's public surface entirely, which is the right trade when the two interfaces genuinely mean different things and the wrong one when they do not.

</details>

3. ▢ You maintain a published library with an `ICustomer` interface, and you need to add a `ComputeLoyaltyDiscount` member. How do you do it without breaking existing implementers, and how do you leave room for one to extend rather than replace your logic?

<details markdown="1"><summary>Hint</summary>

The second half is not about the member itself. Ask where the logic should live so that two different callers can both reach it.

</details>

<details markdown="1"><summary>Check</summary>

Add the member with a **default implementation**. Existing implementers keep compiling and inherit the behaviour, which is the reason the feature exists.

For the second half, put the logic in a `protected static` helper on the interface and have the default member call it. An implementer that wants to extend rather than replace can then override the member, call the same helper, and adjust its result, which is exactly the tutorial's new-customer-discount shape. Without the helper the implementer's only choices are accepting your default or reimplementing it, and the second one silently forks the rules the day you change them.

</details>

4. ▢ An interface cannot hold instance fields. How can a default implementation be parameterised at all?

<details markdown="1"><summary>Check</summary>

With **static** state, which is permitted. The tutorial holds the default implementation's thresholds in private static fields on the interface and exposes a public static method to set them, so an application using the general formula with different parameters does not have to implement the member itself.

The boundary that remains: a default implementation can use the interface's own static members plus whatever it reads through the interface's declared members on `this`, and nothing else, because there is no per-instance storage available to it. That is a real design constraint rather than an oversight: instance state is what a class is for, and an interface that wants some is telling you it should have been an abstract class.

</details>

5. ▢ Which claim about fields in an interface is correct?

   - a) An interface may declare instance fields as long as they stay private
   - b) An interface may declare static fields but never instance fields or auto-properties
   - c) An interface may declare no fields at all, whether static or instance
   - d) An interface may declare instance auto-properties, which the compiler backs with fields

<details markdown="1"><summary>Check</summary>

**b)** Static fields are permitted and are how a default implementation keeps parameters; instance fields are not, and instance auto-properties are excluded for the same reason, since they would create a hidden field. (a) inverts the rule and privacy is irrelevant to it. (c) is the older, pre-C# 8 model, and it is what most Java-shaped intuition still holds. (d) is the trap from practice item 1 stated as a claim: the syntax is accepted and it does not mean that.

</details>

## Real-world reps

- [ ] Find an interface in C# you have access to that declares a property. Check whether any implementing type would be surprised to learn it must implement it, and whether the interface actually wanted an abstract class.
- [ ] Find a type implementing two interfaces. Work out whether any member serves both, and whether that is intentional.
- [ ] Tomorrow: take an interface you would like to add a method to, and write both versions: the breaking one and the one with a default implementation plus a `protected static` helper. Decide what the second version commits you to maintaining.

## Going further

- [Docs: "interface (C# Reference)", Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/keywords/interface)
- [Docs: "Safely update interfaces using default interface methods", Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/csharp/advanced-topics/interface-implementation/default-interface-methods-versions)
- [Docs: "Explicit Interface Implementation", Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/csharp/programming-guide/interfaces/explicit-interface-implementation)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
