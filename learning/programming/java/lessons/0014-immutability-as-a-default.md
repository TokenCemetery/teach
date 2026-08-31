---
title: 14. Immutability as a Default
description: Make the object impossible to change and most of the hard questions stop being asked
type: lesson
---

# Lesson 14. Immutability as a Default

**Mission link:** A shared mutable field is the bug the mission names before stage 4 even starts, and building the default model as immutable is how you close off that failure before a lock ever enters the picture.
**Primary source:** [`List`, Java SE 25 API](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/List.html)
**Prerequisites:** [Lesson 2](0002-identity-and-equality.md), [Lesson 8](0008-records.md)

## Warm-up

1. ▢ A record's canonical constructor copies a `List` parameter into a fresh `ArrayList` before storing it in the field. Does that alone stop a caller from mutating the object after construction?

<details markdown="1"><summary>Check</summary>

No. The copy on the way in stops the caller's *original* list from reaching the field, but the accessor still hands back that same internal list by reference. Whoever calls the accessor gets a live handle on the field and can mutate it directly. The copy closed one door and left the other open.

</details>

2. ▢ Two variables hold a reference to the same mutable list. You call `add` through one of them. Does the other variable see the new element, and what is this situation called?

<details markdown="1"><summary>Check</summary>

Yes, because both variables refer to the one object rather than to separate copies of it. This is aliasing, and it is what makes the accessor leak in the question above observable at all: the caller's variable and the field are aliases of the same list.

</details>

## Know this

### What immutability buys

An object that cannot change after construction can be handed to another thread, stored in a cache, or used as a hash key, without asking who else is holding a reference to it or when they last touched it. Three concrete payoffs follow from that one fact:

- **Safe to share with no coordination.** There is nothing to protect, because there is nothing that changes. No lock, no copy defensively taken before a read.
- **Safe as a hash key.** `hashCode` is computed once and stays valid for as long as the object exists, so it can sit in a `HashMap` or a `HashSet` without the silent corruption that follows from mutating a key after insertion.
- **Invariants hold once and for all.** A constructor that validates its arguments only has to be right once. A setter that can be called at any later time has to keep being right forever, against every caller that might reach it.

### The recipe

Making a type actually immutable takes more than sprinkling `final` on things:

- No setters, and no other method that mutates state after construction.
- Every field `final`.
- The class itself `final`, or `sealed` with permitted subtypes that keep the same discipline. An extensible non-final class lets a subclass add a mutable field or override a method to break an invariant the base class thought it had sealed shut.
- A defensive copy of any mutable argument on the way in, and a defensive copy or an unmodifiable view of any mutable field on the way out.
- No reference to the object escaping before its constructor finishes, since a partially constructed object handed to another thread or stored somewhere can be observed before its invariants are established.

### What a record gives you, and what it does not

A record already supplies most of the recipe: `final` fields, no generated setters, a canonical constructor in one place to validate. What it does not supply is the copying, and that gap is where the leak lives:

```java
record Portfolio(String owner, List<String> holdings) {}

List<String> mutable = new ArrayList<>(List.of("AAPL", "MSFT"));
Portfolio p = new Portfolio("Ada", mutable);
System.out.println(p.holdings());              // [AAPL, MSFT]
mutable.add("GOOG");
System.out.println(p.holdings());               // [AAPL, MSFT, GOOG]
p.holdings().add("EVIL");
System.out.println(p.holdings());               // [AAPL, MSFT, GOOG, EVIL]
```

Two different leaks in that output. The caller's own list reaches the field, because nothing copied it, so a mutation made after construction still shows up. And the accessor hands back the live field, so a caller who never kept the original list can still reach in and mutate it. A compact constructor that copies on the way in closes the first leak but not the second:

```java
record PartiallyDefended(String owner, List<String> holdings) {
    PartiallyDefended(String owner, List<String> holdings) {
        this.owner = owner;
        this.holdings = new ArrayList<>(holdings);   // copy in
    }
}
```

Running the same sequence against `PartiallyDefended`, mutating the original source list after construction no longer changes the object, but `partiallyDefended.holdings().add("EVIL")` still does, because the accessor still returns the internal `ArrayList` itself. Closing that second leak means overriding the accessor too, to return a copy or an unmodifiable view:

```java
@Override
public List<String> holdings() {
    return List.copyOf(holdings);
}
```

With that override in place, mutating the returned list throws `UnsupportedOperationException` rather than silently changing state that the object thought was settled.

### Snapshot against view, and what neither one fixes

`List.copyOf` and `Collections.unmodifiableList` both refuse writes through the reference they return, but they disagree on what happens to the source afterwards:

