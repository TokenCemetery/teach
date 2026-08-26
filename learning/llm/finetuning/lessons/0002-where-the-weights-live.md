# Lesson 2 — Where the Weights Live

**Mission link:** An adapter attaches to specific weight matrices. You cannot choose which ones until you can name them and say what each one does.
**Primary source:** [The Illustrated Transformer — Jay Alammar](https://jalammar.github.io/illustrated-transformer/)
**Prerequisites:** [Lesson 1](0001-what-a-base-model-is.md)

## Warm-up

1. ▢ What does a language model compute, stated as a function?

<details markdown="1"><summary>Check</summary>

Token sequence in, a score for every vocabulary token out. Generation is a loop around that function, not part of it.

</details>

2. ▢ Why does a base model fail to follow an instruction?

<details markdown="1"><summary>Check</summary>

Instruction following is trained behaviour added on top of next-token prediction. A base model has only the next-token objective, so it continues text rather than complying.

</details>

## Know this

Almost every parameter in a modern decoder-only model lives in one of three places: the embedding table, a stack of identical transformer blocks, and the output projection. The blocks hold the overwhelming majority, and they are where adapters attach.

### Inside one block

Each block has two sublayers, each preceded by a normalisation and wrapped in a residual connection.

**Attention.** Four linear projections, conventionally named after what they produce:

| Name | Role |
|---|---|
| `q_proj` | Queries — what this position is looking for |
| `k_proj` | Keys — what each position offers as a match |
| `v_proj` | Values — the content actually retrieved |
| `o_proj` | Mixes the attention result back into the residual stream |

**MLP** (also called the feed-forward network). In current models this is usually three projections rather than two, because of gated activations:

| Name | Role |
|---|---|
| `gate_proj` | Produces the gate, passed through an activation |
| `up_proj` | Projects up to the wider intermediate dimension |
| `down_proj` | Projects back down to the hidden dimension |

The MLP is wider than the hidden dimension — commonly around 2.5× to 4× — so despite having fewer matrices than you might expect, **the MLP holds more parameters than attention does.** That fact drives target-module choice in Lesson 10.

### Counting

A linear layer with input dimension `d_in` and output dimension `d_out` holds `d_in × d_out` weights. For a model with hidden size 2048, 24 layers and intermediate size 5632:

- Attention per layer, ignoring grouped-query attention: 4 × 2048 × 2048 ≈ 16.8M
- MLP per layer: 3 × 2048 × 5632 ≈ 34.6M
- Per layer total ≈ 51.4M, times 24 layers ≈ 1.23B
- Embeddings, with a 32k vocabulary: 32000 × 2048 ≈ 65.5M, doubled if the output projection is untied

That accounts for essentially the whole model. There is no hidden reservoir of parameters somewhere else.

### One trap worth knowing now

Most current models use **grouped-query attention**, where several query heads share one set of keys and values. That makes `k_proj` and `v_proj` *narrower* than `q_proj` and `o_proj` — often by a factor of four or eight. Any calculation that assumes all four attention projections are square will overcount, and any assumption that they are the same size will produce a wrong adapter parameter count in Lesson 8.

### Finding the real names

Never trust a remembered list of module names. They are set by the model implementation and they differ between architectures. Print them:

```python
from transformers import AutoModelForCausalLM

model = AutoModelForCausalLM.from_pretrained("<some-small-model>")
for name, module in model.named_modules():
    if isinstance(module, torch.nn.Linear):
        print(name, tuple(module.weight.shape))
```

This is the single most useful diagnostic in the whole workspace. A fine-tune that silently trains nothing usually means a target-module name that matched nothing.

## Practice

1. ▢ Name the seven linear projections in a typical modern transformer block.

<details markdown="1"><summary>Check</summary>

`q_proj`, `k_proj`, `v_proj`, `o_proj` in attention; `gate_proj`, `up_proj`, `down_proj` in the MLP.

Older or non-gated architectures have only two MLP projections. That is why you print the names rather than reciting them.

</details>

2. ▢ For a model with hidden size 4096 and intermediate size 11008, which holds more parameters per layer — attention or the MLP? Roughly by what factor?

<details markdown="1"><summary>Check</summary>

The MLP, by roughly two to one. Attention (square projections) is 4 × 4096² ≈ 67M. The MLP is 3 × 4096 × 11008 ≈ 135M.

With grouped-query attention the gap widens further, because `k_proj` and `v_proj` shrink while the MLP does not.

</details>

3. ▢ You set your adapter to target `["query", "value"]` on a model whose modules are named `q_proj` and `v_proj`. What happens?

<details markdown="1"><summary>Check</summary>

Nothing matches, so either the library raises an error or — worse, depending on version — you get a model with no trainable adapter weights at all. Training then runs, loss barely moves, and the run looks merely disappointing rather than broken.

Check the trainable-parameter count immediately after building the adapter. Lesson 11 makes this a habit.

</details>

4. ▢ Why does knowing the residual stream structure matter for adapters at all?

<details markdown="1"><summary>Check</summary>

Because an adapter modifies one projection's output, and the residual connection means that change is added to a running stream rather than replacing it. A small adapter contribution can steer the stream without destroying what the frozen layers already wrote into it — which is why starting an adapter at exactly zero (Lesson 9) is safe.

</details>

5. ▢ Grouped-query attention: your notes assume all four attention projections are 2048 × 2048, but the model has 32 query heads and 4 key-value heads with head dimension 64. What are the true shapes?

<details markdown="1"><summary>Check</summary>

`q_proj` and `o_proj` stay 2048 × 2048 (32 × 64 = 2048). `k_proj` and `v_proj` are 2048 × 256 (4 × 64 = 256).

So attention holds about 2 × 2048² + 2 × 2048 × 256 ≈ 9.4M per layer, not 16.8M. Nearly half your estimate.

</details>

## Real-world reps

- [ ] Run the `named_modules` loop above on the smallest model you can download. Write the seven names and their shapes into your own notes by hand.
- [ ] From the shapes alone, compute the model's total parameter count. Compare it against the number on its model card and account for any gap.
- [ ] Tomorrow: repeat for a model from a different family. Note every module name that differs.

## Going further

- [The Illustrated Transformer — Jay Alammar](https://jalammar.github.io/illustrated-transformer/)
- [LLM Visualization — Brendan Bycroft](https://bbycroft.net/llm) — the parameter counts are shown per matrix
- [Paper: "Attention Is All You Need" — Vaswani et al., arXiv:1706.03762](https://arxiv.org/abs/1706.03762)
- [Lesson 10 — Choosing Target Modules](0010-choosing-target-modules.md) is where this pays off

---

Stuck on any of this, or unsure whether an answer counts? Bring it back to the session — that's what your teacher is for.
