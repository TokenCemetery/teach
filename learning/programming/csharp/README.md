---
title: C#
description: "Own a C# service: the type system, async, and what the CLR does with what you wrote, from zero"
type: topic
---

# Learning: C\#

Become the engineer trusted to own a C# service on a team: able to model a domain choosing correctly between a struct, a class and a record, write and reason about `async`/`await`, query and transform data fluently with LINQ, ship a typed, tested ASP.NET Core backend, and explain what the CLR does with the code you wrote.

**Latest lesson:** [36. Struct vs Class, Measured](lessons/0036-struct-vs-class-measured.md)

## Success looks like

- Model a domain choosing correctly between a struct, a class and a record, and defend the choice from the CLR's actual behaviour.
- Write `async`/`await` code and explain what happens to a method's execution at each `await`.
- Query and transform data fluently with LINQ.
- Ship a typed, tested ASP.NET Core backend service, designed idiomatically for C#.
- Given C# written with a habit that merely compiles (a class where a struct belongs, a callback instead of `async`/`await`), name the habit and rewrite it idiomatically.

## Constraints

- Assumes no prior C#. Experience in another object-oriented language (Java, Kotlin) shortens the early stages but is not required, and it brings habits C# punishes quietly: a class where a struct or record belongs, a callback where `async`/`await` reads better.
- ASP.NET Core / backend service context; not general .NET without that focus.

## Out of scope

- Unity and game development with C#: a different enough context that it is not covered here.
- JIT internals, and writing or hand-tuning a garbage collector: stage 8 covers the generational heap, GC modes and profiling at the level a service owner needs to measure and defend a choice, not at the level of implementing one.

## The arc

Eight stages, zero to senior. Not a lesson list: a stage takes several lessons, and the boundaries are soft.

| Stage | Lessons | Covers | Done when |
|---|---|---|---|
| 1. Foundations | 0001 to 0006 | Value types vs reference types (struct vs class), nullable value types, basic types and string interpolation, collections (`List`, `Dictionary`, `IEnumerable`), control flow, exceptions | Can predict copy-vs-reference behaviour without running the code |
| 2. Modelling | 0007 to 0011 | Properties, `record` types, pattern matching and switch expressions, interfaces with default implementations, generics | Models a domain choosing the right type instead of a class for everything |
| 3. Idiom | 0012 to 0016 | Extension methods, LINQ query and method syntax, delegates and events, nullable reference types, expression-bodied members | Writes C# a reviewer would not describe as translated Java |
| 4. Async | 0017 to 0021 | The `Task` model, `async`/`await` mechanics, `Task` composition, cancellation tokens, `IAsyncEnumerable` | Can explain what `await` does to a method's execution and predict an async program's behaviour |
| 5. Testing and build | 0022 to 0024 | xUnit/NUnit, mocking, the `dotnet` CLI and project/package management | Someone else can clone, build, test and run it |
| 6. Shipping the service | 0025 to 0029 | ASP.NET Core routing and middleware, dependency injection, configuration, Entity Framework Core basics, structuring a typed, tested backend | Ships a typed, tested ASP.NET Core service |
| 7. Judgment | 0030 to 0031 | Comparing `async`/`await` to Java virtual threads and LINQ to the Stream API, reviewing C# for a habit that merely compiles | Trusted to make the call and explain it to someone else |
| 8. The CLR Runtime and Performance | 0032 to 0036 | The managed heap's generational design, GC modes, `Span<T>`/`Memory<T>`, `stackalloc`/`ArrayPool<T>`, measuring struct vs class with BenchmarkDotNet, and profiling | Optimises from a profile and defends the win with a trustworthy benchmark, tied back to the CLR's actual generational and allocation behaviour |

## Lessons

Work through these in order.

