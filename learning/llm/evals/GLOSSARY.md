---
title: Glossary
description: "Canonical terms for evals"
type: glossary
---

# Evals Glossary

Canonical terms for proving whether a model change helped, and for defending that a number reflects it.

## Terms

**Data contamination**:
Eval data, or a close paraphrase of it, ending up inside a model's training data (typically pretraining, via a benchmark scraped into web-crawl data) or a model being iteratively tuned against the same eval set until it stops measuring the underlying skill.
_Avoid_: leakage, cheating

**Held-out data**:
Eval examples, or close paraphrases of them, that the model being judged never saw during training or fine-tuning. A score is only informative when the data behind it is held out.
_Avoid_: test set (ambiguous with a training-pipeline split), unseen data
