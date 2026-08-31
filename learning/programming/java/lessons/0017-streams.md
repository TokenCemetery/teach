---
title: 17. Streams
description: A pipeline that describes work, does none of it until asked, and can only be asked once
type: lesson
---

# Lesson 17. Streams

**Mission link:** A stream chain that runs when you did not expect, throws when reused, or hides a side effect in a lambda is exactly the kind of thing a reviewer flags without running it, and knowing precisely when each part of a pipeline runs is what lets you both avoid writing one and say exactly why someone else's is wrong.
**Primary source:** [`Stream`, Java SE 25 API](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/stream/Stream.html)
**Prerequisites:** [Lesson 13](0013-generics-and-erasure.md), [Lesson 9](0009-interfaces.md)

## Warm-up

1. ▢ `List<String>` and `List<Integer>` report the same value from `getClass()` at run time. Why?

<details markdown="1"><summary>Check</summary>

Erasure. The compiler checks the type arguments and then discards them, so both variables are backed by one class, `List`, once the program is running. The distinction the compiler enforced never reaches the runtime to be checked again.

</details>

2. ▢ Between `optional.orElse(fallback())` and `optional.orElseGet(() -> fallback())`, which calls `fallback()` even when `optional` already holds a value?

<details markdown="1"><summary>Check</summary>

`orElse`. Its argument is an ordinary method argument, so Java evaluates it before the call happens, present or not. `orElseGet` takes a supplier and only invokes it when the value is absent, which is why it is the right choice whenever producing the fallback costs anything.

</details>

## Know this

A stream is not a collection. It has no elements of its own, it does not store anything, and most of what feels surprising about one falls out of that single fact.

### Source, intermediate operations, terminal operation

A pipeline has exactly one **source** (a collection, an array, a generator, a range of numbers), any number of **intermediate operations** (`map`, `filter`, `sorted` and the rest, each returning a new stream), and exactly one **terminal operation** (`forEach`, `toList`, `reduce`, `count`, and so on, which produces a result or a side effect instead of another stream).

```java
List<Integer> nums = List.of(1, 2, 3);
Stream<Integer> pipeline = nums.stream()
        .filter(n -> n % 2 != 0)
        .map(n -> n * 10);
```

Nothing above has run yet. Building a pipeline only records what to do; nothing happens until a terminal operation is called on it, and only then does the whole chain execute.

### Laziness, shown one element at a time

Printing inside `filter` and `map` and comparing the order against the source shows the shape of the laziness, rather than just asserting it:

```java
System.out.println("about to call forEach");
pipeline.forEach(n -> System.out.println("sink " + n));
```

```text
about to call forEach
filter 1
map 1
sink 10
filter 2
filter 3
map 3
sink 30
```

Nothing printed until `forEach` ran, and then each element travelled all the way through the pipeline before the next one started. A stream is not "filter everything, then map everything"; it is one element at a time, end to end, pulled through by the terminal operation. That pull is also why an intermediate operation cannot see the whole stream: it only ever sees the one element passing through at that moment.

### A stream is consumed once

A `Stream` is a one-shot description of a computation, not a reusable object:

```java
Stream<Integer> s = Stream.of(1, 2, 3);
System.out.println(s.count());   // 3
s.count();                       // throws
```

The second call fails at run time:

```text
java.lang.IllegalStateException: stream has already been operated upon or closed
```

There is no way to "rewind" a stream. If the same sequence of elements is needed twice, build the pipeline twice from the source, or terminate once into a collection and reuse that.

### Short-circuiting, including an infinite source

Some intermediate operations (`limit`, `takeWhile`) and some terminal operations (`findFirst`, `findAny`, `anyMatch`, and the others ending in `Match`) are **short-circuiting**: they can produce a result without the whole stream being pulled through. That is what makes an infinite source usable at all:

```java
Stream.iterate(1, n -> n + 1)
        .filter(n -> n > 3)
        .findFirst();
```

```text
filter 1
generating 2
filter 2
generating 3
filter 3
generating 4
filter 4
result Optional[4]
```

`Stream.iterate` never runs out of elements to generate, but `findFirst` stopped pulling the moment it had an answer, so generation stopped at 4. Without a short-circuiting operation somewhere in the chain, a terminal operation on an infinite source never returns.

### The core intermediate operations

