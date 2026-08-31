---
title: Resources
description: Trusted sources for Python, each annotated with what it covers
type: resources
---

# Python Resources

## Knowledge

- [Docs: "The Python Tutorial", Python Software Foundation, docs.python.org](https://docs.python.org/3/tutorial/)
  The official guided introduction, written by the people who maintain the language. Use for: stage 1, and for the first honest answer on any built-in type.

- [Docs: "The Python Language Reference", Python Software Foundation, docs.python.org](https://docs.python.org/3/reference/index.html)
  Precise statement of syntax and semantics, including scoping and name binding. Use for: settling what the language guarantees rather than what usually happens.

- [Docs: "Data Model", Python Software Foundation, docs.python.org](https://docs.python.org/3/reference/datamodel.html)
  Every special method, attribute lookup, and the object protocol in one chapter. Use for: stage 4, and for deciding which dunder a type actually needs.

- [Docs: "The Python Standard Library", Python Software Foundation, docs.python.org](https://docs.python.org/3/library/index.html)
  What ships with the interpreter, which is more than most code assumes. Use for: checking whether a dependency is needed at all.

- [Docs: "Descriptor HowTo Guide", Raymond Hettinger, docs.python.org](https://docs.python.org/3/howto/descriptor.html)
  Builds properties, methods and `classmethod` up from the descriptor protocol. Use for: understanding attribute access instead of memorising it.

- [Docs: "asyncio", Python Software Foundation, docs.python.org](https://docs.python.org/3/library/asyncio.html)
  Event loop, tasks, cancellation and the high-level API, with the low-level parts marked as such. Use for: stage 6, and for what blocks an event loop.

- [Docs: "Glossary", Python Software Foundation, docs.python.org](https://docs.python.org/3/glossary.html)
  Short canonical definitions for iterable, iterator, generator, descriptor and the rest. Use for: pinning a term before a lesson leans on it.

- [Docs: "Static Typing with Python", Python Typing Community, typing.readthedocs.io](https://typing.readthedocs.io/en/latest/)
  The specification and the practical guides for the type system, maintained alongside it. Use for: stage 3, and for what a checker is entitled to infer.

- [Docs: "typing", Python Software Foundation, docs.python.org](https://docs.python.org/3/library/typing.html)
  The runtime module behind the annotations, and which spellings are current. Use for: checking whether a construct is deprecated before writing it.

- [Docs: "Python Packaging User Guide", Python Packaging Authority, packaging.python.org](https://packaging.python.org/en/latest/)
  Project metadata, building, publishing and dependency specification, kept current as the standards change. Use for: anything about `pyproject.toml` or a wheel.

- [Docs: "pytest", pytest developers, docs.pytest.org](https://docs.pytest.org/en/stable/)
  Fixtures, parametrisation, marks and the assertion rewriting that makes failures readable. Use for: stage 5 mechanics.

- [Docs: "Hypothesis", Hypothesis contributors, hypothesis.readthedocs.io](https://hypothesis.readthedocs.io/en/latest/)
  Property-based testing: the strategies, shrinking, and the settings that control the search. Use for: stage 5, and for turning an invariant into a test.

- [Docs: "Coverage.py", Ned Batchelder, coverage.readthedocs.io](https://coverage.readthedocs.io/en/latest/)
  What is measured, how branch coverage differs from statement coverage, and every configuration option. Use for: making the number mean something.

- [Docs: "mypy", mypy contributors, mypy.readthedocs.io](https://mypy.readthedocs.io/en/stable/)
  What each strictness flag turns on, and how inference actually proceeds. Use for: making a checker useful rather than noisy.

- [Docs: "pyright", Microsoft, microsoft.github.io](https://microsoft.github.io/pyright/)
  The other checker, stricter about `None` by default and the one most editors run. Use for: a second opinion when mypy accepts something that looks wrong.

- [Docs: "pydantic", Pydantic Services, docs.pydantic.dev](https://docs.pydantic.dev/latest/)
  Runtime validation generated from the same annotations, with the coercion rules stated explicitly. Use for: a boundary where data arrives untrusted and hand-written checks have outgrown a function.

- [Docs: "Ruff", Astral, docs.astral.sh](https://docs.astral.sh/ruff/)
  Every lint rule with its rationale, which doubles as a catalogue of common Python mistakes. Use for: settling a style question with a rule number.

- [Docs: "uv", Astral, docs.astral.sh](https://docs.astral.sh/uv/)
  Environment, dependency and interpreter management in one tool. Use for: reproducing an environment on another machine.

- [PEP: "PEP 8, Style Guide for Python Code", Guido van Rossum, Barry Warsaw, Alyssa Coghlan](https://peps.python.org/pep-0008/)
  The conventions Python reviewers cite, including the parts about when to break them. Use for: naming and layout arguments.

- [PEP: "PEP 484, Type Hints", Guido van Rossum, Jukka Lehtosalo, Łukasz Langa](https://peps.python.org/pep-0484/)
  The design rationale for gradual typing, and why annotations do not affect runtime behaviour. Use for: understanding what the type system is for.

- [PEP: "PEP 703, Making the Global Interpreter Lock Optional in CPython", Sam Gross](https://peps.python.org/pep-0703/)
  States precisely what the GIL protects and what removing it costs. Use for: stage 6, and for correcting folklore about threads in Python.

- [Docs: "What's New in Python", Python Software Foundation, docs.python.org](https://docs.python.org/3/whatsnew/index.html)
  Per-release changes, deprecations and removals. Use for: checking any version-sensitive claim before teaching it.

- [Docs: "Status of Python Versions", Python core developers, devguide.python.org](https://devguide.python.org/versions/)
  Which releases are supported, and until when. Use for: choosing the version a lesson should assume.

- [Book: "Fluent Python", Luciano Ramalho, O'Reilly](https://www.fluentpython.com/)
  The data model treated as the organising idea of the language, with the idiom that follows from it. Use for: stages 2 and 4 when a mental model is missing rather than a fact.

- [Blog: Hynek Schlawack, hynek.me](https://hynek.me/articles/)
  Careful posts on packaging, environments, `attrs` and production Python by a maintainer of several of those tools. Use for: decisions the packaging guide states but does not argue.

## Wisdom (Communities)

- [Forum: "Python Discourse", Python Software Foundation, discuss.python.org](https://discuss.python.org/)
  The archive where PEPs are debated and typing and packaging decisions are argued out in public, readable without an account. Use for: why a feature landed in the shape it did, when no document explains it.

## Gaps

- Packaging and typing tooling moves faster than anything else here. `uv` and Ruff are current choices rather than settled standards, so a lesson naming a tool says what it is standing in for.
- Free-threaded CPython is in progress, so any claim about the GIL states the version and the build it applies to.
- No source is chosen for CPython internals in depth. The mission caps that deliberately at the point where internals stop predicting behaviour.
- The two checkers disagree at the edges, and no source arbitrates. Stage 3 names mypy as the reference implementation and pyright as the editor default; where they differ, the specification at `typing.readthedocs.io` is the tiebreak.
- No book covers the type system at depth. `typing.readthedocs.io` is the closest thing, and it is a specification rather than a course.
