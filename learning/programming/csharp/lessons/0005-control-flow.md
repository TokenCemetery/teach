---
title: "5. Control Flow"
description: "The three places control flow does not transfer from Java: foreach's duck-typed enumerator, switch without fall-through, and goto as a legal jump"
type: lesson
---

# Lesson 5. Control Flow

**Mission link:** Most control flow transfers from Java unchanged, so this lesson spends its length on the three places it does not, which is where a habit produces either a compiler error or a runtime cast failure.
**Primary source:** [Docs: "Selection statements (C# reference)", Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/statements/selection-statements)
**Prerequisites:** [Lesson 4](0004-collections.md), [Lesson 1](0001-structs-and-classes.md)

## Warm-up

1. ▢ `var counts = new Dictionary<string, int>();` then `counts["missing"]`. What happens, and what would Java's `Map.get` have done?

<details markdown="1"><summary>Check</summary>

C# throws a `KeyNotFoundException` on that line. Java returns `null`, which fails later and elsewhere. `TryGetValue` is the C# idiom where a miss is expected.

</details>

2. ▢ What makes a type a queryable type that LINQ can query?

<details markdown="1"><summary>Check</summary>

Implementing `IEnumerable<T>`. LINQ is defined over that interface rather than over any particular collection class, which is why the same query works on a list, an array, a dictionary's values, or something that produces elements on demand.

</details>

3. ▢ For a monetary amount, why `decimal` rather than `double`?

<details markdown="1"><summary>Check</summary>

28 to 29 significant digits against `double`'s ~15 to 17, and no NaN or infinity to represent a computation that went wrong, so a bad value cannot propagate silently through later totals. It costs 16 bytes against 8, and the arithmetic still reads as arithmetic because `decimal` is a built-in value type.

</details>

## Know this

**Most of it transfers, so this is the short part.** `if` and `else`, `for`, `while`, `do`...`while`, `break`, `continue` and `return` all behave as a Java background expects. Read them once in the reference and move on. Three things do not transfer, and each fails in a different way.

**One: `foreach` is duck-typed, not interface-bound.** It works on any type implementing `IEnumerable` or `IEnumerable<T>`, but it is explicitly not limited to those. A type qualifies if it has a public parameterless `GetEnumerator` method, **which may even be an extension method**, whose return type has a public `Current` property and a public parameterless `MoveNext` returning `bool` ([Iteration statements](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/statements/iteration-statements)). The documentation's own example iterates a `Span<int>`, which implements no interfaces at all.

Java's `for-each` requires `Iterable` or an array, a fixed contract. C# asks for a shape instead, with two consequences worth holding: a type can be iterable without declaring that it is, and an extension method can make somebody else's type iterable without touching it.

Keep this straight against lesson 4, because the two rules are deliberately different. `foreach` needs only the shape; LINQ needs the interface. So a `Span<T>` can be iterated with `foreach` and is **not** a queryable type. When a type iterates fine but LINQ methods do not appear on it, that difference is the answer.

**Two: the iteration variable's type is a claim, and it is checked late.** You can let the compiler infer it with `var`, or name it explicitly. Naming it explicitly is where the trap is: for `foreach (V item in collection)` over elements of type `T`, `T` must be implicitly or explicitly convertible to `V`, and **if an explicit conversion fails at run time, `foreach` throws an `InvalidCastException`**. The docs explain why the compiler permits it: if `T` is a non-sealed class, `V` may be any interface type, even one `T` does not implement, because a runtime element could derive from `T` and implement `V`. When it does not, you find out on that iteration.

**Three: `switch` does not fall through, and it matches patterns.** Every switch section must end with `break`, `goto` or `return`, and **falling through from one section to the next generates a compiler error** ([Selection statements](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/statements/selection-statements)). This is the single most dangerous Java habit to bring to C#, and it is also the one the language protects you from most bluntly: the code does not build.

What C# gives you instead of fall-through is multiple labels on one section, which the documentation calls a deliberate design choice for concisely handling cases that share logic. So `case 1:` immediately followed by `case 2:` and one body is the supported way to say "either of these", and it says it without the accident that Java's version makes possible.

The other half is that a C# `switch` matches **patterns**, not just constants. The docs' example uses `case < 0.0:` and `case > 15.0:`, which are relational patterns, alongside a constant pattern. The full pattern vocabulary, and the `switch` **expression** that returns a value rather than directing flow, are stage 2's material. For now: the statement directs execution and its sections may be empty, while the expression produces a value and its sections may not.

**And the one Java does not have at all: `goto`.** It transfers control to a label, and the documentation shows it used to escape a nested loop. Inside a `switch` it can transfer control to another section with a constant case label. Note what this pairs with: C# has no labelled `break` or `continue`, so Java's `break outer;` has no direct translation, and `goto` is the mechanism the language actually offers for that job.

