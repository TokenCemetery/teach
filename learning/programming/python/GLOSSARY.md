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

**Editable install**:
An installation that puts a project on the import path while continuing to read its source files in place, so edits take effect with no reinstall. It is what makes a project importable from any directory, rather than only from the one containing it.
_Avoid_: development install, symlink, `sys.path` entry

**Exception chaining**:
The link Python records between a caught exception and one raised while handling it. `raise New() from exc` states a direct cause; omitting `from` still chains, but reads as an accident.
_Avoid_: wrapping, nesting, rethrowing

**Falsy**:
A property of an object rather than of a comparison: `False`, `None`, any numeric zero, and any empty container all test false in a boolean context. Everything else tests true, including `"0"` and `[0]`.
_Avoid_: empty, null, blank, unset

**Generator**:
The **iterator** a function containing `yield` returns when called, holding a frozen frame that resumes where it left off. The function may be called repeatedly; each generator it produces is consumed once.
_Avoid_: coroutine, lazy list, stream, iterable (which is wider)

**Gradual typing**:
The property that annotations are optional per function and are checked by a separate tool, so an annotated and an unannotated function coexist. The unannotated one is treated as `Any` at the boundary, which is why partial coverage buys much less than it looks like.
_Avoid_: optional typing, static typing, duck typing

**Hashable**:
A property of an object whose hash never changes, which is what a `dict` key and a `set` member must be. Immutable built-ins are hashable, and a tuple only inherits the property if everything inside it has it.
_Avoid_: comparable, immutable, indexable

**Invariance**:
The rule that a container of a subtype is not a container of a supertype, which holds for every mutable generic: `list[int]` is not a `list[object]`. Read-only types such as `Sequence` are covariant instead, which is why they belong in parameters.
_Avoid_: strictness, type mismatch, casting

**Late binding**:
The behaviour of a closure that looks its enclosing names up when it runs rather than when it was defined. Functions built in a loop therefore all see the loop variable's final value.
_Avoid_: lazy evaluation, capture by reference

**Lock file**:
The exact set of package versions a resolver computed, including transitive ones, with hashes. Distinct from a **requirement**, which is a range: the requirement travels to other people's resolvers, the lock reproduces one install.
_Avoid_: requirements file, pinned dependencies, manifest

**Module**:
One `.py` file, executed once per process and cached in `sys.modules`. Importing it binds a name to that single module object, so module-level state is process-wide state.
_Avoid_: file, script, library, unit

**Naive datetime**:
A `datetime` with no `tzinfo`, which records a wall-clock reading without saying which clock produced it. It cannot be compared or subtracted against an aware one, and it is a guess the moment two machines are involved.
_Avoid_: local time, UTC, timestamp

**Narrowing**:
What a checker does to a type after a test it can follow, such as `if x is None: return`, so the code below knows more than the annotation did. It is the alternative to silencing an error, and it produces a runtime check only when written as an `assert`.
_Avoid_: casting, asserting, type checking

**Package**:
A directory of modules with an `__init__.py`, importable under a dotted name. Distinct from a **distribution**, the installable artifact on an index, which may contain several packages or none.
_Avoid_: library, distribution, dependency, project

**Rebinding**:
Pointing an existing **name** at a different object, which is what every assignment does. It is invisible to every other name, and it is the operation people mistake for mutation.
_Avoid_: reassignment, overwriting, updating

**Shallow copy**:
A new container holding the same objects as the original, which is what `[:]`, `list()`, `dict()` and `copy.copy` all produce. The container is independent and its contents are not.
_Avoid_: copy (unqualified), clone, snapshot

**Structural typing**:
Conformance decided by an object's shape rather than by what it inherits, which is what `Protocol` expresses to a checker. It works on classes you do not own, and `isinstance` against a runtime-checkable protocol verifies attribute names only.
_Avoid_: duck typing, interface, subclassing

**Virtual environment**:
A directory holding its own `site-packages` and interpreter links, so one project's dependencies cannot displace another's. Activating it only changes `PATH`; running its interpreter by path is equivalent.
_Avoid_: container, sandbox, installation, environment (unqualified)

**Wheel**:
The built distribution that installs by unpacking, with no build step and no code from the package executed. Its filename records the interpreter, ABI and platform it supports, and `py3-none-any` means pure Python everywhere.
_Avoid_: package, archive, binary, egg
