---
title: "KV cache"
description: "Décompte en octets du KV cache, coût par token, partage de têtes, croissance au fil d'une requête et planification de capacité"
type: reference
---

# KV cache

Décompte en octets du KV cache. Conçu pour la consultation lors du dimensionnement d'un déploiement.

## Coût par token

```text
bytes per token = 2 (K and V) × num_layers × num_kv_heads × head_dim × bytes_per_value
```

`head_dim = d_model / num_heads`. Le cache contient une paire K/V par **tête KV**, et non par tête de requête. Avec l'attention multi-têtes (MHA), `num_kv_heads = num_heads` et cela se réduit à `2 × num_layers × d_model × bytes_per_value`. Avec la grouped-query attention (GQA) ou la multi-query attention (MQA), `num_kv_heads` est plus petit et le cache rétrécit de ce même rapport, gratuitement, sans rien changer à la longueur de contexte ni à la taille de batch.

| Schéma | `num_kv_heads` | Taille relative du cache |
|---|---|---|
| MHA | égal à `num_heads` | 1x |
| GQA | une fraction de `num_heads` | cette même fraction |
| MQA | 1 | `1 / num_heads` |

**Exemple détaillé, Llama-2-70B** (80 couches, 64 têtes de requête, 8 têtes KV, `head_dim` = 128, fp16) :

```text
GQA: 2 × 80 × 8  × 128 × 2 bytes =   327,680 bytes ≈ 320 KB/token
MHA: 2 × 80 × 64 × 128 × 2 bytes = 2,621,440 bytes ≈ 2.5 MB/token   (8x GQA, the num_heads:num_kv_heads ratio)
```

## Passer à une empreinte totale

```text
total cache bytes = bytes per token × context length × batch size
```

| Modèle | Par token | Contexte | Batch | Total |
|---|---|---|---|---|
| Llama-2-7B, MHA, fp16 | 512 KB | 4096 | 1 | ~2 GB |
| Llama-2-7B, MHA, fp16 | 512 KB | 4096 | 16 | ~32 GB |
| Llama-2-70B, GQA, fp16 | 320 KB | 4096 | 1 | ~1.25 GB |
| Llama-2-70B, GQA, fp16 | 320 KB | 4096 | 32 | ~40 GB |

<a id="capacity-budget"></a>

## Budget de capacité

```text
max concurrent sequences = (total memory - weights - overhead) / (bytes per token × context length)
```

Llama-2-70B, en parallélisme tensoriel sur quatre GPU de 80 GB (pool de 320 GB), poids plus surcoût du framework mesurés à 160 GB, contexte de 4096 tokens :

```text
160 GB / 1.25 GB per sequence ≈ 128 concurrent sequences
```

C'est ce plafond, et non le débit brut du modèle, contre lequel un ordonnanceur de batching négocie le plus souvent ; voir [Batching](batching.md).

## Le prefill réclame l'essentiel de l'empreinte en une seule étape

| Phase | Ce qu'elle fait | Croissance du cache |
|---|---|---|
| Prefill | Traite tout le prompt en une seule passe avant | Saute immédiatement à `bytes per token × prompt length` ; limité par le calcul |
| Decode | Génère un token de sortie à la fois | Croît de `bytes per token` par étape ; limité par la bande passante mémoire |

**Exemple détaillé**, un prompt de 2048 tokens suivi de 128 étapes de decode, Llama-2-70B à 320 KB/token :

```text
prefill: 320 KB × 2048 ≈ 640 MB   (94% of the request's final cache)
decode:  320 KB × 128  ≈  40 MB   (6%, added gradually)
total:   680 MB
```

Un plan de capacité construit uniquement à partir de la « longueur de contexte finale » cache que l'essentiel de l'empreinte atterrit au prefill, en une seule étape, et non répartie sur toute la requête.

<a id="cache-precision-is-a-lever-independent-of-the-models-own-weights"></a>

## La précision du cache est un levier indépendant des poids du modèle

Le `bytes_per_value` ci-dessus n'a pas à correspondre à la précision dans laquelle le modèle calcule. Une pile de serving peut stocker le cache lui-même dans une précision plus basse, couramment fp8, pendant que le modèle calcule en bf16 ou en fp16. Il se cumule de façon multiplicative avec le partage de têtes plutôt que de s'y substituer.

```text
Llama-2-70B, GQA, fp16: 320 KB/token
Llama-2-70B, GQA, fp8:  160 KB/token   (half, only bytes_per_value changed)
```

64 séquences avec un contexte de 4096 tokens : fp16 coûte ~80 GB, fp8 coûte ~40 GB, exactement la moitié, en plus de ce que la GQA avait déjà rachetée par rapport à la MHA complète.

## Voir aussi

- [Leçon 1](../lessons/0001-the-kv-cache.md), [Leçon 2](../lessons/0002-capacity-and-batch-size.md), [Leçon 3](../lessons/0003-growth-prefill-decode-precision.md)
- [Batching](batching.md) : ce que contraint réellement le plafond de capacité que calcule cette fiche
