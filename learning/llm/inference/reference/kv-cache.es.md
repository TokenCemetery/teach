---
title: "KV cache"
description: "Contabilidad de bytes de la KV cache, costo por token, reparto de cabezas, crecimiento a lo largo de una solicitud y planificación de capacidad"
type: reference
---

# KV cache

Contabilidad de bytes de la KV cache. Pensado para consultar al dimensionar un despliegue.

## Costo por token

```text
bytes per token = 2 (K and V) × num_layers × num_kv_heads × head_dim × bytes_per_value
```

`head_dim = d_model / num_heads`. La caché guarda un par K/V por **cabeza KV**, no por cabeza de query. Con atención multi-cabeza (MHA), `num_kv_heads = num_heads` y esto se reduce a `2 × num_layers × d_model × bytes_per_value`. Con grouped-query attention (GQA) o multi-query attention (MQA), `num_kv_heads` es menor y la caché se reduce en esa misma proporción, gratis, sin cambiar la longitud de contexto ni el tamaño de lote.

| Esquema | `num_kv_heads` | Tamaño relativo de la caché |
|---|---|---|
| MHA | igual a `num_heads` | 1x |
| GQA | una fracción de `num_heads` | esa misma fracción |
| MQA | 1 | `1 / num_heads` |

**Ejemplo resuelto, Llama-2-70B** (80 capas, 64 cabezas de query, 8 cabezas KV, `head_dim` = 128, fp16):

```text
GQA: 2 × 80 × 8  × 128 × 2 bytes =   327,680 bytes ≈ 320 KB/token
MHA: 2 × 80 × 64 × 128 × 2 bytes = 2,621,440 bytes ≈ 2.5 MB/token   (8x GQA, the num_heads:num_kv_heads ratio)
```

## De ahí a una huella total

```text
total cache bytes = bytes per token × context length × batch size
```

| Modelo | Por token | Contexto | Lote | Total |
|---|---|---|---|---|
| Llama-2-7B, MHA, fp16 | 512 KB | 4096 | 1 | ~2 GB |
| Llama-2-7B, MHA, fp16 | 512 KB | 4096 | 16 | ~32 GB |
| Llama-2-70B, GQA, fp16 | 320 KB | 4096 | 1 | ~1.25 GB |
| Llama-2-70B, GQA, fp16 | 320 KB | 4096 | 32 | ~40 GB |

<a id="capacity-budget"></a>

## Presupuesto de capacidad

```text
max concurrent sequences = (total memory - weights - overhead) / (bytes per token × context length)
```

Llama-2-70B, con tensor parallelism en cuatro GPU de 80 GB (pool de 320 GB), pesos más sobrecarga del framework medidos en 160 GB, contexto de 4096 tokens:

```text
160 GB / 1.25 GB per sequence ≈ 128 concurrent sequences
```

Ese techo, y no el throughput bruto del modelo, es lo que suele negociar un scheduler de batching; consulta [Batching](batching.md).

## El prefill reclama la mayor parte de la huella en un solo paso

| Fase | Qué hace | Crecimiento de la caché |
|---|---|---|
| Prefill | Procesa todo el prompt en una pasada forward | Salta de inmediato a `bytes per token × prompt length`; limitado por cómputo |
| Decode | Genera un token de salida a la vez | Crece `bytes per token` por paso; limitado por el ancho de banda de memoria |

**Ejemplo resuelto**, un prompt de 2048 tokens seguido de 128 pasos de decode, Llama-2-70B a 320 KB/token:

```text
prefill: 320 KB × 2048 ≈ 640 MB   (94% of the request's final cache)
decode:  320 KB × 128  ≈  40 MB   (6%, added gradually)
total:   680 MB
```

Un plan de capacidad construido solo a partir de la "longitud final de contexto" oculta que la mayor parte de la huella cae en el prefill, en un solo paso, y no repartida a lo largo de la solicitud.

<a id="cache-precision-is-a-lever-independent-of-the-models-own-weights"></a>

## La precisión de la caché es una palanca independiente de los propios pesos del modelo

El `bytes_per_value` de arriba no tiene por qué coincidir con la precisión en que calcula el modelo. Un stack de serving puede guardar la propia caché con una precisión menor, habitualmente fp8, mientras el modelo calcula en bf16 o fp16. Se combina de forma multiplicativa con el reparto de cabezas en lugar de sustituirlo.

```text
Llama-2-70B, GQA, fp16: 320 KB/token
Llama-2-70B, GQA, fp8:  160 KB/token   (half, only bytes_per_value changed)
```

64 secuencias con un contexto de 4096 tokens: fp16 cuesta ~80 GB, fp8 cuesta ~40 GB, exactamente la mitad, además de lo que GQA ya recuperó respecto de la MHA completa.

## Relacionado

- [Lección 1](../lessons/0001-the-kv-cache.md), [Lección 2](../lessons/0002-capacity-and-batch-size.md), [Lección 3](../lessons/0003-growth-prefill-decode-precision.md)
- [Batching](batching.md): qué restringe realmente el techo de capacidad que calcula esta hoja
