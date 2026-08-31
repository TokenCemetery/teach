---
title: 9. Interfaces
description: A contract with no state, plus the default methods that let one grow without breaking every implementor
type: lesson
---

# Lesson 9. Interfaces

**Mission link:** The mission asks you to model a domain without reaching for inheritance first, and an interface is where that starts: a contract with no state, which forces the question of what a caller needs to promise before any class exists to answer it.
**Primary source:** [Chapter 9. Interfaces, Java Language Specification, SE 25](https://docs.oracle.com/javase/specs/jls/se25/html/jls-9.html)
**Prerequisites:** [Lesson 5](0005-arrays-and-collections.md), [Lesson 7](0007-classes-and-objects.md)

## Warm-up

1. ▢ What value does an uninitialised `int` field have, and what happens if you try to read an uninitialised local variable of type `int` instead?

<details markdown="1"><summary>Check</summary>

A field defaults to `0` without you writing anything. A local has no default at all, and reading one before assignment is a compile-time error: `variable x might not have been initialized`.

</details>

2. ▢ On a `List<Integer>`, why does `list.remove(1)` do something different from `list.remove(Integer.valueOf(1))`?

<details markdown="1"><summary>Check</summary>

`List` overloads `remove`: one overload takes `int` and removes by index, the other takes `Object` and removes by value. The compiler chooses the overload from the static type of the argument, so the `int` literal `1` picks the index form and the boxed `Integer.valueOf(1)` picks the value form.

</details>

## Know this

An interface declares what a type can be asked to do, without saying how, and without holding any state of its own to do it with.

```java
interface Discount {
    double rate();
}
```

Nothing here says `public` or `abstract`. The compiler adds both: an interface method that has no body is implicitly `public` and `abstract`, and writing either modifier yourself is legal but pointless. Try to weaken that and the compiler stops you, for example by giving an implementation package access instead of public: `attempting to assign weaker access privileges; was public`.

### Fields are constants, and that is a smell more than a feature

A field on an interface follows the same implicitness, with an extra rule attached.

```java
interface Limits {
    int MAX = 100;
}
```

`MAX` is implicitly `public`, `static` and `final`. The `final` half is real: `Limits.MAX = 200;` fails with `cannot assign a value to static final variable MAX`. The consequence that catches people out is upstream of that: an interface field must carry an initialiser, because a `final` field needs a value from somewhere and an interface has no constructor to supply one in, so leaving it off is a compile-time error, `= expected`. That is the mirror image of a class field, which is content to sit at its default of `0`, `false` or `null` until something assigns to it (lesson 7); an interface has no instance to hold a default in, so the value has to exist at compile time.

Because the field arrives `public static final` for free, an interface will happily serve as a bag of constants that anyone can `import static`. Resist it. Every class that implements the interface inherits those constants into its own namespace whether it wants them or not, and the constants become part of the interface's public API even though they say nothing about behaviour, which is the one thing an interface exists to describe. A group of constants that is not a behavioural contract belongs on a class with a private constructor, or on an enum (lesson 12), not on an interface.

### Default methods solve an evolution problem

```java
interface Discount {
    double rate();

    default double apply(double price) {
        return price * (1 - rate());
    }
}
```

Before default methods (final in Java 8), adding `apply` to a published interface would have broken every class that already implements `Discount`, since each one would suddenly be missing a method the interface now demands. A `default` method supplies a body, so existing implementors keep compiling unchanged and simply inherit the new behaviour.

The cost is that a default method cannot see instance state, because the interface holds none: it can only call other methods declared on the same interface, ones that an implementing class supplies. `apply` above only works because `rate()` exists to call; a default method has no field of its own to read.

### static and private methods keep the contract clean

```java
interface Discount {
    double rate();

    private double clamp(double value) {
        return Math.max(0, Math.min(1, value));
    }

    default double apply(double price) {
        return price * (1 - clamp(rate()));
    }

    static Discount none() {
        return () -> 0.0;
    }
}
```

`clamp` (private interface methods, Java 9) exists only to be called from `apply` or another method inside `Discount`; no implementor and no caller can see it, which is exactly the point of writing one, sharing logic between default methods without adding it to the public contract. `none` (static interface methods, Java 8) belongs to the interface itself rather than to any instance, so it is called as `Discount.none()` and never through an implementing object, the same way a static method on a class is never called through an instance of it. Running the two together confirms the split:

```java
Discount tenPercent = () -> 0.10;
System.out.println(tenPercent.apply(200.0));       // 180.0
System.out.println(Discount.none().apply(200.0));  // 200.0
```

### When a class inherits two unrelated defaults with the same signature

```java
interface Greeter {
    default String greet() {
        return "hello from Greeter";
    }
}

interface Welcomer {
    default String greet() {
        return "hello from Welcomer";
    }
}

class Both implements Greeter, Welcomer {
}
```

This fails to compile, and the message names the conflict rather than either interface alone:

```text
error: types Greeter and Welcomer are incompatible
class Both implements Greeter, Welcomer {
      ^
  class Both inherits unrelated defaults for greet() from types Greeter and Welcomer
```

The compiler will not guess which default you meant, so `Both` has to override `greet` and choose, and the qualified form `Interface.super.method()` is how it reaches a specific one instead of the one it would have inherited on its own:

```java
class Both implements Greeter, Welcomer {
    @Override
    public String greet() {
        return Greeter.super.greet() + " and " + Welcomer.super.greet();
    }
}
```

That prints `hello from Greeter and hello from Welcomer`. Without the qualifier, plain `super.greet()` would not compile inside `Both`, since ordinary `super` names a single superclass and `Both` has two superinterfaces offering the same method.

### Functional interfaces, lambdas and method references

```java
@FunctionalInterface
interface PriceRule {
    double apply(double price);
}
```

A functional interface has exactly one abstract method, ignoring anything inherited from `Object`, and that single method is what let `() -> 0.10` above stand in for a `Discount`: the lambda supplies the missing method and the compiler builds an instance around it. `@FunctionalInterface` (Java 8) does not make an interface functional; the shape of its methods does that regardless of the annotation. What the annotation buys is a build-time check that the shape holds, so a second abstract method added later fails the build instead of silently breaking every lambda written against the interface:

```text
error: Unexpected @FunctionalInterface annotation
@FunctionalInterface
^
  PriceRule is not a functional interface
    multiple non-overriding abstract methods found in interface PriceRule
```

A method reference is the other way to supply that one method, pointing at a method that already exists instead of writing a lambda body:

```java
PriceRule doubled = price -> price * 2;
PriceRule positive = Math::abs;
```

Both are instances of `PriceRule`, nothing more exotic than that. Streams and collectors, where lambdas and method references show up constantly, belong to stage 3; here the point is only that a functional interface is what a lambda's type actually is.

### Abstract class or interface

Both let you declare a method with no body and force a subtype to supply one, so the choice between them is not about that. It is about state and inheritance. An abstract class can hold instance fields and run a constructor, so it can share state as well as behaviour between subclasses, but a class extends only one of them. An interface holds no state and has no constructor, but a class implements as many of them as it needs. Reach for an abstract class when the subtypes genuinely share fields or construction logic; reach for an interface when the shared part is only a contract, since implementing one costs nothing and leaves room to implement others besides. Lesson 10 covers what `abstract class` gives you in full; the decision between the two matters before the mechanics do.

### The interface as the unit of API design

A parameter typed as an interface states a promise instead of naming a delivery mechanism: `void charge(Discount discount)` asks only for a `rate()`, not for whichever class happens to implement it today. Designing the interface is deciding the smallest thing a caller must promise, and that is usually smaller than the first draft: one abstract method if a lambda should be able to satisfy it, and no field, ever. A `sealed interface` (lesson 11) closes that promise to a fixed, known list of implementations instead of leaving it open to anyone; until then, the open kind is the default, and the question worth asking of any interface is what it would cost an implementor to keep the promise it makes.

## Practice

1. ▢ A `default` method and a `private` method on the same interface both have a body. What can call the `private` one that cannot call the `default` one, and why write a `private` method at all?

<details markdown="1"><summary>Check</summary>

Nothing outside the interface can call the `private` method: not an implementing class, not a caller, not even a subinterface, only another method declared in the same interface body. Write one when two or more `default` methods need the same logic and that logic should not become part of the interface's public contract, the way `clamp` backs `apply` without ever being something a `Discount` implementor could call.

</details>

2. ▢ Predict the output, and explain it.

   ```java
   interface Logger {
       default String tag() {
           return "[LOG]";
       }
   }

   interface Auditor {
       default String tag() {
           return "[AUDIT]";
       }
   }

   class Recorder implements Logger, Auditor {
       public String tag() {
           return Auditor.super.tag() + Logger.super.tag();
       }
   }

   System.out.println(new Recorder().tag());
   ```

<details markdown="1"><summary>Check</summary>

`[AUDIT][LOG]`.

`Recorder` inherits unrelated defaults named `tag` from both interfaces, so it must override the method itself, exactly as `Both` had to above. The qualified calls pick one default each, in the order written, and concatenate the results; there is no other rule choosing between them.

</details>

3. ▢ This interface fails to compile. Name the line, and quote the compiler's error.

   ```java
   interface Retry {
       int ATTEMPTS;
   }
   ```

<details markdown="1"><summary>Check</summary>

Line 2, `= expected`. `ATTEMPTS` is implicitly `public static final`, and a `final` field needs a value from somewhere; an interface has no constructor to assign one in, so the initialiser has to be written in the declaration itself.

</details>

4. ▢ Find the bug.

   ```java
   interface Cache {
       List<String> KEYS = new ArrayList<>();
   }

   class Left implements Cache {
       void store(String key) { KEYS.add(key); }
   }

   class Right implements Cache {
       void purge() { KEYS.clear(); }
   }
   ```

<details markdown="1"><summary>Hint</summary>

`KEYS` is `final`. Ask what `final` actually promises, and about what.

</details>

<details markdown="1"><summary>Check</summary>

`KEYS` is one list, shared by every class that implements `Cache`, because an interface field is `static` whether you write that or not. Calling `Right.purge()` wipes out everything `Left.store` put there, and neither class looks like it touches the other's state. `final` only stops the field being reassigned to a different list; it says nothing about the object on the other end, so a `final` list can still be cleared. This is the constant-field smell doing real damage rather than sitting quietly.

</details>

5. ▢ A method signature reads `void notify(EmailSender sender)`, where `EmailSender` is a concrete class with a public constructor and one public method, `send(String to, String body)`. A reviewer wants a caller to be able to substitute an SMS or push notifier later without touching `notify`. What do you change, and what does the new type expose?

<details markdown="1"><summary>Check</summary>

Change the parameter's type to an interface, for example `Notifier` with a single method `send(String to, String body)`, and have `notify` depend on that interface instead of on `EmailSender`. `EmailSender` becomes one implementation among several, and an SMS or push notifier becomes another, with `notify` unchanged because it only ever asked for the one method it calls. The interface should expose exactly that method and nothing else `EmailSender` happens to have, since anything extra is a promise every future implementor has to keep for no benefit to `notify`.

</details>

## Real-world reps

- [ ] Write an interface with one abstract method and a default method that calls it, implement it twice, and confirm both implementations get the default behaviour for free without writing it themselves.
- [ ] Reproduce the two-unrelated-defaults conflict from this lesson, read the compiler's error in full, then fix it with a qualified `Interface.super.method()` call.
- [ ] Find a `public static final` field on an interface in code you know, and decide whether it is a genuine part of a behavioural contract or a constant that should move to a class or an enum instead.
- [ ] Tomorrow: find a method in code you know that takes a concrete class as a parameter but only calls one or two methods on it. Decide whether an interface would let a caller substitute a different implementation, and write the smallest version of that interface.

## Going further

- [Chapter 9. Interfaces, Java Language Specification, SE 25](https://docs.oracle.com/javase/specs/jls/se25/html/jls-9.html): the implicit modifiers, the interface method body rules, and the functional interface definition, stated precisely
- [`FunctionalInterface`, Java SE 25 API](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/FunctionalInterface.html): what the annotation checks, and that the compiler treats a qualifying interface as functional with or without it
- [Default Methods, The Java Tutorials](https://docs.oracle.com/javase/tutorial/java/IandI/defaultmethods.html): the evolution problem worked through with the example that motivated the feature
- [Modelling](../reference/modelling.md): the reference sheet for this stage
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
