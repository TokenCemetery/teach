---
title: "34. Java Interop"
description: "Why the boundary is asymmetric, what a platform type costs you and how to pay it back, and which annotations you owe a Java caller"
type: lesson
---

# Lesson 34. Java Interop

**Mission link:** Stage 8 opens on judgment, and the interop boundary is where most of it is needed: every crossing gives up a guarantee, and the useful skill is knowing which one and who pays for it.
**Primary source:** [Docs: "Calling Java from Kotlin", Kotlin](https://kotlinlang.org/docs/java-interop.html)
**Prerequisites:** [Lesson 33](0033-generics-and-variance.md), [Lesson 29](0029-mocking.md), [Lesson 1](0001-null-safety.md)

## Warm-up

1. ▢ What does declaring a type parameter `out` restrict, and what does it buy in exchange?

<details markdown="1"><summary>Check</summary>

It restricts `T` to out-positions, so the class may produce a `T` and never consume one. In exchange, `C<Base>` may safely be a supertype of `C<Derived>`, so a `Source<String>` can be passed where a `Source<Any>` is expected with nothing written at the call site.

</details>

2. ▢ What is a platform type, and how should you treat one?

<details markdown="1"><summary>Check</summary>

The type Kotlin assigns to a value coming from unannotated Java code, because it cannot determine nullability from Java alone. Treat it as possibly null unless there is positive evidence otherwise. It is not equivalent to a Kotlin non-nullable type, however much it behaves like one at the call site.

</details>

3. ▢ Why does mocking one top-level Kotlin function with `mockkStatic` clear the mocks of other functions in the same file?

<details markdown="1"><summary>Check</summary>

Because top-level functions belong to no class, so the JVM compiles them into static methods on a generated class for that file, and it is that class which gets mocked. The unit is the file, not the function. That generated class is about to reappear as the thing a Java caller has to name.

</details>

## Know this

**The boundary is asymmetric, and that is the whole lesson.** Crossing from Java into Kotlin costs you **nullability information**. Crossing from Kotlin into Java costs you **Kotlin's conveniences**. Both directions work without ceremony, which is exactly why the losses are easy to miss.

### Java into Kotlin: you lose nullability

Pretty much all Java code can be called with no trouble, and the friction is concentrated in one place: Kotlin cannot know whether an unannotated Java method may return null, so the result is a platform type. Platform types cannot be written in Kotlin source at all, there is no syntax for them, but the compiler and IDE need to show them, so there is a mnemonic notation you will meet in error messages and tooltips ([Calling Java from Kotlin](https://kotlinlang.org/docs/java-interop.html)):

|Notation|Means|
|---|---|
|`T!`|`T` or `T?`|
|`(Mutable)Collection<T>!`|A Java collection of `T`, which may be mutable or not, nullable or not|
|`Array<(out) T>!`|A Java array of `T` or a subtype of `T`, nullable or not|

The docs also give the remedy, and it has two forms. When you see that notation, either **add an explicit type annotation to your Kotlin variable**, which restores the null-safety checks from that point on, or **eliminate platform types at the source** with nullability annotations on the Java side. The first is local and always available; the second fixes it for every caller and is the one to push for in a codebase you own.

Two smaller conveniences in this direction, both worth recognising rather than memorising. Java methods that follow the getter and setter naming conventions appear in Kotlin as **synthetic properties**, so `calendar.firstDayOfWeek = Calendar.MONDAY` calls `setFirstDayOfWeek`, and a boolean `isLenient()` becomes a property named for the getter. Note the asymmetry there too: a Java class with only a setter gives you no property at all, because Kotlin has no set-only properties. And where a Java library used a word that is a Kotlin keyword, `in`, `object` and `is` among them, the call still works with the name in backticks:

```kotlin
foo.`is`(bar)
```

### Kotlin into Java: you lose the conveniences

Kotlin code can be called from Java easily, but several Kotlin features have no Java equivalent, so the compiler generates something and a small family of annotations is how you shape what Java actually sees ([Calling Kotlin from Java](https://kotlinlang.org/docs/java-to-kotlin-interop.html)).

|What Java cannot see|What it gets instead|The annotation|
|---|---|---|
|Top-level functions and properties|Static methods on a class named after the file, so `app.kt` in `org.example` becomes `org.example.AppKt`|`@file:JvmName("DemoUtils")` renames it. Two files generating the same name is normally an error, and `@file:JvmMultifileClass` on all of them merges the declarations into one facade instead|
|Default parameter values|Only the full signature, with every parameter present|`@JvmOverloads` generates the overloads. It works on constructors and static methods, and **cannot** be used on abstract methods, interface methods included|
|A property as a field|A getter and a setter|`@JvmField`, when the property has a backing field, is not private, has no `open`, `override` or `const` modifier, and is not delegated. A `lateinit` property is exposed as a field already|
|Checked exceptions|Nothing in the `throws` list, because Kotlin has none, so a Java `catch (IOException e)` around it fails to compile|`@Throws(IOException::class)` on the Kotlin function|

The `@Throws` case is the one that surprises people most, because the Java compiler's error names a problem in code that looks correct: the function does throw an `IOException`, the Java caller catches it, and the compiler objects that it was never declared. Kotlin has no checked exceptions, so nothing put it in the signature.

**Where the judgment comes in.** Every one of those annotations is a promise to Java callers, and the promise constrains your Kotlin afterwards. `@JvmOverloads` means the overload set is now part of your published surface, so reordering parameters becomes a breaking change for people you cannot see. `@file:JvmName` fixes the class name Java depends on, so renaming the file is no longer free. `@JvmField` exposes a field rather than accessors, so you can never later put logic in a getter.

None of that is an argument against them. It is an argument for deciding deliberately, on the basis of whether Java callers exist, and for treating the answer as an API decision rather than a build fix. That is also the sharpest version of the general point: the annotations are cheap to add and expensive to remove.

## Practice

1. ▢ A Java method `String findName(int id)` has no nullability annotations, and Kotlin shows its result as `String!`. Name the two documented ways to restore null-safety, and say what each one is good for.

<details markdown="1"><summary>Hint</summary>

One fix is available to you at the call site. The other is available only to whoever owns the Java code.

</details>

<details markdown="1"><summary>Check</summary>

Add an explicit type annotation on the Kotlin side, `val name: String? = findName(id)`, which restores the null-safety checks from there on and forces you to handle the nullable case. Or eliminate the platform type at its source by adding nullability annotations to the Java declaration, which fixes it for every caller rather than one. The first is always available and local; the second is the one worth pushing for in a codebase you own, because a platform type left in place is a null check that no compiler will ever ask for. Note that the third option people reach for, asserting non-null, is not on the documentation's list: it converts an unknown into a crash rather than into a decision.

</details>

2. ▢ A Java class has `setTimeout(int)` and no `getTimeout()`. Why is there no `timeout` property in Kotlin?

<details markdown="1"><summary>Check</summary>

Because Kotlin does not support set-only properties, so a Java setter with no matching getter is not represented as one. You call `setTimeout(...)` as an ordinary method. This is worth knowing as a small case of the general rule: the synthetic-property convenience is a mapping over what Java offers, and where the Java shape has no Kotlin equivalent, the mapping simply does not apply rather than inventing something.

</details>

3. ▢ A Kotlin function `fun writeToFile()` throws an `IOException`. A Java caller wraps it in `try` and `catch (IOException e)`, and the Java compiler rejects it. Why, and what fixes it?

<details markdown="1"><summary>Check</summary>

Kotlin has no checked exceptions, so the generated Java signature does not declare any, and Java will not let you catch a checked exception that the method does not list in its `throws` clause. The exception is genuinely thrown at runtime; the declaration is what is missing. Adding `@Throws(IOException::class)` to the Kotlin function puts it in the signature and the Java catch compiles. The judgment attached: you are choosing to participate in a Java-only discipline, so add it where Java callers exist and leave it off where they do not.

</details>

4. ▢ `fun draw(label: String, lineWidth: Int = 1, color: String = "red")` is called from Java. What does the Java caller see, what does `@JvmOverloads` change, and where can it not be used?

<details markdown="1"><summary>Check</summary>

By default the Java caller sees only the full three-parameter signature, so the default values are invisible and every call has to supply everything. `@JvmOverloads` generates the overloads for the parameters that have defaults, so Java gets the shorter forms too, and it works on constructors and static methods as well as ordinary functions. It cannot be used on abstract methods, which includes methods declared in interfaces. Worth remembering the consequence rather than just the syntax: once those overloads are published, the parameter order is part of your API.

</details>

5. ▢ Which claim about calling an unannotated Java method from Kotlin is correct?

   - a) An unannotated Java method gives Kotlin a nullable type, checked as usual
   - b) An unannotated Java method gives Kotlin a platform type, with checks relaxed
   - c) An unannotated Java method gives Kotlin a non-null type, always safe
   - d) An unannotated Java method cannot be called from Kotlin without a cast

<details markdown="1"><summary>Check</summary>

**b)** Kotlin cannot determine nullability from unannotated Java, so it assigns a platform type, which you may use as though it were non-null and which therefore carries the risk rather than a compile error. (a) would be safe but is not what happens; if it were, the notation `T!` would not need to exist. (c) is the assumption that produces the crash, and it is how a Java habit undoes null safety. (d) overstates it: the call compiles fine, and the absence of friction is precisely the problem.

