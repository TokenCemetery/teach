---
title: 13. What Generation Still Gets Wrong
description: The failure modes that survive even correct, well-placed retrieved context, and how they differ from a retrieval failure
type: lesson
---

# Lesson 13. What Generation Still Gets Wrong

**Mission link:** This is the mission's final lesson: retrieval (stages 1 to 6) and prompt construction (lesson 12) can both succeed and the final answer can still be wrong, because generation itself introduces failure modes none of the earlier stages can fix or even detect.
**Primary source:** [Paper: "RAGAS: Automated Evaluation of Retrieval Augmented Generation", Es et al., 2023](https://arxiv.org/abs/2309.15217)
**Prerequisites:** [Lesson 12](0012-prompt-construction-and-context-budget.md), [Chunk](../GLOSSARY.md)

## Warm-up

1. ▢ What does the "lost in the middle" finding show about a chunk that's technically present in the context window?

<details markdown="1"><summary>Check</summary>

Being present in the context window doesn't guarantee a model uses it: information near the beginning or end of a long context is used far more reliably than information buried in the middle, even when everything is within the stated context limit.

</details>

2. ▢ What is the first stage to check when diagnosing wrong retrieved context, and why?

<details markdown="1"><summary>Check</summary>

Chunking, checked first because if the relevant information was never given a coherent representation (split across a boundary, buried in a mixed-topic chunk), no later stage, embedding, index, hybrid weighting, or reranking, can retrieve what was never usable to begin with.

</details>

## Know this

### Correct retrieval doesn't guarantee a faithful answer

Even with the exact right passage retrieved and placed at the start of the prompt (stages 1 to 7 all working correctly), the model can still generate a claim the retrieved passage doesn't actually support, contradicting it outright, or adding a plausible-sounding detail found nowhere in the retrieved text at all. This is a generation-stage failure, sometimes called a lack of **faithfulness** or **groundedness**: the evidence was present and positioned well, but the model's answer didn't stay tied to it.

### Confidently answering when the context doesn't cover the question

When the retrieved context genuinely lacks the answer, a legitimate outcome would be the model saying so. Instead, a model can produce a confident, plausible-sounding answer anyway, fabricated rather than retrieved. This is arguably the most costly generation failure a RAG system can have, precisely because it looks exactly like a good answer: nothing about its surface fluency signals that it isn't actually grounded in anything the system retrieved.

### Ignoring retrieved context in favor of what the model already "knows"

Retrieved context is usually meant to be treated as more current or more specific than whatever the model absorbed during training, which is the entire premise of retrieval-augmented generation in the first place. A model can still default to its own parametric knowledge instead, especially when the retrieved information contradicts something the model saw far more often during training. A retrieved document stating a policy changed to 60 days, answered with the old, more commonly seen 30-day figure from pretraining, is exactly this failure: the correct, current information was retrieved and available, and the model answered from memory instead.

### Misattributing a claim to the wrong source

When multiple retrieved passages are provided together, a model can use the right information but cite the wrong one as its source, mixing up which chunk actually supports which claim. This matters directly whenever the system needs to show citations: a plausible-looking citation that points at the wrong passage is its own kind of failure, separate from whether the underlying claim was even correct.

### Checking for these is generation evaluation, not retrieval evaluation

Stage 6 diagnosed whether retrieval found and ranked the right chunk. None of that machinery checks whether the generated answer actually stayed faithful to what was retrieved; that is a distinct question, checked by comparing each claim in the generated answer against the retrieved context it's supposed to rest on, commonly with an LLM-as-judge prompt built specifically for that comparison (the LLM-as-judge design and calibration discipline `llm/evals` covers, applied here to a different question than whether retrieval succeeded). Building and defending that evaluation is `llm/evals`' territory, linked to rather than restated here; what this lesson establishes is that the question exists at all, separately from everything stages 1 to 7 already checked.

## Practice

1. ▢ The correct chunk was retrieved and placed near the start of the prompt, but the generated answer includes a specific detail that appears nowhere in the retrieved text. Is this a retrieval failure? What is it instead?

<details markdown="1"><summary>Check</summary>

Not a retrieval failure: the correct chunk was retrieved and well positioned. This is a faithfulness (groundedness) failure at the generation stage, where the model added a claim the retrieved evidence doesn't actually support.

</details>

2. ▢ The retrieved context genuinely doesn't contain the answer to the question, but the model produces a confident, plausible-sounding answer anyway. Why is this considered the most costly kind of generation failure in a RAG system?

<details markdown="1"><summary>Check</summary>

Because it's indistinguishable, on the surface, from a genuinely good answer. A fabricated but fluent answer gives no visible signal that it isn't actually grounded in the retrieved context, unlike an obviously broken or nonsensical response, which makes it far more likely to be trusted and acted on incorrectly.

</details>

3. ▢ A retrieved document states a company's return policy changed to 60 days, but the model's answer states the old 30-day policy. What's the likely cause, and why does it matter that retrieved context is usually meant to be treated as authoritative?

<details markdown="1"><summary>Check</summary>

The model likely defaulted to its own parametric knowledge, the older, more commonly seen figure from training, instead of the retrieved, more current information. It matters because retrieval-augmented generation exists specifically to supply information more current or specific than what training absorbed; a model that ignores retrieved context in favor of memory defeats the entire premise of the system.

</details>

4. ▢ How would you evaluate whether a generated answer is actually faithful to the retrieved context, as a question distinct from whether retrieval found the right context in the first place?

<details markdown="1"><summary>Check</summary>

Compare each claim in the generated answer against the retrieved context it's supposed to rest on, checking whether the context actually supports it, commonly using an LLM-as-judge prompt built specifically for that comparison. This is a separate check from stage 6's retrieval diagnosis, since it assumes the right context was retrieved and asks only whether the generated answer stayed grounded in it.

</details>

5. ▢ Which claim is true of generation-stage failures in a RAG system?

   - a) They can only occur when retrieval has already failed to find the right context
   - b) They can occur even when retrieval and prompt construction both succeeded, since faithfulness to retrieved context is a separate property generation can still get wrong
   - c) Misattributing a claim to the wrong source document is the same failure as fabricating an unsupported claim
   - d) A model always prefers retrieved context over its own parametric knowledge, since that's the reason retrieval was added

<details markdown="1"><summary>Check</summary>

**b)** Every failure mode in this lesson assumed correct retrieval and good placement, and still occurred. (a) is false: that's exactly the distinction this lesson draws. (c) is false: they're different failures, one about which source is cited, the other about whether the claim is supported at all; a model can misattribute a claim that's otherwise correct and supported. (d) is false: a model can and does sometimes default to parametric knowledge even when contradicting retrieved context, which is exactly the policy-example failure.

</details>

## Real-world reps

- [ ] For a RAG system you run or plan to run, hand-check a handful of generated answers against their retrieved context, claim by claim, and note whether any detail lacks support in what was actually retrieved.
- [ ] Find a case where the retrieved context genuinely didn't cover a question, and check whether the system said so or fabricated a plausible-sounding answer instead.
- [ ] Tomorrow: revisit this workspace's mission in `README.md` and confirm, in your own words, that you can now design a retrieval pipeline, diagnose which stage is at fault when it fails, and name what generation itself can still get wrong even when retrieval succeeds.

## Going further

- [Paper: "RAGAS: Automated Evaluation of Retrieval Augmented Generation", Es et al., 2023](https://arxiv.org/abs/2309.15217)
- [Paper: "Lost in the Middle: How Language Models Use Long Contexts", Liu et al., 2023](https://arxiv.org/abs/2307.03172)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
