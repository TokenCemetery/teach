# TypeScript Notes

Working notes for the teaching session. Not linked from `README.md`.

## Preferences

- **Lessons are written for a general reader, deliberately.** No machine, OS, editor or installed version appears in any lesson, reference sheet, `README.md` or `RESOURCES.md`. Requested explicitly; do not personalise the lesson material to whoever is running the session.
- Mission is the full arc: zero to senior specialist, assuming no prior TypeScript and no more JavaScript than the arc teaches. Start at stage 1 rather than calibrating against a particular reader.
- Reps must fit one sitting. Many are type experiments rather than programs, and the playground is enough for those.

## State

The workspace was prepared in one pass: mission, arc and sources. No lesson has been written yet, so the lesson table is empty rather than drifted, and `GLOSSARY.md` holds only the three pinned usage terms.

## On the arc

- Stage 1 is JavaScript, and that is the decision most likely to be questioned. It stays because every hard TypeScript bug is a runtime behaviour the types described wrongly, and a reader who cannot predict the runtime cannot tell which of the two is lying.
- Stage 5 is the load-bearing stage for the mission. If the arc has to be cut short, stages 1 to 5 are the part that makes someone dangerous to leave alone with a codebase; stage 6 mostly prevents self-inflicted damage.
- Stage 6 has a failure mode built into it: type-level puzzles are enjoyable and mostly do not pay. Every lesson there needs a caller who benefits, or it does not get written.

## Version policy

The arc names no TypeScript version. Where a lesson must assume one, it states which and checks the release notes rather than recalling the feature. Inference and narrowing improve in ordinary releases, so a claim that something "cannot be expressed" dates faster than anything else here.

## Open threads

- No decision yet on which runtime the reps use. The playground covers stages 2, 4 and 6 entirely; stages 1, 3 and 5 need a real runtime, and the module-resolution material depends on which one.
- Runtime validation needs one library to teach with. Zod is in `RESOURCES.md` for its inference, which is not the same as a decision, and the lesson should teach the boundary rather than the library.
- Module resolution is under-sourced and over-complicated in practice. Expect this to be the hardest stage 3 lesson to write honestly, and keep it to the compiler's model plus one runtime.
- `enum`, namespaces and decorators are legacy-shaped features that still appear in real codebases. Currently unplaced: they belong somewhere in stage 7 as review material rather than being taught as tools.
