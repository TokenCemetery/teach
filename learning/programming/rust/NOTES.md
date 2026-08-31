# Rust Notes

Working notes for the teaching session. Not linked from `README.md`.

## Preferences

- **Lessons are written for a general reader, deliberately.** No machine, OS, editor or installed version appears in any lesson, reference sheet, `README.md` or `RESOURCES.md`. Requested explicitly; do not personalise the lesson material to whoever is running the session.
- Mission is the full arc: zero to senior specialist, assuming no prior Rust and no systems-programming background. Start at stage 1 rather than calibrating against a particular reader.
- Skill-heavy topic, and the compiler is the answer key. Every early lesson should have a "predict what the compiler says, then compile" rep, because that is the only way the borrow rules stop feeling arbitrary.
- Reps must fit one sitting.

## State

Stage 1 is written: lessons 0001 to 0006, plus the `reference/ownership-and-borrowing.md` sheet every lesson in the stage points at. Stages 2 to 8 are unwritten.

Lesson 0006 is the stage's capstone and the piece worth protecting. It teaches reading the compiler's three spans, the five error codes stage 1 actually produces, and the four honest fixes against the four workarounds. It is the direct answer to the stage's success criterion, and it is also where the "what not to do here" rule below is made explicit for a reader rather than kept as a note.

**How the glossary is populated here.** The skill's test, that a term lands once it can be used correctly, is about a learner's demonstration. These lessons have no single learner, so the test is applied to the material: a term lands when a lesson has taught it well enough for a reader to use it. Stage 1 added eight terms alongside the four pinned ones. Keep doing this per stage, and do not add a term the lessons have not earned.

## On the arc

Eight stages, which is more than the other workspaces here, and the reason is that Rust has three separate hard walls rather than one: ownership in stage 1, lifetimes and traits in stage 4, and async in stage 6. Compressing any of them produces a reader who copies patterns.

Two boundaries worth revisiting once lessons exist:

- Stage 5 and stage 6 could merge into one concurrency stage. They stay apart because sharing across threads is understandable from ownership alone, and async is a separate model layered on top.
- Stage 7 pairs `unsafe` with performance. The link is real, since most `unsafe` in application code is written for speed that was never measured, and the pairing is meant to make that visible. If it reads as two topics, it splits.

## What not to do here

- Do not teach a fight with the borrow checker as a set of workarounds. `clone`, `Rc<RefCell<_>>` and lifetime annotations all make an error go away, and a lesson that reaches for one without saying what the design should have been teaches the wrong habit permanently.
- Do not reach `unsafe` before stage 7. The Rustonomicon is listed for that stage only, and quoting it earlier makes the safe subset look optional.

## Version policy

The arc names no Rust version. Where a lesson depends on an edition or a stabilised feature, it says which, and checks the release announcement rather than recalling it. Async and trait features move fastest, so a claim that something "cannot be expressed" dates quickly.

## Open threads

- No project chosen for the reps. A crate that grows across the arc would make stages 3 and 8 concrete, and a command-line tool is the obvious candidate because it needs no framework.
- Cancellation safety in async is under-sourced. Stage 6 may be the first place the session has to do real source-finding work rather than teaching.
- Variance and higher-ranked trait bounds are unplaced. Currently implied by stage 4, but they may deserve their own late lesson, closer to stage 8, where API design makes them matter.
- Comparisons to other workspaces are tempting here, particularly ownership against garbage collection and async against goroutines. Keep them as pointers to a glossary term in the other workspace rather than importing its material.
