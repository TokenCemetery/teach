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

**Covariance (of arrays)**:
The rule that `String[]` is usable as an `Object[]`, which lets a type error survive compilation and surface as `ArrayStoreException`. Generics are invariant precisely to close this hole.
_Avoid_: polymorphism, subtyping, generics compatibility

**Interning**:
Placing a value in a shared pool so that identical values are one object. String literals and compile-time constants are interned, which makes `==` on strings appear to work until a value is built at run time.
_Avoid_: caching, deduplication, pooling

**Natural ordering**:
The ordering a type defines for itself by implementing `Comparable`. A sorted collection uses it instead of `equals`, so two elements that compare as zero are one element as far as a `TreeSet` is concerned.
_Avoid_: default sort, comparison, ranking

**Total order**:
A comparator or natural ordering under which no two distinct elements compare as zero. Sorted collections need one, and a chain of keys provides it only if the last key is unique per element.
_Avoid_: full sort, strict ordering, complete comparator

**View**:
A collection that reads through to another one rather than holding its own contents, which is what `Collections.unmodifiableList` and `Map.values` return. It refuses writes through itself and still shows every change made to the collection behind it.
_Avoid_: copy, snapshot, wrapper
