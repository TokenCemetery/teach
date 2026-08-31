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

**Blocking call**:
An operation that does not return control until it finishes, and does not release the thread while waiting. In a coroutine it stalls the whole **event loop**, adding its full duration to every other task in flight, and nothing raises or warns.
_Avoid_: slow call, synchronous, I/O, long-running

**Bound method**:
What attribute access on an instance returns for a method: a new object pairing the function with that instance, produced by the function's `__get__`. `Cls.method` gives the plain function instead, which is why the two are not interchangeable.
_Avoid_: method, function, callable, closure

**Branch coverage**:
Measurement of which **outcomes** of each conditional were executed, rather than which lines were. Statement coverage counts an `if` with no `else` as covered from one path, so the untested path stays invisible without it.
_Avoid_: coverage (unqualified), test coverage, code quality

**Class attribute**:
A name in the class's namespace rather than any instance's, so one object exists for every instance. Reading falls through to it; assigning through an instance creates a shadowing instance attribute and stops the sharing.
_Avoid_: static field, constant, default, instance variable

**Context manager**:
An object with `__enter__` and `__exit__`, used through `with`, whose exit runs on every path out of the block. `as` binds whatever `__enter__` returned, which is not always the manager itself.
_Avoid_: resource, wrapper, `try/finally` (which it replaces rather than names)

**Coroutine**:
What calling an `async def` function returns, running none of its body, and resumable at each `await` exactly as a **generator** is at each `yield`. It does nothing until an **event loop** drives it, and `await` on one means "suspend until it finishes" rather than "run it concurrently".
_Avoid_: async function, thread, future, promise

**Data descriptor**:
A class attribute defining both `__get__` and `__set__`, which makes it beat the instance dict on both read and write. A `property` is one, which is why assigning to a property runs its setter instead of creating an attribute.
_Avoid_: property, getter, accessor, field

**Dunder method**:
A method with a reserved double-underscore name that a language construct calls: `len(x)` calls `__len__`, `for` calls `__iter__`. Implement one when the type genuinely is that kind of thing, and note that several are derived from others when absent.
_Avoid_: magic method, operator overload, special case, hook

**EAFP**:
Easier to ask forgiveness than permission: attempt the operation and handle the exception, rather than testing first. Preferred in Python because a `try` that does not raise is nearly free, and because a check and the action it guards can disagree.
_Avoid_: exception-driven design, error handling, defensive programming

**Editable install**:
An installation that puts a project on the import path while continuing to read its source files in place, so edits take effect with no reinstall. It is what makes a project importable from any directory, rather than only from the one containing it.
_Avoid_: development install, symlink, `sys.path` entry

**Event loop**:
The single thread that drives every **coroutine** in an `asyncio` program, resuming whichever **task** is ready. Because there is one, any **blocking call** anywhere stops all of them, and because it switches only at `await`, those points are the only places a task can be interrupted.
_Avoid_: scheduler, thread pool, reactor, runtime

**Exception chaining**:
The link Python records between a caught exception and one raised while handling it. `raise New() from exc` states a direct cause; omitting `from` still chains, but reads as an accident.
_Avoid_: wrapping, nesting, rethrowing

**Falsy**:
A property of an object rather than of a comparison: `False`, `None`, any numeric zero, and any empty container all test false in a boolean context. Everything else tests true, including `"0"` and `[0]`.
_Avoid_: empty, null, blank, unset

**Fixture**:
Setup a test requests by naming it as a parameter, with anything after its `yield` guaranteed to run as teardown. Its **scope** decides how often it is rebuilt, and a scope wider than one test is safe only if nothing mutates the value.
_Avoid_: setup, mock, helper, global

**Flaky test**:
A test whose result varies without a code change, which is worse than no test because it trains everyone to re-run rather than read. The causes are shared state, order dependence, real time, unordered data, or a genuine race in the code.
_Avoid_: intermittent failure, environment issue, false positive

**Generator**:
The **iterator** a function containing `yield` returns when called, holding a frozen frame that resumes where it left off. The function may be called repeatedly; each generator it produces is consumed once.
_Avoid_: coroutine, lazy list, stream, iterable (which is wider)

