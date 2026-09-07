---
title: "2. Nullable Value Types"
description: "Why int? is still a value type, the comparison rule that makes both directions false, and what boxing does to the wrapper"
type: lesson
---

# Lesson 2. Nullable Value Types

**Mission link:** The mission names the type system and what the CLR does with what you wrote. Nullable value types are where those two meet, and where a Java instinct about nullable numbers is wrong twice over.
**Primary source:** [Docs: "Nullable value types (C# reference)", Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/builtin-types/nullable-value-types)
**Prerequisites:** [Lesson 1](0001-structs-and-classes.md)

## Warm-up

1. ▢ What does assigning one struct-typed variable to another actually do, compared to assigning one class-typed variable to another?

<details markdown="1"><summary>Check</summary>

The struct assignment copies the value, so the two variables are independent from then on. The class assignment copies the reference, so both variables name the same object and a mutation through one is visible through the other. That difference is about to decide what `null` even means for a number.

</details>

2. ▢ Why can mutating a struct returned from a property fail to change the thing you meant to change?

<details markdown="1"><summary>Check</summary>

Because the property returns a copy. The mutation lands on that temporary copy, which is then discarded, while the struct stored in the original object is untouched. It is the mirror image of the class-aliasing surprise: there you got sharing you did not ask for, here you got independence you did not want.

</details>

## Know this

**`int?` is not a boxed integer. It is still a value type.** `T?` is shorthand for `System.Nullable<T>`, a nullable value type, and the whole point for someone arriving from Java is that no reference appears anywhere. A value type is implicitly convertible to its nullable form, so `int? m = m2;` needs no ceremony, and the **default value of a nullable value type represents `null`**: an instance whose `HasValue` property returns `false` ([Nullable value types](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/builtin-types/nullable-value-types)).

So "null" here is a flag travelling alongside a value, not the absence of an object. Java's nullable number is an `Integer`, a reference on the heap that may point at nothing. C#'s is a value that carries a boolean saying whether it counts. Everything surprising below follows from that one difference.

**Four ways to get the value out, and what each does when there is none.**

|Written|When there is a value|When there is not|
|---|---|---|
|`if (a is int v)`|Binds `v` to the value|Takes the else branch|
|`a.Value`|Returns it|Throws `InvalidOperationException`|
|`a ?? -1`|Returns it|Returns `-1`|
|`(int)a`|Returns it|Throws `InvalidOperationException` at runtime|

The `is` form with a type pattern is the one the documentation leads with, and `HasValue` with `Value` is always available as the explicit pair. Note the asymmetry in the last two rows: `int m = n;` does not compile at all, while `int m = (int)n;` compiles and throws. The cast is the version that moves the problem from build time to run time, which is worth recognising as a decision rather than a formality. `GetValueOrDefault()` gives you the underlying type's default, and `GetValueOrDefault(T)` a value you choose.

**Operators are lifted, which means they propagate null.** A `T?` supports the predefined unary and binary operators that `T` supports, and those lifted operators return `null` if either operand is `null`; otherwise they use the contained values. So with `int? a = 10; int? b = null;`, `a++` gives 11, `a * c` multiplies, and `a + b` is `null`.

One exception to know: for `bool?`, the predefined `&` and `|` operators do **not** follow that rule, and can produce a non-null result even when an operand is null.

**The comparison rule, which is the part that bites.** For `<`, `>`, `<=` and `>=`, if one or both operands are `null` the result is **`false`**. Both directions. The documentation states the consequence outright: do not assume that because a particular comparison returned `false`, the opposite comparison returns `true`. Its own example is that 10 is neither greater than or equal to `null`, nor less than it.

Set that against the Java habit. There, `Integer x = null; if (x > 5)` throws a `NullPointerException`: loud, immediate, and impossible to ignore. In C# the same shape returns `false` and execution continues into the branch you did not intend. A negation written as `if (!(a >= b))` is where this actually shows up, because a reader parses it as "a is less than b" and the compiler evaluates it as "a is not greater than or equal to b", which is a different claim as soon as either side can be null.

**Boxing erases the wrapper.** Box a `T?` and one of two things happens. If `HasValue` is `false`, the boxing operation returns a **null reference**. If it is `true`, the operation boxes the value of the underlying type `T`, **not** the `Nullable<T>` instance. Unboxing a boxed `T` back to `T?` works fine.

That has a practical consequence the docs call out: calling `GetType()` on an instance of a nullable value type boxes it first, so what you get back is the underlying type, and the nullability is simply not there to see. To ask whether a type is a nullable value type, ask the type rather than the instance: `Nullable.GetUnderlyingType(typeof(int?)) != null`.

