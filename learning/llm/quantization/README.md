---
title: Quantization
description: "Quantize an LLM and defend it: number formats, PTQ and QAT methods, what runs faster, and measuring what it cost"
type: topic
---

# Learning: Quantization

Take a trained LLM and make it smaller and faster with quantization, knowing what each number format and method does to its weights, activations and KV cache. End able to choose a scheme for a given model, hardware and quality bar, measure honestly what it cost, and review someone else's claim that a quantized model "loses nothing".

**Latest lesson:** [27. When the Usual Answer Is Wrong](lessons/0027-when-the-usual-answer-is-wrong.md)

## Success looks like

- Read a number format's bit layout, say what range and precision it buys, and work out a model's memory footprint in that format.
- Quantize a tensor by hand: choose the scale, zero point, clipping range and granularity, and predict where the error will come from.
- Explain why LLMs have outlier features and activations, and which technique handles each.
- Explain what round-to-nearest, GPTQ and AWQ each do to the weights, and what the calibration set contributes and can get wrong.
- Decide when activations and the KV cache can be quantized as well as the weights, and with which technique.
- Say when quantization-aware training earns its cost over post-training quantization.
- Predict whether a scheme will actually run faster on given hardware at a given batch size, rather than assuming fewer bits means faster.
- Measure the quality a quantization cost, beyond perplexity, against an honest baseline.
- Read a quantized checkpoint, in safetensors with its quantization config or in GGUF, and say what is stored in it.
- Choose a scheme for a given model, hardware and quality bar, review someone else's quantization claim by naming what it hides, and say when the usual answer is the wrong one.

## Constraints

- Assumes comfort reading Python and NumPy, and knowing what a transformer layer is at the level of "matrix multiplications plus attention". No prior knowledge of quantization or of floating-point internals.
- Hardware-neutral where it can be. Where a claim is one vendor's or one library's documented behaviour, the lesson names it, because kernel support changes faster than the theory.
- Practice runs on a laptop with NumPy for stages 1 to 3. Later reps quantize a small open model, which a free GPU notebook is enough for.

## Out of scope

- QLoRA, training an adapter through a 4-bit base: see [`llm/finetuning`](../../llm/finetuning/), stage 4 (lessons 0014 to 0017). This track teaches the general theory those lessons apply, and links to them rather than restating QLoRA.
- Picking a scheme for a serving latency budget and running it in vLLM or llama.cpp: see [`llm/inference`](../../llm/inference/), stage 3 (lessons 0007 to 0009) and its [Quantization at Serve Time sheet](../../llm/inference/reference/quantization-at-serve-time.md). This track teaches how the methods work and how to judge them; the serving decision stays there.
- Building an eval: see [`llm/evals`](../../llm/evals/) and its [go/no-go sheet](../../llm/evals/reference/go-no-go.md). This track uses an eval to measure quantization loss and does not re-teach how to build one.
- Pruning, sparsity and distillation, the other ways to shrink a model. They combine with quantization but are separate topics. Distillation has its own track, [`llm/distillation`](../../llm/distillation/), which compares it with quantization in its judgment stage.
- Writing quantization kernels. Stage 7 teaches what a kernel must do for a scheme to run faster, not how to write one.

The boundary with the two neighbours was settled when this track was written: the finetuning and inference lessons stay as they are, each teaching the slice its use case needs, and link here for the foundations.

## The arc

Ten stages, from what a number format is to the judgment to review someone else's quantization. A stage takes several lessons and the boundaries are soft; what makes a stage done is the capability, not the lesson count.

| Stage | Lessons | Covers | Done when |
|---|---|---|---|
| 1. Number formats | 0001 to 0003 | What quantization buys, fp32, fp16, bf16, fp8, int8, int4 and block-scaled formats | Can read a format's bit layout and size a model in it |
| 2. The quantization mapping | 0004 to 0006 | Quantize and dequantize, scale and zero point, choosing the clipping range, per-tensor, per-channel and per-group | Can quantize a tensor by hand and predict its error |
| 3. Outliers | 0007 to 0008 | Outlier features and massive activations in LLMs, and the families of fix | Can say why a naive int8 LLM breaks and which fix applies |
| 4. Post-training weight quantization | 0009 to 0012 | Round-to-nearest, GPTQ, AWQ, the calibration set | Can quantize a model's weights to 4 bits and explain what each method changed |
| 5. Activations and the KV cache | 0013 to 0016 | Weight-only against weight-and-activation, SmoothQuant, rotations, KV-cache quantization | Can decide what to quantize beyond the weights and with which technique |
| 6. Quantization-aware training | 0017 to 0018 | Fake quantization, the straight-through estimator, QAT for LLMs | Can say when QAT is worth its cost over PTQ |
| 7. Hardware and kernels | 0019 to 0020 | Memory-bound against compute-bound, what a kernel must support, which hardware runs which format | Can predict whether a scheme runs faster on given hardware and batch size |
| 8. Measuring quality loss | 0021 to 0022 | Perplexity and its limits, flips, task suites, an honest comparison | Can measure what a quantization cost and defend the number |
| 9. File formats | 0023 to 0024 | Safetensors with quantization configs, GGUF quant types and the importance matrix | Can read a quantized checkpoint and say what it stores |
| 10. Judgment | 0025 to 0027 | Choosing a scheme, reviewing a claim, shipping a quantized model others depend on, when the usual answer is wrong | Trusted to make the call on a quantization and to explain it to someone else |

## Lessons

Work through these in order.

