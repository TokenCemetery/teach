# LLM Post-Training Notes

Working notes for the teaching session. Not linked from `README.md`.

## Preferences

- **Algorithm-first, not paper-survey.** Chosen deliberately over listing papers chronologically. The reasoning is in #134: each stage should teach one training objective from its loss function outward, what is being maximized and what the gradient does, with the papers anchoring each stage rather than driving its structure.
- Reward hacking is taught inside stage 3 (reward modeling), not saved for the judgment stage, because it is the failure mode that makes every later stage's tradeoffs legible.
- Small-scale reps by design: labs run SFT and DPO on a small open model, and reason from there to what the cited frontier papers report, the same scale discipline `llm/finetuning` already uses.
- Disclosed background: not yet established. The constraints in `README.md` assume `llm/transformers` and familiarity with `llm/finetuning`'s adapter mechanics, which are assumptions rather than something the learner confirmed.

## On the arc

The ten stages in `README.md` were written upfront during the planning session recorded in #134, not earned one lesson at a time. Stages 1 through 8 (lessons 0001 through 0016) are now written; `learning-records/` is still empty, so nothing here has been calibrated against a demonstrated answer yet.

Stage 7's distillation-versus-direct-RL comparison (0014, the 32B AIME 2024 gap: 47.0% direct RL against 72.6% distilled) turned out to be an unusually strong, load-bearing piece of evidence, precise enough to cite numerically rather than only qualitatively. Worth reusing directly in Stage 10's judgment material rather than re-deriving a similar point from a weaker source.

Stage 6 surfaced an attribution point worth being careful about: DeepSeekMath's own GRPO uses a *trained* reward model, not a rule-based verifiable one (checked directly in the paper; no mention of rule-based or ground-truth-checker rewards anywhere in its text). Lesson 12 introduces verifiable rewards as a natural pairing with GRPO's mechanism rather than attributing that specific combination to DeepSeekMath itself, and forwards the at-scale version to Stage 7's DeepSeek-R1 source, where it belongs.

Stage 4 needed a source outside RESOURCES.md's original list for lesson 7 (PPO's own clip formula): ar5iv could not convert the PPO paper (no LaTeX source available, only a PDF), so its text was extracted directly from the arXiv PDF with `pdfminer` instead. Worth remembering if a future lesson needs to quote this paper again.

Stage 3's reward-hacking lesson (0005) turned out better sourced than expected: Bai et al.'s train-PM-versus-test-PM divergence methodology gives a genuinely useful detection mechanism, not just a definition, and their harmlessness-over-optimization case (blanket "seek therapy" deflection) is a concrete, memorable real example rather than a hypothetical one.

One merge is held in reserve if the arc proves too long once it is being taught: stage 6 with 7, since GRPO is presented in the same paper that would anchor stage 7 anyway (DeepSeekMath), and DeepSeek-R1 extends rather than replaces it.

**The arc table deliberately has no `Lessons` column yet, and will not until every stage has at least one lesson**, the same approach `llm/pretraining` used while it was written stage by stage (see its own `NOTES.md`). `post-training` carries an explicit `arc_lessons_column: False` entry in `CONVENTIONS` in `check-workspace.py`; remove it and add the column once all ten stages have lessons.

## Open threads

- Whether the learner has GPU access sufficient for a small PPO run (stage 4) is unknown; PPO's instability is easier to demonstrate than to describe, but it is also the most compute-hungry lab in the arc. Ask before writing that stage.
- Preference-data quality (stage 3) is the thinnest-sourced part of the arc; see the gap noted in `RESOURCES.md`.
- Nothing has been attempted yet. The first interactive session should calibrate before teaching forward, rather than assuming the written arc landed as planned.
