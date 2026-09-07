---
title: "21. Grouping and Folding"
description: "Aggregating with fold and reduce, grouping without building the groups, and the stage 4 capstone of defending what a pipeline costs"
type: lesson
---

# Lesson 21. Grouping and Folding

**Mission link:** Stage 4 closes here: these are the operations where the choice between a collection pipeline and a sequence has real consequences, so this lesson asks you to make that choice and defend it.
**Primary source:** [Docs: "Aggregate operations", Kotlin](https://kotlinlang.org/docs/collection-aggregate.html)
**Prerequisites:** [Lesson 20](0020-sequences-and-laziness.md), [Lesson 19](0019-collection-operators.md), [Lesson 14](0014-scope-functions.md)

## Warm-up

1. ▢ What makes a sequence chain actually start doing work, and what is the name for the operations that do not?

<details markdown="1"><summary>Check</summary>

A terminal operation, `toList()` or `sum()` for instance, is what requests the result and therefore triggers the whole chain. Everything that returns another lazily-produced sequence, `map` and `filter` among them, is intermediate and runs nothing on its own. Sequence elements can be retrieved only through a terminal operation.

</details>

2. ▢ What does `partition` return, and what does it save you over calling `filter` and `filterNot` with the same predicate?

<details markdown="1"><summary>Check</summary>

A `Pair<List<T>, List<T>>`, the matches first and the rest second, which destructures straight into two names. The two-call version traverses the input twice, evaluates the predicate twice per element, and leaves two call sites that a later edit can let drift apart.

</details>

3. ▢ `x.let { ... }` and `x.also { ... }`: which one gives you the lambda's result, and which gives you `x` back?

<details markdown="1"><summary>Check</summary>

`let` returns the lambda's result, so it is the one you use to transform. `also` returns the context object `x`, so it is the one you use for a side effect in the middle of a chain without breaking it. Both expose the object as `it` rather than as `this`.

</details>

## Know this

**Aggregates first, because most of the time you do not need a fold at all.** The standard library already has `count()`, `sum()`, `average()`, `sumOf { }`, and the min and max family ([Aggregate operations](https://kotlinlang.org/docs/collection-aggregate.html)). Two distinctions inside that family are worth getting right, because the names look interchangeable and are not. `maxByOrNull { }` returns the **element** for which the selector is largest; `maxOf { }` returns the largest **value the selector produced**. And the `...OrNull` forms return `null` on an empty collection, while the `minOf`/`maxOf` alternatives do not have a null to give you. That is a lesson 1 decision wearing a different hat: take the `OrNull` form where empty is genuinely possible and let the type system make you handle it.

**`fold` and `reduce` are for the aggregate the library does not have.** Both apply an operation to the elements in sequence, where the operation takes the accumulated value so far and the current element. The whole difference is the start: `fold` takes an initial value and uses it on the first step, while `reduce` uses the first and second elements as the operation's two arguments on the first step. The docs' own example is the trap: `numbers.fold(0) { sum, element -> sum + element * 2 }` sums the doubled elements correctly, and passing that same lambda to `reduce` quietly does not, because the first element never gets doubled.

Two consequences follow from that one difference. `reduce` has no initial value, so its accumulator is stuck at the element type, whereas `fold`'s accumulator is whatever you seeded it with: a `Map`, a `StringBuilder`, a domain object. Build anything other than a bigger element with `fold`. And `reduce` on an empty collection has nothing to return at all, so it throws rather than inventing a value; `reduceOrNull()` is the variant that hands back `null` instead, while `fold` simply returns the initial value and needs no special case.

Three variants worth recognising:

|Operation|What it does|
|---|---|
|`foldRight` / `reduceRight`|Same accumulation from the last element backwards. **The operation's parameters swap round:** the element comes first, the accumulated value second|
|`runningFold` / `scan`|A fold that keeps every intermediate accumulator, returning the list of them rather than just the last|
|`runningReduce`|The same, seeded the way `reduce` seeds|

**Grouping is where the cost argument of this stage bites.** `groupBy { }` returns a `Map` whose keys are the lambda's results and whose values are the `List` of elements that produced each key, and a second lambda transforms those values instead of keeping the original elements ([Grouping](https://kotlinlang.org/docs/collection-grouping.html)). That is exactly what you want when you need the members of each group. When you only need one value per group, it is the wrong tool, because it builds every member list first: `groupBy { it.status }.mapValues { it.value.size }` allocates a list of every element in each group and then throws all of them away for their sizes.

`groupingBy { }` is the answer to that. It returns a `Grouping` rather than a `Map`, and the operations you then call on it, `eachCount()` most commonly, accumulate one value per key without ever materialising the member lists ([Grouping](https://kotlinlang.org/docs/collection-grouping.html)). The same `Grouping` also carries `fold`, `reduce` and `aggregate`, which is how you get a per-group total, or a per-group anything, on the same terms.

**So the stage's question, made concrete.** Folding streams: it consumes one element at a time and keeps one accumulator, so it is terminal on a sequence and costs nothing extra there. Grouping does not stream: it has to hold a slot for every key it has seen before it can answer anything, which is precisely lesson 20's stateful category, so its result is materialised wherever you put it. What `asSequence()` still buys you in front of a grouping step is everything upstream of it: the filters and maps that would otherwise each have built a full intermediate list. That is the shape of a defensible answer, and defending it is what closes this stage.

## Practice

1. ▢ For `val numbers = listOf(5, 2, 10, 4)`, predict both results: `numbers.reduce { sum, element -> sum + element * 2 }` and `numbers.fold(0) { sum, element -> sum + element * 2 }`.

<details markdown="1"><summary>Hint</summary>

Write out the first step of each by hand. What is bound to `sum` and to `element` the very first time the lambda runs?

</details>

<details markdown="1"><summary>Check</summary>

`37` and `42`. `fold` starts with the initial `0` and the first element, so every element gets doubled: twice 21 is 42. `reduce` starts with the first and second elements as the two arguments, so `5` arrives as the accumulator and is never doubled: 5 plus 4 plus 20 plus 8 is 37. The gap between them is exactly the undoubled first element. Note that both compile and both look reasonable, which is why this is a bug you predict rather than one you notice.

</details>

2. ▢ `numbers.foldRight(0) { sum, element -> sum + element * 2 }` compiles and returns `81` instead of `42`. Why?

<details markdown="1"><summary>Hint</summary>

The parameter names are yours to choose. The order they arrive in is not.

</details>

<details markdown="1"><summary>Check</summary>

Folding right swaps the operation's parameters: the element comes first and the accumulated value second. So `sum` is bound to the element and `element` to the accumulator, and the expression computes element plus twice the accumulator. Both are `Int`, so nothing stops it compiling, and the names actively lie about what they hold. Written correctly it is `numbers.foldRight(0) { element, sum -> sum + element * 2 }`.

</details>

3. ▢ On an empty list of `Int`, what do `fold(0) { a, b -> a + b }`, `reduce { a, b -> a + b }`, and `maxByOrNull { it }` each give you?

<details markdown="1"><summary>Check</summary>

`fold` returns `0`, the initial value, having run the operation zero times. `reduce` throws: with no initial value its first step needs two elements and there are none, so there is no value it could honestly return. `maxByOrNull` returns `null`, which is the whole reason the name carries that suffix. Reach for `reduceOrNull()` when an empty input is legitimate, or use `fold` and let the seed be the answer for the empty case.

</details>

4. ▢ You need the number of log entries per status code. Compare `entries.groupBy { it.status }.mapValues { it.value.size }` with `entries.groupingBy { it.status }.eachCount()`. What does the first one allocate that the second does not?

<details markdown="1"><summary>Check</summary>

A `List` for every status code, holding every entry that had it. `groupBy` builds the full member list per key because that is its contract, and `mapValues { it.value.size }` then reads one `Int` off each list and discards it. `groupingBy` returns a `Grouping`, and `eachCount()` accumulates a counter per key, so no member list is ever built. Same result map, and the second version's peak memory does not scale with the number of entries per group.

</details>

5. ▢ Which claim correctly describes `groupingBy`?

    - a) `groupingBy` builds a list of members per key, then reduces each list down
    - b) `groupingBy` accumulates one value per key, without ever building the member lists
    - c) `groupingBy` returns a map immediately, so a later fold reads that map twice
    - d) `groupingBy` streams its input lazily, so its final result is also never materialised

<details markdown="1"><summary>Check</summary>

**b)** is right, and it is the reason to reach for it over `groupBy` when you want one value per group rather than the members. (a) is `groupBy` followed by an aggregation, which is the version that allocates. (c) is false: `groupingBy` returns a `Grouping`, not a `Map`, and the map appears only when you call an operation such as `eachCount()` on it. (d) claims too much: grouping has to keep a slot per key while it works, so the result is materialised, and only the steps upstream of the grouping can be lazy.