`map` transforms each element one-for-one; `flatMap` transforms each element into a stream and flattens the results, which is the tool for turning a list of lists into one flat list:

```java
List<List<Integer>> nested = List.of(List.of(1, 2), List.of(3, 4));
nested.stream().flatMap(List::stream).toList();   // [1, 2, 3, 4]
```

`filter` keeps elements matching a predicate. `distinct` removes duplicates by `equals`. `limit` and the short-circuiting `takeWhile` both stop early, but for different reasons: `limit(n)` stops after `n` elements regardless of content, `takeWhile(predicate)` stops at the first element that fails the predicate. `dropWhile` is the mirror image: it discards elements from the front until the predicate first fails, then keeps everything from there on, predicate or not:

```java
List<Integer> source = List.of(1, 2, 3, 10, 4, 5);
source.stream().takeWhile(n -> n < 5).toList();   // [1, 2, 3]
source.stream().dropWhile(n -> n < 5).toList();   // [10, 4, 5]
```

`sorted` is the odd one out: every other intermediate operation here can pass elements downstream as they arrive, but `sorted` cannot know the correct first element until it has seen the last one, so it forces the entire upstream to run before anything downstream sees a single element:

```java
List.of(3, 1, 2).stream()
        .peek(n -> System.out.println("peek " + n))
        .sorted()
        .findFirst()
        .ifPresent(n -> System.out.println("first sorted " + n));
```

```text
peek 3
peek 1
peek 2
first sorted 1
```

All three elements were pulled through before `sorted` released the first one, even though the terminal operation only asked for one. Compare that with the same pipeline minus `sorted`, which short-circuits after the first element and never touches the rest. `sorted` is a **stateful** intermediate operation for exactly this reason.

### Primitive streams, and why they exist

`mapToInt`, `mapToLong` and `mapToDouble` convert a `Stream<T>` into an `IntStream`, `LongStream` or `DoubleStream`, and each has a matching `boxed()` to convert back:

```java
int total = Stream.of("a", "bb", "ccc").mapToInt(String::length).sum();   // 6
```

They exist to avoid boxing every element into an `Integer` or `Double` object, which matters once a pipeline runs over anything large, and they add reductions that only make sense for numbers, such as `sum`, `average`, `max` and `min`, without forcing every caller of `Stream<T>` to carry them.

### `reduce`, and the mutable-accumulation trap

`reduce` combines every element into one value using an identity and a combining function:

```java
int product = Stream.of(1, 2, 3, 4).reduce(1, (a, b) -> a * b);   // 24
```

That is the right use of `reduce`: an immutable identity and a combiner that returns a new value each time. The three-argument overload also accepts a mutable container, an accumulator and a combiner for merging two containers, and it is possible to make it build a list:

```java
Stream.of(1, 2, 3).reduce(
        new ArrayList<Integer>(),
        (list, n) -> { list.add(n); return list; },
        (l1, l2) -> { l1.addAll(l2); return l1; });
```

This runs and gives the right answer on a sequential stream, but it mutates the same accumulator across steps that `reduce`'s contract does not promise will happen in order or on one thread, which is precisely the shape that breaks under parallel execution. Collecting into a mutable container has its own purpose-built operation, `collect`, which lesson 18 covers; the rule for `reduce` itself is to keep the combining function free of side effects and let it return values instead of mutating one.

### Encounter order, `findFirst` versus `findAny`

A stream from an ordered source (a `List`, an array, a range) has an **encounter order**, the order elements arrive in. `findFirst` always returns the first element in that order. `findAny` returns any matching element, and is free to return whichever one it finds fastest:

```java
List.of(1, 2, 3, 4).stream().filter(n -> n > 1).findFirst();   // Optional[2]
List.of(1, 2, 3, 4).stream().filter(n -> n > 1).findAny();     // Optional[2]
```

On a plain sequential stream the two behave identically, which is exactly why the difference is easy to miss: `findAny` exists for parallel pipelines, where relaxing the order requirement lets the runtime return the first match from any thread, and it only diverges from `findFirst` under parallel execution on an unordered or reordered source. On sequential code, prefer `findFirst` when order matters to the reader and `findAny` when it genuinely does not, as a signal of intent rather than for any difference in this run.

### Side effects in a lambda

A lambda passed to a stream operation is meant to be free of side effects, and the reason is not a style rule, it is that the pipeline decides for itself how much of the stream it needs to look at:

