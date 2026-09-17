---
title: 23. Reviewing a Change to Model Code
description: Review someone else's change to model code and name what it breaks or costs, not trust the description
type: lesson
---

# Lesson 23. Reviewing a Change to Model Code

**Mission link:** The mission ends at reading or modifying real model code without the architecture being a black box; the senior version of that skill is reviewing someone else's change to it and naming exactly what it costs, rather than trusting the description.
**Primary source:** [Paper: "FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness", Dao et al., 2022](https://arxiv.org/abs/2205.14135), whose exactness claim (lesson 22) is this lesson's model for how to check any "faster, output unchanged" claim.
**Prerequisites:** [0001-0003](0001-scaled-dot-product-attention.md) (attention), [0004-0011](0004-positional-encoding.md) (transformer blocks and training), [0012](0012-reading-real-model-code.md) (reading real code), [0014, 0017](0014-rotary-position-embeddings.md) (modern variants), [0022](0022-mixture-of-experts-and-flashattention.md) (exactness)

## Warm-up

1. ▢ A pull request claims "replaced slow attention with fast attention, output unchanged." What do you check first before trusting that claim?

<details markdown="1"><summary>Check</summary>

Whether the output actually numerically matches the original, within floating-point tolerance. "Faster" often quietly means "different": a simplified computation or approximation that is slightly wrong. Lesson 22 made exactness the test for FlashAttention specifically because this mistake is common.

</details>

2. ▢ A diff changes the positional encoding from sinusoidal to rotary. Can you spot what the change actually costs without reading the paper?

<details markdown="1"><summary>Check</summary>

You can derive what rotary encodings do from lesson 14: they rotate query and key vectors before attention runs, which is how they achieve position-relative dot products. You can then check whether the diff implements that rotation correctly, and test whether outputs match a reference (lesson 0001's equation).

</details>

3. ▢ A change claims an ablation: "we removed the weight decay term and training still converges." What question do you ask?

<details markdown="1"><summary>Check</summary>

Did the author measure it? Is the claim backed by their own training run, or restated from a blog post's summary of a paper? An ablation claim is only as strong as the measurement behind it.

</details>

## Know this

### The review checklist: four things every model-code change needs

A reviewer who has built a transformer from raw tensors has an advantage most code reviewers lack: you can check a claim against the actual math, not just whether the code looks plausible.

**1. Do the shapes carry through correctly?**

This workspace's recurring convention: every operation preserves sequence length and embedding dimension. A change to attention (lesson 3's mask, lesson 14's RoPE, lesson 17's grouped-query) must not break that. Check:

- Input to the operation: shape `(batch, seq_len, d_model)` or components like `(batch, num_heads, seq_len, d_k)`.
- Output: same shape out.
- Two layers downstream, does a shape-breaking bug hide? A rotary embedding that rotates by the wrong angle might not fail until attention dot-products become nonsense. Check the downstream tests or run the model forward with a known input and verify intermediate shapes.

**2. If claiming a speedup, does the output numerically match?**

Lesson 22 drilled this: FlashAttention is exact, not approximate. It computes the identical equation, just by touching memory differently. It **must** produce the same `output` within floating-point tolerance.

When a diff claims faster-without-changing-output:

- Run the model with the old code and the new code on the same random input. Extract attention outputs (or the full forward pass if the diff is upstream of that).
- Compare outputs element-wise. They must match within floating-point rounding, typically 1e-5 to 1e-4 depending on the precision. If they differ more than that, the change is not a transparent speedup; it is a different computation claiming to be the same.

**3. Is the change justified against what it replaces?**

Lessons 5 (layer norm, residuals) and 19 (initialization, warmup, gradient clipping, mixed precision) are guardrails: each protects against something the training loop can fail on without it. A change to any of these must justify why the new protection is sufficient.

Examples:

- "We replaced layer norm with RMSNorm": RMSNorm drops the re-centering. Does the code show it's still used as a pre-norm (lesson 5), where centering was already optional?
- "We increased the learning rate schedule": does the change account for what the warmup, gradient clipping, and mixed precision were protecting against?
- "We removed gradient clipping": were you actually clipping before? Are you prepared to see loss spikes or training instability now?

A common mistake: copy a config value from an unrelated model and adjust nothing else. "Our model is 7B parameters; I'll use the learning rate from a 70B model I found." That rate was chosen for 70B; context, batch size, and loss curvature are all different.

The justified change either explains the old guardrail's purpose and why the new setup doesn't need it, or shows measurement that the training loop survives without it.

**4. Is an ablation claim backed by actual measurement?**

Lesson 22 again: "FlashAttention produces identical output" is a claim you can verify by comparing outputs. But "we removed weight decay and training is as good" is different: it's an experimental result claiming the removed component didn't matter.

Check:

- Is the change's author the one who measured it? Measured on what dataset, with what random seed, for how many steps?
- Or is the claim restated from a paper's summary, a blog post, or someone else's experiment? If so, does the new context (your model's size, architecture, learning rate, batch size, dataset) match the original measurement?

A real ablation is risky to accept on secondhand authority, especially if the new training run is expensive and failure is costly.

### What good judgment sounds like

When reviewing a model-code change, a senior engineer names specifically what a choice costs or risks, rather than trusting the description.

**Instead of:** "This looks wrong to me."

**Better:** "Lesson 14 derives that RoPE rotates Q and K by an angle proportional to `position * dimension_index`. This diff rotates by `position * constant`. That's a different function. The paper's relative-position property won't hold. I'd want to see outputs match a reference before merging."

**Instead of:** "It should work."

**Better:** "The change removes a `residual_scale` factor before adding residuals back. Lesson 7 showed that scaling the residual is how lesson 5's pre-norm variant avoids activation bloat in deep models. I'd want to see gradient histograms at each layer during training, or understand why this particular model stays stable without scaling."

**Instead of:** "The authors say it works."

**Better:** "This is RMSNorm, which the paper applies pre-norm. Our code uses post-norm (lesson 5). RMSNorm without re-centering might be fine pre-norm but risky post-norm. I'd want to either change to pre-norm or compare outputs carefully."

The difference: naming what the change does, what it protects against or costs, and what evidence would settle the question, rather than saying the change feels right or wrong.

## Practice

1. ▢ A diff replaces the sinusoidal positional encoding (lesson 4) with rotary (lesson 14). Your checks: what shapes must still match, and what do you test first?

<details markdown="1"><summary>Check</summary>

Shapes: input `(batch, seq_len, d_model)`, output `(batch, seq_len, d_model)`. The rotation is applied to Q and K before attention, so attention's input shapes are unchanged, and attention's output shape is still `(batch, seq_len, d_model)`.

Test first: compare attention outputs (or full forward-pass outputs if you can isolate them cleanly) between the old code and the new code on the same random input. If they match within tolerance, the change preserves the computation. If they differ, something is wrong in the rotation math.

</details>

2. ▢ A change claims "multi-head attention → grouped-query attention (lesson 17), no output difference." What's your first skeptical question?

<details markdown="1"><summary>Check</summary>

Grouped-query attention has fewer key and value heads than query heads, so the computation is genuinely different, even if it's designed to approximate multi-head's output. The claim "no output difference" is *too strong*. The right claim is "output is close enough that downstream performance doesn't suffer."

Your check: Do outputs numerically match within a tolerance you're willing to accept? Probably 1e-4 or tighter. If they match exactly, something is probably wrong (you might have left multi-head code active somewhere by accident).

</details>

3. ▢ A PR removes the learning-rate warmup (lesson 19). The author says "the model trains fine without it." What do you ask?

<details markdown="1"><summary>Check</summary>

- Did they measure it? On this model, dataset, and batch size?
- What was the learning rate before warmup kicked in? If the initial rate is lower now, the change might not actually be removing warmup's benefit.
- Did they see gradient spikes, dead layers, or unusual loss curves? Warmup prevents these. If the author didn't look, they might not have noticed.

Without measurement on your actual setup, you're guessing. Warmup is cheap; if it works, keep it.

</details>

4. ▢ Which statement about reviewing a model-code change is the most useful guideline?

    - a) Trust the author's description and focus on code style instead
    - b) Reject any change to attention or the training loop; these are too risky to modify
    - c) Compare outputs numerically when the change claims it doesn't alter output, and name the specific cost when it does
    - d) Require that every ablation result be backed by a published paper before accepting it

