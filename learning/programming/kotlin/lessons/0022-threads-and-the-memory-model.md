---
title: "22. Threads and the Memory Model"
description: "Why Kotlin has no memory model of its own on the JVM, the three constructs it spells as annotations instead of keywords, and the two guarantees a val does not give you"
type: lesson
---

# Lesson 22. Threads and the Memory Model

**Mission link:** Stage 5 opens here. Coroutines change how work is scheduled, not what one thread is allowed to see of another's writes, so the model underneath comes first.
**Primary source:** [Spec: "Threads and Locks", Java Language Specification, Java SE 21](https://docs.oracle.com/javase/specs/jls/se21/html/jls-17.html)
**Prerequisites:** [Lesson 21](0021-grouping-and-folding.md), [Lesson 2](0002-val-var-and-immutability.md), [Lesson 17](0017-delegation.md)

## Warm-up

1. ▢ What does `fold`'s initial value change, compared to `reduce`, and what does that let `fold` do that `reduce` cannot?

<details markdown="1"><summary>Check</summary>

`fold` uses the initial value as the accumulator on the first step, while `reduce` uses the first and second elements as the operation's two arguments. Two things follow: `fold`'s accumulator is whatever type you seeded it with, so it can build a map or any other shape rather than a bigger element, and `fold` on an empty collection returns the seed where `reduce` has nothing to return at all.

</details>

2. ▢ What exactly does `val` promise about the thing it holds?

<details markdown="1"><summary>Check</summary>

That the reference will not be reassigned. Nothing else. The object on the other end is as mutable as its own type allows, which is why a `val` holding a `MutableList` is still a list whose contents can change. Read-only is a property of the interface you hold, not of `val`.

</details>

3. ▢ In `val config by lazy { loadConfig() }`, what actually holds the value, and when does `loadConfig()` run?

<details markdown="1"><summary>Check</summary>

A `Lazy` instance created by `lazy { }`, which the property delegates its `getValue()` to. The initializer runs on the first read of `config`, not at construction, and every read after that returns the stored result. The property itself has no backing field of its own; the delegate object holds the state.

</details>

## Know this

**Kotlin on the JVM has no memory model of its own.** It compiles to the same bytecode Java does, so the rules deciding what one thread may see of another thread's writes are the Java Language Specification's, chapter 17 ([Threads and Locks](https://docs.oracle.com/javase/specs/jls/se21/html/jls-17.html)). That is why this lesson's primary source is a Java document: there is no Kotlin equivalent to read, and a Kotlin-flavoured retelling of it would be a worse version of something already written down.

So the model itself is not taught here. It is taught once, next door, and this arc links to it rather than repeating it: the [Java workspace's concurrency sheet](../../java/reference/concurrency.md) covers happens-before edges, visibility against atomicity, what each construct guarantees, and safe publication, in lookup form; the [Java workspace's glossary](../../java/GLOSSARY.md) pins the terms, **data race**, **happens-before**, **safe publication**, **platform thread** among them. Read the sheet alongside this lesson. What follows is only the part that is Kotlin's.

**Starting a thread.** `Thread { ... }.start()` works directly, because a lambda converts to the `Runnable` the constructor wants. The standard library also has `kotlin.concurrent.thread`, which creates and, by default, starts one, with `isDaemon`, `name` and `priority` available as named arguments ([kotlin.concurrent.thread](https://kotlinlang.org/api/core/kotlin-stdlib/kotlin.concurrent/thread.html)). Neither form changes anything about the model: what you get back is a `java.lang.Thread`.

**Three constructs Kotlin spells differently.** Kotlin has no `volatile`, `synchronized` or `final` keyword, because it targets more than the JVM. The same guarantees arrive as annotations and a function:

|Java|Kotlin|What it actually does|
|---|---|---|
|`volatile` field|`@Volatile` on a `var` property|Marks the JVM **backing field** volatile: reads and writes of that field are atomic, a write is always made visible to other threads, and a reader sees the side effects that led to the value it read ([Volatile](https://kotlinlang.org/api/core/kotlin-stdlib/kotlin.concurrent/-volatile/))|
|`synchronized` method|`@Synchronized` on a function|Marks the generated JVM method synchronized, guarded by the monitor of the instance, or of the class for a static method ([Synchronized](https://kotlinlang.org/api/core/kotlin-stdlib/kotlin.jvm/-synchronized/))|
|`synchronized (lock) { }`|`synchronized(lock) { }`|An ordinary inline function taking the lock explicitly, not a language construct|
|`final` field|`val` with a backing field|Compiles to a `final` field, which is what earns the specification's `final` field guarantee: the freeze happens when the constructor exits ([JLS 17.5](https://docs.oracle.com/javase/specs/jls/se21/html/jls-17.html))|

Two footnotes on that table, both from the API docs and both easy to trip over. `@Volatile` makes **backing field** operations atomic, so if a custom getter or setter performs several operations on the field, reading or writing the *property* through those accessors is not atomic. And `@Synchronized` is a JVM-only affair: the standard library's common declaration of it has been an error since Kotlin 2.1, because locking a class instance means nothing on a platform without monitors. It is also the wrong tool on an extension function, which compiles to a static method and would therefore lock the monitor of the compiled facade class rather than anything you meant; there, name the lock and use `synchronized(lock) { }`.

**Two guarantees a `val` does not give you.** This is where the Java habit and the Kotlin habit both mislead, in opposite directions.

A `val` is not thread safety. What the `final` field guarantee covers is publication of *that object's own fields*: a thread obtaining the reference after construction finished sees them correctly initialised. It says nothing about what those fields point at. A `val` holding a `MutableMap` shared across request threads is a data race on the map, and the `val` is doing exactly what lesson 2 said it does, freezing the reference.

`@Volatile` is not atomicity. It gives visibility, and atomicity of a single read and a single write of the field. `counter++` is a read followed by a write, so two threads can read the same value and both write the same increment, losing one. That is the visibility-against-atomicity distinction on the concurrency sheet, and the fix is an atomic type or a lock, not a stronger annotation.

**One default that is genuinely safer than the hand-written Java version.** `by lazy` is thread-safe unless you ask for otherwise. Its mode defaults to `LazyThreadSafetyMode.SYNCHRONIZED`, which uses a lock so that only a single thread initialises the value and the result is visible to all threads. The alternatives are explicit: `PUBLICATION` allows the initializer to run several times under concurrent first access, but only one computed value becomes the value and is visible to all; `NONE` uses no locks at all, and its behaviour under multiple threads is unspecified ([LazyThreadSafetyMode](https://kotlinlang.org/api/core/kotlin-stdlib/kotlin/-lazy-thread-safety-mode/)). So the double-checked-locking idiom people hand-write in Java is a language feature here, and `NONE` is the opt-out to reach for only when the property is provably touched by one thread. Note that `lateinit var` buys none of this: it is an ordinary non-final field with a null check.

Coroutines, from lesson 23 onwards, sit on top of all of this. They change what work gets scheduled onto which thread; they do not change what a data race is.

## Practice

1. ▢ A class has `@Volatile var counter = 0`. A hundred threads each run `counter++` a thousand times. Predict the final value, and name the guarantee that is missing.

<details markdown="1"><summary>Hint</summary>

Count the field operations in `counter++`. The annotation's promise is about one of them at a time.

</details>

<details markdown="1"><summary>Check</summary>

Something under 100,000, and unpredictably so. `@Volatile` gives visibility, plus atomicity of a single read and a single write of the backing field, and `counter++` is a read and then a write. Two threads can read 41, both write 42, and one increment is gone. What is missing is atomicity of the compound operation, which no annotation provides: use an atomic integer, or hold a lock across the read and the write.

</details>

2. ▢ `class UserCache { val entries = mutableMapOf<String, User>() }`, and one instance is shared by every request thread. Is the `val` enough? Say precisely what it does and does not guarantee.

<details markdown="1"><summary>Check</summary>

Not remotely. `val` freezes the reference, and because it compiles to a `final` field it earns the publication guarantee for the `UserCache` object's own fields: a thread that gets the reference after construction sees `entries` correctly initialised, pointing at the map. From there it guarantees nothing. Concurrent `put` and `get` on that `MutableMap` are unsynchronised accesses to shared mutable state, which is a data race with no happens-before edge. Two properties are being conflated: the reference cannot be reassigned, and the object cannot be mutated. `val` only gives the first.

</details>

3. ▢ Someone writes `@Synchronized fun MutableList<Item>.addChecked(item: Item) { ... }` and expects calls to be serialised per list. What actually gets locked?

<details markdown="1"><summary>Check</summary>

The monitor of the facade class the extension compiles into, because an extension function is a static method with the receiver passed as a parameter. There is no instance whose monitor could be taken, so every call on every list contends on one class-level monitor: too coarse to be what was wanted, and, since it is not the list's own monitor, no protection against code that locks the list directly. The API docs recommend the annotation only on member functions and properties, and `synchronized(lock) { }` with an explicit lock everywhere else.

</details>

4. ▢ Two threads read a `by lazy` property for the first time at the same instant. How many times does the initializer run, under the default mode, under `PUBLICATION`, and under `NONE`?

<details markdown="1"><summary>Check</summary>

Default (`SYNCHRONIZED`): once. A lock ensures a single thread initialises it, and the value is then visible to all threads. `PUBLICATION`: possibly more than once, since the initializer may be called several times on concurrent access, but only one computed value becomes the property's value and that one is visible to all. `NONE`: unspecified, because no locks are used at all, so this mode is a claim you are making about your own code rather than a mode the runtime enforces.

</details>

5. ▢ Which claim about Kotlin and the JVM memory model is correct?

    - a) Kotlin defines its own memory model, which is stricter than the JVM's one
    - b) Kotlin compiles to the JVM's model, spelling three of its constructs as annotations
    - c) Kotlin removes data races by making every val property immutable and deeply final
    - d) Kotlin defers the question to coroutines, which replace threads and their visibility rules

<details markdown="1"><summary>Check</summary>

**b)** is right: same bytecode, same model, and `@Volatile`, `@Synchronized` and `val` are the spellings of `volatile`, `synchronized` and `final`. (a) is false, and it is the comforting version: there is no Kotlin memory model on this platform to be stricter. (c) confuses `val` with deep immutability, which is this lesson's main trap. (d) has the layering backwards: coroutines are scheduled onto threads and inherit the model rather than replacing it.

</details>

## Real-world reps

- [ ] Read the Java workspace's concurrency sheet, sections Happens-before edges and Visibility against atomicity. Note which of the two your last concurrency bug actually violated.
- [ ] Find shared mutable state in Kotlin you have access to, held by a `val` and touched from more than one thread. Decide what makes it safe today, and whether that thing is a guarantee or a coincidence of timing.
- [ ] Tomorrow: search your own code for `@Volatile` and for `lateinit var`. For each hit, say in one sentence which guarantee it was reached for, and whether the construct actually gives that guarantee.

## Going further

- [Spec: "Threads and Locks", Java Language Specification, Java SE 21](https://docs.oracle.com/javase/specs/jls/se21/html/jls-17.html)
- [Concurrency sheet, Java workspace](../../java/reference/concurrency.md)
- [API: "Volatile", Kotlin](https://kotlinlang.org/api/core/kotlin-stdlib/kotlin.concurrent/-volatile/)
- [API: "LazyThreadSafetyMode", Kotlin](https://kotlinlang.org/api/core/kotlin-stdlib/kotlin/-lazy-thread-safety-mode/)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
