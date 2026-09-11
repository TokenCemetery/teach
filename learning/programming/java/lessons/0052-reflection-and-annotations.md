---
title: 52. Reflection and Annotations
description: This is stage 8's capstone, reflection reads and calls a class's own shape at run time instead of at compile time, an annotation is inert data until something reads it reflectively, and every out-of-scope framework in this arc is built from exactly these two mechanisms
type: lesson
---

# Lesson 52. Reflection and Annotations

**Mission link:** This is stage 8's capstone. Lesson 49 closed the arc's judgment with a rubric for whether a framework earns its place, and said nothing about how a framework actually does what it does once adopted. Lesson 50 named the gate strong encapsulation puts in front of it. This lesson is the mechanism itself: reflection is how a dependency-injection container finds your classes and calls your constructors without your code ever calling it back, and an annotation is the inert label the same container reads to decide what to do, the two primitives every framework this arc kept out of scope is actually built from.
**Primary source:** [Package java.lang.reflect, Oracle](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/reflect/package-summary.html)
**Prerequisites:** [Lesson 49](0049-does-this-framework-earn-its-place.md), [Lesson 50](0050-the-module-system.md)

## Warm-up

1. ▢ Per lesson 49, what is a framework usually buying you, when it genuinely earns its place?

<details markdown="1"><summary>Check</summary>

Somebody else's already-solved problem: undifferentiated, necessary work exercised by far more users than your own service will ever produce. This lesson is about the mechanism that solved problem is usually built from underneath.

</details>

2. ▢ Per lesson 50, what does `opens` grant that `exports` does not, and what does neither grant on its own?

<details markdown="1"><summary>Check</summary>

`opens` grants reflective access to every member of a package at run time, public or not, while leaving it exactly as encapsulated at compile time as `exports` alone would not permit direct compilation against it. Neither grants anything to code that never actually calls `setAccessible`; the gate this lesson is about only matters once reflection is the thing trying to get through it.

</details>

## Know this

### Reflection reads and calls a class's own shape, discovered rather than compiled against

```java
Class<?> clazz = order.getClass();
for (Field field : clazz.getDeclaredFields()) {
    field.setAccessible(true);
    System.out.println(field.getName() + " = " + field.get(order));
}
```

The primary source describes this package plainly: it "provides classes and interfaces for obtaining reflective information about classes and objects," letting a program access "the fields, methods, and constructors of loaded classes" and use them "to operate on their underlying counterparts, within encapsulation and security restrictions." A `Class` object, `getDeclaredFields`, `getDeclaredMethods`, `Field.get`/`set`, `Method.invoke`: none of this is a library, it is the JVM answering "what does this object actually look like" and "call this method on it" at run time, for a class the calling code never imported and never compiled against. A dependency-injection container instantiating your class and populating its fields, an ORM mapping a row onto an entity, a serializer walking an object's fields to produce JSON: all three are this exact loop, wearing a different framework's name.

### Reflection operates "within encapsulation and security restrictions," which is lesson 50's gate

That phrase in the primary source is not incidental. `setAccessible(true)` on a private field in a package neither exported nor opened throws `InaccessibleObjectException`, exactly as lesson 50 showed; strong encapsulation applies to reflective access precisely as it applies to a direct compiled reference. This is why a framework's own setup guide routinely tells you to add an `opens` directive naming your entity package: the framework's field-injection loop above is reflection, and reflection needs the same gate any other cross-module access needs. A framework that seems to "just work" against your domain classes is not bypassing the module system, it is running inside a package you, or your build tool, already opened for it.

### An annotation is inert data until something reads it reflectively

```java
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.TYPE)
public @interface Table {
    String value();
}

@Table("orders")
public class Order { /* ... */ }
```

Writing `@Table("orders")` on `Order` does nothing by itself. It becomes something only once code calls `Order.class.getAnnotation(Table.class)` and reads `.value()`, exactly the same reflective machinery this lesson already described, applied to metadata instead of to fields or methods. `@Override` is the case that surprises people the other way: it is checked by the compiler and then thrown away entirely, present in source and gone from the class file, because its whole job is a compile-time check with nothing left for anything to read afterward.

### `@Retention` decides whether an annotation survives to be read reflectively at all

Three constants, from the JDK's own enumeration, and the difference between them decides whether a framework can ever see the annotation:

| Policy | What happens |
|---|---|
| `SOURCE` | discarded by the compiler; never reaches the class file at all |
| `CLASS` | recorded in the class file, but need not be retained by the VM at run time; **this is the default if `@Retention` is omitted entirely** |
| `RUNTIME` | recorded in the class file and retained by the VM at run time, so it can be read reflectively |

A custom annotation meant for a framework to discover has to declare `@Retention(RetentionPolicy.RUNTIME)` explicitly; leaving the meta-annotation off does not mean "no retention decided yet", it means `CLASS`, the documented default, which compiles cleanly, attaches to the element correctly, and is invisible to `getAnnotation` and `isAnnotationPresent` regardless. `@Target` is the annotation type's other declared contract, restricting which kinds of declarations, `TYPE`, `METHOD`, `FIELD`, and so on, it may even be placed on, checked by the compiler rather than by anything reflective.

### The capstone: what "does this framework earn its place" was always resting on