```java
List<String> backing = new ArrayList<>(List.of("one", "two"));
List<String> view = Collections.unmodifiableList(backing);
List<String> snapshot = List.copyOf(backing);
backing.add("three");
System.out.println(view);       // [one, two, three]
System.out.println(snapshot);   // [one, two]
```

`Collections.unmodifiableList` returns a **view**: it wraps the backing list and reads through to it, so a later change to the backing list shows up. `List.copyOf` takes a **snapshot**: the elements are copied out once, and the backing list can do whatever it likes afterwards without the copy noticing.

One detail worth checking rather than assuming: does `List.copyOf` allocate a fresh list every time, even when it is handed a list that is already one of its own immutable results? Comparing identity across calls answers it. `List.copyOf(List.copyOf(List.of("a", "b", "c")))` returns the exact same instance as the inner call, since `List.copyOf` recognises its own immutable implementation and hands it straight back rather than copying it again. Give it a `Collections.unmodifiableList` view instead, which is a different implementation entirely, and `List.copyOf` cannot tell that the view's backing list will never change, so it copies: the result is a new instance. The rule is narrower than "already immutable is free": it is fast for a list `List.copyOf` made itself, and it still copies anything else, however genuinely unmodifiable that other thing is.

Neither wrapping style touches the **elements**. Both refuse a write to the list itself while leaving every element exactly as mutable as it always was:

```java
List<StringBuilder> notes = List.of(new StringBuilder("hi"));
notes.get(0).append(" there");    // fine, the list never objected
System.out.println(notes);        // [hi there]
notes.add(new StringBuilder("nope"));   // throws UnsupportedOperationException
```

An unmodifiable list of mutable elements is not an immutable list of elements. It is an immutable list, full stop, of whatever those elements happen to be, and if they are mutable the list was never going to help.

### Producing a changed copy: withers and builders

Once setters are gone, "changing" an immutable object means producing a new one that differs in one place. A **wither** method does exactly that, named `withX` by convention, returning a new instance built from the current one with a single field replaced. It reads well for a handful of fields. Once a type has enough fields that a constructor call, or a chain of withers, stops being readable, a **builder** trades that away: a separate mutable object accumulates the fields across several calls and produces the immutable target only at the end, with `build()`. The mutability lives in the builder, on purpose, for exactly as long as construction takes, and the object it hands back has none of it.

### `java.time` as the worked example

`java.time.LocalDate` and its neighbours are immutable end to end: every field is `final`, there are no setters, and every method that looks like a mutation is a wither under a shorter name.

```java
LocalDate a = LocalDate.of(2026, 8, 31);
LocalDate b = a.plusDays(10);
System.out.println(a);              // 2026-08-31
System.out.println(b);              // 2026-09-10
System.out.println(a == b);         // false
```

`plusDays` does not change `a`. It returns a different `LocalDate`, and `a` is exactly what it was before the call. Every arithmetic method on the class follows the same shape, which is why a `LocalDate` can be passed around a large codebase without anyone needing to check whether some other part of the program just changed it under them.

### The cost, and the honest answer

Every wither call and every defensive copy allocates. For a small value like a date that cost is negligible; for a large collection copied on every construction it is not automatically negligible, and guessing which side of that line a given type sits on is how a correct instinct turns into a wrong one. The honest answer is to measure it once the allocation is suspected of mattering, with the profiling and benchmarking tools stage 6 covers, rather than to reject the recipe on a hunch about cost that was never checked.

A `final` field also carries a specific guarantee from the Java memory model about when its value becomes visible to another thread without further synchronisation; stage 4 states that guarantee properly, and until then the simpler fact, that nothing in the class can reassign it after construction, is the one this lesson needs.

### When mutability is the right call

Not everything should be immutable. A **builder** is deliberately mutable while it accumulates state, and stops mattering the moment `build()` returns. A **buffer**, such as a `StringBuilder` assembling text or a byte buffer filling from a socket, exists specifically to be appended to cheaply, and copying it on every append would defeat the reason it exists. A **cache** has to accept new entries after it is created, or it is not doing the job of a cache. And some objects have an identity that outlives any one of their values, where the history of changes **is** the object, such as a bank account balance or a game entity's position: forcing those into "produce a new one on every change" describes something other than what they are for.

## Practice

1. ▢ Predict what each line prints, and explain the second one.

   ```java
   List<String> once = List.copyOf(List.of("a", "b", "c"));
   List<String> twice = List.copyOf(once);
   System.out.println(once.equals(twice));
   System.out.println(once == twice);
   ```

<details markdown="1"><summary>Hint</summary>

`List.copyOf` is documented to return an unmodifiable list. Ask what it might do differently when the argument is already one of its own results, rather than assuming every call copies.

</details>

<details markdown="1"><summary>Check</summary>

`true`, then `true`.

