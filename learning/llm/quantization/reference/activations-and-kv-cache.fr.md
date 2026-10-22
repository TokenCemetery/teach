---
title: "Activations et KV cache"
description: "Weight-only contre poids-et-activations, SmoothQuant, rotations et quantification du KV cache pour la consultation"
type: reference
---

# Activations et KV cache : quantifier au-delà des poids

L'étape 5 condensée pour la consultation. La [leçon 13](../lessons/0013-weights-activations-or-both.md) couvre le weight-only contre le poids-et-activations, la [leçon 14](../lessons/0014-smoothquant.md) SmoothQuant, la [leçon 15](../lessons/0015-rotations.md) les rotations, et la [leçon 16](../lessons/0016-kv-cache-quantization.md) la quantification du KV cache.

## Poids, activations ou les deux

| Schéma | Stocké petit | La multiplication de matrices tourne en | Achète | Convient à |
|---|---|---|---|---|
| W4A16, W8A16 (weight-only) | Poids | 16 bits, après déquantification dans le kernel | Mémoire, octets lus par token | Limité par la mémoire : décodage à petit batch |
| W8A8 int8 ou fp8 | Poids et activations | 8 bits | Débit arithmétique, plus mémoire | Limité par le calcul : prefill, grands batchs |
| W4A4 avec rotations | Poids, activations, souvent KV | 4 bits | Mémoire et arithmétique | Seulement là où un kernel 4 bits existe, voir la leçon 20 |

Kurtic et al. (famille Llama 3.1, plus de 500,000 évaluations) : le fp8 W8A8 est effectivement sans perte, l'int8 W8A8 bien réglé perd 1 à 3 % de précision, le W4A16 int rivalise avec le 8 bits. Conseil : W4A16 pour le serving synchrone, W8A8 pour le continuous batching.

## Pourquoi les activations sont plus difficiles

| Propriété | Poids | Activations |
|---|---|---|
| Plage connue | Après l'entraînement, fixe | Seulement à l'exécution |
| Outliers | Plats, faciles à quantifier | Environ 100 fois la plupart des valeurs, dans des canaux fixes sur tous les tokens (SmoothQuant) |
| Granularité de scale qu'un GEMM int8 permet | Par canal de sortie | Par tenseur ou par token seulement |

Le GEMM int8 : `Y = diag(s_X) · (X_int8 @ W_int8) · diag(s_W)`. Les scales ne se placent que sur les dimensions extérieures ; un scale par canal d'entrée se placerait à l'intérieur de la somme.

| Scale d'activation | Calculé | Coût | Risque |
|---|---|---|---|
| Statique | Hors ligne, à partir d'un calibration set | Aucun par requête | Calibration set différent du trafic réel |
| Dynamique | À l'exécution, à partir du tenseur | Une réduction avant chaque multiplication de matrices | Faible ; s'adapte à chaque entrée |

## SmoothQuant

```text
X @ W = (X @ diag(s)^-1) @ (diag(s) @ W)
s_j   = max(|X_j|)^α / max(|W_j|)^(1 - α)
```

| `α` | Effet |
|---|---|
| 0 | Activations inchangées |
| 0.5 | Valeur par défaut équilibrée de l'article, point idéal pour OPT et BLOOM |
| Plus grand, vers 1 | Plus de difficulté dans les poids ; pour les modèles à outliers plus lourds, comme GLM-130B |
| 1 | Chaque canal d'activation a le même maximum ; les poids portent tous les outliers |

- `max(|X_j|)` vient d'un calibration set.
- Le facteur est fusionné hors ligne dans la couche qui produit `X` : aucun coût à l'exécution.
- Une méthode en 8 bits : jusqu'à 1.56x d'accélération et 2x de réduction de mémoire dans l'article.

## Rotations

```text
X @ W = (X @ Q) @ (Q.T @ W)      where Q @ Q.T = I
```

| Point | Détail |
|---|---|
| Ce que cela fait | Répartit un outlier sur tous les canaux ; max proche du RMS |
| `Q` habituelle | Hadamard randomisée : entrées ±1/sqrt(n), coût `n log n` |
| Fusionné hors ligne | Rotation du flux résiduel, dans les poids |
| En ligne | Avant la projection descendante du FFN ; par tête sur les requêtes et les clés, après RoPE |
| QuaRot | Tous les poids, activations et le KV cache en 4 bits ; Llama 2 70B à 0.47 de perplexity WikiText-2, 99 % du zero-shot |
| SpinQuant | Les rotations aléatoires diffèrent jusqu'à 13 points zero-shot ; les rotations apprises réduisent l'écart à 2.9 points sur Llama 2 7B W4A4KV4 |

Question de relecture pour toute affirmation W4A4 : quelle rotation, et a-t-elle été choisie ou apprise pour ce modèle ?

## Quantification du KV cache

```text
KV bytes per token = 2 x layers x kv_heads x head_dim x bytes_per_value
```

Llama 3 8B (32 couches, 8 têtes KV, dimension 128) en bf16 : 128 KiB par token, 4 GiB par séquence de 32,768 tokens.

| Tenseur | Quantifier selon | Pourquoi |
|---|---|---|
| Clés | Par canal, avant RoPE si possible | Quelques canaux outlier fixes (KIVI) ; RoPE mélange les paires de canaux (KVQuant) |
| Valeurs | Par token | Aucun motif par canal ; presque 15 fois moins d'erreur sur la sortie de l'attention que par canal (KIVI) |

| Méthode ou option | Bits | Résultat rapporté |
|---|---|---|
| KIVI | 2 | Presque la même qualité, 2.6x moins de mémoire de pointe, jusqu'à 4x de batch, 2.35 à 3.47x de débit |
| KVQuant | 3 | Moins de 0.1 de dégradation de perplexity ; LLaMA-7B à 1M de contexte sur un seul A100 de 80 GB |
| KV cache fp8 de vLLM | 8 | Scales par tenseur ou par tête ; scales par défaut de 1.0 sans calibration, calibration recommandée |

KIVI garde les tokens les plus récents (128 dans ses expériences) en pleine précision jusqu'à ce qu'un groupe de clés par canal soit complet.
