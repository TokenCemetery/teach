# Java Notes

Working notes for the teaching session. Not linked from `README.md`.

## Preferences

- **Lessons are written for a general reader, deliberately.** No machine, OS, editor or installed version appears in any lesson, reference sheet, `README.md` or `RESOURCES.md`. Requested explicitly; do not personalise the lesson material to whoever is running the session.
- Mission is the full arc: zero to senior specialist, assuming no prior Java. Start at stage 1 rather than calibrating against a particular reader.
- Reps must fit one sitting, with stage 6 excepted because profiling needs a program that runs long enough to profile.

## State

Stage 1 is written: lessons 0001 to 0006, plus the `reference/equality-hashing-and-ordering.md` sheet that lessons 2, 3 and 6 point at. Stages 2 to 7 are unwritten.

**How the glossary is populated here.** The skill's test, that a term lands once it can be used correctly, is a statement about a learner's demonstration. These lessons have no single learner, so the test is applied to the material: a term lands when a lesson has taught it well enough for a reader to use it. Stage 1 added seven terms alongside the three pinned ones. Keep doing this per stage, and do not add a term the lessons have not earned.

## Version policy

The baseline is the current long-term-support release, which was JDK 25 when this workspace was prepared. Two rules follow, and they matter more here than in most languages:

- Every language feature is introduced with the release it arrived in. Java is read across many versions, and a lesson that says "modern Java" without a number is useless in three years.
- Before a stage is written, check the JEP index and the release page in `RESOURCES.md` for what has changed. The six-month cadence means the arc will drift on its own.

Recheck which release is long-term-support when resuming this workspace after a gap. The support roadmap in `RESOURCES.md` is the source for that, not recall.

## On the arc

- Stage 2 is where the arc departs most from how Java is usually taught. Records, sealed types and pattern matching come before deep inheritance, deliberately: a reader who meets inheritance first models everything with it afterwards.
- Stage 4 is the hardest to keep honest. "Java Concurrency in Practice" is canonical for the model and predates virtual threads, so the API side has to come from current JEPs. Watch for teaching a 2006 idiom as current.
- Stage 6 needs a running program with a real workload. Decide what that program is before the stage starts, ideally the artifact stage 5 already shipped.

## Open threads

- No build tool chosen. The `README.md` puts tool comparison out of scope, so a tool still has to be picked to teach stage 5 with. Maven's guides are listed because they explain the lifecycle well; that is not the same as a decision.
- Garbage-collection tuning has no book-length source. Listed as a gap; may need one before stage 6.
- Frameworks are out of scope as subjects, but stage 7 has to judge them. That judgment needs a source and `RESOURCES.md` has none yet.
- Concurrency comparisons across workspaces are tempting here: virtual threads against goroutines, against `asyncio`. Keep them as pointers to the relevant glossary term in the other workspace rather than importing its material.
