---
title: "6. Exceptions"
description: "Exception filters and the stack trace that catch-and-rethrow destroys, using for deterministic cleanup, and the stage 1 capstone"
type: lesson
---

# Lesson 6. Exceptions

**Mission link:** This closes stage 1, whose done-when is predicting copy-versus-reference behaviour without running the code, so the last item is a prediction exercise across everything so far. The new material is the one exception feature C# has and Java does not.
**Primary source:** [Docs: "Exception-handling statements (C# reference)", Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/statements/exception-handling-statements)
**Prerequisites:** [Lesson 5](0005-control-flow.md), [Lesson 4](0004-collections.md), [Lesson 1](0001-structs-and-classes.md)

## Warm-up

1. ▢ Why does `foreach` work on a `Span<int>`, which implements no interfaces, and why can you not call LINQ methods on it?

<details markdown="1"><summary>Check</summary>

`foreach` needs only a shape: a public parameterless `GetEnumerator` returning a type with `Current` and a `bool MoveNext`. LINQ needs the interface, because its operators are defined over `IEnumerable<T>`, which `Span<T>` does not implement. Iteration is duck-typed; querying is interface-bound.

</details>

2. ▢ What must every switch section end with, and what happens if it does not?

<details markdown="1"><summary>Check</summary>

`break`, `goto` or `return`. Falling through from one section to the next is a compiler error, so the code does not build. Multiple labels on a single section are how C# expresses cases that share a body.

</details>

3. ▢ `dict.Add(key, value)` and `dict[key] = value` both add the pair when the key is absent. What is the difference?

<details markdown="1"><summary>Check</summary>

`Add` throws an `ArgumentException` if the key is already present; the indexer silently replaces the existing value. Choosing between them is a statement about whether a duplicate key means a bug.

</details>

## Know this

**The shapes first, briefly.** `try` with `catch`, with `finally`, or with both, and `throw` to raise. All of that reads as a Java background expects. Two additions worth knowing immediately.

`throw` also works as an **expression**, which Java has no equivalent for, so it can appear in a conditional operator, on the right of `??`, or as the whole body of an expression-bodied member ([Exception-handling statements](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/statements/exception-handling-statements)). That turns a three-line guard into a clause of the assignment it guards: `set => name = value ?? throw new ArgumentNullException(...)` is the documentation's own example.

And C# has **no checked exceptions**. Nothing in a signature declares what a method can throw, and the compiler never requires you to handle anything. That has one consequence to internalise now: the Java move of reading a `throws` clause to find out what can go wrong is not available, so what a method can throw lives in its documentation, its tests, and your reading of it.

**Exception filters are the feature to actually learn.** A `catch` clause can carry a Boolean expression after `when`, which examines the exception and decides whether that clause handles it at all:

`catch (Exception e) when (e is ArgumentException || e is DivideByZeroException)`

Three documented consequences follow, and the third surprises people:

- One clause can handle several exception types, as above.
- You may write several `catch` clauses for the **same** type as long as they differ by filter. One may have no filter, and if so it must be the last of the clauses for that type.
- When a clause has a filter, it may name a type the same as or less derived than a later clause's type, so **`catch (Exception e)` no longer has to be last**.

**The reason filters matter is the stack, and this is the sharpest Java contrast in stage 1.** A `when` filter **does not unwind the stack**. So if a filter evaluates to false, the original stack trace is not changed. Whereas a `catch` clause that catches an exception, discovers it cannot process it, and rethrows, has already unwound: the original stack information is lost.

Java gives you no filters, so its idiom for "handle only some of these" is catch-everything-then-inspect-then-rethrow, and that idiom is exactly the one that destroys the trace. Carried into C# it produces a stack trace pointing at your own rethrow instead of at the code that failed, which is worse than useless while debugging. The C# form asks the question **before** committing: filter in the `when`, and never catch what you are not going to handle.

**`using` for cleanup that happens whatever else does.** The `using` statement ensures an `IDisposable` instance is disposed when control leaves the block, **including when an exception is thrown inside it** ([using statement](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/statements/using)). This is Java's try-with-resources with a different interface name, and there is also a `using` **declaration** form that ties disposal to the end of the enclosing scope rather than to a nested block. `await using` does the same for an `IAsyncDisposable`, which stage 4 will need.

**Three exceptions worth recognising on sight**, from the .NET overview's table:

|Exception|What its presence tells you|
|---|---|
|`NullReferenceException`|Thrown by the runtime **only** when a null object is referenced, so it is a bug rather than a condition to handle|
|`IndexOutOfRangeException`|Thrown by the runtime **only** when an array is indexed improperly, likewise a bug|
|`InvalidOperationException`|Thrown by a method called in an invalid state, the documented example being `MoveNext()` after removing an item from the collection being enumerated|

That third row connects to lessons 4 and 5: mutating a collection while a `foreach` is walking it is the classic way to produce one, and lesson 2 met the same exception from `Nullable<T>.Value`.

## Practice

1. ▢ Translate this Java-shaped handler into idiomatic C#, and say what the original costs: `catch (Exception e) { if (!IsTransient(e)) throw; Retry(); }`.

<details markdown="1"><summary>Hint</summary>

Ask at what moment the decision "is this mine to handle" gets made, and what has already happened to the stack by then.

</details>

<details markdown="1"><summary>Check</summary>

`catch (Exception e) when (IsTransient(e)) { Retry(); }`.

