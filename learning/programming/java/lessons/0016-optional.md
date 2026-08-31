---
title: 16. Optional
description: A return type that makes absence part of the contract, and the four places it does not belong
type: lesson
---

# Lesson 16. Optional

**Mission link:** A reviewer flags `Optional` as often for where it is missing as for where it is misused, since it is exactly as useful as a return type as it is harmful as a field or a parameter, and telling those apart is precisely what this stage is for.
**Primary source:** [`Optional`, Java SE 25 API](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/Optional.html)
**Prerequisites:** [Lesson 4](0004-null.md), [Lesson 15](0015-exceptions.md)

## Warm-up

1. ▢ A resource's body throws, and its `close()` also throws. Which exception does the caller's `catch` see, and what happens to the other one?

<details markdown="1"><summary>Check</summary>

The body's exception is the one the caller sees. The `close()` failure is attached to it as a suppressed exception, retrievable with `getSuppressed()`, rather than lost. A hand-written `finally` block whose own `close()` call throws would have replaced the body's exception with the close failure instead, discarding the original with no record it ever happened.

</details>

2. ▢ A record `Team { List<String> members }` copies `members` in its compact constructor, yet `team.members().add("X")` still succeeds. Why, and what is the one-line fix?

<details markdown="1"><summary>Check</summary>

The compact constructor's copy only stops the caller's original list from reaching in. The generated accessor still hands back that internal copy by reference, so mutating through it still works. The fix overrides the accessor to return `List.copyOf(members)` instead of the field itself.

</details>

## Know this

### What it is for

```java
Optional<String> middleName(Person p) { ... }
```

`Optional<T>` is a container holding either exactly one non-null value or none, added in Java 8. It exists for a return value whose absence is a normal outcome, not an exceptional one: a person genuinely may have no middle name, and the signature says so directly. `null` cannot say that, because every reference type can already be `null`, so a caller has no way to tell from the signature alone which methods mean it and which would rather throw. `Optional` moves that decision into the type, where the compiler can make the caller notice.

### `of`, `ofNullable`, `empty`

```java
Optional.of(null);
```

```text
java.lang.NullPointerException
```

`Optional.of` throws immediately, with no message, if the argument is `null`. Use it when a `null` there would already be a bug you want surfaced at the source rather than three calls later. `Optional.ofNullable` is the version for a value that may genuinely be absent, such as wrapping the result of `Map.get`: it returns `Optional.empty()` for a `null` argument instead of throwing. `Optional.empty()` returns the same shared empty instance every time, so `Optional.empty() == Optional.empty()` is true, though relying on that identity rather than calling `isPresent()` would be its own small piece of unidiomatic Java.

### The null check wearing a costume

```java
if (opt.isPresent()) {
    System.out.println(opt.get());
}
```

This compiles, reads like progress, and is a `null` check with extra ceremony: it still branches on presence and still calls a method that throws if you get the branch wrong. Nothing here is safer than `if (x != null)`. What `Optional` is for is not checking presence and then unwrapping, it is describing what to do with the value without ever asking the question:

```java
opt.ifPresent(System.out::println);
```

`ifPresent` runs the action only when a value exists and never involves `get()` at all. Reach for `isPresent()` plus `get()` only when every alternative below genuinely fails to fit, which in practice is close to never.

### `orElse` against `orElseGet`: the eager-argument trap

```java
Optional<String> present = Optional.of("value");
String a = present.orElse(slowDefault());
```

```text
computing default
result: value
```

`orElse` evaluates its argument unconditionally, before checking whether the `Optional` holds a value, because Java evaluates a method's arguments before calling it. `slowDefault()` ran and printed even though its result was thrown away. Swap in `orElseGet`, which takes a `Supplier` instead of a value:

```java
String b = present.orElseGet(OrElseEager::slowDefault);
```

```text
result: value
```

No output before `result:` this time: the supplier is only invoked when the `Optional` is empty. Passing a literal or an already-computed value to `orElse` costs nothing extra, but passing a call that queries a database, builds a collection, or does anything else with a real cost belongs behind `orElseGet` instead, or that cost is paid on the common path where the value was there all along.

### `map` against `flatMap`: the nested-`Optional` trap

```java
record Person(String name, Optional<String> nickname) {}
Person p = new Person("Ann", Optional.of("Annie"));

Optional<Optional<String>> nested = Optional.of(p).map(Person::nickname);
Optional<String> flat = Optional.of(p).flatMap(Person::nickname);
```

