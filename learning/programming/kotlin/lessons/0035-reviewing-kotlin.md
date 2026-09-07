---
title: "35. Reviewing Kotlin"
description: "Turning the arc into a review instrument: the cost each habit hides, the shape of a comment that names it, and what not to review"
type: lesson
---

# Lesson 35. Reviewing Kotlin

**Mission link:** The last line of the mission: given Kotlin written with a habit that merely compiles, name the habit and rewrite it idiomatically. Every earlier lesson asked what a construct does. This one asks what it costs.
**Primary source:** [Docs: "Coding conventions", Kotlin](https://kotlinlang.org/docs/coding-conventions.html)
**Prerequisites:** [Lesson 34](0034-java-interop.md), [Lesson 24](0024-structured-concurrency.md), [Lesson 1](0001-null-safety.md)

## Warm-up

1. ▢ A Java method with no nullability annotations returns a value into Kotlin. What type does Kotlin give it, and what are the two ways to restore null-safety?

<details markdown="1"><summary>Check</summary>

A platform type, which you may use as though it were non-null and which therefore carries the risk instead of the compiler. Restore the guarantee either with an explicit type annotation on the Kotlin side, which is local and always available, or with nullability annotations on the Java declaration, which fixes it for every caller at once.

</details>

2. ▢ Why does a child coroutine's `CancellationException` not fail its parent, when an `IOException` would?

<details markdown="1"><summary>Check</summary>

Because the first propagation condition excludes it: a child's failure fails the parent only when the exception is not a `CancellationException`, the child was not created by a lexical builder, and the parent's `Job` is not a `SupervisorJob`. Cancellation travels down the tree as a request; failure travels up it as news.

</details>

3. ▢ What does `val` promise about the thing it holds?

<details markdown="1"><summary>Check</summary>

That the reference will not be reassigned, and nothing more. The object on the other end is as mutable as its own type allows, which is why a `val` holding a `MutableList` is a list whose contents can still change, and why `val` is not thread safety.

</details>

## Know this

**A review asks a different question from a lesson.** Every earlier lesson answered "what does this construct do". A review asks "what is this construct costing", and the answer has a shape:

> the construct, the mechanism it actually uses, the consequence that follows, and the cheaper alternative.

A comment with all four is a fact the author can check. A comment with only the first and last is a preference, and it is why review threads go in circles. When the answer is a judgement rather than a mechanism, say what it rests on and name what would change it, which converts an argument into a decision somebody can make.

**The arc, turned into a checklist.** Each row is a habit that compiles, the cost it hides, and the lesson that explains the mechanism if the author wants it.

|Habit that compiles|What it is costing|Lesson|
|---|---|---|
|`!!` reached for to silence a compile error|Converts an unknown into a crash rather than a decision|[1](0001-null-safety.md)|
|A null check on a non-nullable type|Dead code, and a signal the author did not trust the signature|[1](0001-null-safety.md)|
|`var` where nothing reassigns|The reader must now check whether anything does|[2](0002-val-var-and-immutability.md)|
|A `MutableList` returned from a public property|Callers can mutate your state, and `val` does not stop them|[5](0005-collections-basics.md)|
|A class where a data class was meant|Hand-written `equals`, or none, and a `toString` nobody updated|[8](0008-data-classes.md)|
|`else` on a `when` over a closed set|The compiler stops telling you when a case is added|[9](0009-sealed-classes-and-exhaustive-when.md)|
|A scope function chosen by habit|A return value nobody meant, usually `also` where `let` was wanted|[14](0014-scope-functions.md)|
|A three-step chain over a large collection|Two intermediate lists built to be discarded|[19](0019-collection-operators.md), [20](0020-sequences-and-laziness.md)|
|`groupBy` followed by counting|A member list per key, allocated and thrown away for its size|[21](0021-grouping-and-folding.md)|
|`@Volatile` on a counter that is incremented|Visibility without atomicity, so increments are lost|[22](0022-threads-and-the-memory-model.md)|
|`Thread.sleep` inside a coroutine|A blocked pool thread, invisible until the pool is under load|[23](0023-suspend-functions-and-coroutine-builders.md)|
|`GlobalScope.launch`, or a `Job()` passed to a builder|Work nobody owns, waits for, or cancels|[24](0024-structured-concurrency.md), [25](0025-coroutine-context-and-dispatchers.md)|
|A hardcoded dispatcher|A test that cannot replace it, so its delays are real|[25](0025-coroutine-context-and-dispatchers.md), [28](0028-test-frameworks.md)|
|A cold flow collected twice|The builder's work done twice, including the query in it|[26](0026-flows.md)|
|`catch (e: CancellationException)` with no rethrow|A coroutine that runs on past a cancellation looking successful|[27](0027-cancellation-and-exception-handling.md)|
|`open` added so a test can subclass|A permanent change to an inheritance contract for one test|[29](0029-mocking.md)|
|`api` for a dependency used only internally|An internal choice becomes every consumer's compile-time contract|[30](0030-gradle-and-dependency-management.md)|
|A type parameter used in one direction only|Callers writing projections that a declaration-site `out` would have saved|[33](0033-generics-and-variance.md)|
|`@JvmOverloads` with no Java callers|A published overload set, so parameter order is now breaking|[34](0034-java-interop.md)|

**The conventions are the shared ground.** A review that cites the official style guide stops being about taste: prefer a property over a no-argument function when the computation does not throw, is cheap or cached, and returns the same result while state is unchanged; prefer `if` for a binary condition and `when` from three options up; keep class contents in the prescribed order without sorting methods alphabetically or by visibility; and name a file for what it contains, which rules out `Util` ([Coding conventions](https://kotlinlang.org/docs/coding-conventions.html)). Where a disagreement is genuinely about style, the guide ends it. Where it is not, saying so is more honest than reaching for the guide anyway.

**What not to review.** The cost of a comment is the author's attention, so spend it where a mechanism produces a consequence. A construct that would merely be shorter is not costing anything yet, and a review that flags everything trains people to skim it. Three tests worth applying before posting: can you name the mechanism, would a reader of this code hit the consequence, and is the alternative actually cheaper here. If the answer to any of them is no, you have a preference rather than a finding, and saying it as a preference is the honest form.

## Practice

1. ▢ Review this: `fun displayName(user: User?): String { if (user == null) { return "" }; return user.name!! }`, where `User.name` is declared `String`. Name every habit and rewrite it.

<details markdown="1"><summary>Check</summary>

Two habits, both from lesson 1. The `!!` is applied to `user.name`, which is already non-nullable, so it protects against nothing and reads as though the author did not believe the type. And the explicit null check is a Java-shaped way of writing something the language has an operator for. Rewritten: `fun displayName(user: User?): String = user?.name ?: ""`. The comment worth leaving names the mechanism rather than the style: the `!!` cannot fire on a non-nullable property, so it is telling a future reader that the type is not to be trusted, which is exactly the doubt null safety exists to remove.

</details>

2. ▢ Review this: a class exposes `var items: MutableList<Item> = mutableListOf()`. Name the costs in order of severity.

<details markdown="1"><summary>Check</summary>

Three, and the order matters. Worst: the property's type is mutable, so any caller can add and remove elements of your state without going through you, and no invariant you maintain survives that. Next: it is a `var`, so a caller can also replace the whole list, which invalidates any reference anyone else was holding. Least, but real: `val` would not have fixed the first problem, and reviewers who stop at "make it a `val`" leave the actual defect in place. The rewrite exposes a `List` and keeps the `MutableList` private, so the type states who may change it, which is lesson 5's read-only-by-interface distinction doing the work.

</details>

3. ▢ Review this request handler: `GlobalScope.launch(Dispatchers.IO) { try { audit.write(event) } catch (e: Exception) { log.warn(e) } }`. Name both defects.

<details markdown="1"><summary>Check</summary>

First, `GlobalScope.launch` puts the work outside the request's tree: nothing waits for it and cancelling the request leaves it running, which is the shape the whole of structured concurrency exists to make hard to write. Launch it in the request's scope, or in a scope some component owns and cancels.

Second, and easier to miss, `catch (e: Exception)` catches `CancellationException` too, and swallowing that means the coroutine carries on past a cancellation request while appearing to have completed normally. Catch the exceptions you mean, or rethrow a `CancellationException` explicitly, which is what the documentation's own examples do.

Both comments are worth making because both name a mechanism. "Do not use `GlobalScope`" on its own would not be.

</details>

4. ▢ Review this: `val first = items.filter { it.isActive }.map { it.name }.first()`, where `items` holds tens of thousands of elements. Name the cost, then say when you would leave it alone.

<details markdown="1"><summary>Check</summary>

The chain is eager, so `filter` builds a full list of active items and `map` builds a full list of their names, and then `first()` takes one element and the rest is garbage. `items.asSequence().filter { ... }.map { ... }.first()` processes element by element and stops at the first match, which for this shape is the difference between touching everything and touching almost nothing.

When to leave it alone: when `items` is small, when the predicate and the transform are trivial, or when this runs once at startup rather than per request. Laziness has its own overhead, and a reviewer who asks for `asSequence()` everywhere is trading a real cost for an imagined one. The comment that survives scrutiny names the input size it depends on, so the author can say "it is never more than twenty" and be right.

</details>

5. ▢ Which claim describes a review comment worth posting?

    - a) A good review comment names the idiom the author should have used instead
    - b) A good review comment names the mechanism, the consequence, and the cheaper alternative
    - c) A good review comment cites the style guide, since taste is not arguable
    - d) A good review comment flags every construct that could have been written shorter

