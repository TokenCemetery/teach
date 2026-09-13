---
title: 3. Byte-Pair Encoding From Scratch
description: The algorithm that turns rare and unknown words into sequences of learned subword units, worked by hand
type: lesson
---

# Lesson 3. Byte-Pair Encoding From Scratch

**Mission link:** "Train a tokenizer and defend a vocabulary size against its effect on sequence length and embedding table size" is the second bullet under Success looks like. This lesson builds the algorithm most tokenizers still use; Lesson 4 covers the vocabulary-size tradeoff itself.
**Primary source:** [Paper: "Neural Machine Translation of Rare Words with Subword Units", Sennrich et al., 2015](https://arxiv.org/abs/1508.07909)
**Prerequisites:** [Lesson 2](0002-deduplication-and-quality-filtering.md)

## Warm-up

1. ▢ Name one thing deduplication removes from a corpus, and one thing quality filtering removes that deduplication would not catch.

<details markdown="1"><summary>Check</summary>

Deduplication removes repeated or near-repeated text that already exists elsewhere in the corpus. Quality filtering removes low-value text that is not a copy of anything, such as boilerplate or machine-generated text, which deduplication has no way to detect.

</details>

## Know this

### Why a fixed word vocabulary breaks

A model that predicts one of a fixed list of whole words has no way to handle a word that was not on that list: a rare name, a novel compound, a typo, a word in a script the list did not anticipate. Sennrich et al. named this directly for translation, where it is unavoidable, since translation is fundamentally an open-vocabulary problem: no fixed list of words, however large, covers every name, number, and coinage a real text will contain. Their fix was to stop tokenizing into whole words at all, and tokenize into **subword units** instead: pieces smaller than a word, built so that a rare or unseen word can still be spelled out of pieces the model has seen before.

### The algorithm: merge the most frequent pair, repeat

Byte-pair encoding was originally a data-compression algorithm, repurposed here for a different job. It starts from the smallest possible vocabulary, individual characters, and builds upward:

1. Start with every word in the training text split into its individual characters, plus a marker for the end of the word.
2. Count how often each adjacent pair of symbols occurs next to each other, across the whole (frequency-weighted) text.
3. Merge the single most frequent pair into one new symbol, everywhere it occurs.
4. Repeat steps 2 and 3 for a fixed number of merges.

The number of merges is the only hyperparameter, and it sets the vocabulary size directly: the final vocabulary is the starting character set plus one new symbol per merge performed. A word that never gets fully merged into one symbol is represented as a short sequence of the pieces it did get merged into, which is exactly what lets an unseen word still be encoded: it falls back to smaller, already-known pieces rather than to a single unknown-word symbol.

### A worked example

Sennrich et al.'s paper gives this toy corpus directly: four words, already split into characters with `</w>` marking the end of each word, each carrying a frequency:

```text
{'l o w </w>': 5, 'l o w e r </w>': 2, 'n e w e s t </w>': 6, 'w i d e s t </w>': 3}
```

Counting every adjacent pair, weighted by each word's frequency, three pairs come out tied for the most frequent, at a weighted count of 9 each: `(e, s)`, `(s, t)`, and `(t, </w>)`. Each of the two words containing "est" (`newest`, frequency 6, and `widest`, frequency 3) contributes one occurrence of every pair inside that shared substring, so `6 + 3 = 9` for all three. The algorithm's rule, "merge the single most frequent pair," does not by itself say which of three exactly-tied pairs to merge first: that detail is left to whatever the implementation does when it has to break a tie, not to the algorithm's own definition. Merging any one of the three does not remove the tie, either: since all three pairs come from the same repeated substring "est", merging one of them (say `e`+`s` into `es`) just relabels the others as new adjacent pairs at the same count (`es`+`t` and `t`+`</w>` are still tied at 9), so all three get folded together within the next couple of merges regardless of which is chosen first, and `newest` and `widest` both end up sharing a single `est` piece.

## Practice

1. ▢ Using the worked example's corpus, `{'l o w </w>': 5, 'l o w e r </w>': 2, 'n e w e s t </w>': 6, 'w i d e s t </w>': 3}`, compute the weighted count of the adjacent pair `(l, o)`.

<details markdown="1"><summary>Hint</summary>

`(l, o)` appears once per occurrence of a word starting "lo...". Which words is that, and at what frequencies?

</details>

<details markdown="1"><summary>Check</summary>

`(l, o)` appears in `low` (frequency 5) and in `lower` (frequency 2), giving `5 + 2 = 7`.

</details>

2. ▢ Why does the algorithm's own definition, "merge the single most frequent pair," not fully determine which pair gets merged first in this corpus?

<details markdown="1"><summary>Check</summary>

Because three pairs, `(e, s)`, `(s, t)`, and `(t, </w>)`, are exactly tied at the highest weighted count, 9. The rule names what to do when there is a unique most-frequent pair; it says nothing about which of several tied pairs to pick, so that choice comes from whatever the implementation does on a tie, not from the algorithm as stated.

</details>

3. ▢ A tokenizer trained with 500 merges is given a word it never saw during training. What happens, and why does this differ from what a fixed whole-word vocabulary would do?

    - a) It is replaced with a single generic "unknown word" symbol, the same outcome a whole-word vocabulary would produce
    - b) Training fails, since the tokenizer has no rule for unseen input
    - c) It gets spelled out as a short sequence of smaller pieces the tokenizer already learned, rather than collapsing to one unknown-word symbol
    - d) The tokenizer automatically adds a new merge rule for it on the spot

<details markdown="1"><summary>Check</summary>

**c)** The unseen word falls back to whatever smaller pieces, down to individual characters if necessary, the training merges already produced. (a) describes exactly the failure mode subword tokenization was built to avoid. (b) and (d) do not describe how a trained, fixed set of merge rules behaves at test time.

</details>

4. ▢ What was the field-specific reason Sennrich et al. gave for needing an open-vocabulary approach at all?

<details markdown="1"><summary>Check</summary>

Translation is fundamentally an open-vocabulary problem: names, compounds, and loanwords mean no fixed word list, however large, can cover every word a real input text will contain.

</details>

## Real-world reps

- [ ] By hand or in a spreadsheet, take the worked example's corpus and compute the weighted count of every adjacent pair after `(e, s)` has been merged into `es` (so `newest` becomes `n e w es t </w>` and `widest` becomes `w i d es t </w>`). Confirm which pair(s) are now tied for the most frequent.
- [ ] Find a tokenizer's vocabulary file for any open model you have access to (many are published alongside the model). Search it for a common word in your own name or a name you know, and see whether it exists as one token or gets split into pieces.
- [ ] Tomorrow: pick five words in your own language that you think would be poorly served by a small subword vocabulary (rare technical terms, names, compounds), and predict, in one sentence per word, how a BPE tokenizer would likely split each one.

## Going further

- [Paper: "Neural Machine Translation of Rare Words with Subword Units", Sennrich et al., 2015](https://arxiv.org/abs/1508.07909)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
