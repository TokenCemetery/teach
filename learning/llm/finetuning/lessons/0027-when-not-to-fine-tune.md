---
title: 27. When Not to Fine-Tune
description: Fine-tuning is sixth on the list, and why that matters
type: lesson
---

# Lesson 27. When Not to Fine-Tune

**Mission link:** The mission ends here: *"who can argue convincingly for prompting or retrieval instead when those would do the job better."* The senior skill is declining the work.
**Primary source:** [Docs: "LoRA Without Regret", Hugging Face TRL](https://huggingface.co/docs/trl/main/en/lora_without_regret)
**Prerequisites:** every previous lesson — this one is the synthesis.

## Warm-up

1. ▢ Which inference phase is bandwidth-bound, and why does that favour smaller models?

<details markdown="1"><summary>Check</summary>

Decode. Each step reads all the weights to produce one token, so speed tracks memory bandwidth and a smaller model is faster nearly in proportion to its size.

</details>

2. ▢ Name the four regression categories.

<details markdown="1"><summary>Check</summary>

General instruction following, format and behavioural compliance, safety and refusal behaviour, adjacent untrained capability.

</details>

3. ▢ What is the baseline a new PEFT variant must beat?

<details markdown="1"><summary>Check</summary>

LoRA at adequate rank on all linear layers with a tuned learning rate.

</details>

## Know this

### The decision, in order

Work down this list. Stop at the first row that solves your problem.

| Approach | Solves | Cost |
|---|---|---|
| Better prompt | Most format and behaviour problems | Minutes |
| Few-shot examples | Format consistency, output shape | Prompt tokens per request |
| Retrieval | Missing or changing knowledge | Retrieval infrastructure |
| Tool use | Calculation, lookup, actions | Tool infrastructure |
| Constrained decoding | Schema validity, absolutely | Serving support |
| **Fine-tuning** | Consistent behaviour, prompt cost, small-model sufficiency | Data, evaluation, maintenance |
| Full fine-tuning | Very large behavioural shifts | Substantially more of everything |

Fine-tuning is sixth. **Most people who want to fine-tune have a problem that one of the first five solves, faster and more reliably.** Reaching row six before exhausting rows one to five is the most common expensive mistake in this field.

Note especially that **constrained decoding solves schema validity completely** — grammar-constrained generation cannot emit invalid JSON. If your entire problem is malformed output, you do not need to train anything.

### The three questions that decide it

**1. Is the problem knowledge or behaviour?**

Knowledge — facts, documents, anything that changes — is retrieval's job. Fine-tuning installs facts unreliably, unverifiably, and staleness requires retraining. Retrieval is accurate, citable, and updated by editing a document.

Behaviour — format, tone, structure, consistency, a decision boundary — is fine-tuning's job. This is where it genuinely excels and where nothing else does as well.

The trap: "the model doesn't know about our product" sounds like a training problem and is a retrieval problem. "The model won't consistently answer in our house style regardless of how I prompt it" sounds like a prompting problem and is a training problem.

**2. Have you actually exhausted prompting?**

Not "tried a few prompts". Exhausted: systematic iteration, few-shot examples, a structured system prompt, and **measured on the same held-out set you would use to evaluate a fine-tune.** Most claims that prompting failed are claims that a handful of unmeasured attempts failed.

If you cannot state prompting's score on your held-out set, you have no baseline, and without a baseline you cannot demonstrate that the fine-tune helped.

**3. Will you maintain it?**

A fine-tune is a living artifact. Base models get superseded, requirements shift, distributions drift, evaluations need updating. If nobody owns it, you are building something that will silently decay while appearing to work — and a stale fine-tune is worse than no fine-tune, because it is trusted.

### When fine-tuning is clearly right

To be fair to the method — these are real and common:

- **High volume with a long prompt.** Moving prompt content into weights repays itself on every request (Lesson 26).
- **A smaller model can then suffice.** The strongest case, because it cuts cost and latency together.
- **Behaviour that resists prompting.** A tone, a format, or a decision boundary the model will not hold consistently no matter how you ask.
- **A narrow task with abundant examples.** Classification, extraction, structured transformation — fine-tuning is excellent and often beats a much larger prompted model.
- **Latency-critical paths.** Shorter prompts and smaller models both help, directly.
- **A domain-specific notation or syntax** genuinely underrepresented in pretraining.

### Combining, rather than choosing

The framing "fine-tune or retrieve" is usually wrong. The strongest systems do both, for different jobs:

**Retrieval supplies the facts. Fine-tuning teaches what to do with them.**

A model fine-tuned to use retrieved context well — cite it, respect it, admit when it is insufficient, decline to invent beyond it — combined with retrieval that supplies current accurate facts, beats either alone. That is an architecture, and recognising it is the senior version of this decision.

### The calibrated position on capability

You have earned a nuanced view here, so hold it precisely.

The old framing — "LoRA is a cheap approximation, full fine-tuning is the real thing" — is largely obsolete. With adequate rank across all linear layers and a properly tuned learning rate, LoRA matches full fine-tuning on typical supervised fine-tuning workloads. **The capability gap has mostly closed for the regime most people work in.**

Which means: if you have decided to fine-tune, adapters are almost certainly the right method. Full fine-tuning is for very large behavioural shifts, continued pretraining on a new domain or language at scale, or research where you need the full parameter space. The remaining question is not "adapter or full" but "should this be trained at all".

### What good judgement sounds like

> "The reported failures are all factual staleness, so this is retrieval, not training. Let me measure a prompted baseline on the held-out set first. If the residual problem after retrieval is format consistency at 40,000 requests a day, then a rank-32 all-linear adapter on a 3B model is worth costing — including the person who will retrain it in six months. I'd want a regression suite covering safety and general instruction following before shipping, because we would be adapting an instruct model."

Nothing in that is a fact you looked up. It is the shape of reasoning this workspace was for.

## Practice

1. ▢ "Our support bot doesn't know about products launched this quarter." Fine-tune or not?

<details markdown="1"><summary>Check</summary>

Not. That is knowledge, and knowledge that changes quarterly — the worst possible fit for fine-tuning, which installs facts unreliably and goes stale immediately.

Retrieval: accurate, citable, updated by editing a catalogue. Fine-tuning might separately be worth it to teach the bot how to *use* retrieved product data well.

</details>

2. ▢ "Prompting didn't work." What do you ask?

<details markdown="1"><summary>Check</summary>

What was measured, on what held-out set, with what score. Also: were few-shot examples tried, was a structured system prompt tried, was constrained decoding tried for a format problem.

Without a measured prompted baseline there is nothing to compare a fine-tune against, so you cannot demonstrate improvement even if you achieve it.

</details>

3. ▢ Your entire problem is that 12% of outputs are invalid JSON. Cheapest fix?

<details markdown="1"><summary>Check</summary>

Constrained decoding. Grammar-constrained generation cannot produce invalid JSON — it is a serving-side change with no training at all.

Fine-tuning might reach 99% validity. Constrained decoding reaches 100% by construction. Fine-tune only if the *values* are also wrong, which is a different problem.

</details>

4. ▢ Which situation most favours fine-tuning?

   - a) The model lacks knowledge of your internal documentation
   - b) High request volume with a very long system prompt
   - c) The model occasionally makes arithmetic errors in output
   - d) The model needs information about events from this week

