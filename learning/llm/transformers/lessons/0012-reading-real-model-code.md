---
title: 12. Reading Real Model Code
description: Where each derived piece lives in a production model library, and the small, common deviations from the original paper worth recognizing rather than being confused by
type: lesson
---

# Lesson 12. Reading Real Model Code

**Mission link:** Stage 5 is the final leg: everything derived from raw tensors in stages 1 to 4 exists inside real, production code, under different names and with a handful of small, standard deviations from the original paper, and this lesson is how to translate between what was built here and what's actually running in practice.
**Primary source:** [Repo: transformers, Hugging Face](https://github.com/huggingface/transformers)
**Prerequisites:** [Lesson 11](0011-adamw-optimizer.md), [Scaled dot-product attention](../GLOSSARY.md)

## Warm-up

1. ▢ What goes wrong with folding weight decay into the gradient in original Adam, and what does AdamW do differently?

<details markdown="1"><summary>Check</summary>

Folded into the gradient, weight decay gets divided by the adaptive scaling term along with everything else, so its effective shrinkage varies by parameter instead of applying uniformly. AdamW applies weight decay directly to the weights, added to the update separately from the gradient-based term.

</details>

2. ▢ Are the weights in one transformer block the same as the weights in another block in the stack? What does that cost and buy?

<details markdown="1"><summary>Check</summary>

No, each block has its own independently learned parameters, costing parameter count roughly linearly with depth but letting different blocks specialize differently rather than being forced to compute an identical transformation at every depth.

</details>

## Know this

### The same pieces, under different names

A GPT-2-style model in Hugging Face's `transformers` library implements everything this workspace derived, just under its own naming conventions. Attention lives in a class like `GPT2Attention`, computing the same scaled dot-product operation from lesson 1, often via one fused linear layer producing Q, K, and V concatenated together, then split apart, a batched-matmul efficiency detail, not a different operation than lesson 2's separate per-head projections. Causal masking (lesson 3) shows up as a precomputed, registered buffer holding a lower-triangular mask, applied to the attention scores before softmax exactly as derived, rather than being rebuilt from scratch on every forward call: since the mask depends only on sequence length, not on the actual input values, computing it once and reusing (or slicing) it is a pure efficiency choice with no change to the mechanism itself. Token and position embeddings appear as `wte` (word token embedding) and `wpe` (word position embedding) tables (lessons 4 and 8); the stacked blocks live in a `ModuleList` iterated over in a for loop in the model's forward method, matching lesson 7 directly; and the output projection is a linear layer, commonly named `lm_head`, tied to `wte`'s weights via an explicit assignment or a `tie_weights()` call, exactly lesson 8's weight tying.

![A two-column mapping. On the left, five pieces derived in this workspace: lessons 1 and 2's attention, lesson 3's causal mask, lesson 4's positional encoding, lesson 7's stacked blocks, and lesson 8's embedding and weight tying. On the right, the corresponding name each takes in Hugging Face's transformers library: GPT2Attention with a fused query-key-value projection, a registered lower-triangular buffer, a learned wpe position table, a ModuleList of blocks iterated in a for loop, and wte tied to lm_head. A line connects each left-hand concept to its right-hand real-code name.](images/workspace-to-real-code-mapping.svg)

### Three small, standard deviations from the original paper

Nearly every modern production model departs from the original paper in the same few small ways, and recognizing them as implementations of concepts already covered, not something new, is the point of this lesson. **Position embedding**: many models use a learned position table (lesson 4's alternative to sinusoidal encoding) or rotary embeddings, rather than the original paper's sinusoidal formula. **Activation function**: the feed-forward block (lesson 6) commonly uses GELU instead of the original paper's ReLU, the same expand-then-contract shape, a different nonlinearity. **Norm placement**: most current models use pre-norm (lesson 5's alternative), placing layer norm before each sublayer inside the residual branch, rather than the original paper's post-norm. None of these change the underlying architecture this workspace derived; they're the standard variations found across nearly every real implementation.

### Training code lives outside the model class

The pieces from stage 4, the cross-entropy loss call, `loss.backward()`, and the optimizer step, aren't part of the model's own class at all; they live in the training script or a training utility (such as Hugging Face's `Trainer`, or a custom loop like nanoGPT's). The model class defines the forward pass that produces logits; everything about turning those logits into a trained model lives one layer up, in the code that calls the model repeatedly and applies stage 4's machinery around it.

### A different codebase, the same mathematical objects

llama.cpp, built in C rather than Python and PyTorch, expresses the same operations, attention, positional encoding (commonly rotary), normalization (commonly RMSNorm, a simplified variant of lesson 5's layer norm), and a feed-forward block (commonly with a SwiGLU activation), not as `nn.Module` classes with a `forward` method, but as explicit calls building a computation graph in `ggml`, the tensor library underneath it. The graph-building calls and the class-and-forward-method style look nothing alike on the page, but they compute the identical mathematical objects this workspace derived from raw tensors; the difference is entirely in how the computation graph gets constructed and run, not in what it computes.

## Practice

1. ▢ Match each of these real-code names to the lesson that derived the concept it implements: `wte`, `wpe`, a registered lower-triangular mask buffer, `lm_head` tied to `wte`'s weights, a `ModuleList` of blocks.

<details markdown="1"><summary>Check</summary>

`wte` (word token embedding): lesson 8's input embedding. `wpe` (word position embedding): lesson 4's positional encoding (here, a learned table rather than sinusoidal). The registered mask buffer: lesson 3's causal masking. `lm_head` tied to `wte`: lesson 8's weight tying. The `ModuleList` of blocks: lesson 7's stacking.

</details>

2. ▢ Name the three common small deviations from the original paper found in most modern real implementations, and which lesson's alternative each one corresponds to.

<details markdown="1"><summary>Check</summary>

Learned or rotary position embeddings instead of sinusoidal (lesson 4's learned alternative, or a further variant like rotary). GELU instead of ReLU in the feed-forward block (lesson 6's nonlinearity, swapped for a different function, same expand-then-contract shape). Pre-norm instead of post-norm placement (lesson 5's pre-norm alternative to the original paper's choice).

</details>

3. ▢ Why does the causal mask appear in real code as a precomputed, registered buffer rather than being rebuilt on every forward call?

<details markdown="1"><summary>Hint</summary>

Consider what the mask actually depends on.

</details>

<details markdown="1"><summary>Check</summary>

The mask depends only on sequence length, never on the actual input values, so it can be computed once (commonly at the maximum sequence length the model supports) and reused or sliced on every forward call, rather than reconstructed from scratch each time. This is a pure efficiency choice; the masking mechanism itself, added to scores before softmax, is unchanged from lesson 3.

</details>

4. ▢ How does llama.cpp's approach to computing attention and the feed-forward block differ mechanically from a PyTorch `nn.Module`'s forward pass, while still computing the same underlying mathematical operations?

<details markdown="1"><summary>Check</summary>

llama.cpp builds an explicit computation graph in `ggml` through function calls in C, rather than defining a class with a `forward` method that PyTorch traces automatically as it runs. The graph-construction style looks entirely different on the page, but the operations it builds, attention, positional encoding, normalization, the feed-forward block, are the same mathematical objects this workspace derived from raw tensors.

</details>

5. ▢ Which claim is true of reading a real model's code after deriving the architecture from scratch?

    - a) Real production models implement an entirely different architecture than what the original paper and this workspace derive
    - b) The same pieces appear under different names, with a handful of small, standard deviations (position embedding scheme, activation function, norm placement) worth recognizing rather than treating as new
    - c) Training code (loss, backward pass, optimizer) is always part of the model's own class definition
    - d) llama.cpp computes fundamentally different mathematical operations than a PyTorch implementation, since it's written in C

<details markdown="1"><summary>Check</summary>

**b)** That's exactly the translation this lesson teaches. (a) is false: the underlying architecture is the same, just named and configured differently. (c) is false: training code lives in a separate training script or utility, not inside the model class itself. (d) is false: the operations are mathematically identical; only how the computation graph is built and expressed differs.

</details>

## Real-world reps

- [ ] Open a GPT-2-style model's implementation in the `transformers` library and find its attention class, its causal mask, and its `wte`/`wpe`/`lm_head` naming, matching each to the lesson that derived it.
- [ ] Check whether that same model uses pre-norm or post-norm, and GELU or ReLU, and note which is which against this lesson's list of common deviations.
- [ ] Tomorrow: find the training script (or `Trainer` usage) for a model you have access to, and locate its loss computation, `.backward()` call, and optimizer step.

## Going further

- [Repo: transformers, Hugging Face](https://github.com/huggingface/transformers)
- [Repo: nanoGPT, Karpathy](https://github.com/karpathy/nanoGPT)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
