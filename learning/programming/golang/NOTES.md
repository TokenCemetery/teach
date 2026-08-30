# Go Notes

Working notes for the teaching session. Not linked from `README.md`.

## Preferences

- Mission is the full arc: zero to senior specialist. Curriculum spans everything; lesson placement is set by calibration, not by starting at stage 1 by default.
- Coming from Java 21 (professional) and TypeScript (heavy daily use). Use that as leverage — teach Go idiom as a contrast with what Java taught, since the wrong Java instinct compiles cleanly in Go.
- Reps must fit an evening.
- **Links go to sources of information, not to places to ask.** Stated 2026-08-30. Documentation, books, articles and style guides qualify; chats, forums and subreddits do not, however well moderated. The `## Wisdom (Communities)` section was deleted from `RESOURCES.md` and the community link removed from lesson 0036. Do not propose a community again — this overrides the Wisdom section of `SKILL.md`, which anticipates exactly this preference and says to record it here.

## Calibration needed before the first teaching session

The full arc is written, so the open question is not what to write but where to start. Stage 1 and parts of stage 2 may already be solid. Confirm with retrieval rather than by asking, then write a learning record for whatever is established so it is not re-taught. Cheapest probes:

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

- Stage 4 went HTTP-first (lessons 0022–0027); gRPC has no lesson and no source. Revisit only if what gets shipped needs it — the arc and `RESOURCES.md` both say so now.
- Observability past `slog` — metrics and tracing — is unwritten and listed as a gap. It is the most likely place the arc grows.
- No decision yet on whether reps land in a scratch repo or in an existing project.
- The Java 21 contrast is currently concentrated in lesson 0015 (goroutines versus virtual threads). If it needs more room, 0018 on `context` is the other place it would earn a section.