```java
int[] evenSeen = {0};
boolean hasOdd = List.of(2, 4, 6, 7, 8, 10).stream()
        .filter(n -> {
            if (n % 2 == 0) evenSeen[0]++;
            return n % 2 != 0;
        })
        .anyMatch(n -> true);
System.out.println("hasOdd " + hasOdd);
System.out.println("evenSeen " + evenSeen[0]);
```

```text
hasOdd true
evenSeen 3
```

The list has five even numbers, but `evenSeen` stopped at 3. `anyMatch` short-circuited the moment it found the first odd number, `7`, and everything after it was never visited. The count is not wrong because of a bug in the arithmetic; it is wrong because a side effect was made to depend on every element being visited, and nothing in a stream's contract promises that. The same reasoning is why the API documentation calls for lambdas that are **non-interfering** (they do not touch state the pipeline itself might be reading) and **stateless** (their result depends only on their argument): both properties are what let the pipeline reorder, skip or parallelise the work without changing the answer, and a reviewer who flags a side-effecting lambda is checking for exactly this.

### `Stream.iterate` and `Stream.generate`

`Stream.iterate(seed, next)` produces an infinite stream by repeatedly applying `next`, and needs a short-circuiting operation downstream to ever finish. A three-argument overload, `Stream.iterate(seed, hasNext, next)`, added in Java 9, takes the stopping condition itself and produces a finite stream directly:

```java
Stream.iterate(1, n -> n <= 5, n -> n * 2).forEach(System.out::println);
```

```text
1
2
4
```

`Stream.generate(supplier)` produces an infinite stream by calling a supplier with no relation between elements, and almost always needs `limit`:

```java
Stream.generate(() -> counter[0]++).limit(5).toList();   // [0, 1, 2, 3, 4]
```

### `peek` is a debugging tool, not a processing step

`peek` runs an action on each element as it passes and returns the same stream unchanged. Its documented purpose is to let you see values flowing through a pipeline while you are working on it, not to do anything the result depends on, and the implementation is explicitly allowed to skip elements the terminal operation does not need:

```java
List<Integer> result = List.of(1, 2, 3, 4, 5).stream()
        .peek(n -> System.out.println("peek " + n))
        .limit(2)
        .toList();
System.out.println(result);
```

```text
peek 1
peek 2
[1, 2]
```

`limit(2)` only needed the first two elements, so `peek` was never called for `3`, `4` or `5`. The same elision happens with a terminal operation that can answer without visiting every element at all: calling `count()` directly on an unfiltered, sized stream skips the whole pipeline body, `peek` included, because the size is already known without looking at a single element; adding a `filter` upstream removes that shortcut and every element gets peeked again. Never make a lambda passed to `peek` do work the program depends on; if the pipeline optimises the visit away, that work silently stops happening.

### The honest limit: when a `for` loop is clearer

A stream pipeline is at its best when it is one line of transformation feeding one terminal operation. It stops being the right tool once the body needs more than one thing at a time: multiple accumulators tracking different conditions, an early exit that depends on comparing two elements, a checked exception that has no clean way through a lambda, or logic that reads better as a sequence of statements than as a chain of named operations. A `for` loop can `break`, `continue` to a label, and update three variables in one iteration without contorting into `reduce` or three separate passes; a stream chain forcing all of that into map, filter and a mutable side channel is usually the less readable option, not the more idiomatic one. The test is whether the stream version actually reads faster than the loop it replaced. If it does not, write the loop.

## Practice

1. ▢ Predict the printed order and the final result, then explain why the last two elements never appear in either.

   ```java
   List<Integer> nums = List.of(1, 2, 3, 4);
   List<Integer> result = nums.stream()
           .filter(n -> { System.out.println("filter " + n); return n % 2 == 0; })
           .map(n -> { System.out.println("map " + n); return n * n; })
           .limit(1)
           .toList();
   System.out.println(result);
   ```

<details markdown="1"><summary>Check</summary>

```text
filter 1
filter 2
map 2
[4]
```

`1` fails the filter and is dropped without ever reaching `map`. `2` passes, is mapped to `4`, and `limit(1)` is satisfied, so the pipeline stops pulling. `3` and `4` are never even offered to `filter`, because `limit` is short-circuiting and one match was already enough.

</details>