```text
map result: Optional[Optional[Annie]]
flatMap result: Optional[Annie]
```

`map` applies a function that returns a plain value and wraps whatever comes back, so mapping to a method that already returns an `Optional` produces an `Optional` inside an `Optional`, which is rarely what anyone wants and has to be unwrapped twice. `flatMap` applies a function that itself returns an `Optional` and does not wrap the result a second time, flattening the two layers into one. The rule is mechanical: if the function you are handing over already returns `Optional`, reach for `flatMap`.

### `filter`, `or`, `stream`

```java
Optional.of(15).filter(a -> a >= 18);   // Optional.empty
Optional.of(21).filter(a -> a >= 18);   // Optional[21]

Optional<Integer> empty = Optional.empty();
empty.or(() -> Optional.of(-1));         // Optional[-1]

Optional.of(3).stream().toList();               // [3]
Optional.<Integer>empty().stream().toList();     // []
```

Every line above prints exactly the value shown in the comment when run. `filter` turns a present `Optional` into an empty one when the predicate fails, and leaves an already-empty one alone; it never throws on a failed test, which is the point. `or` supplies a fallback `Optional` lazily, the same eagerness rule as `orElseGet` but returning another `Optional` rather than a bare value. `stream()` turns the `Optional` into a stream of zero or one elements, which is the bridge for folding a value that might be absent into a larger pipeline without an `if`.

### `orElseThrow`, `ifPresent`, `ifPresentOrElse`

```java
empty.orElseThrow(() -> new IllegalStateException("no age on file"));
```

```text
threw: no age on file
```

The one-argument `orElseThrow` throws whatever the supplier builds, which is where a domain-specific exception belongs instead of a generic one. The zero-argument overload throws a fixed exception instead:

```java
Optional.empty().orElseThrow();
```

```text
java.util.NoSuchElementException: No value present
```

`ifPresentOrElse` takes both branches at once, a consumer for the value and a runnable for its absence, which reads better than an `if` wrapped around two calls that each check presence separately:

```java
Optional.of("x").ifPresentOrElse(
    v -> System.out.println("present: " + v),
    () -> System.out.println("absent"));
```

```text
present: x
```

### The four places it does not belong

`Optional` is a return type, and using it anywhere else tends to move the problem rather than solve it.

**A field.** Nothing stops the field itself from being `null`, since `Optional` is a reference type like any other, so a field of type `Optional<String>` can be in three states, not two, and the type bought nothing:

```java
static void greet(Optional<String> name) {
    if (name.isPresent()) { ... }
}
greet(null);
```

```text
Exception in thread "main" java.lang.NullPointerException: Cannot invoke "java.util.Optional.isPresent()" because "<parameter1>" is null
```

**A parameter,** for the identical reason: a caller can hand over `null` instead of `Optional.empty()`, and the method that exists to remove a `null` check has just reintroduced one, only now it is buried inside a method the caller cannot see into. Overloading, or a `@Nullable`-style contract at worst, serves a genuinely optional argument better.

**The element type of a collection.** A `List<Optional<String>>` makes every consumer of the list handle absence a second time on top of the list already being able to be empty; a plain `List<String>` with no `null` elements is both simpler and already expresses "any number of these, including zero".

**Anything serialised.** Checking the type at run time settles it:

```java
Serializable.class.isAssignableFrom(Optional.class);   // false
```

`Optional` does not implement `Serializable`. Trying to serialise one directly confirms it:

```java
out.writeObject(Optional.of("x"));
```

```text
java.io.NotSerializableException: java.util.Optional
```

Writing `instanceof Serializable` against a variable of static type `Optional<String>` does not even compile, because `Optional` is `final` and unrelated to `Serializable`, so the compiler can prove the check would always fail:

```text
error: incompatible types: Optional<String> cannot be converted to Serializable
```

The type's own API documentation says why directly: "`Optional` is primarily intended for use as a method return type where there is a clear need to represent 'no result'... A variable whose type is `Optional` should never itself be `null`". A field is not a method return type, and neither is anything about to be serialised.

### The rule for a method that already returns a collection

A method whose success case is `List<Order>` should return an empty `List<Order>` for "none found", not `Optional<List<Order>>`. A collection can already represent zero results by being empty, so wrapping it in `Optional` only adds a second, redundant way to say the same thing, and forces every caller to unwrap twice, once for the `Optional` and once by iterating.

## Practice