| # | Lesson | Teaches |
|---|---|---|
| [0001](lessons/0001-what-quantization-buys.md) | What Quantization Buys | Fewer bits per parameter shrink memory and the bytes read per token, which is where most of the speed comes from |
| [0002](lessons/0002-floating-point-formats.md) | Floating-Point Formats | How sign, exponent and mantissa bits split range from precision in fp32, fp16 and bf16 |
| [0003](lessons/0003-low-bit-formats.md) | Low-Bit Formats | What fp8, int8, int4 and block-scaled formats such as MXFP4 can and cannot represent |
| [0004](lessons/0004-quantize-and-dequantize.md) | Quantize and Dequantize | The affine mapping from real values to integers: scale, zero point, rounding and clamping |
| [0005](lessons/0005-choosing-the-range.md) | Choosing the Range | Why clipping the range trades a little clipping error for much less rounding error |
| [0006](lessons/0006-granularity.md) | Granularity | Per-tensor, per-channel and per-group scales, and what each costs in stored bits |
| [0007](lessons/0007-why-llms-have-outliers.md) | Why LLMs Have Outliers | Outlier feature dimensions and massive activations, where they appear and why one value ruins a tensor's scale |
| [0008](lessons/0008-handling-outliers.md) | Handling Outliers | The four families of fix: keep them in high precision, shrink the group, migrate them, or rotate them away |
| [0009](lessons/0009-round-to-nearest.md) | Round-to-Nearest | Quantizing weights one at a time with no data, why it holds at 8 bits and slips at 4 or fewer |
| [0010](lessons/0010-gptq.md) | GPTQ | Quantizing a layer's weights in sequence and spending each rounding error on the weights not yet quantized |
| [0011](lessons/0011-awq.md) | AWQ | Protecting the weights that meet large activations by scaling their channels before rounding |
| [0012](lessons/0012-the-calibration-set.md) | The Calibration Set | What calibration data a method reads, how much it needs, and how a mismatched set shows up |
| [0013](lessons/0013-weights-activations-or-both.md) | Weights, Activations or Both | What weight-only and weight-and-activation schemes each save, and why activations are harder |
| [0014](lessons/0014-smoothquant.md) | SmoothQuant | Moving quantization difficulty from activations into weights with a per-channel scale |
| [0015](lessons/0015-rotations.md) | Rotations | Multiplying by an orthogonal matrix to spread outliers across channels so 4-bit activations survive |
| [0016](lessons/0016-kv-cache-quantization.md) | KV-Cache Quantization | Why keys and values quantize along different axes, and what it buys at long context |
| [0017](lessons/0017-fake-quantization-and-the-ste.md) | Fake Quantization and the STE | How training sees quantization: simulated rounding in the forward pass, a straight-through gradient in the backward pass |
| [0018](lessons/0018-qat-for-llms.md) | QAT for LLMs | What quantization-aware training costs on an LLM, what it recovers, and when PTQ is enough |
| [0019](lessons/0019-what-actually-runs-faster.md) | What Actually Runs Faster | Why weight-only quantization speeds up small-batch decode and can slow down large-batch prefill |
| [0020](lessons/0020-hardware-and-kernel-support.md) | Hardware and Kernel Support | Which formats a GPU computes in natively, which it only stores, and what a missing kernel costs |
| [0021](lessons/0021-perplexity-and-its-limits.md) | Perplexity and Its Limits | What perplexity measures, why a small change can hide large answer flips, and what to measure instead |
| [0022](lessons/0022-an-honest-quantization-eval.md) | An Honest Quantization Eval | Compare a quantized model with its baseline on the same harness and tasks, and report what it lost and where |
| [0023](lessons/0023-quantized-checkpoints.md) | Quantized Checkpoints | What a quantized safetensors checkpoint stores, and how its quantization config tells a loader to read it |
| [0024](lessons/0024-gguf-quant-types.md) | GGUF Quant Types | What a GGUF type name such as Q4_K_M means, and what the importance matrix changes |
| [0025](lessons/0025-choosing-a-scheme.md) | Choosing a Scheme | Pick a format and method from the model, the hardware, the batch shape and the quality bar |
| [0026](lessons/0026-reviewing-a-quantization-claim.md) | Reviewing a Quantization Claim | Review "4-bit with no quality loss" by naming what the measurement hid, and roll out a quantized model others depend on |
| [0027](lessons/0027-when-the-usual-answer-is-wrong.md) | When the Usual Answer Is Wrong | Recognise when 4-bit weights or a standard recipe is the wrong call, and settle the dispute from the primary source |

## Reference

- [Glossary](GLOSSARY.md): canonical terms for this topic
- [Resources](RESOURCES.md): trusted sources, each annotated with what it covers
- [Number Formats](reference/number-formats.md): bit layouts, range and precision of each format, and memory arithmetic, from stage 1
- [The Quantization Mapping](reference/quantization-mapping.md): the quantize and dequantize formulas, range choice, granularity and outlier fixes, from stages 2 and 3
- [Weight PTQ Methods](reference/weight-ptq-methods.md): round-to-nearest, GPTQ and AWQ side by side, and what the calibration set does, from stage 4
- [Activations and the KV Cache](reference/activations-and-kv-cache.md): weight-only against weight-and-activation, SmoothQuant, rotations and KV-cache quantization, from stage 5
- [QAT and Hardware](reference/qat-and-hardware.md): how QAT works and when it pays, and what makes a scheme run faster, from stages 6 and 7
- [Measuring and Storing](reference/measuring-and-storing.md): an honest quantization eval, and how to read a quantized checkpoint or GGUF type, from stages 8 and 9
- [Quantization Review Checklist](reference/quantization-review-checklist.md): choosing a scheme and the questions to ask of someone else's quantization claim, from stage 10

## How this works

Each lesson is short and self-contained. Answer keys are collapsed: recall first, then open them. The real-world reps matter more than the reading, and spacing them out is the point. Anything still unclear at the end of a lesson is worth chasing to its primary source before moving on.
