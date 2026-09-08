---
title: Held-Out Data and Contamination
description: "Train/test split discipline for an eval set, the two contamination pathways, how to detect each, and how to design a custom set that resists them"
type: reference
---

# Held-Out Data and Contamination

Stage 1 compressed for lookup. [Lesson 1](../lessons/0001-held-out-and-contamination.md) covers the two contamination pathways and the guided-instruction test for detecting them; [lesson 2](../lessons/0002-designing-contamination-resistance.md) covers designing a custom eval set to resist contamination from the start. This sheet is the definitions, the pathways, and the prevention toolkit, side by side.

## What "held out" requires

An eval set is held out when the model being judged never saw those exact examples, or close paraphrases of them, during training or fine-tuning. That single property is what lets a good score mean "this generalizes" rather than "this was memorized." Before quoting a score as evidence, answer: *why couldn't the model have gotten this right by memorization, or by having been tuned against this exact set?* If there's no answer, the number describes the eval, not the model.

## Two contamination pathways

| Pathway | What happens | Literal leakage? | Fix |
|---|---|---|---|
| Pretraining absorption | A benchmark gets scraped into web-crawl training data before anyone builds an eval on it | Yes | Choose or build data unlikely to appear in a pretraining corpus, or test for its presence |
| Iterative overfitting | The same eval set is run repeatedly while tuning a model or prompt, gradually shaping the system to pass those specific examples | No | Refresh the set, or hold back an untouched slice of it |

Both produce the same symptom: a number that looks good and does not predict real-world behavior. The fixes differ because the causes do; treating one as a substitute for the other leaves the untreated pathway open.

## Detecting pretraining absorption: the guided-instruction test

Give the model the first part of a benchmark instance and ask it to complete the rest verbatim. Reproducing specifics a plausible guess wouldn't recover, exact wording, an unusual number, a rare proper noun, is strong evidence that instance was in its training data (Golchin and Surdeanu, 2023). This only tests for absorption; it says nothing about iterative overfitting, which leaves no such trace.

## Preventing contamination when building a custom set

| Technique | What it does | When it applies | Limits |
|---|---|---|---|
| Postdate the training cutoff | Source eval data from material created after the model's stated training cutoff | Requires an accurate, verified cutoff date, not a marketing claim | Protects against absorption only; a stale eval set still risks iterative overfitting |
| Canary string (BIG-bench convention) | Embed a unique marker phrase asking any crawler to exclude the marked content | Any published set | A request, not an enforcement mechanism; depends on crawler cooperation |
| n-gram overlap check | Measure direct overlap between eval data and a known corpus | Only when the pretraining corpus is known and accessible | Unusable for a closed model with undisclosed training data |
| Keep the set unpublished | Never post it publicly | Always available | Strongest prevention, at the cost of reproducibility and external scrutiny |

The first three are conditional on something (an accurate cutoff, crawler cooperation, corpus access); keeping a set private is the only technique with no precondition, which is why it is the fallback when the others don't apply.

## Before trusting a score

- The eval set's contamination story is stated, not assumed: which pathway was checked for, and how.
- A borrowed public benchmark has been tested with the guided-instruction method, or a documented reason exists why that risk is low.
- A custom eval set names which prevention technique(s) apply to it, and their limits are known, not just their presence.
- An eval set reused for months of tuning has been refreshed, or a held-back slice exists that hasn't been touched.

## Sources

- [Docs: "Define success criteria and build evaluations", Claude Platform Docs](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests)
- [Paper: "Time Travel in LLMs: Tracing Data Contamination in Large Language Models", Golchin and Surdeanu, 2023](https://arxiv.org/abs/2308.08493)
- [Paper: "Beyond the Imitation Game: Quantifying and Extrapolating the Capabilities of Language Models" (BIG-bench), Srivastava et al., 2022](https://arxiv.org/abs/2206.04615)
- [Resources](../RESOURCES.md)
