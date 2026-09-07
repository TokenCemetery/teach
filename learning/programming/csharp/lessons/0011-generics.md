---
title: "11. Generics"
description: "Constraints as the vocabulary for what a type parameter must be, variance as a rule about positions, and the stage 2 capstone of choosing the right type"
type: lesson
---

# Lesson 11. Generics

**Mission link:** Stage 2 closes here, and its done-when is modelling a domain by choosing the right type rather than a class for everything. Generics are the last of the five choices, and the capstone makes you use all of them.
**Primary source:** [Docs: "Constraints on type parameters", Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/csharp/programming-guide/generics/constraints-on-type-parameters)
**Prerequisites:** [Lesson 10](0010-interfaces.md), [Lesson 9](0009-pattern-matching.md), [Lesson 8](0008-record-types.md)

## Warm-up

1. ▢ What does `public string Name { get; set; }` declare inside an interface?

<details markdown="1"><summary>Check</summary>

A property with no default implementation, which every implementing type must implement. Not an auto-implemented property, because instance auto-properties would require a hidden field and an interface cannot hold instance state.

</details>

2. ▢ A class implements a member as an explicit interface implementation. Who can call it?

<details markdown="1"><summary>Check</summary>

Only code holding a reference of that interface type. An explicit implementation is a member callable only through the specified interface, so it leaves the class's own surface entirely.

</details>

3. ▢ In a switch expression, an arm for a base type appears above an arm for a derived type. What does the compiler say?

<details markdown="1"><summary>Check</summary>

Error CS8510: the later pattern is unreachable, already handled by the earlier arm. The equivalent `if`/`else if` chain has the same bug with no diagnostic at all, which is the strongest argument for pattern matching.

</details>

## Know this

