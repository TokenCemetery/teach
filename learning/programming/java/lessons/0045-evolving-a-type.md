---
title: 45. Evolving a Type Without Breaking It
description: How to add to an interface, a record, an enum and a sealed hierarchy after people depend on them
type: lesson
---

# Lesson 45. Evolving a Type Without Breaking It

**Mission link:** Owning a Java service in production means other code is already compiled against every type you shipped last release, so the question that matters when you touch one of those types again is not whether the change compiles for you, it is whether it still works for everyone who has not rebuilt yet.
**Primary source:** [The Java Language Specification, Java SE 25, chapter 13, Binary Compatibility](https://docs.oracle.com/javase/specs/jls/se25/html/jls-13.html)
**Prerequisites:** [Lesson 43](0043-what-counts-as-breaking.md), [Lesson 11](0011-sealed-types-and-pattern-matching.md)

## Warm-up

Lesson 43 ran one small library through a version bump and got three different failures out of three different changes: a constant that silently stayed stale because it had been inlined, a method whose new behaviour arrived for free, and a return type narrowed from `List` to `ArrayList` that recompiled cleanly against a rebuilt caller yet threw `NoSuchMethodError` against a caller nobody rebuilt. For a type most of your callers will only ever consume as a jar, never as source they rebuild the day you ship, which one of those three compatibilities actually decides whether they notice your change at all?

<details markdown="1"><summary>Check</summary>

Binary compatibility. Most consumers of a published type swap the new artifact in and restart without recompiling anything of their own, so source compatibility only protects the minority who do rebuild before running; what decides whether the class files already sitting in everyone else's deployment keep working unchanged is whether the new version is binary compatible with the old one. Everything in this lesson is about which changes to which construct keep that promise, and which ones only look safe because you tried them with a rebuild.

</details>

## Know this

### Interfaces: the three directions you can move in

An interface published for other code to implement can move in exactly three directions, and lesson 43's compatibility labels sort them cleanly once you actually run each one. Start with one method and one implementor:

```java
public interface Plugin {
    void run();
}

public class Main implements Plugin {
    public void run() { System.out.println("running"); }
}
```

Add a second abstract method, `void stop();`, and recompile nothing but `Plugin` itself. `Main.java` has not changed one character, but recompiling that unchanged source against the new interface fails immediately:

```text
error: Main is not abstract and does not override abstract method stop() in Plugin
```

That is source incompatibility doing exactly what lesson 43 described: the change is invisible until somebody tries to rebuild, and then it is impossible to miss, because the compiler names both the missing method and the interface that now demands it.

Declare the same addition as `default void stop() { System.out.println("stopping (default)"); }` instead, and the story reverses. `Main.java`, still untouched, compiles cleanly against the new interface, and calling `stop()` through a `Plugin` reference to an existing `Main` runs the inherited default with no further work from anyone:

```text
running
stopping (default)
```

This is the whole reason [Lesson 9](0009-interfaces.md) taught default methods, final in Java 8, as more than a convenience: a default method is the one interface change that costs none of lesson 43's three compatibilities at once, because it gives every existing implementor an answer to the new method without asking a single one of them to supply it.

The direction that actually hurts someone already running your code is the third one: taking a default away, or turning it back into an abstract method. A class compiled while `stop()` still carried a default body, never overriding it itself, keeps loading and keeps running with no complaint at all, because nothing about its own class file changed. The break only appears the moment something calls `stop()` on it, and by then the failure is happening inside a running program rather than a build:

```text
running
Exception in thread "main" java.lang.AbstractMethodError: Receiver class Main does not define or inherit an implementation of the resolved method 'abstract void stop()' of interface api.Plugin.
	at Harness.main(Harness.java:6)
```

`run()` still executes; only the one call the old class file cannot satisfy throws. That delay is what makes this the most expensive of the three directions: it costs binary compatibility for a consumer already in production, and behavioural compatibility too, since the program looked correct right up until the exact code path nobody had exercised yet finally ran.

One caveat carries past this lesson: a default method buys compatibility, not correctness. A body for `stop()` that quietly does nothing, or does the wrong thing for a plugin that genuinely needs to release a resource on shutdown, lets every implementor keep compiling while silently inheriting behaviour nobody asked for. A compile error that stops a build is loud and gets fixed before anything ships; a default that is wrong for one implementor is invisible until that implementor's `stop()` finally runs in production, which is worse than the compile error would have been, not better. Reach for a default because it preserves compatibility for implementors with no opinion about the new method, not because it makes the method optional for implementors that do have one.

### Records: the header is a promise, not a draft

[Lesson 8](0008-records.md) taught a record's canonical constructor and its accessors as things the compiler derives, once, from the header. That derivation is exactly why the header is not a draft you can quietly extend later: every accessor, the canonical constructor's parameter list, `equals`, `hashCode` and `toString` all come from that one list of components in that one order, so changing the list changes all of them at once.

```java
public record Point(int x, int y) {}
```

Add a third component so the header reads `Point(int x, int y, int z)`, recompile only the record, and the existing caller's unchanged source fails to compile against it:

```text
error: constructor Point in record Point cannot be applied to given types;
  required: int,int,int
  found:    int,int
  reason: actual and formal argument lists differ in length
```

That is at least a loud failure, source-incompatible and impossible to ship by accident, because nobody's build stays green through it. Reordering the same two components without adding a third is worse, and it is worse specifically because nothing announces it. Change `Point(int x, int y)` to `Point(int y, int x)`, recompile nothing at all, and run the old, unmodified caller's class file, compiled when the first constructor argument still meant `x`, against the new one:

```text
x=3 y=7
```

becomes, with no recompilation, no exception and no warning anywhere in the process:

```text
x=7 y=3
```

The descriptor is still `(II)`, so the caller's bytecode still resolves and still runs, and both `x()` and `y()` still return values without complaint, they are just the wrong values for what the caller meant. Source compatibility survives, binary compatibility survives, and only behavioural compatibility breaks, silently, which is the one kind of break neither the compiler nor the class loader can catch for you. Adding a component fails a build. Reordering one corrupts data.

What you can still add to a record without touching the header at all: a static factory such as `Point.origin()` that hands back `new Point(0, 0)`, a derived method such as `distance(Point other)` computed from the existing components, or a compact constructor that validates or normalises the arguments it already receives, since none of those change the canonical constructor's signature or the accessor set anyone already depends on. What none of that changes is the underlying decision: a record is a poor choice for a type you already expect to grow a field, because growing one is not an additive change the way adding a field to an ordinary class is, it rewrites the constructor everyone calls. That choice gets made when you pick the construct, not repaired afterwards by being careful with the header.

### Enums: adding a constant is quiet until a switch is not

Adding a constant to a published enum is binary compatible on its own, in the narrow sense that nothing about the enum's existing members changes shape. The landmine is behavioural, and [Lesson 12](0012-enums.md) already produced the exact failure it sets off: compile a `switch` expression against a three-constant enum with no `default`, add a fourth constant, recompile only the enum, and run the unrecompiled switch against it, and it throws `java.lang.MatchException` at the exact line that used to be exhaustive. Nothing about that mechanism is different here, so it is not worth re-deriving; what is worth stating plainly for an API author is the consequence. A public enum's constant set is part of its contract in exactly the way an interface's method set is, and every exhaustive `switch` anyone has ever written over it, in code you cannot see and will not rebuild alongside your release, is a place your next constant might land as a `MatchException` instead of a compile error, purely because of when that code happens to get rebuilt relative to when your jar ships.

### Sealed hierarchies: the closed set is the whole point

A sealed type's `permits` clause is [Lesson 11](0011-sealed-types-and-pattern-matching.md)'s closed set, and adding a permitted subclass to it is the same problem as adding an enum constant, for the same reason: the whole value of sealing a type is that its set of alternatives is closed, so every exhaustive `switch` anyone wrote over it was allowed to skip `default` on the strength of that promise. Widen `permits` and any such `switch` that is not rebuilt alongside the widened type inherits the identical failure lesson 12 already showed for enums:

```text
Exception in thread "main" java.lang.MatchException
	at Describe.describe(Describe.java:3)
	at Caller.main(Caller.java:3)
```

Narrowing `permits` instead, by removing a permitted subclass, fails differently and considerably louder. A class already compiled against the wider `permits` list, unchanged, refuses to load at all against a narrowed sealed type, because the sealed constraint is checked by the class loader itself, not only by the compiler that first wrote the code:

```text
Exception in thread "main" java.lang.IncompatibleClassChangeError: Failed listed permitted subclass check: class Circle is not a permitted subclass of Shape
	at java.base/java.lang.ClassLoader.defineClass1(Native Method)
	...
	at UseCircle.main(UseCircle.java:3)
```

Removing a permitted subclass is not the mirror image of adding one. Adding one is quiet until an unrebuilt exhaustive `switch` meets a value it has never seen; removing one is loud the moment the JVM tries to load the class that no longer belongs, a considerably safer failure to have than a silent `MatchException` deep in someone else's code. Sealing a type is a decision to make exhaustiveness someone else's compile-time guarantee, backed by a run-time check the JVM itself enforces, and both directions of changing `permits` ask something real of that guarantee afterwards: widening asks every exhaustive `switch` to be rebuilt before it meets the new case, narrowing asks every permitted subclass to be rebuilt or removed before anything tries to load it. Neither is free, and choosing to seal a hierarchy in the first place is a commitment to that ongoing cost, not a convenience you get to walk away from later.

### Classes: the ordinary case, and the two that catch people out

Most changes to an ordinary class are exactly as safe as they look. Adding a field, adding a method, and widening a member's access from `private` to `protected` or `public` all preserve every one of lesson 43's three compatibilities, because nothing that already existed changes shape and nothing new is demanded of anyone who has not asked for it.

Two changes that look equally harmless are not. The first is adding a constructor overload next to an existing one. `Widget(String s)` alone leaves `new Widget(null)` unambiguous, and it stays unambiguous if you add `Widget(Object o)` beside it, because `String` is more specific than `Object` and the compiler picks the more specific overload for a `null` argument without complaint. Add `Widget(Integer i)` instead, a type unrelated to `String` rather than a supertype of it, and the same unchanged call site fails to compile:

```text
error: reference to Widget is ambiguous
  both constructor Widget(String) in Widget and constructor Widget(Integer) in Widget match
```

The rule underneath both outcomes is ordinary overload resolution, not something special about constructors: a new overload is safe for existing `null` call sites exactly when it is a strict supertype of an already-applicable parameter type, and dangerous exactly when it introduces a second, unrelated reference type that `null` matches equally well.

The second is changing a method from non-`final` to `final`. Nothing about calling that method changes for anyone, but a subclass that already overrides it stops compiling the moment it is recompiled against the new version:

```text
error: greet() in Sub cannot override greet() in Base
  overridden method is final
```

Both surprises share the same shape: the change reads as purely additive or purely restrictive from the point of view of the class doing the changing, and the damage lands entirely on a caller or a subclass that the change itself never mentions.

### The decision table

| Change | Costs |
|---|---|
| Add an abstract method to an interface | Source, immediately for anyone who rebuilds; binary and behavioural too, for anyone who never does |
| Add a default method to an interface | Nothing |
| Remove a default method, or make it abstract | Binary and behavioural, for already-compiled implementors |
| Add a component to a record | Source and binary, since the canonical constructor's descriptor changes |
| Reorder a record's existing components | Behavioural only, and silently, with no compile or link error at all |
| Add a static factory, a derived method or compact-constructor validation to a record | Nothing |
| Add a constant to an enum | Behavioural, for any unrebuilt exhaustive `switch` |
| Widen `permits` on a sealed type | Behavioural, for any unrebuilt exhaustive `switch`, the same failure as an enum constant |
| Narrow `permits` on a sealed type | Binary, for any already-compiled permitted subclass, checked at class load |
| Add a field, add a method, or widen access on a class | Nothing |
| Add a constructor overload with a parameter type unrelated to an existing one | Source, for call sites passing `null` |
| Change a method from non-`final` to `final` | Source, for overriding subclasses |

None of these comparisons need to stay a manual exercise you run by hand every release. A build plugin such as `japicmp-maven-plugin`, 0.26.1 on Maven Central at the time of writing, compares two built jars directly and can fail a build the moment it finds a binary-incompatible change, which is the mechanised version of exactly the by-hand comparisons this lesson has been running throughout.

## Practice

1. ▢ A published interface `Cache` has one abstract method, `get(String key)`. You need to add `getOrDefault(String key, String fallback)`, and `RedisCache`, an implementor nobody plans to touch again, is already running in production compiled against the old interface. Predict what happens to that already-running `RedisCache` if you add the new method as `default`, and what happens instead if you add it abstract and someone eventually calls it without recompiling `RedisCache` first.

<details markdown="1"><summary>Check</summary>

Added as `default`, nothing happens to `RedisCache` at all: it keeps loading, keeps running, and if anything ever calls `getOrDefault` on it, that call runs the inherited default body with no recompilation needed anywhere. Added abstract, `RedisCache` still loads and still runs `get` correctly, right up until something actually calls `getOrDefault` on it, at which point it throws `AbstractMethodError`, the identical failure this lesson showed for turning an existing default back into an abstract method, because from the class loader's point of view an abstract method that was never there and a default method that was removed look the same: a method the interface now demands that this particular compiled class does not provide.

</details>

2. ▢ A `record Money(long cents)` has been in production for a year. A ticket asks for a `currency` component, so the type becomes `Money(long cents, String currency)`. Predict what happens to every existing call site written as `new Money(500)`, and say whether recompiling those call sites without editing them is enough to fix it.

<details markdown="1"><summary>Check</summary>

Every one of them fails to compile: the canonical constructor is now `Money(long, String)`, so a one-argument call has no matching constructor at all, the same "argument lists differ in length" failure this lesson ran against `Point`. Recompiling alone is not enough, because there is nothing for the compiler to resolve to; every call site's source has to be edited to pass a currency, which is the whole reason a record is a poor fit for a type expected to grow a field later.

</details>

3. ▢ Your team's public API returns a sealed `PaymentResult` with two permitted records, and product now wants a third outcome, `Pending`. Before touching `permits`, what one search across your consumers' code tells you whether this is safe to ship as a point release rather than something that needs coordinated rebuilds first?

<details markdown="1"><summary>Hint</summary>

You are not asking whether your own code compiles. You are asking which of your consumers' `switch` expressions over `PaymentResult` will run again before they are rebuilt.

</details>

<details markdown="1"><summary>Check</summary>

Search every consumer for an exhaustive `switch` over `PaymentResult` or its permitted types that ships as an already-compiled artifact you do not control the rebuild timing of. If none exist, or every one of them has a `default` arm already, widening `permits` costs nothing any of them will notice. If even one unrebuilt exhaustive `switch` exists, adding `Pending` is a behavioural break for whoever owns it the moment a `Pending` value reaches that `switch`, which means either that consumer needs to rebuild before your release reaches them, or every such `switch` needs a `default` added first, or this genuinely is not a point release for the API's consumers even though it compiles cleanly on your own side.

</details>

4. ▢ `Base` declares `public void greet()`, and `Sub extends Base` overrides it. A later change makes `Base.greet()` `final`. Predict what happens if `Sub` is recompiled against the new `Base`, and separately what happens if `Sub`'s already-compiled class file is simply run, unrecompiled, against the new `Base`.

<details markdown="1"><summary>Hint</summary>

One of these two outcomes is a build failure. The other one asks whether the JVM re-checks the override relationship at load time the way it re-checks a sealed type's `permits` list.

</details>

<details markdown="1"><summary>Check</summary>

Recompiled, `Sub` fails immediately with `greet() in Sub cannot override greet() in Base, overridden method is final`, exactly the error this lesson ran. Left unrecompiled and simply run against the new `Base`, the already-compiled `Sub.class` keeps working with no error at all, because its override was legal when it was compiled and the JVM does not re-verify that a method is still overridable every time a class loads, unlike the permitted-subclass check a sealed type carries. The break only exists for whoever rebuilds `Sub` next.

</details>

5. ▢ `Widget` has one constructor, `Widget(String s)`. Predict which of these two additions would make an existing, unchanged `new Widget(null)` call site fail to compile, and which would leave it exactly as it was: adding `Widget(Object o)`, or adding `Widget(Integer i)`.

<details markdown="1"><summary>Check</summary>

Adding `Widget(Object o)` changes nothing: `String` is more specific than `Object`, and Java's overload resolution always picks the most specific applicable method for a `null` argument, so `new Widget(null)` still resolves to `Widget(String)` without complaint. Adding `Widget(Integer i)` breaks it: `String` and `Integer` are unrelated reference types, neither one more specific than the other, so `null` now matches both equally and the call site fails with `reference to Widget is ambiguous`. The difference is entirely about whether the new overload's parameter type is a supertype of an existing one or a stranger to it.

</details>

## Real-world reps

- [ ] Pick a public interface you maintain and check whether every abstract method it has ever gained was shipped as `default` first; if any went straight to abstract, find out who that broke and when they noticed.
- [ ] Take a record you own and ask whether it has already grown, or is likely to grow, a component since it first shipped; if the honest answer is yes, decide out loud whether it should have been a record at all.
- [ ] Search your own codebase for every sealed type's `permits` clause and count how many separately built modules pattern-match over it without a `default`, since that count is exactly how many places a new permitted subclass can break silently rather than at compile time.
- [ ] Find a class you maintain with a constructor that takes a reference type, and check whether adding another overload beside it with an unrelated parameter type would turn any existing `null` call site ambiguous.
- [ ] Tomorrow: pick one type you maintain that other code depends on, and for the next change you actually expect to make to it, write down which of source, binary and behavioural compatibility that change would cost, before you write a line of the change itself.

## Going further

- [Kinds of Compatibility, OpenJDK Compatibility and Specification Review](https://wiki.openjdk.org/display/csr/Kinds+of+Compatibility): the three-way definition this whole lesson keeps applying, construct by construct
- [The Java Language Specification, Java SE 25, chapter 8, Classes](https://docs.oracle.com/javase/specs/jls/se25/html/jls-8.html): the rules behind sealed `permits`, final methods and constructor overload resolution
- [Effective Java, Joshua Bloch](https://openlibrary.org/isbn/9780134685991): the book-length version of designing a type right the first time, most of it addressed to exactly the problem of not needing this lesson later
- [Judgment](../reference/judgment.md): the stage 7 reference sheet
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
