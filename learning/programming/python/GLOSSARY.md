---
title: Glossary
description: Canonical terms for Python
type: glossary
---

# Python Glossary

Canonical terms for this workspace. A term lands here once it can be used correctly, not when it is first mentioned, so this grows as lessons are earned.

## Usage in this workspace

Three words mean something narrower in Python than they do in most other languages. Carrying the wider meaning across produces code that runs and is still wrong, so all three are pinned from the start:

**Name**:
A binding in a namespace that refers to an object. Assignment rebinds the name and never copies the object, which is why two names can refer to the same list.
_Avoid_: variable (as a box holding a value), pointer, reference

**Mutability**:
A property of an object, never of the name bound to it. A tuple is immutable even when it holds a list that is not.
_Avoid_: constant, final, read-only

**Iterator**:
An object with `__next__` that yields values once and is then exhausted. An **iterable** is anything that can produce one, so a list can be iterated repeatedly and its iterator cannot.
_Avoid_: generator (which is one specific kind), stream, sequence

## Terms

**Aliasing**:
The situation where two or more **names** refer to one object, which is what assignment always produces. Mutating through either name is observable through all of them.
_Avoid_: sharing, pointing, referencing

**Falsy**:
A property of an object rather than of a comparison: `False`, `None`, any numeric zero, and any empty container all test false in a boolean context. Everything else tests true, including `"0"` and `[0]`.
_Avoid_: empty, null, blank, unset

**Hashable**:
A property of an object whose hash never changes, which is what a `dict` key and a `set` member must be. Immutable built-ins are hashable, and a tuple only inherits the property if everything inside it has it.
_Avoid_: comparable, immutable, indexable

**Late binding**:
The behaviour of a closure that looks its enclosing names up when it runs rather than when it was defined. Functions built in a loop therefore all see the loop variable's final value.
_Avoid_: lazy evaluation, capture by reference

**Rebinding**:
Pointing an existing **name** at a different object, which is what every assignment does. It is invisible to every other name, and it is the operation people mistake for mutation.
_Avoid_: reassignment, overwriting, updating

**Shallow copy**:
A new container holding the same objects as the original, which is what `[:]`, `list()`, `dict()` and `copy.copy` all produce. The container is independent and its contents are not.
_Avoid_: copy (unqualified), clone, snapshot
