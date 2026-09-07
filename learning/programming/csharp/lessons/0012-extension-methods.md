---
title: "12. Extension Methods"
description: "Two syntaxes compiling to the same IL, the binding rule that stops an extension overriding anything, and what that costs at a call site"
type: lesson
---

# Lesson 12. Extension Methods

**Mission link:** Stage 3 is idiom, and this is the mechanism most of it is built from. It is also the feature Java has no equivalent for, so the habit it replaces is the static helper class whose calls read inside out.
**Primary source:** [Docs: "Extension members (C# Programming Guide)", Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/csharp/programming-guide/classes-and-structs/extension-methods)
**Prerequisites:** [Lesson 11](0011-generics.md), [Lesson 5](0005-control-flow.md)

## Warm-up

1. ▢ `IEnumerable<T>` is covariant and `IList<T>` is not. What decides that?

<details markdown="1"><summary>Check</summary>

The positions `T` appears in. A covariant parameter may appear only in output positions, and `IList<T>` has `Add(T)`, which is an input position, so it must stay invariant. Variance is a conclusion drawn from what the type can do, not a permission you grant.

</details>

2. ▢ Why does `where T : struct, new()` fail to compile?

<details markdown="1"><summary>Check</summary>

Because `struct` already implies `new()`: every value type has an accessible parameterless constructor, so the two cannot be combined. The related ordering rules are that at most one kind constraint may appear and it must come first, and `new()` must come last.

</details>

3. ▢ What exactly does `foreach` require of a type, and where might that member come from?

<details markdown="1"><summary>Check</summary>

A public parameterless `GetEnumerator` whose return type has a public `Current` and a public parameterless `MoveNext` returning `bool`. Lesson 5 noted that the `GetEnumerator` **may be an extension method**, which means you have already used this lesson's feature without being told its name.

</details>

## Know this

