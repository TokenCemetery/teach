---
title: 10. Inheritance and Composition
description: What extends actually gives you, and why the answer is usually a field instead of a superclass
type: lesson
---

# Lesson 10. Inheritance and Composition

**Mission link:** The mission promises a domain modelled without reaching for inheritance first, and this lesson is where `extends` gets priced honestly: what it actually buys, where the bill arrives later, and why a held field is usually the better trade.
**Primary source:** [JLS 8.4.8, Inheritance, Overriding, and Hiding](https://docs.oracle.com/javase/specs/jls/se25/html/jls-8.html#jls-8.4.8)
**Prerequisites:** [Lesson 7](0007-classes-and-objects.md), [Lesson 9](0009-interfaces.md)

## Warm-up

1. ▢ What value does an uninitialised `int` field have before its initialiser runs, and what happens if you try to read an uninitialised local variable of type `int` instead?

<details markdown="1"><summary>Check</summary>

The field gets the default, `0`. The local variable has no default, so the compiler rejects the read: `variable count might not have been initialized`.

</details>

2. ▢ Why is a constant declared in an interface usually a smell rather than a feature?

<details markdown="1"><summary>Check</summary>

An interface field is implicitly `public static final`, so it is not really "in" the interface at all: it is a permanent, unqualified public constant that every implementor exposes whether it wants to or not, and outside code ends up depending on a name that belongs to no particular type.

</details>

## Know this

`extends` gives a class exactly two things: it inherits the superclass's non-private members, and an object of the subclass can stand in anywhere the superclass type is expected. Both of those are useful, and both of those are also exactly what composition, a field plus delegation, gives you without the coupling that comes bundled with `extends`. The rest of this lesson is about where that coupling bites.

### `extends`, single inheritance, and construction order

A class extends at most one class, unlike the interfaces from lesson 9, of which it can implement several. If a constructor body contains no explicit call to `this(...)` or `super(...)` anywhere, the compiler inserts a call to the superclass's no-argument constructor. That only works if one exists:

```java
class Base {
    Base(int id) { System.out.println("Base id=" + id); }
}

class Sub extends Base {
    Sub() { }
}
```

```text
error: constructor Base in class Base cannot be applied to given types;
  required: int
  found:    no arguments
```

`Base` has no no-argument constructor, so the implicit call has nothing to call, and `Sub` must call `super(42)` or some other matching constructor explicitly. The call no longer has to be the first statement, as lesson 7 showed: statements that do not touch the instance may run before it, which is how an argument gets validated or computed before the superclass sees it.

Construction always runs superclass first: the superclass constructor completes, including every field initialiser and instance initialiser block it runs, before the subclass's own field initialisers execute. That ordering is invisible until a superclass constructor calls a method the subclass overrides:

```java
class Logger {
    Logger() {
        System.out.println("starting: " + status());
    }
    String status() { return "base"; }
}

class FileLogger extends Logger {
    private String prefix = "FILE";

    @Override
    String status() { return prefix; }
}

new FileLogger();
```

This prints `starting: null`. The call to `status()` dispatches to `FileLogger.status()`, because dispatch is on the runtime type regardless of which constructor is running, but `prefix`'s initialiser has not run yet: the `Logger` constructor is still executing, and subclass field initialisers only run afterwards. The fix is never to call an overridable method from a constructor, or to make the method `final` or `private` so there is nothing to override.

### Overriding, overloading, and what `@Override` catches

Overriding replaces the body of an inherited instance method for the identical signature, and the call resolves at runtime against the object's actual class. Overloading declares a different method that happens to share a name, and the call resolves at compile time against the static type of the reference and the argument types. The two look alike enough that a typo turns one into the other:

```java
class Repository {
    void save(Object record) { System.out.println("Repository.save(Object)"); }
}

class UserRepository extends Repository {
    void save(String record) { System.out.println("UserRepository.save(String)"); }
}

Repository r = new UserRepository();
r.save("alice");
```

This prints `Repository.save(Object)`. `UserRepository.save(String)` is a second, unrelated method, not an override, because the parameter type differs, and `r` is declared as `Repository`, so overload resolution never considers the `String` version at all. Marking the intended override `@Override` turns this class of mistake into a compile error instead of a silent wrong answer:

```text
error: method does not override or implement a method from a supertype
```

Write `@Override` on every intended override, with no exceptions, because the annotation costs nothing and the failure mode it catches produces no warning otherwise.

### The rules an override must obey

An override may widen the access of the method it overrides but never narrow it, may return a subtype of the original return type (covariant return types, final in Java 5) instead of the exact original type, and may declare fewer checked exceptions than the original, including none, but never a new one. Each rule failing is a compile error, not a runtime surprise:

```java
class Vehicle {
    public Vehicle service() throws IOException { return this; }
}
```

Narrowing access to package-private fails with `attempting to assign weaker access privileges; was public`. Adding a new checked exception fails with `overridden method does not throw SQLException`. Dropping the exception and covariantly returning `Car` instead of `Vehicle` both compile, because neither one breaks a caller that only knows about `Vehicle`: a caller catching `IOException` still catches everything the override can throw, and a caller expecting a `Vehicle` back is still holding one.

`final` closes off the two remaining ways in. A `final` method cannot be overridden (`overridden method is final`), and a `final` class cannot be extended at all (`cannot inherit from final Locked`). Reach for `final` on any method a subclass calling it from a constructor would otherwise be able to hijack, and on a class that has no business being a base class.

### Hiding: static methods and fields don't override

Instance methods dispatch on the runtime type. Static methods and fields do neither: a subclass can declare a static method or a field with the same name as the superclass's, but that only **hides** the superclass member, and which one a reference sees depends on the reference's declared type, not the object underneath it:

```java
class Animal {
    static String kind() { return "Animal.kind"; }
    String label = "Animal.label";
}

class Dog extends Animal {
    static String kind() { return "Dog.kind"; }
    String label = "Dog.label";
}

Animal a = new Dog();
a.kind();   // "Animal.kind"
a.label;    // "Animal.label"
```

Both resolve on the declared type `Animal`, even though the object is a `Dog`, which is the opposite of how `a.someInstanceMethod()` would behave. Calling a static method through an instance reference is legal, and just as misleading as it looks here, which is one more reason to always call a static method through its class name.

### `protected`, `abstract`, and the fragile base class

`protected` grants access to subclasses anywhere, not only subclasses in the same package, so a `protected` member is not an implementation detail: it is a contract with every subclass anyone ever writes, including ones the author never sees. Changing what a `protected` method does, or removing it, breaks those subclasses exactly as a public method change would. This is the fragile base class problem: a superclass author can break a subclass author's code by changing something that looked internal, and the subclass author can break by depending on more of the superclass's behaviour than its documentation actually promised.

`abstract` classes cannot be instantiated:

```text
error: Shape is abstract; cannot be instantiated
```

They exist for the case where several types genuinely are the same kind of thing, share state and some implementation, and differ only in a few operations, which an `abstract` method declares without a body and forces each subclass to supply. That is a narrower case than it looks: it requires the shared state to be worth sharing and the "is-a" relationship to be real, not just a resemblance in the method list. Closing off exactly which types are allowed to supply those bodies is a job for `sealed`, in the next lesson.

### Composition and delegation as the default

Subclassing a class you do not control couples you to its implementation, not just its documented contract. `HashSet` inherits `addAll` from `AbstractCollection`, which is implemented by calling `add` once per element, so a subclass that counts in both methods double-counts every bulk insert:

```java
class InstrumentedHashSet<E> extends HashSet<E> {
    private int addCount = 0;

    @Override
    public boolean add(E e) {
        addCount++;
        return super.add(e);
    }

    @Override
    public boolean addAll(Collection<? extends E> c) {
        addCount += c.size();
        return super.addAll(c);
    }

    public int getAddCount() { return addCount; }
}

InstrumentedHashSet<String> set = new InstrumentedHashSet<>();
set.addAll(List.of("a", "b", "c"));
set.getAddCount();  // 6
set.size();         // 3
```

`addAll` adds 3 up front, then calls `super.addAll`, which is the inherited `AbstractCollection` implementation, which calls `add` for each element in turn, and `add` is overridden too, so each of those calls adds another 1. Nothing here is documented behaviour being violated; it is `HashSet`'s undocumented implementation choice leaking through a supposedly safe override.

Composition sidesteps this by holding the collection instead of extending it, and forwarding every method explicitly:

```java
class ForwardingSet<E> implements Set<E> {
    private final Set<E> delegate;
    ForwardingSet(Set<E> delegate) { this.delegate = delegate; }
    public boolean add(E e) { return delegate.add(e); }
    public boolean addAll(Collection<? extends E> c) { return delegate.addAll(c); }
    // size, iterator, contains, remove and the rest, each forwarded the same way
}

class InstrumentedSet<E> extends ForwardingSet<E> {
    private int addCount = 0;
    InstrumentedSet(Set<E> delegate) { super(delegate); }

    @Override
    public boolean add(E e) {
        addCount++;
        return super.add(e);
    }

    @Override
    public boolean addAll(Collection<? extends E> c) {
        addCount += c.size();
        return super.addAll(c);
    }
}
```

Run the same `addAll(List.of("a", "b", "c"))` through this version and `getAddCount()` is `3`, matching `size()`. `addAll` here calls `delegate.addAll`, the real `HashSet` implementation, which never calls back into `InstrumentedSet.add`, because `delegate` is a plain `HashSet` with no idea `InstrumentedSet` exists. That is the actual win composition offers over inheritance for reuse: the wrapped object's internal calls stay internal, instead of dispatching back into your override.

### Why `equals` and inheritance fight

Lesson 3's `equals` contract requires symmetry: `x.equals(y)` and `y.equals(x)` must agree. A subclass that adds a field to its own `equals` puts that symmetry at risk, whichever direction the comparison delegates:

```java
class Point {
    final int x, y;
    public boolean equals(Object o) {
        if (!(o instanceof Point p)) return false;
        return p.x == x && p.y == y;
    }
}

class ColorPoint extends Point {
    final String color;
    public boolean equals(Object o) {
        if (!(o instanceof ColorPoint cp)) return false;
        return super.equals(cp) && color.equals(cp.color);
    }
}

Point p = new Point(1, 2);
ColorPoint cp = new ColorPoint(1, 2, "red");
p.equals(cp);   // true
cp.equals(p);   // false
```

`p.equals(cp)` is `true` because `cp` passes the `instanceof Point` check and the coordinates match. `cp.equals(p)` is `false` because `p` fails the `instanceof ColorPoint` check. No amount of cleverness in `ColorPoint.equals` fixes this while `Point.equals` also runs an `instanceof` check against a type `ColorPoint` extends, because one side of the comparison always knows about the extra field and the other never can. There are exactly two ways out: stop extending, giving `ColorPoint` a `Point` field instead of a `Point` superclass, which drops the "is-a" relationship but leaves `equals` sound, or keep extending and switch both classes to `getClass()` equality instead of `instanceof`, which keeps `equals` an equivalence relation but makes a `Point` and a `ColorPoint` with identical coordinates simply never equal, in either direction. Composition is the one that costs less in most domain models, which is exactly why it is the default this lesson is arguing for.

## Practice

1. ▢ Predict the output, and explain it.

   ```java
   class Logger {
       Logger() {
           System.out.println("starting: " + status());
       }
       String status() { return "base"; }
   }

   class FileLogger extends Logger {
       private String prefix = "FILE";

       @Override
       String status() { return prefix; }
   }

   new FileLogger();
   ```

<details markdown="1"><summary>Hint</summary>

By the time `Logger`'s constructor body runs, has `FileLogger`'s field initialiser run yet?

</details>

<details markdown="1"><summary>Check</summary>

`starting: null`. `status()` dispatches to `FileLogger.status()` because dispatch is always on the runtime type, but `prefix` is still at its default, `null`, because the `Logger` constructor runs to completion before any `FileLogger` field initialiser does.

</details>

2. ▢ This compiles cleanly and the author believes `save` is overridden. Find the bug.

   ```java
   class Repository {
       void save(Object record) { System.out.println("Repository.save(Object)"); }
   }

   class UserRepository extends Repository {
       void save(String record) { System.out.println("UserRepository.save(String)"); }
   }

   Repository r = new UserRepository();
   r.save("alice");
   ```

<details markdown="1"><summary>Hint</summary>

Compare the parameter types against the superclass method, not just the method name.

</details>

<details markdown="1"><summary>Check</summary>

It prints `Repository.save(Object)`. `UserRepository.save(String)` has a different parameter type, so it is a second, unrelated overload rather than an override, and `r`'s declared type, `Repository`, is all overload resolution looks at, so the `String` version is never even a candidate. Marking the intended override `@Override` turns this into a compile error instead of a silent wrong answer.

</details>

3. ▢ Given `Vehicle.service()` below, which of these overrides in `Car` compile?

   ```java
   class Vehicle {
       public Vehicle service() throws IOException { return this; }
   }
   ```

   - a) `Vehicle service() throws IOException { return this; }`
   - b) `public Car service() { return this; }`
   - c) `public Vehicle service() throws IOException, SQLException { return this; }`
   - d) `public Vehicle service() throws IOException { return this; }`

