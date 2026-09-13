# LLM Agents Notes

Working notes for the teaching session. Not linked from `README.md`.

## Preferences

- **Pseudocode, not runnable code.** Chosen deliberately over targeting one provider's SDK. The reasoning is in #130: tool-calling surfaces churn, and pseudocode keeps the loop correct while the APIs move. A lesson that quietly drifts into one provider's exact call signature has lost the point of the choice.
- **Provider-neutral.** Where a wire format has to be shown as a real captured exchange, show one, then show a second provider only as the diff from it. Do not double every example.
- Computer use and browser agents were promoted to a full stage rather than folded into environments, so stage 11 is expected to carry real depth rather than a mention.
- MCP stays in this track at stage 9 rather than waiting for a track of its own.
- Disclosed background: not yet established. The constraints in `README.md` assume familiarity with what a language model is and comfort reading Python-like code, which is an assumption rather than something the learner confirmed.

## On the arc

The sixteen stages in `README.md` were written upfront during the planning session recorded in #130, not earned one lesson at a time. No lesson exists yet and `learning-records/` is empty, so nothing here has been calibrated against a demonstrated answer.

Two merges are held in reserve if the arc proves too long once it is being taught: stage 12 with 13, and stage 10 with 11.

The arc table has no `Lessons` column yet, because there are no lessons for it to name. Add the column with the first lesson, not later: `check-workspace.py` requires it, and six older arcs already had to be retrofitted.

## Open threads

- The pseudocode choice removes the "predict, then run" rep that the teach skill leans on. The replacement is inspection: read a real trace, open a real MCP manifest, mark the permission boundary of an agent that already runs. Whether that carries the same weight is unproven, and the first two or three lessons are where to find out.
- Which real agent the learner has access to for those inspection reps is unknown. Ask before writing stage 2, because several later reps depend on the answer.
- Nothing has been attempted yet. The first interactive session should calibrate before teaching forward: take one practice item and check the level, rather than assuming the written arc landed.
