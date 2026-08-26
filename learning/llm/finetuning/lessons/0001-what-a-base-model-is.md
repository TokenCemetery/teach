# Lesson 1 — What a Base Model Actually Is

**Mission link:** You cannot judge whether fine-tuning is the right answer until you know exactly what the model does when you leave it alone.
**Primary source:** [LLM Visualization — Brendan Bycroft](https://bbycroft.net/llm)
**Prerequisites:** none — this is the first lesson.

## Know this

A language model is one function. It takes a sequence of token IDs and returns a score for every token in its vocabulary, describing what could come next. That is the whole operation. Chat, tool calls, refusals, reasoning traces — all of it is built on top of that single next-token step.

Those raw scores are called **logits**. Softmax turns them into a probability distribution. A sampler picks one token from that distribution, the token is appended to the sequence, and the function runs again. Text appears one token at a time, and nothing else is happening.

Two consequences matter for everything later.

**The weights do not change at inference.** When a model appears to remember something from earlier in a conversation, the memory is the tokens sitting in its context window, not a change in the model. Fine-tuning is the only thing in this workspace that alters weights, and it happens offline, before serving.

**Sampling is not the model.** Temperature, top-p and top-k reshape the distribution after the model has produced it. If output quality changes when you change temperature, you learned something about your sampler, not about your weights. Hold sampling fixed before attributing anything to training.

### Base versus instruct

A **base** model has been trained on one objective only: predict the next token across a very large corpus. It does not answer questions. Given `What is the capital of France?` it may continue with three more exam questions, because that is what the surrounding text looked like in its training data.

An **instruct** or **chat** model is a base model that has been trained further on pairs of instructions and responses — supervised fine-tuning — and usually on human or model preference data after that. The instruction-following behaviour you take for granted is a trained layer, not a property of the architecture.

Which one you start from is a real decision:

| Starting point | You inherit | You must supply |
|---|---|---|
| Base | Nothing but raw language ability | Every formatting and behavioural convention |
| Instruct | Formatting, instruction following, refusal behaviour | Only your task — but you risk degrading what is already there |

Most adapter fine-tuning starts from an instruct model, because rebuilding instruction following from scratch on a small dataset is a losing trade. The cost is that your training data now competes with training the vendor already did, and that competition is where [catastrophic forgetting](../GLOSSARY.md) comes from later.

### The training signal

During training the model is shown a real sequence and scored on how much probability it assigned to the token that actually came next. That score is **cross-entropy loss**. Low loss means the model found the real continuation unsurprising.

Hold on to one caveat, because stage 6 is built on it: loss measures next-token surprise on text you already have. It does not measure whether the model is useful.

## Practice

1. ▢ Describe, in one sentence and without the word "understand", what a language model computes.

<details markdown="1"><summary>Check</summary>

Given a sequence of tokens, it produces a score for every token in the vocabulary describing what could come next.

The wrong instinct is to describe generation ("it writes text") rather than the function. Generation is a loop wrapped around the function, implemented outside the weights. Keeping the two separate is what lets you reason about where a problem lives.

</details>

2. ▢ You prompt a model twice with identical input and get two different answers. Name two places the difference could come from, and say which one involves the weights.

<details markdown="1"><summary>Check</summary>

The sampler (temperature above zero picks different tokens from the same distribution) and the context (a different system prompt, or conversation history you forgot was there). Neither involves the weights.

The weights are frozen at inference. If you have not changed them, they cannot be the explanation — and this is the first thing to rule out before you conclude a model is inconsistent.

</details>

3. ▢ You give a base model the prompt `Summarise this article:` followed by an article, and it produces another article instead of a summary. Is the model broken?

<details markdown="1"><summary>Check</summary>

No. It is doing exactly its job: continuing plausible text. In its training corpus, an article is far more often followed by more article than by a summary.

Instruction following is a trained behaviour. Expecting it from a base model is the single most common early mistake, and it usually gets misdiagnosed as a bad model or a bad prompt.

</details>

4. ▢ Which of these does fine-tuning change?

   - a) The sampling temperature used at serving time
   - b) The numeric values stored inside the model weights
   - c) The tokens present in the model context window
   - d) The vocabulary size the model was first built with

<details markdown="1"><summary>Check</summary>

**b)** The numeric values stored inside the model weights.

Temperature is a serving-time knob. Context is per-request input. Vocabulary size is fixed by the tokenizer and the embedding matrix, and changing it is a much more invasive operation than fine-tuning. Only the weight values are what training moves.

</details>

5. ▢ Give one reason to fine-tune an instruct model rather than a base model, and one reason to do the opposite.

<details markdown="1"><summary>Check</summary>

Start from instruct when you want to keep instruction following and general helpfulness that you cannot afford to rebuild from a small dataset — which is nearly always.

Start from base when your task's output format is so unlike ordinary chat that inherited chat behaviour actively interferes: rigid structured output, a single classification label, or a domain notation where conversational padding is pure noise.

</details>

## Real-world reps

- [ ] Run any model you can reach locally or through an API. Send one prompt at temperature 0 twice, then at temperature 1 twice. Write down which pair matched and why.
- [ ] Find a model on the Hugging Face Hub that has both a base and an instruct variant. Read both model cards and note what the instruct card claims was added.
- [ ] Tomorrow: give a base model a direct question and record what it does instead of answering. Keep the output — you will recognise this failure again in stage 6.

## Going further

- [LLM Visualization — Brendan Bycroft](https://bbycroft.net/llm) — click through a single token's path end to end
- [The Illustrated Transformer — Jay Alammar](https://jalammar.github.io/illustrated-transformer/)
- [Glossary](../GLOSSARY.md) — `fine-tuning` in this workspace always means the frozen-base kind
- [Resources](../RESOURCES.md)

---

Stuck on any of this, or unsure whether an answer counts? Bring it back to the session — that's what your teacher is for.