<details markdown="1"><summary>Check</summary>

**b) and d).**

a) narrows access from `public` to package-private, which an override may never do. c) adds `SQLException`, a checked exception the original method never declared, which an override may never do. b) compiles: it widens nothing, drops the checked exception entirely, which is allowed, and returns the covariant `Car` instead of `Vehicle`. d) compiles as a plain, unchanged override.

</details>

4. ▢ The `InstrumentedHashSet` from this lesson double-counts through `addAll`. Rewrite it as a composed wrapper instead of a subclass, so the count stays right no matter which bulk method a caller reaches for.

<details markdown="1"><summary>Check</summary>

Hold a `Set<E>` field and forward every `Set` method to it, then override only `add` and `addAll` on the wrapper to add the counting, the way `ForwardingSet` and `InstrumentedSet` do earlier in this lesson. Running the same `addAll(List.of("a", "b", "c"))` gives `getAddCount() == 3 == size()`, because `addAll` now calls the delegate's real `addAll`, which has no idea the wrapper's `add` exists and never calls back into it.

</details>

5. ▢ A reviewer flags that `ColorPoint extends Point` breaks the symmetry rule from lesson 3's `equals` contract. Name the two fixes, and what each one gives up.

<details markdown="1"><summary>Check</summary>

Stop extending: give `ColorPoint` a `Point` field instead of a `Point` superclass. `equals` becomes sound because there is no shared supertype for one side to pass an `instanceof` check the other side cannot pass back, but a `ColorPoint` is no longer usable anywhere a `Point` is expected. Or keep extending, but write both `equals` methods with `getClass()` instead of `instanceof`, so a `Point` and a `ColorPoint` are simply never equal to each other in either direction, which keeps `equals` an equivalence relation at the cost of a stricter comparison than the coordinates alone would justify.

