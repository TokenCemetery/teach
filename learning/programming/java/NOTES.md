# Java Notes

Working notes for the teaching session. Not linked from `README.md`.

## Preferences

- **Lessons are written for a general reader, deliberately.** No machine, OS, editor or installed version appears in any lesson, reference sheet, `README.md` or `RESOURCES.md`. Requested explicitly; do not personalise the lesson material to whoever is running the session.
- Mission is the full arc: zero to senior specialist, assuming no prior Java. Start at stage 1 rather than calibrating against a particular reader.
- Reps must fit one sitting, with stage 6 excepted because profiling needs a program that runs long enough to profile.

## State

Stages 1 and 2 are written: lessons 0001 to 0014, plus the `reference/equality-hashing-and-ordering.md` and `reference/modelling.md` sheets. Stages 3 to 7 are unwritten.

Stage 2 is eight lessons rather than the six or seven the other stages will need, because the modelling surface is genuinely wider here: a class, a record, an interface, an abstract class, a sealed hierarchy and an enum are six ways to say almost the same thing, and the stage's whole job is telling them apart. The order is the load-bearing part. Interfaces (0009) come before inheritance (0010) so that a reader meets the contract before the mechanism, and sealed types (0011) come after both because sealing is a restriction on inheritance that only makes sense once inheritance has been priced. If the stage is ever reordered, that run is what must survive.

Lesson 0010 is the one to protect. It is the only place in the arc that argues against a language feature at length, and it does that with measured evidence rather than taste: construction order producing a `null` field, static and field hiding resolving on the declared type, and the counting-set failure with real numbers before and after the fix.

**Onboarding is handled inside lesson 0007**, in a short "Running these examples" subsection, rather than by inserting a new lesson at the front. Stage 1 shipped without ever showing how to compile and run, which is a real gap for a workspace whose constraints say "assumes no prior Java", and 0007 is the first lesson where the reader declares a class of their own, so it is the honest place for it. Renumbering stage 1 to put it first would have broken every existing cross-reference for no pedagogical gain. If stage 3 shows a gap of the same kind, solve it the same way.

**How the glossary is populated here.** The skill's test, that a term lands once it can be used correctly, is a statement about a learner's demonstration. These lessons have no single learner, so the test is applied to the material: a term lands when a lesson has taught it well enough for a reader to use it. Stage 1 added seven terms alongside the three pinned ones, and stage 2 added thirteen. Keep doing this per stage, and do not add a term the lessons have not earned. Two of stage 2's entries are deliberately a pair: "Invariance (of generics)" is written to be read against the existing "Covariance (of arrays)", since the two rules are opposites and the contrast is the lesson.

## What execution changed

Every behavioural claim in stage 2 was run rather than recalled, on the release the workspace names. Four things came out differently from what recall would have produced, and all four changed lesson content.

- **`this(...)` and `super(...)` no longer have to be the first statement.** JEP 513, Flexible Constructor Bodies, was finalised in Java 25: statements that do not touch the instance may run before the call, which is how an argument gets validated or computed before the superclass sees it. The old rule is stated in every book and was nearly written into two lessons. Verified by running a constructor with a validating prologue.
- **The classic counting-set bug does not reproduce in its usual form.** Overriding only `add` on a `HashSet` subclass gives the correct count, because `AbstractCollection.addAll` calls the overridable `add` and increments nothing itself. The double count needs both methods overridden and both incrementing. Building it on `ArrayList` never reproduces at all, since its `addAll` is a bulk copy. Lesson 0010 uses the version that actually fails.
- **Adding an enum constant without recompiling a switch throws `MatchException`**, not the `IncompatibleClassChangeError` usually named. Reproduced by split compilation, and stated as observed.
- **`List.copyOf` does not simply skip the copy for an already-unmodifiable list.** It returns the same instance for a list its own factories produced, and a new one for a `Collections.unmodifiableList` view, because the view is an implementation it cannot recognise as safe. Lesson 0014 states that distinction rather than the flat claim.

A fifth detail worth keeping: `this.field = ...` inside a compact constructor is a compile error, not a redundancy, which lesson 0008 turns into a practice item.

## Version policy

The baseline is the current long-term-support release, which was JDK 25 when this workspace was prepared. Two rules follow, and they matter more here than in most languages:

- Every language feature is introduced with the release it arrived in. Java is read across many versions, and a lesson that says "modern Java" without a number is useless in three years.
- Before a stage is written, check the JEP index and the release page in `RESOURCES.md` for what has changed. The six-month cadence means the arc will drift on its own.

Recheck which release is long-term-support when resuming this workspace after a gap. The support roadmap in `RESOURCES.md` is the source for that, not recall.

Rechecked against that roadmap before stage 2 was written: 8, 11, 17, 21 and 25 are the long-term-support releases, and the next is 29, planned for September 2027. JDK 25 is therefore still the right baseline and no link needs moving. Recheck again before stage 5, since the build and testing material is the part most likely to have drifted.

## On the arc

- Resolved: stage 2 did depart from how Java is usually taught, and the departure held. Records (0008) and interfaces (0009) come before `extends` (0010), and by the time inheritance arrives the reader has already modelled two domains without it, so lesson 0010 can price it rather than sell it. Sealed types then land as a restriction on something already understood. Keep this order.
- Stage 4 is the hardest to keep honest. "Java Concurrency in Practice" is canonical for the model and predates virtual threads, so the API side has to come from current JEPs. Watch for teaching a 2006 idiom as current.
- Stage 6 needs a running program with a real workload. Decide what that program is before the stage starts, ideally the artifact stage 5 already shipped.

## Open threads

- No build tool chosen. The `README.md` puts tool comparison out of scope, so a tool still has to be picked to teach stage 5 with. Maven's guides are listed because they explain the lifecycle well; that is not the same as a decision.
- Garbage-collection tuning has no book-length source. Listed as a gap; may need one before stage 6.
- Frameworks are out of scope as subjects, but stage 7 has to judge them. That judgment needs a source and `RESOURCES.md` has none yet.
- Concurrency comparisons across workspaces are tempting here: virtual threads against goroutines, against `asyncio`. Keep them as pointers to the relevant glossary term in the other workspace rather than importing its material.
