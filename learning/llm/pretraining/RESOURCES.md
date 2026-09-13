---
title: Resources
description: "Trusted sources for LLM pretraining"
type: resources
---

# LLM Pretraining Resources

## Knowledge

- [Paper: "Scaling Laws for Neural Language Models", Kaplan et al., 2020](https://arxiv.org/abs/2001.08361)
  Fits the original power-law relationships between loss, compute, parameter count, and data, and argues for scaling parameters faster than data. Use for: stage 3, as the baseline that Chinchilla later revises.
- [Paper: "Training Compute-Optimal Large Language Models", Hoffmann et al., 2022](https://arxiv.org/abs/2203.15556)
  The Chinchilla paper. Refits the scaling laws with a wider sweep and finds parameters and tokens should scale together, roughly twenty tokens per parameter, overturning Kaplan's parameter-heavy recommendation. Use for: stage 3's central result, and the token budget most modern training runs actually use.
- [Paper: "ZeRO: Memory Optimizations Toward Training Trillion Parameter Models", Rajbhandari et al., 2019](https://arxiv.org/abs/1910.02054)
  Defines the three ZeRO stages, sharding optimizer state, then gradients, then parameters across data-parallel devices. Use for: stage 5's central technique, which FSDP implements.
- [Documentation: "Fully Sharded Data Parallel", PyTorch](https://pytorch.org/docs/stable/fsdp.html)
  The API reference for PyTorch's ZeRO-stage-3-style sharding, including the sharding strategies and wrapping policies a lesson's lab actually runs. Use for: stage 5's hands-on reps.
- [Paper: "Efficient Large-Scale Language Model Training on GPU Clusters Using Megatron-LM", Narayanan et al., 2021](https://arxiv.org/abs/2104.04473)
  Combines tensor parallelism, pipeline parallelism, and data parallelism in one system, with the throughput and memory tradeoffs of each measured against the others. Use for: stage 6's central technique and its worked numbers.
- [Documentation: "DeepSpeed", Microsoft](https://github.com/microsoft/DeepSpeed)
  A second production implementation of ZeRO alongside 3D parallelism, with configuration examples a lesson can point to as a second concrete system next to FSDP and Megatron-LM. Use for: stages 5 and 6, as the cross-check that a claim is about the technique rather than one library's API.
- [Paper: "The Pile: An 800GB Dataset of Diverse Text for Language Modeling", Gao et al., 2020](https://arxiv.org/abs/2101.00027)
  A fully documented pretraining corpus: what sources went in, at what proportions, and why. Use for: stage 1, as a worked example of a data-mixing decision made explicit.
- [Paper: "Deduplicating Training Data Makes Language Models Better", Lee et al., 2021](https://arxiv.org/abs/2107.06499)
  Shows near-duplicate text and long repeated substrings cause verbatim memorization, and gives two deduplication techniques (exact substring matching via a suffix array, and near-duplicate matching via MinHash), each measured against a real corpus. Use for: stage 1's deduplication material, with concrete before/after numbers.
- [Paper: "Language Models are Few-Shot Learners", Brown et al., 2020](https://arxiv.org/abs/2005.14165)
  The GPT-3 paper. Appendix A documents a concrete quality-filtering pipeline: a classifier trained to distinguish curated text from raw Common Crawl, used to re-sample it toward higher-scoring documents, alongside a separate fuzzy-deduplication pass. Use for: stage 1's quality-filtering material, as the worked example the deduplication paper above does not itself provide.
- [Paper: "Neural Machine Translation of Rare Words with Subword Units", Sennrich et al., 2015](https://arxiv.org/abs/1508.07909)
  Introduces byte-pair encoding for subword tokenization, the algorithm most modern tokenizers still build on. Use for: stage 2's core algorithm.
- [Paper: "SentencePiece: A simple and language independent subword tokenizer and detokenizer for Neural Text Processing", Kudo and Richardson, 2018](https://arxiv.org/abs/1808.06226)
  Treats tokenization as operating on raw text directly, without a language-specific pre-tokenization step, and covers unigram-language-model tokenization as an alternative to BPE. Use for: stage 2's second algorithm and the vocabulary-size tradeoff.
- [Paper: "Scaling Language Models: Methods, Analysis & Insights from Training Gopher", Rae et al., 2021](https://arxiv.org/abs/2112.11446)
  A detailed, honest account of a large training run, including where loss spikes and instability appeared and what the authors did about them. Use for: stage 7's central case study.
- [Paper: "LLaMA: Open and Efficient Foundation Language Models", Touvron et al., 2023](https://arxiv.org/abs/2302.13971)
  A published, reproducible training recipe: data mixture, tokenizer, schedule, and hyperparameters, stated plainly enough to check a lesson's claims against. Use for: cross-checking stages 1 through 3 and 7 against a real, complete recipe.

## Gaps

- No primary source yet on continued pretraining or domain-adaptive pretraining as a cost tradeoff against fine-tuning. Needed before stage 10 can defend that specific choice; revisit once that lesson is drafted.
- Checkpointing and fault tolerance for a multi-day distributed run (stage 8) is currently documented mainly inside individual framework docs (PyTorch, DeepSpeed) rather than in a framework-neutral source. A vendor-neutral treatment has not been located.
- GPT-3's classifier-based filtering (2020) is the only worked quality-filtering example listed so far. Corpora built since 2023 (FineWeb, Dolma) filter far more aggressively and document it in more depth; a more recent primary source would strengthen stage 1.
