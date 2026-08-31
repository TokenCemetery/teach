---
title: 18. Collectors
description: Turning a pipeline back into a container, and the three collectors that throw where you do not expect it
type: lesson
---

# Lesson 18. Collectors

**Mission link:** A stream is not the deliverable; the list, map or set it collects into is, and the three collectors that throw in places a loop never would are exactly the kind of thing a reviewer expects you to already know.
**Primary source:** [`Collectors`, Java SE 25 API](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/stream/Collectors.html)
**Prerequisites:** [Lesson 17](0017-streams.md), [Lesson 5](0005-arrays-and-collections.md)

## Warm-up

1. ▢ What actually runs a stream pipeline built from `.filter(...).map(...)`, and what happens if you call a terminal operation on the same stream a second time?

<details markdown="1"><summary>Check</summary>

Nothing runs until a terminal operation is called; the intermediate operations only describe the work. Calling a terminal operation again on the same stream throws, because a stream is a one-shot description of work rather than a reusable collection.

</details>

2. ▢ Which `Map` implementation is the default when you need key-to-value storage with no ordering promise, and which one keeps insertion order instead?

<details markdown="1"><summary>Check</summary>

`HashMap` is the default; `LinkedHashMap` keeps insertion order. Worth having front of mind here, because `toMap` and `groupingBy` hand you the default back unless you ask for something else.

</details>

## Know this

A terminal operation ends a stream, but `collect` is the one that turns it back into the container the rest of the program wants. `Collectors` supplies the recipes; `collect` runs them.

### `Collectors.toList` against `Stream.toList`

```java
List<Integer> a = Stream.of(1, 2, 3).collect(Collectors.toList());
a.add(4);                        // [1, 2, 3, 4]

List<Integer> b = Stream.of(1, 2, 3).toList();
b.add(4);                        // UnsupportedOperationException
```

Both lines produce a `List<Integer>` holding `1, 2, 3`, and that is where the similarity ends. `Collectors.toList()` makes no promise about the result, and in the current implementation it hands back an `ArrayList`, which is mutable. `Stream.toList()`, final in Java 16, is specified to return an unmodifiable list, and calling `add` on it throws `UnsupportedOperationException`.

The two also disagree about `null`. Running each through a stream containing `null` shows it directly: `Stream.of("a", null, "b").toList()` succeeds and returns `[a, null, b]`, while the same stream collected with `Collectors.toUnmodifiableList()` throws a `NullPointerException` with no message. `Stream.toList()` is unmodifiable but not null-hostile; `toUnmodifiableList()` is both. That is not the difference a name like "unmodifiable" suggests, and it is only visible by trying it.

This is a difference in mutability and null handling, not a style choice: reach for `Stream.toList()` when the result should be inert, and `Collectors.toList()` (or a `Collectors.toCollection(ArrayList::new)`) when the caller is going to keep building on it. `Collectors.toUnmodifiableList()`, `toUnmodifiableSet()` and `toUnmodifiableMap()`, also from Java 10 alongside `toSet` and `toMap`, are the collector-based route to the same unmodifiable guarantee `Stream.toList()` gives for free.

### `toSet` and `toMap`

```java
Set<Integer> lengths = words.stream().map(String::length).collect(Collectors.toSet());
Map<String, Integer> byWord = words.stream().collect(Collectors.toMap(w -> w, String::length));
```

`toSet` gives back a `HashSet`, so iteration order is not the insertion order. `toMap` takes a key function and a value function; running it prints the runtime type as `HashMap`, the same default `Map` you would have reached for by hand. Neither guarantee is part of the contract, only what the current implementation does, so do not write code that depends on the concrete class.

### The `toMap` traps

Two-argument `toMap` throws in two places a `HashMap` built by hand would not.

A duplicate key is the first. Collecting `"apple"` and `"avocado"`, which share a first letter, into a map keyed by that letter throws:

```text
java.lang.IllegalStateException: Duplicate key a (attempted merging values apple and avocado)
```

A `null` **value** is the second, and it surprises people who expect `toMap` to behave like the map it builds:

```java
Map<String, String> m = Stream.of("a", "b").collect(Collectors.toMap(k -> k, k -> null));
// throws NullPointerException, no message

Map<String, String> hm = new HashMap<>();
hm.put("a", null);               // succeeds: {a=null}
```

`HashMap.put` accepts a `null` value without complaint. `toMap` refuses one outright, because its merge step calls `Map.merge` internally, and `merge` treats a `null` value as "remove this key", which it cannot reconcile with inserting one. The exception carries no message in either case, only the type, so do not expect the trace to name the key.

The three-argument overload fixes the duplicate-key case by taking a merge function that decides what happens when two entries land on the same key:

```java
Map<Character, String> merged = words.stream()
    .collect(Collectors.toMap(w -> w.charAt(0), w -> w, (a, b) -> a + "/" + b));
// {a=apple/avocado, b=banana}
```