<details markdown="1"><summary>Check</summary>

**b)** High request volume with a very long system prompt.

Moving prompt content into the weights removes prefill cost on every request, and the saving scales with volume. (a) and (d) are retrieval. (c) is tool use — give it a calculator.

</details>

5. ▢ Is LoRA a compromise relative to full fine-tuning?

<details markdown="1"><summary>Check</summary>

Largely not, in the regime most people work in. With adequate rank across all linear layers and a tuned learning rate, LoRA matches full fine-tuning on typical supervised fine-tuning workloads.

Full fine-tuning remains appropriate for very large behavioural shifts, continued pretraining at scale, or research needing the full parameter space. For an ordinary task adaptation, adapters are the right method and not a concession.

</details>

6. ▢ You have retrieval working and the model still ignores retrieved context and invents answers. Now what?

<details markdown="1"><summary>Check</summary>

Now fine-tuning is well-motivated — and this is the combined architecture, not a choice between approaches.

The problem is behavioural: grounding in provided context, respecting it, citing it, and declining when it is insufficient. Retrieval supplies facts; training teaches what to do with them. Build the dataset from real retrieved contexts with correct grounded responses, including cases where the right answer is "the provided context does not cover this".

</details>

## Real-world reps

- [ ] Take a fine-tuning proposal — yours or someone else's — and work the three questions against it. Write a one-paragraph verdict.
- [ ] Measure a prompted baseline on your held-out set, properly. Record the number before training anything.
- [ ] Cost the full lifetime of one fine-tune: data, evaluation, serving, retraining, ownership. Compare against the saving.
- [ ] Tomorrow: find a case where you would decline to fine-tune, and write the argument for the alternative in a paragraph someone else could act on.

## Going further

- [Docs: "LoRA Without Regret", Hugging Face TRL](https://huggingface.co/docs/trl/main/en/lora_without_regret)
- [Paper: "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks", Lewis et al., arXiv:2005.11401](https://arxiv.org/abs/2005.11401)
- [r/LocalLLaMA](https://www.reddit.com/r/LocalLLaMA/): search it for the cases where practitioners decided against fine-tuning, and what they shipped instead
- [Failure modes](../reference/failure-modes.md), [LoRA hyperparameters](../reference/lora-hyperparameters.md), [Memory budget](../reference/memory-budget.md)

---

That is the arc. From here the work is reps on real tasks — and the mission's last line is the one to keep: being able to argue convincingly *against* fine-tuning is what makes the argument *for* it worth anything.

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