**Extension members let you add methods to an existing type without creating a derived type, recompiling, or modifying the original** ([Extension members](https://learn.microsoft.com/en-us/dotnet/csharp/programming-guide/classes-and-structs/extension-methods)). They are static methods that are **called as if they were instance methods**, and to client code there is no apparent difference between calling one and calling a method the type declares itself.

**Two syntaxes, one IL.** Before C# 14 you declare an extension method by adding the `this` modifier to the first parameter of a static method. From C# 14 you can instead write an `extension` block. Both forms must live in a **top-level, nongeneric static class**, and both **compile to the same IL**, so a consumer cannot tell which was used.

|Form|Available|Can declare|
|---|---|---|
|`this` on the first parameter|Any version|Instance extension methods|
|`extension` block|C# 14 and later|Methods, properties, indexers and operators, as **instance** extensions (extending an instance) or **static** extensions (extending the type itself)|

The block declares the extended type and names a **receiver**, and that name is in scope in every instance member inside the block, which is what lets several members share it. You can write as many blocks in one class as you like, with different receivers, and generics with constraints are allowed: `extension<T>(IEnumerable<T> source) where T : IEquatable<T>`. If a block contains only static members, the receiver needs no name at all.

That is a real widening rather than a syntax preference. The `this` form gives you methods only; a block can give a type a **property** (`numbers.Median`) or an **operator**, neither of which was previously expressible on a type you do not own.

**The binding rule is the whole lesson.** Extension members can extend a class or interface but **cannot override behaviour defined in a class**. At compile time they always have **lower priority** than the instance or static members the type declares itself. The compiler first looks for a match among the type's own members; only if it finds none does it search extension members, and it then binds to the **first** extension member it finds.

Three consequences follow, and each is a real hazard rather than a technicality:

- **An extension with the same name and signature as an existing member is never called.** Not preferred less often: never. If your extension appears to be ignored, this is why.
- **The type's author can take your call site away.** Ship an extension `Process(int)`, and the day the type gains its own `Process(int)`, every call in your code silently rebinds to theirs. Nothing breaks at compile time and the behaviour changes.
- **Extensions are resolved by discovery, not by best match**, since the compiler binds to the first one it finds. Two extensions that both apply are not weighed against each other the way overloads within a type are.

**What this replaces from Java, and what it does not.** Java has no extension methods, so the equivalent is a static helper class, and the call reads inside out: `Collections.sort(list)` puts the verb first and the subject in parentheses. C# lets the identical static method read as `list.Sort()`, subject first, which is the entire ergonomic gain and the reason a chain of them is readable at all.

What it is not is a way to change what a type does. Because an extension can never win against a declared member and can never be overridden, it is the right tool for **adding vocabulary to a type you do not own** and the wrong tool for **altering behaviour**. If you find yourself wanting the second, you want a wrapper, an interface, or a different type.

One forward pointer: the query operators in the next lesson arrive by exactly this mechanism, as extension members over `IEnumerable<T>`. That is why lesson 4's rule, that anything implementing `IEnumerable<T>` is a queryable type, shows up at the call site as methods that appear to belong to every collection you have.

## Practice

1. ▢ A static class defines `MethodA(this IMyInterface x, int i)` and `MethodA(this IMyInterface x, string s)`. Class `B` implements `IMyInterface` and declares its own `MethodA(int i)`. Predict where `b.MethodA(1)` and `b.MethodA("hello")` bind.

<details markdown="1"><summary>Check</summary>

`b.MethodA(1)` binds to `B.MethodA(int)`, the type's own member, because the compiler looks there first and finds a match. `b.MethodA("hello")` finds no matching member on `B`, so the compiler searches extension members and binds to `MethodA(this IMyInterface, string)`.

So one call site name resolves to two different declarations depending on the argument type, and the decision is made entirely by whether the type itself could satisfy the call. Extension members are the fallback, never the preference.

</details>

2. ▢ Your library ships an extension method `Process(this Widget w, int id)`, and callers use `widget.Process(42)`. A later version of the `Widget` library adds an instance method `Process(int id)` with different behaviour. What happens to your callers, and when do they find out?

<details markdown="1"><summary>Hint</summary>

Nothing about the call site changes. Ask which of the two candidates the compiler now prefers, and whether it says anything.

</details>

<details markdown="1"><summary>Check</summary>

Every `widget.Process(42)` silently rebinds to the new instance method on the next recompile, because extension members always have lower priority than members declared on the type. There is no error, no warning, and no change at the call site to notice in review. Callers find out from behaviour, which is the worst way to find out.

This is worth knowing as a design constraint on libraries: an extension method over a type you do not own is a name you are borrowing, not one you hold. Where the behaviour matters, a differently named extension, or a method on a type of your own, keeps the binding under your control.

</details>

3. ▢ What can an `extension` block declare that the `this`-parameter form cannot, and what is identical between them?

<details markdown="1"><summary>Check</summary>

A block can declare **properties, indexers and operators** as well as methods, and it can declare **static** extensions that extend the type itself rather than an instance. The `this` form supports instance extension methods only. So a block is what lets you write `numbers.Median` as a property, or an operator over a type you do not own.

What is identical is the output: both forms compile to the same IL and both must sit in a top-level, nongeneric static class, so consumers cannot tell which syntax was used and switching between them is not a breaking change. That matters for a library author choosing whether to adopt the newer syntax.

</details>

4. ▢ Java's answer to the same problem is a static helper, as in `Collections.sort(list)`. What does the C# version change, and what does it not change?

<details markdown="1"><summary>Check</summary>

It changes the reading order and nothing else that matters. The method is still static, still declared elsewhere, and still cannot see the type's private members. What moves is the subject: `list.Sort()` puts the thing first and the verb second, which is why a sequence of such calls composes into a readable chain and a sequence of static helper calls nests into an unreadable one.

What it does not change is dispatch. A static helper cannot be overridden and neither can an extension, so neither one gives you polymorphism. Anyone reaching for an extension method to alter what an existing type does has mistaken call-site convenience for behaviour, and the binding rule will eventually tell them so.

</details>

5. ▢ Which claim about extension member binding is correct?

   - a) An extension member overrides a same-signature instance member, since it is more specific
   - b) An extension member is never called when the type has a matching member
   - c) An extension member is chosen by best match across the type and extensions
   - d) An extension member requires the extended type to be partial or otherwise open

<details markdown="1"><summary>Check</summary>

**b)** The type's own members are searched first, and an extension with the same name and signature as a declared member is never called. (a) inverts the priority and is the assumption behind most surprise about extensions being ignored. (c) describes overload resolution within a type; across extensions the compiler binds to the first it finds rather than weighing candidates. (d) invents a requirement: the point of the feature is extending types you cannot modify at all.

</details>

## Real-world reps

- [ ] Find an extension method in C# you have access to. Decide whether it adds vocabulary to a type you do not own, or whether it is trying to change what that type does.
- [ ] Find a static helper class in a codebase you can reach whose methods all take the same first parameter. Work out which of them would read better as extensions, and whether any would collide with an existing member.
- [ ] Tomorrow: pick a type from a library you use and write one extension you have wanted on it. Then check the type's current members for a name collision, and decide what you would do if the library later added that method itself.

## Going further

- [Docs: "Extension members (C# Programming Guide)", Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/csharp/programming-guide/classes-and-structs/extension-methods)
- [Docs: "Extension declaration (C# Reference)", Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/keywords/extension)
- [Docs: "Collections and Data Structures", Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/standard/collections/)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
