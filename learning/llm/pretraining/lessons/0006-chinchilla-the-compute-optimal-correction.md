---
title: 6. Chinchilla: The Compute-Optimal Correction
description: Why model size and token count should scale together, and how to turn a compute budget into a token count
type: lesson
---

# Lesson 6. Chinchilla: The Compute-Optimal Correction

**Mission link:** "Given a parameter count and a compute budget, compute the compute-optimal token count and defend it against a Kaplan-style undertrained alternative" is the third bullet under Success looks like. Lesson 5 covered Kaplan et al.'s recommendation; this lesson covers the wider study that overturned it, and the arithmetic for applying it.
**Primary source:** [Paper: "Training Compute-Optimal Large Language Models", Hoffmann et al., 2022](https://arxiv.org/abs/2203.15556)
**Prerequisites:** [Lesson 5](0005-scaling-laws-what-kaplan-predicted.md)

## Warm-up

1. ▢ Per Kaplan et al., for a fixed compute budget, does optimally compute-efficient training mean training the largest affordable model on comparatively little data, or a smaller model on as much data as the budget allows?

<details markdown="1"><summary>Check</summary>

The largest affordable model, trained on comparatively little data and stopped before convergence. Larger models being more sample-efficient is what makes that the recommended allocation of a fixed budget.

</details>

2. ▢ GPT-3 trained a 175-billion-parameter model on 300 billion tokens. Roughly how many tokens is that per parameter?

<details markdown="1"><summary>Check</summary>

About 1.7 tokens per parameter (300 billion divided by 175 billion).

</details>

## Know this

### A much larger sweep, a different answer

Hoffmann et al. ran the same kind of scaling-law study Kaplan et al. did, but far larger and more carefully controlled: over 400 models, ranging from 70 million to more than 16 billion parameters, trained on between 5 billion and 500 billion tokens. Fitting a scaling law to that sweep, they reached a different practical conclusion: for compute-optimal training, model size and the number of training tokens should be scaled up **equally**. Doubling the compute budget means doubling both the model size and the token count, not, as Kaplan et al.'s recommendation implied, spending nearly all of the extra compute on a bigger model.

### The approximation that makes this arithmetic

Both papers use the same rough approximation for how much compute a training run costs: `FLOPs(N, D) ≈ 6ND`, where `N` is the parameter count and `D` is the number of training tokens. Hoffmann et al. checked this approximation directly against a more exact FLOP count for a range of model sizes and found the difference small enough not to affect their conclusions. That means a compute budget `C`, a parameter count `N`, and a token count `D` are not three independent choices: fixing any two determines the third, via `D ≈ C / (6N)`.

### Chinchilla, and the numbers behind the headline

Hoffmann et al. trained a model, Chinchilla, at 70 billion parameters on 1.4 trillion tokens, using the same training compute Gopher (a 280-billion-parameter model) had used. That is roughly 20 tokens for every parameter (1.4 trillion divided by 70 billion). Their own optimal-allocation projections for other compute budgets land in a similar range without landing on the exact same number every time: a 175-billion-parameter compute-optimal model is projected to want over 4.2 trillion tokens (about 24 per parameter), and a 280-billion-parameter one about 6.8 trillion tokens (about 24 per parameter) at a larger budget. The right takeaway is "roughly 20 to 25 tokens per parameter at compute-optimal allocation across the range this paper checked," not a single universal constant.

Set next to that, GPT-3's 175 billion parameters on 300 billion tokens, about 1.7 tokens per parameter from this lesson's warm-up, is far below that range. That gap is exactly what the Chinchilla paper's abstract means by calling contemporary large language models "significantly undertrained": the same training compute could have gone toward a smaller model trained to a lower loss, or the same-size model trained on several times more data, and either would have used the compute better than what was actually spent.

### The result that made the correction stick

Trained at Gopher's compute budget but at one quarter of its parameter count and on four times its token count, Chinchilla uniformly and significantly outperformed Gopher (280B), GPT-3 (175B), Jurassic-1 (178B), and Megatron-Turing NLG (530B), several of them several times its size, across a wide range of downstream evaluations, including a then-state-of-the-art 67.5% on MMLU, more than 7 points above Gopher. Being a quarter of Gopher's size also made Chinchilla considerably cheaper to run at inference, a separate, deployment-time benefit that compute-optimal training buys on top of the training-time argument this lesson makes.

## Practice

1. ▢ A team is training a model with 13 billion parameters and wants to land in Chinchilla's roughly-20-to-25-tokens-per-parameter range. About how many training tokens does that imply?

<details markdown="1"><summary>Check</summary>

Roughly 260 to 325 billion tokens (13 billion times 20 to 25). Either end of that range is a defensible answer; a number far outside it, such as GPT-3's 1.7-per-parameter ratio, is not.

</details>

2. ▢ A team has a compute budget of `1.2 × 10^22` FLOPs and plans to train a 10-billion-parameter model. Using `FLOPs(N, D) ≈ 6ND`, about how many tokens does that budget afford?

<details markdown="1"><summary>Hint</summary>

Solve `D ≈ C / (6N)` with `C = 1.2 × 10^22` and `N = 10^10`.

</details>

<details markdown="1"><summary>Check</summary>

About 200 billion tokens: `1.2 × 10^22 / (6 × 10^10) = 2 × 10^11`, which is 200 billion, about 20 tokens per parameter and squarely inside the range this lesson gives.

</details>

3. ▢ Which best characterizes the practical difference between Kaplan et al.'s recommendation and Hoffmann et al.'s correction, for a fixed compute budget?

    - a) Kaplan recommends spending most of the budget on a bigger model with comparatively little data; Hoffmann recommends scaling model size and token count equally
    - b) The two papers reach identical recommendations, only phrased differently
    - c) Kaplan says model size is irrelevant to loss; Hoffmann says only model size matters
    - d) Hoffmann argues a bigger model is always worse than a smaller one at the same compute

