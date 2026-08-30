---
title: Go
description: "Own Go on a team: design, ship and operate a production service"
type: topic
---

# Learning: Go

Become the engineer trusted to own Go on a team — able to design, ship and operate a production Go service, review someone else's Go and name concretely why a design is wrong, and recognise when a design imported from another language is fighting Go rather than using it.

**Latest lesson:** _none yet_

## Success looks like

- Design and ship a production service: config, structured logging, graceful shutdown, health checks, database access.
- Debug a data race and a goroutine leak in code you did not write, using `-race` and `pprof`.
- Review a colleague's PR and say precisely why an interface, a pointer receiver, or a channel is the wrong tool there.
- Predict what a concurrent program does before running it, from the scheduler and memory model rather than from experiment.
- Cut allocations with evidence from `pprof` and `benchstat`, not guesswork.
- Design a package API you can keep backwards-compatible, and know when *not* to reach for a goroutine.

## Constraints

- Assumes no prior Go. Experience in another language shortens the early stages but is not required, and it brings habits that Go will punish quietly — wrong instincts here still compile.
- Needs only the standard toolchain on any supported OS. Nothing through stage 5 requires paid tooling, a cloud account, or a second machine.
- Reps are small programs that fit one sitting. Spacing them across days is the mechanism, not an inconvenience.
- Version-sensitive material dates fast. Claims about the current release are checked against release notes rather than against books.

## Out of scope

- Other languages as subjects in their own right. Comparisons appear only where they stop a habit from being carried into Go.
- Frontend, WASM, and mobile targets.
- Kubernetes and infrastructure beyond what one Go service needs to run.
- Compiler and runtime internals past the point where they stop predicting program behaviour.

## The arc

Six stages, zero to senior. Not a lesson list — a stage takes several lessons, and the boundaries are soft.

| Stage | Covers | Done when |
|---|---|---|
| 1. Foundations | Types, zero values, value vs pointer semantics, slice and map mechanics including aliasing, strings vs runes vs bytes, package basics | Can predict aliasing and copy behaviour without running the code |
| 2. Idiom | Errors as values, wrapping with `%w`, `errors.Is`/`As`, implicit interface satisfaction, small interfaces, struct embedding, package layout and naming | Writes Go that a reviewer would not describe as "Java in Go syntax" |
| 3. Concurrency | Goroutines, channels, `select`, `sync` primitives, `context` cancellation, `errgroup`, the race detector, the memory model, leak patterns | Can find a leak and a race in unfamiliar code and explain the guarantee that was violated |
| 4. Production | HTTP and gRPC services, config, `slog`, graceful shutdown, observability, database access, generics where they earn their keep | Has shipped a service that survives being operated |
| 5. Performance and tooling | Table-driven tests, fuzzing, benchmarks, `pprof`, escape analysis, allocation reduction, modules and versioning, release builds | Optimises from a profile and proves the win with `benchstat` |
| 6. Judgment | API design and compatibility, when *not* to use a goroutine, review, mentoring, reading stdlib source for answers | Trusted to make the call and to explain it to someone else |

## Lessons

Work through these in order.

| # | Lesson | Teaches |
|---|---|---|
| _none yet_ | | |

## Reference

- [Glossary](GLOSSARY.md) — canonical terms for this topic
- [Resources](RESOURCES.md) — trusted sources and communities

## How this works

Each lesson is short and self-contained. Answer keys are collapsed — recall first, then open them. The real-world reps matter more than the reading, and spacing them out is the point. Anything still unclear at the end of a lesson is worth chasing to its primary source before moving on.
