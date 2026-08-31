---
title: 3. Tokenizers and Chat Templates
description: Train on the rendering you will serve
type: lesson
---

# Lesson 3. Tokenizers and Chat Templates

**Mission link:** The most common cause of a fine-tune that trains cleanly and behaves badly is a template mismatch, not a hyperparameter.
**Primary source:** [Docs: Chat Templates, Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/chat_templating)
**Prerequisites:** [Lesson 1](0001-what-a-base-model-is.md), [Lesson 2](0002-where-the-weights-live.md)

## Warm-up

1. ▢ Which holds more parameters in a modern block, attention or the MLP?

<details markdown="1"><summary>Check</summary>

The MLP, because its intermediate dimension is several times the hidden size, and grouped-query attention shrinks `k_proj` and `v_proj` further.

</details>

2. ▢ How do you find a model's real module names?

<details markdown="1"><summary>Check</summary>

Print them from the loaded model with `named_modules()`. Never recall them; they vary by architecture.

</details>

3. ▢ What does cross-entropy loss measure?

<details markdown="1"><summary>Check</summary>

How much probability the model assigned to the token that actually came next. Low loss means the true continuation was unsurprising to the model.

</details>

## Know this

The model does not see text. It sees integers. The tokenizer is the mapping between them, and it is part of the model: a checkpoint's tokenizer is not interchangeable with another's, even within the same family.

### What a tokenizer is

Modern models use subword tokenization, usually byte-pair encoding. Training the tokenizer means starting from bytes and repeatedly merging the most frequent adjacent pair, producing a vocabulary where common words are single tokens and rare words split into pieces.

Three properties bite in practice:

**Tokens are not words.** ` the` (with a leading space) and `the` are different tokens. Capitalisation changes tokenization. A number like `1234` may be one token or four, and this is why models are bad at arithmetic in ways that look arbitrary.

**Token count is not character count.** English averages roughly four characters per token; code, non-Latin scripts and unusual formatting are far less efficient. Your sequence-length budget in Lesson 7 is measured in tokens, so you must measure, not estimate.

**Special tokens carry structure.** Beginning-of-sequence, end-of-sequence, padding, and the role markers below are ordinary vocabulary entries that the model has learned to treat as structural. Emitting them by hand incorrectly is not a syntax error; it is a silent distribution shift.

### Chat templates

A chat model was trained on conversations rendered into one flat token sequence by a specific, exact string format. For example, a model might have been trained on something shaped like:

```text
<|im_start|>system
You are helpful.<|im_end|>
<|im_start|>user
Hello<|im_end|>
<|im_start|>assistant
Hi.<|im_end|>
```

Another family uses entirely different markers. The format is not a convention you can approximate: it is the distribution the weights were fit to. Get a marker wrong, add a stray newline, or omit the system block when the model expects one, and the model is now operating slightly off-distribution. It will still produce fluent text, which is exactly why this failure is hard to spot.

The template ships with the tokenizer, as a Jinja string. Use it rather than writing the format yourself:

```python
from transformers import AutoTokenizer

tok = AutoTokenizer.from_pretrained("<model>")
messages = [
    {"role": "system", "content": "You are helpful."},
    {"role": "user", "content": "Hello"},
]

# For inference: leaves the sequence ready for the model to continue.
prompt = tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

# For training: the assistant turn is already present, so no generation prompt.
full = tok.apply_chat_template(
    messages + [{"role": "assistant", "content": "Hi."}], tokenize=False
)
print(repr(prompt))
print(repr(full))
```

`repr` matters. The difference between a correct and a broken template is often one whitespace character, and `print` hides it.

### The one rule

**Train on the same rendering you will serve.** If you fine-tune on your own hand-rolled format and then serve through the model's official template, you have trained one distribution and deployed another. The loss curve will look fine. The model will be subtly worse, and you will spend a day blaming rank.

`add_generation_prompt` is where this most often goes wrong: it belongs in inference, where you want the model to continue as the assistant, and not in a training example, where the assistant text is part of the sequence being learned.

### Base models have no template

If a base model's tokenizer has no chat template, that is not a bug, because there is no conversation format to preserve. You are choosing the format, so choose one, write it down, and use it identically in training and serving.

## Practice

1. ▢ Why can't you swap a tokenizer between two checkpoints of the same model family?

<details markdown="1"><summary>Check</summary>

Token IDs index directly into the embedding matrix. A different vocabulary maps the same integer to a different row, so every input is silently mistranslated. Output is fluent nonsense, or a crash if the vocabulary sizes differ.

</details>

2. ▢ You are building a training example. Should `add_generation_prompt` be `True` or `False`, and why?

<details markdown="1"><summary>Check</summary>

`False`. The generation prompt is the opening marker that tells the model "the assistant speaks next", which is useful at inference, when the assistant turn does not exist yet. In training the assistant turn is present in the text, so adding the prompt duplicates the marker and shifts the sequence off the format the model knows.

</details>

3. ▢ Your fine-tune trains to a low loss but at serving time the model rambles past the end of its answer instead of stopping. Name the most likely cause.

<details markdown="1"><summary>Check</summary>

The end-of-turn token was missing from your training examples, so the model never learned that answers terminate.

Loss cannot catch this: predicting fluent continuation is exactly what the model was rewarded for on your data. It is a data-construction bug that only an actual generation reveals, which is one reason Lesson 24 insists on generating rather than just scoring.

</details>

4. ▢ A prompt is 700 English words. Roughly how many tokens, and would you trust that estimate for a training budget?

<details markdown="1"><summary>Check</summary>

Roughly 900–1000 tokens, taking about 1.3 tokens per English word. No, you would not trust it: the ratio moves substantially with code, JSON, non-Latin scripts and unusual formatting, all of which are common in fine-tuning data.

Measure the real distribution with the actual tokenizer. Lesson 7 turns that distribution into a memory number.

</details>

5. ▢ Which of these is safe to change between training and serving?

   - a) The exact chat template string used
   - b) The tokenizer shipped with the model
   - c) The sampling temperature used at generation
   - d) The special token marking a turn end

<details markdown="1"><summary>Check</summary>

**c)** The sampling temperature used at generation.

Temperature is applied after the model produces its distribution, so it is a serving choice. The other three define the distribution the weights were fit to; changing any of them means serving a different problem than you trained.

</details>

## Real-world reps

- [ ] Take one model and print `apply_chat_template(..., tokenize=False)` with `repr`. Copy the exact string into your notes, whitespace included.
- [ ] Tokenize the same paragraph in two different model families and compare token counts. Then tokenize a block of JSON and compare again.
- [ ] Tomorrow: deliberately break a template by dropping the end-of-turn marker, then prompt the model. Watch what it does. That is the failure you are learning to recognise.

## Going further

- [Docs: Chat Templates, Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/chat_templating)
- [Code: minbpe, Andrej Karpathy](https://github.com/karpathy/minbpe): byte-pair encoding in readable form
- [Failure modes](../reference/failure-modes.md): template mismatch appears there
- [Lesson 21. Building the Dataset](0021-building-the-dataset.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
