---
title: 7. Classes and Objects
description: A class is a template for state and behaviour, and every field starts at a default you did not write
type: lesson
---

# Lesson 7. Classes and Objects

**Mission link:** Every other way of modelling a domain in this stage, records, interfaces, enums and sealed types, is a class underneath, so knowing exactly what a class hands you for free, and knowing that a getter and setter for every field is not the same thing as a well-designed type, is the baseline the rest of stage 2 assumes.
**Primary source:** [The Java Language Specification, Chapter 8, Classes](https://docs.oracle.com/javase/specs/jls/se25/html/jls-8.html)
**Prerequisites:** [Lesson 1](0001-references-are-values.md), [Lesson 3](0003-equals-and-hashcode.md)

## Warm-up

1. ▢ A `TreeSet<Task>` orders its elements with a comparator that compares only by priority. Two tasks with the same priority but different names are both added. What is the set's size afterwards, and why?

<details markdown="1"><summary>Check</summary>

`1`. A `TreeSet` decides membership with the comparator, not with `equals`, so the second task compared as zero against the first and was rejected as a duplicate. The two tasks are not `equals`, but nothing ever asked.

</details>

2. ▢ A method with the signature `void refill(List<Item> items)` runs `items = new ArrayList<>();` as its first line, then adds to that new list. What does the caller's list look like afterwards?

<details markdown="1"><summary>Check</summary>

Exactly as it was before the call. `items` inside the method holds a copy of the caller's reference, and reassigning that copy only rebinds the local parameter. The caller's variable still refers to the original list, which nothing touched.

</details>

## Know this

### Running these examples

Every example on this page is small enough to run with the single-file source launcher: `java Scratch.java` compiles the file in memory and runs it in one step, no separate `.class` file left behind, as long as the file holds every class the example needs. Once a program spans more than one file, compile them together with `javac` and run the named class with `java`, against the same classpath. For a single expression, `jshell` starts an interactive shell that evaluates one line at a time, useful for checking something small without a file at all.

### Fields, methods, and instance versus static

```java
class Robot {
    static int unitsBuilt = 0;
    String name;

    Robot(String name) {
        this.name = name;
        unitsBuilt++;
    }
}

Robot r1 = new Robot("R1");
Robot r2 = new Robot("R2");
System.out.println(Robot.unitsBuilt);   // 2
```

A class declares two kinds of member. An **instance field** such as `name` exists once per object, so `r1.name` and `r2.name` are two separate strings. A **static field** such as `unitsBuilt` exists once per class, shared by every instance and reachable without one, which is why `Robot.unitsBuilt` reads `2` after two constructions rather than `1` for each. Methods split the same way: a static method has no receiving object and cannot use `this`; an instance method always runs against one particular object. A static member is reachable through an instance variable too, so `r1.unitsBuilt` compiles and also reads `2`, but it reads the one field the class owns, not something belonging to `r1`, which is why most tooling flags the style and the fix is to write `Robot.unitsBuilt`.

### The constructor you get for free, and losing it

A class with no constructor at all gets an implicit public no-argument one, which is why `new Robot()` would compile if `Robot` declared nothing. Declaring any constructor removes it:

```java
class Widget {
    Widget(String name) {
    }
}

new Widget();   // error
```

```text
error: constructor Widget in class Widget cannot be applied to given types;
  required: String
  found:    no arguments
  reason: actual and formal argument lists differ in length
```

There is no partial version of this rule: one declared constructor, of any arity, and the no-argument one is gone unless you write it yourself.

### this, and chaining constructors with this(...)

`this` refers to the object the current constructor or instance method is running against. Its most common job is disambiguating a field from a same-named parameter, as `this.name = name` did above: without the prefix, `name = name` would assign the parameter to itself and the field would keep its default forever. A constructor can also delegate to another constructor of the same class with `this(...)`:

```java
class Point {
    final int x;
    final int y;

    Point(int x, int y) {
        this.x = x;
        this.y = y;
        System.out.println("two-arg constructor, x=" + x + " y=" + y);
    }

    Point() {
        this(0, 0);
        System.out.println("no-arg constructor finished delegating");
    }
}

new Point();
```

```text
two-arg constructor, x=0 y=0
no-arg constructor finished delegating
```

The delegated-to constructor runs to completion, in full, before the statement after `this(...)` executes. For a long time the `this(...)` call also had to be the very first statement, full stop. Java 25 relaxed that (JEP 513, Flexible Constructor Bodies): a constructor may now run statements ahead of the call, but only if none of them touch the instance under construction. Reading a field through `this` still fails, even one statement earlier:

```text
error: cannot reference this before supertype constructor has been called
```

In practice the delegating call is still usually written first; the relaxation exists mainly to let a constructor validate its arguments, and fail fast, before handing them to another constructor. `super(...)`, the equivalent call to a superclass constructor, follows the same rule and belongs properly to lesson 10.

### Fields get a default; locals do not

```java
class Robot {
    String name;
    int battery;
    boolean active;
}

Robot r = new Robot();
System.out.println(r.name + " " + r.battery + " " + r.active);
```

```text
null 0 false
```

Every field is initialised before anything can read it: `null` for a reference, `0` or `0.0` for a numeric primitive, `false` for `boolean`. A local variable gets none of that, and the compiler enforces the difference:

```java
int total;
System.out.println(total);
```

```text
error: variable total might not have been initialized
```

That asymmetry is deliberate: the compiler can prove a local is read before assignment by tracing the one method it lives in, and does; it cannot prove the same for a field, which any constructor or method might set in any order, so it defaults it instead.

### Initialisation order

```java
class Gadget {
    int a = printAndReturn("field a", 1);

    {
        System.out.println("instance initialiser block");
    }

    int b = printAndReturn("field b", 2);

    static int s = printAndReturn("static field s", 10);

    static {
        System.out.println("static initialiser block");
    }

    Gadget() {
        System.out.println("constructor body");
    }
}

System.out.println("before first new");
new Gadget();
System.out.println("before second new");
new Gadget();
```

```text
before first new
static field s
static initialiser block
field a
instance initialiser block
field b
constructor body
before second new
field a
instance initialiser block
field b
constructor body
```

Two rules fall out of that run. Field initialisers and instance initialiser blocks (a bare `{ }` block with no name) execute in the order they appear in the source, interleaved exactly as written, and always before the constructor body runs, every time an instance is created. Static field initialisers and static blocks run once, the first time the class is used, here immediately before the first instance is built, and never again for the second. A field initialiser can only read a field declared earlier in the same class; reading one declared later is an *illegal forward reference* and the compiler rejects it at that line, which is the same source-order rule catching a mistake before it becomes a bug.

### Four access levels, one with no keyword

Java has four access levels, and only three have a keyword: `private`, `protected` and `public`. The fourth, no modifier at all, is called **package-private**, and it means visible to any class in the same package, whatever the file:

```java
package a;
public class Box {
    int quantity;
}
```

```java
package b;
import a.Box;
public class UseBox {
    public static void main(String[] args) {
        Box box = new Box();
        System.out.println(box.quantity);   // error
    }
}
```

```text
error: quantity is not public in Box; cannot be accessed from outside package
```

`private` narrows that further, to the declaring class itself:

```text
error: code has private access in Secret
```

`public` widens it to everyone, and `protected` widens package-private to include subclasses outside the package too, which lesson 10 covers once subclasses exist to talk about. Choosing the narrowest level that works is the whole game: a member wider than it needs to be is a promise you did not mean to make.

### final fields

`final` on a field means it can be assigned once, during construction, and never reassigned:

```java
class Account {
    final String owner;

    Account(String owner) {
        this.owner = owner;
    }

    void rename(String newOwner) {
        this.owner = newOwner;   // error
    }
}
```

```text
error: cannot assign a value to final variable owner
```

As the [glossary](../GLOSSARY.md) already pins: `final` is a promise about the reference, not the object on the other end, so a `final List` still permits `add` and `remove` on the list it refers to.

### The default toString

```java
Robot r = new Robot();
System.out.println(r);
```

```text
Robot@2a40cd94
```

Every class inherits `toString` from `Object`, and the inherited version prints the fully qualified class name, an `@`, and the object's hash code in hexadecimal, which is why the digits differ on every run. It identifies which object printed, and nothing about what it holds. Overriding `toString` is the fix, and lesson 8 gives you a type that writes a useful one for free.

### var for locals

```java
var scores = new HashMap<String, Integer>();
scores.put("alice", 9);
var fee = 12;
```

`var` (Java 10) tells the compiler to infer a local's type from its initialiser rather than writing the type twice. It earns its place when the type is already visible on the right, as with `scores`, where the declared type would only repeat `HashMap<String, Integer>`. It hurts readability exactly where that visibility disappears: `var fee = 12` hides that `fee` is an `int` behind a number that could as easily have been a `long` or a `double`, and `var result = process(order)` hides whatever `process` returns behind a method name that gives no hint. `var` never changes what the variable can hold; it only changes whether the type appears in the source.

### A getter and setter for every field is not encapsulation

A class that exposes `getBalance()`, `setBalance(int)`, `getOwner()` and `setOwner(String)` for a `BankAccount` has hidden nothing. Any code that could reach in and set the balance directly can still set it to anything, just through a method instead of a field, and the class has gained boilerplate without gaining a rule. Encapsulation is not about wrapping access; it is about deciding which operations the type offers at all. A `BankAccount` that offers `deposit(int amount)` and `withdraw(int amount)` instead can reject a negative amount or an overdraft inside those methods, in one place, which a setter can never do because a setter's whole job is accepting whatever it is given. The question worth asking about a new type is never "does every field have a getter and setter", it is "what can a caller legitimately do to this object, and does the API say exactly that and nothing more".

## Practice

1. ▢ Predict the output, and explain it.

   ```java
   class Counter {
       static int created = 0;
       int id = ++created;

       Counter() {
           System.out.println("created #" + id);
       }
   }

   new Counter();
   new Counter();
   System.out.println(Counter.created);
   ```

<details markdown="1"><summary>Check</summary>

```text
created #1
created #2
2
```

`created` is static, so both objects increment the one shared field. Each object's `id` initialiser runs before that object's constructor body, and captures the value `created` holds at that moment, which is why the first object gets `1` and the second gets `2` rather than both racing to the same number.

</details>

2. ▢ Find the bug. `p.x` and `p.y` both print `0` no matter what is passed in.

   ```java
   class Point {
       int x;
       int y;

       Point(int x, int y) {
           x = x;
           y = y;
       }
   }
   ```

<details markdown="1"><summary>Hint</summary>

The parameters are named identically to the fields. Ask what `x = x` actually assigns, and to what.

</details>

<details markdown="1"><summary>Check</summary>

The parameters shadow the fields inside the constructor body, so `x = x` assigns the parameter to itself and never touches the field. The fields keep their default of `0` forever. The fix is `this.x = x; this.y = y;`, which is exactly why lesson 8's records generate that assignment for you instead of leaving it to be typed correctly by hand.

</details>

3. ▢ Why does this fail to compile, and what does it have to do with initialisation order?

   ```java
   class Session {
       String log = "created " + id;
       String id = "abc123";
   }
   ```

<details markdown="1"><summary>Check</summary>

```text
error: illegal forward reference
```

Field initialisers run top to bottom in source order, so at the point `log` is initialised, `id` has not been assigned yet, only defaulted. The compiler does not wait to find that out at run time; a simple forward reference like this one is caught at compile time. Swapping the two declarations fixes it.

</details>

4. ▢ A field has no access modifier at all. Which of these callers can read it directly: a class in the same file and package, an unrelated class in a different package, a subclass declared in a different package?

<details markdown="1"><summary>Check</summary>

Only the first. No modifier means package-private, visible to any class sharing the package regardless of file. An unrelated class in a different package cannot reach it, and neither can a subclass in a different package, since package-private carries no allowance for inheritance; that is what the separate `protected` level exists for.

</details>

5. ▢ A reviewer says a new `Inventory` class "isn't properly encapsulated" because its fields are `private` but it has no setters. The author adds a getter and setter for every field to satisfy the comment. Was the original review comment right, and did the fix address it?

<details markdown="1"><summary>Check</summary>

The review comment, taken at face value, was wrong: `private` fields with no way to reach them from outside are already about as encapsulated as a field can be. The fix made things worse, not better, since a setter for every field reopens exactly the access `private` had closed, just via a method. What the reviewer probably meant, and should have said, is that `Inventory` has no operations yet, no `reserve`, `restock` or `reorderPoint` check, only raw access to its state. That is a real gap, and it is not fixed by a getter and setter for anything.

</details>

## Real-world reps

- [ ] Write the `Gadget` class from this lesson, or your own version with different field and block names, and watch the initialisation order print before you predicted every line of it.
- [ ] Find a class in code you know with a getter and setter for every field. Pick one field and name the operation the type should offer instead of raw access to it.
- [ ] Take a class from another language you have written and rewrite its fields with a deliberate Java access level each, rather than defaulting everything to public.
- [ ] Tomorrow: open a class you already have, and for every field ask whether it needs a setter at all, or whether the class should offer an operation that changes it under a rule instead.

## Going further

- [JLS Chapter 8, Classes](https://docs.oracle.com/javase/specs/jls/se25/html/jls-8.html): the full declaration syntax, initialisation order, and every access rule, stated formally
- [`Object`](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/Object.html): where the default `toString` and every method every class inherits comes from
- [JEP 513, Flexible Constructor Bodies](https://openjdk.org/jeps/513): what may run before `this(...)` or `super(...)`, finalised in Java 25
- [Modelling](../reference/modelling.md): the reference sheet for this stage
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