| # | Lesson | Teaches |
|---|---|---|
| [0001](lessons/0001-structs-and-classes.md) | Structs and Classes | The type-system choice Java never gave you, and what the CLR actually does with each |
| [0002](lessons/0002-nullable-value-types.md) | Nullable Value Types | Why int? is still a value type, the comparison rule that makes both directions false, and what boxing does to the wrapper |
| [0003](lessons/0003-basic-types-and-string-interpolation.md) | Basic Types and String Interpolation | Keywords as aliases for .NET types, why decimal is built in rather than a class, and the interpolation hole's width, format and side-effect rules |
| [0004](lessons/0004-collections.md) | Collections | IEnumerable as the abstraction the rest of the arc leans on, and the dictionary lookup that throws where Java's map returns null |
| [0005](lessons/0005-control-flow.md) | Control Flow | The three places control flow does not transfer from Java: foreach's duck-typed enumerator, switch without fall-through, and goto as a legal jump |
| [0006](lessons/0006-exceptions.md) | Exceptions | Exception filters and the stack trace that catch-and-rethrow destroys, using for deterministic cleanup, and the stage 1 capstone |
| [0007](lessons/0007-properties.md) | Properties | Accessors as a language feature, the three orthogonal promises of required, init and a non-nullable type, and computed properties with no backing field |
| [0008](lessons/0008-record-types.md) | Record Types | What the record modifier actually generates, why equality depends on the runtime type, and the shallow immutability a with expression does not fix |
| [0009](lessons/0009-pattern-matching.md) | Pattern Matching | The pattern vocabulary, the switch expression's exhaustiveness and its one silent gap, and why arm order is a compile-time question |
| [0010](lessons/0010-interfaces.md) | Interfaces | What an interface may hold now that it can carry implementations, the auto-property that is not one, and the member you can only call through the interface |
| [0011](lessons/0011-generics.md) | Generics | Constraints as the vocabulary for what a type parameter must be, variance as a rule about positions, and the stage 2 capstone of choosing the right type |
| [0012](lessons/0012-extension-methods.md) | Extension Methods | Two syntaxes compiling to the same IL, the binding rule that stops an extension overriding anything, and what that costs at a call site |
| [0013](lessons/0013-linq.md) | LINQ | One query language with two syntaxes and no semantic difference, why nothing runs until you iterate, and the expression tree that lets the same query reach a database |
| [0014](lessons/0014-delegates-and-events.md) | Delegates and Events | A delegate as a type whose signature includes its return type, the invocation list where one throwing handler stops the rest, and what the event keyword takes away from callers |
| [0015](lessons/0015-nullable-reference-types.md) | Nullable Reference Types | Annotations rather than types, the null-state the compiler tracks through your control flow, and the one library that turns your annotation into runtime behaviour |
| [0016](lessons/0016-expression-bodied-members.md) | Expression-Bodied Members | The second job of the arrow token, the statement-expression rule for void members, and the stage 3 capstone of rewriting translated Java |
| [0017](lessons/0017-the-task-model.md) | The Task Model | A task as an asynchronous operation rather than a thread, the four ways one comes into existence, and the AggregateException that can terminate a process you thought had finished |
| [0018](lessons/0018-async-and-await.md) | async and await | What await does to the enclosing method, the three places it is forbidden, and why async void breaks the only mechanism a caller has |
| [0019](lessons/0019-task-composition.md) | Task Composition | Starting work before awaiting it, the ToArray that makes a LINQ-built task list actually run, and the double await that WhenAny requires |
| [0020](lessons/0020-cancellation-tokens.md) | Cancellation Tokens | Cooperative cancellation with one requester and many listeners, why returning early reports success, and the token comparison that decides whether a task says it was canceled |
| [0021](lessons/0021-async-streams.md) | Async Streams | The three interfaces behind await foreach, the attribute that lets a consumer's token reach an async iterator's body, and the stage 4 capstone of predicting an async program |
| [0022](lessons/0022-xunit-and-nunit.md) | xUnit and NUnit | The per-test instance rule that leaves xUnit no setup attribute to need, the word theory meaning two different things, and the parallelism a shared fixture quietly costs |
| [0023](lessons/0023-mocking.md) | Mocking | The runtime proxy behind every substitution library, the C# default that decides what it is allowed to replace, and the mocked assertion that passes without the call ever happening |
| [0024](lessons/0024-the-dotnet-cli-and-packages.md) | The dotnet CLI and Packages | The one command a fresh clone needs, why a package version is a floor rather than a pin, the SDK release that reordered the commands, and the stage 5 capstone |
| [0025](lessons/0025-routing-and-middleware.md) | Routing and Middleware | Two systems sharing one Program.cs, one settled by the order you wrote and one by template precedence, and the two positions that decide what a middleware can know and whether it runs at all |
| [0026](lessons/0026-dependency-injection.md) | Dependency Injection | Three lifetimes as claims the container enforces only where it can see them, the long-lived service that silently promotes a short-lived one, and why nobody disposes what the container made |
| [0027](lessons/0027-configuration.md) | Configuration | One flat dictionary of strings where the last provider wins, three options interfaces separated by lifetime rather than by taste, and validation that waits for the first request unless you ask it not to |
| [0028](lessons/0028-entity-framework-core.md) | Entity Framework Core | A context that remembers what you queried so an assignment becomes an update, the single place a query is allowed to fall back to the client, and why stage 4's habit of overlapping work corrupts it |
| [0029](lessons/0029-structuring-a-typed-tested-backend.md) | Structuring a Typed, Tested Backend | The container as the seam a test replaces registrations through, the documented rule for choosing between a unit test and an integration test, and the stage 6 capstone of four defects that all compile |
| [0030](lessons/0030-two-comparisons-with-java.md) | Two Comparisons with Java | The same waiting problem solved at two different layers, why Java's answer removes the style C# requires rather than adopting it, and the expression tree that has no counterpart in a Stream |
| [0031](lessons/0031-reviewing-csharp.md) | Reviewing a C# Codebase | The difference between a style opinion and a cost you can name, a review pass ordered by what the compiler will never tell you, and the habits this arc has been collecting since lesson 1 |
| [0032](lessons/0032-the-managed-heap-and-generations.md) | The Managed Heap and Generations | Lesson 1 said a class instance lives on the managed heap; this lesson opens up what happens to it there, why the heap is split into three generations, and why most objects are meant to die in the youngest one without ever being promoted |
| [0033](lessons/0033-gc-modes-and-tradeoffs.md) | GC Modes and Trade-offs | Lesson 32 established the generational heap; this lesson covers how a collection actually runs against it, one dedicated thread or one per core, blocking every managed thread or letting most of them keep going, and the one moment even the non-blocking mode still has to stop everything |
| [0034](lessons/0034-span-and-memory.md) | Span and Memory | A zero-allocation view over existing memory that never enters lesson 32's generational system at all, the compiler restrictions that keep it safely stack-only, and the heap-safe counterpart built for exactly the one thing it cannot do: cross an await |
| [0035](lessons/0035-stackalloc-and-arraypool.md) | stackalloc and ArrayPool | Lesson 34 let a Span<T> view stackalloc'd memory; this lesson covers what stackalloc actually allocates, why pairing it with a ref struct is what makes it safe, its real risk (a stack overflow, not garbage collection), and ArrayPool<T> as the fallback for a buffer too large or too long-lived for the stack |
| [0036](lessons/0036-struct-vs-class-measured.md) | Struct vs Class, Measured | Lesson 1 argued that a struct can avoid a heap allocation a class of the same shape would require; this lesson is where that argument gets measured instead of reasoned about, and why the obvious way to measure it produces a number that means nothing at all |

## Reference

- [Glossary](GLOSSARY.md): canonical terms for this topic
- [Resources](RESOURCES.md): trusted sources

## How this works

Each lesson is short and self-contained. Answer keys are collapsed: recall first, then open them. The real-world reps matter more than the reading, and spacing them out is the point. Anything still unclear at the end of a lesson is worth chasing to its primary source before moving on.
