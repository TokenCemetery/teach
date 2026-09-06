---
title: 9. Cross-Entropy Loss Over the Vocabulary
description: How logits become one trainable number, and why the loss is the negative log probability of the actual next token
type: lesson
---

# Lesson 9. Cross-Entropy Loss Over the Vocabulary

**Mission link:** Stage 4 opens the training loop: the full forward pass (stages 1 to 3) produces logits, and this lesson turns those logits into the single scalar number training actually improves the model against.
**Primary source:** [Docs: "torch.nn.functional.cross_entropy", PyTorch](https://pytorch.org/docs/stable/generated/torch.nn.functional.cross_entropy.html)
**Prerequisites:** [Lesson 8](0008-embedding-output-and-weight-tying.md), [Scaled dot-product attention](../GLOSSARY.md)

## Warm-up

1. ▢ Why can the input embedding and output layers share a single weight matrix (weight tying), rather than needing two separate ones?

<details markdown="1"><summary>Check</summary>

Their shapes are transposes of each other (`vocab_size × d_model` versus `d_model × vocab_size`), and both layers relate a token to the same underlying representation, one as a lookup, the other as a projection, which is what makes reusing one matrix for both a sensible choice, not just a shape coincidence.

</details>

2. ▢ How does causal masking restrict what a query position can attend to?

<details markdown="1"><summary>Check</summary>

A query at position *i* can only attend to key positions 0 through *i*; positions later than *i* are masked with a large negative score before softmax, driving their contribution to effectively zero.

</details>

## Know this

### From logits to a probability, from a probability to a loss

Lesson 8's output layer produces a `vocab_size`-length logit vector at every position, one raw score per possible next token. Softmax turns those logits into a proper probability distribution. Training then needs a single number measuring how wrong that distribution was, given what the actual next token in the training data turned out to be: **cross-entropy loss** is that number, computed as the negative log of the probability the model assigned to the actual correct token: `loss = -log(p_correct)`.

### Why negative log probability specifically

A perfect prediction, probability 1 for the correct token, gives a loss of exactly 0. As the assigned probability for the correct token shrinks toward 0, `-log(p)` grows without bound, an unboundedly increasing penalty for a confidently wrong prediction. Compare `p = 0.8` for the correct token, giving `-log(0.8) ≈ 0.223`, against `p = 0.1`, giving `-log(0.1) ≈ 2.303`: the loss grows sharply, not just linearly, as the model's confidence moves further from the truth. A simpler-looking alternative like `1 - p` doesn't have this property: it saturates at 1 no matter how confidently wrong the model is, giving no extra signal to distinguish "somewhat wrong" from "catastrophically, confidently wrong." Cross-entropy also has a clean gradient with respect to the logits, `softmax_output - one_hot_true_label`, a simple, numerically well-behaved expression that backpropagation (next lesson) can use directly, which is part of why softmax and cross-entropy are almost always paired together and often implemented as one fused, numerically stable operation taking raw logits directly, rather than a separate softmax step followed by a log.

### Teacher forcing: every position's loss, computed in one pass

During training, the model predicts the token at position *i+1* using only positions 0 through *i*, exactly what causal masking (lesson 3) already enforces. Because causal masking lets every position's prediction be computed simultaneously in a single forward pass, the loss at every position in the sequence, comparing that position's predicted distribution against the actual next token from the training data, can also be computed in that same single pass. This is **teacher forcing**: training always feeds the true, ground-truth previous tokens as context, never the model's own possibly-wrong past predictions, which is different from generation, where the model necessarily conditions on its own previously generated tokens instead.

### One scalar for the whole batch

Each position produces its own cross-entropy loss value; these are averaged across every position in the sequence and across every sequence in the batch, collapsing down to one single scalar number. A single scalar is what the backward pass (next lesson) needs: gradient descent updates weights with respect to one number to minimize, not a whole tensor of separate loss values, so the averaging step is what turns "how wrong was every prediction across an entire batch" into the one quantity training actually optimizes.

## Practice

1. ▢ The model assigns probability 0.8 to the correct next token in one case, and 0.1 in another. Compute the cross-entropy loss for each, and describe how the loss changes as the assigned probability for the correct token drops.

<details markdown="1"><summary>Hint</summary>

`loss = -log(p)`.

</details>

<details markdown="1"><summary>Check</summary>

`-log(0.8) ≈ 0.223`; `-log(0.1) ≈ 2.303`. The loss doesn't grow linearly as the correct probability drops; it grows sharply, over ten times larger for a tenfold drop in assigned probability, penalizing confident wrongness far more severely than a merely uncertain prediction.

</details>

2. ▢ Why does cross-entropy use `-log(p)` as its penalty rather than something like `1 - p`?

<details markdown="1"><summary>Check</summary>

`-log(p)` grows without bound as `p` approaches 0, giving an unboundedly increasing penalty for a confidently wrong prediction. `1 - p` saturates at 1 regardless of how close to 0 the assigned probability gets, so it can't distinguish a merely wrong prediction from a catastrophically confident one the way `-log(p)` can.

</details>

3. ▢ How does causal masking (lesson 3) make it possible to compute the training loss for every position in a sequence using a single forward pass, rather than one pass per position?

<details markdown="1"><summary>Check</summary>

Causal masking already restricts each position to attending only to earlier positions, which is exactly the constraint that predicting position *i+1* from positions 0 through *i* requires. Because every position's masked attention computation can run simultaneously in one pass, every position's predicted distribution, and so every position's loss against the true next token, can also be computed together in that same single pass, rather than needing a separate pass per position.

</details>

4. ▢ Why does training need the per-position, per-batch losses averaged down to a single scalar, rather than working with the full tensor of individual loss values directly?

<details markdown="1"><summary>Check</summary>

Gradient descent updates the model's weights to minimize one quantity; the backward pass needs a single scalar to compute gradients with respect to, not a whole tensor of separate values. Averaging collapses "how wrong was every prediction across the batch" into that one number training actually optimizes.

</details>

5. ▢ Which claim is true of teacher forcing during training?

   - a) The model conditions each prediction on its own previously generated tokens, the same way it does during inference
   - b) The model conditions each position's prediction on the true, ground-truth previous tokens from the training data, not on its own predictions
   - c) Teacher forcing requires a separate forward pass for each position in the sequence
   - d) Teacher forcing and causal masking address unrelated problems with no connection to each other

<details markdown="1"><summary>Check</summary>

**b)** That's exactly what teacher forcing means, and it's what distinguishes training from generation. (a) is false: that describes inference, not training under teacher forcing. (c) is false: causal masking is precisely what lets every position be computed in one pass. (d) is false: causal masking's per-position restriction is what makes computing every position's teacher-forced loss in a single pass possible at all.

</details>

## Real-world reps

- [ ] Implement cross-entropy loss from raw operations (softmax, then negative log of the correct token's probability) for a small example, and confirm it matches PyTorch's `F.cross_entropy` on the same logits and target.
- [ ] For a training sequence, compute the per-position loss for each position by hand from a small set of made-up logits, then average them into a single scalar.
- [ ] Tomorrow: read the PyTorch `cross_entropy` docs and note why it takes raw logits rather than requiring you to call softmax yourself first.

## Going further

- [Docs: "torch.nn.functional.cross_entropy", PyTorch](https://pytorch.org/docs/stable/generated/torch.nn.functional.cross_entropy.html)
- [Repo: nanoGPT, Karpathy](https://github.com/karpathy/nanoGPT)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
