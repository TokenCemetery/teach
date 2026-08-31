# Java Notes

Working notes for the teaching session. Not linked from `README.md`.

## Preferences

- **Lessons are written for a general reader, deliberately.** No machine, OS, editor or installed version appears in any lesson, reference sheet, `README.md` or `RESOURCES.md`. Requested explicitly; do not personalise the lesson material to whoever is running the session.
- Mission is the full arc: zero to senior specialist, assuming no prior Java. Start at stage 1 rather than calibrating against a particular reader.
- Reps must fit one sitting, with stage 6 excepted because profiling needs a program that runs long enough to profile.

## State

Stages 1 to 4 are written: lessons 0001 to 0028, plus the `reference/equality-hashing-and-ordering.md`, `reference/modelling.md`, `reference/idiom-and-library.md` and `reference/concurrency.md` sheets. Stages 5 to 7 are unwritten.

Stage 4 was written under two rules the earlier stages did not need: reproduce every race and say how many attempts it took, and report honestly when a race does not reproduce. Both earned their place. Three of the stage's demonstrations came out other than expected because of them, and the stage is better for saying so than it would have been for asserting the folklore.

Lesson 0023 is the stage's anchor and the piece to protect. It contains a **directly observed reordering**, which most writing on this subject says you should not expect to see: a store-buffering test produced an outcome impossible under sequential consistency on ninety-five to ninety-eight per cent of five million rounds, and marking the two fields `volatile` took it to zero on the same five million. That single pair of runs does more for the reader than the whole vocabulary does, and the lesson is built around it.

Lesson 0027 is the other one to protect, for the opposite reason: it is the lesson most likely to go stale, and it is written so that the reader is told to measure rather than to trust it.

Stage 3 is seven lessons and is organised as two halves that share one question, which is whether a reviewer would call the code unidiomatic. The first half is control flow and absence, meaning exceptions (0015) and `Optional` (0016), and the second is the library a reviewer expects you to know, meaning streams and collectors (0017, 0018) then files, time and text (0019 to 0021). Streams are split from collectors deliberately: the pipeline and the container it becomes fail in different ways, and putting them together produced a lesson where the traps drowned the mechanics.

Lesson 0018 is the one to protect in this stage, because it carries the least guessable fact in the arc: `Stream.toList` accepts a null element and `Collectors.toUnmodifiableList` refuses one, which is the opposite of what the names suggest. That asymmetry is a three-column table in the sheet for exactly this reason.

Stage 2 is eight lessons rather than the six or seven the other stages will need, because the modelling surface is genuinely wider here: a class, a record, an interface, an abstract class, a sealed hierarchy and an enum are six ways to say almost the same thing, and the stage's whole job is telling them apart. The order is the load-bearing part. Interfaces (0009) come before inheritance (0010) so that a reader meets the contract before the mechanism, and sealed types (0011) come after both because sealing is a restriction on inheritance that only makes sense once inheritance has been priced. If the stage is ever reordered, that run is what must survive.

Lesson 0010 is the one to protect. It is the only place in the arc that argues against a language feature at length, and it does that with measured evidence rather than taste: construction order producing a `null` field, static and field hiding resolving on the declared type, and the counting-set failure with real numbers before and after the fix.

**Onboarding is handled inside lesson 0007**, in a short "Running these examples" subsection, rather than by inserting a new lesson at the front. Stage 1 shipped without ever showing how to compile and run, which is a real gap for a workspace whose constraints say "assumes no prior Java", and 0007 is the first lesson where the reader declares a class of their own, so it is the honest place for it. Renumbering stage 1 to put it first would have broken every existing cross-reference for no pedagogical gain. If stage 3 shows a gap of the same kind, solve it the same way.

**How the glossary is populated here.** The skill's test, that a term lands once it can be used correctly, is a statement about a learner's demonstration. These lessons have no single learner, so the test is applied to the material: a term lands when a lesson has taught it well enough for a reader to use it. Stage 1 added seven terms alongside the three pinned ones, stage 2 added thirteen, stage 3 added eight, and stage 4 added eleven. Keep doing this per stage, and do not add a term the lessons have not earned. Two of stage 2's entries are deliberately a pair: "Invariance (of generics)" is written to be read against the existing "Covariance (of arrays)", since the two rules are opposites and the contrast is the lesson.

