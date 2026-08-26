# Adapter Fine-Tuning Resources

## Knowledge

- [Paper: "LoRA: Low-Rank Adaptation of Large Language Models" — Hu et al., arXiv:2106.09685](https://arxiv.org/abs/2106.09685)
  The original low-rank adapter method and the intrinsic-dimensionality argument for why it works. Use for: stage 3, and for what rank and alpha actually control.

- [Paper: "QLoRA: Efficient Finetuning of Quantized LLMs" — Dettmers et al., arXiv:2305.14314](https://arxiv.org/abs/2305.14314)
  NF4, double quantisation and paged optimizers, with the memory accounting spelled out. Use for: stage 4, and as the reference for what a quantized base costs in quality.

- [Paper: "DoRA: Weight-Decomposed Low-Rank Adaptation" — Liu et al., arXiv:2402.09353](https://arxiv.org/abs/2402.09353)
  Splits weights into magnitude and direction and adapts the direction. Use for: stage 5, and for why the gain concentrates at low rank.

- [Docs: PEFT — Hugging Face](https://huggingface.co/docs/peft)
  Reference implementation of all three methods and the configuration surface they expose. Use for: what a hyperparameter is called in practice. Version-sensitive — check against the installed release rather than from memory.

- [Code: MLX Examples — LoRA fine-tuning, Apple ml-explore](https://github.com/ml-explore/mlx-examples/tree/main/lora)
  The Apple Silicon path, and the one that runs on this machine. Use for: every local run in stages 3 and 5.

- [Docs: llama.cpp — ggml-org](https://github.com/ggml-org/llama.cpp)
  GGUF conversion and serving, including adapter handling. Use for: stage 7, getting a trained adapter into the local stack.

- [Blog: "Practical Tips for Finetuning LLMs Using LoRA" — Sebastian Raschka, Ahead of AI](https://magazine.sebastianraschka.com/p/practical-tips-for-finetuning-llms)
  Ablations over rank, alpha and target modules, with the experiments shown. Use for: sanity-checking hyperparameter folklore against measurements.

## Wisdom (Communities)

- [r/LocalLLaMA](https://www.reddit.com/r/LocalLLaMA/)
  The largest concentration of people fine-tuning on consumer hardware, including Apple Silicon. Use for: what actually works within a memory budget, and which folklore is worth testing.

- [MLX Discussions — ml-explore/mlx](https://github.com/ml-explore/mlx/discussions)
  Maintainers answer directly. Use for: Apple Silicon specifics and whether something is supported yet.

- [Hugging Face Forums](https://discuss.huggingface.co/)
  Searchable and archived, with library authors present. Use for: PEFT and `transformers` behaviour that the docs leave ambiguous.

- [EleutherAI Discord](https://www.eleuther.ai/community)
  Research-grade discussion with people who read the papers critically. Use for: stage 7 judgment calls on whether a claimed result generalises.

## Gaps

- No source tracks which `torch`, PEFT and MLX versions actually work together on a given Python version and platform. This blocks the first run more often than any concept does, and each environment has to be verified against release notes rather than assumed.
- Current PEFT API surface for DoRA. The flag name should be read from the installed version's docs, never recalled.
- No trusted source yet for evaluation design specific to small-model task adaptation — the weakest link in stage 6, and the hardest part of the mission.
- No GPU rental provider evaluated. Needed by stage 4.
- Most published LoRA hyperparameter advice targets 7B models and above. Nothing found yet that addresses whether it transfers to the 1–3B class this machine can train.
