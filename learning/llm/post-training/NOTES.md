# LLM Post-Training Notes

Working notes for the teaching session. Not linked from `README.md`.

## Preferences

- **Algorithm-first, not paper-survey.** Chosen deliberately over listing papers chronologically. The reasoning is in #134: each stage should teach one training objective from its loss function outward, what is being maximized and what the gradient does, with the papers anchoring each stage rather than driving its structure.
- Reward hacking is taught inside stage 3 (reward modeling), not saved for the judgment stage, because it is the failure mode that makes every later stage's tradeoffs legible.
- Small-scale reps by design: labs run SFT and DPO on a small open model, and reason from there to what the cited frontier papers report, the same scale discipline `llm/finetuning` already uses.
- Disclosed background: not yet established. The constraints in `README.md` assume `llm/transformers` and familiarity with `llm/finetuning`'s adapter mechanics, which are assumptions rather than something the learner confirmed.

## On the arc

The ten stages in `README.md` were written upfront during the planning session recorded in #134, not earned one lesson at a time. No lesson exists yet and `learning-records/` is empty, so nothing here has been calibrated against a demonstrated answer.

One merge is held in reserve if the arc proves too long once it is being taught: stage 6 with 7, since GRPO is presented in the same paper that would anchor stage 7 anyway (DeepSeekMath), and DeepSeek-R1 extends rather than replaces it.

The arc table has no `Lessons` column yet, because there are no lessons for it to name. Add the column with the first lesson, not later: `check-workspace.py` requires it once `lessons/` exists.

## Open threads

- Whether the learner has GPU access sufficient for a small PPO run (stage 4) is unknown; PPO's instability is easier to demonstrate than to describe, but it is also the most compute-hungry lab in the arc. Ask before writing that stage.
- Preference-data quality (stage 3) is the thinnest-sourced part of the arc; see the gap noted in `RESOURCES.md`.
- Nothing has been attempted yet. The first interactive session should calibrate before teaching forward, rather than assuming the written arc landed as planned.
