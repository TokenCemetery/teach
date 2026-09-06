---
title: 10. Recall@k and MRR
description: The two standard retrieval metrics, what each one tells you that the other doesn't, and how to pick k for the workload
type: lesson
---

# Lesson 10. Recall@k and MRR

**Mission link:** Stage 6 opens the "measure, don't assume" half of this workspace's mission: every earlier stage's decisions (chunking, embeddings, indexing, hybrid weights, reranking) were framed as things to measure, and this lesson gives the two standard numbers to measure them with.
**Primary source:** [Article: "Evaluation Measures for Search and Recommender Systems", Pinecone](https://www.pinecone.io/learn/offline-evaluation/)
**Prerequisites:** [Lesson 9](0009-when-reranking-earns-its-cost.md), [Chunk](../GLOSSARY.md)

## Warm-up

1. ▢ How should a team decide whether reranking earns its cost for their specific workload?

<details markdown="1"><summary>Check</summary>

Measure retrieval quality both without and with reranking on the same query set, separately measure the added latency at the candidate-set size in use, and compare both against the workload's actual latency budget and quality bar, rather than assuming reranking always or never helps.

</details>

2. ▢ In reciprocal rank fusion, what does the constant `k` do to the fused ranking?

<details markdown="1"><summary>Check</summary>

It dampens the influence of the very top ranks: a smaller `k` makes the score more sensitive to small differences in rank near the top, while a larger `k` (commonly 60) makes those differences matter less.

</details>

## Know this

### Recall@k: did the right document make the cut

**Recall@k** asks, across a set of test queries with known relevant documents, what fraction of them had a relevant document appear somewhere within the top *k* retrieved results. It's a budget question: if the downstream system only ever looks at the top *k* results, recall@k tells you how often the system even gave it a chance to find the right answer. Recall@k grows as *k* grows (a relevant document at rank 50 counts toward recall@100 but not recall@10), and it treats every position within the top *k* identically: a relevant document at rank 1 and one at rank *k* both count as a hit, with no credit for landing higher.

### MRR: how quickly the right document showed up

**Mean reciprocal rank (MRR)** fixes exactly what recall@k can't see. For each query, take the reciprocal of the rank position of the first relevant result (`1/rank`), then average that reciprocal across all queries. A relevant result at rank 1 contributes a full 1.0 to the average; the same relevant result at rank 10 contributes only 0.1. MRR rewards ranking the right answer as high as possible, not merely getting it inside some cutoff, which is exactly the information recall@k throws away by treating every position inside the top *k* the same.

### A worked example

Four test queries, each with one known relevant document, and its rank in each system's results: 1, 3, 1, 8.

```text
recall@1: ranks ≤ 1 are queries 1 and 3 → 2/4 = 0.50
recall@5: ranks ≤ 5 are queries 1, 2, and 3 (ranks 1, 3, 1); query 4 (rank 8) misses → 3/4 = 0.75
MRR: (1/1 + 1/3 + 1/1 + 1/8) / 4 = (1.000 + 0.333 + 1.000 + 0.125) / 4 ≈ 0.615
```

recall@5 says three out of four queries would find their answer if the system only looked at its top 5 results. MRR's 0.615 reflects that most of those hits landed at rank 1, with one weaker hit at rank 3 and one miss dragging the average down.

### Choosing k, and choosing between the metrics

The right *k* for recall@k isn't a default; it's whatever the downstream system actually uses. If only the top 5 chunks get passed to generation, recall@100 measures something the pipeline never actually exploits; recall@5 is the number that reflects reality. MRR is most informative when only the very top result matters a great deal (a single best answer surfaced to a user), since it specifically rewards rank 1 far more than rank 10. Recall@k is more informative when several results within a budget are all genuinely usable (generation can draw on several of the top-k chunks, not only the very first). Reporting both, at the *k* the pipeline actually uses, gives a fuller picture than either alone.

## Practice

1. ▢ Using the four-query example from this lesson (ranks 1, 3, 1, 8), compute recall@3.

<details markdown="1"><summary>Hint</summary>

Count how many of the four ranks are 3 or less.

</details>

<details markdown="1"><summary>Check</summary>

Ranks 1, 3, and 1 are all ≤ 3; rank 8 is not. `recall@3 = 3/4 = 0.75`, the same as recall@5 in this example, since no query's relevant document landed at rank 4 or 5.

</details>

2. ▢ Why doesn't recall@k alone distinguish a system that always ranks the relevant document 1st from one that always ranks it exactly at position `k`?

<details markdown="1"><summary>Check</summary>

Recall@k only checks whether a relevant document appears anywhere within the top k positions; it doesn't record which position within that range it landed at. A hit at rank 1 and a hit at rank k both count identically toward recall@k, so the metric can't tell the two systems apart even though one is clearly ranking better.

</details>

3. ▢ Why does MRR distinguish those two systems, where recall@k couldn't?

<details markdown="1"><summary>Check</summary>

MRR uses the reciprocal of the exact rank position, not just whether it falls under a cutoff. A system that always ranks the relevant document 1st gets a reciprocal rank of 1.0 every time, giving it an MRR of 1.0; a system that always ranks it at position k gets a reciprocal rank of `1/k` every time, giving it a much lower MRR whenever k is greater than 1. The exact position matters to MRR in a way it never mattered to recall@k.

</details>

4. ▢ A team's generation step only ever uses the top 5 retrieved chunks. Should they report recall@100 as their headline retrieval metric? Why or why not?

<details markdown="1"><summary>Check</summary>

No. Recall@100 measures whether the relevant document appears anywhere in the top 100 results, but the pipeline never looks past the top 5, so a hit at rank 40 is invisible to the actual system and shouldn't count as a success. Recall@5 is the number that reflects what the pipeline actually exploits; reporting recall@100 would overstate how often the system actually surfaces the right answer to generation.

</details>

5. ▢ Which claim is true of recall@k and MRR?

   - a) They measure exactly the same thing, so reporting both is redundant
   - b) Recall@k measures whether a relevant result falls within a budget of k; MRR measures how high-ranked the first relevant result is, rewarding rank 1 far more than a lower rank
   - c) MRR should always be preferred over recall@k, regardless of the workload
   - d) Recall@k is insensitive to the choice of k; any value gives the same result

<details markdown="1"><summary>Check</summary>

**b)** That's exactly the complementary information each metric captures. (a) is false: the worked example showed two systems that could tie on recall@k while differing sharply on MRR. (c) is false: which metric matters more depends on whether only the very top result counts or several results within a budget are usable. (d) is false: recall@k grows as k grows, by definition, so the choice of k changes the reported value.

</details>

## Real-world reps

- [ ] For a retrieval pipeline you run or plan to run, identify the actual k your downstream system uses (how many chunks reach generation), and compute recall at that k, not a default like 10 or 100.
- [ ] If you have a labeled or synthetic query set, compute MRR alongside recall@k and check whether the two numbers tell a consistent story or reveal something one metric alone would have hidden.
- [ ] Tomorrow: for a query where your system's relevant document ranks lower than you'd like, note its exact rank and how that affects both recall@k (at your chosen k) and MRR.

## Going further

- [Article: "Evaluation Measures for Search and Recommender Systems", Pinecone](https://www.pinecone.io/learn/offline-evaluation/)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
