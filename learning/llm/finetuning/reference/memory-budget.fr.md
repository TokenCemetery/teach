---
title: "Budget mémoire"
description: "Le décompte des octets, et que tenter quand un run ne tient pas"
type: reference
---

# Budget mémoire

Le décompte des octets pour le fine-tuning avec adapters. Conçu pour la consultation pendant un run.

## Octets par paramètre

| Format | Octets | Bits |
|---|---|---|
| fp32 | 4 | 32 |
| bf16 / fp16 | 2 | 16 |
| int8 | 1 | 8 |
| 4 bits, brut | 0.5 | 4 |
| 4 bits + échelles fp32, bloc de 64 | 0.5625 | 4.5 |
| 4 bits + double quantification | ~0.516 | ~4.13 |

**Réflexe :** les gigaoctets en bf16 ≈ 2 × les paramètres en milliards.

## Coût d'entraînement par paramètre

| Catégorie | fp32 | Précision mixte |
|---|---|---|
| Poids | 4 | 2 bf16 + 4 fp32 maître |
| Gradients | 4 | 2 |
| Moment 1 d'AdamW | 4 | 4 |
| Moment 2 d'AdamW | 4 | 4 |
| **Total entraînable** | **16** | **16** |
| **Total gelé** | **4** | **2** |

La précision mixte ne réduit pas le total. Elle achète du débit de calcul arithmétique.

| Variante d'optimizer | Octets/paramètre |
|---|---|
| AdamW, moments en fp32 | 16 |
| AdamW, moments en 8 bits | 10 |
| SGD avec momentum | 12 |

## Nombre de paramètres

```text
attention/layer = 2·d² + 2·d·d_kv          # q,o full; k,v narrowed by GQA
mlp/layer       = 3·d·d_ff                  # gate, up, down
model           ≈ n_layers·(attn + mlp) + vocab·d·(1 if tied else 2)
```

Le MLP représente typiquement de 75 à 80 % d'un bloc.

## Nombre de paramètres d'un adapter

```text
adapter = Σ over targeted layers:  r · (d_in + d_out)
```

Dominé par la dimension la **plus grande**, si bien que le rétrécissement de GQA réduit à peine un adapter.

| Base | Cibles | Rank | Adapter | % de la base |
|---|---|---|---|---|
| ~1.1B, d=2048 | attention | 8 | 2.5M | 0.22 % |
| ~7B, d=4096 | q,v | 16 | 6.8M | 0.10 % |
| ~7B, d=4096 | all-linear | 64 | ~160M | ~2.3 % |

## Activations

```text
activations ≈ n_layers · batch · seq_len · d · ~20 bytes
```

La constante est un point de départ à confronter à la mesure, pas une loi. Linéaire en batch et en longueur de séquence ; le terme quadratique des scores d'attention est supprimé par un kernel d'attention économe en mémoire.

| Configuration | Estimation |
|---|---|
| 24 couches, d=2048, batch 4, seq 2048 | ~8 Go |
| 32 couches, d=4096, batch 2, seq 4096 | ~21 Go |

Le gradient checkpointing réduit cela d'environ un ordre de grandeur, pour ~20 à 40 % de temps de pas en plus.

**Dans un run avec adapter, les activations dominent généralement.** Cela inverse le profil du full fine-tuning.

![Deux barres empilées sur une même échelle en gigaoctets. Un full fine-tuning d'un 7B avec AdamW représente 112 Go fixes plus 21 Go d'activations, donc les activations en font 16 %. Un run QLoRA sur un base model 7B en NF4 avec un adapter de 20M représente 3.9 Go fixes plus les mêmes 21 Go, donc les activations en font 84 %.](images/activations-dominate.svg)

Les deux barres prennent la mémoire fixe dans le tableau ci-dessous et les activations dans la ligne 32 couches, d=4096, batch 2, seq 4096 ci-dessus, sans gradient checkpointing. Le bloc d'activations a la même taille dans les deux, parce qu'il dépend de la forme de la passe avant et non du nombre de paramètres entraînables. Seule la mémoire autour s'effondre, c'est pourquoi ce qu'il faut réduire est rarement l'adapter.

## Totaux calculés, activations exclues

| Configuration | Mémoire fixe |
|---|---|
| Full FT, 1.5B, AdamW | 24 Go |
| Full FT, 7B, AdamW | 112 Go |
| Full FT, 70B, AdamW | 1120 Go |
| Base 7B en bf16 + adapter de 20M | 14.3 Go |
| Base 7B en NF4 + adapter de 20M | ~3.9 Go |
| Base 13B en NF4 + adapter de 30M | ~7.2 Go |

## Quand un run ne tient pas

Dans l'ordre de ce à quoi vous renoncez :

1. **Gradient checkpointing**, ne coûte que du temps
2. **Batch size plus petite, gradient accumulation plus grande**, statistiquement équivalent
3. **Longueur de séquence plus courte**, mais examinez d'abord la distribution des longueurs en tokens ; cela change la tâche
4. **Quantifier le base model**, coûte un peu de qualité
5. **Rank plus bas**, économise le moins et coûte de la capacité

Le rank est le réflexe et presque la pire option. Diviser par deux le rank d'un adapter de 4M économise ~32 Mo.

## Batch size effective

```text
effective = per_device_batch × grad_accumulation × num_devices
```

Rapportez toujours le chiffre effectif.

## Voir aussi

- [Leçon 5](../lessons/0005-counting-parameters-and-bytes.md), [Leçon 6](../lessons/0006-gradients-and-optimizer-state.md), [Leçon 7](../lessons/0007-activations-and-checkpointing.md), [Leçon 15](../lessons/0015-nf4-and-double-quantisation.md)
