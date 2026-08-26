# Lesson 20 — Judging a New PEFT Variant

**Mission link:** "Read a new PEFT paper and judge whether its claimed win would survive on your own task" is the last item on the success list. This lesson is that skill.
**Primary source:** [Docs: LoRA variants — Hugging Face PEFT](https://huggingface.co/docs/peft/main/en/developer_guides/lora)
**Prerequisites:** [Lesson 19](0019-when-dora-wins.md), [Lesson 17](0017-what-qlora-costs.md)

## Warm-up

1. ▢ Under what condition is DoRA the right choice over more rank?

<details markdown="1"><summary>Check</summary>

When rank is pinned low by something you cannot remove — usually overfitting risk on a small dataset.

</details>

2. ▢ What must be equal for two runs to be comparable?

<details markdown="1"><summary>Check</summary>

Everything except the single variable under test: data, split, seed, rank, alpha, learning rate, schedule, steps.

</details>

3. ▢ Which two quality costs does quantisation have, and how are they separated?

<details markdown="1"><summary>Check</summary>

Base degradation before training, and worse adapter training on a degraded base. Isolate the first by evaluating quantized and unquantized bases with no adapter.

</details>

## Know this

New parameter-efficient fine-tuning methods appear constantly. Most do not matter to you. The skill is triage, not enthusiasm.

### The landscape, organised by what they change

Rather than memorising methods, learn the axes. Almost every variant modifies one of four things.

**The scaling.** rsLoRA ([arXiv:2312.03732](https://arxiv.org/abs/2312.03732)) replaces the `α/r` divisor with `α/√r`, arguing `α/r` over-damps at high rank. Cheap, one flag, matters when you work at high rank.

**The learning rates.** LoRA+ ([arXiv:2402.12354](https://arxiv.org/abs/2402.12354)) uses a higher learning rate for `B` than `A`, arguing the two factors should not share one rate given their different roles and scales. Cheap, and a genuinely different knob from anything in Lesson 9.

**The initialisation.** Instead of random `A` and zero `B`:
- **PiSSA** ([arXiv:2404.02948](https://arxiv.org/abs/2404.02948)) initialises from the principal singular components of `W₀`, so the adapter starts aligned with the weight's dominant directions.
- **OLoRA** initialises via QR decomposition of `W₀`.
- **LoftQ** ([arXiv:2310.08659](https://arxiv.org/abs/2310.08659)) initialises the adapter to compensate for quantisation error, specifically for the QLoRA setting.

Note that these all give up the zero-initialisation property from Lesson 9 — the model no longer starts identical to the base. That is a deliberate trade, and it is the thing to scrutinise.

**The structure.**
- **AdaLoRA** ([arXiv:2303.10512](https://arxiv.org/abs/2303.10512)) allocates rank adaptively across layers instead of using one rank everywhere, on the grounds that layers differ in how much adaptation they need.
- **VeRA** ([arXiv:2310.11454](https://arxiv.org/abs/2310.11454)) shares frozen random `A` and `B` across layers and trains only small scaling vectors, cutting adapter size drastically.
- **DoRA** decouples magnitude from direction, as in Lesson 18.

In PEFT most of these are a config flag or an `init_lora_weights` value rather than a separate code path, which makes trying them cheap and makes reading the config surface a fast way to see what the library considers established.

### The triage questions

When a new method appears, ask these in order. You can usually stop early.

**1. What does it change, on which of the four axes?** If you cannot answer this from the abstract and one figure, the paper is either poorly written or you are not the audience yet. This question alone filters most things.

**2. What is the baseline?** The most common way to inflate a result is a weak baseline. Watch for: LoRA at a rank the authors chose, attention-only targets when all-linear is the modern default, a learning rate tuned for the new method but inherited for the baseline. **A method that beats an untuned LoRA has not been shown to beat LoRA.**

**3. Is the gain larger than the noise?** Look for seed variance or confidence intervals. If the paper reports single numbers with no spread, and the gain is a point or two, the result is not yet distinguishable from noise. This is extremely common.

**4. What does it cost?** Step time, implementation complexity, whether it merges cleanly, whether it composes with quantisation, whether an implementation you trust exists. A 1% gain for a 30% slowdown is a bad trade in most settings.

**5. Does its mechanism apply to your regime?** DoRA's benefit lives at low rank. LoftQ's lives in quantized training. rsLoRA's lives at high rank. A method whose mechanism addresses a constraint you do not have will not help you, and this is predictable *before* running anything.

**6. Has anyone independent reproduced it?** Practitioner communities test methods on real tasks quickly and are blunt about what fails to replicate. This is often faster and more informative than reading the paper twice.

### Three reliable warning signs

- **Gains reported only on benchmarks, never on a task with a deployment.** Benchmarks are proxies and are heavily optimised against.
- **Comparison against an attention-only LoRA baseline** in a paper written after all-linear became standard practice. Either uninformed or convenient.
- **No cost accounting.** Every method has a cost. A paper that does not state its own is not being straight with you, and the omission is usually the interesting part.

### The default position

**LoRA at adequate rank on all linear layers, with a tuned learning rate, is a strong baseline that is hard to beat by much.** That is the practical upshot of the "LoRA without regret" line of work, and it should be your starting point and your comparison.

A new variant needs to beat *that*, on your task, by more than your seed noise, for less cost than raising rank would have. Most do not clear the bar. Knowing this is not cynicism — it is what lets you spend attention on the few that do.

## Practice

1. ▢ Name the four axes a PEFT variant can modify, with one example each.

<details markdown="1"><summary>Check</summary>

Scaling (rsLoRA), learning rates (LoRA+), initialisation (PiSSA, OLoRA, LoftQ), structure (AdaLoRA, VeRA, DoRA).

Knowing the axes means a new method is classifiable on sight rather than needing to be learned from scratch.

</details>

2. ▢ A paper reports its method beating LoRA by 2.1 points, with LoRA at rank 8 on attention modules only. What is your concern?

<details markdown="1"><summary>Check</summary>

The baseline is weak by current standards. All-linear targets at higher rank is the modern default and is substantially stronger than attention-only rank 8.

The method may well beat that weak baseline and still lose to a properly configured LoRA. The comparison as published does not tell you.

</details>

3. ▢ Which paper property most undermines a claimed 1.5-point gain?

   - a) The absence of any reported seed variance or intervals
   - b) The use of a smaller model than you intend to use
   - c) The absence of a released reference implementation
   - d) The evaluation on only three separate downstream tasks

<details markdown="1"><summary>Check</summary>

**a)** The absence of any reported seed variance or intervals.

Without a spread, a 1.5-point gain cannot be distinguished from run-to-run noise, which is often of that size. The others are real limitations but do not undercut the central claim the way missing variance does.

</details>

4. ▢ LoftQ initialises the adapter to compensate for quantisation error. In which regime would you predict it helps, and where would you predict nothing?

<details markdown="1"><summary>Check</summary>

It should help when training against a quantized base, most visibly at aggressive quantisation and on smaller models where quantisation error is proportionally more damaging.

It should do nothing for an unquantized bf16 base — there is no quantisation error to compensate for, so the mechanism has no purchase.

</details>

5. ▢ PiSSA gives up zero initialisation. Why does that matter, and what would you check?

<details markdown="1"><summary>Check</summary>

Zero initialisation guarantees the adapted model starts identical to the base, so training begins from known-good weights and any degradation is attributable to training.

Giving that up means the model starts perturbed. Check for early instability, and check whether the perturbation has damaged capabilities outside your task — a regression suite (Lesson 24) run at step zero, before training, is the direct test.

</details>

6. ▢ What is the baseline every new variant must beat, and why is it hard?

<details markdown="1"><summary>Check</summary>

LoRA at adequate rank across all linear layers with a tuned learning rate.

It is hard because it already has enough capacity and coverage to approach full fine-tuning on many supervised tasks. When the baseline is near a ceiling, there is little headroom left for a mechanism refinement to claim.

</details>

## Real-world reps

- [ ] Pick one variant from this lesson you have not used. Run the six triage questions against its paper and write a one-paragraph verdict for your own task.
- [ ] Read the `init_lora_weights` options in your installed PEFT version. Map each to a method and an axis.
- [ ] Search a practitioner community for independent reports on that method. Compare what they found against what the paper claimed.
- [ ] Tomorrow: run your chosen variant against a properly tuned all-linear LoRA baseline, three seeds each. Record whether the gain survives.

## Going further

- [Docs: LoRA variants — Hugging Face PEFT](https://huggingface.co/docs/peft/main/en/developer_guides/lora)
- [Docs: "LoRA Without Regret" — Hugging Face TRL](https://huggingface.co/docs/trl/main/en/lora_without_regret)
- [EleutherAI Discord](https://www.eleuther.ai/community) — where claims get tested against people who read papers critically
- [r/LocalLLaMA](https://www.reddit.com/r/LocalLLaMA/) — fast, blunt replication reports

---

Stuck on any of this, or unsure whether an answer counts? Bring it back to the session — that's what your teacher is for.
