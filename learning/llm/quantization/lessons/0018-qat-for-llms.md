---
title: "18. QAT for LLMs"
description: What quantization-aware training costs on an LLM, what it recovers, and when PTQ is enough
type: lesson
---

# Lesson 18. QAT for LLMs

**Mission link:** The mission asks you to say when quantization-aware training earns its cost over post-training quantization, which takes the price tag, the measured gain, and the cases where the gain is zero.
**Primary source:** [Paper: "LLM-QAT: Data-Free Quantization Aware Training for Large Language Models", Liu et al., 2023](https://arxiv.org/abs/2305.17888)
**Prerequisites:** [Lesson 17](0017-fake-quantization-and-the-ste.md), [Quantization-aware training](../GLOSSARY.md), [Post-training quantization](../GLOSSARY.md), [Weight-only quantization](../GLOSSARY.md)

## Warm-up

1. ▢ Lesson 9 compared round-to-nearest at 8 bits and at 4 or fewer. Which of the two does it hold up at, and why does it slip at the other?

<details markdown="1"><summary>Check</summary>

It holds at 8 bits, where the grid has 256 levels and the [rounding error](../GLOSSARY.md) per weight is small. At 4 bits there are 16 levels, each weight can be off by up to half a much larger step, and plain rounding has nothing that compensates for the errors. That gap is the room GPTQ, AWQ and QAT compete in.

</details>

2. ▢ Why can a training loop not simply differentiate through `round`, and what does fake quantization do about it?

<details markdown="1"><summary>Check</summary>

The derivative of round is zero almost everywhere, so no gradient reaches the weights. Fake quantization keeps a float master copy, applies quantize and dequantize in the forward pass, and uses the [straight-through estimator](../GLOSSARY.md) to pass the gradient through the rounding step in the backward pass, with zero gradient for values the clamp cut off.

</details>

## Know this

### What QAT costs on an LLM

QAT is ordinary training with fake quantization inserted, so it inherits training's costs. Nagel et al. list them: longer training, the need for data, and hyper-parameter search ([white paper](https://arxiv.org/abs/2106.08295), section 4). Two LLM-specific measurements make this concrete.

The PyTorch team measured it with their torchao QAT flow on Llama3-8B, using int8 per-token dynamic activations with int4 grouped weights. Every one of the 225 linear layers gets at least one fake quantize operation. In their microbenchmarks QAT fine-tuning was about 34% slower than regular full fine-tuning, and with activation checkpointing the memory use rose by around 2.35 GB per GPU ([PyTorch blog](https://pytorch.org/blog/quantization-aware-training/)). A 20-hour fine-tune becomes about 27 hours. These are their numbers on their setup, so treat them as an order of magnitude.

The second cost is data. Liu et al. note that the original training data of an LLM is often unavailable, and that models are often trained in several stages (instruction tuning, reinforcement learning) that would be hard to replicate during QAT. Their answer is **data-free** training: the full-precision model generates text itself, with the first few tokens picked greedily and the rest sampled, and the quantized model is trained to match the full-precision model as its teacher. They report distilling the quantized models from only a small set of 100,000 sampled sequences, on a single 8-GPU node. Sequences were capped at 1,024 tokens, so the whole set is at most about 100 million tokens, a figure that follows from their two numbers rather than one they state.

### What it recovers

LLM-QAT quantizes weights, activations and the KV cache, written as W-A-KV in bits. Their Table 1 reports the average zero-shot accuracy over seven common-sense tasks. For LLaMA-7B the full-precision average is 66.2.

| Setting (W-A-KV) | RTN | SmoothQuant | LLM-QAT |
|---|---|---|---|
| 8-8-8 | 65.6 | 66.3 | 66.0 |
| 4-16-16 (4-bit weights only) | 63.0 | not reported | 64.4 |
| 4-8-4 | 41.2 | 43.2 | 60.7 |

At 8 bits every method is within a point of full precision. Weight-only 4-bit already holds up under RTN, and QAT gains 1.4 points. The 4-bit activations and KV-cache setting is where the PTQ methods collapse and QAT stays within 5.5 points. At LLaMA-30B the full-precision average is 71.4: 4-8-4 gives 42.5 with RTN and 40.7 with SmoothQuant against 69.9 for LLM-QAT, but 4-bit weights only gives 70.1 with RTN, 70.3 with GPTQ and 70.1 with LLM-QAT. The paper's own summary agrees: all methods do well at 8 bits, and when weights, activations or KV cache drop below 8 bits the PTQ methods lose accuracy while LLM-QAT holds up much better. The PTQ baselines here are RTN, GPTQ and SmoothQuant. The rotation methods of lesson 15 came later and are not in this comparison.

The torchao blog reports the same pattern from the training side. On Llama3-8B with the 8da4w scheme, QAT recovered 96% of the normalized-accuracy degradation on hellaswag compared with PTQ, and 68% of the word-perplexity degradation on wikitext. At 2-bit weights the PTQ model's wikitext word perplexity was 603,336. Skipping the first 3 and last 2 layers brought it to 6,766, and adding QAT to that brought it to 30. Without skipping those layers QAT was far less effective, so QAT did not rescue 2 bits by itself.

### QLoRA is the neighbour, not QAT

[QLoRA](https://arxiv.org/abs/2305.14314) also trains a quantized model, but it backpropagates through a frozen 4-bit base into low-rank adapters. The base weights never change, so the model is not learning to survive its own rounding: the quantization is there to fit the fine-tune in memory. This track does not teach it. The finetuning track does, and its [memory budget](../../finetuning/reference/memory-budget.md) sheet counts the bytes.

### When PTQ is enough, and when QAT pays

| Situation | Evidence | Default |
|---|---|---|
| 8-bit weights and activations | Table 1 above; [Kurtic et al.](https://arxiv.org/abs/2411.02355) report FP8 effectively lossless across Llama 3.1 sizes and well-tuned INT8 at 1 to 3% degradation | PTQ |
| 4-bit weights only, large model | LLaMA-30B row above; Kurtic et al. find INT4 weight-only rivals 8-bit | PTQ, then measure |
| 4-bit weights only, small model | LLaMA-7B: RTN loses 3.2 points, QAT 1.8 | Try PTQ, QAT if the gap matters |
| 4-bit activations or KV cache | LLaMA-30B 4-8-4: RTN 42.5, LLM-QAT 69.9 | QAT, or the rotations of lesson 15, tested |
| 3 bits or fewer | torchao 2-bit and 3-bit experiments | QAT plus keeping sensitive layers |
| Model trained on a great deal of data | [Kumar et al.](https://arxiv.org/abs/2411.04330) find PTQ degradation grows as a model sees more data | Test PTQ early, expect a larger gap |

The Kumar result comes from models up to 1.7B parameters trained on up to 26B tokens, so it says where to look, not how big the gap is for a large model. Every row is a default to test against your own baseline, not a rule.

## Practice

1. ▢ From the LLM-QAT numbers above for LLaMA-30B (full precision 71.4), how many points does RTN lose with 4-bit weights only, and how many with 4-8-4? Is QAT worth its cost in each case?

<details markdown="1"><summary>Check</summary>

RTN loses 1.3 points with 4-bit weights only (70.1) and 28.9 points at 4-8-4 (42.5). With weights only, LLM-QAT also scores 70.1, so it buys nothing here and PTQ is enough. At 4-8-4, LLM-QAT scores 69.9, 1.5 points under full precision, so the training cost buys almost all of the lost accuracy. QAT pays when activations or the KV cache go to 4 bits, not when only weights do.

</details>

2. ▢ A full fine-tune of your model takes 20 hours. Using the torchao microbenchmark, about how long would the same run take with QAT, and what else grows?

<details markdown="1"><summary>Check</summary>

About 27 hours (20 times 1.34 is 26.8). Memory also grows, by about 2.35 GB per GPU with activation checkpointing on, because the weights must be cloned before fake quantization is applied. This is one measured setup on Llama3-8B, so your run may differ.

</details>

3. ▢ Which of these describes QLoRA?

    - a) Training adapters through a frozen 4-bit base model
    - b) Updating all weights behind a straight-through rounding step
    - c) Distilling the model on text it generated itself
    - d) Quantizing the KV cache while fine-tuning the model

<details markdown="1"><summary>Check</summary>

**a)** QLoRA keeps the quantized base frozen and trains small adapters through it. (b) describes QAT in general: the weights change so they survive rounding. (c) is LLM-QAT's data-free distillation. (d) is something LLM-QAT also does, and QLoRA does not.

</details>

4. ▢ In the torchao 2-bit experiment, QAT took the wikitext word perplexity from 6,766 to 30. Does that show QAT alone makes 2-bit weights work?

<details markdown="1"><summary>Hint</summary>

Look at what had already been done to the model before QAT was added, and what happened without it.

</details>

<details markdown="1"><summary>Check</summary>

No. That model already had its first 3 and last 2 layers left unquantized, a step that cost model size and had taken the perplexity from 603,336 to 6,766. Without skipping those layers QAT was far less effective. At very low bits QAT is one ingredient next to keeping the sensitive layers in higher precision, which is a decision about what to quantize as well as how.

</details>

5. ▢ Your team's PTQ int4 model is fine, but the next model you train is trained on three times more data and its int4 version scores noticeably worse. What does the literature in this lesson suggest, and what should you not conclude?

<details markdown="1"><summary>Check</summary>

Kumar et al. report that PTQ degradation grows as a model is trained on more data, so a larger gap after longer training is what the scaling-law evidence predicts. Options to test are a higher bit width, a stronger PTQ method, or QAT. Do not conclude it is inevitable or give its size: their evidence is for models up to 1.7B parameters and 26B tokens, so run the comparison on your own model against the full-precision baseline.

</details>

## Real-world reps

- [ ] Open the PyTorch QAT blog and find the sentence on what the convert step produces compared with the PTQ flow. Write down what that implies for deploying a QAT model on the same kernels as a PTQ one.
- [ ] Pick a quantized open model you might deploy and read its model card: does it say whether the weights came from PTQ or QAT, and which calibration or training data was used?
- [ ] Tomorrow: without notes, write three costs of QAT, the situations where PTQ is enough, and the situation where QAT pays.

## Going further

- [QAT and Hardware](../reference/qat-and-hardware.md)
- [Blog: "Quantization-Aware Training for Large Language Models with PyTorch", PyTorch, 2024](https://pytorch.org/blog/quantization-aware-training/)
- [Paper: "QLoRA: Efficient Finetuning of Quantized LLMs", Dettmers et al., 2023](https://arxiv.org/abs/2305.14314)
- [Finetuning: Memory Budget](../../finetuning/reference/memory-budget.md)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
