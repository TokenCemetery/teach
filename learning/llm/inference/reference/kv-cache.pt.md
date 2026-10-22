---
title: "KV cache"
description: "Contabilidade de bytes do KV cache, custo por token, compartilhamento de heads, crescimento ao longo de uma requisição e planejamento de capacidade"
type: reference
---

# KV cache

Contabilidade de bytes do KV cache. Feito para consulta ao dimensionar um deployment.

## Custo por token

```text
bytes per token = 2 (K and V) × num_layers × num_kv_heads × head_dim × bytes_per_value
```

`head_dim = d_model / num_heads`. O cache guarda um par K/V por **KV head**, e não por query head. Na multi-head attention (MHA), `num_kv_heads = num_heads` e isso se reduz a `2 × num_layers × d_model × bytes_per_value`. Na grouped-query attention (GQA) ou na multi-query attention (MQA), `num_kv_heads` é menor e o cache encolhe nessa mesma proporção, de graça, sem mudança no comprimento de contexto nem no batch size.

| Esquema | `num_kv_heads` | Tamanho relativo do cache |
|---|---|---|
| MHA | igual a `num_heads` | 1x |
| GQA | uma fração de `num_heads` | essa mesma fração |
| MQA | 1 | `1 / num_heads` |

**Exemplo resolvido, Llama-2-70B** (80 camadas, 64 query heads, 8 KV heads, `head_dim` = 128, fp16):

```text
GQA: 2 × 80 × 8  × 128 × 2 bytes =   327,680 bytes ≈ 320 KB/token
MHA: 2 × 80 × 64 × 128 × 2 bytes = 2,621,440 bytes ≈ 2.5 MB/token   (8x GQA, the num_heads:num_kv_heads ratio)
```

## Crescendo até uma pegada total

```text
total cache bytes = bytes per token × context length × batch size
```

| Modelo | Por token | Contexto | Batch | Total |
|---|---|---|---|---|
| Llama-2-7B, MHA, fp16 | 512 KB | 4096 | 1 | ~2 GB |
| Llama-2-7B, MHA, fp16 | 512 KB | 4096 | 16 | ~32 GB |
| Llama-2-70B, GQA, fp16 | 320 KB | 4096 | 1 | ~1.25 GB |
| Llama-2-70B, GQA, fp16 | 320 KB | 4096 | 32 | ~40 GB |

<a id="capacity-budget"></a>

## Orçamento de capacidade

```text
max concurrent sequences = (total memory - weights - overhead) / (bytes per token × context length)
```

Llama-2-70B, com paralelismo de tensor em quatro GPUs de 80 GB (pool de 320 GB), pesos mais overhead do framework medidos em 160 GB, contexto de 4096 tokens:

```text
160 GB / 1.25 GB per sequence ≈ 128 concurrent sequences
```

Esse teto, e não o throughput bruto do modelo, é normalmente aquilo contra o qual um scheduler de batching negocia; veja [Batching](batching.md).

## O prefill reivindica a maior parte da pegada em um só passo

| Fase | O que faz | Crescimento do cache |
|---|---|---|
| Prefill | Processa o prompt inteiro em uma passada forward | Salta de imediato para `bytes per token × prompt length`; limitado por compute |
| Decode | Gera um token de saída por vez | Cresce `bytes per token` por passo; limitado pela largura de banda de memória |

**Exemplo resolvido**, um prompt de 2048 tokens seguido de 128 passos de decode, Llama-2-70B com 320 KB/token:

```text
prefill: 320 KB × 2048 ≈ 640 MB   (94% of the request's final cache)
decode:  320 KB × 128  ≈  40 MB   (6%, added gradually)
total:   680 MB
```

Um plano de capacidade construído apenas a partir do "comprimento de contexto final" esconde que a maior parte da pegada cai no prefill, em um único passo, e não espalhada ao longo da requisição.

<a id="cache-precision-is-a-lever-independent-of-the-models-own-weights"></a>

## A precisão do cache é uma alavanca independente dos pesos do próprio modelo

`bytes_per_value` acima não precisa coincidir com a precisão em que o modelo calcula. Uma stack de serving pode armazenar o próprio cache em uma precisão menor, geralmente fp8, enquanto o modelo calcula em bf16 ou fp16. Ela se soma de forma multiplicativa ao compartilhamento de heads, em vez de substituí-lo.

```text
Llama-2-70B, GQA, fp16: 320 KB/token
Llama-2-70B, GQA, fp8:  160 KB/token   (half, only bytes_per_value changed)
```

64 sequências com contexto de 4096 tokens: o fp16 custa ~80 GB, o fp8 custa ~40 GB, exatamente a metade, sobre o que a GQA já devolveu em relação à MHA completa.

## Relacionado

- [Lição 1](../lessons/0001-the-kv-cache.md), [Lição 2](../lessons/0002-capacity-and-batch-size.md), [Lição 3](../lessons/0003-growth-prefill-decode-precision.md)
- [Batching](batching.md): o que o teto de capacidade calculado nesta folha realmente restringe
