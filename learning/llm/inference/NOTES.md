# Inference Notes

Working notes for the teaching session. Not linked from `README.md`.

## Preferences

- Interview recorded in #32, answered partly in the issue and partly in chat. Success was defined as both halves, not either: stand up a serving stack for a real model, and quote and defend a latency budget from the KV cache, batching and quantization choices behind it.
- **The two stacks have an order, and it was the learner's: vLLM on GPU first, then llama.cpp for CPU and edge.** Other stacks are mentioned only where a concept transfers differently, so do not let TGI or TensorRT-LLM grow into coverage of their own.
- Disclosed background: comfortable running a Python ML environment, no serving-infrastructure experience. So infrastructure vocabulary needs introducing, Python does not.

## On the arc

The six stages and their seventeen lessons are public, in `README.md`. What belongs here is the caveat on them: the arc was written upfront across successive runs, not one lesson per interactive session, and `learning-records/` is empty. So nothing in this workspace has been calibrated against a demonstrated answer, and every practice item's difficulty is guessed.

## Open threads

- Nothing has been attempted yet. The first interactive session should calibrate before teaching forward: take a practice item from an early lesson and check whether the level is right, rather than assuming the written arc landed.
- The mission's first success criterion is standing up a serving stack, which no answer key can verify. Whether that gets checked by a real deployment or stays a judgment question in the arc is not settled.