Lesson 49's rubric priced a framework from the outside: its transitive graph, its upgrade cadence, what removing it would touch. This lesson is what was happening on the inside the whole time: a framework scanning your classpath for a custom annotation, retained at `RUNTIME`, and reflectively instantiating and wiring together whatever it finds, entirely outside the call graph your own code ever writes down. Reading a stack trace three frames deep into a framework's own reflective dispatch, or finding out why a `@Component`-style annotation you copied from an example silently did nothing, is the same mechanism this lesson named, not a new mystery per class of framework. Every item in this arc's Out of scope list, Spring, Jakarta EE, Quarkus, Hibernate, is a particular, opinionated arrangement of exactly these two primitives, reflection and a retained annotation, and nothing else was ever going to be found underneath one.

```mermaid
flowchart TD
    A["@Table(\"orders\")<br>on class Order"] --> B{"@Retention on<br>@Table itself?"}
    B -->|"SOURCE"| C["Discarded by javac;<br>never in the class file"]
    B -->|"CLASS (default,<br>no @Retention written)"| D["In the class file;<br>VM need not keep it;<br>getAnnotation sees nothing"]
    B -->|"RUNTIME"| E["In the class file<br>AND kept by the VM"]
    E --> F["Framework calls<br>Order.class.getAnnotation(Table.class)"]
    F --> G["Framework reflects over<br>Order's fields, setAccessible(true)"]
    G --> H{"Field's package<br>exported or opened?<br>(lesson 50)"}
    H -->|"Neither"| I["InaccessibleObjectException"]
    H -->|"opens (or open module)"| J["Field read or set successfully"]
```

## Practice

1. ▢ A custom annotation `@Service` is declared with no `@Retention` meta-annotation at all, and placed on several classes. A framework calls `clazz.isAnnotationPresent(Service.class)` at run time. Predict the result.

<details markdown="1"><summary>Hint</summary>

Ask what retention policy an annotation type gets when `@Retention` is left off its own declaration entirely.

</details>

<details markdown="1"><summary>Check</summary>

`false`, for every class. With no `@Retention` written, the annotation type defaults to `RetentionPolicy.CLASS`, the JDK's own documented default: recorded in the class file, but not necessarily kept by the VM at run time, which is precisely the case here, so no reflective check ever sees it.

</details>

2. ▢ `@Override` is written on a method, compiles without complaint, and the method is confirmed by the compiler to actually override something. Does `method.getAnnotation(Override.class)` return anything at run time?

<details markdown="1"><summary>Check</summary>

No, it returns `null`. `@Override` is declared with `SOURCE` retention, discarded by the compiler entirely; it never reaches the class file in the first place, which is a stronger absence than `CLASS` retention, where the annotation exists in the file but is merely not kept by the VM.

</details>

3. ▢ A framework's field-injection code calls `field.setAccessible(true)` on a private field of an entity class whose package is `exported` by its module, but not `opened`. Predict the outcome.

<details markdown="1"><summary>Check</summary>

`InaccessibleObjectException`. `exports` grants compile- and run-time access to public types and members only; it does nothing for reflective access to a private field, which needs `opens` specifically. An exported-but-unopened package is exactly as closed to `setAccessible` as an unexported one.

</details>

4. ▢ A team defines a custom `@Column` annotation for their own lightweight object mapper, correctly marking it `@Retention(RetentionPolicy.RUNTIME)`, but leaves off `@Target` entirely. What does omitting `@Target` change about where the annotation may be written, and which mechanism, the compiler or reflection, enforces that?

<details markdown="1"><summary>Check</summary>

With no `@Target` specified, the annotation may be placed on any kind of declaration at all, since nothing restricts it; the compiler is what enforces a stated `@Target` when one exists, rejecting a misplaced annotation at compile time, not reflection, which only ever sees what already successfully compiled and was retained.

</details>

5. ▢ **Stage capstone.** Evaluating a framework against lesson 49's rubric, a team finds it uses reflection to populate private fields on domain classes carrying its own custom annotations. Name the two mechanisms this lesson taught that make this work, what the domain classes' own module declaration needs to grant for it to succeed, and what would silently break the same setup if the team, writing a similar annotation of their own elsewhere in the codebase, forgot one particular meta-annotation.

<details markdown="1"><summary>Check</summary>

The two mechanisms are reflection, `setAccessible`-based field access discovering members the framework's own code never compiled against, and a `RUNTIME`-retained annotation, read via `getAnnotation`, telling the reflective code which fields or classes to act on. For it to succeed, the domain classes' module needs to `opens` (or belong to an `open module`) the package those classes live in, since `exports` alone permits compilation against public members but not reflective access to private ones. Forgetting `@Retention(RetentionPolicy.RUNTIME)` on a custom annotation defaults it to `CLASS` retention, which compiles and attaches silently and is then invisible to every reflective check the framework performs, breaking the integration with no compiler error and no exception, only a feature that quietly never activates.

</details>

## Real-world reps

- [ ] Write a small class with private fields, iterate its `getDeclaredFields()` reflectively, and read each field's value with `setAccessible(true)` plus `Field.get`.
- [ ] Define a custom annotation, apply it to a class, and check with `isAnnotationPresent` both with and without `@Retention(RetentionPolicy.RUNTIME)` on its declaration, confirming the difference this lesson describes.
- [ ] Tomorrow: find one framework annotation already in a codebase you have access to, and check its own declaration for `@Retention` and `@Target`, rather than assuming both are what you'd expect.

## Going further

- [Package java.lang.reflect, Oracle](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/reflect/package-summary.html)
- [RetentionPolicy, Oracle](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/annotation/RetentionPolicy.html)
- [Retention, Oracle](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/annotation/Retention.html)
- [Lesson 49. Does This Framework Earn Its Place](0049-does-this-framework-earn-its-place.md)
- [Lesson 50. The Module System](0050-the-module-system.md)
- [The Module System](../reference/the-module-system.md): the stage 8 sheet
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
