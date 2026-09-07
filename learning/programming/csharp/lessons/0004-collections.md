---
title: "4. Collections"
description: "IEnumerable as the abstraction the rest of the arc leans on, and the dictionary lookup that throws where Java's map returns null"
type: lesson
---

# Lesson 4. Collections

**Mission link:** Two things start here. `IEnumerable<T>` is the interface LINQ is defined over, so stage 3 depends on this lesson; and the dictionary is where a Java habit produces a crash rather than a wrong answer.
**Primary source:** [Docs: "Collections and Data Structures", Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/standard/collections/)
**Prerequisites:** [Lesson 3](0003-basic-types-and-string-interpolation.md), [Lesson 2](0002-nullable-value-types.md)

## Warm-up

1. ▢ Is `System.Int32 count = 5;` different from `int count = 5;`?

<details markdown="1"><summary>Check</summary>

No. The keyword is an alias for the .NET type and the two are interchangeable, so both declarations produce the same type and the same compiled output. C# has no primitive-versus-wrapper split to import from Java.

</details>

2. ▢ Why should an interpolation hole never contain a method call that does work?

<details markdown="1"><summary>Check</summary>

Because an interpolated string is processed by a handler, and the documentation warns that a handler might not evaluate every interpolation expression under all conditions, so side effects might not occur. A logging call that decides not to emit the message is exactly such a condition, which makes the program's behaviour depend on the log level.

</details>

3. ▢ `int? a = 10;`. What do `a >= null` and `a < null` return, and what is the Java equivalent's behaviour?

<details markdown="1"><summary>Check</summary>

Both return `false` in C#. In Java, `Integer x = null; x > 5` throws a `NullPointerException`. So on that particular question C# is the quiet one and Java is the loud one. Hold that thought, because this lesson reverses it.

</details>

## Know this

