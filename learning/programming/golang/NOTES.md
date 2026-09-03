# Go Notes

Working notes for the teaching session. Not linked from `README.md`.

## Preferences

- Mission is the full arc: zero to senior specialist. Curriculum spans everything; lesson placement is set by calibration, not by starting at stage 1 by default.
- Coming from Java 21 (professional) and TypeScript (heavy daily use). Use that as leverage: teach Go idiom as a contrast with what Java taught, since the wrong Java instinct compiles cleanly in Go.
- Reps must fit an evening.

## Calibration needed before the first teaching session

The full arc is written, so the open question is not what to write but where to start. Stage 1 and parts of stage 2 may already be solid. Confirm with retrieval rather than by asking, then write a learning record for whatever is established so it is not re-taught. Cheapest probes:

- Slice aliasing after `append`. The answer separates "reads Go" from "writes Go".
- Whether a `nil` interface holding a `nil` pointer is `nil`.
- Value receiver mutating a struct field.

## Contrast notes worth spending time on

These are where Java and TypeScript habits actively mislead, so they deserve their own lessons rather than a footnote:

- Zero values are usable. Java trains you to expect `null` and to guard for it.
- Interfaces are satisfied implicitly and belong to the consumer. Java trains you to declare them up front, next to the implementation.
- Composition via embedding is not an inheritance workaround; there is no inheritance to work around.
- Goroutines vs Java 21 virtual threads, a genuinely illuminating comparison and available here because Java 21 is already known. Keep it inside this workspace as a note; there is no Java workspace to defer it to.
- `context` cancellation has no Java or Promise analogue that transfers cleanly.

## The arc is complete against its own promises, checked clause by clause

Asked, after every other workspace here was finished, whether this arc is done or merely thin. It is 37 lessons where the others are 44 to 63, which invites the assumption that something is missing. **Settled by checking each stage's done-when clause against the lessons that claim it, rather than by comparing lesson counts, and every clause is discharged by a lesson that demonstrates it rather than describing it.**

- **Stage 1, predicting aliasing and copy behaviour without running the code.** Lessons 0002 to 0004 own value semantics, the backing array and map rules, and their practice items ask for the prediction before the run.
- **Stage 2, writing Go a reviewer would not call Java in Go syntax.** Lessons 0011 to 0014, with 0013 arguing embedding against inheritance directly, which is where that habit actually arrives.
- **Stage 3, finding a leak and a race in unfamiliar code and naming the guarantee that was violated.** Lesson 0021's mission link states that it *is* the failure closing the stage, "finding a leak in code you did not write", and its first practice item is literally to find the leak in code the reader is handed. Lesson 0020 supplies the guarantee half, including a practice item on what a passing `-race` run has actually established, which is the honest answer to a question most writing gets wrong.
- **Stage 4, having shipped a service that survives being operated.** Lessons 0022 to 0026, and 0025's reps build the whole shutdown path, break it deliberately by passing the cancelled context to `Shutdown`, and watch the in-flight request get dropped. That is the clause discharged rather than asserted.
- **Stage 5, optimising from a profile and proving the win with `benchstat`.** Lesson 0030 names the clause as its own mission and its reps prove a win with `benchstat` after switching to `strings.Builder`, with 0031 and 0032 supplying the profile and the allocation half.
- **Stage 6, being trusted to make the call and explain it to someone else.** Lesson 0036 is the review vocabulary and order, and 0037 closes the arc on self-sufficiency, answering "how does this actually work" from the source when the documentation is ambiguous.

**So the thinness is lessons per promise, not a missing promise.** This arc declares six stages and discharges six; the Rust arc declared eight because its own notes record three separate hard walls to get through. A stage table with fewer lessons is not an unfinished arc, and the check that matters is whether a clause has a lesson behind it.

**One real over-promise was found and fixed rather than argued away.** Stage 6's covers column named "mentoring", and no lesson teaches it. The clause that column supports is discharged by 0036 and 0037, so the honest fix was to drop the word from the table rather than to write a lesson nobody needs or to leave a topic list promising something absent. A topic list that names what no lesson covers is the same defect as a reference sheet promising material a later stage never wrote.

**The two recorded gaps are deliberate, and only one of them is cleanly settled by the declared scope.** gRPC is squarely out: it is a third-party framework, the out-of-scope list excludes those as subjects, and stage 4 went HTTP-first on purpose. Observability past `slog` is the one where that defence does not hold, because `expvar` and `runtime/metrics` are both in the standard library, so it could be taught without adding a dependency. What settles it instead is that **no stage's done-when clause asks for it**: a service with structured logging, health checks, graceful shutdown and `net/http/pprof` can be operated, and stage 4's clause is about surviving operation rather than about being comfortable to operate. So it stays an optional extension, and `RESOURCES.md` now records that if anyone writes it, the standard library is the route and reaching for OpenTelemetry would need the out-of-scope list revisited first.

## Open threads

- Resolved: gRPC stays out, as a third-party framework the out-of-scope list already excludes, and no done-when clause needs it. See the section above.
- Resolved: observability past `slog` is an optional extension rather than a gap in a promise, because no done-when clause asks for it. If it is ever written it must be `expvar` and `runtime/metrics` rather than a third-party dependency. See the section above.
- No decision yet on whether reps land in a scratch repo or in an existing project.
- The Java 21 contrast is currently concentrated in lesson 0015 (goroutines versus virtual threads). If it needs more room, 0018 on `context` is the other place it would earn a section.