The lists are equal because they hold the same elements, which is unsurprising. The identity line is the interesting one: `List.copyOf` recognises that `once` is already the immutable implementation it would have produced itself, and returns it unchanged rather than copying it again. Hand it a `Collections.unmodifiableList` view instead of one of its own results and the identity check comes back `false`, because that view is a different implementation and `List.copyOf` has no way to know its backing list will never change.

</details>

2. ▢ Find the bug. `Booking` is meant to be immutable.

   ```java
   record Booking(String guest, List<String> requests) {
       Booking(String guest, List<String> requests) {
           this.guest = guest;
           this.requests = new ArrayList<>(requests);
       }
   }
   ```

   ```java
   List<String> req = new ArrayList<>(List.of("late checkout"));
   Booking b = new Booking("Priya", req);
   req.add("extra towels");
   b.requests().add("airport shuttle");
   System.out.println(b.requests());
   ```

<details markdown="1"><summary>Check</summary>

`[late checkout, airport shuttle]`.

The compact constructor's copy stops `req.add("extra towels")` from reaching the field, which is why that request is missing from the output. But the accessor `requests()` was never overridden, so it still hands back the same internal `ArrayList` the constructor created, and `b.requests().add(...)` mutates it directly. The fix is an overridden accessor that returns `List.copyOf(requests)` or an unmodifiable view, so the object refuses that write the same way it already refuses the first one.

</details>

3. ▢ Predict both lines.

   ```java
   LocalDate booked = LocalDate.of(2026, 12, 24);
   LocalDate rebooked = booked.plusDays(7);
   System.out.println(booked);
   System.out.println(booked == rebooked);
   ```

<details markdown="1"><summary>Check</summary>

`2026-12-24`, then `false`.

`plusDays` is a wither: it computes and returns a new `LocalDate` seven days later and leaves `booked` exactly as it was. Nothing about calling a method named like an action on `booked` changes `booked` itself, which is the entire point of the class being immutable.

</details>

4. ▢ You are given `record LineItem(String sku, int quantity, List<String> notes) {}`. Walk through the recipe and say exactly what is still missing before this type is actually immutable, then write the fix.

<details markdown="1"><summary>Check</summary>

`final` fields and no setters come free from being a record. Missing: the class is implicitly final already, so that box is ticked too, but there is no defensive copy of `notes` on the way in, and the generated accessor `notes()` hands back whatever list it was given, which is the same leak this lesson opened with. The fix is a compact constructor that copies, and an overridden accessor that returns an unmodifiable view or another copy:

```java
record LineItem(String sku, int quantity, List<String> notes) {
    LineItem {
        notes = List.copyOf(notes);
    }
}
```

Assigning `List.copyOf(notes)` to the compact constructor's own parameter both copies and makes the result unmodifiable in one line, which also makes a separately overridden accessor unnecessary here, since the field itself is now something a caller cannot mutate through.

</details>

5. ▢ A colleague proposes making every field of every class in a new service `final` and banning setters project-wide, no exceptions. Where does that rule cause real damage, and what would you say instead?

<details markdown="1"><summary>Check</summary>

It breaks anything whose job depends on being mutated after construction: a builder accumulating fields before `build()`, a `StringBuilder`-style buffer assembling output incrementally, a cache that has to accept new entries as they arrive, and any object whose current state is the point, such as a running total or a game entity's position, where "produce a new one on every change" is not a lighter version of the same object but a different design entirely. The rule worth stating is narrower: make the default model, the value types passed between parts of the system, immutable, and treat a mutable class as a deliberate choice for the small set of things, builders, buffers, caches, and stateful identity, that need it.

</details>

## Real-world reps

- [ ] Take a record you already have and check every component's type. For each one that is a `List`, a `Map`, an array, or another mutable type, add a defensive copy in the constructor and an overridden accessor, then confirm mutating the original argument and mutating through the accessor both stop working.
- [ ] Run the `List.copyOf` identity comparison yourself, once against a list `List.copyOf` produced and once against a `Collections.unmodifiableList` view, and confirm which one comes back as the same instance.
- [ ] Write a wither method by hand for a small immutable class of your own, then decide at what field count you would reach for a builder instead, and say why in one sentence.
- [ ] Tomorrow: open a class you already have with a setter for every field, and for each field decide whether anything in the codebase actually needs to reassign it after construction, or whether the setter is there out of habit.

## Going further

- [`List`](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/List.html): `copyOf`, and the unmodifiable list it returns
- [`Collections`](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/Collections.html): `unmodifiableList` and the rest of the view-returning wrappers
- [`LocalDate`](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/time/LocalDate.html): an immutable value type worked all the way through
- [Modelling](../reference/modelling.md): the reference sheet for this stage
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