1. ▢ Predict the output, and explain it.

   ```java
   Optional<String> o = Optional.of("hi");
   String r = o.map(String::toUpperCase)
                .filter(s -> s.length() > 5)
                .orElse("nope");
   System.out.println(r);
   ```

<details markdown="1"><summary>Check</summary>

`nope`.

`map` produces `Optional[HI]`. `filter` tests `"HI".length() > 5`, which is false, so `filter` turns a present `Optional` into `Optional.empty()` rather than throwing. `orElse` then supplies its fallback because the chain arrived empty.

</details>

2. ▢ Find the bug in this method, quote the exception it produces for the call shown, and give the one-line design fix rather than a null check.

   ```java
   static void greet(Optional<String> name) {
       if (name.isPresent()) {
           System.out.println("Hello, " + name.get());
       } else {
           System.out.println("Hello, stranger");
       }
   }
   // called as: greet(null);
   ```

<details markdown="1"><summary>Hint</summary>

`Optional` is a reference type. What stops a caller from passing a bare `null` where an `Optional<String>` is expected?

</details>

<details markdown="1"><summary>Check</summary>

```text
Exception in thread "main" java.lang.NullPointerException: Cannot invoke "java.util.Optional.isPresent()" because "<parameter1>" is null
```

Nothing in the language stops a caller from passing `null` for an `Optional<String>` parameter, so the method that exists to make absence safe has a `null` case of its own now. The fix is not a `null` check in front of it, it is removing `Optional` from the parameter list entirely: take a plain `String` and let the caller pass `null` or not, or better, overload the method for the two cases. `Optional` belongs on the way out of a method, not on the way in.

</details>

3. ▢ A `findUser(String id)` method returns `Optional<User>` today. A colleague proposes changing `findAllInRole(String role)`, which returns `List<User>`, to return `Optional<List<User>>` instead, "for consistency". Should it?

<details markdown="1"><summary>Check</summary>

No. `Optional<User>` earns its place because `User` cannot represent "none" on its own, absence needs a wrapper. `List<User>` already can: an empty list is a perfectly good "none", so wrapping it in `Optional` only adds a second empty case for every caller to handle, alongside the list already being able to be empty. Consistency is not the right axis here, what each return type can already express is.

</details>

4. ▢ Rewrite this without `isPresent` or `get`.

   ```java
   Optional<String> nickname = person.nickname();
   String label;
   if (nickname.isPresent()) {
       label = nickname.get().toUpperCase();
   } else {
       label = "N/A";
   }
   ```

<details markdown="1"><summary>Check</summary>

```java
String label = person.nickname().map(String::toUpperCase).orElse("N/A");
```

`map` transforms the value only when present and leaves an empty `Optional` empty, and `orElse` supplies the fallback in the one case that remains, with no branch and no call that can throw on the wrong path.

</details>

5. ▢ A method builds a report by calling an expensive `buildFallbackReport()` only when a cached one is missing. The current code is `cached.orElse(buildFallbackReport())`. What is wrong with it, and what is the fix?

<details markdown="1"><summary>Check</summary>

`orElse` evaluates its argument unconditionally, before checking whether `cached` holds a value, because Java evaluates a method call's arguments before making the call. `buildFallbackReport()` runs on every call, cached or not, defeating the point of caching. The fix is `cached.orElseGet(this::buildFallbackReport)`, which only invokes the supplier when `cached` is actually empty.

</details>

## Real-world reps

- [ ] Find every `isPresent()` in code you own and check whether it is followed by `get()`. Rewrite each one with `map`, `orElse`, `filter` or `ifPresent` instead.
- [ ] Find a field or a parameter typed `Optional<T>` in code you own, and change it to a plain `T` that may be `null`, or to an overload, whichever removes the `Optional` cleanly.
- [ ] Write the eager-argument trap yourself: a method with a `println` inside it, called through both `orElse` and `orElseGet` on a present `Optional`, and watch which one prints.
- [ ] Tomorrow: pick one method in code you own that returns `null` for "not found", and change its signature to `Optional<T>`, updating every caller to stop checking for `null`.

## Going further

- [`Optional`, Java SE 25 API](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/Optional.html): every method on the type, including the primitive-specialised `OptionalInt`, `OptionalLong` and `OptionalDouble`, and the `@apiNote` that states what the type is for
- [Lesson 4](0004-null.md): where `null` comes from, and what `Optional` is trading it for
- [Idiom and the library](../reference/idiom-and-library.md): the reference sheet for this stage
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
