---
title: "8. L'idée du faible rang"
description: "`ΔW = BA`, et compter un adapter"
type: lesson
---

# Leçon 8. L'idée du faible rang

**Lien avec la mission :** LoRA est la méthode sur laquelle repose tout le reste de la mission. Cette leçon est le mécanisme ; les deux suivantes sont les décisions.
**Source primaire :** [Article : "LoRA: Low-Rank Adaptation of Large Language Models", Hu et al., arXiv:2106.09685](https://arxiv.org/abs/2106.09685)
**Prérequis :** [Leçon 6](0006-gradients-and-optimizer-state.md), [Leçon 7](0007-activations-and-checkpointing.md), [adapter](../GLOSSARY.md)

## Échauffement

1. ▢ Octets par paramètre entraînable, et par paramètre gelé ?

<details markdown="1"><summary>Vérifier</summary>

Seize pour un paramètre entraînable, deux pour un paramètre gelé. Le rapport de huit contre un est la raison d'être des adapters.

</details>

2. ▢ Votre run avec adapter manque de mémoire. Que changez-vous en premier, et que ne changez-vous pas ?

<details markdown="1"><summary>Vérifier</summary>

Activez le gradient checkpointing, puis réduisez la batch size par appareil avec de l'accumulation pour compenser. Ne réduisez pas le rank : l'état de l'adapter se compte en mégaoctets, contre des gigaoctets d'activations.

</details>

3. ▢ Quelle catégorie de mémoire n'est pas affectée par le gel du base model ?

<details markdown="1"><summary>Vérifier</summary>

Les activations. Elles évoluent avec la batch size et la longueur de séquence, pas avec le nombre de paramètres entraînables.

</details>

## À savoir

Le full fine-tuning apprend une mise à jour `ΔW` pour chaque matrice de poids, de la même forme que `W`. L'affirmation de LoRA est que cette mise à jour n'a pas besoin d'être de rang plein, parce que le changement qu'exige une tâche occupe un sous-espace de faible dimension.

Donc, au lieu de stocker `ΔW` directement, on le factorise :

```text
ΔW = B A

A : r × d_in     (down-projection, r is small)
B : d_out × r    (up-projection)
```

et la couche adaptée calcule :

```text
h = W₀ x + (α / r) · B A x
```

`W₀` est gelé. Seuls `A` et `B` reçoivent des gradients.

### Pourquoi cela économise autant

Une matrice `d_in × d_out` contient `d_in · d_out` paramètres. Sa factorisation de rang `r` en contient `r · (d_in + d_out)`. Pour une projection 2048 × 2048 au rank 8 :

```text
full        = 2048 × 2048        = 4,194,304
rank 8      = 8 × (2048 + 2048)  =    32,768
```

Une réduction de 128× sur cette seule matrice. Sur un modèle entier, l'économie se cumule, parce que vous évitez aussi le gradient et les deux moments d'optimizer pour tout ce que vous n'avez pas rendu entraînable.

### Compter un adapter

La formule, pour un ensemble de target modules :

```text
adapter params = Σ over targeted layers of  r × (d_in + d_out)
```

Calculé pour le modèle de 24 couches avec `d = 2048` et `d_kv = 256` de la leçon 5, rank 8, en ciblant les quatre projections d'attention :

```text
q_proj: 2048 → 2048   →  8 × (2048 + 2048) = 32,768
k_proj: 2048 →  256   →  8 × (2048 +  256) = 18,432
v_proj: 2048 →  256   →  8 × (2048 +  256) = 18,432
o_proj: 2048 → 2048   →  8 × (2048 + 2048) = 32,768
per layer                                  = 102,400
× 24 layers                                = 2,457,600
```

Environ 2.5M paramètres entraînables face à un base model de 1.12B, soit **0.22 %**. L'état d'optimizer de cet adapter fait 2.5e6 × 16 ≈ 39 Mo.

Notez que le rétrécissement de la grouped-query attention compte ici d'une manière qui ne comptait pas pour le base model : les adapters de `k_proj` et `v_proj` ne sont *pas* proportionnellement plus petits, parce que `r × (d_in + d_out)` est dominé par la plus grande des deux dimensions. Réduire `d_out` de 2048 à 256 a divisé la matrice de base par 8, mais l'adapter seulement par 1.8.

### Pourquoi un faible rang suffit

L'affirmation empirique repose sur la **dimension intrinsèque** : l'observation que le fine-tuning d'un grand modèle préentraîné vers une nouvelle tâche peut se faire dans un sous-espace étonnamment petit de son espace de paramètres, et que les modèles plus grands et mieux préentraînés ont une dimension intrinsèque *plus basse*, pas plus haute (Aghajanyan et al., [arXiv:2012.13255](https://arxiv.org/abs/2012.13255)). Le préentraînement a déjà construit les features ; l'adaptation consiste en grande partie à les repondérer et à les recombiner, et c'est une petite opération.

Deux réserves honnêtes :

**C'est une affirmation empirique, pas un théorème.** Elle tient bien pour adapter un comportement, un style, un format et une compétence étroite sur une tâche. Elle tient moins bien pour installer de grands volumes de connaissances réellement nouvelles, ce qui est l'un des arguments de la leçon 27.

**« Faible » est relatif et a évolué.** Les premières pratiques se sont arrêtées à des rank comme 8 ou 16, en partie parce que la mémoire était rare. Des travaux plus récents, dans la [Leçon 10](0010-choosing-target-modules.md), constatent que sur de nombreuses tâches de fine-tuning supervisé, des adapters généreusement dotés en rank et couvrant toutes les couches linéaires égalent le full fine-tuning, alors que des adapters chiches non. Le rank 8 est un point de départ, pas une loi.

### La propriété d'inférence qui rend LoRA spécial

Comme la mise à jour est *additive* et linéaire, elle peut être refondue dans le poids de base après l'entraînement :

```text
W = W₀ + (α / r) · B A
```

Le résultat est une matrice de poids ordinaire. **Un LoRA fusionné a exactement zéro surcoût à l'inférence** : pas de multiplications de matrices supplémentaires, pas d'architecture modifiée, rien à installer au moment du service. C'est la propriété qui distingue LoRA des méthodes à couches d'adaptation qui l'ont précédé, lesquelles inséraient de nouveaux modules dans le chemin de la passe avant et payaient de la latence pour toujours. La leçon 13 traite la fusion en pratique, et la leçon 25 traite des cas où *ne pas* fusionner.

## Pratique

1. ▢ Calculez les paramètres entraînables d'un adapter de rank 16 sur `q_proj` et `v_proj` seulement, dans un modèle de 32 couches avec `d = 4096` et `d_kv = 1024`.

<details markdown="1"><summary>Vérifier</summary>

`q_proj` : 16 × (4096 + 4096) = 131,072.
`v_proj` : 16 × (4096 + 1024) = 81,920.
Par couche : 212,992. Fois 32 couches ≈ 6.82M.

Face à un base model d'environ 7B, cela fait 0.10 %.

</details>

2. ▢ Pourquoi une factorisation de rang `r` d'une matrice `d × d` économise-t-elle bien plus quand `d` est grand ?

<details markdown="1"><summary>Vérifier</summary>

La matrice complète croît comme `d²` tandis que la factorisation croît comme `2rd`, c'est-à-dire linéairement. Le rapport `d / 2r` s'améliore donc à mesure que le modèle s'élargit.

C'est pourquoi LoRA devient *relativement* moins cher sur les gros modèles, et pourquoi la méthode a gagné en importance à mesure que les modèles grandissaient.

</details>

3. ▢ Quel est l'argument de la dimension intrinsèque, et quelle est sa limite ?

<details markdown="1"><summary>Vérifier</summary>

Adapter un modèle bien préentraîné à une tâche n'exige de se déplacer que dans un sous-espace de faible dimension de l'espace des paramètres, parce que le préentraînement a déjà construit les features nécessaires.

Sa limite : c'est un constat empirique sur l'*adaptation*, le plus fort pour le comportement et le format et le plus faible pour installer des connaissances factuelles nouvelles substantielles. Il ne vous dit pas non plus quel rank suffit pour votre tâche précise.

</details>

4. ▢ Pourquoi un LoRA fusionné n'a-t-il aucun surcoût à l'inférence, alors que les anciennes méthodes à couches d'adaptation en avaient un ?

<details markdown="1"><summary>Vérifier</summary>

La mise à jour de LoRA est additive et linéaire dans le même espace que le poids, donc `W₀ + (α/r)BA` se réduit à une seule matrice ordinaire. Les méthodes à couches d'adaptation insèrent de nouveaux modules non linéaires dans le chemin de la passe avant, qui ne peuvent pas être refondus et ajoutent donc de la latence à chaque couche pour toujours.

</details>

5. ▢ Vrai ou faux : un adapter de rank 8 peut représenter n'importe quelle mise à jour qu'un full fine-tuning pourrait produire.

<details markdown="1"><summary>Vérifier</summary>

Faux. `ΔW = BA` avec `B` à `r` colonnes a un rang d'au plus `r`, donc il ne peut atteindre que des mises à jour situées dans un sous-espace de rank 8. Un full fine-tuning peut produire une mise à jour de rang plein.

Le pari est que la mise à jour dont votre tâche a besoin se situe près d'un tel sous-espace. Quand ce n'est pas le cas, cela se voit comme un plancher de loss que davantage d'entraînement n'abaisse pas, et le correctif est davantage de rank ou de target modules plutôt que davantage d'epochs.

</details>

6. ▢ Avec la grouped-query attention, la sortie de `v_proj` passe de 4096 à 512. De quel facteur la matrice de base rétrécit-elle, et de quel facteur son adapter de rank 16 rétrécit-il ?

<details markdown="1"><summary>Vérifier</summary>

Base : 4096 × 4096 → 4096 × 512, une réduction de 8×.
Adapter : 16 × (4096 + 4096) = 131,072 → 16 × (4096 + 512) = 73,728, une réduction de 1.8×.

Le coût de l'adapter est piloté par la somme des dimensions, donc il est dominé par la plus grande. Réduire la plus petite n'aide presque pas.

</details>

## Exercices en situation réelle

- [ ] Calculez à la main le nombre de paramètres d'adapter pour un modèle et un ensemble de cibles que vous comptez réellement utiliser. Gardez le chiffre.
- [ ] Construisez l'adapter en code et affichez le nombre de paramètres entraînables. Il doit correspondre à votre calcul à la main. Si ce n'est pas le cas, trouvez quel module vous avez mal dimensionné.
- [ ] Demain : recalculez le même adapter aux rank 8, 32 et 128, et notez comment change le pourcentage du base model.

## Pour aller plus loin

- [Article : "LoRA: Low-Rank Adaptation of Large Language Models", Hu et al., arXiv:2106.09685](https://arxiv.org/abs/2106.09685)
- [Article : "Intrinsic Dimensionality Explains the Effectiveness of Language Model Fine-Tuning", Aghajanyan et al., arXiv:2012.13255](https://arxiv.org/abs/2012.13255)
- [Hyperparamètres de LoRA](../reference/lora-hyperparameters.md)
- [Leçon 9. Rank, alpha et initialisation](0009-rank-alpha-and-initialisation.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
