---
title: Resources
description: Trusted sources and communities for adapter fine-tuning
type: resources
---

# Adapter Fine-Tuning Resources

## Knowledge

### The three methods

- [Paper: "LoRA: Low-Rank Adaptation of Large Language Models", Hu et al., arXiv:2106.09685](https://arxiv.org/abs/2106.09685)
  The original low-rank adapter method and the intrinsic-dimensionality argument for why it works. Use for: stage 3, and for what rank and alpha actually control.

- [Paper: "QLoRA: Efficient Finetuning of Quantized LLMs", Dettmers et al., arXiv:2305.14314](https://arxiv.org/abs/2305.14314)
  NF4, double quantisation and paged optimizers, with the memory accounting spelled out. Use for: stage 4, and as the reference for what a quantized base costs in quality. Read the limitations section.

- [Paper: "DoRA: Weight-Decomposed Low-Rank Adaptation", Liu et al., arXiv:2402.09353](https://arxiv.org/abs/2402.09353)
  Splits weights into magnitude and direction and adapts the direction. Use for: stage 5. Section 4's analysis of how full fine-tuning and LoRA move each quantity is the actual argument.

- [Paper: "Intrinsic Dimensionality Explains the Effectiveness of Language Model Fine-Tuning", Aghajanyan et al., arXiv:2012.13255](https://arxiv.org/abs/2012.13255)
  Why adaptation can live in a low-dimensional subspace at all. Use for: the justification underneath LoRA rather than the mechanism.

### Current practice

- [Docs: "LoRA Without Regret", Hugging Face TRL](https://huggingface.co/docs/trl/main/en/lora_without_regret)
  The case that all-linear targets with adequate rank close the gap to full fine-tuning. Use for: target-module and rank choice, and as the baseline any new variant must beat. This supersedes the attention-only convention inherited from the original paper.

- [Blog: "Practical Tips for Finetuning LLMs Using LoRA", Sebastian Raschka, Ahead of AI](https://magazine.sebastianraschka.com/p/practical-tips-for-finetuning-llms)
  Ablations over rank, alpha and target modules, with the experiments shown. Use for: sanity-checking hyperparameter folklore against measurements.

- [Docs: PEFT, Hugging Face](https://huggingface.co/docs/peft)
  Reference implementation of all three methods and the configuration surface they expose. Use for: what a hyperparameter is called in practice, and which variants are established enough to be a flag. Version-sensitive, so check against the installed release rather than from memory.

- [Docs: SFTTrainer, Hugging Face TRL](https://huggingface.co/docs/trl/main/en/sft_trainer)
  The standard supervised fine-tuning loop and its dataset formats. Use for: stage 3 onward. Version-sensitive; parameter names have moved between releases.

### Foundations

- [Interactive: LLM Visualization, Brendan Bycroft](https://bbycroft.net/llm)
  Click through a single token's path with per-matrix parameter counts. Use for: stage 1, and the best available answer to "where do the parameters live".

- [Blog: "The Illustrated Transformer", Jay Alammar](https://jalammar.github.io/illustrated-transformer/)
  The standard visual explanation of the architecture. Use for: stage 1 when the block structure has not landed yet.

- [Docs: Chat Templates, Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/chat_templating)
  How conversations are rendered to token sequences, and how to apply the model's own template. Use for: the single most common silent failure in fine-tuning.

- [Paper: "Decoupled Weight Decay Regularization" (AdamW), Loshchilov & Hutter, arXiv:1711.05101](https://arxiv.org/abs/1711.05101)
  The optimizer everything here uses, and why its weight decay differs from Adam's. Use for: stage 2's memory argument.

- [Paper: "ZeRO: Memory Optimizations Toward Training Trillion Parameter Models", Rajbhandari et al., arXiv:1910.02054](https://arxiv.org/abs/1910.02054)
  The canonical accounting of weights, gradients and optimizer state as separate memory categories. Use for: deriving the sixteen-bytes-per-parameter figure.

- [Paper: "Training Deep Nets with Sublinear Memory Cost", Chen et al., arXiv:1604.06174](https://arxiv.org/abs/1604.06174)
  Gradient checkpointing, and the compute-for-memory trade it makes. Use for: stage 2, and for the setting you will leave on permanently.

- [Blog: "A Recipe for Training Neural Networks", Andrej Karpathy](https://karpathy.github.io/2019/04/25/recipe/)
  How to run experiments so their results mean something. Use for: stage 3's diagnosis lesson, and the overfit-two-examples smoke test.

### Quantisation

- [Paper: "LLM.int8(): 8-bit Matrix Multiplication for Transformers at Scale", Dettmers et al., arXiv:2208.07339](https://arxiv.org/abs/2208.07339)
  The outlier-feature problem that makes transformer quantisation harder than the arithmetic suggests. Use for: why blockwise beats per-tensor.

- [Docs: bitsandbytes quantization, Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/quantization/bitsandbytes)
  The 4-bit configuration surface in practice. Use for: stage 4 setup.

- [Code: bitsandbytes, bitsandbytes-foundation](https://github.com/bitsandbytes-foundation/bitsandbytes)
  The `backends/` directory is the authority on which hardware supports which operation. Use for: settling a hardware-support question against the source rather than a tutorial, which in this area is usually stale.

### Data and evaluation

- [Paper: "LIMA: Less Is More for Alignment", Zhou et al., arXiv:2305.11206](https://arxiv.org/abs/2305.11206)
  Evidence that a small carefully curated dataset outperforms a large careless one, and that SFT largely teaches format. Use for: stage 6's opening argument.

- [Paper: "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena", Zheng et al., arXiv:2306.05685](https://arxiv.org/abs/2306.05685)
  Model-as-judge evaluation with its biases characterised: position, verbosity, self-preference. Use for: free-form generation metrics, and for why the judge needs calibrating against human labels.

- [Paper: "An Empirical Study of Catastrophic Forgetting in Large Language Models During Continual Fine-tuning", Luo et al., arXiv:2308.08747](https://arxiv.org/abs/2308.08747)
  That forgetting is measurable, common, and not confined to edge cases. Use for: justifying the regression suite to someone who thinks it is overhead.

- [Paper: "Fine-tuning Aligned Language Models Compromises Safety, Even When Users Do Not Intend To!", Qi et al., arXiv:2310.03693](https://arxiv.org/abs/2310.03693)
  Safety behaviour degrading from fine-tuning on benign data. Use for: why the regression suite must include refusal cases.

- [Code: lm-evaluation-harness, EleutherAI](https://github.com/EleutherAI/lm-evaluation-harness)
  Standard benchmark implementations and the contamination problems they document. Use for: building an eval, and for reading published scores sceptically.

### Serving

- [Docs: LoRA adapters, vLLM](https://docs.vllm.ai/en/latest/features/lora.html)
  Serving adapters in production, including multi-adapter routing. Use for: stage 7. Check maximum-rank and maximum-adapter limits against the installed version.

- [Paper: "S-LoRA: Serving Thousands of Concurrent LoRA Adapters", Sheng et al., arXiv:2311.03285](https://arxiv.org/abs/2311.03285)
  How many adapters get batched against one shared base efficiently. Use for: understanding why multi-adapter serving is a solved problem rather than a research idea.

- [Blog: "LLM Inference Performance Engineering: Best Practices", Databricks](https://www.databricks.com/blog/llm-inference-performance-engineering-best-practices)
  Prefill versus decode, and what each phase is bound by. Use for: stage 7's cost arithmetic.

### The alternative

- [Paper: "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks", Lewis et al., arXiv:2005.11401](https://arxiv.org/abs/2005.11401)
  The canonical statement of the approach that should usually be preferred when the problem is knowledge. Use for: the final lesson's argument, and for making the case against fine-tuning credibly.

## Wisdom (Communities)

- [r/LocalLLaMA](https://www.reddit.com/r/LocalLLaMA/)
  The largest concentration of people fine-tuning on consumer hardware, across every backend. Use for: searching what already worked within a memory budget, which folklore is worth testing, and replication reports on new methods. Read the archive; posting is a rep, not a source.

- [Hugging Face Forums](https://discuss.huggingface.co/)
  Searchable and archived, with library authors present. Use for: PEFT, TRL and `transformers` behaviour that the docs leave ambiguous.

- [EleutherAI Blog](https://blog.eleuther.ai/)
  Write-ups from a group that reads its own field critically, including negative results. Use for: stage 5 and 7 judgment calls on whether a claimed result generalises. Their Discord is where this gets discussed first, and is deliberately not listed: nothing said there is retrievable later.

- [MLX Discussions, ml-explore/mlx](https://github.com/ml-explore/mlx/discussions)
  Public, searchable, and answered by the maintainers. Use for: reading whether a given operation is supported on Apple Silicon yet, usually already asked.

## Gaps

- No source tracks which `torch`, PEFT, TRL and quantisation-library versions actually work together on a given Python version and platform. This blocks a first run more often than any concept does, and each environment has to be verified against release notes rather than assumed.
- Hardware backend coverage for 4-bit operations changes release to release. No document is reliable here; the library source is the only authority, and any tutorial's claim about hardware requirements should be treated as expired.
- No trusted source yet for evaluation design specific to small-model task adaptation. This is the weakest link in stage 6 and the hardest part of the mission. The general evaluation literature is aimed at benchmarking foundation models, not at proving a narrow adapter helped.
- Most published LoRA hyperparameter advice targets 7B models and above. Little addresses whether it transfers to the 1–3B class, which is where most people actually start.
- No independent replication surveyed for DoRA at the scale LoRA and QLoRA enjoy. Treat its reported gains as needing local measurement.
- No source chosen for constrained decoding, which Lesson 27 recommends as the correct answer to schema-validity problems. It is named without a reference behind it.