**One boundary to fix now, because the same character means two different things in C#.** This lesson is about nullable **value** types, a runtime construct: `Nullable<T>`, `HasValue`, boxing. Nullable **reference** types, where `string?` differs from `string`, are a separate feature built on compiler flow analysis rather than on a wrapper, and they arrive in lesson 15. Same `?`, different mechanism, and conflating them is the most common confusion in this corner of the language.

## Practice

1. ▢ `int? a = 10;`. Predict the value of `a >= null` and of `a < null`, then say what is wrong with writing a negation as `if (!(a >= b))`.

<details markdown="1"><summary>Hint</summary>

Work out each comparison on its own before you try to relate them to each other.

</details>

<details markdown="1"><summary>Check</summary>

Both are `false`. For `<`, `>`, `<=` and `>=`, a null operand makes the result `false` regardless of direction, so 10 is neither greater than or equal to null nor less than it. That is why the negation is a trap: a reader of `!(a >= b)` understands it as "a is less than b", but when `b` is null the inner comparison is `false`, so the negation is `true` and the branch runs, even though `a < b` is also `false`. The two are not opposites once null is in play. Write the null case explicitly, with a pattern or a `HasValue` check, rather than relying on a negation to cover it.

</details>

2. ▢ `int? c = null;`. Compare what happens for `int d = (int)c;`, for `int d = c ?? -1;`, and for `int d = c;`.

<details markdown="1"><summary>Check</summary>

`(int)c` compiles and throws an `InvalidOperationException` at run time, because there is no value to convert. `c ?? -1` gives `-1`, which is the documented way to supply a stand-in for null. `int d = c;` does not compile at all, because a nullable value type is not implicitly convertible to its underlying type, only the other way round. Worth noticing which of the three the compiler is willing to help with: the safe conversion and the impossible one are both handled at build time, and the cast is the one that defers the problem to production.

</details>

3. ▢ `int? n = 41; object o = n; Console.WriteLine(o.GetType());`. Predict what is printed, and say how you would actually test whether a type is a nullable value type.

<details markdown="1"><summary>Check</summary>

It prints the underlying type, `System.Int32`, not `System.Nullable`. Assigning to `object` boxes the value, and boxing a nullable value type that has a value boxes the underlying `T` rather than the wrapper, so by the time `GetType()` runs there is nothing nullable left to report. Had `n` been null, the boxing would have produced a null reference and `GetType()` would have thrown instead. To ask the question properly, ask the type and not the instance: `Nullable.GetUnderlyingType(typeof(int?)) != null` returns true, and the same call on `typeof(int)` returns null.

</details>

4. ▢ With `int? a = 10; int? b = null;`, predict `a + b`. Then say why `bool?` needs a footnote in this lesson.

<details markdown="1"><summary>Check</summary>

`a + b` is `null`. The operators a `T?` inherits from `T` are lifted, and a lifted operator returns null when either operand is null rather than throwing or treating null as zero. `bool?` is the exception: its predefined `&` and `|` do not follow that rule and can return a non-null result with a null operand, which makes sense once you consider that `false & null` is false whatever the null turns out to be. Everywhere else, null in means null out.

</details>

5. ▢ Which claim about a nullable value type is correct?

    - a) A nullable value type is a reference type, exactly like Java's Integer wrapper
    - b) A nullable value type is a value type whose null is a flag
    - c) A nullable value type cannot be boxed, since null has no object representation
    - d) A nullable value type throws when compared with null, as Java's wrapper does

<details markdown="1"><summary>Check</summary>

**b)** `T?` is `Nullable<T>`, a value type, and its default value represents null as an instance whose `HasValue` is false. No reference is involved. (a) is the Java instinct this lesson exists to correct, and it predicts the wrong behaviour for boxing and for comparison. (c) is false: boxing is well defined, and it yields a null reference when there is no value and a boxed underlying value when there is. (d) is the most dangerous wrong answer, because the Java version really does throw, and the C# version quietly returns `false` in both directions.

</details>

## Real-world reps

- [ ] Find a nullable value type in C# you have access to, or in any sample project. Follow one of its values to the point where the null case is handled, and note which of this lesson's four extraction forms was used.
- [ ] Search for a comparison operator applied to a nullable value type. Decide whether the null case reaches that line, and what the code does if it does.
- [ ] Tomorrow: write down what `Integer` does in Java for the same three operations (comparison with null, arithmetic with null, and asking for its type after assignment to `Object`), and put the two lists side by side. The differences are the habits to unlearn.

## Going further

- [Docs: "Nullable value types (C# reference)", Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/builtin-types/nullable-value-types)
- [Docs: "Types (C# reference)", Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/types/)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