<details markdown="1"><summary>Check</summary>

**b)** Those three parts are what make it checkable rather than arguable, and the fourth part, the construct itself, is already on the screen. (a) skips the middle and is why review threads stall: the author has no way to evaluate the claim except by trusting you. (c) is right about style disagreements and wrong as a general method, since most costs in this lesson's table are mechanisms rather than matters of taste. (d) mistakes volume for rigour, and spends the author's attention on findings that cost nothing.

</details>

6. ▢ **Final item.** Take a Kotlin file from your own work, or the largest one you have access to, and write three review comments on it in the four-part form: construct, mechanism, consequence, cheaper alternative. Then, for each, decide whether it is a finding or a preference.

<details markdown="1"><summary>Check</summary>

There is no answer key for this one, which is the point: the arc has run out of things to tell you and this is the part that only works on real code.

What to check in your own three comments. Each should name a mechanism you could explain to the author without appealing to authority, and a consequence a reader of that code would actually meet. If a comment's consequence is "it is harder to read", ask whose reading, and whether the alternative is genuinely easier or just more familiar to you. If you cannot name the mechanism, you have found a preference, and the honest form is to say so: "I would have written this as X, though I cannot point at anything it costs" is a legitimate comment and a much better one than a mechanism you invented afterwards to justify a taste.

