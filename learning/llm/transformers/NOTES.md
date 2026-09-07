# Transformers Notes

Working notes for the teaching session. Not linked from `README.md`.

## Preferences

- Interview recorded in #35. The outcome was not narrowed: both building the architecture from scratch and being able to read real model code afterward.
- **PyTorch with raw tensor operations, asked for explicitly.** No `nn.Transformer` or other pre-built attention modules, but autograd and GPU support are kept: only the architecture is hand-built, not the framework. A lesson that reaches for a pre-built module has given away the thing being learned.
- The basic training loop was pulled in rather than deferred, so the reader can see the block actually train. Optimizer and scheduler variants, distributed training and adapter machinery stay with `llm/finetuning`.
- Mathematics to assume: matrix multiplication, and nothing beyond it taken for granted. The linear algebra has to be derived, not referenced.

## On the arc

The five stages and their thirteen lessons are public, in `README.md`. What belongs here is the caveat on them: the arc was written upfront across successive runs, not one lesson per interactive session, and `learning-records/` is empty. So nothing in this workspace has been calibrated against a demonstrated answer, and every practice item's difficulty is guessed.

## Open threads

- Nothing has been attempted yet. The first interactive session should calibrate before teaching forward: take a practice item from an early lesson and check whether the level is right, rather than assuming the written arc landed.
- This is the workspace where a wrong calibration would show up soonest, because the material is derivation rather than API surface. The mathematics is either at the right level or it is useless, and only a real answer will say which.
