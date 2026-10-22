---
title: "9. La récompense implicite de DPO : pourquoi la fonction de partition s'annule"
description: "Un terme de normalisation intraitable se dresse entre une récompense et sa policy optimale, jusqu'à ce qu'une différence de deux récompenses le fasse disparaître"
type: lesson
---

# Leçon 9. La récompense implicite de DPO : pourquoi la fonction de partition s'annule

**Lien avec la mission :** « Dériver la récompense implicite de DPO à partir des mêmes données de préférence que RLHF, et dire ce à quoi elle renonce en supprimant la boucle de RL » est la quatrième puce sous « Objectif ». Cette leçon couvre la dérivation elle-même ; la leçon 10 couvre la loss qui en résulte et ce qu'elle abandonne par rapport à PPO.
**Source primaire :** [Article : "Direct Preference Optimization: Your Language Model is Secretly a Reward Model", Rafailov et al., 2023](https://arxiv.org/abs/2305.18290)
**Prérequis :** [Leçon 8](0008-why-ppo-is-expensive-and-unstable.md)

## Échauffement

1. ▢ Nommez les quatre modèles (ou cinq, si l'on compte la value function séparément) impliqués dans un pas d'entraînement PPO pour RLHF, et à quoi sert chacun.

<details markdown="1"><summary>Vérifier</summary>

La policy entraînée ; un modèle SFT figé, pour la pénalité KL ; le reward model, qui note les sorties ; et la value function (initialisée à partir du reward model), qui produit les estimations d'avantage dont le clipping de PPO a besoin.

</details>

2. ▢ D'après la propre constatation d'Ouyang et al., un reward model plus grand et à plus faible loss était-il toujours le meilleur choix pratique pour PPO ?

<details markdown="1"><summary>Vérifier</summary>

Non. Leur reward model de 175B avait un entraînement plus instable et un coût de calcul plus élevé comme initialisation de la value function que leur modèle de 6B, qu'ils ont trouvé stable et tout aussi efficace, si bien qu'ils ont utilisé le plus petit pour toutes les tailles de policy.

</details>

## À savoir

### Le même objectif de départ que RLHF

Rafailov et al. partent exactement de l'objectif de maximisation de récompense sous contrainte KL que couvre déjà la leçon 6 : maximiser la récompense espérée `r(x, y)` sous la policy, moins une pénalité KL (mise à l'échelle par `β`) contre une policy de référence figée `π_ref`. Des travaux antérieurs, sur lesquels s'appuient directement Rafailov et al., ont montré que cet objectif a une solution optimale connue, sous forme close :

```text
π_r(y|x) = (1 / Z(x)) · π_ref(y|x) · exp((1/β) · r(x, y))
```

où `Z(x)` est une **fonction de partition**, une somme de normalisation sur toutes les complétions possibles `y` du prompt `x`, nécessaire pour que `π_r` soit une distribution de probabilité valide. Calculer `Z(x)` exactement reviendrait à sommer sur toutes les complétions qu'un modèle de langage pourrait générer, ce qui est aussi intraitable que cela en a l'air, et c'est précisément pourquoi cette forme close, correcte telle quelle, n'était pas directement utilisable comme méthode d'entraînement.

### Inverser la relation

Le coup de Rafailov et al. consiste à réarranger cette même équation pour résoudre la récompense au lieu de la policy. Prendre le logarithme des deux côtés et réarranger donne :

```text
r(x, y) = β · log( π_r(y|x) / π_ref(y|x) ) + β · log Z(x)
```

Cela exprime la récompense impliquée par n'importe quelle policy `π_r`, en fonction de cette policy, de la policy de référence et de la même fonction de partition gênante, toujours présente comme terme additif.

### Pourquoi la fonction de partition cesse de compter

C'est là que la loss de Bradley-Terry (leçon 4) fait un vrai travail. Les probabilités de préférence de Bradley-Terry ne dépendent que de la *différence* entre les récompenses de deux complétions, `r(x, y_1) - r(x, y_2)`, jamais de la valeur absolue de l'une ou l'autre. Comme `Z(x)` ne dépend que du prompt `x`, pas de la complétion `y` qu'on note, c'est exactement le même terme additif dans `r(x, y_1)` et dans `r(x, y_2)`. Substituer l'expression inversée de la récompense dans une différence de deux récompenses pour le même prompt fait s'annuler complètement chaque terme `β · log Z(x)`. Ce qui reste est une probabilité de préférence exprimée uniquement en fonction de la policy `π_r` et de la policy de référence figée `π_ref`, sans reward model ni fonction de partition nulle part.

### La récompense implicite

C'est exactement ce que nomme le terme du glossaire de la leçon 4, **récompense implicite** : la fonction de récompense `r(x, y) = β · log(π_r(y|x) / π_ref(y|x))` (le terme de fonction de partition peut être abandonné dès que seules les différences comptent) qu'une policy définit mathématiquement, du simple fait d'être la policy qu'elle est, par rapport à une référence. Aucun reward model séparé n'a jamais été entraîné pour la produire ; elle découle directement de la même relation de policy optimale sur laquelle RLHF était déjà construit. Entraîner une policy à satisfaire directement des données de préférence humaines, en utilisant cette récompense implicite à la place d'une récompense entraînée séparément, c'est toute l'idée qui donne son nom à DPO.

## Pratique

1. ▢ Pourquoi dit-on que la fonction de partition `Z(x)` est intraitable à calculer directement ?

<details markdown="1"><summary>Vérifier</summary>

Parce que la calculer exactement exige de sommer sur toutes les complétions possibles `y` qu'un modèle de langage pourrait générer pour un prompt donné `x`, une somme sur un espace énorme qu'on ne peut pas évaluer directement.

</details>

2. ▢ Pourquoi `Z(x)` s'annule-t-il quand on calcule la différence `r(x, y_1) - r(x, y_2)` pour deux complétions d'un même prompt, mais ne s'annulerait-il pas si l'on avait besoin de la récompense d'une seule complétion prise isolément ?

<details markdown="1"><summary>Indice</summary>

Demandez-vous de quoi dépend réellement `Z(x)`, et si cette dépendance diffère entre `y_1` et `y_2`.

</details>

<details markdown="1"><summary>Vérifier</summary>

`Z(x)` ne dépend que du prompt `x`, pas de la complétion qu'on note, donc il apparaît comme exactement le même terme additif (`β · log Z(x)`) dans `r(x, y_1)` et dans `r(x, y_2)`. Soustraire l'un de l'autre le retire entièrement. Une récompense isolée porterait toujours ce même terme non retiré.

</details>

3. ▢ Que signifie « récompense implicite », au sens précis où cette leçon la dérive ?

<details markdown="1"><summary>Vérifier</summary>

La fonction de récompense `β · log(π(y|x) / π_ref(y|x))` que n'importe quelle policy définit mathématiquement, par rapport à une policy de référence figée, uniquement comme conséquence de la même relation de policy optimale qu'implique déjà l'objectif de RLHF. Elle n'est jamais entraînée comme modèle séparé ; elle découle directement de la policy et de la policy de référence elles-mêmes.

</details>

4. ▢ Laquelle de ces descriptions rend le mieux ce qu'accomplit la dérivation de DPO, par rapport à la nécessité d'estimer `Z(x)` directement ?

    - a) Elle trouve une méthode numérique plus rapide pour approcher `Z(x)`
    - b) Elle restructure le problème pour que `Z(x)` s'annule entièrement dès que seule une différence de deux récompenses est nécessaire, ce qui évite d'avoir à le calculer
    - c) Elle remplace `Z(x)` par une seconde fonction de partition plus simple
    - d) Elle montre que `Z(x)` vaut toujours 1 pour les modèles de langage

