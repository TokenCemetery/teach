---
title: The Training Loop
description: "Cross-entropy loss over the vocabulary, the backward pass and autograd, and the AdamW optimizer step, from logits to updated weights"
type: reference
---

# The Training Loop: Loss, Backward Pass, and Optimizer

Stage 4 compressed for lookup. [Lesson 9](../lessons/0009-cross-entropy-loss.md) covers turning logits into a single scalar loss; [lesson 10](../lessons/0010-backward-pass-and-autograd.md) covers turning that scalar into a gradient for every weight; [lesson 11](../lessons/0011-adamw-optimizer.md) covers turning gradients into weight updates. This sheet is the three formulas, in the order training actually uses them.

## Cross-entropy loss

```text
loss = -log(p_correct)
```

| `p_correct` | Loss | Reads as |
|---|---|---|
| 0.8 | `-log(0.8) ≈ 0.223` | Confident and right, small penalty |
| 0.1 | `-log(0.1) ≈ 2.303` | Confidently wrong, penalty over 10x larger for a 10x drop in probability |

`-log(p)` grows without bound as `p` approaches 0; a simpler `1 - p` penalty saturates at 1 and can't distinguish "somewhat wrong" from "catastrophically confident and wrong." It also has a clean gradient with respect to the logits (`softmax_output - one_hot_true_label`), which is why softmax and cross-entropy are almost always paired, often as one fused, numerically stable operation over raw logits.

**Teacher forcing.** Training always feeds the true previous tokens as context, never the model's own predictions. Because causal masking already restricts every position to attending only backward, every position's prediction, and so every position's loss, computes in one forward pass rather than one pass per position. Per-position, per-batch losses are averaged into one scalar, since gradient descent needs a single quantity to minimize.

## The backward pass and autograd

Every forward operation (matrix multiply, softmax, a residual addition) is recorded into a **computation graph**. `loss.backward()` walks it in reverse, applying the chain rule automatically using each operation's already-implemented local backward rule, populating every trainable parameter's `.grad`.

Worked chain-rule example: `y = 3x + 1`, `z = y^2`, at `x = 2`: `y = 7`, `dz/dy = 2y = 14`, `dy/dx = 3`, so `dz/dx = 14 x 3 = 42`.

| Approach | How it gets a gradient | Cost |
|---|---|---|
| Symbolic differentiation | Derives a closed-form formula by hand or via computer algebra | Not what autograd does |
| Numerical differentiation | Perturbs each parameter, re-runs the forward pass | Imprecise, one extra forward pass per parameter |
| Automatic differentiation (autograd) | Chains each operation's already-implemented local backward rule over the recorded graph | Exact, one backward traversal for every parameter at once |

**Why residuals actually prevent vanishing gradients.** For `y = x + Sublayer(x)`, `d(loss)/d(x) = d(loss)/d(y) x 1 + [a term through Sublayer]`. The identity path's local derivative is exactly 1, so the direct term passes through unscaled no matter how small `Sublayer`'s own derivative gets. This is the mechanical reason, not just an intuition.

**Gradients accumulate, they don't overwrite.** `.grad` adds into whatever was already there, so a training loop must explicitly zero gradients before each new `backward()` call, or a step's gradient is contaminated by the previous step's leftovers.

## The AdamW optimizer step

```text
plain gradient descent:  w = w - lr * grad
Adam's moments:           m = beta1 * m + (1 - beta1) * grad          (momentum)
                          v = beta2 * v + (1 - beta2) * grad^2        (adaptive scale)
Adam's update:            w = w - lr * m_hat / (sqrt(v_hat) + eps)
AdamW's update:           w = w - lr * (m_hat / (sqrt(v_hat) + eps) + weight_decay * w)
```

(`m_hat`, `v_hat` are `m`, `v` with bias correction for both starting at zero.)

| Piece | Adds | Fixes |
|---|---|---|
| Momentum (`m`) | A running average of past gradients | Noisy per-batch gradients; the update follows a consistent direction rather than jittering |
| Adaptive scale (`v`) | A per-parameter typical-gradient-magnitude estimate | One fixed learning rate for every weight; small-gradient parameters get relatively larger steps, large-gradient ones smaller |
| Decoupled weight decay (AdamW) | Weight decay applied directly to `w`, never passed through `m`, `v`, or the adaptive denominator | Folding decay into the gradient (original Adam) makes its effective shrinkage depend on each parameter's typical gradient magnitude, instead of the uniform shrinkage decay is supposed to be |

Worked example: `w = 5.0`, `grad = 2.0`, `lr = 0.1`, plain gradient descent: `w = 5.0 - 0.1 x 2.0 = 4.8`.

## Before trusting a training loop implementation

- [ ] Cross-entropy takes raw logits directly (a fused softmax + negative-log-probability operation), not a manual softmax followed by a separate log step.
- [ ] Training feeds ground-truth previous tokens (teacher forcing), and the loss is computed for every position in one forward pass, not one pass per position.
- [ ] Gradients are explicitly zeroed before each `backward()` call.
- [ ] The optimizer is AdamW, not plain Adam, if weight decay is in use, and weight decay is applied directly to the weights, not folded into the gradient.

## Sources

- [Docs: "torch.nn.functional.cross_entropy", PyTorch](https://pytorch.org/docs/stable/generated/torch.nn.functional.cross_entropy.html)
- [Docs: "Autograd mechanics", PyTorch](https://pytorch.org/docs/stable/notes/autograd.html)
- [Paper: "Decoupled Weight Decay Regularization", Loshchilov and Hutter, 2019](https://arxiv.org/abs/1711.05101)
- [Paper: "Adam: A Method for Stochastic Optimization", Kingma and Ba, 2015](https://arxiv.org/abs/1412.6980)
- [Resources](../RESOURCES.md)