It does not fix the null-value case; the merge function only ever runs when a key collides, and a single `null` value collides with nothing. A four-argument overload adds a map factory, which is also how you ask `toMap` for something other than a `HashMap`:

```java
TreeMap<Character, String> sorted = words.stream()
    .collect(Collectors.toMap(w -> w.charAt(0), w -> w, (a, b) -> a, TreeMap::new));
```

### `groupingBy` and `partitioningBy`

`groupingBy` splits a stream into buckets by a classifier function, and the concrete type it returns, checked at run time, is `HashMap`. Every value list inside it is an `ArrayList` unless you say otherwise:

```java
Map<Integer, List<String>> byLength = words.stream().collect(Collectors.groupingBy(String::length));
// {5=[apple], 6=[banana], 7=[avocado]}, runtime type java.util.HashMap
```

A second argument is a **downstream collector**, applied to each bucket instead of collecting it into a list. This is where `counting`, `summingInt`, `averagingDouble`, `mapping`, `flatMapping`, `filtering` and `reducing` earn their place, since none of them are useful alone against a whole stream the way they are against each group:

```java
Map<Integer, Long> countsByLength = words.stream()
    .collect(Collectors.groupingBy(String::length, Collectors.counting()));
// {5=1, 6=1, 7=1}

Map<Integer, List<Character>> firstLettersByLength = words.stream()
    .collect(Collectors.groupingBy(String::length,
        Collectors.mapping(w -> w.charAt(0), Collectors.toList())));
// {5=[a], 6=[b], 7=[a]}
```

`mapping` transforms each element before it joins its bucket; `filtering` (Java 9) discards elements from a bucket without discarding the bucket, which is what plain `Stream.filter` before the `groupingBy` cannot do, since that would drop the key entirely instead of leaving it mapped to an empty list; `flatMapping` (Java 9) lets each element contribute zero or more results to its bucket; `reducing` folds a bucket down to one value the way `Stream.reduce` folds a whole stream. A three-argument `groupingBy` takes a map factory in the middle, the same idea as `toMap`'s fourth argument, so `Collectors.groupingBy(String::length, TreeMap::new, Collectors.toList())` groups into a `TreeMap` instead.

`partitioningBy` is `groupingBy` narrowed to a predicate: it always returns exactly two entries, keyed `true` and `false`, even when one side is empty. Checked at run time its concrete type is an internal `Collectors` nested class rather than a public one, which is the practical reason to program against `Map<Boolean, List<T>>` and never against its runtime class.

### `counting`, `summingInt`, `averagingDouble` alone

Used directly as the argument to `collect`, without `groupingBy`, these are just a longer way to write `count()`, `mapToInt(...).sum()` or `mapToDouble(...).average()`. Their real use is as the downstream collector shown above, where there is no primitive stream to fall back on because the grouping already happened.

### `joining`

```java
String s = words.stream().collect(Collectors.joining(", ", "[", "]"));
// [apple, avocado, banana]
```

The one-argument form takes only a delimiter; the three-argument form adds a prefix and a suffix, which is the tidy way to render a collection without a trailing separator to trim.

### `teeing`

`teeing`, final in Java 12, runs two collectors over the same stream and combines their results with a merge function, which is the one case where you need two different answers out of a stream that can only be consumed once:

```java
record MinMax(Optional<Integer> min, Optional<Integer> max) {}

MinMax mm = Stream.of(4, 8, 15, 16, 23, 42).collect(
    Collectors.teeing(
        Collectors.minBy(Comparator.naturalOrder()),
        Collectors.maxBy(Comparator.naturalOrder()),
        MinMax::new));
// MinMax[min=Optional[4], max=Optional[42]]
```

Without `teeing` this needs either two passes over a re-created stream or a hand-rolled accumulator; `teeing` keeps it a single pass and a one-line result type.

### `collect` with three arguments, and the honest limit

`collect(supplier, accumulator, combiner)` is the collector-free escape hatch: a way to build a container out of primitive pieces when no `Collectors` factory matches what you need.

```java
List<String> result = words.stream()
    .collect(ArrayList::new, ArrayList::add, ArrayList::addAll);
```

That is also the point at which to ask whether a plain loop would be clearer. A single `groupingBy` or `toMap` reads better than the loop it replaces. A `groupingBy` whose downstream collector is itself a `mapping` of a `filtering` of a `reducing`, nested three deep to answer one question, does not; a `for` loop with an `if` and a `Map.computeIfAbsent` says the same thing in a shape the next reader does not have to unwind. Reach for the collector while it reads as one sentence, and reach for the loop once you are narrating.

## Practice

1. ▢ Predict what each line prints or throws.

   ```java
   List<String> names = List.of("Ann", "Ben", "Amy");
   Map<Character, String> byInitial = names.stream()
       .collect(Collectors.toMap(n -> n.charAt(0), n -> n));
   System.out.println(byInitial);
   ```

<details markdown="1"><summary>Check</summary>