<details markdown="1"><summary>Vérifier</summary>

**b)** est exactement la dérivation que parcourt cette leçon. (a) et (c) supposent toutes deux que `Z(x)` doit encore être calculé ou approché sous une forme ou une autre, ce que la dérivation réelle évite de faire. (d) n'est pas une affirmation que la dérivation fait ni dont elle a besoin.

</details>

## Exercices en situation réelle

- [ ] Lisez la section de dérivation de l'article DPO (liée plus haut), de l'objectif sous contrainte KL jusqu'à l'annulation de la fonction de partition, et écrivez, avec vos propres mots, une phrase par équation nommant ce qui a changé entre elle et la précédente.
- [ ] Écrivez, symbole par symbole, ce que vaudrait `β · log(π(y|x) / π_ref(y|x))` si la policy et la policy de référence attribuaient exactement la même probabilité à `y`. Confirmez que cela correspond à votre intuition de ce à quoi devrait ressembler « aucun signal de préférence venant de cette complétion ».
- [ ] Demain : sans regarder la suite, écrivez une prédiction d'une phrase pour la leçon 10 : sachant que la récompense implicite est définie uniquement à partir de la policy et du modèle de référence, sans reward model ni fonction de partition dans le tableau, quelle boucle d'entraînement attendez-vous que DPO exige, par rapport à la boucle d'échantillonnage et d'optimisation de PPO ?

## Pour aller plus loin

- [Article : "Direct Preference Optimization: Your Language Model is Secretly a Reward Model", Rafailov et al., 2023](https://arxiv.org/abs/2305.18290)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
