# Kotlin Notes

Working notes for the teaching session. Not linked from `README.md`.

## Preferences

- **This is a standalone zero-to-senior course, not a delta over Java. Requested explicitly, and do not reintroduce the prerequisite.** The workspace was first written as one of only two in the repository framed as "assumes professional Java background", and that framing was removed on instruction (see #42). The Java contrast survives only where it clarifies a Kotlin idiom, and JVM internals link to `programming/java`'s runtime stage instead of being assumed. The arc still runs the contrast through almost every lesson, so this is the note most at risk of being quietly undone.
- Interview recorded in #42. The outcome was never narrowed: both backend/server-side and Android, and coroutines against Java 21 virtual threads confirmed as a lesson of its own rather than a passing mention.
- Scope questions came back pulled in rather than cut. Where a later session is tempted to drop Android or the virtual-threads comparison to shorten the arc, that narrowing was declined once already.

## On the arc

The eight stages are public, in `README.md`. What belongs here is the caveat on them: all 35 lessons were written upfront across successive runs, not one per interactive session, and `learning-records/` is empty. So nothing in this workspace has been calibrated against a demonstrated answer, and every practice item's difficulty is guessed. Expect to revise individual lessons, particularly practice difficulty, once real answers come back.

## Open threads

- Nothing has been attempted yet. The first interactive session should calibrate before teaching forward: take a practice item from an early foundations lesson and check whether the level is right, rather than assuming the written arc landed.
- Stage 7's done-when is "has shipped a typed, tested Kotlin backend service or Android component", which no answer key can verify. Lesson 0033 stands in for it with a judgment question. Whether that substitute is enough is still open, and only a real project would settle it.