What the original costs is the stack trace. Entering the `catch` unwinds the stack, so by the time `IsTransient` returns false the original stack information is already gone, and the bare `throw` propagates an exception whose trace no longer points cleanly at the code that failed. The filter version never enters the clause for a non-transient exception, and because a `when` filter does not unwind, the trace reaches the next handler unchanged. The rule to carry: decide in the filter, not in the body, and do not catch what you will not handle.

</details>

2. ▢ Why does a `try` statement compile when a filtered `catch (Exception e) when (IsRetryable(e))` appears **above** a `catch (IOException e)` clause, given that `IOException` derives from `Exception`?

<details markdown="1"><summary>Check</summary>

Because the ordering rule that forces more-derived clauses first applies to unfiltered clauses. A clause with a filter may name a type the same as or less derived than a later clause's type, precisely because the filter means it might decline the exception and let matching continue. The restriction that remains: among clauses for the same type, one without a filter must come last, since it can never decline. So the shape "catch anything retryable, otherwise fall through to the specific handlers" is expressible, which it is not in a filterless language.

</details>

3. ▢ Code inside a `using (var reader = File.OpenText(path))` block throws. Is the reader disposed, and what is the Java construct this replaces?

<details markdown="1"><summary>Check</summary>

Yes. The `using` statement disposes the acquired `IDisposable` when control leaves the block, and the documentation is explicit that this includes leaving because an exception was thrown. It replaces Java's try-with-resources, with `IDisposable` in place of `AutoCloseable`. Two things Java does not have alongside it: a `using` **declaration**, which drops the braces and disposes at the end of the enclosing scope, and `await using` for an `IAsyncDisposable`, which stage 4 will use for resources whose cleanup itself has to be awaited.

</details>

4. ▢ Rewrite this using a `throw` expression: `public string Name { set { if (value == null) { throw new ArgumentNullException(nameof(value)); } name = value; } }`.

<details markdown="1"><summary>Check</summary>

`set => name = value ?? throw new ArgumentNullException(nameof(value));`

The guard becomes part of the assignment rather than three lines in front of it, because `throw` is usable as an expression, including on the right-hand side of `??`. It reads as one claim: the field takes the value, or the caller made a mistake. The same trick works in a conditional operator and as the whole body of an expression-bodied member. Note what has not changed: the exception is the same and the failure is the same, so this is a readability decision, not a behavioural one.

</details>

5. ▢ Which claim about an exception filter is correct?

   - a) An exception filter runs after the stack unwinds, losing the original trace
   - b) An exception filter runs before the stack unwinds, so the trace survives
   - c) An exception filter is sugar for an if inside the catch block
   - d) An exception filter may only appear on the last catch clause present

<details markdown="1"><summary>Check</summary>

**b)** A `when` filter does not unwind the stack, so a filter returning false leaves the original stack trace unchanged. (a) inverts the mechanism and describes what a `catch` body does. (c) is the answer worth understanding, because it is the near-miss: an `if` inside the `catch` produces the same control flow and a different stack, which is the whole reason the feature exists. (d) reverses the real rule, which is that a filtered clause is freed from the ordering requirement, while an unfiltered clause for a type must come last.

</details>

6. ▢ **Stage capstone.** Predict all five without running anything, then state the single question that decides the first three.

   - a) `var p2 = p1;` then `p2.X = 5;`, where `Point` is a struct. Has `p1.X` changed?
   - b) The same two lines, where `Point` is a class. Has `p1.X` changed?
   - c) `int? a = 10;` What is `a >= null`, and what is `a < null`?
   - d) `var n = counts["absent"];` on a `Dictionary<string, int>`. What happens?
   - e) `foreach (IFormattable f in objects)` over an `object[]` whose third element is a plain `object`. What happens, and when?

<details markdown="1"><summary>Check</summary>

**(a)** No. The assignment copied the value, so `p2` is independent and `p1.X` is untouched. **(b)** Yes. The assignment copied a reference, so both names denote one object and the mutation is visible through either. **(c)** Both `false`, because a null operand makes every relational comparison false in both directions. **(d)** A `KeyNotFoundException`, at that line, where Java's map would have returned null and failed later. **(e)** An `InvalidCastException`, on the third iteration, because the explicit iteration-variable type is a per-element cast that the compiler permitted and the runtime rejected.

The question behind the first three is **what does this name actually hold**: a value, a reference, or a value plus a flag. A struct variable holds the value, so copying copies it. A class variable holds a reference, so copying aliases. A `Nullable<T>` holds a value and a boolean saying whether it counts, which is why comparing it to null yields false rather than throwing.

The last two are the same skill pointed at an API instead of at a variable: ask what this operation does in the case where the thing is not there. Answering that per API rather than per language is what stage 1 was for, and it is the habit the rest of the arc keeps leaning on.

</details>

## Real-world reps

- [ ] Search C# you have access to for `catch` clauses containing an `if` that rethrows. Each one is a filter waiting to be written, and each is currently discarding a stack trace.
- [ ] Find a `catch (Exception` in that codebase. Decide, for each, whether the clause actually handles the exception or merely logs and rethrows it.
- [ ] Tomorrow: take one method you would have annotated with `throws` in Java and write down what it can actually throw. Then decide where that list should live, given that the compiler will never ask for it.

## Going further

- [Docs: "Exception-handling statements (C# reference)", Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/statements/exception-handling-statements)
- [Docs: "Handling and throwing exceptions in .NET", Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/standard/exceptions/)
- [Docs: "using statement (C# reference)", Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/statements/using)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
