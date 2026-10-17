---
title: "15. GKD and MiniLLM"
description: Sampling from the student and scoring with the teacher, and the divergence and mixing choices that come with it
type: lesson
---

# Lesson 15. GKD and MiniLLM

**Mission link:** The mission asks you to run on-policy distillation and choose its settings, which takes knowing what GKD's two knobs do, what MiniLLM does differently, and which results came from which task.
**Primary source:** [Paper: "On-Policy Distillation of Language Models: Learning from Self-Generated Mistakes", Agarwal et al., 2023](https://arxiv.org/abs/2306.13649), sections 2 to 4
**Prerequisites:** [Lesson 5](0005-forward-and-reverse-kl.md), [Lesson 14](0014-exposure-bias.md), [Generalized knowledge distillation](../GLOSSARY.md), [On-policy distillation](../GLOSSARY.md), [Reverse KL](../GLOSSARY.md)

## Warm-up

1. ▢ Which sequences does an on-policy distillation step train on, and which model decides them?

<details markdown="1"><summary>Check</summary>

Sequences the student generates during training, so the student decides them. The teacher only scores each token the student chose. Training on fixed sequences, whether human or teacher-written, is [off-policy](../GLOSSARY.md).

</details>

2. ▢ Forward KL pushes the student to cover every mode of the teacher and reverse KL pushes it to commit to one. Which of the two risks putting probability on text the teacher considers unlikely?

<details markdown="1"><summary>Check</summary>

Forward KL, because it penalises missing any region the teacher covers, so a small student stretches over regions it cannot model well. Reverse KL penalises probability where the teacher has little, so it avoids that at the cost of diversity.

</details>

3. ▢ What is the difference between exposure bias and a student simply being too small?

<details markdown="1"><summary>Check</summary>

Exposure bias is about the prefixes: the student trains on prefixes someone else wrote and generates from its own. A student that is too small has a capacity limit on what it can represent, which would remain even if every prefix were its own. On-policy training addresses the first and cannot remove the second.

</details>

## Know this

### GKD: one loop with two knobs

Generalized knowledge distillation (GKD) is one algorithm with two hyperparameters (Agarwal et al., Algorithm 1). At each step it draws a random number. With probability lambda it generates sequences from the student for a batch of prompts. Otherwise it takes a batch from a fixed dataset of ground-truth or teacher-written sequences. Then it updates the student to minimise a divergence between teacher and student token distributions, averaged over positions, with no gradient through the sampling.

Lambda is the **student data fraction**. Lambda 0 is ordinary supervised distillation and lambda 1 is purely on-policy. The paper's "mixed" variants use 0.5. During training the student samples at temperature 1 to keep its sequences diverse.

The second knob is the divergence. GKD uses the generalized Jensen-Shannon divergence, JSD(beta), a bounded mix of the two KL directions. With the paper's convention, beta near 0 behaves like forward KL and beta near 1 like reverse KL, so 0.1, 0.5 and 0.9 are points along that line. TRL's trainer documents the same direction: beta 0.0 approximates forward KL and beta 1.0 reverse KL.

### What the paper found, task by task

The students are T5-small (77M), T5-base (250M) and T5-large (800M) parameters, distilled from a fine-tuned T5-XL of about 3B, so the teacher is 38 times, 12 times and 3.8 times larger. Results are the paper's own on T5, not general facts about LLMs.

| Task | Metric | What worked | Source in paper |
|---|---|---|---|
| XSum summarization | ROUGE-2 | On-policy GKD with JSD(0.9) beat the additional baselines ImitKD and f-distill under greedy and temperature sampling. Mode-seeking divergences did better under temperature sampling, and the divergence mattered little under greedy decoding | Section 4.1, Figures 3 and 4 |
| WMT14 English to German | BLEU | Generalized JSD beat forward and reverse KL, with a smaller gap for the larger student. Student-generated data only beat the other data mixes. Figure 1 used JSD(0.1) | Section 4.2, Figure 6 |
| GSM8K with chain of thought | accuracy | Student-generated chains alone beat fixed or mixed data. Forward KL did well, and reverse KL did well too. Gains held once at least 25% of the data was on-policy | Section 4.3, Figures 8 and 9 |
| Instruction tuning on FLAN | held-out MMLU and BBH | On-policy GKD with reverse KL clearly beat forward KL | Section 4.4, Figure 10 |

The authors' summary is that the best divergence is task-dependent, while on-policy and mixed data consistently beat fixed data. Two other results are worth knowing. On XSum with T5-small, on-policy GKD on a 5% subsample, with no ground-truth summaries, beat supervised KD and ImitKD trained on the full dataset (section 4.1). Averaged over student sizes, the performance gains over the initial student were 2.1 times those of baseline KD on summarization, 1.7 times on translation and 1.9 times on arithmetic reasoning (Introduction).

For instruction tuning the paper's text and its Figure 10 caption disagree on whether the student is T5-base or T5-large, so this lesson does not quote a student size for that task. The teacher reached 52.4% on MMLU and 41% on BBH. The authors hypothesise that reverse KL works there because its mode-seeking nature makes the model zero in on the instruction's main intent, and they present that as a hypothesis, not a finding.

### MiniLLM: reverse KL optimised as a policy

Gu et al. (MiniLLM) reach on-policy training from a different direction. They argue forward KL makes a low-capacity student overestimate low-probability regions of the teacher, and minimise reverse KL over whole sequences instead. Because the expectation is under the student's own distribution, they derive the gradient with the policy gradient theorem and train it like reinforcement learning, with the log-ratio of teacher to student probability as the per-token signal.

Plain policy gradient has problems, and the paper adds three fixes:

| Problem | Fix | Detail |
|---|---|---|
| High variance | Single-step decomposition | The per-token term is computed by summing over the vocabulary instead of by sampling |
| Reward hacking: degenerate text such as repeated phrases scoring well with the teacher | Teacher-mixed sampling | Sample from alpha times the teacher plus (1 minus alpha) times the student at each step, with alpha 0.2 in the experiments |
| Long outputs get small accumulated rewards, so the student learns to output very short or empty answers | Length normalisation | Normalise the accumulated reward by the remaining length |

It also adds clipping and a language-modelling loss on pretraining text to keep general benchmark performance. Training starts from a student fine-tuned on the task data. Note the difference from GKD: MiniLLM's samples come partly from the teacher through the mixing, so it is not purely on-policy, and it optimises a sequence-level objective where GKD averages a token-level divergence.

### MiniLLM's results

The setup is instruction following on 15K Dolly examples, about 12.5K for training, with students from GPT-2 (120M to 760M, teacher GPT-2 1.5B), OPT (1.3B to 6.7B, teacher OPT 13B) and LLaMA (7B, teacher LLaMA 13B). A few cells from Table 1, the average GPT-4 feedback score on DollyEval:

| Student | Fine-tuned only | Standard KD | SeqKD | MiniLLM | Teacher |
|---|---|---|---|---|---|
| OPT 1.3B | 52.6 | 52.7 | 51.0 | 60.7 | 70.3 |
| OPT 6.7B | 67.9 | 68.6 | 69.6 | 70.8 | 70.3 |
| LLaMA 7B | 73.0 | 73.7 | 73.6 | 76.4 | 79.0 |

The GPT-4 metric is the ratio of GPT-4's score for the model's answer to its score for the reference answer, so it is relative, not absolute. The authors also report that students sometimes beat the teacher on Rouge-L and conjecture that this reflects exposure bias in the teacher. On calibration, the student MiniLLM had lower error than forward-KL baselines but still above the teacher: on SST2, ECE 0.099 against the teacher's 0.025 and 0.191 for standard KD (Table 2).

### What you cannot conclude

Each paper tuned its own method on its own students, teachers and metrics, so the numbers above do not rank GKD against MiniLLM. I found no head-to-head comparison in either paper. Compare their ideas, and test both on your own pair.

### A runnable configuration

TRL's `GKDTrainer` exposes both knobs as `lmbda` and `beta` on `GKDConfig`. Its documented defaults are 0.5 for each, with `temperature` 0.9 and `max_new_tokens` 128 for generation, and `seq_kd` off. The docs example below distils Qwen2-1.5B-Instruct into Qwen2-0.5B-Instruct. I did not run it, so check the import path against the TRL version you install, since the current docs place GKD under `trl.experimental`.

```python
from datasets import Dataset
from transformers import AutoModelForCausalLM, AutoTokenizer
from trl.experimental.gkd import GKDConfig, GKDTrainer

tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2-0.5B-Instruct")
student = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2-0.5B-Instruct")
teacher = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2-1.5B-Instruct")

train = Dataset.from_dict({"messages": [[
    {"role": "user", "content": "Hi, how are you?"},
    {"role": "assistant", "content": "I'm great thanks"},
]] * 100})

args = GKDConfig(
    output_dir="gkd-model",
    per_device_train_batch_size=1,
    lmbda=1.0,  # purely on-policy: every batch is student-generated
    beta=1.0,   # generalized JSD at the reverse-KL end
)
trainer = GKDTrainer(model=student, teacher_model=teacher, args=args,
                     processing_class=tokenizer, train_dataset=train)
trainer.train()
```

The two models share a tokenizer because they are the same family, which lesson 6 explained is required for logit distillation. The TRL page's own guidance matches the paper: on-policy data (high `lmbda`) performs better, and the best `beta` depends on the task and evaluation method.

## Practice

1. ▢ In GKD, which settings of lambda and the divergence reproduce (a) supervised distillation and (b) on-policy KD as the paper defines them?

<details markdown="1"><summary>Check</summary>

Both use forward KL. Lambda 0 gives supervised KD, where the student never generates, and lambda 1 gives on-policy KD, where every sequence is the student's. Values in between are the mixed variants. The divergence and the data source are independent knobs, which is why the same forward KL appears in both.

</details>

2. ▢ In GKD's instruction-tuning experiment on FLAN, which pairing did the paper find clearly better than its forward-KL counterpart?

    - a) Forward KL, student samples
    - b) Reverse KL, student samples
    - c) Forward KL, fixed sequences
    - d) Reverse KL, fixed sequences

