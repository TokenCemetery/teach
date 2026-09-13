---
title: 23. Defending a Compute Budget
description: A pretraining plan is a bet made of many separate decisions, and defending it means defending each one on its own terms
type: lesson
---

# Lesson 23. Defending a Compute Budget

**Mission link:** "Can decide whether a stated task calls for pretraining, continued pretraining, or fine-tuning an existing base model, and defend the choice on cost" is the Success looks like bullet stage 10 closes. Lesson 22 covered when pretraining is the wrong call; this lesson covers defending the plan once it genuinely is the right one.
**Primary source:** [Paper: "Training Compute-Optimal Large Language Models", Hoffmann et al., 2022](https://arxiv.org/abs/2203.15556)
**Prerequisites:** [Lesson 22](0022-pretraining-is-usually-the-wrong-default.md)

## Warm-up

1. ▢ Per Gururangan et al., does domain-adaptive pretraining help more, less, or about the same, whether the target domain was already close to the base model's original training data?

<details markdown="1"><summary>Check</summary>

It helps more precisely when the target domain was not already well represented in the base model's original pretraining; targets already close to in-domain benefit less, since the base model already covers them reasonably well.

</details>

2. ▢ Name one legitimate reason to pretrain from scratch rather than adapt an existing model, per Lesson 22.

<details markdown="1"><summary>Check</summary>

Any one of: the target language or domain is so far outside every available base model's training data and tokenizer that adaptation cannot close the gap, a licensing or provenance requirement rules out every available base model, or a deliberate architectural change an existing checkpoint cannot be adapted into.

</details>

## Know this

### A pretraining plan is not one number

Once pretraining is genuinely the right call, defending it to someone who controls the budget means defending more than a single total-cost figure. Every earlier stage of this track produced one piece of that plan, and each piece is a claim that can be checked, and challenged, on its own terms:

- **The token-to-parameter ratio (Stage 3).** Is the planned parameter count and token count close to Hoffmann et al.'s roughly-20-to-25-tokens-per-parameter range for the chosen compute budget, or does it lean toward Kaplan et al.'s parameter-heavy, comparatively data-light allocation? A plan that departs from the compute-optimal range needs a stated reason, not silence.
- **The data pipeline (Stages 1 and 2).** Is the token count achievable from a corpus that has actually been sourced, deduplicated, and quality-filtered, or does it assume data that does not yet exist at the needed scale and quality?
- **The parallelism plan (Stages 4 through 6).** Does the plan's device count, sharding strategy, and any tensor- or pipeline-parallel split match the hardware's actual interconnect, per Lesson 14's own reasoning, or does it assume communication patterns the hardware cannot support efficiently?
- **The stability and monitoring plan (Stages 7 through 9).** Does the plan say what precision, clipping, and schedule will be used, and does it include checkpointing frequent enough, and monitoring thorough enough, for the failure rates Stage 8's own evidence showed are normal at this scale, not exceptional?

### Why bundling these into one number invites the wrong question

A budget presented only as a single total cost invites exactly one question in return: can it be made cheaper. A budget presented as the specific claims above invites a more useful set of questions: is this token-to-parameter ratio actually compute-optimal for the stated goal, does the data exist to support it, does the parallelism plan match the hardware, and is the run protected against the failure rate a run of this length should expect. Defending each claim separately is also what makes it possible to say, honestly, where the plan is uncertain (an unproven data source, an unverified interconnect assumption) rather than presenting uniform confidence across a plan that does not have it.

### What "defensible" does not mean

Defending a compute budget does not mean guaranteeing the training run will succeed on the first attempt, or that a review board must approve it. It means every major number in the plan traces to a stated reason grounded in the material this track covered, so a challenge to any one of them ("why this ratio," "why this parallelism split," "why this checkpoint interval") has an answer other than "that is what we always do."

## Practice

1. ▢ A proposed pretraining plan trains a 30-billion-parameter model on 200 billion tokens. Using Stage 3's roughly-20-to-25-tokens-per-parameter range, is this plan's ratio inside or outside that range, and what follow-up question does that raise?

<details markdown="1"><summary>Hint</summary>

Divide the token count by the parameter count and compare to the range.

</details>

<details markdown="1"><summary>Check</summary>

About 6.7 tokens per parameter (`200 / 30`), well below the roughly-20-to-25 range. This raises the follow-up question of why the plan is trained on comparatively little data relative to its size, the same undertrained pattern Lesson 6 diagnosed in GPT-3, and whether that departure from the compute-optimal range is deliberate and justified or simply unexamined.

</details>

2. ▢ A team presents a pretraining budget as a single total-dollar figure with no further breakdown. Per this lesson, what is the main problem with presenting it this way?

    - a) A single number is always inaccurate
    - b) It invites only "can this be made cheaper" in return, rather than surfacing which specific claims (ratio, data, parallelism, stability plan) are actually solid or shaky
    - c) Reviewers cannot understand dollar figures
    - d) It is illegal to present a budget this way

<details markdown="1"><summary>Check</summary>

**b)** is the actual problem this lesson raises: bundling every decision into one number hides which parts of the plan are well-supported and which are assumptions, and invites a much less useful conversation than defending each claim would. (a), (c), and (d) are not the reasoning this lesson gives.

</details>

3. ▢ Name the four categories of claim this lesson says a defensible pretraining plan should be broken into.

<details markdown="1"><summary>Check</summary>

The token-to-parameter ratio, the data pipeline (sourcing, deduplication, quality filtering), the parallelism plan matched to the hardware's interconnect, and the stability and monitoring plan (precision, clipping, schedule, checkpointing frequency).

</details>

## Real-world reps

- [ ] Find a published technical report for an open pretrained model and see how many of this lesson's four claim categories it actually states explicitly (ratio, data pipeline, parallelism plan, stability and monitoring plan). Note any it leaves unstated.
- [ ] For a compute budget of your choosing, write out the four categories as a short bulleted plan, one sentence of justification each, the way this lesson argues a defensible budget should be presented.
- [ ] Tomorrow: pick one of your four bullets from the previous rep and write down what evidence, from this track or elsewhere, you would point to if someone challenged that specific claim.

## Going further

- [Paper: "Training Compute-Optimal Large Language Models", Hoffmann et al., 2022](https://arxiv.org/abs/2203.15556)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
