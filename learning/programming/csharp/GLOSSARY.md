---
title: Glossary
description: "Canonical terms for C#"
type: glossary
---

# C# Glossary

Canonical terms for owning a C# service, and for naming precisely where a Java instinct misleads.

## Terms

**Background GC**:
The mode that lets managed threads keep running while a generation 2 collection proceeds on a dedicated background thread (one for workstation GC, one per logical processor for server GC). Only ever applies to generation 2; generation 0 and generation 1 collections are always non-concurrent.
_Avoid_: assuming it removes all pausing (a foreground GC can still suspend every thread if generation 0 or 1 needs to collect while a background generation 2 collection is running)

**Foreground GC**:
A generation 0 or generation 1 collection that runs while a background generation 2 collection is in progress, suspending every managed thread (including pausing the background collection) until it finishes.
_Avoid_: treating this as a failure of background GC (background GC only ever promised concurrency for generation 2; generation 0 and 1 were never concurrent to begin with)

**Generation (GC)**:
One of three age-based divisions (0, 1, 2) of the managed heap. Every new object starts in generation 0; surviving a collection promotes it to the next generation. The split lets a collection reclaim memory in a small, frequently-turned-over portion of the heap instead of the whole thing.
_Avoid_: assuming an object is collected once, wherever it lives (an object is repeatedly re-examined and promoted across generations until it either dies or reaches generation 2)

**Large Object Heap (LOH)**:
A separate heap for objects above a size threshold, bypassing the generation 0 to 1 to 2 promotion path entirely. Sometimes called generation 3, but it is only collected as part of a generation 2 collection, never as cheaply as a small object dying in generation 0.
_Avoid_: assuming a large object gets its own cheap, frequent collection (it rides along with the most expensive kind of collection this system has, generation 2)

**Reference type**:
A type (every `class`) where assigning a variable of that type copies a reference, not the underlying data; two variables can point at the same object, and a mutation through either is visible through both.
_Avoid_: object type (ambiguous with C#'s `object` base type)

**Server GC**:
A GC flavor that collects across multiple threads, typically one per logical processor, built for a server application needing high throughput and scalability. Can cause contention when many processes each running server GC share the same small number of CPUs.
_Avoid_: assuming it is always the better choice for a service (many small processes sharing one host, each running server GC, compete for the same CPUs; workstation GC with concurrent GC disabled is the documented fix for that shape of deployment)

**Value type**:
A type (every `struct`, plus the built-in numeric types) where assigning, passing, or returning a variable of that type copies the entire value; two variables of a value type are always independent copies.
_Avoid_: primitive type (too narrow; a user-defined struct is a value type too)

**Workstation GC**:
The default GC flavor for a standalone app, collecting with essentially one thread. A hosted app's default flavor is decided by its host rather than always defaulting to workstation.
_Avoid_: assuming a hosted service always defaults to workstation GC (the host, such as ASP.NET Core, decides the default flavor a hosted app starts with)
