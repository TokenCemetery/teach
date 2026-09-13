---
title: 4. SentencePiece and the Vocabulary Size Tradeoff
description: Tokenizing raw text without a pre-tokenizer, and what a larger or smaller vocabulary actually costs
type: lesson
---

# Lesson 4. SentencePiece and the Vocabulary Size Tradeoff

**Mission link:** "Train a tokenizer and defend a vocabulary size against its effect on sequence length and embedding table size" is the second bullet under Success looks like. Lesson 3 built the merge algorithm; this lesson covers training it without assuming word boundaries, and the size decision itself.
**Primary source:** [Paper: "SentencePiece: A simple and language independent subword tokenizer and detokenizer for Neural Text Processing", Kudo and Richardson, 2018](https://arxiv.org/abs/1808.06226)
**Prerequisites:** [Lesson 3](0003-byte-pair-encoding-from-scratch.md)

## Warm-up

1. ▢ In the byte-pair encoding algorithm, what does the number of merge operations performed determine?

<details markdown="1"><summary>Check</summary>

The final vocabulary size: it equals the starting character set plus one new symbol per merge performed.

</details>

2. ▢ Why did three pairs in Lesson 3's worked example (`(e, s)`, `(s, t)`, `(t, </w>)`) all end up merged within a few steps of each other, regardless of which one was merged first?

<details markdown="1"><summary>Check</summary>

They were all tied at the same frequency because they all came from the same repeated substring, "est". Merging any one of them relabeled the others as new pairs at the same count rather than removing the tie, so all three folded together in short order no matter which was merged first.

</details>

## Know this

### Why assuming word boundaries breaks down

Byte-pair encoding, as Lesson 3 described it, is usually run on top of a **pre-tokenizer**: something that first splits raw text into words, so BPE only ever has to learn merges within a word. For English, splitting on whitespace is an easy, mostly reliable pre-tokenizer. It is not language-independent: plenty of widely used written languages, including Japanese and Chinese, do not delimit words with spaces at all, so a whitespace pre-tokenizer has nothing sensible to split on before BPE even starts. Building a different pre-tokenizer per language, or per script, undermines the idea of one tokenizer-training procedure that works anywhere.

### Training directly on raw sentences

Kudo and Richardson's SentencePiece removes the pre-tokenization step rather than trying to fix it per language: it trains its subword model directly on raw sentence text, with no assumption of pre-existing word boundaries built in. Whitespace itself is treated as an ordinary symbol in the input, typically represented with a dedicated marker so the original spacing can be reproduced exactly on detokenization, rather than as something to split on before training starts. This makes the same training procedure language-independent, which the paper backs with an English-Japanese machine translation experiment: training end-to-end on raw sentences reached accuracy comparable to training on text that had already been word-segmented by a separate tool.

### One toolkit, two training algorithms

SentencePiece is not a second competing algorithm to BPE; it is a toolkit that implements BPE (Lesson 3's merge procedure) alongside a second training algorithm, a **unigram language model** trainer, which works in the opposite direction. Instead of starting from individual characters and growing merges upward, it starts from a large set of candidate subwords and repeatedly prunes down to the target vocabulary size, at each step removing whichever pieces the model's likelihood would miss least. Either training algorithm produces the same shape of result: a fixed vocabulary of subword pieces and a deterministic way to split new raw text into them.

### The vocabulary-size tradeoff

The target vocabulary size, however it was trained, is a single number that pulls in more than one direction at once:

- A **larger** vocabulary encodes the same text in fewer tokens on average, since more common substrings earn their own single symbol. Shorter token sequences mean less compute spent attending over and generating the same input.
- A **larger** vocabulary also means a larger embedding table and a larger output projection (usually the same matrix, tied together), which is parameter count that scales with vocabulary size directly, independent of how deep or wide the rest of the model is.
- A **larger** vocabulary spreads training signal more thinly: with the same corpus sliced into more distinct pieces to choose among, any one specific token, especially a rarer one, is seen fewer times per pass over the data.
- A **smaller** vocabulary reverses all three: longer token sequences per input, a smaller embedding and output table, and denser per-token training signal, at the cost of splitting ordinary words into more pieces each.

No single vocabulary size wins on every axis at once, so it is chosen against a specific model's shape and budget rather than read off a formula. A real, checkable example: the LLaMA paper reports tokenizing its training data with byte-pair encoding through the SentencePiece implementation, splitting all numbers into individual digits and falling back to raw bytes to represent any UTF-8 character the trained vocabulary does not otherwise cover, so that no input character is ever truly unrepresentable, whatever the chosen vocabulary size.

## Practice

1. ▢ A tokenizer built on a whitespace pre-tokenizer, trained only on English, is applied unmodified to Japanese text, which has no spaces between words. What goes wrong, and what does SentencePiece do differently that avoids it?

<details markdown="1"><summary>Check</summary>

The whitespace pre-tokenizer has nothing sensible to split on, since Japanese does not delimit words with spaces, so it cannot hand BPE reasonable word-sized chunks to merge within. SentencePiece avoids this by training directly on raw sentence text with no assumption of pre-existing word boundaries, treating whitespace as an ordinary symbol rather than a required pre-split.

</details>

2. ▢ A team doubles their tokenizer's vocabulary size while keeping the model's hidden dimension and depth exactly the same. Which of these best describes the result?

    - a) Sequences get shorter on average, and the embedding and output tables shrink
    - b) Sequences get shorter on average, but the embedding and output tables grow
    - c) Sequences get longer on average, but the embedding and output tables shrink
    - d) Neither sequence length nor parameter count is affected by vocabulary size

