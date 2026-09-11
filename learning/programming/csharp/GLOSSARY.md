---
title: Glossary
description: "Canonical terms for C#"
type: glossary
---

# C# Glossary

Canonical terms for owning a C# service, and for naming precisely where a Java instinct misleads.

## Terms

**Generation (GC)**:
One of three age-based divisions (0, 1, 2) of the managed heap. Every new object starts in generation 0; surviving a collection promotes it to the next generation. The split lets a collection reclaim memory in a small, frequently-turned-over portion of the heap instead of the whole thing.
_Avoid_: assuming an object is collected once, wherever it lives (an object is repeatedly re-examined and promoted across generations until it either dies or reaches generation 2)

**Large Object Heap (LOH)**:
A separate heap for objects above a size threshold, bypassing the generation 0 to 1 to 2 promotion path entirely. Sometimes called generation 3, but it is only collected as part of a generation 2 collection, never as cheaply as a small object dying in generation 0.
_Avoid_: assuming a large object gets its own cheap, frequent collection (it rides along with the most expensive kind of collection this system has, generation 2)

**Reference type**:
A type (every `class`) where assigning a variable of that type copies a reference, not the underlying data; two variables can point at the same object, and a mutation through either is visible through both.
_Avoid_: object type (ambiguous with C#'s `object` base type)

**Value type**:
A type (every `struct`, plus the built-in numeric types) where assigning, passing, or returning a variable of that type copies the entire value; two variables of a value type are always independent copies.
_Avoid_: primitive type (too narrow; a user-defined struct is a value type too)
