# Python Notes

Working notes for the teaching session. Not linked from `README.md`.

## Preferences

- **Lessons are written for a general reader, deliberately.** No machine, OS, editor or installed version appears in any lesson, reference sheet, `README.md` or `RESOURCES.md`. Requested explicitly; do not personalise the lesson material to whoever is running the session.
- Mission is the full arc: zero to senior specialist, assuming no prior Python. Start at stage 1 rather than calibrating against a particular reader.
- Skill-heavy topic. Every stage has something runnable, and the reps carry the learning rather than confirming it.
- Reps must fit one sitting.

## State

Stages 1 to 6 are written: lessons 0001 to 0039, plus eight reference sheets. Stage 7 is unwritten.

Stage 6 stayed as one stage rather than splitting concurrency from performance, and the reason held up: both halves answer the same question, which is where the time goes. Lesson 0038 is the hinge, and it sends the reader to 0039 for the measurement that chooses the model.

Every number in the stage is from a run on one machine with CPython 3.14.7, and the numbers are labelled that way because the ratios transfer and the absolutes do not. Three findings changed what the lessons say. The classic lost-update demonstration with `counter += 1` did **not** reproduce, on any attempt, even with the switch interval at 1 microsecond, so the stage teaches the race through check-then-act across a real yield instead, which reproduces every time. Micro-optimisation folklore is dead: binding a function to a local gave no gain, and a comprehension beat an append loop by 12 per cent rather than the two-fold that gets repeated. And `fork` is no longer the default start method on any platform as of 3.14, which breaks code that relied on inheriting parent memory.

Stage 5 is anchored on a demonstration rather than an argument. Lesson 0033 contains a real run in which three parametrised tests reach 100 per cent statement and branch coverage, assert nothing, and let a function return double what it should. Everything the stage says about coverage as a signal follows from that one output, and it is the piece to protect if the stage is ever trimmed. The second anchor is lesson 0031's patch-target demonstration, which is lesson 0013's `from x import y` binding rule arriving as a broken test, so the two lessons should keep pointing at each other.

Stage 4 avoided becoming a tour of metaclasses, which the arc explicitly did not want, and the defence turned out to be structural rather than editorial: attribute lookup comes first (0022), and every later lesson in the stage is an application of that one ordered list. Properties and descriptors are steps one and three of it, the dunder map is what each construct calls, `__new__` is the step before any of it runs, the MRO is the path step three walks, and the metaclass lesson can then be mostly a table of cheaper hooks. Lesson 0027 states the decision rule in one line: a decorator does it unless subclasses must be affected without opting in.

Stage 3 kept typing and packaging together, as the arc planned, and the boundary held: they are one stage about code leaving the machine it was written on. Every tool claim in it was executed rather than recalled, against CPython 3.14.7, mypy 2.3.1, ruff 0.16.5 and uv 0.12.1, and three claims changed as a result. Annotations are lazily evaluated from 3.14 (PEP 649), which makes most of the old forward-reference advice historical. `strict = false` in a per-module mypy override is silently ineffective. And ruff's default rule selection is now far broader than the documented minimum, so the lesson tells the reader to write the selection down rather than naming a default.

Stage 2 is built as one chain rather than a set of topics. The iteration protocol (0008) is what makes generators (0009) predictable, generators are what make the `try/finally` in a context manager (0011) subtle, and exceptions (0010) sit between them because both later lessons depend on knowing what `finally` guarantees. Lessons 0012 to 0014 are the equipment: the shape data should take, the unit code is organised into, and what already ships. If a stage-2 lesson gets reordered, the 0008 to 0011 run is the part that must stay in sequence.

**How the glossary is populated here.** The skill says a term lands once it can be used correctly, which is a statement about a learner's demonstration. These lessons have no single learner, so the test is applied to the material instead: a term lands when a lesson has taught it well enough for a reader to use it. Stage 1 added six terms alongside the three pinned ones, stage 2 added seven, stage 3 added eight, stage 4 added seven, stage 5 added seven, and stage 6 added seven. Keep doing this per stage rather than upfront, and do not add a term the lessons have not earned.

## On the arc

Two stage boundaries are judgment calls worth revisiting once lessons exist:

- Stage 3 puts typing and packaging together because both are about code leaving the machine it was written on. If either grows past three or four lessons, they split.
- Resolved: stage 6 stayed merged. Six lessons was enough room for the GIL material to stand alone as 0034, and lesson 0038 is the hinge that uses the measurement from 0039 to choose a model, which is the shared idea made explicit.

## Version policy

The arc names no Python version. Where a lesson must assume one, it states which, and checks the claim against "What's New" and the version-status page in `RESOURCES.md` rather than recalling it. Two areas date fastest: the type system's current spellings, and the packaging toolchain.

## Open threads

- Tooling choice is unsettled. `uv` and Ruff are in `RESOURCES.md` because their documentation is good and current, not because they have won. A lesson naming a tool should teach the underlying standard, meaning `pyproject.toml` and virtual environments, so the lesson survives the tool being replaced. Stage 3 followed this: every lesson leads with the PEP and shows the tool as one instance, and lesson 0019 carries a command map so a reader on a different tool can translate.
- Free-threading was rechecked before stage 6 was written, and the stage now takes the position that a reader should write code correct on either build, since that is the same code. Recheck when a free-threaded build becomes the default: at that point lesson 0034's measurements need rerunning on one, and the CPU-bound rows of the model table in lesson 0038 change.
- `InterpreterPoolExecutor` is new enough that lesson 0036 recommends processes for anything shipping. Revisit once C extension support is settled; the lesson says explicitly that the answer comes from trying it rather than reading.
- Still no decision on whether reps land in a scratch repo or in one project that grows across the arc. Stages 3 and 5 were written assuming the reader has some project of their own, and both would land harder with a shared one. If that is ever added, the packaging reps in 0020 and the coverage reps in 0033 are the two places to rewrite first.
- Resolved: stage 4 did not become a tour of metaclasses. Ordering it around attribute lookup did the work, and the metaclass lesson ended up mostly a table of cheaper hooks. Keep that ordering if the stage is ever revised.
