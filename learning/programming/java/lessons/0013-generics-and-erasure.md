---
title: 13. Generics and Erasure
description: Type parameters the compiler checks and the runtime forgets, and the wildcards that make them usable
type: lesson
---

# Lesson 13. Generics and Erasure

**Mission link:** Erasure is why a `ClassCastException` sometimes names a line that contains no cast at all, and why a raw-typed collection compiles with nothing worse than a warning; reading that gap between what the compiler checked and what the runtime kept is what turns a baffling generics bug into one you can name precisely in a review.
**Primary source:** [The Java Language Specification, 4.6 Type Erasure](https://docs.oracle.com/javase/specs/jls/se25/html/jls-4.html#jls-4.6)
**Prerequisites:** [Lesson 5](0005-arrays-and-collections.md), [Lesson 7](0007-classes-and-objects.md)

## Warm-up

1. ▢ `Object[] objects = new String[1]; objects[0] = 42;` compiles without complaint. Does it fail, and if so where?

<details markdown="1"><summary>Check</summary>

It fails at run time with `ArrayStoreException`, not at compile time. Arrays are covariant, so the compiler accepts assigning a `String[]` to an `Object[]` variable, and the mismatch surfaces only when the store actually happens.

</details>

2. ▢ A field is declared `static`. How many copies of it exist across a thousand instances of the class, and why?

<details markdown="1"><summary>Check</summary>

One. A `static` field belongs to the class itself rather than to any instance, so every instance reads and writes the same storage.

</details>

## Know this

A type parameter is checked exhaustively at compile time and then thrown away. What the runtime keeps is called the **erasure** of the type, and almost everything in this lesson is a consequence of that one design decision.

### Generic classes and generic methods

A generic class declares its type parameter after the class name, and every member can use it:

```java
class Box<T> {
    private final T value;
    Box(T value) { this.value = value; }
    T get() { return value; }
}
```

A generic method declares its own type parameter, and it goes before the return type, not before the method name:

```java
static <T> T firstNonNull(T a, T b) {
    return a != null ? a : b;
}
```

A generic method's type parameter is independent of any type parameter on the enclosing class, and a `static` method can only ever introduce its own, since it has no instance and so no access to the class's.

### Inference and the diamond

The diamond, `new Box<>("hello")`, tells the compiler to infer the type argument from context instead of writing `new Box<String>("hello")` (final in Java 7). Inference reads the target: assigning the result to `Box<String> box` or passing it where a `Box<String>` is expected both give the compiler enough to fill in the diamond. This compiled and ran as expected, printing `hello`.

### Bounded type parameters

An unbounded `<T>` only guarantees `Object`'s methods. Bound it to demand more:

```java
static <T extends Comparable<T>> T max(List<T> items) {
    T best = items.get(0);
    for (T item : items) {
        if (item.compareTo(best) > 0) best = item;
    }
    return best;
}
```

`max(List.of(3, 1, 4, 1, 5))` returned `5`, because `Integer` satisfies `Comparable<Integer>`.

A bound can combine a class and interfaces with `&`, and the class, if there is one, must come first:

```java
static <T extends Comparable<T> & Serializable> T maxSerializable(List<T> items) { ... } // compiles
static <T extends Serializable & Comparable<T>> T bad(T t) { return t; }                 // does not
```

Reversing the order gave `error: interface expected here`, pointing at `Number` in a similar declaration. The rule is mechanical: at most one class bound, and it is written first.

### Invariance, and why it is the opposite of what arrays do

Lesson 5 showed that `String[]` is usable as an `Object[]`, and that the price is `ArrayStoreException` at the point of the mismatched store. Generics made the opposite choice:

```java
List<String> strings = new ArrayList<>();
List<Object> objects = strings; // does not compile
```

The compiler rejected this with `incompatible types: List<String> cannot be converted to List<Object>`. If it had compiled, `objects.add(42)` next would have gone straight into `strings` without the compiler ever seeing an `Integer` land in a `List<String>`, which is exactly the hole arrays leave open. **Invariance** is generics closing that hole at compile time instead of leaving it for a run-time exception to find. `List<String>` is not a `List<Object>`, full stop, even though `String` is an `Object`.

### Wildcards, and the PECS rule

Invariance also makes a plain `List<Number>` parameter too strict to accept a `List<Integer>` argument. Wildcards loosen that, in one direction at a time.

```java
static double sumOf(List<? extends Number> source) {
    double total = 0;
    for (Number n : source) total += n.doubleValue(); // reading is fine
    return total;
}

static void fill(List<? super Integer> sink) {
    sink.add(1);           // writing is fine
    Object o = sink.get(0); // reading only ever gives Object back
}
```

`sumOf(List.of(1, 2, 3))` returned `6.0`, and `fill` on a `List<Number>` left it holding `[1]`. The rule is **PECS**: use `? extends T` for a source you only read from (a **producer**), and `? super T` for a destination you only write into (a **consumer**). Each forbids the operation that would be unsafe: adding to `source` in `sumOf` failed to compile with `incompatible types: int cannot be converted to CAP#1`, because the compiler cannot know which subtype of `Number` is really behind the wildcard, and reading `sink.get(0)` as an `Integer` in `fill` failed the same way, because the compiler cannot know which supertype of `Integer` is really there either. `Collections.copy(List<? super T> dest, List<? extends T> src)` is this rule in the standard library: the destination consumes, the source produces.

### The unbounded wildcard is not a raw type

`List<?>` still has a type argument, just an unknown one, and the compiler enforces that consistently: `list.add("x")` on a `List<?> list` failed with the same shape of error as the bounded wildcards, `incompatible types: String cannot be converted to CAP#1`. A raw `List`, the type written with no argument at all, is different: it switches generics checking off for that variable. `list.add(42)` on a raw `List<String>` compiled, with only `warning: [unchecked] unchecked call to add(E) as a member of the raw type List`. Raw types exist to interoperate with code written before Java 5 introduced generics, and reaching for one in new code trades a compile-time guarantee for a warning that is easy to miss.

### Erasure, one consequence at a time

The compiler enforces every rule above and then erases the type argument, so `List<String>` and `List<Integer>` are one class at run time:

```java
List<String> strings = new ArrayList<>();
List<Integer> ints = new ArrayList<>();
strings.getClass() == ints.getClass() // true
```

Both reported `class java.util.ArrayList`, and the comparison printed `true`. Several restrictions follow directly from there being nothing left at run time to check against:

- **No `new T[]`.** `return new T[size];` inside a generic class failed with `error: generic array creation`, because the runtime would need to know `T` to build the array's component type, and it does not.
- **No `instanceof` against a parameterised type.** `if (o instanceof List<String>)` failed with `error: Object cannot be safely cast to List<String>`, since at run time there is only `List` left to test against.
- **No two methods differing only after erasure.** `process(List<String>)` and `process(List<Integer>)` in the same class failed with `error: name clash: process(List<Integer>) and process(List<String>) have the same erasure`, because the JVM would see one signature, not two.
- **No type parameter in a static context.** `static T value;` on a class `StaticContext<T>` failed with `error: non-static type variable T cannot be referenced from a static context`, because a `static` member exists once per class while `T` is only known per instance.

The sharpest consequence is a `ClassCastException` at a line that has no cast written on it:

```java
static void poison(List list) {
    list.add(42); // unchecked call, warned about and ignored
}

List<String> strings = new ArrayList<>();
poison(strings);
String first = strings.get(0); // throws here
```

Running it threw `ClassCastException: class java.lang.Integer cannot be cast to class java.lang.String`, with the stack pointing at the `strings.get(0)` line. Erasure means `get` really returns `Object` at run time, so the compiler inserts an invisible cast to `String` at every call site that expects one, and that inserted cast is what throws. The line that looks innocent is the one paying for the line that was not.

### Unchecked warnings, heap pollution and `@SafeVarargs`

A generic varargs parameter is a `T[]` under the covers, so declaring one risks the same hole a raw type does, called **heap pollution**: an array that quietly holds something other than what its erased type promises. Compiling a generic varargs method with no annotation produced `warning: [unchecked] Possible heap pollution from parameterized vararg type T` at the declaration. `@SafeVarargs` is a promise to the compiler that the method never stores anything unsafe into that array and never lets a reference to it escape; a version that only reads its `elements` parameter in a loop compiled cleanly under `@SafeVarargs` with no warning at all. The annotation only suppresses the warning, it does not add a check, and it is restricted to methods the compiler can trust will not be overridden with a different body: putting it on an ordinary instance method failed with `error: Invalid SafeVarargs annotation. Instance method <T>listOf(T...) is neither final nor private.`

### `Class<T>` tokens

Erasure removes `T` from a generic method's own body, but a `Class<T>` parameter hands back a genuine run-time type to check against:

```java
static <T> T decode(Class<T> type, Object raw) {
    return type.cast(raw);
}
```

`decode(String.class, "typed via token")` returned the string as expected, and `decode(Integer.class, "not a number")` threw `ClassCastException: Cannot cast java.lang.String to java.lang.Integer` right where `type.cast(raw)` is written. That is the opposite of the invisible cast two sections up: `Class.cast` performs a real check against a token the caller supplied, so the exception lands on the line that made the decision rather than on some later line that merely trusted it.

### A passing note on generic records

A record takes type parameters exactly like a class does, and every consequence above applies to it the same way:

```java
record Pair<A, B>(A first, B second) {}
```

`new Pair<>("age", 42)` printed `Pair[first=age, second=42]`, with `first()` and `second()` returning the two values untouched. Nothing about being a record changes how erasure treats `A` and `B`.

## Practice

1. ▢ Predict what this throws, and name the line the stack trace points at.

   ```java
   static void poison(List list) {
       list.add(42);
   }

   List<String> strings = new ArrayList<>();
   poison(strings);
   String first = strings.get(0);
   System.out.println(first);
   ```

<details markdown="1"><summary>Hint</summary>

`add` is where the wrong value gets in. Ask where a `String` is actually demanded back out.

</details>

<details markdown="1"><summary>Check</summary>

`ClassCastException: class java.lang.Integer cannot be cast to class java.lang.String`, thrown at `String first = strings.get(0);`. `add` never throws, since the raw parameter switched off checking there and the runtime array only ever holds `Object`. The exception waits for the first read that the compiler treats as returning `String`, because that is where the compiler's inserted cast lives, and that line contains no cast in the source.

</details>

2. ▢ Find the bug in this class, name the compiler error it produces, and fix it without losing either behaviour.

   ```java
   class Reporter {
       static void process(List<String> names) { System.out.println("names: " + names); }
       static void process(List<Integer> ids) { System.out.println("ids: " + ids); }
   }
   ```

<details markdown="1"><summary>Check</summary>

`error: name clash: process(List<Integer>) and process(List<String>) have the same erasure`. Both parameters erase to plain `List`, so the two methods would become one signature on the JVM, which the compiler refuses to allow even though the source looks like ordinary overloading. The fix is to give the methods different names, `processNames` and `processIds`, since overloading on a type argument alone is never available.

</details>

3. ▢ You are writing `static <T> void copy(List<? A> src, List<? B> dest)`, which reads every element out of `src` and writes it into `dest`. Which wildcards are `A` and `B`?

   - a) both `extends T`
   - b) `A` is `extends T`, `B` is `super T`
   - c) `A` is `super T`, `B` is `extends T`
   - d) both plain `T`, no wildcard

