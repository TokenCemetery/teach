# LLM Pretraining Notes

Working notes for the teaching session. Not linked from `README.md`.

## Preferences

- **Framework-adjacent, not framework-agnostic.** Chosen deliberately over the pseudocode approach `llm/agents` uses. The reasoning is in #133: distributed-training techniques (ZeRO, tensor and pipeline parallelism) are stable enough, and specific enough in their APIs, that naming the real library is more useful than hiding behind pseudocode.
- Small-scale reps by design: no lesson trains a frontier-scale model. A lab runs a GPT-2-scale model on a handful of GPUs, or simulates the collective operations on CPU, then reasons from there to what the cited papers report at frontier scale.
- Disclosed background: not yet established. The constraints in `README.md` assume `llm/transformers` as a prerequisite and access to multiple GPUs (or a CPU simulation of the collective operations), which are assumptions rather than something the learner confirmed.

## On the arc

The ten stages in `README.md` were written upfront during the planning session recorded in #133, not earned one lesson at a time, then written stage by stage, one commit per stage, across lessons 0001 through 0024. The arc closed exactly as planned: ten stages, no stage needed the stage-4-with-5 merge held in reserve, and the `Lessons` column has been added to the arc table now that every stage has one. `pretraining`'s `arc_lessons_column: False` entry has been removed from `CONVENTIONS` in `check-workspace.py`; `post-training` still carries the equivalent entry until its own arc completes. `learning-records/` is still empty: no lesson here has yet been taught in an interactive session, so nothing has been calibrated against a demonstrated answer.

Stage 9's second lesson (0021) is this track's one deliberate link into `llm/evals`, per the `## Out of scope` line in `README.md`. It links the reference sheet and glossary term directly rather than a lesson, per `SKILL.md`'s linking rule, and does not restate held-out design or contamination detection beyond the one sentence needed to explain why Gopher filtered its eval benchmarks out of training.

Stage 8 turned out better sourced than `RESOURCES.md`'s original gap note expected: the OPT-175B paper's public logbook gave real failure-frequency numbers and a concrete recovery procedure, closing most of the gap. What is still missing, and noted in `RESOURCES.md`, is a primary source stating an actual checkpoint-interval policy; the checkpoint-frequency tradeoff itself is taught from general engineering reasoning rather than a cited number.

Stage 6's last lesson (0014) synthesizes a judgment call ("reach for ZeRO first, tensor/pipeline parallelism once sharding alone is not enough") from combining the ZeRO and Megatron-LM papers' own separately stated positions, rather than quoting either paper making that exact combined claim. Flagging this in case a future pass wants a single source that already makes the comparison directly, which was not found.

Stage 10's closing lesson (0024) settles a specific, genuinely common online confusion (whether bf16 needs loss scaling the way fp16 does) from the primary sources this track already cites, as its worked example of settling a disputed claim rather than trusting a secondary account. Confirmed the negative claim carefully: "loss scal" does not appear anywhere in the Gopher paper's text before stating that it describes no such mitigation for bf16.

Lesson 3's worked BPE example surfaced a wrinkle not called out in the mission or arc: the "merge the most frequent pair" rule does not by itself resolve a tie between equally frequent pairs, which the paper's own toy corpus happens to produce on its very first step. Worth remembering if a later lesson references "the" BPE merge order for this example, since it is implementation-dependent, not uniquely determined.

## Open threads

- Whether the learner has access to multiple GPUs for the distributed-training reps (stages 4 through 6) is unknown, and was never asked, since no interactive session has run yet.
- Nothing in this track has been taught in a real session. The first one should calibrate before trusting the arc's pacing, difficulty, or stage boundaries as written; several stages (especially 5 and 6, dense with worked arithmetic) are candidates for turning out too long for one sitting.
