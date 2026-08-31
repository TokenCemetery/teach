# Python Notes

Working notes for the teaching session. Not linked from `README.md`.

## Preferences

- **Lessons are written for a general reader, deliberately.** No machine, OS, editor or installed version appears in any lesson, reference sheet, `README.md` or `RESOURCES.md`. Requested explicitly; do not personalise the lesson material to whoever is running the session.
- Mission is the full arc: zero to senior specialist, assuming no prior Python. Start at stage 1 rather than calibrating against a particular reader.
- Skill-heavy topic. Every stage has something runnable, and the reps carry the learning rather than confirming it.
- Reps must fit one sitting.

## State

Stage 1 is written: lessons 0001 to 0007, plus the `reference/mutability-and-copying.md` sheet they all point at. Stages 2 to 7 are unwritten.

**How the glossary is populated here.** The skill says a term lands once it can be used correctly, which is a statement about a learner's demonstration. These lessons have no single learner, so the test is applied to the material instead: a term lands when a lesson has taught it well enough for a reader to use it. Stage 1 therefore added six terms alongside the three pinned ones. Keep doing this per stage rather than upfront, and do not add a term the lessons have not earned.

## On the arc

Two stage boundaries are judgment calls worth revisiting once lessons exist:

- Stage 3 puts typing and packaging together because both are about code leaving the machine it was written on. If either grows past three or four lessons, they split.
- Stage 6 merges concurrency and performance. They share one idea, that you measure before you choose, but the GIL material may need enough room to stand alone.

## Version policy

The arc names no Python version. Where a lesson must assume one, it states which, and checks the claim against "What's New" and the version-status page in `RESOURCES.md` rather than recalling it. Two areas date fastest: the type system's current spellings, and the packaging toolchain.

## Open threads

- Tooling choice is unsettled. `uv` and Ruff are in `RESOURCES.md` because their documentation is good and current, not because they have won. A lesson naming a tool should teach the underlying standard, meaning `pyproject.toml` and virtual environments, so the lesson survives the tool being replaced.
- Free-threaded CPython changes what stage 6 can claim about threads. Recheck the state of PEP 703 before that stage is written.
- No decision yet on whether reps land in a scratch repo or in one project that grows across the arc. The latter would make stages 3 and 5 land much harder.
- Stage 4 risks becoming a tour of metaclasses, which the arc explicitly does not want. The out-of-scope list is the defence.