<details markdown="1"><summary>Check</summary>

**b)** On-policy GKD with reverse KL outperformed the other approaches in section 4.4. (a) is the paper's choice for XSum and GSM8K with greedy decoding, not for instruction tuning. (c) and (d) use fixed data, which the paper found consistently weaker than student-generated data.

</details>

3. ▢ Match each MiniLLM fix to the failure it prevents: (1) teacher-mixed sampling, (2) length normalisation, (3) single-step decomposition. Failures: A, the student returns very short or empty answers. B, high variance in the gradient. C, the student finds degenerate text the teacher scores well.

<details markdown="1"><summary>Check</summary>

(1) goes with C, (2) with A, (3) with B. Teacher-mixed sampling suppresses degenerate samples by mixing the teacher into the sampling distribution. Length normalisation stops long sequences from being penalised by small accumulated rewards. Single-step decomposition computes the per-token term over the whole vocabulary instead of by sampling, which reduces variance.

</details>

4. ▢ A student trained with a MiniLLM-style objective starts emitting a repeated phrase that the teacher assigns high probability. Which trick targets this, and what value did the paper use?

<details markdown="1"><summary>Hint</summary>

The teacher's score is the reward. A degenerate sample that the teacher likes is exploiting that reward.

</details>

<details markdown="1"><summary>Check</summary>

