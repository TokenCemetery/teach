---
title: 24. Reviewing Someone Else's Training Run Config
description: Walk the plan through every stage this track covered, in order, and settle a disputed claim from the source rather than a blog post
type: lesson
---

# Lesson 24. Reviewing Someone Else's Training Run Config

**Mission link:** This closes the arc. Every earlier stage produced one thing to check in someone else's plan; this lesson is the checklist, plus the discipline of settling a disputed technical claim from a primary source instead of trusting whichever secondary account is more convenient.
**Primary source:** [Paper: "Training Compute-Optimal Large Language Models", Hoffmann et al., 2022](https://arxiv.org/abs/2203.15556)
**Prerequisites:** every previous lesson in this track, since this one is the synthesis.

## Warm-up

1. ▢ Name the four categories of claim Lesson 23 says a defensible pretraining plan should be broken into.

<details markdown="1"><summary>Check</summary>

The token-to-parameter ratio, the data pipeline, the parallelism plan matched to the hardware's interconnect, and the stability and monitoring plan.

</details>

2. ▢ Per Lesson 22, name one legitimate reason to pretrain from scratch rather than adapt an existing model.

<details markdown="1"><summary>Check</summary>

Any one of: the target language or domain is so far outside every available base model's coverage that adaptation cannot close the gap, a licensing or provenance requirement rules out every available base model, or a deliberate architectural change an existing checkpoint cannot be adapted into.

</details>

## Know this

### The review checklist: stages in order

When reviewing a proposed or existing pretraining plan, walk it through the stages of this track in order, asking the same question at each one: is this choice stated and justified, or merely assumed?

**Stages 1 and 2, data and tokenizer.** Is the corpus's sourcing and mixing an explicit, defended decision (Lesson 1), with deduplication and quality filtering actually applied and described (Lesson 2), rather than "whatever we could scrape"? Is the tokenizer's vocabulary size a stated choice weighed against sequence length and embedding-table cost (Lesson 4), rather than a default carried over from an unrelated project?

**Stage 3, the ratio.** Compute the plan's tokens-per-parameter ratio directly and compare it to the roughly-20-to-25 range Lesson 6 grounded in Chinchilla's own results. A plan far outside that range, in either direction, is not automatically wrong, but it is a claim that needs its own stated reason, the same test Lesson 23 applied.

**Stages 4 through 6, parallelism.** Does the sharding strategy (ZeRO stage, or an equivalent) match the actual memory the model needs, per Lesson 8's per-parameter accounting? Does any tensor-parallel split stay within a single node's fast interconnect, and does pipeline parallelism carry the load of spanning nodes, per Lesson 14's own reasoning, rather than the reverse?

**Stages 7 through 9, running it.** Does the plan state a precision choice and, if using bf16 parameters, whether stochastic rounding or an fp32 master copy is used (Lesson 15)? Does it state a gradient-clipping value, and does that value tighten for the largest models the plan trains, the way Gopher's own did (Lesson 16)? Does it state a checkpoint frequency defensible against the failure rate Stage 8's evidence showed is normal, not exceptional, at this scale (Lesson 18)? Does it include periodic held-out evaluation, not just training loss, as a way to catch trouble early (Lesson 21)?

**Stage 10, the decision itself.** Does the plan explain why continued pretraining or fine-tuning an existing model would not have served the stated goal (Lesson 22), before defending the from-scratch budget on its own terms (Lesson 23)?

A plan that answers all of these with a stated, defensible choice is a plan that has done the work this track describes. A plan that answers several of them with silence has not, whatever its final cost estimate looks like.

### Settling a disputed claim from the source, not from a blog post

A specific, common confusion is worth walking through directly, because it shows the discipline this lesson is really about. It is sometimes claimed online that "bf16 requires loss scaling, the same as fp16." This is stated confidently in enough secondary sources that it can sound settled. But Lesson 15 traced why bf16 keeps fp32's full 8 exponent bits, giving it the same dynamic range as fp32; loss scaling (multiplying values up before storing them in a narrow-range format, and back down before the update, to avoid underflow) is specifically a mitigation for fp16's narrower 5-bit exponent range, the exact problem bf16's wider range was built to avoid in the first place. Rae et al.'s own account of Gopher's training does not describe loss scaling for their bf16 activations at all; the numerical concern they do describe and address for bf16 is stochastic rounding for parameter updates, a different problem (precision, not range) with a different fix. A secondary source repeating "bf16 needs loss scaling too" is conflating two different formats' two different problems; going back to what a primary source actually describes each format needing, rather than trusting a confident restatement, is what catches that conflation. This is the habit worth carrying out of this track: when two accounts disagree, or one account states something suspiciously close to but not quite matching what an earlier lesson traced, the primary source is what settles it, not whichever account was read first or sounded most confident.

## Practice

1. ▢ A training plan proposes a 50-billion-parameter model trained on 400 billion tokens, using ZeRO stage 2 across 16 devices split 2 nodes of 8, with tensor parallelism set to size 16 (spanning both nodes). Name two things in this plan worth challenging, using this lesson's checklist.

<details markdown="1"><summary>Check</summary>

The ratio (`400 / 50 = 8` tokens per parameter) is well below the roughly-20-to-25 compute-optimal range, worth asking whether that is a deliberate, justified choice. The tensor-parallel size of 16, spanning both nodes rather than staying within one 8-GPU node, contradicts Lesson 14's own reasoning that tensor parallelism's frequent all-reduce belongs within a single node's fast interconnect, with pipeline parallelism (not tensor parallelism) carrying the cross-node split instead.

</details>

2. ▢ A colleague claims "bf16 needs loss scaling, just like fp16, since they're both 16-bit formats." Using this lesson's worked example, what is the actual answer, and what specifically is being conflated?

<details markdown="1"><summary>Check</summary>

bf16 does not need loss scaling the way fp16 does. Loss scaling addresses fp16's narrow 5-bit exponent range causing underflow; bf16 keeps fp32's full 8-bit exponent range, which is the specific problem loss scaling exists to work around, so bf16 does not have that problem in the first place. The colleague's claim conflates the two formats' bit widths (both 16 bits total) with their actual exponent-range difference, which is what determines whether loss scaling is needed.

</details>

3. ▢ A plan states only a single total compute-cost figure, with no breakdown of ratio, data pipeline, parallelism plan, or stability plan. Per Lessons 23 and this lesson, is this plan reviewable as stated?

<details markdown="1"><summary>Check</summary>

Not really: a single bundled number invites only "can this be cheaper" and hides which underlying claims are well-supported and which are unexamined assumptions. A proper review needs the plan broken into the categories this lesson's checklist walks through, so each one can be checked on its own terms.

</details>

## Real-world reps

- [ ] Find a real, published pretraining configuration (a technical report, a training script's configuration file, or a model card) and run it through this lesson's checklist, stage by stage, noting which items are stated explicitly and which are left silent.
- [ ] Find a claim about LLM pretraining stated confidently in a blog post or forum answer, and check it against the actual primary source it should trace back to (a paper this track cites, or another you locate). Note whether it holds up, is a simplification, or is a genuine conflation like this lesson's bf16 example.
- [ ] Tomorrow: write a short review, three to five sentences, of a real or hypothetical pretraining plan, naming at least one specific choice you would challenge and what you would ask the person defending it to justify.

## Going further

- [Paper: "Training Compute-Optimal Large Language Models", Hoffmann et al., 2022](https://arxiv.org/abs/2203.15556)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
