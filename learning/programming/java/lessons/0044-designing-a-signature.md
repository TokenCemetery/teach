---
title: 44. Designing a Signature
description: The parameter and return types decide what callers can do, and most of the damage is done at the boundary
type: lesson
---

# Lesson 44. Designing a Signature

**Mission link:** Every caller who depends on your class depends on its signatures, not on the method bodies behind them, so the parameter and return types you choose are the interface you are stuck defending in production long after the implementation has been rewritten twice.
**Primary source:** [Effective Java, Joshua Bloch](https://openlibrary.org/isbn/9780134685991)
**Prerequisites:** [Lesson 43](0043-what-counts-as-breaking.md), [Lesson 13](0013-generics-and-erasure.md)

## Warm-up

Lesson 43 changed `Config.items()` from returning `List<String>` to returning `ArrayList<String>`, and running the old class files against the new library, unrecompiled, threw `NoSuchMethodError`. Now imagine you are designing `Config` from scratch, before a single caller exists. Which return type should you choose, `List` or `ArrayList`, and does the reasoning behind that choice have anything to do with how you would choose a parameter type?

<details markdown="1"><summary>Check</summary>

`List`, and the reasoning is the mirror image of a parameter choice, not the same reasoning applied twice. A parameter type is a minimum you demand of the caller, so the more general choice costs the caller nothing and leaves you free to widen it later. A return type is a maximum you promise the caller, so the more general choice is the one that keeps your own future free, because lesson 43 already measured what committing to `ArrayList` costs you if you ever want to change your mind. Choosing `List` up front is not caution for its own sake, it is refusing to make a promise you have not been asked to make.

</details>

## Know this

### The signature is the part callers cannot work around

Six stages of writing methods, and every one of them ended at a body. This lesson stops at the line above it, because that line is the only part of a class a caller depends on. They cannot see your fields, your loops, or which collection implementation you picked. They see three things: what you demand in the parameters, what you promise in the return type, and what exceptions you declare, and lesson 15 already covered the last of those. Get the body wrong and you can fix it tomorrow, silently. Get the signature wrong and lesson 43 already showed the two ways that plays out: a source-incompatible change breaks the build the moment anyone rebuilds, and a binary-incompatible one sits quietly until old class files hit it and throw `NoSuchMethodError` or `AbstractMethodError` nowhere near the actual change. A signature is genuinely hard to walk back, which is why it deserves the deliberate attention the rest of this lesson gives it.

### Parameters: accept the most general type you can actually use

A parameter type is a demand: the caller must show up with at least this much, or the compiler will not let the call happen at all. Every demand you drop is a caller you no longer turn away for free. A method that only ever iterates its argument and reads elements has no business demanding `ArrayList`:

```java
static int totalLength(Collection<String> words) {
    int total = 0;
    for (String w : words) {
        total += w.length();
    }
    return total;
}
```

Written against `Collection<String>`, this accepts a `List`, a `HashSet`, a `TreeSet`, or the result of `Map.values()`, anything that can hand back an iterator. Written against `ArrayList<String>` it would reject all of those unless the caller first copied their data into an `ArrayList` purely to satisfy a demand the body never needed. Lesson 13 already gave you the vocabulary for pushing this further with generics, `Collection<? extends CharSequence>` where you only read characters, and the same PECS reasoning that told you when a wildcard should produce values and when it should consume them.

That is one half of the advice, and stated alone it turns into the standard overapplied slogan, "always program to the most general type", which is not what this lesson is teaching. The honest counterweight: generalising a parameter past what the method needs costs the caller nothing, but it costs you the ability to rely on anything beyond that weaker type's contract, and a parameter type is also documentation, not just a filter. A method that demands `Collection` tells every reader "I do not care about order or random access, do not read anything into either one." If the contract genuinely depends on order, demanding `Collection` when you mean `List` does not make the method more flexible, it makes the signature lie about what it needs, and the caller finds out the hard way.

The test to apply is mechanical: look at every call your implementation actually makes on the parameter, and find the weakest type that still declares all of them. If the body only calls `iterator()`, `size()`, `stream()`, or a `for` loop over it, `Collection` is the honest type. If it calls `get(int)`, you need `List`, and wanting to be general does not change that the method would break on a `Set`. The moment you cast the parameter back down inside the method, or write an `instanceof` check to recover behaviour the declared type does not offer, the signature is telling you it generalised past what it can actually use.

### Return types: return the most specific type that is part of your contract

Turn the same question around for a return type and the answer reverses, and the warm-up already stated why: a parameter type is a demand, and loosening a demand later is safe, because everyone who satisfied the stricter version still satisfies the looser one. A return type is a promise, and loosening a promise later takes away something a caller may already rely on. Lesson 43 measured exactly how unforgiving that promise is. Narrowing `Config.items()` from `List<String>` to `ArrayList<String>` compiled cleanly against the old source, because `ArrayList<String>` satisfies `List<String>`, and that same change threw `NoSuchMethodError` at every caller who had not rebuilt, because the descriptor baked into their class files, `()Ljava/util/List;`, no longer existed. Widening the return type back would not undo that either: the descriptor changes again, so it is binary-incompatible the same way, and it can be source-incompatible too if a caller had come to depend on an `ArrayList`-only method the wider type never promised. A return type, once released, is close to fixed for the working life of the API, harder to revisit in either direction than anything else in the signature.

That is why the specific type you commit to should describe an actual guarantee, not today's implementation. If every caller can rely on order and positional access, promise `List`. If nothing about the contract needs that much, promise `Collection`, because promising more than the contract needs only removes flexibility from you for no caller's benefit. What a return type should almost never be is the concrete class behind it purely because that is what today's implementation builds: `ArrayList`, `HashMap`, `LinkedList` name an implementation, not a contract, and lesson 43's experiment is the receipt for what it costs to have promised one and changed your mind.

### What not to return

Three shapes of return value cause damage far out of proportion to how easy they are to write.

`null` for absence. Lesson 16 taught the fix and its limits: `Optional<T>` exists for a return value whose absence is normal, and belongs in exactly one place, a return type, which is why that lesson spent as much time on the four places it does not belong, a field, a parameter, a collection's element type, and anything serialised. A method that returns `null` for "not found" hands the caller a value that type-checks identically to one that means something, and the only way to tell them apart is to remember to check, every time, forever.

Arrays where a collection is meant. Lesson 1 covered why arrays are the exception to Java's variance rules and why their length is fixed at construction, and both properties turn into liabilities once an array is a public return type: a caller gets no protection against writing past what was promised, cannot resize it, and can be surprised by `ArrayStoreException` if the element type participates in the covariance lesson 1 demonstrated. A `List` says everything a caller needs from its type alone, at no extra cost.

A mutable internal collection, returned by reference. This is lesson 14's defensive copy, seen from the far side of the boundary. A getter that hands back the field it holds is not returning data, it is handing the caller a key to the object's internals:

```java
class Roster {
    private final List<String> names = new ArrayList<>();
    List<String> namesLeaky() { return names; }
    List<String> namesSafe() { return List.copyOf(names); }
}
```

Run against a `Roster` seeded with two names, `roster.namesLeaky().clear()` genuinely empties the roster's own field, because the caller was never holding a copy, they were holding the field. The same call against `namesSafe()` throws `UnsupportedOperationException`, because `List.copyOf` returns an unmodifiable copy the caller cannot reach back through. One line separates "the method exposed private state" from "the method returned an answer", and the return type gives the caller no warning about which one they are holding.

### Overloading, and why it is usually a trap

Overload resolution, which of several same-named methods a call invokes, is decided once, at compile time, by the compiler looking at the static, declared type of each argument. It has nothing to do with what object the variable holds at run time, and that mismatch is where the trap lives. Take three overloads that look reasonable individually:

```java
static String classify(Set<?> s) { return "Set"; }
static String classify(List<?> l) { return "List"; }
static String classify(Collection<?> c) { return "Unknown Collection"; }
```

Called from a loop over an array declared `Collection<?>[]`, holding a `HashSet`, an `ArrayList`, and the view returned by `Map.values()`, the honest expectation is `Set`, `List`, `Unknown Collection`. Running it says otherwise:

```text
Unknown Collection
Unknown Collection
Unknown Collection
```

Every call resolves to the third overload, because the loop variable's declared type is `Collection<?>`, and the compiler chose the matching overload once, at compile time, with no regard for which concrete object turned up later. Declaring the loop variable with `var` does not change this, since `var` infers the same declared type the array already carries: still three lines of `Unknown Collection`. Overriding, which class's implementation of a method runs, is resolved dynamically by the runtime class, the behaviour most people expect first. Overloading, which same-named method runs, is resolved statically by the declared type, and the two disagreeing with each other's reputation is why this surprises people who have never had it explained.

The rule that follows is not "never overload", it is narrower: when two operations do genuinely different things, give them different names, so the reader typing the call chooses, not a compiler resolving types the reader may not be thinking about. Reserve overloading for cases that are unambiguously the same operation over convertible argument types, the way `StringBuilder.append(String)`, `append(int)`, and `append(char)` are all "append this, converted to text" and never disagree regardless of which one resolves. `classify` fails that test because the three overloads are not one operation with convertible arguments, they are three different answers that only look like one method because they share a name.

### Varargs, and the two traps in the signature

A trailing parameter written `T... name` is sugar for a parameter of type `T[]`, and every call site that supplies its arguments as a list of separate values, rather than an existing array, allocates a fresh array to hold them:

```java
static void identity(int... items) {
    System.out.println(System.identityHashCode(items));
}
int[] existing = {1, 2, 3};
identity(existing);   // no new array: the compiler passes existing straight through
identity(1, 2, 3);    // a new array is allocated to hold 1, 2, 3
```

Passing an existing array through directly costs nothing extra, because the compiler recognises it already has the exact type needed and hands it over unchanged. Passing a literal list of values costs one array allocation per call, invisible at the call site, and it matters exactly as much as any other per-call allocation: negligible on a rarely-called method, worth knowing about on a hot path, and never worth avoiding varargs over on a guess rather than lesson 41's benchmark.

The second trap is sharper, because it changes what compiles, not just what allocates. A varargs parameter accepts zero arguments unless the signature says otherwise, because an empty array is a completely ordinary array:

```java
static int sum(int... nums) {
    int total = 0;
    for (int n : nums) total += n;
    return total;
}
sum();          // compiles, returns 0
sum(1, 2, 3);   // compiles, returns 6
```

That is correct for `sum`, where zero terms summing to zero is the honest answer. It is a bug waiting to happen for an operation with no honest answer for the empty case, `max` among them: what should the maximum of nothing be? Writing `static int max(int... nums)` lets `max()` compile and silently return whatever value an empty loop leaves the accumulator holding, a wrong answer with no complaint from the compiler. The fix is a parameter list that says a first value is not optional:

```java
static int max(int first, int... rest) {
    int m = first;
    for (int n : rest) if (n > m) m = n;
    return m;
}
```

`max(3)` now compiles and returns 3. `max()` fails to compile, and the compiler's own words say exactly why:

```text
error: method max in class MaxDemo cannot be applied to given types;
        System.out.println("max() = " + max());
                                        ^
  required: int,int[]
  found:    no arguments
  reason: actual and formal argument lists differ in length
```

The signature decided the question the implementation would otherwise have had to decide with a runtime check, and decided it at compile time, for every caller, permanently.

### Parameter lists that have got too long

A parameter list earns scrutiny well before it earns a rewrite, and the honest options are three, not one. The first, and usually the right default, is a parameter object, which lesson 8 already gave you the cheapest possible way to build:

```java
record MessageRequest(String to, String subject, String body, boolean urgent, boolean html) {}
void send(MessageRequest request) { ... }
```

A five-argument call with two unlabelled `boolean`s is a call site nobody can read back without checking the declaration, since `send(to, subject, body, true, false)` gives no reader a way to tell which flag is which. `send(new MessageRequest(to, subject, body, urgent, html))` names both, and lesson 43's return type reasoning applies here too: a record used only as a parameter type is far cheaper to add a component to later than a bare parameter list is to insert one into.

The second option is a builder, and the tell for reaching past a record to it is what most of the parameters are doing, not their count: when most are optional with a sensible default, or you find yourself writing several overloads to cover which subset a caller supplied, a record still forces every caller to state every component, while a builder lets a caller state only what differs and construct incrementally.

The third option is worth checking before reaching for either container: a parameter list that has grown long because it naturally splits into two groups never needed together is not a signature problem, it is the method doing two things under one name. Bundling the groups into one parameter object only hides that behind a tidier call. Splitting the method into two shorter signatures is usually the option the container was avoiding.

### Nullability as part of the signature

Java's syntax has no way to say a reference parameter or return value must not be `null`, but the signature can still say it, through three tools this stage already taught separately and is now asking you to choose between deliberately. `Optional<T>` as a return type says absence is normal, and lesson 16 already drew the line for where that expectation belongs, a return type and nowhere else. `Objects.requireNonNull` on a parameter, at the moment a constructor or method begins, turns silent acceptance of `null` into a documented, immediate failure at the boundary, worth doing because the alternative, lesson 4 showed, is a `NullPointerException` three calls deeper, pointing at innocent code that only inherited someone else's `null`. Where neither tool fits, documentation is what is left, stating in prose whether `null` is accepted or returned, the honest choice for cases the other two do not cover, such as matching an existing convention like `Map.get` returning `null` for an absent key.

What ties the three together is where the decision gets made, not which you pick. Deciding nullability once, at the outer boundary where a signature is public and a caller is unknown, is the same discipline lesson 4 taught for construction, applied to the wider surface of a signature. Everything behind that boundary can then assume the guarantee holds, and every caller in front of it knows exactly what they may hand over and rely on getting back.

## Practice

1. ▢ `classify(Set<?>)`, `classify(List<?>)`, and `classify(Collection<?>)` are called from a loop declared `for (Collection<?> c : collections)`. Predict what changing the loop header to `for (var c : collections)` does to the printed output, and say why.

<details markdown="1"><summary>Check</summary>

Nothing changes: all three calls still print `Unknown Collection`. `var` infers its type from the array's declared component type, <code>Collection&lt;?&gt;</code>, the same type the explicit declaration already had, so the compiler resolves the overload the same way both times. `var` is inference of a static type, not a request for dynamic dispatch, and overload resolution only ever looks at the static type.

</details>

2. ▢ `identity(int... items)` prints `System.identityHashCode(items)`. Predict whether `identity(existing)`, where `existing` is a variable of type `int[]` already holding three values, allocates a new array, and predict the same for `identity(1, 2, 3)`.

<details markdown="1"><summary>Hint</summary>

Ask what the compiler has to build to satisfy the parameter's declared type, `int[]`, in each case, and whether it already has something of exactly that type sitting at the call site.

</details>

<details markdown="1"><summary>Check</summary>

`identity(existing)` allocates nothing new: the argument already has the exact array type the varargs parameter desugars to, so it passes straight through, confirmed by `items` printing the same identity hash code as `existing`. `identity(1, 2, 3)` allocates a fresh three-element array, since no existing array sits at that call site to reuse, confirmed by a different identity hash code each run.

</details>

3. ▢ `max(int first, int... rest)` requires at least one argument. Predict which of `max(3)` and `max()` compiles, and name the category of compiler error the other one produces.

<details markdown="1"><summary>Check</summary>

`max(3)` compiles and returns 3, because `first` is satisfied and `rest` is the empty array. `max()` fails with a "cannot be applied to given types" error, reason "actual and formal argument lists differ in length", because nothing satisfies the mandatory `first`. Writing that value outside the varargs turns a wrong runtime answer into a compile-time refusal.

</details>

4. ▢ A public method is declared `void register(ArrayList<String> names)` and returns `List<String>` from a second method on the same class. Applying this lesson's separate tests for parameters and for return types, predict which of the two type choices is the design smell, and which one needs no change.

<details markdown="1"><summary>Check</summary>

The parameter is the smell. `ArrayList<String>` demands an implementation the method almost certainly never needs, since registering names only requires iterating them, which `Collection<String>` already supports, and forces every caller holding a `List`, a `Set`, or a stream collector's result to convert first for no benefit. `List<String>` as the return type needs no change: it already names the most specific type describing a real guarantee, ordered access, without naming a concrete implementation the class would be stuck with under lesson 43's rule.

</details>

5. ▢ `Roster` has `namesLeaky()`, which returns its private `List<String>` field directly, and `namesSafe()`, which returns `List.copyOf` of the same field. Predict the result of calling `.clear()` on each returned list, and what that result means for the field back inside `Roster`.

<details markdown="1"><summary>Check</summary>

`roster.namesLeaky().clear()` succeeds and empties the roster's own field, since the caller was holding a reference to that exact object, not a copy. `roster.namesSafe().clear()` throws `UnsupportedOperationException`, leaving the field unaffected, since `List.copyOf` handed back an unmodifiable copy. The return type in both cases is `List<String>`, so nothing in the signature tells a reader which behaviour they are getting; only the implementation decides it.

</details>

## Real-world reps

- [ ] Take one method you maintain whose parameter type is a concrete class, such as `ArrayList` or `HashMap`, check every call the body makes against it, and widen the parameter to the weakest interface that still supports them all.
- [ ] Take one method you maintain that returns `null` for an absent result, rewrite the return type as `Optional`, and update its callers to use `orElse`, `orElseThrow`, or `map` in place of the null check.
- [ ] Find a getter that returns a mutable field directly, the way `namesLeaky` does, change it to return a defensive copy or an unmodifiable view, and confirm a caller can no longer mutate the field through the result.
- [ ] Find two overloaded methods in a project you maintain, or a library you call, and decide whether they are the same operation over convertible types or two different operations sharing a name by accident.
- [ ] Tomorrow: pick one signature with four or more parameters from code you own, decide whether a parameter object, a builder, or splitting the method fits best, and say out loud why, before writing a line of the change.

## Going further

- [Kinds of Compatibility, OpenJDK Compatibility and Specification Review](https://wiki.openjdk.org/display/csr/Kinds+of+Compatibility): the source and binary distinction lesson 43 built and this lesson leans on for why return types are hard to revisit
- [The Java Language Specification, Java SE 25, chapter 15, Expressions](https://docs.oracle.com/javase/specs/jls/se25/html/jls-15.html): the formal rule for how overload resolution is decided from argument types, section 15.12
- [Judgment](../reference/judgment.md): the stage 7 reference sheet
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
