---
title: 5. Arrays and Collections
description: Arrays are covariant and fixed, and three list factories differ in ways their names hide
type: lesson
---

# Lesson 5. Arrays and Collections

**Mission link:** Choosing a collection is a decision made in every method that holds more than one thing, and the three ways to build an unmodifiable list are not interchangeable. Knowing which is which is the difference between a defensive copy and a shared view.
**Primary source:** [The Collections Framework, dev.java](https://dev.java/learn/api/collections-framework/)
**Prerequisites:** [Lesson 1](0001-references-are-values.md), [Lesson 3](0003-equals-and-hashcode.md)

## Warm-up

1. ▢ What does `List.copyOf(items)` give you that `items` did not, and what does it reject?

<details markdown="1"><summary>Check</summary>

An unmodifiable copy, so the caller's later mutations are invisible. It rejects a null list and null elements.

</details>

2. ▢ Why is a mutable object a poor `HashMap` key?

<details markdown="1"><summary>Check</summary>

The hash is computed at insertion. Change a field that `hashCode` reads and the entry stays in the old bucket, so lookups miss it.

</details>

## Know this

An array is a fixed-length object with a covariant type. A collection is an interface with several implementations and a length that usually is not fixed. The two are not variations of one idea.

### Arrays are covariant, and that is a hole in the type system

```java
String[] names = {"a"};
Object[] objects = names;       // compiles: String[] is an Object[]
objects[0] = 42;                // ArrayStoreException at run time
```

Generics are **invariant** precisely to close this hole: `List<Object> l = new ArrayList<String>()` does not compile, so the corresponding mistake is caught at compile time instead of thrown at run time.

Arrays also have a fixed length, no useful `toString`, and `equals` by identity. `Arrays.toString(a)` and `Arrays.equals(a, b)` exist because of that last pair. Use an array when an API hands you one, when you need primitives without boxing, or when profiling says so. Otherwise use a `List`.

### The collection interfaces

`Collection` splits into `List` (ordered, duplicates allowed), `Set` (no duplicates), and `Queue` and `Deque` (ends matter). `Map` is **not** a `Collection`: it has no `add`, and its `values()` is a view rather than a collection it contains.

| Need | Use | Notes |
|---|---|---|
| ordered, indexed, growable | `ArrayList` | the default; `LinkedList` almost never wins |
| no duplicates, no order guarantee | `HashSet` | needs correct `equals` and `hashCode` |
| no duplicates, insertion order | `LinkedHashSet` | predictable iteration, small extra cost |
| no duplicates, sorted | `TreeSet` | uses ordering, not `equals`, see lesson 6 |
| key to value | `HashMap` | the default |
| key to value, insertion order | `LinkedHashMap` | also the basis of a simple cache |
| key to value, sorted by key | `TreeMap` | rejects a null key under natural ordering |
| stack or queue | `ArrayDeque` | prefer over `Stack` and over `LinkedList` |

Declare the interface and construct the implementation: `List<Order> orders = new ArrayList<>();`. That keeps the choice of implementation a detail rather than part of the signature.

### Three unmodifiable lists that behave differently

```java
List<String> a = List.of("x", "y");                    // immutable, rejects null
List<String> b = Collections.unmodifiableList(source); // a VIEW of source
List<String> c = List.copyOf(source);                  // an immutable copy
List<String> d = Arrays.asList("x", "y");              // FIXED-SIZE, writes through
```

The differences are the whole point:

- `b` is a window. Mutating `source` changes what `b` shows, so it protects the recipient from writing and not from change.
- `c` is a snapshot. Later mutations of `source` are invisible.
- `d` is neither: `add` and `remove` throw `UnsupportedOperationException`, while `set` succeeds and writes into the backing array.

So "returns an unmodifiable list" means three different things depending on which one you wrote, and only `copyOf` is a defensive copy.

Two smaller traps in the same family:

```java
Arrays.asList(new int[]{1, 2, 3});      // a List<int[]> with ONE element
list.remove(1);                          // removes INDEX 1
list.remove(Integer.valueOf(1));         // removes the VALUE 1
```

The `remove` pair is an overload chosen by static type, so on a `List<Integer>` the two lines do entirely different things and both compile.

### Modifying while iterating

```java
for (String s : list) {
    if (s.isBlank()) list.remove(s);     // ConcurrentModificationException
}
```

The iterator notices the structural change and throws, on the next step rather than at the removal. It is a fail-fast check, not a guarantee: it is documented as best effort, so never write code that relies on catching it.

Three correct forms:

```java
list.removeIf(String::isBlank);                 // the one to reach for

Iterator<String> it = list.iterator();          // when the condition needs more
while (it.hasNext()) {
    if (it.next().isBlank()) it.remove();
}

for (String s : List.copyOf(list)) { ... }      // iterate a snapshot instead
```

The same applies to maps: remove through `entrySet().iterator()`, or use `values().removeIf(...)`, and never through the map while a for-each is running over it.

## Practice

1. ▢ Which line fails, at compile time or at run time?

   ```java
   Object[] objects = new String[1];
   objects[0] = 42;
   List<Object> list = new ArrayList<String>();
   ```

<details markdown="1"><summary>Check</summary>

Line 2 throws `ArrayStoreException` at run time. Line 3 fails at compile time.

Arrays are covariant, so the compiler accepts the assignment on line 1 and the check is deferred to the store. Generics are invariant, so the analogous mistake cannot be written at all. Line 3 is the type system doing the job the array version cannot.

</details>

2. ▢ Predict each of the four.

   ```java
   List<String> source = new ArrayList<>(List.of("a"));
   List<String> view = Collections.unmodifiableList(source);
   List<String> copy = List.copyOf(source);
   source.add("b");
   System.out.println(view);
   System.out.println(copy);
   view.add("c");
   copy.add("d");
   ```

<details markdown="1"><summary>Hint</summary>

One of these two unmodifiable lists knows about `source` after the fact, and one does not.

</details>

<details markdown="1"><summary>Check</summary>

`[a, b]`, then `[a]`, then `UnsupportedOperationException` from `view.add`. The last line never runs, and would have thrown the same exception.

`unmodifiableList` is a view over `source`, so the `add` on line 4 shows through. `copyOf` took a snapshot. Both refuse writes through themselves, which is the only thing their names have in common.

</details>

3. ▢ You return a collection from a method and must guarantee the caller cannot change your internal state, now or later. Which do you write?

   - a) `return Collections.unmodifiableList(items);`
   - b) `return List.copyOf(items);`
   - c) `return Arrays.asList(items.toArray(new String[0]));`
   - d) `return new ArrayList<>(items);`

