# LLM Post-Training Notes

Working notes for the teaching session. Not linked from `README.md`.

## Preferences

- **Algorithm-first, not paper-survey.** Chosen deliberately over listing papers chronologically. The reasoning is in #134: each stage should teach one training objective from its loss function outward, what is being maximized and what the gradient does, with the papers anchoring each stage rather than driving its structure.
- Reward hacking is taught inside stage 3 (reward modeling), not saved for the judgment stage, because it is the failure mode that makes every later stage's tradeoffs legible.
- Small-scale reps by design: labs run SFT and DPO on a small open model, and reason from there to what the cited frontier papers report, the same scale discipline `llm/finetuning` already uses.
- Disclosed background: not yet established. The constraints in `README.md` assume `llm/transformers` and familiarity with `llm/finetuning`'s adapter mechanics, which are assumptions rather than something the learner confirmed.

## On the arc

The ten stages in `README.md` were written upfront during the planning session recorded in #134, not earned one lesson at a time, then written stage by stage, one commit per stage, across lessons 0001 through 0020. The arc closed exactly as planned: ten stages, no stage needed the stage-6-with-7 merge held in reserve, and the `Lessons` column has been added to the arc table now that every stage has one. `post-training`'s `arc_lessons_column: False` entry has been removed from `CONVENTIONS` in `check-workspace.py`, the same way `pretraining`'s was when its arc completed. `learning-records/` is still empty: no lesson here has yet been taught in an interactive session, so nothing has been calibrated against a demonstrated answer.

Stage 10's closing lesson (0020) settles the same GRPO/verifiable-reward attribution point noted below as its own worked example of settling a disputed claim from the primary source, rather than introducing a fresh one.

Stage 9's second lesson (0018) is this track's one deliberate link into `llm/evals`, per the `## Out of scope` line in `README.md`, mirroring how `llm/pretraining`'s own stage 9 handed off to the same track. Its primary source is `llm/evals`'s own LLM-as-judge reference sheet rather than a paper, since the lesson's content (over-refusal, judge bias) is drawn directly from it rather than from a source this track located independently.

Stage 7's distillation-versus-direct-RL comparison (0014, the 32B AIME 2024 gap: 47.0% direct RL against 72.6% distilled) turned out to be an unusually strong, load-bearing piece of evidence, precise enough to cite numerically rather than only qualitatively. Worth reusing directly in Stage 10's judgment material rather than re-deriving a similar point from a weaker source.

Stage 6 surfaced an attribution point worth being careful about: DeepSeekMath's own GRPO uses a *trained* reward model, not a rule-based verifiable one (checked directly in the paper; no mention of rule-based or ground-truth-checker rewards anywhere in its text). Lesson 12 introduces verifiable rewards as a natural pairing with GRPO's mechanism rather than attributing that specific combination to DeepSeekMath itself, and forwards the at-scale version to Stage 7's DeepSeek-R1 source, where it belongs.

Stage 4 needed a source outside RESOURCES.md's original list for lesson 7 (PPO's own clip formula): ar5iv could not convert the PPO paper (no LaTeX source available, only a PDF), so its text was extracted directly from the arXiv PDF with `pdfminer` instead. Worth remembering if a future lesson needs to quote this paper again.

Stage 3's reward-hacking lesson (0005) turned out better sourced than expected: Bai et al.'s train-PM-versus-test-PM divergence methodology gives a genuinely useful detection mechanism, not just a definition, and their harmlessness-over-optimization case (blanket "seek therapy" deflection) is a concrete, memorable real example rather than a hypothetical one.

## Open threads

- Whether the learner has GPU access sufficient for a small PPO run (stage 4) is unknown, and was never asked, since no interactive session has run yet.
- Preference-data quality (stage 3) is the thinnest-sourced part of the arc; see the gap noted in `RESOURCES.md`.
- Nothing in this track has been taught in a real session. The first one should calibrate before trusting the arc's pacing, difficulty, or stage boundaries as written; stage 4 (three lessons, dense with the RLHF objective, PPO's clip formula, and the four-model cost accounting) is a candidate for turning out too long for one sitting.
