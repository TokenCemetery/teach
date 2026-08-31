---
title: 11. Sealed Types and Pattern Matching
description: A closed set of alternatives, and a compiler that checks you handled all of them
type: lesson
---

# Lesson 11. Sealed Types and Pattern Matching

**Mission link:** This is where "model a domain without reaching for inheritance first" stops being an aspiration: a sealed interface of records states every alternative up front, and the compiler, not a code reviewer, is what notices when a `switch` has not handled a new one.
**Primary source:** [JEP 441: Pattern Matching for switch](https://openjdk.org/jeps/441)
**Prerequisites:** [Lesson 9](0009-interfaces.md), [Lesson 10](0010-inheritance-and-composition.md)

## Warm-up

1. ▢ A superclass constructor calls a method that the subclass overrides, and the override reads a field the subclass declares. What does it see, and why?

<details markdown="1"><summary>Check</summary>

The field's default value, not whatever the subclass constructor was about to assign it, because the superclass constructor runs to completion before any subclass field initialiser runs. A `private int value = 42;` read this way prints `0`.

</details>

2. ▢ An interface declares `int MAX = 10;`. Why does everyone call this a smell rather than a feature, even though it compiles and works?

<details markdown="1"><summary>Check</summary>

An interface field is implicitly `public static final`, so it is not a private implementation detail: every implementor inherits it into its own namespace whether or not it is relevant there, and anyone can read it straight off the interface without implementing anything. Trying to assign one, `Config.MAX = 20;`, gets `cannot assign a value to static final variable MAX`. Constants belong on the type that owns their meaning, not on a contract that happens to be a convenient place to park them.

</details>

## Know this

### Closing the set with `sealed`

```java
sealed interface Shape permits Circle, Square, Rectangle {}
record Circle(double radius) implements Shape {}
record Square(double side) implements Shape {}
record Rectangle(double width, double height) implements Shape {}
```

`sealed`, final in Java 17, names every type allowed to extend or implement it. An ordinary interface is open: any class anywhere can implement `Shape`, so code that branches on which kind of `Shape` it has can never be sure it has seen them all. A sealed interface closes that: `Circle`, `Square` and `Rectangle` are the whole set, forever, as far as this compilation unit's dependents are concerned.

### What a permitted subtype must be

Every type named in `permits` must itself be `final`, `sealed` or `non-sealed`, and it must live in the same module as the sealed type, or the same package if there is no module. Leaving a permitted type unmarked does not compile:

```text
error: sealed, non-sealed or final modifiers expected
```

The requirement is what keeps the set closed at every level: a `sealed` subtype hands the decision to its own `permits` clause, a `final` one stops there, and `non-sealed` deliberately reopens it, which is a choice you have to write down rather than one that happens by omission. When `permits` is left off entirely, the compiler infers it from whichever subtypes are declared in the same source file, which is convenient for a small hierarchy but says nothing different from writing it out.

### The pattern form of `instanceof`

```java
Object o = new Circle(4);
if (o instanceof Circle c) {
    System.out.println(c.radius());
}
```

`instanceof` with a pattern, final in Java 16, tests the type and binds a variable in one step: `c` exists and is typed `Circle` for the rest of the branch where the test is known to be true, including later in a chain of `&&`. Before this, the same code needed a cast right after the test, repeating the type the `instanceof` had just checked.

### Exhaustive `switch`, and why no `default`

```java
static double area(Shape s) {
    return switch (s) {
        case Circle c -> Math.PI * c.radius() * c.radius();
        case Square sq -> sq.side() * sq.side();
        case Rectangle r -> r.width() * r.height();
    };
}
```

Pattern matching for `switch`, final in Java 21, lets a `case` label be a type pattern, and when the selector's type is `sealed` the compiler can prove the `switch` is exhaustive from the `permits` list alone, with no `default` needed. Delete the `Rectangle` case and this stops compiling:

```text
error: the switch expression does not cover all possible input values
```

That message is the entire point of leaving `default` off. With a `default`, a later `Triangle` added to `permits` compiles cleanly and silently falls into whatever the `default` branch does. Without one, adding `Triangle` breaks every `switch` over `Shape` that has not been taught about it, at compile time, at the exact line that needs a new case. A `default` on a sealed `switch` is not caution, it is turning off the one thing sealing bought.

### Record patterns

```java
record Point(int x, int y) {}
sealed interface Shape permits Circle, Rectangle {}
record Circle(Point centre, double radius) implements Shape {}
record Rectangle(Point topLeft, Point bottomRight) implements Shape {}

static String describe(Shape s) {
    return switch (s) {
        case Circle(Point(var x, var y), var r) -> "circle radius " + r + " at " + x + "," + y;
        case Rectangle(Point(var x1, var y1), Point(var x2, var y2)) ->
            "rectangle " + x1 + "," + y1 + " to " + x2 + "," + y2;
    };
}
```

Record patterns, final in Java 21 alongside pattern matching for `switch`, deconstruct a record's components in the pattern itself, `Circle(Point(var x, var y), var r)` pulling `x` and `y` out of the nested `Point` in one match. Running this against `Circle(new Point(1, 2), 5)` prints `circle radius 5.0 at 1,2`. A nested pattern that names a specific type only matches when the value is actually that type: given a sealed `Coord` of `Cartesian` and `Polar`, a `case Located(Cartesian(var x, var y))` simply does not match a `Located` holding a `Polar`, and control falls through to whichever case does, the same as any other `case` that fails to match.

### `when` guards

```java
case Login(var user, var attempt) when attempt > 3 -> user + " locked out";
case Login(var user, var attempt) -> user + " logged in, attempt " + attempt;
```

A `when` clause adds a boolean condition to a case that has already matched the pattern; if the guard is false, the `switch` moves to the next label as though the pattern itself had not matched. Order matters for the same reason it always does with the first-match semantics of `switch`: the guarded case has to come before the unguarded one that would otherwise catch every `Login`.

### `null` in a pattern `switch`

An ordinary `switch` throws on a `null` selector, and a pattern `switch` still does, unless a `case null` label says otherwise:

```java
return switch (s) {
    case Circle c -> "circle";
    case Square sq -> "square";
};
```

Calling this with `null` throws `java.lang.NullPointerException` at the `switch` itself, exactly as an old-style `switch` on a `null` `String` always has. Adding `case null -> "no shape";` before the type patterns changes that: `null` now matches the `null` label instead of raising anything, and every other value still reaches the type patterns as before. The rule is symmetric with `default`: a `case null` label is consulted first for a `null` selector, a `default` label is consulted for anything that matched no other label, and the two are independent, so a pattern `switch` can have both, either, or neither.

### The modelling idea

A sealed interface whose permitted subtypes are records is a closed sum of alternatives: exactly one of a fixed set of shapes, each carrying its own data, with no shared mutable state and no method to override. This is what a visitor pattern and an `instanceof` chain were both working around: the visitor pattern gets double dispatch at the cost of a class per operation, and an `instanceof` chain gets directness at the cost of no exhaustiveness check, ever. A sealed hierarchy with pattern matching over it gets both, directness and a compiler-checked exhaustiveness, because the set of shapes is closed and the language now knows how to prove a `switch` has covered it.

### Sealed hierarchy or enum

Both close a set. A `sealed` hierarchy is for alternatives that carry different data or behaviour per case, `Circle` needs a radius and `Rectangle` needs two, where an enum constant cannot vary its shape that way. An enum is for a fixed set of interchangeable instances that share one shape and mostly differ by identity, a day of the week or a status code. Lesson 12 comes back to what an enum constant can and cannot carry.

## Practice

1. ▢ Predict what each call prints, and explain why the order of the first two cases matters.

   ```java
   sealed interface Event permits Login, Logout {}
   record Login(String user, int attempt) implements Event {}
   record Logout(String user) implements Event {}

   static String describe(Event e) {
       return switch (e) {
           case Login(var user, var attempt) when attempt > 3 -> user + " locked out";
           case Login(var user, var attempt) -> user + " logged in, attempt " + attempt;
           case Logout(var user) -> user + " logged out";
       };
   }

   describe(new Login("ana", 5));
   describe(new Login("bo", 1));
   describe(new Logout("cy"));
   ```

<details markdown="1"><summary>Check</summary>

```text
ana locked out
bo logged in, attempt 1
cy logged out
```

`ana` matches the first `Login` pattern and the guard `attempt > 3` is true, so it stops there. `bo` matches the same pattern but the guard is false, so the `switch` moves on to the second, unguarded `Login` case. Swap the two `Login` cases and the guard never gets a chance to matter, since the unguarded case would catch every `Login` first.

</details>

2. ▢ Find the bug.

   ```java
   sealed interface Payment permits CardPayment, CashPayment {}
   record CardPayment(String cardNumber, double amount) implements Payment {}
   class CashPayment implements Payment {
       double amount;
   }
   ```

<details markdown="1"><summary>Hint</summary>

Every type named in `permits` has to declare what it is willing to let happen below it, even if the answer is nothing.

</details>

<details markdown="1"><summary>Check</summary>

`CashPayment` implements a sealed interface without being `final`, `sealed` or `non-sealed` itself, so it does not compile: `error: sealed, non-sealed or final modifiers expected`. Adding `final` to `class CashPayment` is the fix here, since nothing needs to extend it.

</details>

3. ▢ Predict what happens, and explain the rule.

   ```java
   sealed interface Shape permits Circle, Square {}
   record Circle(double radius) implements Shape {}
   record Square(double side) implements Shape {}

   static String describe(Shape s) {
       return switch (s) {
           case Circle c -> "circle";
           case Square sq -> "square";
       };
   }

   describe(null);
   ```

<details markdown="1"><summary>Check</summary>

`NullPointerException`, thrown by the `switch` itself, because a pattern `switch` still rejects a `null` selector unless one of its labels is `case null`. Adding `case null -> "no shape";` before the type patterns changes the outcome to that string instead of the exception, and every non-null `Shape` still reaches the type patterns exactly as before.

</details>

4. ▢ A colleague adds `Triangle` to `permits` on an existing sealed `Shape`, then adds a `class Triangle` that implements it correctly. Every `switch` over `Shape` in the codebase either has a `default` or does not. Which group breaks, when, and is that good or bad?

<details markdown="1"><summary>Check</summary>

The `switch`es with no `default` break, immediately, at compile time, at the exact line that needs a new case. That is the good outcome: the compiler has just handed over the complete list of places `Triangle` needs handling. The `switch`es with a `default` compile without complaint and route every `Triangle` into whatever the `default` branch does, which is silent and easy to miss, and is exactly the failure mode omitting `default` exists to prevent.

</details>

5. ▢ You are modelling the result of parsing a request line: either it succeeded and carries a `Request`, or it failed and carries a reason string. Would you reach for a sealed interface of two records, or an enum with two constants that each hold a field? Justify it, and say what would change your answer.

<details markdown="1"><summary>Check</summary>

A sealed interface of two records: `Success(Request request)` and `Failure(String reason)` carry different data by nature, one has a parsed request and the other has a reason string, and there is no shared field between the two cases for an enum constant to hold. An enum constant can hold a field, but every constant of a given enum shares the same field declarations, so `Success` and `Failure` would either both need to declare fields that do not apply to them or use `Object` and cast, which throws away exactly the type safety a sealed hierarchy provides here for free. If the two cases instead differed only by which value of one shared field they carried, for example a status that is always exactly one of three named codes with no data attached, that symmetry is what would tip the answer over to an enum instead.

</details>

## Real-world reps

- [ ] Write the sealed `Shape` hierarchy from this lesson, remove one `case` from a `switch` over it, and read the compiler's own exhaustiveness message before adding the case back.
- [ ] Write a pattern `switch` over a sealed type both with and without a `case null` label, call each with `null`, and compare the exception against the branch.
- [ ] Declare a permitted subtype with no `final`, `sealed` or `non-sealed` modifier and read what the compiler asks for, then fix it.
- [ ] Tomorrow: look at the composition-over-inheritance code from lesson 10 and ask whether any `instanceof` chain or type-tag `switch` in code you already have is secretly a closed set of alternatives; if it is, model it as a sealed interface of records and switch over it instead.

## Going further

- [JEP 409: Sealed Classes](https://openjdk.org/jeps/409): the `permits` rule, and why it is stricter than access control alone
- [JEP 440: Record Patterns](https://openjdk.org/jeps/440): nested deconstruction, and where a type pattern is allowed to fail to match
- [Modelling](../reference/modelling.md): the reference sheet for this stage
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
