---
title: C#
description: "Own a C# service: the type system, async, and what the CLR does with what you wrote"
type: topic
---

# Learning: C#

Become the engineer trusted to own a C# service on a team, able to ship a typed, tested ASP.NET Core backend and explain what the CLR does with the code you wrote, rather than carrying Java habits into code that merely compiles.

**Latest lesson:** [1. Structs and Classes](lessons/0001-structs-and-classes.md)

## Success looks like

- Ship a typed, tested ASP.NET Core service, designed idiomatically for C# rather than as translated Java.
- Given C# written with a Java habit (a class where a struct belongs, a callback instead of `async`/`await`), name the habit and rewrite it idiomatically.
- Compare `async`/`await` against Java's virtual threads, and LINQ against the Stream API, and explain what each buys you and what it costs.

## Constraints

- Assumes professional Java background, the same leverage `programming/kotlin` uses; teaches the contrast rather than C# from zero.
- ASP.NET Core / backend service context; not general .NET without that focus.

## Out of scope

- Unity and game development with C#: a different enough context that it is not covered here.
- What the JVM does underneath: that is `programming/java`, referenced only for the contrast.

## The arc

{N} stages, {start} to {end}. Not a lesson list: a stage takes several lessons, and the boundaries are soft.

| Stage | Covers | Done when |
|---|---|---|
| 1. {Name} | {What it covers} | {The capability that closes the stage} |

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