Teacher-mixed sampling, which the paper introduces against reward hacking, with alpha 0.2 throughout its experiments (section 3.1). The value is that paper's choice on its setup, so treat it as a starting point, not a constant.

</details>

5. ▢ Using Table 1 above, what share of the gap between the fine-tuned-only student and the teacher does MiniLLM close for OPT 1.3B and for LLaMA 7B? What can you not conclude from the OPT 6.7B row?

<details markdown="1"><summary>Check</summary>

OPT 1.3B: the gap is 70.3 minus 52.6, which is 17.7, and MiniLLM gains 8.1, about 46%. LLaMA 7B: the gap is 6.0 and MiniLLM gains 3.4, about 57%. In the OPT 6.7B row MiniLLM scores 70.8 against the teacher's 70.3, but that does not show the student is better: the metric is relative to reference answers, the difference is half a point, and it is one model pair.

</details>

6. ▢ You want a pure on-policy run with reverse KL in TRL. Which two config values do you set, and could you run it if you only had the teacher's text?

<details markdown="1"><summary>Check</summary>

`lmbda=1.0` and `beta=1.0`. No: the divergence needs the teacher's distribution at each position of the student's sequence, so you need the teacher model itself, not a stored text dump. With only text you would be back at sequence level (lesson 8). TRL's `seq_kd` option does not change this, since the teacher still gives token-specific feedback.

</details>

## Real-world reps

- [ ] Read section 3.1 of the GKD paper. Write the loss as one line, then circle where lambda and the divergence each enter.
- [ ] Open Table 1 of the MiniLLM paper and pick one student where MiniLLM did not beat the teacher on every column. Write which metric it lost on and by how much.
- [ ] Tomorrow: without notes, write what lambda and beta each control, name one task where reverse KL won in GKD, and name MiniLLM's three fixes.

## Going further

- [On-Policy Distillation](../reference/on-policy-distillation.md)
- [Paper: "On-Policy Distillation of Language Models: Learning from Self-Generated Mistakes", Agarwal et al., 2023](https://arxiv.org/abs/2306.13649)
- [Paper: "MiniLLM: On-Policy Distillation of Large Language Models", Gu et al., 2023](https://arxiv.org/abs/2306.08543)
- [Documentation: "Generalized Knowledge Distillation Trainer", Hugging Face TRL](https://huggingface.co/docs/trl/main/en/gkd_trainer)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
