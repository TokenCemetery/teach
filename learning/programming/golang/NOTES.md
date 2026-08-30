# Go Notes

Working notes for the teaching session. Not linked from `README.md`.

## Preferences

- Mission is the full arc: zero to senior specialist. Curriculum spans everything; lesson placement is set by calibration, not by starting at stage 1 by default.
- Coming from Java 21 (professional) and TypeScript (heavy daily use). Use that as leverage — teach Go idiom as a contrast with what Java taught, since the wrong Java instinct compiles cleanly in Go.
- Reps must fit an evening.

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
- Goroutines vs Java 21 virtual threads — a genuinely illuminating comparison, and available here because Java 21 is already known. Keep it inside this workspace as a note; there is no Java workspace to defer it to.
- `context` cancellation has no Java or Promise analogue that transfers cleanly.

## Open threads

- Which stage 4 target: HTTP or gRPC first? Depends on what gets shipped, and nothing has been chosen yet.
- No decision yet on whether reps land in a scratch repo or in an existing project.
