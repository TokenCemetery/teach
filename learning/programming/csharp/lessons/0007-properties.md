---
title: "7. Properties"
description: "Accessors as a language feature, the three orthogonal promises of required, init and a non-nullable type, and computed properties with no backing field"
type: lesson
---

# Lesson 7. Properties

**Mission link:** Stage 2 opens on modelling, and a property is the unit a C# model is built from. Java has no properties at all, so this is the first stage-2 lesson where the Java habit is not wrong so much as absent.
**Primary source:** [Docs: "Properties (C# Programming Guide)", Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/csharp/properties)
**Prerequisites:** [Lesson 6](0006-exceptions.md), [Lesson 1](0001-structs-and-classes.md)

## Warm-up

1. ▢ Why is `catch (Exception e) when (IsTransient(e))` better than catching and rethrowing when the exception turns out not to be transient?

<details markdown="1"><summary>Check</summary>

A `when` filter does not unwind the stack, so a filter returning false leaves the original stack trace unchanged. Entering a `catch` body unwinds, so a clause that catches and then rethrows has already destroyed the trace that pointed at the failure.

</details>

2. ▢ `var p2 = p1; p2.X = 5;`. Has `p1.X` changed, and what does the answer depend on?

<details markdown="1"><summary>Check</summary>

It depends on whether `Point` is a struct or a class. A struct variable holds the value, so the assignment copied it and `p1` is untouched. A class variable holds a reference, so the assignment aliased it and `p1.X` is now 5.

</details>

3. ▢ What does `foreach` actually require of a type?

<details markdown="1"><summary>Check</summary>

A shape, not an interface: a public parameterless `GetEnumerator`, which may be an extension method, whose return type has a public `Current` property and a public parameterless `MoveNext` returning `bool`. LINQ is the one that requires `IEnumerable<T>`.

</details>

## Know this

**A property is a language feature, and that is the whole difference from Java.** `public string FirstName { get; set; }` declares a property, and the compiler synthesises the backing field for you. In Java, `getFirstName` and `setFirstName` are two ordinary methods following a naming convention that tools agree to recognise. In C# a property is a single member, which means it can carry an access modifier, appear in an interface, be overridden, and be assigned in an object initializer. None of those is true of a pair of Java methods, which is why the C# version is not just shorter.

**Accessors can differ in accessibility, within one rule.** `public string? FirstName { get; private set; }` is readable everywhere and writable only inside the declaring type. The rule is that an access modifier on an individual accessor must be **more restrictive** than the property's own access, so a private property with a public accessor is not expressible ([Properties](https://learn.microsoft.com/en-us/dotnet/csharp/properties)).

**A computed property has no backing field at all.** An accessor that is a single expression can be written as an expression-bodied member: `public string Name => $"{FirstName} {LastName}";`. The documentation is explicit that there is no backing field for such a property and that it computes the value on each access. So it is a method wearing a property's clothes, and the consequence is the useful part: it cannot go stale, because there is nothing stored to go stale.

Since C# 14 the reverse is also available. The `field` keyword reaches the compiler-synthesised backing field from inside an accessor, so validation no longer requires declaring a separate field by hand:

```csharp
public string? FirstName
{
    get;
    set => field = value.Trim();
}
```

**The three promises, and why keeping them apart matters.** C# has three modifiers that all sound like "this value is guaranteed", and they guarantee different things. Confusing them is the most common modelling mistake in this corner of the language.