</details>

## Real-world reps

- [ ] Grep a codebase you know for `extends`, and for each hit decide whether the subclass genuinely is a superclass, in the domain's own terms, or is only reusing its code. Flag the second kind as a composition candidate.
- [ ] Take a class that extends a JDK collection or utility class, and check whether it overrides one method of a pair, such as `add` without `addAll`, where the other calls back into it. That pairing is the counting-set bug waiting to happen.
- [ ] Find a class that overrides `equals` and check every one of its subclasses for an added field. If one exists, decide whether it uses composition or is quietly living with the symmetry problem.
- [ ] Tomorrow: pick one class from your own code that extends another purely for code reuse, with no real "is-a" relationship, and rewrite it to hold a field and delegate instead.

## Going further

- [JLS 8.4.8, Inheritance, Overriding, and Hiding](https://docs.oracle.com/javase/specs/jls/se25/html/jls-8.html#jls-8.4.8): the rules an override and a hiding declaration must satisfy, stated precisely
- [`Object.equals`](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/Object.html): the contract this lesson's last section leans on
- [Book: "Effective Java", Joshua Bloch](https://openlibrary.org/isbn/9780134685991): Item 18 on preferring composition to inheritance, and Item 10 on the `equals` contract, both argued in far more depth than one lesson can give
- [Modelling](../reference/modelling.md): the reference sheet for this stage
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