2. ▢ This code is meant to report whether any number in the list is negative, and separately count how many numbers were even along the way. Find the bug.

   ```java
   List<Integer> nums = List.of(2, 4, 6, 7, 8, 10);
   int[] evenCount = {0};
   boolean hasNegative = nums.stream()
           .peek(n -> { if (n % 2 == 0) evenCount[0]++; })
           .anyMatch(n -> n < 0);
   ```

<details markdown="1"><summary>Hint</summary>

`anyMatch` does not have to look at every element to answer the question it was asked. Would it, here?

</details>

<details markdown="1"><summary>Check</summary>

There is no negative number in the list, so `anyMatch` cannot short-circuit early on a match, but it still has to walk the entire stream to be sure none exists, so in this particular data `evenCount` does happen to end at 5. The bug is structural rather than visible in this run: the moment the list contains an early negative number, `anyMatch` returns as soon as it finds it, and every element after that point, even numbers included, is never peeked, so `evenCount` silently undercounts. Counting evens must not depend on how far a short-circuiting terminal operation happens to look; run the count with `filter(n -> n % 2 == 0).count()` as its own pass, or fold both facts into a single pass with `reduce` or a plain loop, rather than piggybacking one measurement on another operation's side effect.

</details>

3. ▢ Predict what the second line does, and quote the exception.

   ```java
   Stream<Integer> s = Stream.of(1, 2, 3);
   System.out.println(s.count());
   s.count();
   ```

<details markdown="1"><summary>Check</summary>

The first call prints `3` and consumes the stream. The second throws:

```text
java.lang.IllegalStateException: stream has already been operated upon or closed
```

A `Stream` has no state to reset once a terminal operation has run; if the elements are needed again, build the pipeline again from the source.

</details>

4. ▢ A method walks a list of records, and for each one: increments one of three separate counters depending on which of three conditions the record meets, appends a formatted line to a report `StringBuilder`, and stops the whole walk the moment it meets a record flagged `poisoned`. Would you write this as a stream pipeline, or a `for` loop? Justify your answer in a sentence or two.

<details markdown="1"><summary>Check</summary>

A `for` loop. Three independent counters, a growing side-effecting `StringBuilder`, and an early `break` on a condition unrelated to the other work are exactly the shape a stream chain has no clean vocabulary for: forcing them into `map`/`filter`/`reduce` needs either several passes over the same list or a bundle of mutable side channels threaded through lambdas that were supposed to be side-effect free. The loop states the four things happening per iteration as four statements, in order, and `break` says what it means.

</details>

5. ▢ You replace `.findFirst()` with `.findAny()` in a sequential pipeline over a `List`, run it a hundred times, and get the same element every time. Does that show `findAny` is safe to use here going forward? Explain.

<details markdown="1"><summary>Hint</summary>

What does `findAny`'s contract promise, as opposed to what one particular execution happened to do?

</details>

<details markdown="1"><summary>Check</summary>

No. `findAny`'s contract never promised encounter order in the first place; a sequential stream over an ordered source happens to visit elements in that order and return the first match it meets, which is why it looks identical to `findFirst` here. Nothing changes if the pipeline is later parallelised, or the source changes to something unordered, and at that point `findAny` is free to return a different match, while `findFirst` still would not. Repeated runs of unchanged sequential code can only confirm what the contract already allowed; they cannot upgrade a permission the contract never granted.

</details>

## Real-world reps

- [ ] Take a stream pipeline you have written before, or find one in code you have access to, add a `peek` between each stage, and run it to see whether every stage actually fires for every element.
- [ ] Find a nested loop that builds one flat list from a list of lists, and rewrite it with `flatMap`.
- [ ] Find a stream pipeline ending in `findAny`. Check whether its source is ordered, and decide honestly whether `findFirst` would say what you actually mean.
- [ ] Tomorrow: open a stream pipeline in code you already have, and for each intermediate operation ask whether a plain `for` loop would read faster. Rewrite it that way if the honest answer is yes.

## Going further

- [`Stream`](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/stream/Stream.html): the full operation list, with each one marked stateful or stateless
- [`java.util.stream` package summary](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/stream/package-summary.html): the non-interference and statelessness rules a stream lambda has to satisfy
- [`IntStream`](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/stream/IntStream.html): the primitive stream types and the reductions they add
- [Idiom and the library](../reference/idiom-and-library.md): the reference sheet for this stage
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
