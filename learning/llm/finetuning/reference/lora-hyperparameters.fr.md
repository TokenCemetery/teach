---
title: "Hyperparamètres de LoRA"
description: "Rank, alpha, cibles, learning rate, variantes"
type: reference
---

# Hyperparamètres de LoRA

Fiche de décision. Lisez la version installée de la bibliothèque pour les noms exacts des paramètres, car cette surface change d'une version à l'autre.

## L'équation

```text
h = W₀x + (α/r) · BAx
```

`A` est aléatoire, `B` est nul, donc `ΔW = 0` au pas 0 et le modèle démarre identique à la base.

![L'entrée alimente deux chemins dont les sorties sont additionnées. Le chemin du haut est la matrice de base gelée. Celui du bas est l'adapter entraîné, où A projette vers le bas jusqu'à une barre large de seulement r, B reprojette vers le haut, et le résultat est mis à l'échelle par alpha sur r.](images/lora-bottleneck.svg)

La barre entre `A` et `B` fait `r` valeurs de large, et c'est le seul chemin que l'adapter a de l'entrée à la sortie. C'est ce que la section suivante entend par capacité : augmenter le rank élargit cette barre et ne change rien d'autre à l'image, ce qui explique qu'il achète de l'expressivité pour presque aucune mémoire.

## Rank

La capacité. Borne la complexité de la mise à jour que l'adapter peut exprimer.

| Rank | Convient à |
|---|---|
| 4 à 8 | Style, ton, format de sortie ; petits datasets |
| 16 à 32 | Une vraie tâche, quelques milliers d'exemples |
| 64 à 128 | Tâches plus difficiles, données plus nombreuses, comportement qui repose sur le raisonnement |
| 256+ | Approche la capacité du full fine-tuning sur de grandes données de SFT |

Le rank ne coûte presque aucune mémoire. Son vrai coût est le risque de surapprentissage sur de petites données.

## Alpha

**Seul `α/r` compte.** La convention est `α = 2r`.

| `r` | `α` | `α/r` | |
|---|---|---|---|
| 8 | 16 | 2.0 | référence |
| 16 | 32 | 2.0 | plus de capacité, même échelle |
| 16 | 16 | 1.0 | mise à jour plus faible |
| 64 | 16 | 0.25 | **piège** : capacité en hausse, influence divisée par 8 |

Augmenter `r` sans augmenter `α` *baisse* l'adapter. À partir d'un rank ≥ 64, envisagez `use_rslora=True`, qui utilise `α/√r`.

## Target modules

| Situation | Cibles |
|---|---|
| Valeur par défaut pour une vraie tâche | all linear |
| Petit dataset (< ~1k) | attention seule, rank bas |
| Style ou ton seulement | attention seule, rank bas |
| Demande de nouvelles discriminations | doit inclure le MLP |
| Reproduire un article | exactement les siennes |

`"all-linear"` se résout par rapport au modèle chargé, donc il ne peut pas devenir obsolète face à une nomenclature inhabituelle. « Attention seule » est une ablation de 2021, pas une valeur par défaut.

Noms typiques, mais **vérifiez avec `named_modules()`** :

```text
attention: q_proj  k_proj  v_proj  o_proj
mlp:       gate_proj  up_proj  down_proj
```

## Learning rate

| Méthode | Plage |
|---|---|
| Fine-tuning avec adapter | `1e-4` à `2e-4` |
| Full fine-tuning | `1e-5` à `5e-5` |

Importer un learning rate de full fine-tuning dans un run avec adapter est une cause majeure de premier résultat décevant. Utilisez un warm-up (quelques centaines de pas) et une décroissance cosinus.

## Autres réglages

| Réglage | Valeur par défaut | Notes |
|---|---|---|
| `lora_dropout` | 0.0 à 0.05 | À augmenter seulement si la loss held-out monte |
| `bias` | `"none"` | Rarement décisif ; complique la fusion |
| Epochs | 2 à 3 | Sur de petites données d'instructions ; davantage conduit généralement à mémoriser |
| Gradient checkpointing | activé | Quasiment une valeur par défaut pour les adapters |
| `use_cache` | désactivé à l'entraînement | Entre en conflit avec le checkpointing ; inutile pour entraîner |

## Variantes, par axe

| Axe | Méthode | Aide quand |
|---|---|---|
| Mise à l'échelle | rsLoRA | Rank élevé |
| Learning rates | LoRA+ | Learning rates séparés pour `A` et `B` |
| Initialisation | PiSSA, OLoRA | Convergence plus rapide ; renonce à l'initialisation à zéro |
| Initialisation | LoftQ | Entraînement face à un base model quantifié |
| Structure | DoRA | Rank maintenu bas pour une autre raison |
| Structure | AdaLoRA | Les couches ont besoin de rank inégaux |
| Structure | VeRA | La taille de l'adapter est la contrainte qui lie |

**Référence à battre :** all-linear, rank suffisant, learning rate réglé. La plupart des variantes ne la dépassent pas de plus que le bruit des seeds.

## Base model quantifié (QLoRA)

```python
BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",             # not "fp4"
    bnb_4bit_use_double_quant=True,
    bnb_4bit_compute_dtype=torch.bfloat16,  # do not leave at default
)
```

Puis `prepare_model_for_kbit_training(model, use_gradient_checkpointing=True)`. Sauter cette étape donne des runs instables ou des erreurs de gradient opaques.

Tous les autres hyperparamètres restent inchangés. **QLoRA, c'est LoRA avec un base model moins cher.**

Fusionnez dans le base model en **pleine précision**, jamais dans le base model quantifié.

## Diagnostic par la courbe

| Train | Held-out | Diagnostic | Action |
|---|---|---|---|
| ↓ | ↓ | Apprentissage | Continuer |
| ↓ | ↑ après un creux | Surapprentissage | Livrer le minimum ; moins de capacité ou plus de données |
| → haut | → haut | Sous-apprentissage | Plus de rank, plus de cibles, learning rate plus élevé |
| Plat dès le pas 1 | Plat | Cassé | Vérifier que l'adapter est attaché et que les labels ne sont pas tous `-100` |
| `NaN` | aussi `NaN` | Débordement | Baisser le learning rate ; ajouter un warm-up ; préférer bf16 |

## Voir aussi

- [Leçon 9](../lessons/0009-rank-alpha-and-initialisation.md), [Leçon 10](../lessons/0010-choosing-target-modules.md), [Leçon 19](../lessons/0019-when-dora-wins.md), [Leçon 20](../lessons/0020-judging-a-new-variant.md)
