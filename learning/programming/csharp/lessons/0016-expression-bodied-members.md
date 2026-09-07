---
title: "16. Expression-Bodied Members"
description: "The second job of the arrow token, the statement-expression rule for void members, and the stage 3 capstone of rewriting translated Java"
type: lesson
---

# Lesson 16. Expression-Bodied Members

**Mission link:** Stage 3 closes here, and its done-when is writing C# a reviewer would not describe as translated Java. The new material is small; the capstone is the stage.
**Primary source:** [Docs: "The lambda operator", Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/operators/lambda-operator)
**Prerequisites:** [Lesson 15](0015-nullable-reference-types.md), [Lesson 13](0013-linq.md), [Lesson 12](0012-extension-methods.md)

## Warm-up

1. ▢ What is the runtime difference between `string` and `string?`?

<details markdown="1"><summary>Check</summary>

None. Both are `System.String`. A nullable reference type is an annotation on an existing reference type, not a new type, and the compiler adds no runtime checking, so the whole guarantee is compile-time warnings.

</details>

2. ▢ Three handlers are subscribed to an event and the second throws. What happens to the third?

<details markdown="1"><summary>Check</summary>

It never runs. An uncaught exception passes to the caller of the delegate and no subsequent methods in the invocation list are invoked, while the first handler's effects already stand.

</details>

3. ▢ Is a LINQ query written in query syntax slower than the same query in method syntax?

<details markdown="1"><summary>Check</summary>

No. The compiler converts query expressions into standard query operator calls at compile time, so the two forms are semantically identical with no performance difference.

</details>

## Know this

**The arrow token has two jobs, and telling them apart is a reading skill.** `=>` is supported as the **lambda operator**, separating a lambda's parameters from its body, and as the separator between a **member name and that member's implementation** in an expression body definition ([The lambda operator](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/operators/lambda-operator)). One token, two grammatical roles, which is a large part of why modern C# looks the way it does.

**The syntax is `member => expression;`, with two rules depending on what the member returns.**

|The member|What the body must be|
|---|---|
|Returns a value|An expression whose result is **implicitly convertible** to the member's return type|
|Is `void`, a constructor, a finalizer, or a `set`, `init`, `add` or `remove` accessor|A **statement expression**: an assignment, a method invocation, an object creation, an increment or decrement, or an `await` expression. Its result, if any, is **discarded**|

That second row is more restrictive than "any expression", and the restriction is the useful part: a `void` member cannot be given a body that merely computes something, because computing and throwing the answer away is not a statement. Note also that `await` counts, which is what makes an expression-bodied asynchronous member possible; stage 4 will use it.

`public override string ToString() => $"{fname} {lname}".Trim();` is the documentation's own example, and it is exactly the block-bodied version with `return` and braces removed. Lesson 7 already used this form for a computed property, so the shape is familiar; what is new is how far it reaches. Methods, local functions, operators, properties, constructors, finalizers, and the accessors named above can all be written this way, and the reference carries the complete list.

**Now the part that makes this a capstone rather than a syntax note: when not to.** An expression body is right when the member **is** the expression, and wrong when it hides work. The test I would apply in review is whether a reader would have to reformat the member to add a second statement to it. If the answer is obviously yes and obviously soon, the compact form has been borrowed against a change you already expect.

That is a judgement rather than a rule. What it rests on is that a diff which reformats a member and changes its behaviour in the same commit is harder to review than one that only changes behaviour. What would change it: a codebase whose members are overwhelmingly one-liners, where the consistency of always using the compact form is worth more than the occasional noisy diff. What does not change it is a nested conditional squeezed into one expression to avoid braces, which trades a reviewer's attention for a line count nobody was counting.

**Where stage 3 leaves you.** Five idioms, each replacing a specific Java habit:

|Lesson|The C# idiom|The habit it replaces|
|---|---|---|
|12|Extension members|A static helper class whose calls read inside out|
|13|LINQ over `IEnumerable<T>`|A loop that builds a list, or a stream pipeline reimplemented by hand|
|14|Delegates, `Func` and `Action`, and `event`|A single-method interface, and `addXListener` by convention|
|15|Nullable annotations|Defensive null checks standing in for a type the reader could have read|
|16|Expression-bodied members|Braces and `return` around a single expression|

The stage's done-when is that a reviewer would not call your C# translated Java. The capstone is that review, done to a piece of code that deserves it.

## Practice

1. ▢ Which of these compile as expression-bodied members, and why: `void Log() => Console.WriteLine("hi");`, `void Log() => 42;`, `void Log() => count > 0;`?

<details markdown="1"><summary>Check</summary>

Only the first. A `void` member's expression body must be a **statement expression**, and the permitted forms are an assignment, a method invocation, an object creation, an increment or decrement, and an `await`. `Console.WriteLine(...)` is a method invocation, so it qualifies.

`42` is a literal and `count > 0` is a comparison, and neither is a statement expression: they compute a value with nowhere for it to go. That is the same rule that stops you writing `42;` as a statement in a block body, so the restriction is not special to expression bodies, it is the ordinary statement rule showing through.

</details>

2. ▢ `long Total() => someInt;` compiles and `int Total() => someLong;` does not. What is the rule?

<details markdown="1"><summary>Check</summary>

For a member that returns a value, the expression's result must be **implicitly** convertible to the member's return type. `int` to `long` is an implicit conversion, so the first compiles. `long` to `int` is not, since it can lose information, so the second needs an explicit cast and the compiler will not add one for you.

