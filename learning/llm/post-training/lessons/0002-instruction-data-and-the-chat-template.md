---
title: 2. Instruction Data and the Chat Template
description: A special token marks where a prompt ends and an answer begins, and that boundary has to match at training and serving time
type: lesson
---

# Lesson 2. Instruction Data and the Chat Template

**Mission link:** "Write an SFT training loop that masks loss on non-assistant tokens, and explain what breaks in a chat model trained without that mask" is the first bullet under Success looks like. This lesson covers what SFT data looks like and how its segments are marked; Lesson 3 covers the masking itself.
**Primary source:** [Paper: "Llama 2: Open Foundation and Fine-Tuned Chat Models", Touvron et al., 2023](https://arxiv.org/abs/2307.09288)
**Prerequisites:** [Lesson 1](0001-what-post-training-buys.md)

## Warm-up

1. ▢ What is an alignment tax, and what did Ouyang et al. find could partially offset it?

<details markdown="1"><summary>Check</summary>

A measured drop in performance on certain public NLP benchmarks that came with post-training's alignment gains. Mixing PPO updates with updates that increase the likelihood of the original pretraining data (PPO-ptx) recovered much of that lost performance without giving up the preference gains.

</details>

## Know this

### What SFT data actually looks like

**Supervised fine-tuning (SFT)** data is a set of prompt-and-answer pairs, exactly the shape Lesson 1's Step 1 described. Touvron et al. give real examples from Llama 2's own SFT annotation: a prompt asking for a poem about the periodic table's first ten elements, paired with an annotator-written poem that answers it; a prompt asking for a deliberately cruel "roast," paired with an annotator-written refusal explaining why. Both are simply a prompt and the exact response an annotator wants the model to learn to produce for it.

### Marking where one segment ends and the next begins

Training on this data means concatenating many prompt-and-answer pairs into the training corpus, and the model needs some way to tell where a prompt ends and its answer begins, since nothing about plain text marks that boundary on its own. Touvron et al. describe exactly this: "a special token is utilized to separate the prompt and answer segments." This is the seed of what gets called a **chat template**: a fixed, consistent way of marking role boundaries (a prompt segment, an answer segment, and in a multi-turn conversation, a system message and each successive turn) with special tokens, so the same structure appears every time in training and can be reproduced exactly at serving time.

### Why the boundary has to match at training and serving time

A chat template is not just a formatting convenience; it is part of what the model was actually trained on. The model learned to associate the special tokens marking "this is where an answer begins" with actually producing the kind of answer that followed those tokens during training. Serving the model with a different template, different special tokens, a different order of roles, or a missing system-message convention, presents it with a structure it never saw paired with the behavior it learned, and its behavior degrades or becomes unpredictable as a result. Reproducing the exact training-time template at serving time is not optional cleanup; it is part of correctly using the model at all.

### Multi-turn is the same idea, repeated

A multi-turn conversation extends this same segment-marking idea across more than one exchange: a system message (if any), then alternating user and assistant turns, each marked with the same kind of special tokens that separate any single prompt from its answer. Nothing new is invented for the multi-turn case; it is the same boundary-marking principle, applied once per turn instead of once per example.

## Practice

1. ▢ Why can a model not learn where a prompt ends and its answer begins from plain concatenated text alone, without some kind of marker?

<details markdown="1"><summary>Check</summary>

Because plain text carries no inherent signal distinguishing "this is what was asked" from "this is the answer I should learn to produce"; without a marker, the boundary between the two is not represented anywhere in the training data itself.

</details>

2. ▢ A team fine-tunes a model using one chat template, but serves it in production using a different template (different special tokens marking role boundaries). What is the most likely consequence?

    - a) No effect; the model ignores formatting entirely
    - b) The model's behavior degrades or becomes unpredictable, since it is being presented with a structure it never saw paired with the behavior it learned during training
    - c) The model automatically detects and adapts to the new template
    - d) Only the system message is affected; user and assistant turns still work normally

<details markdown="1"><summary>Check</summary>

**b)** is the actual consequence: the chat template is part of what the model was trained on, not a cosmetic wrapper, so a mismatch presents an untrained structure. (a), (c), and (d) all assume a robustness to template mismatch that training gives no reason to expect.

</details>

3. ▢ How does a multi-turn conversation's chat template relate to the single prompt-and-answer template Touvron et al. describe for SFT?

<details markdown="1"><summary>Check</summary>

It is the same segment-marking idea, applied repeatedly: a system message if present, then each user and assistant turn in sequence, each marked with the same kind of special tokens that separate a single prompt from its answer, rather than requiring a fundamentally different mechanism.

</details>

## Real-world reps

- [ ] Find the chat template for an open model you have access to (many are published as a template file or documented directly), and identify the special tokens it uses to mark a system message, a user turn, and an assistant turn.
- [ ] Read Touvron et al.'s two example SFT annotations (linked above, Table 5) and write, in your own words, what distinguishes a good SFT answer from a merely plausible-sounding one, based on the roast-refusal example.
- [ ] Tomorrow: without looking ahead, write a one-sentence prediction for Lesson 3: if a chat template concatenates a prompt and an answer into one sequence with no gap, and training uses an ordinary next-token-prediction loss on the whole sequence, what would the model start learning to do with the prompt tokens themselves that it should not?

## Going further

- [Paper: "Llama 2: Open Foundation and Fine-Tuned Chat Models", Touvron et al., 2023](https://arxiv.org/abs/2307.09288)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
