# Adapter Fine-Tuning Glossary

Canonical terms for this workspace. A term lands here once it can be used correctly, not when it is first mentioned — so this grows as lessons are earned.

## Usage in this workspace

Three words are used loosely across the field in ways that would make later lessons ambiguous, so they are pinned from the start:

**Fine-tuning**:
Training a small set of added or selected parameters on a task while the base model's weights stay frozen. When all weights are trained instead, this workspace always says *full fine-tuning* explicitly.
_Avoid_: training, retraining, teaching the model

**Adapter**:
The small set of trainable weights added alongside a frozen base model, together with the configuration describing where they attach.
_Avoid_: fine-tune (as a noun), LoRA (when the method is not specifically LoRA), checkpoint

**Quantisation**:
Storing weights at lower numeric precision than they were trained in. In this workspace it always refers to the *frozen base* unless stated otherwise — adapters stay at higher precision, and quantisation for inference is a separate concern.
_Avoid_: compression, shrinking, optimisation

## Terms

_Added as lessons establish them._