Worth noting what this is not: it is not a rule about expression bodies. It is the ordinary return-type conversion rule, and the same expression in a block body with `return` in front of it behaves identically. Expression bodies remove syntax, not semantics.

</details>

3. ▢ In `Func<int, int> doubler = x => x * 2;` and `int Double(int x) => x * 2;`, name the job each arrow is doing.

<details markdown="1"><summary>Check</summary>

The first is the **lambda operator**, separating the lambda's parameter list from its body, and the whole thing on the right is a value assigned to a variable of a delegate type. The second is an **expression body definition**, separating a member's name and signature from its implementation, and there is no lambda anywhere in it.

Reading them apart matters because they compile to different things. The first creates a delegate instance, which lesson 13 called the delegate half of the delegate-or-expression-tree distinction. The second is just a method, with the same IL as the block-bodied version. Same token, and no relationship beyond the spelling.

</details>

4. ▢ A pull request converts a six-line method with two `if` statements into a single expression body using nested conditional operators. Review it.

<details markdown="1"><summary>Hint</summary>

Ask what the next change to this member will look like as a diff.

</details>

<details markdown="1"><summary>Check</summary>

Reject it, and say why in terms of the next change rather than of taste. The member is not an expression, it is a decision with two branches that has been folded into one, so the compact form is now carrying logic rather than removing ceremony. The next person who adds a third case has to reformat the whole member back into a block, and the diff will mix that reformatting with the behavioural change, which makes the review harder than either change alone.

The version of this comment worth posting names the mechanism: nested conditionals in one expression are read by unwinding them, while `if` statements are read in order, so the compact form has moved cost from the writer to every future reader.

Where the same reviewer should say yes: the member that really is one expression, such as a computed property or a `ToString` that formats its fields. There the braces and the `return` were the only content being removed.

</details>

5. ▢ Which claim about a `void` expression-bodied member is correct?

    - a) A void expression-bodied member may have any expression, including a bare literal
    - b) A void expression-bodied member needs a statement expression, whose result is discarded
    - c) A void expression-bodied member is not allowed, since there is nothing returned
    - d) A void expression-bodied member must end with a return statement to compile

<details markdown="1"><summary>Check</summary>

**b)** The body must be a statement expression, an assignment, invocation, object creation, increment or decrement, or `await`, and any result it produces is discarded. (a) is the intuition the rule exists to correct. (c) is false and would rule out the most common use of the form, a one-line `void` method. (d) contradicts the syntax entirely, since removing `return` is the point.

</details>

6. ▢ **Stage capstone.** Review this class and rewrite it, naming which stage 3 lesson each change comes from.

    - a) A `static class OrderHelpers` with `public static decimal TotalOf(Order o)`, called as `OrderHelpers.TotalOf(order)`
    - b) A method that declares `var results = new List<string>();`, loops over orders with a `foreach`, tests each with an `if`, and adds a projection to the list
    - c) An `interface IOrderFilter { bool Matches(Order o); }` with one implementation, used to parameterise that loop
    - d) A method beginning `if (customer == null) { throw new ArgumentNullException(); }`, where every parameter is a plain reference type and the file has no annotations
    - e) `public string Describe() { return $"{Id}: {Total}"; }`

<details markdown="1"><summary>Check</summary>

**(a)** An extension member, from lesson 12: `public static decimal Total(this Order o) => ...`, called as `order.Total()`. What changes is the reading order, subject first, which is what lets it join a chain. Check for a name collision with a declared member first, since the type's own member would win silently.

**(b)** A LINQ query, from lesson 13: `orders.Where(...).Select(...)`. And decide deliberately whether the result should stay a query or be materialised with `ToList`, because the loop version produced a list and the query version produces a question, which is a behavioural difference rather than a stylistic one.

**(c)** A `Func<Order, bool>`, from lesson 14. A single-method interface with one implementation is a delegate that has been given a class to live in, and the framework already ships the type. Keep the interface only if implementations need names, state, or to be discovered.

**(d)** Nullable annotations, from lesson 15: annotate the parameters so the signature says which may be null, and then keep the argument check only where it is a public boundary that untrusted callers reach. The annotation informs honest callers at compile time; the check handles everyone else. Deleting the check because you added a `?` is the mistake to avoid, since annotations enforce nothing at run time.

**(e)** An expression body, from this lesson: `public string Describe() => $"{Id}: {Total}";`. This one is the safe kind, since the member really is the expression.

The thread: each change replaces a construct that was carrying its own scaffolding with one the language already provides, and in four of the five cases the scaffolding was there because another language needed it. That is what "translated Java" means as a review comment, and being able to name the specific replacement is what makes the comment actionable rather than stylistic.

</details>

## Real-world reps

- [ ] Find three expression-bodied members in C# you have access to. For each, decide whether the member is the expression or whether the form is hiding a decision.
- [ ] Find a `static` helper class in a codebase you can reach and apply the stage 3 table to it, one row at a time.
- [ ] Tomorrow: take one file you wrote before this stage and rewrite it against the five-row table. Count how many of the five applied, and keep the ones you would defend in review.

## Going further

- [Docs: "The lambda operator", Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/operators/lambda-operator)
- [Docs: "Properties (C# Programming Guide)", Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/csharp/properties)
- [Docs: "Language Integrated Query (LINQ)", Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/csharp/linq/)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
