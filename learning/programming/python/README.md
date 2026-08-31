---
title: Python
description: "Own Python in production: ship it typed, tested, packaged and profiled"
type: topic
---

# Learning: Python

Become the engineer trusted to own Python on a team: able to ship a typed, tested, packaged Python service or tool, take a traceback or a profile to its root cause instead of guessing, and say concretely why someone's clever use of Python's dynamism is going to hurt them.

**Start here:** [0001. Names Are Bindings, Not Boxes](lessons/0001-names-are-bindings.md)
**Latest lesson:** [0014. The Standard Library](lessons/0014-the-standard-library.md)

## Success looks like

- Predict what a mutable default argument, a closure over a loop variable, and a shared list do, before running the code.
- Ship a package that installs and runs on a machine that is not the one it was written on.
- Add type hints a checker verifies, and fix what it reports rather than silencing it.
- Write `pytest` tests that fail informatively, using fixtures and parametrisation instead of copied test bodies.
- Find the slow part with a profiler and prove the fix with a measurement.
- Choose between threads, processes and `asyncio` from the shape of the workload, and state what the GIL does and does not prevent.
- Implement a dunder method or a context manager when the data model calls for one, and recognise when a plain function is the better answer.
- Review someone's Python and name precisely why a class, a metaclass, or an inheritance chain is the wrong tool there.

## Constraints

- Assumes no prior Python. Experience in another language shortens the early stages but is not required, and it brings habits Python punishes quietly: a class where a function would do, a loop where a comprehension reads better, a defensive copy the language already made.
- Needs only CPython and a terminal on any supported OS. Nothing in the arc requires paid tooling, a cloud account, or a second machine.
- CPython is the reference implementation throughout. Other implementations appear only where behaviour genuinely differs.
- Reps are small programs that fit one sitting. Spacing them across days is the mechanism, not an inconvenience.
- Typing and packaging move faster than the language does. Version-sensitive claims are checked against the current documentation and the relevant PEP, and any lesson that depends on a release says which one.

## Out of scope

- Web frameworks as subjects in their own right: Django, FastAPI, Flask.
- The scientific and machine-learning stack as a subject: NumPy, pandas, PyTorch. A workspace on adapter fine-tuning exists separately, at [`llm/finetuning`](../../llm/finetuning/README.md).
- Distribution beyond wheels published to an index: conda, OS packages, frozen single-file binaries.
- CPython internals past the point where they stop predicting program behaviour: bytecode, the C API, writing extension modules.
- Python 2, and migration from it.

## The arc

Seven stages, zero to senior. Not a lesson list: a stage takes several lessons, and the boundaries are soft.

| Stage | Covers | Done when |
|---|---|---|
| 1. Foundations | Objects and names, mutability and aliasing, lists, dicts, sets, tuples, truthiness, comprehensions, functions and argument passing | Can predict aliasing and mutation without running the code |
| 2. Idiom | Iterators and generators, context managers, exceptions as control flow, `dataclasses`, modules and packages, the standard library worth knowing | Reaches for a generator or a context manager rather than hand-rolling the loop and the `try/finally` |
| 3. Types and tooling | Annotations, generics, `Protocol`, checker strictness, linting and formatting, virtual environments, dependency and project management, building a wheel | A strict checker passes, and someone else can install the result |
| 4. The data model | Dunder methods, `__init__` versus `__new__`, properties, descriptors, class versus instance attributes, method resolution order, why metaclasses are almost never the answer | Implements the protocol a type needs, and can say when not to |
| 5. Testing | `pytest` mechanics, fixtures and scope, parametrisation, property-based testing, what deserves a mock and what does not, coverage as a signal rather than a target | Has a test suite that caught a regression before a human did |
| 6. Concurrency and performance | Threads, processes, `asyncio`, what the GIL actually serialises, blocking calls inside an event loop, profiling, the cost of attribute lookup and allocation | Chooses the concurrency model from the workload and proves the win from a profile |
| 7. Judgment | API and package design, deprecation, review, reading the standard library and the PEPs for answers | Trusted to make the call and to explain it to someone else |

## Lessons

Work through these in order.

| # | Lesson | Teaches |
|---|---|---|
| [0001](lessons/0001-names-are-bindings.md) | Names Are Bindings, Not Boxes | Assignment binds a name to an object and never copies it, so two names can mean one thing |
| [0002](lessons/0002-mutability-and-copying.md) | Mutability and Copying | Mutability belongs to the object, so an immutable container can still hold something that changes |
| [0003](lessons/0003-lists-and-slicing.md) | Lists and Slicing | A slice copies, in-place methods return None, and += mutates what + would rebuild |
| [0004](lessons/0004-dicts-and-sets.md) | Dicts and Sets | Keys must be hashable, lookup has one right idiom per intention, and a view is not a snapshot |
| [0005](lessons/0005-truthiness-none-and-equality.md) | Truthiness, None and Equality | Empty is falsy but not None, so the wrong default idiom rejects zero and the empty string |
| [0006](lessons/0006-functions-and-arguments.md) | Functions and Arguments | Defaults are evaluated once at definition, and a caller sees every mutation you make |
| [0007](lessons/0007-comprehensions.md) | Comprehensions | One expression that builds a container, with its own scope and a limit worth respecting |
| [0008](lessons/0008-the-iteration-protocol.md) | The Iteration Protocol | Why for works on anything, and why some of those things can only be looped over once |
| [0009](lessons/0009-generators.md) | Generators | A function that pauses, keeps its local state, and produces values only when asked |
| [0010](lessons/0010-exceptions.md) | Exceptions | Asking forgiveness instead of permission, and catching exactly what you can handle |
| [0011](lessons/0011-context-managers.md) | Context Managers | A block with a guaranteed exit, and how to write one in six lines |
| [0012](lessons/0012-dataclasses.md) | Dataclasses | Generated init, repr and equality, and choosing the right shape for a bundle of data |
| [0013](lessons/0013-modules-and-packages.md) | Modules and Packages | A module runs once, an import binds a name, and how the two produce every import error you have seen |
| [0014](lessons/0014-the-standard-library.md) | The Standard Library | The modules that delete code you were about to write, and the ones that prevent a dependency |

## Reference

- [Glossary](GLOSSARY.md): canonical terms for this topic
- [Resources](RESOURCES.md): trusted sources, each annotated with what it covers
- [Mutability and copying](reference/mutability-and-copying.md): which types mutate, what each copy idiom copies, and who can see it
- [Iteration and generators](reference/iteration-and-generators.md): what is consumed once, what survives a second pass, and which itertools tool fits
- [Exceptions and cleanup](reference/exceptions-and-cleanup.md): the hierarchy, what each clause guarantees, and which built-in to raise

## How this works

Each lesson is short and self-contained. Answer keys are collapsed: recall first, then open them. The real-world reps matter more than the reading, and spacing them out is the point. Anything still unclear at the end of a lesson is worth chasing to its primary source before moving on.
