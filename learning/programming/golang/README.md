---
title: Go
description: "Own Go on a team: design, ship and operate a production service"
type: topic
---

# Learning: Go

Become the engineer trusted to own Go on a team: able to design, ship and operate a production Go service, review someone else's Go and name concretely why a design is wrong, and recognise when a design imported from another language is fighting Go rather than using it.

**Latest lesson:** [0037. Reading the Standard Library](lessons/0037-reading-the-standard-library.md)

## Success looks like

- Design and ship a production service: config, structured logging, graceful shutdown, health checks, database access.
- Debug a data race and a goroutine leak in code you did not write, using `-race` and `pprof`.
- Review a colleague's PR and say precisely why an interface, a pointer receiver, or a channel is the wrong tool there.
- Predict what a concurrent program does before running it, from the scheduler and memory model rather than from experiment.
- Cut allocations with evidence from `pprof` and `benchstat`, not guesswork.
- Design a package API you can keep backwards-compatible, and know when *not* to reach for a goroutine.

## Constraints

- Assumes no prior Go. Experience in another language shortens the early stages but is not required, and it brings habits that Go will punish quietly, because a wrong instinct here still compiles.
- Needs only the standard toolchain on any supported OS. Nothing through stage 5 requires paid tooling, a cloud account, or a second machine.
- Reps are small programs that fit one sitting. Spacing them across days is the mechanism, not an inconvenience.
- Version-sensitive material dates fast. Claims about the current release are checked against release notes rather than against books.

## Out of scope

- Other languages as subjects in their own right. Comparisons appear only where they stop a habit from being carried into Go.
- Third-party frameworks as subjects in their own right: routers, ORMs, dependency-injection containers, CLI toolkits. The standard library covers routing, structured logging and database access directly, so lessons build on it; where a team has already chosen a framework, judging whether it earns its place is a review skill and belongs in stage 6.
- Frontend, WASM, and mobile targets.
- Kubernetes and infrastructure beyond what one Go service needs to run.
- Compiler and runtime internals past the point where they stop predicting program behaviour.

## The arc

Six stages, zero to senior. Not a lesson list: a stage takes several lessons, and the boundaries are soft.

| Stage | Covers | Done when |
|---|---|---|
| 1. Foundations | Types, zero values, value vs pointer semantics, slice and map mechanics including aliasing, strings vs runes vs bytes, package basics | Can predict aliasing and copy behaviour without running the code |
| 2. Idiom | Errors as values, wrapping with `%w`, `errors.Is`/`As`, implicit interface satisfaction, small interfaces, struct embedding, package layout and naming | Writes Go that a reviewer would not describe as "Java in Go syntax" |
| 3. Concurrency | Goroutines, channels, `select`, `sync` primitives, `context` cancellation, `errgroup`, the race detector, the memory model, leak patterns | Can find a leak and a race in unfamiliar code and explain the guarantee that was violated |
| 4. Production | HTTP services, config, `slog`, graceful shutdown, health checks, database access, generics where they earn their keep | Has shipped a service that survives being operated |
| 5. Performance and tooling | Table-driven tests, fuzzing, benchmarks, `pprof`, escape analysis, allocation reduction, modules and versioning, release builds | Optimises from a profile and proves the win with `benchstat` |
| 6. Judgment | API design and compatibility, when *not* to use a goroutine, review, mentoring, reading stdlib source for answers | Trusted to make the call and to explain it to someone else |

## Lessons

Work through these in order.

