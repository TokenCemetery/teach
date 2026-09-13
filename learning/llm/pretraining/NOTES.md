# LLM Pretraining Notes

Working notes for the teaching session. Not linked from `README.md`.

## Preferences

- **Framework-adjacent, not framework-agnostic.** Chosen deliberately over the pseudocode approach `llm/agents` uses. The reasoning is in #133: distributed-training techniques (ZeRO, tensor and pipeline parallelism) are stable enough, and specific enough in their APIs, that naming the real library is more useful than hiding behind pseudocode.
- Small-scale reps by design: no lesson trains a frontier-scale model. A lab runs a GPT-2-scale model on a handful of GPUs, or simulates the collective operations on CPU, then reasons from there to what the cited papers report at frontier scale.
- Disclosed background: not yet established. The constraints in `README.md` assume `llm/transformers` as a prerequisite and access to multiple GPUs (or a CPU simulation of the collective operations), which are assumptions rather than something the learner confirmed.

## On the arc

The ten stages in `README.md` were written upfront during the planning session recorded in #133, not earned one lesson at a time. Stages 1 through 9 (lessons 0001 through 0021) are now written; only stage 10 (judgment) remains, and `learning-records/` is still empty, so nothing here has been calibrated against a demonstrated answer yet.

Stage 9's second lesson (0021) is this track's one deliberate link into `llm/evals`, per the `## Out of scope` line in `README.md`. It links the reference sheet and glossary term directly rather than a lesson, per `SKILL.md`'s linking rule, and does not restate held-out design or contamination detection beyond the one sentence needed to explain why Gopher filtered its eval benchmarks out of training.

Stage 8 turned out better sourced than `RESOURCES.md`'s original gap note expected: the OPT-175B paper's public logbook gave real failure-frequency numbers and a concrete recovery procedure, closing most of the gap. What is still missing, and noted in `RESOURCES.md`, is a primary source stating an actual checkpoint-interval policy; the checkpoint-frequency tradeoff itself is taught from general engineering reasoning rather than a cited number.

Stage 6's last lesson (0014) synthesizes a judgment call ("reach for ZeRO first, tensor/pipeline parallelism once sharding alone is not enough") from combining the ZeRO and Megatron-LM papers' own separately stated positions, rather than quoting either paper making that exact combined claim. Flagging this in case a future pass wants a single source that already makes the comparison directly, which was not found.

Stage 5 ended up as three lessons as planned (ZeRO stages 1-2, ZeRO stage 3 and FSDP, then ZeRO-R for residual memory), and used the `activation checkpointing` glossary term as a genuine prerequisite link rather than redefining it inline, which is the first lesson in this track to link the glossary that way.

Lesson 3's worked BPE example surfaced a wrinkle not called out in the mission or arc: the "merge the most frequent pair" rule does not by itself resolve a tie between equally frequent pairs, which the paper's own toy corpus happens to produce on its very first step. Worth remembering if a later lesson references "the" BPE merge order for this example, since it is implementation-dependent, not uniquely determined.

One merge is held in reserve if the arc proves too long once it is being taught: stage 4 with 5, since data parallelism and memory sharding are usually taught and decided together in practice.

**The arc table deliberately has no `Lessons` column yet, and will not until every stage has at least one lesson.** This track is being written stage by stage, one commit per stage, rather than in the single pass `llm/agents` and `llm/finetuning` used. The column requires every named stage to reference lessons that already exist, which a not-yet-reached stage cannot do, so adding it now would either drop stages 2 through 10 from the public arc table or fail the checker. `pretraining` carries an explicit `arc_lessons_column: False` entry in `CONVENTIONS` in `check-workspace.py` for exactly this reason; remove it and add the column once all ten stages have lessons.

## Open threads

- Whether the learner has access to multiple GPUs for the distributed-training reps (stages 4 through 6) is unknown. Ask before writing those stages, since a CPU-only simulation of collective operations changes what the reps can show.
- Checkpointing and fault tolerance (stage 8) is the thinnest-sourced stage; see the gap noted in `RESOURCES.md`. May need a practitioner account rather than a paper.
- Stage 1's lessons were written without an interactive session to calibrate against; nothing yet confirms they land at the right difficulty. The first real session on this track should check that before trusting the rest of the arc's pacing.
