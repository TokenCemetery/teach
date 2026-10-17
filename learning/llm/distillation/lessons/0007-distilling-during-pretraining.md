---
title: "7. Distilling During Pretraining"
description: How Gemma 2 and Minitron used a teacher's distribution as a training signal at scale, and what storing logits costs
type: lesson
---

# Lesson 7. Distilling During Pretraining

**Mission link:** The mission asks you to write the token-level loss and say when it cannot be used, and this lesson shows that loss as the training signal of two real model families, with the cost of keeping the teacher's distributions counted in bytes.
**Primary source:** [Paper: "Gemma 2: Improving Open Language Models at a Practical Size", Gemma Team, 2024](https://arxiv.org/abs/2408.00118)
**Prerequisites:** [Lesson 6](0006-the-tokenizer-constraint.md), [Token-level distillation](../GLOSSARY.md), [Logit](../GLOSSARY.md), [Top-k logits](../GLOSSARY.md)

## Warm-up

1. ▢ Why does a Llama student with a Qwen teacher rule out the plain token-level loss, even when both give you full logits?

<details markdown="1"><summary>Check</summary>

The loss compares probability i in the student's row with probability i in the teacher's, and different tokenizers make index i a different token, with possibly different sizes and positions. Stage 2's workarounds are a cross-tokenizer loss or a student from the teacher's family.

</details>

2. ▢ Which direction of KL does a mode-covering student minimize, and which setting did Minitron find it best in?

<details markdown="1"><summary>Check</summary>

[Forward KL](../GLOSSARY.md). Minitron found it better than reverse KL when retraining pruned base models, with an LM loss of 2.155 against 2.665 for a depth-pruned Minitron 8B (Table 16 of their paper). That is one setting, and lesson 5 gives the instruction-tuning evidence for the other direction.

</details>

## Know this

This lesson teaches the distillation half of two training recipes. How a pretraining run is organised, from data to hardware, belongs to the [pretraining track](../../pretraining/), and pruning as a method belongs to neither.

### Distillation as the pretraining objective: Gemma 2

The Gemma 2 report trains its 2B and 9B models with knowledge distillation instead of next token prediction. The motivation is that next-token training scales only logarithmically with data, and small models need very long runs to improve. Distillation replaces the one-hot vector at each token with the distribution of next tokens from a large model, which the report says gives richer gradients. Its stated aim is to train for very large numbers of tokens with distillation to simulate training beyond the number of available tokens (introduction).

The facts the report gives:

- The 2B model was trained on 2 trillion tokens, the 9B on 8 trillion, and the 27B on 13 trillion (section 3.1). The 27B was trained from scratch, without distillation.
- The 2B and 9B token counts are more than 50 times the compute-optimal quantity predicted by Hoffmann et al. (introduction).
- The loss is the negative log-likelihood between the teacher's probability of each token given its context and the student's, minimized over the student: the sum of -P_T(x | x_c) log P_S(x | x_c) (section 3.2). That is lesson 4's loss at temperature 1.
- The vocabulary has 256,128 entries (Table 1), inherited from Gemini, and the context length is 8,192 tokens (section 2).

Its ablations use a 7B teacher, not the final one. A 2B student trained on 500B tokens, which the report says is 10 times the compute-optimal number for 2B, scored an average of 60.3 on three benchmarks from scratch and 67.7 distilled (Table 6). With the teacher fixed at 7B, validation perplexity at 200M, 400M and 1B parameters was 23, 19 and 17 from scratch and 21, 17 and 15 distilled (Table 7). The report also says the new 2B, at 2T tokens, improves significantly on Gemma 1's 2B at 3T tokens (section 6.1). These are Google's own comparisons.

### What the report does not say

The report does not name the teacher of the final 2B and 9B models or give its size. It does not describe how the teacher's distribution was supplied to the student: stored, computed alongside training, or approximated. Statements about a sampled or truncated top-k in Gemma 2 are not in the report. The next section computes what each option costs, so you can reason about it without a source for the choice.

### What storing the teacher costs

A distribution over the vocabulary for each training token is large. The script uses Gemma 2's vocabulary and token counts and two assumptions of this lesson, bf16 probabilities at 2 bytes and, for the truncated version, an illustrative k of 256 with a 4-byte token index.

```python
vocab = 256_128            # Gemma 2 vocabulary size (Table 1 of the report)
tokens = {"2B run": 2e12, "9B run": 8e12}

full = vocab * 2           # bf16: 2 bytes per probability
k = 256                    # an illustrative k, not a number from any paper
topk = k * (2 + 4)         # 2-byte probability + 4-byte token index

print("full per token: %d bytes" % full)
print("top-%d per token: %d bytes (%.1fx smaller)" % (k, topk, full / topk))
print("full per 8192-token sequence: %.2f GB" % (full * 8192 / 1e9))
for name, n in tokens.items():
    print(name, "full: %.2f EB" % (full * n / 1e18), " top-%d: %.2f PB" % (k, topk * n / 1e15))
```

Predict the order of magnitude of the full-distribution cost for the 2B run before you run it. The output:

```text
full per token: 512256 bytes
top-256 per token: 1536 bytes (333.5x smaller)
full per 8192-token sequence: 4.20 GB
2B run full: 1.02 EB  top-256: 3.07 PB
9B run full: 4.10 EB  top-256: 12.29 PB
```

Storing full distributions for the 2B run is about an exabyte, and for the 9B run about four. Keeping 256 entries per token cuts that by a factor of 333.5, to petabytes, and the figure still counts training tokens once, with no epochs repeated. Truncation costs something too. The tail mass that is dropped must be handled, by renormalizing or by treating it as one bucket, and the choice changes the target.

There is an alternative that stores nothing: run the teacher alongside the student and read its distribution from the forward pass. Minitron takes that route, and notes that distillation adds the overhead of an additional forward pass on the teacher, so they compare their distilled and conventional runs at equal compute (section 4). Which route a given lab used is not something this lesson claims.

The Minitron authors also tested truncation directly. In their appendix on distillation (A.3), keeping only the top K teacher and student logits for K up to 100 caused a significant drop in accuracy. The drop disappeared for larger K, but the results were no better than not truncating. That is one pruned-model retraining setup, and the K at which truncation stops hurting will differ by vocabulary and model.

### Pruning plus distillation: Minitron

Minitron (Muralidharan et al., 2024) compresses Nemotron-4 15B by pruning it and recovering accuracy by retraining with the original as the teacher. Its student starts as a pruned copy, so it shares the teacher's tokenizer by construction. This lesson takes the distillation half only.

- **Tokens.** The Minitron 8B and 4B models were each retrained on 94 billion tokens. The paper compares Minitron 8B with Nemotron-3 8B, trained on 3.8 trillion, and states the saving as 40 times fewer tokens (Table 2).
- **Distillation against conventional retraining.** For a 4B model they compare at equal compute (Table 11). Training from scratch on 150B tokens gave HellaSwag 46.22 and MMLU 24.36. Pruning 15B to 4B and retraining conventionally on 150B gave 50.85 and 24.57. Pruning and retraining with distillation on 100B tokens gave 51.04 and 37.81. The distilled run uses 100B tokens against 150B because of the teacher's extra forward pass. That is a gain of 4.8 points on HellaSwag and 13.5 on MMLU over training from scratch.
- **Loss.** Forward KL on the logits, at temperature 1, with the logit loss alone better than a weighted mix with the language modeling loss, and no gain from truncating to top K (section 4 and appendix A.3).

The follow-up paper (Sreenivas et al., 2024) applies the recipe to Llama 3.1 8B and Mistral NeMo 12B. It adds a step before distillation: teacher correction. When the original pretraining data is not available, the teacher gives sub-optimal guidance on a different dataset, which the authors attribute to a change in the distribution of sub-word tokens. So they fine-tune the teacher on about 100B tokens of the distillation data first, with warm-up and low learning rates. Then they prune and distill with forward KL on the logits only. Llama-3.1-Minitron 4B was retrained on 94B tokens and MN-Minitron-8B on 380B (Table 4). The paper says the 4B compares favourably with Llama 3.1 8B using 150 times fewer tokens, 94B against 15T, and the 8B outperforms Llama 3.1 8B using 40 times fewer, 380B against 15T (section 5.1). These are NVIDIA's comparisons on their own evaluation.

## Practice

1. ▢ In the report, which Gemma 2 models were trained with distillation, and how many tokens did each see?

    - a) The 2B on 8T and the 27B on 2T
    - b) The 9B on 8T and the 27B on 13T
    - c) All three models were each trained on 13T tokens
    - d) The 2B on 2T and the 9B on 8T

