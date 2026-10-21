---
title: "18. DoRA : magnitude et direction"
description: "La renormalisation découple les deux, et c'est cela, la méthode"
type: lesson
---

# Leçon 18. DoRA : magnitude et direction

**Lien avec la mission :** La troisième méthode nommée dans la mission, et celle dont le mécanisme est le plus souvent décrit de travers.
**Source primaire :** [Article : "DoRA: Weight-Decomposed Low-Rank Adaptation", Liu et al., arXiv:2402.09353](https://arxiv.org/abs/2402.09353)
**Prérequis :** [Leçon 8](0008-the-low-rank-idea.md), [Leçon 9](0009-rank-alpha-and-initialisation.md)

## Échauffement

1. ▢ Écrivez la mise à jour de LoRA et dites quels facteurs sont entraînables.

<details markdown="1"><summary>Vérifier</summary>

`h = W₀x + (α/r)BAx`. Seuls `A` et `B` sont entraînables ; `W₀` est gelé. `B` démarre à zéro.

</details>

2. ▢ Quel est le rang maximal d'une mise à jour LoRA à `r = 8` ?

<details markdown="1"><summary>Vérifier</summary>

Huit. `BA` ne peut pas dépasser le rang de sa dimension interne, ce qui borne les mises à jour que l'adapter peut exprimer.

</details>

3. ▢ Pourquoi la quantification n'est-elle pas gratuite sur les petits modèles ?

<details markdown="1"><summary>Vérifier</summary>

L'erreur de quantification est une perturbation relative fixe, et les petits modèles ont moins de redondance disponible pour l'absorber.

</details>

## À savoir

### L'observation

Toute matrice de poids peut se décomposer en une **magnitude** et une **direction**. Colonne par colonne :

```text
W = m · (V / ‖V‖_c)
```

où `‖·‖_c` est la norme par colonne, `V / ‖V‖_c` est une matrice de colonnes de norme unité, c'est-à-dire de la pure direction, et `m` est un vecteur d'un scalaire par colonne, qui porte la magnitude.

Les auteurs de DoRA ont analysé comment le full fine-tuning et LoRA déplacent chacune de ces deux grandeurs pendant l'entraînement, et ont constaté que les schémas diffèrent. Le full fine-tuning tend à faire des changements de direction relativement grands avec des changements de magnitude comparativement modestes, et montre une relation distinctive entre les deux. Les mises à jour de LoRA déplacent la magnitude et la direction ensemble de manière plus couplée, parce qu'un seul terme additif de faible rang change les deux à la fois et n'a aucun moyen de les ajuster indépendamment.

L'hypothèse : ce couplage est une limitation, et découpler les deux devrait donner à LoRA un comportement d'apprentissage plus proche de celui du full fine-tuning.

### La méthode

Décomposer le `W₀` gelé en sa magnitude et sa direction. Puis :

- Rendre le **vecteur de magnitude `m` directement entraînable.** C'est un scalaire par colonne, donc `d_out` paramètres, négligeable.
- Appliquer la **mise à jour de faible rang à la direction**, et renormaliser ensuite.

```text
W' = m · (W₀ + BA) / ‖W₀ + BA‖_c
```

Lisez cela attentivement, car c'est là que les descriptions se trompent. `BA` est ajouté au poids puis le résultat est **renormalisé en colonnes unité**, ce qui élimine tout changement de magnitude introduit par `BA`. La magnitude est alors fournie séparément et explicitement par le `m` entraînable.

Ainsi `BA` ne peut plus changer la magnitude, même par accident, puisqu'il ne fait qu'orienter la direction, et `m` gère l'échelle. C'est le découplage, et c'est toute la contribution.

![Une colonne d'une matrice de poids sous forme de vecteur à partir d'une origine, avec un quart de cercle en pointillés qui marque la norme unité. À gauche, W0 plus BA atterrit quelque part avec un angle différent et une longueur différente. À droite, seul l'angle survit : la direction se trouve sur le cercle unité et m fixe la longueur, ici revenue à celle de W0.](images/length-and-angle.svg)

Les deux panneaux utilisent le même `W0` et le même `BA`. À gauche, un seul terme a déplacé les deux grandeurs à la fois ; à droite, l'angle est tout ce que `BA` a apporté, et la longueur est ce que `m` dit qu'elle est.

### Ce que cela coûte

**Paramètres :** un vecteur supplémentaire par couche adaptée, de longueur `d_out`. Pour une couche de largeur 4096, cela fait 4096 nombres contre les 131,072 d'un adapter de rank 16. Quasiment gratuit.

**Calcul :** pas gratuit. La norme par colonne de `W₀ + BA` doit être calculée, et elle dépend de `BA`, donc elle change à chaque pas et ne peut pas être mise en cache d'une mise à jour à l'autre. DoRA est donc mesurablement plus lent par pas que LoRA, couramment de l'ordre de quelques dizaines de pourcents, selon l'implémentation et la part du travail que la bibliothèque parvient à fusionner ou à mettre en cache.

**Complexité :** la fusion est plus délicate. Le poids fusionné est `m · (W₀ + BA)/‖W₀ + BA‖_c`, toujours une matrice ordinaire, donc un DoRA fusionné est exact et n'a aucun surcoût à l'inférence, exactement comme LoRA. Mais l'arithmétique pour y arriver n'est pas une simple addition, et l'implémentation compte.

### L'utiliser

Dans PEFT, DoRA est un flag de la configuration LoRA plutôt qu'une méthode séparée :

```text
config := {
    use_dora: true,
    rank: 8,
    alpha: 32,
    target_modules: "all-linear",
    dropout: 0.05,
    adapt_bias: false,
}
```

Tout ce que vous savez sur le rank, alpha, les target modules et le learning rate se transpose. C'est une modification de la façon dont la mise à jour est appliquée, pas un nouvel ensemble de décisions. Confirmez le nom du flag dans la version installée, comme toujours.

DoRA se combine aussi avec la quantification : un base model quantifié plus un adapter DoRA, parfois appelé QDoRA. L'interaction mérite d'être mesurée plutôt que supposée : la renormalisation opère maintenant sur des poids déquantifiés porteurs d'erreur de quantification, ce qui n'est pas manifestement inoffensif.

### Le résumé honnête

DoRA est un raffinement bien motivé, avec un mécanisme clair, des gains annoncés concentrés à bas rank, et un vrai coût en vitesse. Ce n'est pas un remplaçant de LoRA et ce n'est pas un effet important à tous les réglages. La leçon 19 porte sur la prédiction du moment où il se rentabilisera.

## Pratique

1. ▢ Écrivez la formule de DoRA et identifiez chaque grandeur entraînable.

<details markdown="1"><summary>Vérifier</summary>

`W' = m · (W₀ + BA) / ‖W₀ + BA‖_c`.

Entraînables : le vecteur de magnitude `m`, plus `A` et `B`. Gelé : `W₀`.

</details>

2. ▢ Que permet d'accomplir la renormalisation ?

<details markdown="1"><summary>Vérifier</summary>

Elle élimine tout changement de magnitude introduit par `BA`, ce qui laisse `BA` capable d'affecter la direction seulement. La magnitude est ensuite fixée explicitement par le `m` entraînable.

Cette séparation est le découplage qui donne son nom à la méthode.

</details>

3. ▢ Pourquoi DoRA est-il plus lent que LoRA alors qu'il n'ajoute presque aucun paramètre ?

<details markdown="1"><summary>Vérifier</summary>

La norme par colonne de `W₀ + BA` doit être calculée, et comme elle dépend de `BA`, elle change à chaque pas et ne peut pas être mise en cache d'une mise à jour à l'autre. Les paramètres supplémentaires sont négligeables ; l'arithmétique supplémentaire ne l'est pas.

</details>

4. ▢ Combien de paramètres supplémentaires DoRA ajoute-t-il à une couche 4096 × 4096, et comment cela se compare-t-il à un LoRA de rank 16 sur cette couche ?

<details markdown="1"><summary>Vérifier</summary>

4096, un scalaire de magnitude par colonne de sortie.

Un LoRA de rank 16 sur cette couche fait 16 × (4096 + 4096) = 131,072. L'ajout de DoRA représente donc environ 3 % en plus, ce qui n'est pas la raison d'hésiter. Le temps par pas, si.

</details>

5. ▢ Un DoRA fusionné a-t-il un surcoût à l'inférence ?

<details markdown="1"><summary>Vérifier</summary>

Non. Le résultat fusionné `m · (W₀ + BA)/‖W₀ + BA‖_c` est une matrice de poids ordinaire, donc un DoRA fusionné est indiscernable de n'importe quel autre modèle à l'inférence.

L'arithmétique pour le produire est plus délicate que la simple addition de LoRA, mais le produit est le même genre de chose.

</details>

6. ▢ Quel énoncé décrit correctement DoRA ?

    - a) Il ajoute une seconde mise à jour de faible rang au terme de magnitude
    - b) Il entraîne la magnitude directement et met à jour la direction par un faible rang
    - c) Il remplace la mise à jour de faible rang par une mise à l'échelle de rang plein
    - d) Il normalise les gradients plutôt que la matrice de poids

<details markdown="1"><summary>Vérifier</summary>

**b)** Il entraîne la magnitude directement et met à jour la direction par un faible rang.

Il n'y a pas de second facteur de faible rang. La mise à jour n'est pas de rang plein. La normalisation s'applique au poids, pas aux gradients.

</details>

## Exercices en situation réelle

- [ ] Implémentez la décomposition à la main : prenez une matrice de poids, calculez les normes par colonne, séparez en `m` et en `V` de norme unité, et vérifiez que `m · V` la reconstruit.
- [ ] Entraînez la même configuration avec `use_dora=True` et `False`. Notez les secondes par pas pour les deux et calculez le surcoût.
- [ ] Demain : lisez la section 4 de l'article DoRA, où est présentée l'analyse magnitude-direction du full fine-tuning face à LoRA. Cette analyse est l'argument.

## Pour aller plus loin

- [Article : "DoRA: Weight-Decomposed Low-Rank Adaptation", Liu et al., arXiv:2402.09353](https://arxiv.org/abs/2402.09353)
- [Doc : LoRA variants, Hugging Face PEFT](https://huggingface.co/docs/peft/main/en/developer_guides/lora)
- [Leçon 19. Quand DoRA gagne, et quand non](0019-when-dora-wins.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