**Global interpreter lock**:
The mutex allowing one thread at a time to execute bytecode, held to protect the interpreter's own state and **released around waiting**. It therefore prevents CPU-bound threads from scaling and does nothing for your invariants, and a free-threaded build removes it without changing what code has to be correct.
_Avoid_: thread lock, mutex (unqualified), thread safety, bottleneck

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

**Metaclass**:
The type of a class, which is `type` unless replaced, and which therefore controls class creation. Required only for a non-dict class-body namespace, custom `isinstance` behaviour, customising the class object itself, or reaching a hierarchy whose base has no hook; two bases with different ones cannot be combined.
_Avoid_: base class, decorator, factory, abstract class

**Method resolution order**:
The flat, computed sequence of classes that attribute lookup walks, available as `Cls.__mro__`. `super()` means the next class after the current one **in this sequence**, which is not necessarily a base of the class the code was written in.
_Avoid_: inheritance chain, class hierarchy, parent order

**Mixin**:
A class that adds one piece of behaviour and is never instantiated alone, placed before the base class so it precedes it in the **method resolution order**. Any attribute it expects the host class to provide is a hidden dependency, and belongs in an annotation plus a class-creation check.
_Avoid_: interface, trait, helper, abstract class

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

**Parametrisation**:
Running one test body over several argument sets, each collected as a **separate** test with its own name. That separation is the point: a failure names the case, the remaining cases still run, and one case can be re-run alone.
_Avoid_: loop, data-driven test, test case, fuzzing

**Property-based test**:
A test that states an invariant over generated inputs rather than an expected output for one input, and reports the smallest failing input it can find. It complements examples rather than replacing them, since a property says what holds and an example says what the code is for.
_Avoid_: fuzzing, random testing, generative test

**Race condition**:
A defect where the result depends on when execution switches between concurrent workers, which for Python means at any bytecode boundary between threads or at any `await` between tasks. Whether it is ever observed is an implementation detail, so it is found by reading for invariants that span statements rather than by reproducing it.
_Avoid_: flaky behaviour, timing issue, deadlock, thread bug

**Rebinding**:
Pointing an existing **name** at a different object, which is what every assignment does. It is invisible to every other name, and it is the operation people mistake for mutation.
_Avoid_: reassignment, overwriting, updating

**Regression test**:
A test written for a defect that has already occurred, and the only kind whose ability to detect something is proven: it fails before the fix and passes after. Write it first, and watch it fail.
_Avoid_: unit test, bug ticket, smoke test

**Shallow copy**:
A new container holding the same objects as the original, which is what `[:]`, `list()`, `dict()` and `copy.copy` all produce. The container is independent and its contents are not.
_Avoid_: copy (unqualified), clone, snapshot

**Structural typing**:
Conformance decided by an object's shape rather than by what it inherits, which is what `Protocol` expresses to a checker. It works on classes you do not own, and `isinstance` against a runtime-checkable protocol verifies attribute names only.
_Avoid_: duck typing, interface, subclassing

**Subinterpreter**:
A separate interpreter inside one process, with its own module state and its own **global interpreter lock**, so several run bytecode in parallel. Module-level globals are not shared with the parent or with each other, and support depends on every C extension in use.
_Avoid_: thread, process, sandbox, virtual environment

**Task**:
A **coroutine** scheduled on the **event loop**, which is what creates concurrency; `await` on a bare coroutine does not. A task holds its exception until someone reads its result, and one that nothing references can be collected mid-flight.
_Avoid_: thread, coroutine, job, future

**Test double**:
Any stand-in for a real collaborator: a dummy, stub, fake, spy, or mock. A **fake** is a working simplified implementation and lets tests assert on outcomes; a **mock** records calls and couples the test to how the code is written.
_Avoid_: mock (as the general term), stub, dependency, patch

**Virtual environment**:
A directory holding its own `site-packages` and interpreter links, so one project's dependencies cannot displace another's. Activating it only changes `PATH`; running its interpreter by path is equivalent.
_Avoid_: container, sandbox, installation, environment (unqualified)

**Wheel**:
The built distribution that installs by unpacking, with no build step and no code from the package executed. Its filename records the interpreter, ABI and platform it supports, and `py3-none-any` means pure Python everywhere.
_Avoid_: package, archive, binary, egg