The docs attach a tip rather than a prohibition, and it is the right instinct: when you are working with nested loops, consider refactoring the separate loops into separate methods, which usually leads to simpler code with no `goto` in it. Treat `goto` as evidence that a method wants extracting.

## Practice

1. ▢ `Span<int> numbers = [3, 14, 15, 92, 6]; foreach (int n in numbers) { }` compiles, though `Span<T>` implements no interfaces. Explain why, and say whether `numbers.Where(...)` would work.

<details markdown="1"><summary>Check</summary>

`foreach` does not require an interface. It requires a shape: a public parameterless `GetEnumerator` whose return type has a public `Current` property and a public parameterless `MoveNext` returning `bool`. `Span<T>` has that, so the loop compiles.

LINQ is a different question with a different answer. Its operators are defined over `IEnumerable<T>`, which `Span<T>` does not implement, so the queryable-type rule from lesson 4 is not satisfied and those methods are not available on it. "It iterates, therefore LINQ works" is the inference to drop: iteration is duck-typed and querying is interface-bound.

</details>

2. ▢ Translate this Java shape into C#: `case 1: case 2: HandleLow(); case 3: HandleThree(); break;` where the author intended 1 and 2 to share `HandleLow`, and intended 2 to also run `HandleThree`.

<details markdown="1"><summary>Check</summary>

Half of it translates and half of it does not, which is the point.

The shared part is supported directly: `case 1:` followed by `case 2:` with one body is multiple labels on a single section, and the documentation describes that as a deliberate design choice for cases that share logic. So the first intent survives unchanged.

The second intent, falling out of the 1-or-2 section into the 3 section, is a compiler error in C#, because every section must end with `break`, `goto` or `return`. That is a feature: in Java the same code compiles whether the author meant to fall through or forgot a `break`, and the reader cannot tell which. In C# you have to say it, either by calling both methods in the one section or by writing `goto case 3;` to state the jump explicitly.

</details>

3. ▢ `object[] items = GetItems(); foreach (IFormattable f in items) { Use(f); }` compiles. Predict what happens at run time and why the compiler allowed it.

<details markdown="1"><summary>Hint</summary>

Ask what the compiler can know about the actual runtime type of each element, given the declared element type.

</details>

<details markdown="1"><summary>Check</summary>

It works for as long as every element happens to implement `IFormattable`, and throws an `InvalidCastException` on the first element that does not. The compiler allows it because the element type `object` is a non-sealed class, so a runtime element could be some type deriving from it that does implement the interface, and the conversion is therefore possible rather than provably wrong. The explicit iteration-variable type is a per-element cast you wrote without cast syntax. If the intent was "only the formattable ones", the honest version filters rather than casting, which is what `OfType` exists for.

</details>

4. ▢ A nested loop needs to abandon both levels as soon as a match is found. Java would use `break outer;`. Name the C# options and say which the documentation recommends.

<details markdown="1"><summary>Check</summary>

C# has no labelled `break`, so the two options are a `goto` to a label after the loops, which the docs demonstrate for exactly this case, or extracting the search into its own method and using `return`. The documentation's tip recommends the second: with nested loops, consider refactoring the separate loops into separate methods, which tends to produce simpler code without a `goto`. The useful reading is that a nested loop wanting to break out of both levels is usually a method that has not been named yet, and `return` is the labelled break you were looking for.

</details>

5. ▢ Which claim about a C# switch section is correct?

    - a) A switch section may fall through to the next one, just like Java
    - b) A switch section must end with break, goto or return, or compilation fails
    - c) A switch section may share a body with another only by duplicating it
    - d) A switch section needs no terminator, since C# inserts an implicit break

<details markdown="1"><summary>Check</summary>

**b)** Falling through from one section to the next is a compiler error, so each section states its own exit. (a) is the habit that makes this lesson necessary, and importing it produces code that does not build, which is the good outcome. (c) misses multiple labels: `case 1:` and `case 2:` above one body is a single section with two labels, not duplication and not fall-through. (d) invents a rule that would make the missing-`break` bug silent again, which is precisely what the real rule prevents.

</details>

## Real-world reps

- [ ] Find a `switch` statement in C# you have access to. Check whether any section shares a body through multiple labels, and whether a reader could mistake that for fall-through.
- [ ] Find a `foreach` whose iteration variable has an explicit type rather than `var`. Decide whether that type is guaranteed by the collection's element type or is a cast waiting to fail.
- [ ] Tomorrow: write a small nested loop that needs to exit both levels, first with `goto` and then by extracting a method. Compare the two and decide which you would want to find in a review.

## Going further

- [Docs: "Selection statements (C# reference)", Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/statements/selection-statements)
- [Docs: "Iteration statements (C# reference)", Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/statements/iteration-statements)
- [Docs: "Jump statements (C# reference)", Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/statements/jump-statements)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