## What execution changed

Every behavioural claim in stage 2 was run rather than recalled, on the release the workspace names. Four things came out differently from what recall would have produced, and all four changed lesson content.

- **`this(...)` and `super(...)` no longer have to be the first statement.** JEP 513, Flexible Constructor Bodies, was finalised in Java 25: statements that do not touch the instance may run before the call, which is how an argument gets validated or computed before the superclass sees it. The old rule is stated in every book and was nearly written into two lessons. Verified by running a constructor with a validating prologue.
- **The classic counting-set bug does not reproduce in its usual form.** Overriding only `add` on a `HashSet` subclass gives the correct count, because `AbstractCollection.addAll` calls the overridable `add` and increments nothing itself. The double count needs both methods overridden and both incrementing. Building it on `ArrayList` never reproduces at all, since its `addAll` is a bulk copy. Lesson 0010 uses the version that actually fails.
- **Adding an enum constant without recompiling a switch throws `MatchException`**, not the `IncompatibleClassChangeError` usually named. Reproduced by split compilation, and stated as observed.
- **`List.copyOf` does not simply skip the copy for an already-unmodifiable list.** It returns the same instance for a list its own factories produced, and a new one for a `Collections.unmodifiableList` view, because the view is an implementation it cannot recognise as safe. Lesson 0014 states that distinction rather than the flat claim.

A fifth detail worth keeping: `this.field = ...` inside a compact constructor is a compile error, not a redundancy, which lesson 0008 turns into a practice item.

Stage 3 produced four more, and the first two are the ones that would have been written wrongly from recall.

- **`Stream.toList` and `Collectors.toUnmodifiableList` disagree about null.** The first accepts a null element, the second throws. Both produce an unmodifiable list, so the names give no hint. Taught as a contrast rather than a rule.
- **The documented "`Files.lines` must be closed" leak does not reproduce the obvious way.** A tight loop reusing one variable survived a hundred thousand iterations, because the cleaner closes unreachable streams. It only failed once every stream was kept reachable, at roughly sixty thousand open descriptors. Lesson 0019 teaches the rule and the mechanism that hides it, since "it works in my loop" is exactly how this reaches production.
- **`String.valueOf(null)` is not a compile-time ambiguity.** It compiles, resolves to the more specific `valueOf(char[])` overload, and throws at run time. The spec for the lesson said "ambiguity" and was wrong; the lesson teaches what happens.
- **A single expression using `+` on strings already compiles to one `StringConcatFactory` call**, checked with `javap`, not to a chain of `StringBuilder` appends. So the familiar advice applies to the loop and not to the expression, and lesson 0021 says which.

Two smaller ones worth not losing: `peek` can be skipped entirely when the terminal operation does not need the elements, which makes it a debugging tool and not a processing step, and end-of-month clamping does not remember the original day, so January the 31st plus two months is the 28th of March rather than the 31st.

Stage 4 produced the largest set, and the first two are the reason this stage was flagged as the hardest to keep honest.