<details markdown="1"><summary>Check</summary>

**d)** The 27B was trained from scratch on 13T tokens, so (b) and (c) wrongly include it. Choice (a) swaps the token counts. The report states the counts in section 3.1.

</details>

2. ▢ With a vocabulary of 256,128 and 2 bytes per probability, how many bytes does one full next-token distribution take, and how many gigabytes does it come to for a single 8,192-token sequence?

<details markdown="1"><summary>Hint</summary>

Multiply the vocabulary by the bytes per entry, then by the sequence length, then divide by one billion.

</details>

<details markdown="1"><summary>Check</summary>

256,128 times 2 is 512,256 bytes per token. Times 8,192 gives 4,196,401,152 bytes, about 4.20 GB for one sequence. A training run has many millions of such sequences, which is why the question of storing versus recomputing exists.

</details>

3. ▢ Keeping the top 256 entries, each with a 2-byte probability and a 4-byte index, how large is one token's record, and how much smaller than the full distribution is that?

<details markdown="1"><summary>Check</summary>

256 times 6 is 1,536 bytes, which is 333.5 times smaller than 512,256. The k of 256 and the byte sizes are assumptions of this lesson, not figures from Gemma 2. The record also leaves out the tail of the distribution, which has to be renormalized or bucketed, and that choice changes the target.

