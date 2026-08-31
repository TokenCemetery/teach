---
title: Glossary
description: Canonical terms for Java
type: glossary
---

# Java Glossary

Canonical terms for this workspace. A term lands here once it can be used correctly, not when it is first mentioned, so this grows as lessons are earned.

## Usage in this workspace

Three words are used loosely in ways that would make later lessons ambiguous, and each one hides a mistake that compiles cleanly, so all three are pinned from the start:

**Reference**:
A value that refers to an object, held in a variable, a field, or an array slot. Everything in Java is passed by value, and for objects the value passed is the reference, which is why a method can mutate what it was given and can never rebind the caller's variable.
_Avoid_: pointer, handle, alias

**Final**:
A promise that a variable, field or parameter will not be reassigned. It says nothing about the object on the other end, so a `final` list can still be cleared.
_Avoid_: immutable, constant, read-only

**Thread-safe**:
A property of a class relative to a stated contract: correct behaviour when accessed concurrently, with the contract saying what "correct" means. It is not a synonym for using `synchronized`, and a class built entirely from thread-safe parts is not automatically one.
_Avoid_: synchronised, atomic, concurrent

## Terms

**Aliasing**:
The situation where two or more variables hold references to one object, which is what assignment always produces. Mutating through either is observable through both.
_Avoid_: sharing, pointing, double reference

**Autoboxing**:
The implicit conversion between a primitive and its wrapper type, performed by calls the source code does not show. `Integer.valueOf` caches `-128` to `127`, which is why `==` on boxed values is correct for small numbers and wrong for large ones.
_Avoid_: casting, wrapping, promotion

**Canonical constructor**:
The constructor whose parameters are exactly a record's components, in declaration order. It is generated unless you declare it, and every other constructor on the record has to delegate to it, which is why validation placed there cannot be bypassed.
_Avoid_: default constructor, primary constructor, main constructor

**Checked exception**:
A `Throwable` outside `RuntimeException` and `Error`, which the compiler forces every caller to catch or declare. It earns its place only when a reasonable caller can act on the failure, because a caller who can only give up will wrap it or swallow it instead.
_Avoid_: compile-time exception, declared error, fatal exception

**Closeable stream**:
A `Stream` backed by an open operating-system handle, which is what `Files.lines`, `Files.walk` and `Files.find` return. Unlike a stream over a collection it must be closed, and skipping that usually appears to work, because unreachable ones are cleaned up eventually and the descriptors run out only under load.
_Avoid_: file stream, lazy stream, resource

**Compact constructor**:
A canonical constructor written with no parameter list, whose body runs before the components are assigned to the fields. Assigning to the parameter is what reaches the field, and assigning to `this.field` there is a compile error rather than a redundancy.
_Avoid_: compact form, short constructor, implicit constructor

**Covariance (of arrays)**:
The rule that `String[]` is usable as an `Object[]`, which lets a type error survive compilation and surface as `ArrayStoreException`. Generics are invariant precisely to close this hole.
_Avoid_: polymorphism, subtyping, generics compatibility

**Defensive copy**:
A copy taken so that a reference cannot be used to change an object from outside it: on the way in so a caller's later mutation cannot reach a field, and on the way out so a returned reference cannot either. The second half is the half that gets forgotten.
_Avoid_: deep copy, clone, snapshot

**Downstream collector**:
A collector handed to another one, such as `groupingBy`, `partitioningBy` or `teeing`, which runs against each group or branch rather than against the whole stream. It is what turns a grouping into counts, sums or a nested map without a second pass.
_Avoid_: nested collector, sub-collector, inner reduction

**Encounter order**:
The order in which a stream's elements arrive, where the source has one. `findFirst`, sort stability and the order of a collected `List` are all defined against it, and a source such as a `HashSet` gives them nothing to be defined against.
_Avoid_: sort order, iteration order, sequence

**Erasure**:
The compiler's discarding of type arguments, which leaves `List<String>` and `List<Integer>` as one class at run time. Every restriction on generics follows from it, and so does a `ClassCastException` on a line that contains no cast.
_Avoid_: type deletion, unboxing, runtime generics

**Exhaustive switch**:
A `switch` whose labels the compiler can prove cover every possible value, which is what permits omitting `default`. Omitting it is the point rather than an oversight, because adding an alternative then fails compilation at every place that has to decide again.
_Avoid_: complete switch, total switch, default-free switch