<details markdown="1"><summary>Hint</summary>

Vocabulary size affects two different things: how many tokens a piece of text turns into, and how big the table mapping each token to a vector is. Consider each separately.

</details>

<details markdown="1"><summary>Check</summary>

**b)** A larger vocabulary means more common substrings get their own token, which shortens sequences, while the embedding and (usually tied) output projection tables both scale directly with vocabulary size, so they grow. (a) and (c) each get one of the two effects backwards, and (d) ignores both.

</details>

3. ▢ Name one axis on which a smaller vocabulary is better than a larger one, and one axis on which it is worse.

<details markdown="1"><summary>Check</summary>

Better: denser per-token training signal (each token is seen more often per pass over the same corpus), or a smaller embedding and output table. Worse: longer token sequences per input, since ordinary words get split into more pieces, which costs more compute to attend over and generate.

</details>

4. ▢ Which of these best describes what SentencePiece is, as a piece of software?

    - a) A single new tokenization algorithm that replaces byte-pair encoding
    - b) A toolkit that implements both byte-pair encoding and a unigram-language-model trainer, directly on raw text with no pre-tokenization step required
    - c) A pre-tokenizer only, meant to be run before a separate BPE implementation
    - d) A way to train a model without any fixed vocabulary at all

<details markdown="1"><summary>Check</summary>

**b)** SentencePiece packages two training algorithms, byte-pair encoding and a unigram language model, and its distinguishing feature is training directly from raw sentences. (a) is wrong because it still implements BPE rather than replacing it. (c) inverts SentencePiece's actual contribution, which is removing the pre-tokenization step. (d) describes no real tokenizer discussed in this track; both algorithms still produce a fixed vocabulary.

</details>

## Real-world reps

- [ ] Find the reported vocabulary size of a tokenizer you have access to, whether through a library or a hosted model's published tokenizer files.
- [ ] If you can access two tokenizers with noticeably different vocabulary sizes, encode the same sentence with both and compare the resulting token counts directly.
- [ ] Tomorrow: for a specific project or use case you know the scale of (a chat assistant, a code-focused model, a tool for a low-resource language), decide qualitatively whether you would lean toward a larger or smaller vocabulary than a mainstream model, and write down which single axis of the tradeoff drove your answer.

## Going further

- [Paper: "SentencePiece: A simple and language independent subword tokenizer and detokenizer for Neural Text Processing", Kudo and Richardson, 2018](https://arxiv.org/abs/1808.06226)
- [Resources](../RESOURCES.md)

---

Stage 1 covered what goes into a corpus and what gets removed from it; stage 2 covered how that corpus gets turned into tokens at all. Stage 3 turns to the question that sits above both: given a parameter count, how many of those tokens are worth training on.

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