- **`synchronized` no longer pins a carrier thread.** Measured against a genuine two-worker platform pool as a control, virtual threads holding a monitor across a blocking sleep finished in about half a second where the pinned control took about twelve and a half. `Object.wait` inside `synchronized` behaves the same way. JEP 491 made this change in JDK 24. **JEP 444's own text still says `synchronized` pins**, and so does almost everything else written on the subject, including its corollary advice to move off `synchronized` onto `ReentrantLock` for this reason. That advice is now stale, and lesson 0027 says so with the measurement behind it. A real blocking native call, made through the Foreign Function and Memory API, does still pin, and matched the control exactly.
- **The diagnostic built for pinning does not catch the remaining case.** The `jdk.VirtualThreadPinned` flight-recorder event reported zero for the native call that demonstrably pinned, because the event fires on a *failed unmount attempt* and a plain native call never attempts one. It correctly reported zero for the `synchronized` cases too, so the event agrees with the timing in three cases out of three and is useless in exactly the one that matters. This is not spelled out in the JEP and only surfaced from cross-checking event counts against timings. `-Djdk.tracePinnedThreads` produces no output at all now, which is intentional.
- **Structured concurrency is still a preview in this release, and its shape has changed.** `StructuredTaskScope` is now an interface with a static `open()` factory taking a `Joiner`, and two type parameters. The constructor-based form that most write-ups show does not compile even with the preview flag. The lesson shows the verified current shape once, states that it is preview, and tells the reader what to use meanwhile.
- **Unsafe publication of a non-`final` field did not reproduce**, in six million attempts across three runs. Lesson 0023 reports that rather than asserting the failure, and uses it as the deliberate counterpoint to the reordering that did reproduce: a clean run proves nothing, a dirty run proves everything.
- **The naive check-then-act race across two lock acquisitions did not reproduce** with no delay between the check and the act. It reproduced on five runs out of five once the window was widened. Lesson 0024 teaches the widened version and says why the narrow one passed.
- **`findDeadlockedThreads` does not find cycles involving virtual threads.** That is documented rather than measured, and it directly bounds the diagnostic technique lesson 0028 recommends, so both lessons state it.

Numbers worth keeping for comparison when this stage is revised, all from one machine and useful as ratios: the platform-thread ceiling landed at 4,066 and 4,068 in two independently written lessons, a million virtual threads were created and blocked in under a second, blocking I/O across virtual threads beat a platform pool by about seventeen times while CPU-bound work showed no gain at all, `LongAdder` beat `AtomicLong` by ten to seventeen times under contention, and holding a lock across a simulated I/O call cost about eight times the throughput of releasing it first.

## Version policy

The baseline is the current long-term-support release, which was JDK 25 when this workspace was prepared. Two rules follow, and they matter more here than in most languages:

- Every language feature is introduced with the release it arrived in. Java is read across many versions, and a lesson that says "modern Java" without a number is useless in three years.
- Before a stage is written, check the JEP index and the release page in `RESOURCES.md` for what has changed. The six-month cadence means the arc will drift on its own.

Recheck which release is long-term-support when resuming this workspace after a gap. The support roadmap in `RESOURCES.md` is the source for that, not recall.

Rechecked against that roadmap before stage 2 was written: 8, 11, 17, 21 and 25 are the long-term-support releases, and the next is 29, planned for September 2027. JDK 25 is therefore still the right baseline and no link needs moving. Recheck again before stage 5, since the build and testing material is the part most likely to have drifted.

## On the arc

- Resolved: stage 2 did depart from how Java is usually taught, and the departure held. Records (0008) and interfaces (0009) come before `extends` (0010), and by the time inheritance arrives the reader has already modelled two domains without it, so lesson 0010 can price it rather than sell it. Sealed types then land as a restriction on something already understood. Keep this order.
- Resolved: stage 4 was the hardest to keep honest, and the split the note predicted held. "Java Concurrency in Practice" carried the model, meaning happens-before, publication and the failure modes, and none of that has aged. Every API claim came from a run instead, and that is what caught the stale pinning advice. The warning to watch for a 2006 idiom taught as current turned out to understate the problem: the stalest advice came from a 2023 JEP rather than a 2006 book.
- Stage 6 needs a running program with a real workload. Decide what that program is before the stage starts, ideally the artifact stage 5 already shipped.

## Open threads

- No build tool chosen. The `README.md` puts tool comparison out of scope, so a tool still has to be picked to teach stage 5 with. Maven's guides are listed because they explain the lifecycle well; that is not the same as a decision.
- Garbage-collection tuning has no book-length source. Listed as a gap; may need one before stage 6.
- Frameworks are out of scope as subjects, but stage 7 has to judge them. That judgment needs a source and `RESOURCES.md` has none yet.
- Concurrency comparisons across workspaces are tempting here: virtual threads against goroutines, against `asyncio`. Keep them as pointers to the relevant glossary term in the other workspace rather than importing its material.
