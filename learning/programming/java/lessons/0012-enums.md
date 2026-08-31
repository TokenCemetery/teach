---
title: 12. Enums
description: A fixed set of instances the language guarantees, with room for state and behaviour on each one
type: lesson
---

# Lesson 12. Enums

**Mission link:** An enum is how you tell the compiler that a domain concept has a fixed, small set of values, the same modelling promise a sealed interface makes for an open-ended shape, and choosing correctly between the two is part of modelling a domain without reaching for inheritance first.
**Primary source:** [`Enum`, Java SE 25 API](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/Enum.html)
**Prerequisites:** [Lesson 7](0007-classes-and-objects.md), [Lesson 11](0011-sealed-types-and-pattern-matching.md)

## Warm-up

1. ▢ A sealed interface's permitted subtypes are covered by a `switch` expression with no `default`. Why is the missing `default` the point, rather than an oversight?

<details markdown="1"><summary>Check</summary>

Because the compiler already proved every permitted subtype is handled. A `default` would swallow a newly permitted subtype silently; leaving it out means adding one breaks compilation at every switch that has not been updated for it, which is the exhaustiveness check doing its job.

</details>

2. ▢ What happens to a class's implicit no-argument constructor the moment you declare a constructor of your own?

<details markdown="1"><summary>Check</summary>

It disappears. The compiler only supplies the implicit one when you have written none at all, so if a no-argument constructor is still wanted, it has to be written explicitly alongside the others.

</details>

## Know this

### The constants are the only instances

The `enum` declaration, final in Java 5, declares a class with a fixed set of named constants and nothing outside that set:

```java
enum Suit { CLUBS, DIAMONDS, HEARTS, SPADES }
```

This declares a class, `Suit`, with exactly four instances, one per named constant, and no others can ever exist. `Suit` implicitly extends `java.lang.Enum<Suit>`, which is why an enum cannot extend anything else, and the compiler refuses `new` outright:

```text
error: enum classes may not be instantiated
```

Because every value of the type is one of these four fixed objects, `==` compares them correctly and is the idiomatic comparison, the same guarantee that made reference equality the right tool for interned strings back in [Lesson 2](0002-identity-and-equality.md), here provided by the language for a type you declared yourself rather than by a pool.

### Constructors, fields and methods

An enum constant can carry state, computed once when the class initialises:

```java
enum Planet {
    MERCURY(3.303e+23, 2.4397e6),
    VENUS(4.869e+24, 6.0518e6),
    EARTH(5.976e+24, 6.37814e6);

    private final double mass;
    private final double radius;

    Planet(double mass, double radius) {
        this.mass = mass;
        this.radius = radius;
    }

    double surfaceGravity() {
        double g = 6.67300e-11;
        return g * mass / (radius * radius);
    }
}
```

`Planet.EARTH.surfaceGravity()` gives `9.80`. The constructor runs once per constant, in declaration order, before any other code can observe the type. An enum constructor is implicitly private and cannot be declared otherwise: writing `public Planet(...)` fails with `modifier public not allowed here`, since letting outside code call it would contradict the fixed-set guarantee.

### Constant-specific bodies

A constant can override a method with its own body instead of the enum sharing one implementation:

```java
enum Operation {
    PLUS {
        public int apply(int a, int b) { return a + b; }
    },
    MINUS {
        public int apply(int a, int b) { return a - b; }
    };

    public abstract int apply(int a, int b);
}
```

`Operation.PLUS.apply(2, 3)` gives `5`, `Operation.MINUS.apply(2, 3)` gives `-1`, each constant running its own code behind one abstract method. This costs something invisible in the declaration: `Operation.PLUS.getClass()` is `Operation$1` and `Operation.MINUS.getClass()` is `Operation$2`, two different anonymous subclasses of `Operation`, so `PLUS.getClass() == MINUS.getClass()` is `false`. An enum with no constant bodies has no such split: every constant of `Suit` reports the same `getClass()`, `Suit` itself.

### Enums implementing interfaces

An enum can implement one or more interfaces, since implementing an interface costs it nothing it has not already spent by extending `Enum`:

```java
interface Describable { String describe(); }

enum Operation implements Describable {
    PLUS { public int apply(int a, int b) { return a + b; } },
    MINUS { public int apply(int a, int b) { return a - b; } };

    public abstract int apply(int a, int b);

    public String describe() { return "operation " + name(); }
}
```

This is how an enum becomes a strategy implementation with a closed, known set of strategies, one object per case, satisfying whatever interface the rest of the code depends on.

### `values()`, `valueOf`, `name()` and `ordinal()`