**`IEnumerable<T>` is the floor, and almost everything later stands on it.** It exposes an enumerator supporting a simple iteration over a collection of a specified type, and it has exactly one method to implement, `GetEnumerator`, which returns an `IEnumerator<T>`. `List<T>`, `Dictionary<TKey,TValue>` and `Stack<T>` all implement it, and `foreach` uses that enumerator while hiding the machinery ([Collections and Data Structures](https://learn.microsoft.com/en-us/dotnet/standard/collections/)).

The sentence to carry forward is this one: any collection that implements `IEnumerable<T>` is considered a **queryable type** and can be queried with LINQ. So when LINQ arrives in stage 3, it is not a feature of `List<T>`; it is a set of operations defined over this interface, which is why the same query works on a list, a dictionary's values, an array, or something that generates values as you ask for them. Stage 4's `IAsyncEnumerable<T>` is the same idea again for values that arrive over time.

One detail to notice now and understand later: the interface is declared `IEnumerable<out T>`. That `out` is why a sequence of a derived type is usable as a sequence of its base type, and it gets explained properly in stage 2's generics lesson.

**Which container to reach for.** The guidance is blunt: in general, use the generic collections. Then the two you will write most days:

|You want|Reach for|Lookup|Add|
|---|---|---|---|
|Access items by index|`List<T>`|O(1)|O(1) amortised, O(n) worst case|
|Key/value pairs for quick lookup by key|`Dictionary<TKey,TValue>`|O(1)|O(1) amortised, O(n) worst case|

Retrieval from a dictionary is close to O(1) because it is implemented as a hash table, with the documented caveat that the speed depends on the quality of the hashing algorithm of the type used for `TKey`. And a rule that connects straight back to lesson 1: while an object is in use as a key, it must not change in any way that affects its hash. A struct key that copies on assignment is safe by construction; a mutable class used as a key is the hazard.

**The dictionary's four operations, and what each does when the key is absent.** This is the part worth memorising, because three of the four can fail and they fail differently.

|Operation|Key present|Key absent|
|---|---|---|
|`dict[key]` (read)|Returns the value|**Throws `KeyNotFoundException`**|
|`dict[key] = value` (write)|Replaces the value|Adds the pair|
|`dict.Add(key, value)`|**Throws `ArgumentException`**|Adds the pair|
|`dict.TryGetValue(key, out var v)`|Returns true, sets `v`|Returns false|

The documentation recommends `TryGetValue` specifically for the case where a program often has to try keys that turn out not to be in the dictionary, and calls it a more efficient way to retrieve values than testing first and reading afterwards.

**Now the reversal.** Java's `Map.get(key)` returns `null` for a missing key: quiet, and the null travels until something dereferences it. C#'s indexer throws at the point of the mistake. So the Java habit of writing `if (map.get(k) != null)` translates into `if (dict[k] != null)`, which does not guard anything, it just relocates the crash into the condition.

Put that beside warm-up 3 and the lesson generalises into something more useful than either fact. On nullable comparisons, C# is quiet where Java throws. On dictionary misses, C# throws where Java is quiet. Neither language is uniformly the strict one, so "C# is stricter" and "C# is more forgiving" are both wrong, and the only reliable move is to know what the specific API does on the absent case. That question, asked per API rather than per language, is the actual transferable skill in this lesson.

## Practice

1. ▢ `var counts = new Dictionary<string, int>();` and then `var n = counts["missing"];`. Predict what happens, and what the closest Java code would do.

<details markdown="1"><summary>Check</summary>

C# throws a `KeyNotFoundException` on that line. Java's `map.get("missing")` returns `null`, which for a `Map<String, Integer>` then throws a `NullPointerException` somewhere later when it is unboxed, possibly in a different method. Same mistake, two failure modes: C# fails at the point of the error with a message naming the problem, Java fails downstream with a message naming the symptom. The C# behaviour is easier to debug and harsher to discover, which is why the next item exists.

</details>

2. ▢ Rewrite this Java-shaped guard in idiomatic C#: `if (counts[key] != null) { Use(counts[key]); }`.

<details markdown="1"><summary>Hint</summary>

The condition is trying to answer a question. Ask which dictionary member answers that question without reading the value first.

</details>

<details markdown="1"><summary>Check</summary>

`if (counts.TryGetValue(key, out var n)) { Use(n); }`.

The original is wrong twice. It throws on a missing key inside the condition, so the guard never gets to protect anything, and for a `Dictionary<string, int>` the comparison against null does not even mean what it looks like, since `int` is not nullable. It also reads the dictionary twice in the success path. `TryGetValue` answers "is it there" and produces the value in one operation, which is what the documentation recommends when misses are expected. Where a fallback value is all you need, `GetValueOrDefault(key)` is the shorter form.

</details>

3. ▢ When would you write `dict.Add(key, value)` rather than `dict[key] = value`, given that both add the pair when the key is absent?

<details markdown="1"><summary>Check</summary>

When a duplicate key means a bug. `Add` throws an `ArgumentException` on a key that is already present, while the indexer silently replaces the existing value. So the choice is a statement about your expectations: `Add` says "this key is new and if it is not, something upstream is wrong", and the indexer says "last write wins, by design". Reaching for the indexer everywhere is comfortable and throws away a check the type was offering you for free, which is the habit this arc keeps naming: taking the convenient call and losing the assertion that came with the strict one.

</details>

4. ▢ A method is declared `void Report(IEnumerable<Order> orders)`. Name three different arguments you could pass it, and say what accepting the interface rather than `List<Order>` buys.

<details markdown="1"><summary>Check</summary>

A `List<Order>`, an `Order[]` array, the `Values` of a `Dictionary<string, Order>`, the result of a LINQ query, or anything else implementing the interface, including something that produces orders one at a time rather than holding them all.

What it buys is twofold. The method stops caring how the caller stored the data, so callers do not have to copy into a list to satisfy the signature. And it declares what the method actually needs, which is to enumerate once, forwards, rather than to index, count or mutate. Taking `List<Order>` would claim the right to do all three. This is also why LINQ is defined over `IEnumerable<T>`: a queryable type is anything that can be enumerated, and stage 3 gets that for free from the choice made here.

</details>

5. ▢ Which claim about reading a missing key from a `Dictionary` is correct?

   - a) A dictionary indexer returns the default value for a missing key, like Java
   - b) A dictionary indexer throws KeyNotFoundException for a missing key, so prefer TryGetValue instead
   - c) A dictionary indexer returns null for a missing key, which nullable types handle
   - d) A dictionary indexer adds the missing key on read and returns its default

<details markdown="1"><summary>Check</summary>

**b)** The read indexer throws, and `TryGetValue` is the documented answer when misses are expected. (a) confuses the indexer with `GetValueOrDefault`, which does return the default, and it is not what Java does either. (c) is the Java model imported wholesale, and it cannot even be expressed for a value-type value, since `Dictionary<string, int>` has no null to return. (d) describes a defaultdict from another language entirely; nothing in C# mutates a dictionary on read.

</details>

## Real-world reps

- [ ] Find a dictionary read in C# you have access to, or in a sample project. Decide whether a missing key is possible there, and whether the code would throw or handle it.
- [ ] Find a method signature taking a concrete collection type. Work out whether it indexes, counts or mutates, and if it does none of those, whether `IEnumerable<T>` would have been the honest parameter type.
- [ ] Tomorrow: write down what your usual language's map does on a missing key, and what it does on a duplicate insert. Put the two answers beside C#'s four dictionary operations, and note which of your habits does not survive the move.

## Going further

- [Docs: "Collections and Data Structures", Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/standard/collections/)
- [API: "Dictionary<TKey,TValue>", Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/api/system.collections.generic.dictionary-2)
- [API: "IEnumerable<T>", Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/api/system.collections.generic.ienumerable-1)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