**What generics are for, stated plainly.** They let you tailor a method, class, structure or interface to the precise data type it acts on, which is why `Dictionary<TKey,TValue>` exists rather than a `Hashtable` taking anything, and the benefits are reusability and type safety ([Generics in .NET](https://learn.microsoft.com/en-us/dotnet/standard/generics/)).

**And in C# they are not erased.** The type argument survives compilation, so inside a generic method `typeof(T)` gives you the actual type, and a `List<int>` stores integers rather than boxed objects. If you are arriving from Java or Kotlin, this is the difference that removes a whole category of workaround: there is no need for a `reified` modifier, no need to pass a `Class<T>` alongside the type parameter, and `List<int>` and `List<string>` are genuinely distinct types at run time. This one is worth stating without a citation, since it is a property of the runtime rather than a documented API.

**Constraints are the vocabulary for what a type parameter must be.** The important ones, with the traps the reference calls out:

|Constraint|Meaning|
|---|---|
|`where T : struct`|A non-nullable value type, including `record struct`. Because every value type has an accessible parameterless constructor, this **implies** `new()` and cannot be combined with it|
|`where T : class`|A reference type, including interfaces, delegates and arrays. In a nullable context it must be a **non-nullable** reference type|
|`where T : class?`|A reference type, nullable or not|
|`where T : notnull`|Any non-nullable type, reference or value|
|`where T : new()`|A type with an accessible parameterless constructor|
|`where T : SomeBase`|That base class, or a derived one|
|`where T : ISomeInterface`|A type implementing that interface|

Two ordering rules follow from that table and both are enforced. At most one of `struct`, `class`, `class?`, `notnull` and `unmanaged` may appear, and it must be **first**. And `new()`, if present, must be **last** ([Constraints on type parameters](https://learn.microsoft.com/en-us/dotnet/csharp/programming-guide/generics/constraints-on-type-parameters)). A base class constraint cannot be combined with any of the kind constraints, and you cannot name both the nullable and non-nullable forms of the same interface.

**Variance is a rule about positions, not a preference.** A covariant type parameter, written `out T`, may appear **only in output positions** such as return types; a contravariant one, written `in T`, only in **input positions** such as parameters. That is what makes the conversions safe:

- `IEnumerable<out T>` is covariant, so an `IEnumerable<Dog>` is usable where an `IEnumerable<Animal>` is expected.
- `Action<in T>` is contravariant, so an `Action<Animal>` is usable where an `Action<Dog>` is expected, because anything that can handle any animal can handle a dog.

Many built-in types are already variant, `IEnumerable<out T>`, `IReadOnlyList<out T>` and `Func<out T>` among them. This is also the promise lesson 4 made: the `out` in `IEnumerable<out T>` is why a sequence of a derived type flows into a parameter typed for the base, and the position rule is the reason a type with both a getter and an `Add` cannot be variant at all.

**`static abstract` members, and why they are unusual.** An interface can declare `static abstract` and `static virtual` members for every member kind except fields, which lets it require that implementing types define operators or other static members. That is what makes generic algorithms able to specify number-like behaviour, and the .NET numeric interfaces such as `System.Numerics.INumber<TSelf>` are built from it.

The mechanism is the part to remember, because it explains the odd shapes you will see. There is **no runtime dispatch** for these members, nothing analogous to a `virtual` method on a class: the compiler must resolve the call at compile time from type information it already has. Consequently they are almost exclusively declared in **generic** interfaces, and most such interfaces constrain a type parameter to implement the interface itself:

`public interface IAdditionSubtraction<T> where T : IAdditionSubtraction<T>`

That self-constraint is not decoration. Without it, the operators would have to be declared in terms of the interface rather than the type parameter, which would force every implementer into explicit interface implementation. With it, the interface defines the operators in terms of `T` and implementers can implement them implicitly.

**Where stage 2 leaves you.** You now have five ways to declare a type, and the stage's done-when is choosing among them rather than reaching for `class` by reflex: a `struct` for a small value compared by contents, a `class` for something with identity and a lifecycle, a `record` or `record struct` for data whose equality is its contents, an `interface` for a contract others implement, and a generic type or method for behaviour that is the same whatever it operates on. The capstone below is that choice, five times.

## Practice

1. ▢ `where T : struct, new()` does not compile. Why? And in `where T : IComparable<T>, new()`, where must `new()` go?

<details markdown="1"><summary>Check</summary>

The first fails because `struct` already **implies** `new()`: every value type has an accessible parameterless constructor, declared or implicit, so the reference states the two cannot be combined. It is redundancy rejected rather than a conflict.

In the second, `new()` must come **last**, which is a documented ordering rule. The companion rule is that at most one of `struct`, `class`, `class?`, `notnull` and `unmanaged` may appear and it must come **first**. So a constraint list has a shape: the kind constraint, then base and interface constraints, then `new()`.

</details>

2. ▢ `IEnumerable<T>` is declared `IEnumerable<out T>`, but `IList<T>` is not variant at all. What decides that?

<details markdown="1"><summary>Check</summary>

The positions `T` appears in. A covariant parameter may appear only in output positions, and `IEnumerable<T>` only ever produces a `T`, so `out` is available. `IList<T>` has `Add(T)` and an indexer setter, which put `T` in an input position, so it can be neither covariant nor contravariant and stays invariant.

The consequence is worth carrying: an `IEnumerable<Dog>` flows into a parameter typed `IEnumerable<Animal>` and an `IList<Dog>` does not. If it did, you could add a `Cat` through the second reference and read it back as a `Dog`. Variance is not a permission the language grants generously; it is a conclusion drawn from what the type can do.

</details>

3. ▢ Why does `INumber<TSelf>` constrain its own type parameter to implement `INumber<TSelf>`, and what happens without that constraint?

<details markdown="1"><summary>Check</summary>

Because `static abstract` members have no runtime dispatch. The compiler must resolve those calls at compile time, so it needs the type argument to tell it which type's operator to call, which is why such members appear almost exclusively in generic interfaces.

Without the self-constraint, the operators would have to be declared in terms of the interface itself rather than the type parameter, which the reference spells out: `static abstract IAdditionSubtraction<T> operator +(IAdditionSubtraction<T> left, ...)`. That signature forces every implementer to use explicit interface implementation. With the constraint, the interface declares the operators in terms of `T`, and implementing types implement them implicitly, which is the difference between an idiomatic numeric type and a curiosity.

</details>

4. ▢ Inside `T Parse<T>(string s)`, what can `typeof(T)` tell you, and what would the Java or Kotlin equivalent have to do instead?

<details markdown="1"><summary>Check</summary>

It gives you the actual type argument, because C# generics are not erased: the type argument is present at run time. So a generic method can branch on `typeof(T)`, construct a `T` when constrained with `new()`, and store value types without boxing.

On the JVM the type argument is erased, so the same method has to be handed the type another way, whether as a `Class<T>` parameter or, in Kotlin, by being `inline` with a `reified` type parameter. C# needs neither mechanism, which is why searching for a `reified` equivalent is a dead end rather than a gap in your knowledge.

</details>

5. ▢ Which claim about a covariant `out` type parameter is correct?

   - a) A covariant out parameter may appear in both input and output positions freely
   - b) A covariant out parameter may appear only in output positions like return types
   - c) A covariant out parameter makes the generic type usable with any unrelated argument
   - d) A covariant out parameter is a runtime cast, checked when the conversion happens