`values()` is a static method the compiler generates, and it hands back a new array on every call:

```java
Suit[] a = Suit.values();
Suit[] b = Suit.values();
a == b;          // false
a[0] = Suit.SPADES;
Suit.values();   // [CLUBS, DIAMONDS, HEARTS, SPADES], unaffected
```

Mutating the array you were handed changes nothing else, and calling `values()` inside a loop allocates a fresh array on every iteration, which is worth knowing before doing it in anything hot.

`valueOf(String)` looks a constant up by its exact declared name and throws when there is no match:

```text
java.lang.IllegalArgumentException: No enum constant Suit.clubs
```

`name()` returns that declared name, and `ordinal()` returns the constant's position in declaration order, starting at zero. `compareTo` compares by that ordinal, so it always follows declaration order: `Suit.CLUBS.compareTo(Suit.SPADES)` is negative and `Suit.SPADES.compareTo(Suit.CLUBS)` is positive, purely because `CLUBS` was declared first. `ordinal()` is for the language's own use, in `EnumMap`, `EnumSet` and `compareTo`, and it must never be persisted to a file, a database column or a message: insert a constant in the middle of the declaration later, and every ordinal after it shifts to mean something else, silently, with nothing to catch the mismatch. If a stored value needs to survive that kind of change, store `name()` instead, since a rename is at least visible in the diff that caused it.

### `EnumMap` and `EnumSet`

```java
EnumSet<Suit> set = EnumSet.of(Suit.SPADES, Suit.CLUBS, Suit.HEARTS);
set;   // [CLUBS, HEARTS, SPADES]
```

Inserted as `SPADES, CLUBS, HEARTS`, iterated as `CLUBS, HEARTS, SPADES`: both `EnumSet` and `EnumMap` ignore insertion order entirely and iterate in the enum's declaration order, because internally they index by `ordinal()` into an array-backed structure sized to the constant count, rather than hashing or comparing. That is also why they beat a `HashMap` or a `HashSet` for an enum key: no hashing, no boxing of the key beyond what the enum constant already is, and a bit-set-like representation for `EnumSet` that makes membership tests and set operations run in constant time against the fixed universe of constants.

### `switch` over an enum

A `switch` **expression** that names every constant needs no `default`, because the compiler can already see that every possibility is covered:

```java
enum Direction { NORTH, SOUTH, EAST, WEST }

String label(Direction d) {
    return switch (d) {
        case NORTH -> "up";
        case SOUTH -> "down";
        case EAST -> "right";
        case WEST -> "left";
    };
}
```

Switch expressions were finalised in Java 14. Leave one constant out and the same code fails to compile:

```text
error: the switch expression does not cover all possible input values
```

That error is a compile-time favour, and it depends on the switch being recompiled against the enum it switches on. Compile this method against a three-constant version of `Direction`, then add a fourth constant to `Direction` and recompile only the enum, leaving the already-compiled switch class file untouched, and calling the old code with the new constant throws at run time instead of failing to compile:

```text
Exception in thread "main" java.lang.MatchException
	at UseDirection.label(UseDirection.java:3)
```

`MatchException` was added with pattern matching for `switch`, final in Java 21, as the general run-time signal that a switch was evaluated and nothing matched. The lesson is the same one every binary-compatibility hazard teaches: exhaustiveness is checked once, at compile time, against whatever the enum looked like then, and separately compiling and shipping the two sides is what lets them drift apart.

### The enum as a singleton

Because the language itself refuses `new` and guarantees exactly one instance per declared constant, an enum constant is a singleton the language enforces rather than one a design pattern has to defend by convention, including against serialisation: `Enum` documents that deserialising a constant produces the existing instance rather than a new one. A single-constant enum is accordingly a common way to write a singleton in Java.

### Enum versus sealed interface

Both close a set of alternatives against the addition of an uncovered one, but an enum's alternatives are interchangeable values of one shape sharing one field set, while a sealed interface's alternatives, usually records from [Lesson 11](0011-sealed-types-and-pattern-matching.md), are its own choice whenever the alternatives carry genuinely different data: reach for an enum when every case is a label with at most the same handful of per-constant fields, and for a sealed interface when the cases disagree about what data they even hold.

## Practice

1. ▢ Predict what this prints, then explain why the second `Suit.values()` call is unaffected by the mutation.

   ```java
   Suit[] a = Suit.values();
   a[0] = Suit.SPADES;
   System.out.println(a[0]);
   System.out.println(Suit.values()[0]);
   ```

<details markdown="1"><summary>Check</summary>

`SPADES`, then `CLUBS`.