<details markdown="1"><summary>Check</summary>

**b)**. `src` is only read from, so it is a producer and takes `? extends T`. `dest` is only written to, so it is a consumer and takes `? super T`. Option a lets a caller pass a `List<Integer>` as `src` but forces `dest` to be exactly `List<Integer>` too, which is more restrictive than the method needs. Option c has the two backwards, so a `List<Number>` could not be read from as `src`. Option d is invariant, so a caller with a `List<Integer> src` and a `List<Object> dest`, both of which are individually safe, could not call it at all.

</details>

4. ▢ A configuration file names a class by string, and you need to build one instance of whatever type that name resolves to, validated against the type the caller expects. A type parameter alone cannot do this. Why not, and what do you reach for instead?

<details markdown="1"><summary>Check</summary>

A type parameter is erased before the program runs, so by the time the configuration file's string is read, there is no `T` left anywhere to check the constructed object against, or to hand to whatever reflective call builds it. A `Class<T>` parameter fixes that, since it is an ordinary object that exists at run time and carries the real type: the caller passes `Config.class` or similar, the method uses it to drive the reflective construction, and `type.cast(result)` gives a genuine, checked confirmation that what came back really is a `T`, throwing `ClassCastException` on the spot if it is not.

</details>

5. ▢ A teammate writes `List list = new ArrayList<String>(); list.add(42);`, sees it compile, and says "it's fine, generics didn't complain." What is wrong with that reasoning, and what would writing `List<?> list` instead have done at the same line?