It throws `IllegalStateException: Duplicate key A (attempted merging values Ann and Amy)`. `"Ann"` and `"Amy"` both start with `A`, and two-argument `toMap` treats a second value for the same key as an error rather than an overwrite, unlike a plain `HashMap.put` called twice with the same key.

</details>

2. ▢ This code compiles and runs. Find the bug.

   ```java
   List<Order> pending = new ArrayList<>();
   List<Order> snapshot = orders.stream()
       .filter(Order::isPending)
       .toList();
   pending.addAll(snapshot);
   pending.add(new Order());   // meant to append a manual entry to `pending`, not `snapshot`
   snapshot.add(new Order());  // then later, someone does this by mistake
   ```

<details markdown="1"><summary>Hint</summary>

Only one of the last two lines throws. Which list is `Stream.toList()` guaranteed not to let you change?

</details>

<details markdown="1"><summary>Check</summary>

`pending.add(...)` on line 4 is fine, since `pending` is a plain `ArrayList`. `snapshot.add(...)` on the last line throws `UnsupportedOperationException`, because `snapshot` came from `Stream.toList()`, which is unmodifiable. The bug is treating `snapshot` as if it were as writable as `pending`; if it needs to grow, collect it with `Collectors.toList()` or `Collectors.toCollection(ArrayList::new)` instead.

</details>

3. ▢ You are building `Map<String, Integer>` keyed by customer ID, summing order totals, from a stream where a customer ID can appear more than once. Plain `toMap(Order::customerId, Order::total)` throws on the second order from any repeat customer. Fix it.

<details markdown="1"><summary>Check</summary>

```java
Map<String, Integer> totalsByCustomer = orders.stream()
    .collect(Collectors.toMap(Order::customerId, Order::total, Integer::sum));
```

The three-argument overload's merge function runs exactly when a key repeats, and `Integer::sum` says what to do with the two values instead of treating the second one as an error. `Collectors.groupingBy(Order::customerId, Collectors.summingInt(Order::total))` reaches the same map by a different route, grouping first and reducing each group, and reads slightly better when "group, then reduce" is how you would say it out loud.

</details>

4. ▢ Predict the concrete runtime type `Collectors.groupingBy(String::length)` hands back, and whether that is something you should ever write code that depends on.

<details markdown="1"><summary>Check</summary>

`HashMap`, checked with `getClass()`. It is not something to depend on: the contract only promises a `Map`, and the concrete type is free to change between JDK versions because nothing documents it. Program against `Map<Integer, List<String>>` and use the three-argument overload with a map factory the moment you need a specific implementation, such as `TreeMap::new` for a sorted result.

</details>

5. ▢ A teammate writes this and asks whether it is idiomatic:

   ```java
   Map<Boolean, List<Order>> result = orders.stream()
       .collect(Collectors.groupingBy(Order::isPending,
           Collectors.mapping(Order::id,
               Collectors.filtering(id -> !id.isBlank(),
                   Collectors.toList()))));
   ```

   What would you say, and what would you write instead?

<details markdown="1"><summary>Check</summary>

Two things are worth flagging before the nesting. First, splitting into exactly two groups by a predicate is what `partitioningBy` is for, and it says that intent directly instead of leaving the reader to notice the classifier only ever returns `true` or `false`. Second, the map declares `Map<Boolean, List<Order>>` but the pipeline builds a list of `id` strings, so the code as shown does not even compile; that mismatch is exactly the kind of thing that gets lost inside three levels of downstream collectors. A version that both compiles and reads in one pass:

```java
Map<Boolean, List<String>> result = orders.stream()
    .collect(Collectors.partitioningBy(Order::isPending,
        Collectors.mapping(Order::id, Collectors.toList())));
```

The `filtering` step is gone because nothing upstream produces a blank ID to filter out; if it turns out to be needed, that is one more downstream layer to add back deliberately, not one to carry along "just in case".

</details>

## Real-world reps

- [ ] Collect the same stream both ways, `Collectors.toList()` and `Stream.toList()`, and try to `add` to each. Confirm which throws before you run it.
- [ ] Take any list of your own records with a field that repeats across at least two of them, and run it through two-argument `toMap` keyed on that field. Read the `IllegalStateException` message, then add the merge-function argument that makes it succeed.
- [ ] Group something you already have, files by extension or transactions by month, with `groupingBy`, and print `getClass()` on the result so the default map type stops being a guess.
- [ ] Tomorrow: find a loop in code you have that builds a `List` or `Map` by hand from something iterable, and decide whether a single collector says it better or whether the loop was already the right call.

## Going further

- [`Collectors`](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/stream/Collectors.html): every factory method named above, with the exact guarantees each one makes
- [`Stream`](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/stream/Stream.html): `toList()` and the terminal operations `collect` sits alongside
- [`Collector`](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/stream/Collector.html): the interface behind every factory, for the rare case a custom one earns its keep
- [Idiom and the library](../reference/idiom-and-library.md): the reference sheet for this stage
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
