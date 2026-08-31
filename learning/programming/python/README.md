---
title: Python
description: "Own Python in production: ship it typed, tested, packaged and profiled"
type: topic
---

# Learning: Python

Become the engineer trusted to own Python on a team: able to ship a typed, tested, packaged Python service or tool, take a traceback or a profile to its root cause instead of guessing, and say concretely why someone's clever use of Python's dynamism is going to hurt them.

**Latest lesson:** _none yet_

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
| _none yet_ | | |

## Reference

- [Glossary](GLOSSARY.md): canonical terms for this topic
- [Resources](RESOURCES.md): trusted sources, each annotated with what it covers

## How this works

Each lesson is short and self-contained. Answer keys are collapsed: recall first, then open them. The real-world reps matter more than the reading, and spacing them out is the point. Anything still unclear at the end of a lesson is worth chasing to its primary source before moving on.
