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

_Added as lessons establish them._