The bar the mission set was naming the habit and rewriting it idiomatically. Three comments that meet it, on code somebody is going to ship, is the whole thing.

</details>

## Real-world reps

- [ ] Review one open pull request in Kotlin, or one file you wrote more than six months ago, against this lesson's table. Count how many rows apply.
- [ ] Take a review comment you received and disagreed with. Work out whether it named a mechanism or a preference, and write the version of it that would have persuaded you.
- [ ] Tomorrow: pick the row of the table you have never thought about, open the lesson it points at, and find one instance of that habit in code you can reach.

## Going further

- [Docs: "Coding conventions", Kotlin](https://kotlinlang.org/docs/coding-conventions.html)
- [Docs: "Kotlin for Java developers", Kotlin](https://kotlinlang.org/docs/comparison-to-java.html)
- [Resources](../RESOURCES.md)

---

That is the arc: thirty-five lessons from `null` to a review comment, and the through-line was never the syntax, since every construct in it exists because something was costing somebody something, and knowing which cost is what earns you the right to disagree with a convention rather than merely follow it. The lesson table in the [workspace README](../README.md) is a lookup now rather than a curriculum: when a review needs the mechanism behind a habit, the lesson that taught it is the citation. What is left is the part no lesson can do for you, which is doing it on code somebody is about to ship.

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