`values()` returns a new array each time it is called, copied from the constants the language holds internally, so mutating the array named `a` has no effect on the array a later call returns.

</details>

2. ▢ Find the bug. A service stores a user's chosen `Priority` as the integer from `priority.ordinal()`, and reads it back with `Priority.values()[storedOrdinal]`. Months later, someone inserts a new constant in the middle of the `Priority` declaration to fill a gap in the ordering. What breaks, and for whom?

<details markdown="1"><summary>Check</summary>

Every row stored before the insertion now decodes to the wrong constant, because `ordinal()` is a position in declaration order and every constant after the insertion point shifted by one. Nothing throws: `values()[storedOrdinal]` is still a valid index into a longer array, so it silently returns a different, wrong `Priority` for every affected row, and it surfaces as a data problem, not a Java problem, for whoever notices the wrong priority later. Storing `name()` and decoding with `valueOf` would have failed loudly instead, with an `IllegalArgumentException`, only if the name itself were removed or renamed, which is the visible, reviewable change.

</details>

3. ▢ Write a `Coin` enum with constants `PENNY`, `NICKEL`, `DIME`, `QUARTER`, each carrying its value in cents as constructor state, plus a method that returns that value. Then write a `switch` expression over `Coin` that returns `"small"` for `PENNY` and `NICKEL` and `"large"` for `DIME` and `QUARTER`, with no `default`.

<details markdown="1"><summary>Check</summary>

```java
enum Coin {
    PENNY(1), NICKEL(5), DIME(10), QUARTER(25);

    private final int cents;
    Coin(int cents) { this.cents = cents; }
    int cents() { return cents; }
}

String size(Coin c) {
    return switch (c) {
        case PENNY, NICKEL -> "small";
        case DIME, QUARTER -> "large";
    };
}
```

Multiple constants can share one arm of a `switch` expression, separated by commas, and the compiler still checks that all four are covered before it will accept the missing `default`.

</details>

4. ▢ You are modelling an HTTP method: `GET`, `HEAD`, `POST`, `PUT`, `DELETE`, `PATCH`. Each one needs to answer whether it is safe and whether it is idempotent. Would you reach for an enum or a sealed interface of records here, and why?

<details markdown="1"><summary>Check</summary>

An enum. Every method is a label carrying exactly the same two boolean facts, decided once and fixed for the life of the type; nothing about `GET` needs data that `POST` does not also have room for. A sealed interface earns its keep when the alternatives disagree about what data they hold, which is not the case here: six constants with two constructor arguments each, or two constant-specific overrides if the answers are better read as behaviour than as data, is the whole design.

</details>

5. ▢ A `switch` expression over a `DayType` enum handles all three of its constants with no `default`, and ships inside a library. A second team, in a separate build, adds a fourth constant to `DayType` and deploys only the updated library jar, without rebuilding the code that contains the switch. What happens the first time that code runs with the new constant, and what step, skipped here, would have turned this into a compile error instead?

<details markdown="1"><summary>Check</summary>

The switch throws `MatchException` at run time, since none of its three cases match the new constant and the exhaustiveness check that would have caught this only runs at compile time, against whichever version of `DayType` was on the classpath then. Rebuilding the switch's own code against the updated library, rather than only replacing the jar, would have forced a compile-time failure naming the missing case instead of a run-time exception naming nothing useful.

</details>

## Real-world reps

- [ ] Find an enum in code you have written or read, and check every `switch` over it for a `default` arm; decide for each one whether that `default` is hiding the exhaustiveness check or genuinely handling an open-ended "anything else" case.
- [ ] Take a set of related constants in your own code that are still bare `int` or `String` values, and rewrite them as an enum with a constant-specific method replacing whatever `if` chain currently reads them.
- [ ] Search your own code, or a project you can read, for every call to `ordinal()`, and check whether any of them cross a boundary such as a database column, a file format or a network message, where a reordered enum would corrupt stored data without an exception to announce it.
- [ ] Tomorrow: pick a closed set of alternatives in code you already have, whichever shape it is written in today, and check it against the enum-versus-sealed-interface rule from this lesson.

## Going further

- [`Enum`](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/Enum.html): the full contract for `name`, `ordinal`, `compareTo` and singleton serialisation
- [`EnumSet`](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/EnumSet.html): the array-backed set built for a fixed enum universe
- [`EnumMap`](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/EnumMap.html): the counterpart map, ordered by declaration
- [JLS §8.9, Enum Classes](https://docs.oracle.com/javase/specs/jls/se25/html/jls-8.html#jls-8.9): the full specification, including constant-specific class bodies
- [Modelling](../reference/modelling.md): the reference sheet for this stage
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
