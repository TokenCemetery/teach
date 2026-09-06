---
title: 11. PagedAttention
description: The block table mechanism behind vLLM, its block-size trade-off, and how it lets sequences share a common prefix's cache
type: lesson
---

# Lesson 11. PagedAttention

**Mission link:** vLLM's memory manager is the mechanism that makes lesson 2's capacity ceiling a moving, shareable target rather than a fixed per-sequence cost, and this lesson is where that mechanism gets named in full.
**Primary source:** [Paper: "Efficient Memory Management for Large Language Model Serving with PagedAttention", Kwon et al., SOSP 2023](https://arxiv.org/abs/2309.06180)
**Prerequisites:** [Lesson 10](0010-standing-up-vllm.md), [KV cache](../GLOSSARY.md)

## Warm-up

1. ▢ What two kinds of fragmentation did a naive, contiguous, max-length-sized KV cache allocation suffer from (lesson 1)?

<details markdown="1"><summary>Check</summary>

Internal fragmentation: a sequence that finishes short still holds memory reserved for the maximum length it never used. External fragmentation: gaps between differently-sized reserved blocks that no other sequence's cache can fit into.

</details>

2. ▢ In one sentence, what did lesson 1 say PagedAttention borrows from operating-system virtual memory?

<details markdown="1"><summary>Check</summary>

Splitting the cache into fixed-size blocks, stored non-contiguously, addressed through a per-sequence table that maps logical positions to physical blocks, the same idea as OS page tables.

</details>

## Know this

### The block table, one level of detail deeper

Each sequence's KV cache is divided into fixed-size **blocks**, each holding a set number of tokens' worth of keys and values. A sequence's **block table** maps its logical token positions to physical block locations in memory, wherever they happen to sit. Attention for a given sequence looks up its blocks through this table rather than assuming they're contiguous, which is what lets the underlying memory manager place blocks anywhere it has room, exactly like an OS page table lets a process's memory pages sit anywhere in physical RAM.

### Block size is a trade-off, not a free parameter

A larger block size means fewer blocks per sequence and less block-table bookkeeping, but more wasted space in the last, partially-filled block of a sequence whose length doesn't divide evenly (internal fragmentation, just at a much smaller scale than lesson 1's naive, whole-sequence version). A smaller block size wastes less space per sequence but means more blocks, and more block-table entries, to track. vLLM's default block size (16 tokens) is a chosen middle ground between these two costs, not an arbitrary number.

### Sharing blocks across sequences

Because a sequence's blocks are reached indirectly, through its block table, rather than by assuming a fixed physical layout, two different sequences' block tables can point at the *same* physical block when its content is identical, most commonly a shared prompt prefix. Parallel sampling (asking for several completions of the same prompt) or beam search are the clearest cases: every sample shares the identical prompt tokens' cache, so the prompt's blocks need to exist physically only once, with every sample's block table pointing at them. When a sample's generation diverges from the others (any new, sample-specific token), a **copy-on-write** creates that sample's own private copy of the block being modified, exactly the mechanism an operating system uses when two processes share memory pages until one of them writes.

## Practice

1. ▢ With a block size of 16 tokens, a sequence generates 40 tokens of output. How many blocks does it use, and how much space is wasted in the last one?

<details markdown="1"><summary>Hint</summary>

Divide 40 by 16 and round up to a whole number of blocks; the waste is what's left unused in the final, partially-filled block.

</details>

<details markdown="1"><summary>Check</summary>

`40 / 16 = 2.5`, rounded up to 3 blocks. The first two hold 32 tokens; the third holds the remaining 8, wasting the other 8 slots in that block, internal fragmentation at the scale of one block instead of a whole sequence.

</details>

2. ▢ Why does a smaller block size reduce that wasted space, and what does it cost in exchange?

<details markdown="1"><summary>Check</summary>

A smaller block size means the last, partially-filled block has fewer unused slots to waste, since there are fewer positions in each block to begin with. The cost is more blocks per sequence overall, and so more block-table entries the memory manager has to track and look up.

</details>

3. ▢ Ten parallel samples are requested from the same 200-token prompt, with a block size of 16 tokens. How many physical blocks does the prompt's cache need, with block sharing, versus without it?

<details markdown="1"><summary>Hint</summary>

Work out how many blocks one copy of the 200-token prompt needs, then decide how many copies exist in each case.

</details>

<details markdown="1"><summary>Check</summary>

`200 / 16 = 12.5`, rounded up to 13 blocks for one copy of the prompt. Without sharing, all 10 samples each hold their own copy: `13 × 10 = 130` blocks. With sharing, every sample's block table points at the same 13 physical blocks for the shared prompt, so only 13 blocks are needed until any sample starts generating its own diverging tokens.

</details>

4. ▢ One of the ten samples in question 3 generates a token that differs from what any other sample generated at that position. What happens to that sample's cache at that point?

<details markdown="1"><summary>Check</summary>

A copy-on-write is triggered: that sample gets its own private copy of the block being written to, rather than modifying the shared block every other sample's table still points at. Only the diverging sample pays for a new block; the other nine keep sharing the original.

</details>

5. ▢ Which claim is true of vLLM's block size choice?

   - a) Larger blocks always waste more memory than smaller ones, with no offsetting benefit
   - b) Block size trades internal fragmentation against block-table bookkeeping overhead
   - c) Block size only affects parallel sampling workloads, not single-request serving
   - d) A smaller block size always increases total memory usage

<details markdown="1"><summary>Check</summary>

**b)** Smaller blocks waste less space in a partially-filled final block but require tracking more block-table entries; larger blocks are the reverse. (a) is false: larger blocks reduce bookkeeping overhead, which is a real benefit. (c) is false: every sequence, shared or not, is divided into blocks and pays the fragmentation/bookkeeping trade-off. (d) is false: smaller blocks reduce internal fragmentation, which can lower total memory usage, not always raise it.

</details>

## Real-world reps

- [ ] Find vLLM's block-size flag or config option in its docs and read what its default value is and what the docs say about changing it.
- [ ] If you can run a server, send several parallel sampling requests (`n` greater than 1) for the same prompt, and see whether the docs or logs report anything about prefix or block sharing.
- [ ] Tomorrow: read one paragraph on prefix caching (reusing a shared system prompt's blocks across otherwise unrelated requests) and note how it's the same block-sharing idea applied across requests instead of within one.

## Going further

- [Paper: "Efficient Memory Management for Large Language Model Serving with PagedAttention", Kwon et al., SOSP 2023](https://arxiv.org/abs/2309.06180)
- [Docs: vLLM Documentation, vLLM Project](https://docs.vllm.ai/en/latest/)
- [Resources](../RESOURCES.md)

---

Not landing? Reread the primary source at the top, since this lesson compresses it and compression is where understanding leaks. Check the [glossary](../GLOSSARY.md) for any term that felt slippery.

If the lesson itself is unclear rather than the material, that is a defect: [open an issue](https://github.com/TokenCemetery/teach/issues).
