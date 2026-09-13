# LLM Pretraining Notes

Working notes for the teaching session. Not linked from `README.md`.

## Preferences

- **Framework-adjacent, not framework-agnostic.** Chosen deliberately over the pseudocode approach `llm/agents` uses. The reasoning is in #133: distributed-training techniques (ZeRO, tensor and pipeline parallelism) are stable enough, and specific enough in their APIs, that naming the real library is more useful than hiding behind pseudocode.
- Small-scale reps by design: no lesson trains a frontier-scale model. A lab runs a GPT-2-scale model on a handful of GPUs, or simulates the collective operations on CPU, then reasons from there to what the cited papers report at frontier scale.
- Disclosed background: not yet established. The constraints in `README.md` assume `llm/transformers` as a prerequisite and access to multiple GPUs (or a CPU simulation of the collective operations), which are assumptions rather than something the learner confirmed.

## On the arc

The ten stages in `README.md` were written upfront during the planning session recorded in #133, not earned one lesson at a time. No lesson exists yet and `learning-records/` is empty, so nothing here has been calibrated against a demonstrated answer.

One merge is held in reserve if the arc proves too long once it is being taught: stage 4 with 5, since data parallelism and memory sharding are usually taught and decided together in practice.

The arc table has no `Lessons` column yet, because there are no lessons for it to name. Add the column with the first lesson, not later: `check-workspace.py` requires it once `lessons/` exists.

## Open threads

- Whether the learner has access to multiple GPUs for the distributed-training reps (stages 4 through 6) is unknown. Ask before writing those stages, since a CPU-only simulation of collective operations changes what the reps can show.
- Checkpointing and fault tolerance (stage 8) is the thinnest-sourced stage; see the gap noted in `RESOURCES.md`. May need a practitioner account rather than a paper.
- Nothing has been attempted yet. The first interactive session should calibrate before teaching forward, rather than assuming the written arc landed as planned.