</details>

6. ▢ You are publishing a Kotlin library that Java code will consume. Decide which of the interop annotations you owe those callers, and say what each one costs you afterwards.

<details markdown="1"><summary>Check</summary>

The defensible list, with the cost attached:

`@file:JvmName` on files whose generated `SomethingKt` name would leak an implementation detail into Java call sites. The cost is that the name is now part of your API and renaming the file no longer changes it for free.

`@JvmOverloads` on functions and constructors whose default parameters are genuinely useful to Java callers. The cost is that the generated overload set is published, so parameter order and defaults become breaking changes.

`@Throws` on functions that throw a checked exception a Java caller is expected to handle. The cost is small but real: you have opted into a discipline Kotlin deliberately does not have, and the annotation has to keep matching what the body throws.

`@JvmField` only where a field genuinely reads better than accessors, which is rare. The cost is the largest of the four: you can never put logic behind that name later.

And the answer that shows the judgment: if there are no Java callers, you owe nothing, and adding these annotations speculatively is the same mistake as any other premature API commitment. The general rule worth stating out loud is that all four are cheap to add and expensive to remove, so the question is never "would this be convenient" but "is there a caller who needs it".

</details>

## Real-world reps

- [ ] Find a place in Kotlin you have access to where a value comes from a Java library. Check whether its type is a platform type, and whether anything in the surrounding code would notice a null.
- [ ] Search a Kotlin codebase for `@Jvm` annotations. For each, work out whether a Java caller actually exists, and what the annotation is now preventing you from changing.
- [ ] Tomorrow: take one Kotlin file of top-level functions and work out the Java class name it generates. Decide whether a Java caller naming that class would be told anything true about the code.

## Going further

- [Docs: "Calling Java from Kotlin", Kotlin](https://kotlinlang.org/docs/java-interop.html)
- [Docs: "Calling Kotlin from Java", Kotlin](https://kotlinlang.org/docs/java-to-kotlin-interop.html)
- [Docs: "Null safety", Kotlin](https://kotlinlang.org/docs/null-safety.html)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