| # | Lesson | Teaches |
|---|---|---|
| [0001](lessons/0001-values-and-the-zero-value.md) | Values and the Zero Value | Every declared variable is already usable, and nil is a value rather than an absence |
| [0002](lessons/0002-value-semantics-and-pointers.md) | Value Semantics and Pointers | Every assignment and every argument is a copy, and a pointer is how you opt out |
| [0003](lessons/0003-slices-and-the-backing-array.md) | Slices and the Backing Array | A slice is a three-word header over an array someone else may also be holding |
| [0004](lessons/0004-maps-and-their-rules.md) | Maps and Their Rules | Comma-ok, unaddressable elements, randomised iteration, and the fatal error a shared map throws |
| [0005](lessons/0005-strings-bytes-and-runes.md) | Strings, Bytes and Runes | A string is immutable UTF-8 bytes, so len is not a character count and indexing is not a character |
| [0006](lessons/0006-methods-and-method-sets.md) | Methods and Method Sets | Which receiver you pick decides which types satisfy an interface, not just who can mutate |
| [0007](lessons/0007-packages-and-modules.md) | Packages and Modules | A directory is a package, a capital letter is the whole visibility system, and internal is enforced |
| [0008](lessons/0008-errors-are-values.md) | Errors Are Values | error is an ordinary interface, so failures are data you handle rather than control flow that escapes |
| [0009](lessons/0009-wrapping-is-and-as.md) | Wrapping, Is and As | %w builds a chain, Is and As search it, and wrapping is an API commitment |
| [0010](lessons/0010-defer-panic-and-recover.md) | defer, panic and recover | Arguments freeze at the defer statement, and panic is for bugs rather than for failures |
| [0011](lessons/0011-implicit-interfaces.md) | Interfaces Are Satisfied Implicitly | The consumer declares the interface, the implementation never mentions it, and small is the point |
| [0012](lessons/0012-the-nil-interface-trap.md) | The Nil Interface Trap | An interface holds a type and a value, so a nil pointer inside it is not a nil interface |
| [0013](lessons/0013-embedding-is-not-inheritance.md) | Embedding Is Not Inheritance | Promotion looks like subclassing until an embedded method refuses to call your override |
| [0014](lessons/0014-designing-a-package.md) | Designing a Package | Doc comments, a small exported surface, and a dependency arrow that points one way |
| [0015](lessons/0015-goroutines-and-what-they-cost.md) | Goroutines and What They Cost | Cheap enough to start thousands, never free enough to start without a plan to stop |
| [0016](lessons/0016-channels.md) | Channels | Unbuffered means rendezvous, closing is a broadcast, and only the sender may close |
| [0017](lessons/0017-select-and-timeouts.md) | select and Timeouts | Waiting on several channels at once, choosing randomly among the ready, and disabling a case with nil |
| [0018](lessons/0018-context-cancellation.md) | context and Cancellation | One value that carries a deadline and a stop signal down every call it touches |
| [0019](lessons/0019-sync-primitives.md) | sync and errgroup | When sharing memory beats passing it, and the four primitives that cover almost everything |
| [0020](lessons/0020-memory-model-and-races.md) | The Memory Model and Races | A data race is undefined behaviour, not a coin flip, and the detector only sees what runs |
| [0021](lessons/0021-goroutine-leaks.md) | Goroutine Leaks | A goroutine blocked forever is never collected, and neither is anything it holds |
| [0022](lessons/0022-an-http-server.md) | An HTTP Server Worth Operating | Handlers, routing patterns and the four timeouts the default server does not set |
| [0023](lessons/0023-configuration-and-startup.md) | Configuration and Startup | A main that only wires, a run function that returns an error, and validation before the first request |
| [0024](lessons/0024-structured-logging-with-slog.md) | Structured Logging with slog | Key-value attributes, one logger passed as a dependency, and levels you can change without a deploy |
| [0025](lessons/0025-graceful-shutdown.md) | Graceful Shutdown and Health | Catch the signal, stop accepting, drain in-flight work, then close dependencies in order |
| [0026](lessons/0026-talking-to-a-database.md) | Talking to a Database | sql.DB is a pool, every call takes a context, and an unclosed Rows holds a connection |
| [0027](lessons/0027-generics-that-earn-their-keep.md) | Generics That Earn Their Keep | Type parameters remove duplication across types, and an interface is still the right answer for behaviour |
| [0028](lessons/0028-table-driven-tests.md) | Table-Driven Tests | One test function, a slice of cases, subtests that name themselves and fail independently |
| [0029](lessons/0029-fuzzing.md) | Fuzzing | State a property that must always hold, then let the toolchain search for the input that breaks it |
| [0030](lessons/0030-benchmarks-you-can-trust.md) | Benchmarks You Can Trust | b.Loop, repeated runs and benchstat, because one number from one run is not a measurement |
| [0031](lessons/0031-reading-a-pprof-profile.md) | Reading a pprof Profile | Find where the time and the memory actually go, before changing a single line |
| [0032](lessons/0032-escape-analysis-and-allocation.md) | Escape Analysis and Allocation | Why a value lands on the heap, how to ask the compiler, and which fixes actually pay |
| [0033](lessons/0033-modules-and-release-builds.md) | Modules and Release Builds | Minimal version selection, the v2 path rule, and the flags that make a binary reproducible |
| [0034](lessons/0034-api-design-and-compatibility.md) | API Design and Compatibility | What you can add without breaking callers, and the three changes that always do |
| [0035](lessons/0035-when-not-to-use-a-goroutine.md) | When Not to Use a Goroutine | Concurrency is a structure, not a speedup, and the sequential version is often the right answer |
| [0036](lessons/0036-reviewing-go.md) | Reviewing Go | Let the tools find style, spend your attention on lifecycle, boundaries and what the compiler cannot check |
| [0037](lessons/0037-reading-the-standard-library.md) | Reading the Standard Library | The source is on your machine, it settles arguments the docs cannot, and it is the style reference |

## Reference

- [Glossary](GLOSSARY.md): canonical terms for this topic
- [Resources](RESOURCES.md): trusted sources, each annotated with what it covers
- [Slices and Maps](reference/slice-and-map-mechanics.md): aliasing, capacity, and the operations that panic
- [Error Handling](reference/error-handling.md): wrapping verbs, matching functions, and the traps that compile
- [Concurrency Patterns](reference/concurrency-patterns.md): channel rules, context constructors, leak checklist
- [Toolchain Commands](reference/toolchain-commands.md): test, benchmark, profile and release-build flags
- [Review Checklist](reference/review-checklist.md): what the tools catch and what you must

## How this works

Each lesson is short and self-contained. Answer keys are collapsed: recall first, then open them. The real-world reps matter more than the reading, and spacing them out is the point. Anything still unclear at the end of a lesson is worth chasing to its primary source before moving on.
