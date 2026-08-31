---
title: 8. Records
description: A transparent carrier for immutable data, with the constructor, accessors, equals, hashCode and toString derived from the header
type: lesson
---

# Lesson 8. Records

**Mission link:** Modelling a domain in modern Java starts with reaching for a record before a class, since most immutable data is exactly a header plus a rule, and a record states that once instead of writing equals, hashCode and toString by hand.
**Primary source:** [JEP 395: Records](https://openjdk.org/jeps/395)
**Prerequisites:** [Lesson 3](0003-equals-and-hashcode.md), [Lesson 7](0007-classes-and-objects.md)

## Warm-up

1. ▢ What does the default `toString` a plain class inherits from `Object` print, and why doesn't it tell you anything about the object's state?

<details markdown="1"><summary>Check</summary>

The class name followed by `@` and the hash code in hexadecimal, for example `Plain@2bea5ab4`. It never mentions a field, because `Object` has no idea which fields exist or what they mean.

</details>

2. ▢ In the `equals`/`hashCode` contract, what must be true of `hashCode()` whenever two objects are `equals()`? Is the reverse also required?

<details markdown="1"><summary>Check</summary>

If `x.equals(y)` is true, `x.hashCode() == y.hashCode()` must also be true. The reverse is not required: two unequal objects may share a hash code. A record's generated `hashCode` satisfies this automatically, because it and `equals` are both derived from the same components.

</details>

## Know this

### The header generates a type

```java
record Point(double x, double y) {}
```

That one line is the whole declaration, and the compiler expands it into a full type. Reflecting on the class shows exactly what appears:

```text
field: private final double x
field: private final double y
ctor:  Point(double,double)
method: public final boolean Point.equals(java.lang.Object)
method: public final java.lang.String Point.toString()
method: public final int Point.hashCode()
method: public double Point.x()
method: public double Point.y()
```

A private final field per component, an accessor named for the component, never `getX()`, a **canonical constructor** taking every component in header order, and `equals`, `hashCode` and `toString`, all three declared `final` so nothing downstream can override just one of them. `toString` prints every component in header order, `Point[x=1.0, y=2.0]`. `equals` requires the same runtime type and every component equal; `hashCode` combines the components' hash codes, so equal records always hash the same. For a `double` component specifically, "equal" follows `Double`'s boxed semantics rather than the `==` operator: two `NaN` values compare equal, and `-0.0` does not equal `0.0`, the opposite of what `-0.0 == 0.0` gives as primitives. Every record also implicitly extends `java.lang.Record`, which is verifiable directly: `Point.class.getSuperclass()` reports `class java.lang.Record`. That is not a technicality, it is the reason a record cannot extend anything else, covered below.

### The compact constructor: validate, then normalise

A **compact constructor** names no parameter list, because it reuses the header's, and it runs before the field assignments the compiler appends automatically:

```java
record Range(int lo, int hi) {
    Range {
        if (lo > hi) throw new IllegalArgumentException(lo + " > " + hi);
        if (lo < 0) lo = 0;
    }
}
```

`new Range(10, 1)` throws, with the message `10 > 1` produced exactly as written. `new Range(-5, 10)` does not throw; it normalises, and `lo()` on the result reports `0`. The line `lo = 0` is doing the entire job: **assigning to the parameter is what reaches the field**, because the compiler's implicit `this.lo = lo;` runs after your code, using whatever the parameter holds by then. Writing `this.lo = 0;` instead does not work the way it looks like it should:

```java
record Team(String name, List<String> members) {
    Team {
        this.members = List.copyOf(members);
    }
}
```

```text
error: cannot assign a value to final variable members
        this.members = List.copyOf(members);
            ^
```

Inside a compact constructor the field is not yet assigned and is treated as a blank final you may not touch directly; only the implicit tail assignment may set it. The fix is to drop `this.`: `members = List.copyOf(members);`.

### Static factories

A record's body can hold static methods exactly like a class's can, so a named construction path costs nothing extra:

```java
static Range of(int lo, int hi) {
    return new Range(lo, hi);
}
```

There is nothing record-specific here beyond convenience: a factory can pick a more descriptive name than a bare constructor call, or centralise which overload gets used, without the caller ever seeing the canonical constructor directly.

### What a record cannot do

A record is implicitly `final`: it cannot be subclassed, and nothing declares that explicitly. The grammar goes further and refuses an `extends` clause outright, a parse-level restriction rather than a later semantic check, `record Bad(int x) extends Base {}` fails with `error: '{' expected` at the point `extends` appears. That restriction exists because the single superclass slot is already spent on `java.lang.Record`. A record **can** implement interfaces, in the ordinary way:

```java
interface Shape { double area(); }
record Circle(double r) implements Shape {
    public double area() { return Math.PI * r * r; }
}
```

A record also has no instance fields beyond its components. Declaring one is rejected, not silently ignored:

```java
record BadRecord(int x) {
    private int y;
}
```

```text
error: field declaration must be static
    private int y;
                ^
  (consider replacing field with record component)
```

A `static` field is fine; only per-instance state beyond the header is closed off.

### The mutable-component trap

A record's generated `equals` compares components with their own `equals`, and for a reference component that is whatever that type defines, which is where an array component goes wrong: array `equals` is identity, not content.

```java
record Holder(int[] data) {}

Holder h1 = new Holder(new int[]{1, 2, 3});
Holder h2 = new Holder(new int[]{1, 2, 3});
h1.equals(h2);              // false: different array objects
h1.toString();               // Holder[data=[I@7f010382]
```

Two holders built from separately allocated, identical-content arrays are not equal, and printing one shows the array's identity-based `toString`, not its contents. A record does not special-case arrays to fix either problem.

A `List` component fares better on comparison, since `List.equals` is structural, but it introduces a different failure: mutability that outlives construction. A defensive copy in the compact constructor closes the door the caller came in through, but not necessarily the one the accessor opens on the way out.

```java
record Team(String name, List<String> members) {
    Team { members = List.copyOf(members); }   // unmodifiable snapshot
}

List<String> src = new ArrayList<>(List.of("Ann", "Bo"));
Team team = new Team("Core", src);
src.add("Cy");                        // mutate the source after construction
team.members();                       // [Ann, Bo], unaffected
team.members().add("Dee");            // throws UnsupportedOperationException
```

`List.copyOf` happens to close both leaks at once, because its result is both a snapshot and unmodifiable. Swap it for a plain defensive copy and the second leak reopens:

```java
record LeakyTeam(String name, List<String> members) {
    LeakyTeam { members = new ArrayList<>(members); }   // copy, but still mutable
}

List<String> src2 = new ArrayList<>(List.of("Ann", "Bo"));
LeakyTeam leaky = new LeakyTeam("Core2", src2);
src2.add("Cy");                       // still doesn't show: [Ann, Bo]
leaky.members().add("Dee");           // succeeds: [Ann, Bo, Dee]
```

The constructor's copy stopped the caller's own list from reaching in. It did nothing to stop the generated accessor from handing back that same mutable list by reference, which is the remaining leak: whatever holds the reference `members()` returns can mutate the record after the fact. Closing it means the accessor has to change too, not just the constructor:

```java
record SafeTeam(String name, List<String> members) {
    SafeTeam { members = new ArrayList<>(members); }
    public List<String> members() { return List.copyOf(members); }   // override
}
```

`safeTeam.members().add(...)` now throws, because every call hands out a fresh unmodifiable snapshot rather than the field itself. The same shape applies to an array component: a compact constructor that does `data = data.clone();` still leaves the accessor returning the live internal array unless the accessor is overridden to clone on the way out too. This is a partial pattern for one trap, not the general immutability recipe, which is its own lesson.

### Local records

A method body can declare a record scoped to that block, finalised alongside pattern matching for `instanceof` in the same release:

```java
void main() {
    record Pair(int a, int b) {}
    Pair p = new Pair(1, 2);
    System.out.println(p);   // Pair[a=1, b=2]
}
```

Every generated member still applies; a **local record** is only a local record in the sense that its declaration is scoped, useful for a throwaway multi-value result or a grouping key that has no business existing outside one method.

### When a record is the wrong choice

Three shapes push back on a record. **Mutable state**: a record has no setters and cannot grow them, every field is final, so a concept that genuinely changes in place after construction is fighting the type rather than being modelled by it. **Identity that outlives the values**: a database row or a long-lived entity where two objects sharing today's field values are not necessarily the same thing (its identity is a key, not its current state) wants the identity-flavoured `equals` a class gives you, not the structural one a record forces. **Types that need subclasses**: a record is implicitly final, so if the model genuinely needs to grow variants later, that door is already shut; a sealed interface of records is usually the shape that direction wants instead, and lesson 11 covers it.

## Practice

1. ▢ Predict the three outputs, and explain the last line against the first two.

   ```java
   record Point(double x, double y) {}
   Point a = new Point(Double.NaN, 1.0);
   Point b = new Point(Double.NaN, 1.0);
   Point c = new Point(-0.0, 1.0);
   Point d = new Point(0.0, 1.0);
   System.out.println(a.equals(b));
   System.out.println(c.equals(d));
   System.out.println(-0.0 == 0.0);
   ```

<details markdown="1"><summary>Check</summary>

`true`, `false`, `true`.

Generated `equals` on a `double` component follows `Double`'s boxed semantics, not the primitive `==` operator: `NaN` compares equal to `NaN`, and `-0.0` does not compare equal to `0.0`. The primitive `==` used directly on line three gives the opposite answer for the zeros, which is exactly why the two lines disagree.

</details>

2. ▢ Find the bug, quote the message it produces, and give the one-line fix.

   ```java
   record Team(String name, List<String> members) {
       Team {
           this.members = List.copyOf(members);
       }
   }
   ```

<details markdown="1"><summary>Hint</summary>

Inside a compact constructor, what is `members` before the compiler's own implicit assignment runs, and is `this.members` the same thing?

</details>

<details markdown="1"><summary>Check</summary>

`error: cannot assign a value to final variable members`. Inside a compact constructor the field behind `this.members` has not been assigned yet and cannot be assigned directly; only the compiler's implicit tail assignment may set it. The fix drops `this.`: `members = List.copyOf(members);`, assigning to the parameter, which the tail assignment then copies into the field.

</details>

3. ▢ Predict what these two lines print.

   ```java
   record Holder(int[] data) {}
   Holder h1 = new Holder(new int[]{1, 2, 3});
   Holder h2 = new Holder(new int[]{1, 2, 3});
   System.out.println(h1.equals(h2));
   System.out.println(h1);
   ```

<details markdown="1"><summary>Hint</summary>

Compare what a record's generated `equals` does with two boxed `Double` components against what it does with two array components: both delegate to the component's own `equals`.

</details>

<details markdown="1"><summary>Check</summary>

`false`, then `Holder[data=[I@...]` with some hash suffix.

Array `equals` is identity, so two separately allocated arrays with the same content are never equal, and array `toString` never shows the contents either. A record does not special-case arrays to give either one deep behaviour.

</details>

4. ▢ `LeakyTeam` below copies its `members` list in the compact constructor, yet a caller can still mutate the stored list after construction. Name the one-line fix, and say why it has to touch the accessor rather than the constructor.

   ```java
   record LeakyTeam(String name, List<String> members) {
       LeakyTeam { members = new ArrayList<>(members); }
   }
   ```

<details markdown="1"><summary>Check</summary>

Override the accessor to hand back a copy instead of the field itself: `public List<String> members() { return List.copyOf(members); }`. The constructor's copy only stops the *caller's original list* from reaching in; the generated accessor still returns the internal list by reference, so `leakyTeam.members().add(...)` mutates the record's own state. The constructor guards the door on the way in, the accessor is a separate door on the way out, and only overriding the accessor closes that one.

</details>

5. ▢ A `Customer` type carries a database-assigned `id` that never changes and a `name` that sometimes does. Two `Customer` values with the same `id` but different `name` (one stale, one freshly renamed) should be treated as the same customer. Is a record the right tool here? Justify the answer.

<details markdown="1"><summary>Check</summary>

No. A record's `equals` is structural, comparing every component, so a stale copy and a renamed copy of the same customer would compare unequal even though they represent one customer. What this type needs is identity keyed on `id` alone, which means writing `equals` and `hashCode` by hand around the key, the thing a record exists specifically to avoid writing. A record still works well for genuinely value-shaped pieces of the domain, such as an `Address`, just not for the entity whose identity outlives its current field values.

</details>

## Real-world reps

- [ ] Find a class in code you own that is only a bag of fields with a hand-written `equals`, `hashCode` and `toString`, and check whether every field could be a record component.
- [ ] Write a record with a `List` component, add a compact constructor that defensively copies it, then call the accessor directly and check whether the copy actually closed the leak.
- [ ] Declare an instance field inside a record and read the compiler's rejection for yourself.
- [ ] Tomorrow: rewrite one real data-carrying class from your own code as a record, and note exactly which methods you got to delete.

## Going further

- [JEP 395: Records](https://openjdk.org/jeps/395): the proposal that finalised records in Java 16
- [`Record`, Java SE 25 API](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/Record.html): the implicit superclass every record extends
- [JLS §8.10, Record Classes](https://docs.oracle.com/javase/specs/jls/se25/html/jls-8.html#jls-8.10): the exact rules the compiler enforces on a record header
- [Modelling](../reference/modelling.md): the reference sheet for this stage
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
