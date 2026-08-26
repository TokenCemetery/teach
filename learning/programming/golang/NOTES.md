# Go Notes

Working notes for the teaching session. Not linked from `README.md`.

## Preferences

- Mission is the full arc: zero to senior specialist. Curriculum spans everything; lesson placement is set by calibration, not by starting at stage 1 by default.
- Coming from Java 21 (professional) and TypeScript (heavy daily use). Use that as leverage — teach Go idiom as a contrast with what Java taught, since the wrong Java instinct compiles cleanly in Go.
- Reps must fit an evening.

## Curriculum arc

Six stages, zero to senior. Not a lesson list — one stage takes several lessons, and the boundaries are soft.

| Stage | Covers | Done when |
|---|---|---|
| 1. Foundations | Types, zero values, value vs pointer semantics, slice and map mechanics including aliasing, strings vs runes vs bytes, package basics | Can predict aliasing and copy behaviour without running the code |
| 2. Idiom | Errors as values, wrapping with `%w`, `errors.Is`/`As`, implicit interface satisfaction, small interfaces, struct embedding, package layout and naming | Writes Go that a reviewer would not describe as "Java in Go syntax" |
| 3. Concurrency | Goroutines, channels, `select`, `sync` primitives, `context` cancellation, `errgroup`, the race detector, the memory model, leak patterns | Can find a leak and a race in unfamiliar code and explain the guarantee that was violated |
| 4. Production | HTTP and gRPC services, config, `slog`, graceful shutdown, observability, database access, generics where they earn their keep | Has shipped a service that survives being operated |
| 5. Performance and tooling | Table-driven tests, fuzzing, benchmarks, `pprof`, escape analysis, allocation reduction, modules and versioning, release builds | Optimises from a profile and proves the win with `benchstat` |
| 6. Judgment | API design and compatibility, when *not* to use a goroutine, review, mentoring, reading stdlib source for answers | Trusted to make the call and to explain it to someone else |

## Calibration needed before lesson 0001

Stage 1 and parts of stage 2 may already be solid. Confirm with retrieval rather than by asking, then write a learning record for whatever is established so it is not re-taught. Cheapest probes:

- Slice aliasing after `append` — the answer separates "reads Go" from "writes Go".
- Whether a `nil` interface holding a `nil` pointer is `nil`.
- Value receiver mutating a struct field.

## Contrast notes worth spending time on

These are where Java and TypeScript habits actively mislead, so they deserve their own lessons rather than a footnote:

- Zero values are usable. Java trains you to expect `null` and to guard for it.
- Interfaces are satisfied implicitly and belong to the consumer. Java trains you to declare them up front, next to the implementation.
- Composition via embedding is not an inheritance workaround; there is no inheritance to work around.
- Goroutines vs Java 21 virtual threads — a genuinely illuminating comparison, and available here because Java 21 is already known. Keep it inside this workspace as a note; do not link across workspaces.
- `context` cancellation has no Java or Promise analogue that transfers cleanly.

## Open threads

- Which stage 4 target: HTTP or gRPC first? Depends on what gets shipped, and nothing has been chosen yet.
- No decision yet on whether reps land in a scratch repo or in an existing project.