|Written|The promise|What it does **not** promise|
|---|---|---|
|`required`|Every expression that creates an instance must initialise this member. Available from C# 11 ([required](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/keywords/required))|That the value is not null. Setting a required property to `null` or `default` is valid|
|`init`|It can be assigned only during construction, by a constructor or an object initializer, and never afterwards ([init](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/keywords/init))|That it will be assigned at all|
|A non-nullable type|The value should not be null, checked by flow analysis (stage 3's material)|That it must be set, or that it cannot change later|

The documentation attaches an Important to the first row for exactly this reason: do not confuse `required` with non-nullable. Assigning `null` to a required, non-nullable property satisfies `required` and produces a **nullability warning**, while omitting the member entirely is error CS9035. Two different mechanisms, two different diagnostics.

Two more details worth having. `required` applies to fields and properties on `struct` and `class` types, including `record` and `record struct`, but **not** to interface members. And a constructor annotated `[SetsRequiredMembers]` tells the compiler it initialises all required members, so callers using that constructor do not have to set them in an object initializer.

**What this replaces from Java.** Java's tool for an immutable field is `final`, which forces initialisation through a constructor. `init` gets the same guarantee while permitting object-initializer syntax, so callers name what they are setting instead of matching a positional argument list. Put `required` beside it and you have compiler-checked, named, order-free initialisation with no constructor written at all:

`public required string FirstName { get; init; }`

Read that as one sentence: every caller must set it, by name, and nobody can change it afterwards.

**One boundary, since stage 2 continues into it.** Records are built out of the machinery in this lesson: a positional record parameter becomes an init-only property, with value equality added on top. That is lesson 8's subject. This lesson is the mechanics; the next one is the type that packages them.

## Practice

1. ▢ Compare `{ get; private set; }`, `{ get; init; }` and `{ get; }` on an auto-implemented property. For each, say who can assign it and when.

<details markdown="1"><summary>Check</summary>

`{ get; private set; }`: assignable from any code inside the declaring type, at any time, including long after construction. Readable everywhere.

`{ get; init; }`: assignable only during construction, from a constructor **or** from an object initializer at the call site, and never afterwards. The documentation notes that `init` is more restrictive than `private` on a set accessor, which is worth pausing on: `private set` restricts *who*, while `init` restricts *when*.

`{ get; }`: assignable only by calling a constructor, since there is no setter for an object initializer to use.

So the three answer different questions. If you want callers to name values at creation and nothing to change after, `init` is the only one of the three that does it.

</details>

2. ▢ Given `public required string FirstName { get; init; }`, is `new Person { FirstName = null }` legal? And `new Person()`?

<details markdown="1"><summary>Hint</summary>

Two separate mechanisms are watching that line. Ask what each one is actually checking.

</details>

<details markdown="1"><summary>Check</summary>

The first compiles with a **nullability warning**, not an error: it satisfies `required` because the member was initialised, and the documentation says outright that setting a required property to `null` or `default` is valid. The warning comes from the separate machinery of non-nullable reference types, because the declared type is `string` rather than `string?`.

The second is error **CS9035**: a required member was not set. That is the `required` mechanism itself, and it is an error rather than a warning.

The lesson in the pair: `required` polices *whether you said something*, and nullability polices *what you said*. A model that needs both guarantees has to ask for both, and a reviewer who reads `required` as "cannot be null" will approve a null.

</details>

3. ▢ `public string Name => $"{FirstName} {LastName}";`. Does this allocate a backing field, and what happens to `Name` after `FirstName` changes?

<details markdown="1"><summary>Check</summary>

No backing field exists for it, and the value is computed on each access, so `Name` reflects the new `FirstName` immediately. There is nothing stored that could disagree with the parts it is derived from, which is the reason to prefer a computed property over a field updated in two setters. The trade is that every read does the work, so the same choice is wrong for an expensive computation read in a loop, where a stored value with a deliberate invalidation point is the honest design.

</details>

4. ▢ Translate this Java shape into C# and name what the translation gains: a private `name` field with a public `getName()` and a public `setName(String)` that trims its argument.

<details markdown="1"><summary>Check</summary>

From C# 14, one member, in the shape the documentation uses: a property whose `get` is auto-implemented and whose `set` is an expression assigning to `field` after trimming. Before C# 14, the same thing with an explicitly declared backing field and a full `set` body.

What it gains is not brevity. It gains a **property**, which is a single member rather than two methods that happen to share a name stem: it can be assigned in an object initializer, declared in an interface, given asymmetric accessibility, and overridden as one thing. The Java pair cannot be any of those, because Java has no property concept for a compiler to act on, only a convention for tools to notice.

</details>

5. ▢ Which claim about `required` is correct?

   - a) A required property cannot be null, because required implies a non-nullable type
   - b) A required property must be set at construction, and may be set null
   - c) A required property is only checked when the type has no constructor
   - d) A required property cannot be combined with init, as both restrict writing

<details markdown="1"><summary>Check</summary>

**b)** Every construction expression must initialise it, and initialising it to `null` satisfies that requirement, with the nullability warning coming from a different mechanism. (a) is the confusion the documentation explicitly warns against. (c) inverts the role of a constructor: a constructor does not switch the check off, and `[SetsRequiredMembers]` exists precisely because a constructor needs a way to say it has done the job. (d) is false and misses the idiomatic combination, `required` with `init`, which is how you get named, mandatory, write-once initialisation.

</details>

## Real-world reps

- [ ] Find a C# type with an auto-implemented property that has a public setter. Decide whether anything outside the type actually needs to write it after construction, and what `init` would cost if not.
- [ ] Find a property whose value is stored and also updated from two places. Work out whether it could be computed instead, and what would break if it were.
- [ ] Tomorrow: take a Java class you know with three or four fields and a constructor, and write the C# equivalent using `required` and `init`. Compare what each version forces the caller to do.

## Going further

- [Docs: "Properties (C# Programming Guide)", Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/csharp/properties)
- [Docs: "The init keyword", Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/keywords/init)
- [Docs: "required modifier", Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/keywords/required)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
