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

**Context manager**:
An object with `__enter__` and `__exit__`, used through `with`, whose exit runs on every path out of the block. `as` binds whatever `__enter__` returned, which is not always the manager itself.
_Avoid_: resource, wrapper, `try/finally` (which it replaces rather than names)

**EAFP**:
Easier to ask forgiveness than permission: attempt the operation and handle the exception, rather than testing first. Preferred in Python because a `try` that does not raise is nearly free, and because a check and the action it guards can disagree.
_Avoid_: exception-driven design, error handling, defensive programming

**Exception chaining**:
The link Python records between a caught exception and one raised while handling it. `raise New() from exc` states a direct cause; omitting `from` still chains, but reads as an accident.
_Avoid_: wrapping, nesting, rethrowing

**Falsy**:
A property of an object rather than of a comparison: `False`, `None`, any numeric zero, and any empty container all test false in a boolean context. Everything else tests true, including `"0"` and `[0]`.
_Avoid_: empty, null, blank, unset

**Generator**:
The **iterator** a function containing `yield` returns when called, holding a frozen frame that resumes where it left off. The function may be called repeatedly; each generator it produces is consumed once.
_Avoid_: coroutine, lazy list, stream, iterable (which is wider)

**Hashable**:
A property of an object whose hash never changes, which is what a `dict` key and a `set` member must be. Immutable built-ins are hashable, and a tuple only inherits the property if everything inside it has it.
_Avoid_: comparable, immutable, indexable

**Late binding**:
The behaviour of a closure that looks its enclosing names up when it runs rather than when it was defined. Functions built in a loop therefore all see the loop variable's final value.
_Avoid_: lazy evaluation, capture by reference

**Module**:
One `.py` file, executed once per process and cached in `sys.modules`. Importing it binds a name to that single module object, so module-level state is process-wide state.
_Avoid_: file, script, library, unit

**Naive datetime**:
A `datetime` with no `tzinfo`, which records a wall-clock reading without saying which clock produced it. It cannot be compared or subtracted against an aware one, and it is a guess the moment two machines are involved.
_Avoid_: local time, UTC, timestamp

**Package**:
A directory of modules with an `__init__.py`, importable under a dotted name. Distinct from a **distribution**, the installable artifact on an index, which may contain several packages or none.
_Avoid_: library, distribution, dependency, project

**Rebinding**:
Pointing an existing **name** at a different object, which is what every assignment does. It is invisible to every other name, and it is the operation people mistake for mutation.
_Avoid_: reassignment, overwriting, updating

**Shallow copy**:
A new container holding the same objects as the original, which is what `[:]`, `list()`, `dict()` and `copy.copy` all produce. The container is independent and its contents are not.
_Avoid_: copy (unqualified), clone, snapshot