<details markdown="1"><summary>Check</summary>

**b)** `return List.copyOf(items)`.

Option a stops the caller writing and lets them observe your later changes, which is sometimes what you want and is not what was asked. Option c is fixed-size, so the caller can still `set` an element. Option d is a copy the caller may freely modify, which protects your state and misleads anyone who assumes the result is stable.

</details>

4. ▢ On a `List<Integer>` holding `[10, 20, 30]`, predict both lines.

   ```java
   list.remove(1);
   list.remove(Integer.valueOf(30));
   ```

<details markdown="1"><summary>Check</summary>

The first removes index 1, leaving `[10, 30]`. The second removes the value `30`, leaving `[10]`.

`List` has both `remove(int)` and `remove(Object)`, and the compiler picks by static type. This is the strongest single argument for not writing `List<Integer>` where a domain type would do.

</details>

5. ▢ Rewrite this loop correctly, and say why the original throws on the iteration after the removal rather than at the removal itself.

   ```java
   for (Order o : orders) {
       if (o.isCancelled()) orders.remove(o);
   }
   ```

<details markdown="1"><summary>Check</summary>

`orders.removeIf(Order::isCancelled);`

The removal itself only increments a modification counter on the list. The iterator compares that counter against the value it recorded when it was created, and it does that comparison on the next call to `next()` or `hasNext()`. So the throw happens one step later, which is why the stack trace points at the loop rather than at the line that caused it.

An aside worth knowing rather than relying on: removing the second-to-last element can make the loop finish without throwing at all, because `hasNext()` compares sizes and happens to return false. The check is documented as best effort for exactly this reason.

</details>

## Real-world reps

- [ ] Build the covariance example and watch `ArrayStoreException` appear. Then try the generic version and read the compiler error. The pair is the clearest demonstration of what generics bought.
- [ ] Reproduce all four rows of the unmodifiable-list comparison in one file, including the view seeing a later `add`. Then decide which one your own code has been returning.
- [ ] Tomorrow: find a method in code you know that returns a collection field directly. Decide whether it should be a copy, a view, or left alone, and be able to defend the answer.

## Going further

- [The Collections Framework](https://dev.java/learn/api/collections-framework/): the interfaces and implementations, with the trade-offs
- [`Collection`](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/Collection.html): the contract every implementation is judged against, including optional operations
- [`Arrays`](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/Arrays.html): `asList`, `toString`, `equals` and the sorting overloads
- [Trail: Collections](https://docs.oracle.com/javase/tutorial/collections/): the older tutorial, still the clearest on iteration order and fail-fast behaviour
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