**Fragile base class problem**:
The coupling inheritance creates in both directions: a superclass author breaks subclasses by changing behaviour that looked internal, and a subclass author breaks by depending on more than the superclass promised. It is why every `protected` member is published API.
_Avoid_: tight coupling, bad inheritance, base class rot

**Functional interface**:
An interface with exactly one abstract method, which is what lets a lambda or a method reference stand in for an instance of it. The `@FunctionalInterface` annotation states and enforces the intent, and is never required for the lambda to work.
_Avoid_: lambda interface, callback, SAM type

**Hiding**:
A subclass declaring a `static` method or a field with the same name as one in the superclass. It resolves on the declared type of the reference rather than the runtime type of the object, which is the opposite of overriding and looks identical in the source.
_Avoid_: overriding, shadowing, masking

**Interning**:
Placing a value in a shared pool so that identical values are one object. String literals and compile-time constants are interned, which makes `==` on strings appear to work until a value is built at run time.
_Avoid_: caching, deduplication, pooling

**Invariance (of generics)**:
The rule that `List<String>` is not a `List<Object>`, whatever the relationship between the type arguments. It is the deliberate opposite of array covariance, and it is what moves the error from run time to compile time.
_Avoid_: strictness, missing polymorphism, type mismatch

**Local (of a date or time)**:
A value naming a reading on a calendar or a wall clock with no zone attached, which is what `LocalDate`, `LocalTime` and `LocalDateTime` are. None of them is a point on the universal timeline, so none converts to an `Instant` without being told a zone, and using one as a timestamp is the most common mistake in the time API.
_Avoid_: naive time, zoneless, floating time

**Natural ordering**:
The ordering a type defines for itself by implementing `Comparable`. A sorted collection uses it instead of `equals`, so two elements that compare as zero are one element as far as a `TreeSet` is concerned.
_Avoid_: default sort, comparison, ranking

**PECS**:
Producer extends, consumer super: `? extends T` for a structure you only read from, `? super T` for one you only write to. A parameter that must do both takes a plain `T` and gives up the flexibility, which is the trade rather than a defect.
_Avoid_: wildcards, variance, bounded generics

**Raw type**:
A generic type used with no type argument, such as `List` in place of `List<String>`. It switches off checking for every member whose signature mentions the parameter, which is how a wrong element gets in silently and surfaces as a cast failure somewhere else entirely.
_Avoid_: untyped collection, legacy generic, unparameterised type

**Sealed hierarchy**:
A supertype whose permitted direct subtypes are fixed at compile time, so the set of alternatives is closed and the compiler can enumerate it. That is what makes a `switch` over it exhaustive with no `default`.
_Avoid_: closed class, final hierarchy, restricted inheritance

**Short-circuiting operation**:
A stream operation that can finish without pulling every element through the pipeline, such as `findFirst`, `anyMatch` or `limit`. It is what makes an infinite source usable, and it is what an operation such as `sorted` takes away, since sorting has to see everything first.
_Avoid_: early exit, lazy operation, break

**Suppressed exception**:
An exception attached to another rather than replacing it, which is what try-with-resources does when a resource fails to close while an exception from the body is already propagating. A hand-written `finally` loses the original instead, with no trace that it happened.
_Avoid_: secondary exception, ignored exception, nested exception

**Terminal operation**:
The stream operation that makes the pipeline run and consumes it, such as `forEach`, `collect` or `count`. Nothing before it executes, and nothing after it is possible on that stream, because a second terminal call throws.
_Avoid_: final operation, sink, evaluation

**Total order**:
A comparator or natural ordering under which no two distinct elements compare as zero. Sorted collections need one, and a chain of keys provides it only if the last key is unique per element.
_Avoid_: full sort, strict ordering, complete comparator

**View**:
A collection that reads through to another one rather than holding its own contents, which is what `Collections.unmodifiableList` and `Map.values` return. It refuses writes through itself and still shows every change made to the collection behind it.
_Avoid_: copy, snapshot, wrapper

**Wither method**:
A method returning a new instance that differs in one component, conventionally named `withX`. It is the immutable replacement for a setter, and it makes the cost visible, since every call allocates.
_Avoid_: setter, mutator, copy method
