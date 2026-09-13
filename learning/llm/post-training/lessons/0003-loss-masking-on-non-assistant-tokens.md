---
title: 3. Loss Masking on Non-Assistant Tokens
description: Zero out the loss on the prompt, or spend gradient signal teaching the model to predict text it did not generate
type: lesson
---

# Lesson 3. Loss Masking on Non-Assistant Tokens

**Mission link:** "Write an SFT training loop that masks loss on non-assistant tokens, and explain what breaks in a chat model trained without that mask" is the first bullet under Success looks like, and this lesson is where it is answered directly.
**Primary source:** [Paper: "Llama 2: Open Foundation and Fine-Tuned Chat Models", Touvron et al., 2023](https://arxiv.org/abs/2307.09288)
**Prerequisites:** [Lesson 2](0002-instruction-data-and-the-chat-template.md), [Loss masking](../GLOSSARY.md)

## Warm-up

1. ▢ What is a chat template, and why does it matter that the same one is used at both training and serving time?

<details markdown="1"><summary>Check</summary>

A fixed, consistent way of marking role boundaries (system, user, assistant turns) with special tokens, so the model can learn a structure it will reliably see again. A mismatch between training and serving templates presents the model with a structure it never saw paired with the behavior it learned, degrading or destabilizing its behavior.

</details>

2. ▢ Per Touvron et al., what special token do they use to separate a prompt from its answer in SFT training data?

<details markdown="1"><summary>Check</summary>

A dedicated special token inserted specifically to mark the boundary between the prompt segment and the answer segment.

</details>

## Know this

### The plain, unmasked version of this loss would be wrong

An ordinary language-modeling loss trains a model to predict the next token at every position in a sequence, compared against what the sequence actually contains there. Applied naively to a concatenated prompt-and-answer example, with no adjustment, this would train the model to predict the prompt's own tokens too, not just the answer's, since the prompt is part of the sequence exactly like the answer is.

### What Touvron et al. actually do instead

Touvron et al. state their approach directly: "we utilize an autoregressive objective and zero-out the loss on tokens from the user prompt, so as a result, we backpropagate only on answer tokens." This is **loss masking**: every token belonging to the prompt (or, in a multi-turn example, to any user or system turn) has its contribution to the loss set to zero, so only the tokens the model is actually meant to generate, the assistant's answer, produce a gradient. Mechanically, this is usually implemented by giving every masked position a label value a loss function is told to ignore (a common convention sets it to `-100` for a standard cross-entropy loss), rather than the token that actually appears there.

### What breaks without it

Skipping this masking does not simply waste a little compute; it changes what the model is actually being trained to do. Two concrete problems follow directly:

- **The model learns to predict text it did not generate and will never need to reproduce.** Nothing about training a model to predict a user's own prompt back to itself serves the goal of SFT, which is shaping what the model produces as an answer, not what it can regurgitate of the question.
- **Prompts are frequently much longer than the answers that follow them.** An unmasked loss is dominated by however many prompt tokens there are, diluting the gradient signal on the answer tokens, the only part of the sequence SFT is actually trying to shape, with a large amount of loss spent on a task (predicting the prompt) that was never the point.

### The result: masking concentrates the objective on the thing being taught

Masking every non-assistant token does the opposite of both problems: every unit of gradient signal in an SFT step comes from tokens the model is actually meant to learn to produce, none of it spent predicting text the model was simply given. This is what makes SFT teach the specific skill it is meant to teach, imitating the desired answer, rather than a mixture of that skill and an unrelated one (predicting arbitrary user text) that happens to share the same training sequence.

## Practice

1. ▢ A training example concatenates a 200-token prompt and a 20-token answer, with no loss masking applied. Roughly what fraction of the total loss for this example comes from tokens that are not the actual target of SFT?

<details markdown="1"><summary>Check</summary>

Roughly 200 out of 220 tokens, about 91%, would be prompt tokens contributing loss that has nothing to do with the answer SFT is trying to teach the model to produce. Only about 9% of the unmasked loss would come from the answer itself.

</details>

2. ▢ Which of these best describes what loss masking actually does, mechanically?

    - a) It removes the prompt tokens from the input sequence entirely
    - b) It gives each masked token's position a label the loss function is told to ignore, so only unmasked (assistant) positions contribute a gradient
    - c) It reduces the learning rate specifically when processing prompt tokens
    - d) It trains a separate model just for the prompt tokens

<details markdown="1"><summary>Check</summary>

**b)** is the actual mechanism: the prompt tokens are still present as input, so the model can condition its answer on them, but their positions are excluded from the loss computation itself. (a) would remove information the model needs to condition its answer on. (c) and (d) do not describe any technique this lesson or its source describes.

</details>

3. ▢ A model trained without loss masking on non-assistant tokens is compared to one trained with it, on the exact same SFT data. Name one concrete way you would expect the unmasked model's SFT training to have gone differently.

<details markdown="1"><summary>Check</summary>

Any reasonable version of: gradient signal was diluted by, or spent on, learning to predict prompt tokens rather than concentrated entirely on the answer tokens, so for the same number of training steps, less of the model's learning was actually shaping its answer-generation behavior, the one thing SFT is meant to teach.

</details>

## Real-world reps

- [ ] Find where a training framework you have access to implements loss masking for chat-style SFT data (an `ignore_index`, a `labels` field with masked positions, or similar), and confirm which convention it uses to mark a masked position.
- [ ] Take a short example conversation (a system message, a user turn, an assistant turn) and mark, token by token or segment by segment, which parts would be masked and which would contribute to the loss, per this lesson's rule.
- [ ] Tomorrow: for a multi-turn conversation with two user turns and two assistant turns, write out which turns get masked and which do not, and check your answer against this lesson's rule that every non-assistant turn is masked, not just the first prompt.

## Going further

- [Paper: "Llama 2: Open Foundation and Fine-Tuned Chat Models", Touvron et al., 2023](https://arxiv.org/abs/2307.09288)
- [Documentation: "TRL - Transformer Reinforcement Learning", Hugging Face](https://huggingface.co/docs/trl/index)
- [Resources](../RESOURCES.md)

---

Stage 2 covered imitating a demonstrated answer directly. Stage 3 turns to a different kind of signal: not what the answer should be, but which of two answers a human preferred.

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