</details>

4. ▢ A forum post says Gemma 2 trained on a stored top-256 teacher distribution. What do you do with that claim?

<details markdown="1"><summary>Check</summary>

Look for it in the report. The report states the loss, the token counts and the ablations, and does not describe how the distribution was supplied. So the claim is unverified from the report. Treat it as unsupported, write down what is missing, and look for a primary source such as the authors' text before relying on it.

</details>

5. ▢ In Minitron's Table 11, pruning plus conventional retraining reached MMLU 24.57 and pruning plus distillation reached 37.81, with distillation on fewer tokens. Why are the token counts 150B and 100B, and what is the table's limit?

<details markdown="1"><summary>Check</summary>

They compare at equal compute, and distillation spends part of its budget on the teacher's forward pass, so it gets 100B tokens against 150B. The table is one 4B model pruned from Nemotron-4 15B. The authors use it to show distillation beats conventional retraining after pruning. It does not show the gain for other teachers, sizes or benchmarks.

</details>

6. ▢ Teacher correction in the follow-up Minitron paper fine-tunes the teacher on about 100B tokens before distilling. When is it needed, and what do the authors blame when it is skipped?

<details markdown="1"><summary>Check</summary>

It is needed when the original pretraining data of the teacher is not available, so the distillation data has a different distribution. The authors say the teacher gives sub-optimal guidance then, and hypothesize it is because the distribution of sub-word tokens differs between the teacher's original data and the data used to distill. The explanation is their hypothesis.

</details>

## Real-world reps

- [ ] Run the storage script with your own vocabulary size and with k set to 64 and 1,024, and write down the three cost ratios.
- [ ] Open the Minitron paper's Table 11 and find the iso-compute marker. Write down which row used the teacher and how many tokens it saw.
- [ ] Tomorrow: without notes, state the three Gemma 2 token counts and the storage arithmetic for one token, then say what the report leaves unsaid about the teacher.

## Going further

- [Distillation Losses](../reference/distillation-losses.md)
- [Paper: "Gemma 2: Improving Open Language Models at a Practical Size", Gemma Team, 2024](https://arxiv.org/abs/2408.00118)
- [Paper: "Compact Language Models via Pruning and Knowledge Distillation", Muralidharan et al., 2024](https://arxiv.org/abs/2407.14679)
- [Paper: "LLM Pruning and Distillation in Practice: The Minitron Approach", Sreenivas et al., 2024](https://arxiv.org/abs/2408.11796)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