<details markdown="1"><summary>Check</summary>

Generics did complain, just not with an error: `javac` reports `warning: [unchecked] unchecked call to add(E) as a member of the raw type List`, and a warning that nothing enforces reading is not the same as nothing being wrong. The raw type switched off checking for every call that mentions the erased type parameter, so `add(42)` is accepted with no compile-time link back to the `<String>` the variable was declared with. `List<?>` keeps a type argument, just an unknown one, so `list.add(42)` there fails outright with `incompatible types: int cannot be converted to CAP#1`, because the compiler still enforces that whatever goes in must match the wildcard's hidden type, even without knowing what that type is.

</details>

## Real-world reps

- [ ] Build the raw-type `ClassCastException` from this lesson yourself, and confirm the stack trace names the read, not the write.
- [ ] Write the two overloaded methods with the same erasure, watch `javac` reject them, then rename one instead of relying on overloading.
- [ ] Take a method that takes `Object` and casts it internally, give it a bounded type parameter instead, and see which of its current callers the compiler now refuses.
- [ ] Tomorrow: find a wildcard, a raw type, or a `Class<T>` parameter in code you know, and say in one sentence what erasure forced that choice.

## Going further

- [The Java Language Specification, 4.6 Type Erasure](https://docs.oracle.com/javase/specs/jls/se25/html/jls-4.html#jls-4.6): the exact erasure mapping, and 4.8 next to it for raw types
- [`Collections`](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/Collections.html): `copy`, `unmodifiableList` and the rest, each signature a real-world PECS example
- [`Class`](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/Class.html): `cast` and `isInstance`, the way back to a checked run-time type
- [Modelling](../reference/modelling.md): the reference sheet for this stage
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