<details markdown="1"><summary>Check</summary>

**b)** Output positions only, which is the restriction that makes the conversion safe and the reason a type with an `Add` cannot be covariant. (a) removes the restriction and with it the safety, since you could then write the wrong type in through a widened reference. (c) confuses variance with unrelated conversion: it only relates type arguments that already stand in an inheritance relationship. (d) puts the check in the wrong place, since variance is verified when the type is declared and the conversion is then free at run time.

</details>

6. ▢ **Stage capstone.** For each requirement, choose the type declaration and defend it in one sentence from what stage 2 taught.

   - a) A monetary amount with a currency, compared by its contents, passed around constantly
   - b) A customer with a database identity, mutated over a request's lifetime
   - c) An event carrying three read-only fields, which downstream code pattern matches on
   - d) A contract several unrelated types implement, where you will later need to add a method
   - e) A cache that works for any key and value type, requiring keys that are never null

<details markdown="1"><summary>Check</summary>

**(a)** `readonly record struct Money(decimal Amount, string Currency);` A value type, so no allocation per amount and copy semantics; a record for the compiler-synthesized value equality, which for a struct also avoids the reflective `ValueType.Equals`; `readonly` because a positional `record struct` otherwise gets read-write properties. Note `decimal` from lesson 3, not `double`.

**(b)** A plain `class`. It has identity, so two customers with equal fields are not the same customer, and reference equality is what a change tracker needs. Lesson 8's note applies directly: records are not appropriate as Entity Framework Core entity types for exactly this reason.

**(c)** A positional `record`. Value equality suits an event, and the positional form generates the `Deconstruct` that makes positional patterns work downstream, which is the connection lesson 9 drew.

**(d)** An `interface`, with the method added later as a **default implementation** so existing implementers keep compiling, and the logic in a `protected static` helper so an implementer can extend rather than replace it.

**(e)** A generic type, `class Cache<TKey, TValue> where TKey : notnull`. `notnull` rather than `class` because the requirement is non-nullability, not reference-ness, and it permits value-type keys. This is also what the framework itself does: `Dictionary<TKey, TValue>` constrains `TKey` to `notnull`.

The thread through all five: the declaration is an argument about identity and mutability, made once, that every later reader inherits. Reaching for `class` every time is not a neutral default, it is a claim that the thing has identity and can change, made silently.

</details>

## Real-world reps

- [ ] Find a generic method in C# you have access to with no constraints. Decide what it actually requires of `T`, and whether a constraint would have documented it.
- [ ] Find a generic interface in a codebase you can reach and check whether its type parameter is variant. If not, find the member that prevents it.
- [ ] Tomorrow: take five types from your own domain and redo the capstone on them. For each, write the one sentence you would use to defend the choice in review.

## Going further

- [Docs: "Constraints on type parameters", Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/csharp/programming-guide/generics/constraints-on-type-parameters)
- [Docs: "Generic types and methods", Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/types/generics)
- [Docs: "Generics in .NET", Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/standard/generics/)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
