---
title: 37. The Shape of an Object
description: A small object is mostly header, and the flag that shrinks it is off by default
type: lesson
---

# Lesson 37. The Shape of an Object

**Mission link:** Owning a Java service in production means caring about what one allocation actually costs, because a header a few bytes larger than it needs to be, multiplied by the millions of small objects a real workload allocates, is exactly the difference between a heap that never troubles you and the collection pauses lesson 36 taught you to read.
**Primary source:** [JEP 519, Compact Object Headers](https://openjdk.org/jeps/519)
**Prerequisites:** [Lesson 36](0036-where-memory-goes.md), [Lesson 8](0008-records.md)

## Warm-up

Lesson 8 showed that `record Point(double x, double y)` generates a private final field per component and nothing else beyond that: an accessor, a canonical constructor, and `equals`, `hashCode` and `toString`, all derived from those two fields. Take a record with two `int` fields instead, 4 bytes each, 8 bytes of data you can point to in the declaration. Does an instance of it occupy 8 bytes, or something else?

<details markdown="1"><summary>Check</summary>

Something else, and by a wide margin. Every object the JVM allocates carries a small, fixed block of bookkeeping ahead of its fields, called the object header, and the whole allocation is then rounded up to the next 8-byte boundary, so whatever is left over between the last field and that boundary is padding. Neither the header nor the padding appears anywhere in the declaration. The rest of this lesson puts an exact, measured number on both.

</details>

## Know this

### The header, the fields, then the padding

An object's bytes are never only its fields. Every instance begins with a small, fixed block of bookkeeping the JVM writes before your fields even start, called the object header, and nothing in the language lets you see it, name it, or opt out of it by declaring your fields differently. After the header come the fields, and after the last field the JVM rounds the whole allocation up to the next 8-byte boundary, so there is often a handful of bytes left over that hold nothing at all, present purely so the next object in memory starts at an aligned address. Lesson 8 used the word "header" for something else entirely, the component list that generates a record's fields and methods; this lesson's header is a different thing, a block of runtime bookkeeping that exists for every object, record or otherwise, and has nothing to do with what you wrote. Lesson 8 answered what a record's declaration generates. This lesson answers what one instance of it actually occupies once it exists: header, fields and padding together.

### What a record actually costs

Take `record Point(int x, int y)`. Two `int` fields are 4 bytes each, 8 bytes of data you asked for and can account for by reading the declaration. Measured with the allocation profiler, one `Point` instance occupies 24 bytes by default. Sixteen of those 24 bytes, two thirds of the object, are header and padding around the 8 bytes you actually declared: the default layout for a small object is mostly overhead, not mostly data. `-XX:+UseCompactObjectHeaders` shrinks the same instance to 16 bytes, removing a third of the object without touching a single field, because the flag changes only what the header looks like. JEP 534 states the underlying change in bits rather than bytes: on a 64-bit architecture the object header itself shrinks from 96 bits to 64 bits, from 12 bytes to 8. That single fact explains both measurements at once. The default header is 12 bytes, so `Point` is 12 bytes of header plus 8 bytes of `int` data, 20 bytes, rounded up to the next multiple of 8, 24. The compact header is 8 bytes, so the same object is 8 plus 8, 16 exactly, with nothing left over to pad. The arithmetic generalises past records and past two-field objects. `int[5]`, a five-element `int` array, measures 40 bytes: a 16-byte header, the same 12-byte base plus the 4-byte length every array carries on top of it, 20 bytes of payload, five `int`s at 4 bytes each, and 4 bytes of padding to reach the next multiple of 8. Two declarations that look like they cost exactly what their fields add up to, an eight-byte record and a twenty-byte array, actually cost 24 and 40. The gap is the header, every time, and it does not shrink because the object is small; if anything a small object is where the header dominates most, since there is less data around it to dilute a fixed cost.

### Compact object headers, a product flag and an opt-in decision

On JDK 25, `-XX:+UseCompactObjectHeaders` is reported as `{product lp64_product}`, defaulting to `false`, and the JVM accepts it directly with no `-XX:+UnlockExperimentalVMOptions` needed. That absence is itself informative: the same layout spent JDK 24 behind exactly that unlock flag as an experimental feature, and JEP 519 is the act of promoting it to an ordinary, supported product feature, on the strength of testing its authors describe as the JDK's own full test suite plus, independently, hundreds of services run in production at Amazon, some on backports to JDK 17 and JDK 21 rather than JDK 25 itself. None of that testing history makes it the default. JEP 519 states as an explicit non-goal that compact object headers becoming the default layout is not what this particular change is for, and JDK 25 ships exactly as measured above, off unless asked for. A related JEP, 534, has already been delivered on the same terms for JDK 27, where the default does flip to `true`, so the fact this lesson is teaching, off by default, is a property of JDK 25 specifically and not a permanent one. JEP 534 states its own case for the eventual default change in three words worth remembering together: a smaller header means a smaller heap for the same objects, more instances fitting in the same amount of memory the machine actually has, and more of them sitting close enough together in that memory for the processor's cache to help rather than miss. Read the JDK 25 situation plainly while it lasts: this is a mature, exercised feature that its own authors are still choosing not to hand you unasked.

The JEP's own motivation section cites case studies for why the change was worth making at all, and they are worth knowing even though none of them were run for this lesson: with the flag on, the SPECjbb2015 benchmark used 22 per cent less heap space and 8 per cent less CPU time in one setting, the number of garbage collections it triggered fell by 15 per cent under both the G1 and Parallel collectors, and a highly parallel JSON-parsing benchmark ran about 10 per cent faster. Treat those the way every ratio in this stage should be treated: as evidence that the effect can be large on an allocation-heavy workload, measured on somebody else's hardware, running somebody else's benchmark, not as a number your own service will reproduce. Before turning the flag on anywhere that matters, two things are worth checking first rather than assumed. First, whether your workload's bottleneck is actually the volume of small objects it allocates, which is a question a profiler answers and a guess does not, and a header saving on an object you rarely allocate buys you nothing measurable. Second, whether anything in your toolchain inspects raw object layout directly, since one widely recommended tool for exactly that already does not work at all on a current JDK, which the last section of this lesson covers.

### Compressed ordinary object pointers, the other lever on the same problem

Object headers are one place a small object's size hides overhead; references to other objects are another, and JDK 25 already defaults to a fix for that one. `UseCompressedOops` is `true` by default, reported as `{ergonomic}` rather than as a flag you set, and what it buys is smaller references: instead of storing every object reference as a full 8-byte address, the JVM stores it as a 32-bit offset for heaps small enough that the offset still reaches every object, falling back to full-width references automatically once a heap grows past the point where that stops being possible. Every reference field, every array of references, and every reference-typed slot inside a collection is half the size it would otherwise be, which is why it is on by default rather than offered as a choice: the JVM already knows the heap size it is running with and can decide for itself whether the trick still applies. Compact object headers and compressed ordinary object pointers attack two different halves of the same object: one shrinks the header sitting at the front of every instance, the other shrinks every reference sitting inside one. They compound rather than compete, and only one of the two currently defaults to on.

### The price of a box

The header cost this lesson has been measuring applies to every object, including the ones autoboxing creates without a `new` anywhere in sight. An `int` costs 4 bytes and lives wherever it was declared, on the stack or inline inside another object's own fields. An `Integer` is a full object: its own header, its one `int` field, its own padding, the same shape as `Point` above but for a single field instead of two, and a reference to it costs additional bytes wherever that reference is stored. A `Map<String, Integer>` built to count occurrences, such as this one:

```java
static Map<String, Integer> countByLevel(String[] lines) {
    Map<String, Integer> counts = new HashMap<>();
    for (String line : lines) {
        String[] parts = line.split("\\s*\\|\\s*");
        String level = parts[1].toLowerCase();
        counts.put(level, counts.getOrDefault(level, 0) + 1);
    }
    return counts;
}
```

does not cost four bytes per count, whatever picture "a number in a map" brings to mind. Every call to `getOrDefault(level, 0) + 1` computes a new `int` and immediately boxes it into a fresh `Integer`, because `Integer` is immutable and the old boxed value cannot be incremented in place. Each entry in the map is therefore, at minimum, a map-internal node object holding a hash, a key reference and a value reference, plus the boxed `Integer` value object that node points to, plus whatever `String` object the key already was. None of those pieces is the four bytes the number itself would cost as a primitive; every one of them carries the same header-and-padding tax this lesson has been measuring, stacked once per piece rather than once per count. This is exactly what the stage's workload runs into at scale, and exactly why its fix, further along in this stage, replaces the map of boxed counters with a plain `int[]` indexed by severity: no boxing, no map node, one contiguous block of memory with a single header for the whole array rather than one header per count.

### When any of this is worth thinking about

Millions of small objects is the scale where a 16-byte saving per instance or a boxed `Integer` avoided actually shows up: a log-line indexer running over hundreds of thousands of lines many times over, a cache holding one entry per user session across a fleet, a numeric pipeline that allocates a wrapper type once per element of a large dataset. Below that scale, the same savings are just as real and just as invisible, because they are a fixed number of bytes multiplied by a small number of allocations, and no collection pause or heap graph will ever show them as the thing worth fixing. Most code sits at that second scale. A request handler that allocates a handful of records per call, called a modest number of times a second, has nothing to gain from shaving a third off an object header, because the header was never the bottleneck: a network call, a database round trip, or an algorithm doing more work than it needs to almost always costs orders of magnitude more than the header of any one object it touches. Reaching for a header flag or a boxing rewrite before measuring where your own allocations actually go is usually the wrong instinct, for the same reason reaching for a lock-free data structure before measuring contention usually is: the fix is real, and it is aimed at a problem you have not yet confirmed you have.

### How these numbers were obtained, and a tool to leave alone

Every byte figure in this lesson came from the allocation profiler's bytes-per-operation reading, an instrument that needs no agent, no extra dependency and no special flag, and that this stage relies on throughout rather than something assembled for this lesson alone. JOL, the Java Object Layout tool, is what nearly every article on this subject reaches for instead, and on a current JDK it needs a dynamically attached agent that the platform is already warning it intends to disallow by default in a future release, so nothing here is built on it.

## Practice

1. ▢ `record Point(int x, int y)` holds 8 bytes of data. Predict its measured size with default object headers, and again with `-XX:+UseCompactObjectHeaders`.

<details markdown="1"><summary>Check</summary>

24 bytes by default, 16 bytes with the flag. The 8 bytes of `int` data never change. What changes is the header in front of them, from 12 bytes to 8, and the object shrinks by twice that because the 12-byte header left 20 bytes to be padded up to 24 while the 8-byte header lands on 16 exactly. Losing 4 bytes of header also loses the 4 bytes of padding that header forced.

</details>

2. ▢ `int[5]` measures 40 bytes with default object headers. Predict the three pieces that sum to that number, and what each one is.

<details markdown="1"><summary>Check</summary>

A 16-byte header, 20 bytes of payload, five `int`s at 4 bytes each, and 4 bytes of padding to reach the next multiple of 8. An array's header carries the same bookkeeping any object's header does, plus the length the JVM needs to bounds-check every access.

</details>

3. ▢ A default `Point` is two thirds header and padding. Once `-XX:+UseCompactObjectHeaders` is on, is the object free of overhead, or does it still carry some?

<details markdown="1"><summary>Hint</summary>

The flag changed the header from 16 bytes to 8. The 8 bytes of `int` data did not move.

</details>

<details markdown="1"><summary>Check</summary>

It still carries overhead, half of the object rather than two thirds: 8 bytes of header against 8 bytes of data, 16 bytes total. The flag removes a third of the object, it does not remove the concept of a header. A small object always pays for one; the only question this lesson leaves open is how large that one is.

</details>

4. ▢ A teammate wants to add `-XX:+UseCompactObjectHeaders` to production's start-up flags this week, because "it's free, JEP 519 proves it works." Name the one question their plan skips, and what answers it.

<details markdown="1"><summary>Check</summary>

Whether this particular service's own bottleneck is actually the volume of small objects it allocates, which a profiler answers and a JEP's own case studies, run on someone else's workload and hardware, do not. JEP 519 being a stable, well-tested product feature is a fact about the feature's maturity, not a fact about whether this service will notice the difference; the JEP itself does not claim the flag should be everyone's default, and JDK 25 ships it off for exactly that reason.

</details>

5. ▢ `countByLevel` above calls `counts.getOrDefault(level, 0) + 1` and stores the result on every line. Name every distinct kind of object that one line can allocate, beyond the `String` key already produced by the split.

<details markdown="1"><summary>Check</summary>

A boxed `Integer` holding the incremented count, since `Integer` is immutable and the previous value cannot be updated in place, and, on the first sight of a given level, a new map-internal node to hold that key, its hash and a reference to the boxed value. None of those is the four bytes a reader picturing "a number in a map" might expect; each one pays a header of its own.

</details>

## Real-world reps

- [ ] Check whether the JDK you actually deploy reports `-XX:+UseCompactObjectHeaders` as `false` by default too, the same way this lesson checked it on JDK 25.
- [ ] Find one place in code you own where a primitive is stored in a boxed collection, such as a `List<Integer>` or a `Map<K, Long>`, and count how many distinct objects one entry actually costs once the box and the container's own internal node are both counted.
- [ ] Pick one small, frequently allocated type in a project you maintain and write one honest sentence on whether millions of instances of it are remotely plausible for that project's real traffic, before treating anything in this lesson as relevant to it.
- [ ] Search a project you maintain, or a library it depends on, for a comment, script or build flag that mentions JOL, and check whether whoever wrote it was relying on an agent JDK 25 already warns will stop working by default.
- [ ] Tomorrow: look at one `Map<String, Integer>` or similar boxed counter in code you own, and write down, honestly, whether you have ever measured that it allocates enough to matter, or whether it has simply never been questioned.

## Going further

- [JEP 450, Compact Object Headers (Experimental)](https://openjdk.org/jeps/450): the JDK 24 feature JEP 519 promoted from experimental to a product flag
- [JEP 534, Compact Object Headers by Default](https://openjdk.org/jeps/534): already delivered, targeting the release where this lesson's off-by-default fact stops being true
- [The runtime](../reference/the-runtime.md): the stage 6 reference sheet
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
