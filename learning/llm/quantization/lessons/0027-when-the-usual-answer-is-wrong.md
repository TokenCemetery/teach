---
title: "27. When the Usual Answer Is Wrong"
description: Recognise when 4-bit weights or a standard recipe is the wrong call, and settle the dispute from the primary source
type: lesson
---

# Lesson 27. When the Usual Answer Is Wrong

**Mission link:** The track ends with trusting you to make the call on a quantization and to explain it to someone else. "Use 4-bit weights" and "AWQ beats GPTQ" are the usual answers, and each is true for some models, tasks and hardware and false for others. This lesson is the method for finding out which, and the cases where the usual answer fails.
**Primary source:** [Paper: "Scaling Laws for Precision", Kumar et al., 2024](https://arxiv.org/abs/2411.04330), sections 1 to 3
**Prerequisites:** [Lesson 25](0025-choosing-a-scheme.md), [Lesson 26](0026-reviewing-a-quantization-claim.md), [Post-training quantization](../GLOSSARY.md), [Compute-bound](../GLOSSARY.md), [Weight-only quantization](../GLOSSARY.md)

## Warm-up

1. ▢ Why does one massive activation or outlier feature ruin a per-tensor scale, and which fix shrinks the group instead of keeping outliers in high precision?

<details markdown="1"><summary>Check</summary>

The scale is set by the largest value, so one huge value leaves almost all the others on a few levels near zero. Per-group scales shrink the group so the outlier only wastes the levels of its own group (lessons 7, 8 and 6).

</details>

2. ▢ What does a calibration set contribute to GPTQ and to AWQ, and how does a mismatched one show up?

<details markdown="1"><summary>Check</summary>

Activation statistics from representative inputs: GPTQ uses them for second-order error compensation, AWQ to find which weight channels meet large activations. A mismatched set shows up as a model that scores well on text like the calibration data and worse on the traffic it was not like (lessons 10, 11 and 12).

</details>

3. ▢ What is a flip, and why can it be large when accuracy is unchanged?

<details markdown="1"><summary>Check</summary>

An answer that changed from correct to incorrect or the reverse between baseline and quantized model. Gains and losses cancel in the average, so accuracy can be equal while many individual answers move (lessons 21 and 26).

</details>

## Know this

### The method

A usual answer arrives as a slogan without its conditions. Four steps decide whether it holds for you.

1. **Find the primary source.** The paper, not the post that cites it, read for what was actually measured.
2. **Check the model, the size and the date.** Which model families, how big, trained on how much, measured when. A result on 2022 models says little about a 2024 recipe.
3. **Check what the claim covers.** Zero-shot accuracy against total bits is not serving throughput, and an average over academic tasks is not open-ended chat.
4. **Test on your own tasks.** If the source and your case differ, the result that settles it is yours (lesson 22).

None of the cases below says the usual answer is always wrong. Each says what its source supports, and where it stops.

### Case 1: a heavily trained model

Kumar et al. fit "precision-aware" scaling laws and find that the degradation from post-training quantization increases as a model is trained on more data, "eventually making additional pretraining data actively harmful" ([abstract](https://arxiv.org/abs/2411.04330)). Their intuition: a model trained on more data compresses more information into its weights, so perturbing them hurts more. They call models with a very high ratio of training tokens to parameters "overtrained", and note that Llama-3-8B is trained to a ratio of about 2000.

Read the scope. They fit their laws on more than 465 pretraining runs and validate on models up to 1.7B parameters trained on up to 26B tokens. They note that an unreasonable amount of data is needed for extra pretraining to turn harmful at commonly used precisions such as 8-bit, but that on heavily overtrained models the degradation effects become nontrivial around 5 bits and dominant below that. So the claim is that the usual 4-bit answer gets riskier as the training budget per parameter grows, and the evidence is small-scale models plus a fitted law. It is not a measurement of how much a particular Llama 3 checkpoint loses.

A contrasting result exists. Kurtic et al. measured quantized Llama 3.1 models of 8B, 70B and 405B and found W4A16 recovering 99.36 percent of the bf16 average on the Open LLM Leaderboard V1 tasks, using a tuned GPTQ ([Kurtic et al., 2024](https://arxiv.org/abs/2411.02355)). The two do not settle each other. One is a fitted law on small models, the other a measurement of one family with a tuned recipe and averaged tasks. The lesson is to treat a heavily trained model as a reason to measure more carefully, not as a verdict either way.

### Case 2: a small model, or a reasoning model

Kurtic et al. report that the smallest models lose a bit more at INT4. Their reasoning benchmarks, run on DeepSeek-R1-Distill models, show it in numbers: recovery of the bf16 average for W4A16-INT was 99.5 percent for Qwen-32B and 98.3 percent for Llama-70B, 97.2 percent for Llama-8B, and 93.5 percent for Qwen-1.5B, for which W8A8-INT recovered 96.9 percent and W8A8-FP 100.3 percent. A separate study of quantized reasoning models, [Liu et al., 2025](https://arxiv.org/abs/2504.04823), finds lossless quantization achievable with W8A8 or W4A16 but significant accuracy risks at lower bit widths. Its abstract names model size, model origin and task difficulty as the determinants.

Notice the noise too. On AIME24, the 1.5B model scored 30.1 with a reported margin of 5.3 in bf16 and 24.6 with a margin of 5.1 in W4A16, so single-benchmark gaps on small sets overlap their own margins. The average over tasks says the small model lost more. The single task would not prove it.

### Case 3: long context, where the worry does not hold

It is easy to assume long context breaks under quantization. On the RULER long-context benchmark, evaluated from 4k to 128k tokens, Kurtic et al. report average score recovery of at least 98 percent across all three formats, with the 405B model not evaluated because it is prohibitively expensive. That is one benchmark on Llama 3.1 and does not cover quantizing the KV cache, which the paper lists among the things it did not study. It is a good example of a usual worry that the source does not support, for the case it measured.

### Case 4: compute-bound serving

Weight-only 4-bit is the usual answer for memory pressure, and it assumes the work is memory-bound. MARLIN's authors give the arithmetic: one input token takes 2 FLOPs per weight and the GPU can execute about 100 FLOPs in the time it takes to load one 4-bit weight, so memory loading dominates only while the batch is below about 50 ([Frantar et al., 2024](https://arxiv.org/abs/2408.11743)). The same ratio of compute to bandwidth makes a 16-bit weight take four times as long to load, so the crossover for bf16 sits near batch 200. Quantizing the weights moves the crossover down, which is why the gain shrinks as batches grow.

Existing INT4 methods, QServe reports, suffer a 20 to 90 percent dequantization overhead and accelerate low-batch inference only ([Lin et al., 2024](https://arxiv.org/abs/2405.04532)). In Kurtic et al.'s asynchronous serving results W8A8 dominates throughput. For a throughput-bound service on modern hardware, the usual 4-bit answer is the wrong one.

### Case 5: when fp8 is the safer default

If the GPU computes fp8 natively, W8A8-FP is effectively lossless at every model size in Kurtic et al.'s data, and needs no calibration data because they quantize with round-to-nearest. A well-tuned W8A8-INT lost 1 to 3 percent, and needed SmoothQuant and better calibration data at 70B. So where the hardware supports it and the memory fits, fp8 is the lower-risk first try, and 4-bit has to earn its place with a memory or decode-latency need.

### Settling a dispute from the primary source

Two colleagues say two things.

- **"AWQ always beats GPTQ."** Open Kurtic et al.'s Table 1 rather than argue. On the academic benchmarks AWQ led GPTQ by only 0.23 and 0.35 points at 8B and 70B, a near tie. On the real-world benchmarks (Arena-Hard, HumanEval, MBPP) GPTQ led AWQ by 2.9 points at 8B (52.3 against 49.4) and by 0.8 at 70B. They attribute earlier findings that favoured AWQ to suboptimal hyperparameters, and give their own setup: GPTQ with MSE-optimal clipping where the earlier comparison used abs-max, a better calibration set than the C4 default, and group size 128 for both. Then check the noise: on Arena-Hard at 8B, the bf16 model's two runs scored 25.1 and 26.5, so a gap near 1 point is inside run-to-run variation. What the source supports: no method wins always, the ranking moved with the recipe and the task type, and the authors are one team that also chose GPTQ as their method. Run both on your tasks.
- **"Perplexity went up by 0.1, so it is fine."** Ask: relative to which baseline, on which text and window, and what happened to individual answers? Dutta et al. found schemes with accuracy within 0 to 2 percent of the baseline and flips up to 13.6 percent, and compressed models with many flips scoring significantly worse on MT-Bench. A perplexity change of 0.1 is an average and could be small or large depending on what it averages over. The source supports "check flips and an open-ended task", not "0.1 is too small to matter" or "0.1 is too large".

## Practice

1. ▢ A colleague says "AWQ always beats GPTQ." Which table do you open, and what do you check in it?

<details markdown="1"><summary>Check</summary>

Open the head-to-head comparison in Kurtic et al. (Table 1) and check the setup behind it: the same group size, the clipping method, the calibration set, and whether the tasks are academic or open-ended. It shows a near-tie on academic tasks and a GPTQ lead on real-world ones. It does not show GPTQ always wins, only that the AWQ claim has conditions.

</details>

2. ▢ A teammate says "Kumar et al. proved post-training 4-bit will wreck our heavily trained model." What does the paper support?

    - a) A fitted law, so measure your model
    - b) A proof that every 4-bit scheme fails
    - c) A result only about training in fp4
    - d) A measurement of your exact model checkpoint

<details markdown="1"><summary>Check</summary>

**a)** The paper fits laws on runs of up to 1.7B parameters and 26B tokens and finds that more data raises post-training quantization degradation, which is a reason to measure your model, not a verdict on it. (b) overstates a fitted law into a proof. (c) is wrong because it covers post-training quantization as well as training precision. (d) is wrong because it measured no checkpoint of yours.

</details>

3. ▢ Predict, then run. Using MARLIN's figure of about 100 FLOPs per 4-bit weight load and 2 FLOPs per token per weight, predict the batch size below which memory dominates for 4-bit weights and for 16-bit weights if the machine's compute-to-bandwidth ratio is the same. Then run this.

    ```python
    flops_per_weight_load_4bit = 100
    flops_per_token_per_weight = 2
    for name, bytes_per_weight in [("4-bit weights", 0.5), ("16-bit weights", 2.0)]:
        flops_per_byte = flops_per_weight_load_4bit / 0.5
        crossover = flops_per_byte * bytes_per_weight / flops_per_token_per_weight
        print(f"{name:15s} memory-bound below batch about {crossover:.0f}")
    ```

<details markdown="1"><summary>Hint</summary>

A 16-bit weight is four times the bytes of a 4-bit one, so it takes four times as many FLOPs to cover its load.

</details>

<details markdown="1"><summary>Check</summary>

```text
4-bit weights   memory-bound below batch about 50
16-bit weights  memory-bound below batch about 200
```

The 4-bit figure is MARLIN's own estimate, and the 16-bit one is this arithmetic on the same assumption, not a measurement. The point stands without exact numbers: quantizing the weights lowers the batch size at which a service becomes compute-bound, so a service that runs large batches gains less from weight-only 4-bit.

</details>

4. ▢ From Kurtic et al.'s reasoning table: Qwen-1.5B scored 30.1 (margin 5.3) on AIME24 in bf16 and 24.6 (margin 5.1) in W4A16-INT, with 93.5 percent average recovery. A colleague says "AIME24 proves 4-bit broke it". What do you say?

<details markdown="1"><summary>Check</summary>

On AIME24 alone the two scores sit within their reported margins of each other, so that benchmark does not prove it. The 93.5 percent average recovery across three tasks, set beside 98 to 99 percent for the larger models, is the stronger evidence that the smallest model lost more. Neither says the model is unusable: the next step is to run your own tasks with enough samples to tell the difference from noise.

</details>

5. ▢ A team has H100 GPUs, enough memory for an 8B model in bf16, and a batch job where throughput is all that matters. A colleague proposes 4-bit AWQ "because 4-bit is standard". Make the case against, and say what would change your mind.

<details markdown="1"><summary>Check</summary>

The job is compute-bound at large batches, where weight-only 4-bit gains little and its dequantization can cost throughput (MARLIN, QServe), while W8A8-FP is effectively lossless in Kurtic et al.'s data and dominates their asynchronous throughput results on hardware with native fp8. Memory is not a constraint. What would change your mind: a measured throughput and quality comparison on your own batch size and tasks showing the 4-bit kernel ahead, or a memory limit that forced a bigger model than fits at 8 bits.

</details>

## Real-world reps

- [ ] Take one quantization rule of thumb you rely on (for example "4-bit is fine") and trace it to the paper. Write the models, the sizes, the year and what was measured, and where your case differs.
- [ ] Open Table 1 of Kurtic et al. and write the one-line setup differences between their GPTQ and AWQ runs, so you can answer the next "which is better" argument from the table.
- [ ] Tomorrow: for the model you would most like to quantize, write the one case from this lesson most likely to apply to it, and the measurement that would show whether it does.

## Going further

- [Quantization Review Checklist](../reference/quantization-review-checklist.md)
- [Paper: "Scaling Laws for Precision", Kumar et al., 2024](https://arxiv.org/abs/2411.04330)
- [Paper: "Give Me BF16 or Give Me Death? Accuracy-Performance Trade-Offs in LLM Quantization", Kurtic et al., 2024](https://arxiv.org/abs/2411.02355)
- [Paper: "Quantization Hurts Reasoning? An Empirical Study on Quantized Reasoning Models", Liu et al., 2025](https://arxiv.org/abs/2504.04823)
- [Resources](../RESOURCES.md)

---

This is the end of the track, and the habit it was built for is the one in this lesson: a quantized model is a claim about a number format, a method, a kernel and a set of tasks, so find where the claim comes from, check what it covered, and measure on your own tasks before you defend it to anyone else.

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