<details markdown="1"><summary>Check</summary>

**c)** Compare outputs numerically when the change claims it doesn't alter output, and name the specific cost when it does.

(a) is how mistakes ship. (b) is overly cautious; the whole point is to be able to judge changes carefully. (d) is too strict; a useful change might come before publication, and measurement on your actual setup is often more relevant than a paper's measurement on a different scale.

</details>

5. ▢ A diff changes RMSNorm (lesson 15) placement from post-norm to pre-norm (lesson 5). What's one thing you verify before trusting the change?

<details markdown="1"><summary>Hint</summary>

Think about what lesson 5 says each placement is for, and what RMSNorm drops compared to layer norm.

</details>

<details markdown="1"><summary>Check</summary>

Pre-norm RMSNorm works because RMSNorm only re-scales (doesn't re-center), and pre-norm doesn't need re-centering to prevent activation bloat: the residual into the next block is unbounded, but the normalization in *that* block handles it.

Post-norm is different: the residual output is unbounded, and layer norm's re-centering was partly why post-norm stayed stable. RMSNorm drops re-centering. You'd want to compare activation histograms (are they bloating?), training curves (do they show instability?), or at least run a quick test to see whether the loss curves match before and after the change.

</details>

## Real-world reps

- [ ] Next time you see a PR changing attention, positional encoding, or the training loop in a model you work on or understand, use the four-point checklist above: shapes, output exactness, justification against what it replaces, and measurement backing any ablation claim.
- [ ] On that same PR (or your own), practice writing a review comment that names specifically what a change does and what would settle the question, rather than saying it looks right or wrong.
- [ ] Tomorrow: if you modify your own model code this week (changing a layer, swapping an activation, adjusting a schedule), check whether you can verify shapes and outputs numerically before submitting. If you can't, you don't actually know whether you changed anything important or nothing at all.
- [ ] Tomorrow: Revisit a claim you've heard about attention, embeddings, or a training trick. Go to the original paper (not the blog post summary) and check whether the claim matches the paper's actual equations. Lesson 12 showed how to find real code; now use that skill and the papers in [Resources](../RESOURCES.md) to settle one disputed point.

## Going further

- [Paper: "RoFormer: Enhanced Transformer with Rotary Position Embedding"](https://arxiv.org/abs/2104.09864), Su et al. Use for: the original rotary embeddings math, to verify claims against what the paper actually says.
- [Paper: "GQA: Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints"](https://arxiv.org/abs/2305.13245), Ainslie et al. Use for: grouped-query attention's design, to check the approximation claim and understand what trade-off it makes.
- [Paper: "FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness"](https://arxiv.org/abs/2205.14135), Dao et al. Use for: confirming that FlashAttention is exact, not approximate, and seeing how they verify it against reference implementations.
- Revisit the [training loop lessons](0019-initialization-warmup-and-gradient-clipping.md) when you're reviewing changes to learning rate, gradient clipping, or mixed precision. The "Going further" sections in those lessons link to the papers behind each guardrail.
- [Glossary](../GLOSSARY.md) for any term that felt slippery.
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
