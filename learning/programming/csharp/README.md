---
title: C#
description: "Own a C# service: the type system, async, and what the CLR does with what you wrote, from zero"
type: topic
---

# Learning: C#

Become the engineer trusted to own a C# service on a team: able to model a domain choosing correctly between a struct, a class and a record, write and reason about `async`/`await`, query and transform data fluently with LINQ, ship a typed, tested ASP.NET Core backend, and explain what the CLR does with the code you wrote.

**Latest lesson:** [1. Structs and Classes](lessons/0001-structs-and-classes.md)

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
- CLR internals past what explains value/reference semantics and `async` behaviour (deep garbage-collector tuning, JIT internals): touched at the level the arc needs, not as a full runtime-operations topic.

## The arc

Seven stages, zero to senior. Not a lesson list: a stage takes several lessons, and the boundaries are soft.

| Stage | Lessons | Covers | Done when |
|---|---|---|---|
| 1. Foundations | 0001 to 0006 | Value types vs reference types (struct vs class), nullable value types, basic types and string interpolation, collections (`List`, `Dictionary`, `IEnumerable`), control flow, exceptions | Can predict copy-vs-reference behaviour without running the code |
| 2. Modelling | 0007 to 0011 | Properties, `record` types, pattern matching and switch expressions, interfaces with default implementations, generics | Models a domain choosing the right type instead of a class for everything |
| 3. Idiom | 0012 to 0016 | Extension methods, LINQ query and method syntax, delegates and events, nullable reference types, expression-bodied members | Writes C# a reviewer would not describe as translated Java |
| 4. Async | 0017 to 0021 | The `Task` model, `async`/`await` mechanics, `Task` composition, cancellation tokens, `IAsyncEnumerable` | Can explain what `await` does to a method's execution and predict an async program's behaviour |
| 5. Testing and build | 0022 to 0024 | xUnit/NUnit, mocking, the `dotnet` CLI and project/package management | Someone else can clone, build, test and run it |
| 6. Shipping the service | 0025 to 0029 | ASP.NET Core routing and middleware, dependency injection, configuration, Entity Framework Core basics, structuring a typed, tested backend | Ships a typed, tested ASP.NET Core service |
| 7. Judgment | 0030 to 0031 | Comparing `async`/`await` to Java virtual threads and LINQ to the Stream API, reviewing C# for a habit that merely compiles | Trusted to make the call and explain it to someone else |

## Lessons

Work through these in order.

| # | Lesson | Teaches |
|---|---|---|
| [0001](lessons/0001-structs-and-classes.md) | Structs and Classes | The type-system choice Java never gave you, and what the CLR actually does with each |

## Reference

- [Glossary](GLOSSARY.md): canonical terms for this topic
- [Resources](RESOURCES.md): trusted sources

## How this works

Each lesson is short and self-contained. Answer keys are collapsed: recall first, then open them. The real-world reps matter more than the reading, and spacing them out is the point. Anything still unclear at the end of a lesson is worth chasing to its primary source before moving on.
