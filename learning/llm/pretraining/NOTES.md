# LLM Pretraining Notes

Working notes for the teaching session. Not linked from `README.md`.

## Preferences

- **Framework-adjacent, not framework-agnostic.** Chosen deliberately over the pseudocode approach `llm/agents` uses. The reasoning is in #133: distributed-training techniques (ZeRO, tensor and pipeline parallelism) are stable enough, and specific enough in their APIs, that naming the real library is more useful than hiding behind pseudocode.
- Small-scale reps by design: no lesson trains a frontier-scale model. A lab runs a GPT-2-scale model on a handful of GPUs, or simulates the collective operations on CPU, then reasons from there to what the cited papers report at frontier scale.
- Disclosed background: not yet established. The constraints in `README.md` assume `llm/transformers` as a prerequisite and access to multiple GPUs (or a CPU simulation of the collective operations), which are assumptions rather than something the learner confirmed.

## On the arc

The ten stages in `README.md` were written upfront during the planning session recorded in #133, not earned one lesson at a time. Stages 1 through 4 (lessons 0001 through 0008) are now written; the remaining six stages are not, and `learning-records/` is still empty, so nothing here has been calibrated against a demonstrated answer yet.

Lesson 3's worked BPE example surfaced a wrinkle not called out in the mission or arc: the "merge the most frequent pair" rule does not by itself resolve a tie between equally frequent pairs, which the paper's own toy corpus happens to produce on its very first step. Worth remembering if a later lesson references "the" BPE merge order for this example, since it is implementation-dependent, not uniquely determined.

One merge is held in reserve if the arc proves too long once it is being taught: stage 4 with 5, since data parallelism and memory sharding are usually taught and decided together in practice.

**The arc table deliberately has no `Lessons` column yet, and will not until every stage has at least one lesson.** This track is being written stage by stage, one commit per stage, rather than in the single pass `llm/agents` and `llm/finetuning` used. The column requires every named stage to reference lessons that already exist, which a not-yet-reached stage cannot do, so adding it now would either drop stages 2 through 10 from the public arc table or fail the checker. `pretraining` carries an explicit `arc_lessons_column: False` entry in `CONVENTIONS` in `check-workspace.py` for exactly this reason; remove it and add the column once all ten stages have lessons.

## Open threads

- Whether the learner has access to multiple GPUs for the distributed-training reps (stages 4 through 6) is unknown. Ask before writing those stages, since a CPU-only simulation of collective operations changes what the reps can show.
- Checkpointing and fault tolerance (stage 8) is the thinnest-sourced stage; see the gap noted in `RESOURCES.md`. May need a practitioner account rather than a paper.
- Stage 1's lessons were written without an interactive session to calibrate against; nothing yet confirms they land at the right difficulty. The first real session on this track should check that before trusting the rest of the arc's pacing.