<details markdown="1"><summary>Check</summary>

**a)** is the actual difference this lesson and Lesson 5 walk through. (b) erases a real, practically consequential disagreement between the two papers. (c) and (d) do not describe either paper's claims.

</details>

4. ▢ GPT-3 trained 175 billion parameters on 300 billion tokens, about 1.7 tokens per parameter. Per Chinchilla's compute-optimal range of roughly 20 to 25 tokens per parameter, was GPT-3 closer to over-trained or under-trained on data, relative to its size?

<details markdown="1"><summary>Check</summary>

Under-trained. Its ratio is more than ten times below the range Chinchilla's results imply is compute-optimal, meaning the same training compute could plausibly have gone to a smaller model trained to a lower loss, or the same 175-billion-parameter model trained on substantially more data.

</details>

## Real-world reps

- [ ] Find the published parameter count and training-token count for an open model released after 2022 (Llama, Mistral, or similar all publish both). Compute its tokens-per-parameter ratio and compare it to this lesson's roughly-20-to-25 range.
- [ ] Using `FLOPs(N, D) ≈ 6ND`, estimate the training compute (in FLOPs) that GPT-3's actual training run (175 billion parameters, 300 billion tokens) used, and separately estimate what compute a compute-optimal 175-billion-parameter run would have needed at 4.2 trillion tokens. Compare the two numbers.
- [ ] Tomorrow: pick a hypothetical compute budget of your choosing (any order of magnitude), and work out, on paper, both a Kaplan-style allocation (favor a much larger model, hold tokens comparatively fixed) and a Chinchilla-style allocation (scale both together) for that same budget. Write down the two resulting `(N, D)` pairs side by side.

## Going further

- [Paper: "Training Compute-Optimal Large Language Models", Hoffmann et al., 2022](https://arxiv.org/abs/2203.15556)
- [Resources](../RESOURCES.md)

---

Stages 1 and 2 decided what the model trains on and how it gets tokenized; this stage decided how much of it to use for a given size. Stage 4 turns to how a training run actually gets that much compute onto more than one device at once.

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
