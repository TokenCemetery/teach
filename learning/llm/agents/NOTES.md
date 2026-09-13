# LLM Agents Notes

Working notes for the teaching session. Not linked from `README.md`.

## Preferences

- **Pseudocode, not runnable code.** Chosen deliberately over targeting one provider's SDK. The reasoning is in #130: tool-calling surfaces churn, and pseudocode keeps the loop correct while the APIs move. A lesson that quietly drifts into one provider's exact call signature has lost the point of the choice.
- **Provider-neutral.** Where a wire format has to be shown as a real captured exchange, show one, then show a second provider only as the diff from it. Do not double every example.
- Computer use and browser agents were promoted to a full stage rather than folded into environments, so stage 11 is expected to carry real depth rather than a mention.
- MCP stays in this track at stage 9 rather than waiting for a track of its own.
- Disclosed background: not yet established. The constraints in `README.md` assume familiarity with what a language model is and comfort reading Python-like code, which is an assumption rather than something the learner confirmed.

## On the arc

The sixteen stages in `README.md` were written upfront during the planning session recorded in #130. All 37 lessons were then also written in one batch session (still #130), not earned one lesson at a time against a live learner's demonstrated answers. `learning-records/` is still empty: nothing here has been calibrated against a real learner's performance, only checked for internal consistency and structural correctness.

Two merges are held in reserve if the arc proves too long once it is actually taught: stage 12 with 13, and stage 10 with 11. Since every lesson now exists, this is unlikely to still be needed, but the option is recorded here in case a real learner's pace argues for it.

Grounding: most lessons cite one of the sources already in `RESOURCES.md`; a handful of concrete claims (illustrative token-cost figures in stage 15, some worked examples) are original synthesis rather than something a primary source stated directly, and are labeled as illustrative in the lesson text rather than presented as measured facts.

## Open threads

- The pseudocode choice removes the "predict, then run" rep that the teach skill leans on. The replacement is inspection: read a real trace, open a real MCP manifest, mark the permission boundary of an agent that already runs. Whether that carries the same weight is unproven, since no learner has actually worked through these reps yet.
- Which real agent the learner has access to for the inspection reps is still unknown; several reps in stages 2 onward assume access to a running agent or its trajectory logs. Ask on the first real teaching session.
- Nothing has been attempted by an actual learner yet. The first real session should calibrate before trusting the written arc: take one practice item from an early lesson and check the level, rather than assuming a batch-authored lesson landed correctly for this specific learner.
- Because all 37 lessons were drafted before any learner feedback, expect the first several real sessions to surface pacing or difficulty corrections that a normally-earned arc would have caught lesson by lesson. Revise lessons in place as that feedback arrives, per `FORMATS.md`'s glossary guidance extended to lessons: this is compressed understanding, not a frozen artifact.