</details>

6. ▢ **Stage capstone.** Ten million log lines are read from a file, filtered to the ones from today, mapped to a status code, and counted per code. Write the pipeline you would use, then defend it: name what each decision avoids building, and name the one thing that gets materialised no matter what you choose.

<details markdown="1"><summary>Check</summary>

Something with the shape `lines.asSequence().filter { it.isToday() }.groupingBy { it.status }.eachCount()`, and the defence matters more than the exact code.

`asSequence()` earns its overhead here on both counts from lesson 20: the input is large, and there is a multistep chain in front of the aggregation, so the eager version would build a full filtered list and then a full list of status codes before counting anything. The per-element cost of laziness is negligible against ten million elements of real work. `groupingBy` rather than `groupBy` avoids one list per status code holding every line that had it, which is the allocation that actually scales with the input.

What is materialised regardless: the result map, one entry per distinct status code. Grouping is stateful, so it must hold a slot per key it has seen. That is fine, and saying so is the point: the count of distinct status codes is small and bounded, while the count of lines is neither.

The answer that would fail this capstone is "use a sequence, sequences are faster". On a list of twenty lines, the eager version is the better call, and being able to say why is the same skill.

</details>

## Real-world reps

- [ ] Find a `groupBy` in code you have access to. Decide whether the caller uses the member lists or only one value per group, and say which of `groupBy` and `groupingBy` that code should be using.
- [ ] Find a hand-written accumulation loop in your own work, the kind with a `var` outside a `for`. Rewrite it as a `fold` on paper, then decide honestly which version you would rather read in six months.
- [ ] Tomorrow: take the pipeline from the capstone item and re-argue it for an input of fifty elements instead of ten million. Write down the point at which your answer flips, and what you would need to measure to find it exactly.

## Going further

- [Docs: "Aggregate operations", Kotlin](https://kotlinlang.org/docs/collection-aggregate.html)
- [Docs: "Grouping", Kotlin](https://kotlinlang.org/docs/collection-grouping.html)
- [Docs: "Sequences", Kotlin](https://kotlinlang.org/docs/sequences.html)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
