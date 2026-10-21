---
title: "19. Quand DoRA gagne, et quand non"
description: "Prédire le gain avant de lancer le run"
type: lesson
---

# Leçon 19. Quand DoRA gagne, et quand non

**Lien avec la mission :** « Savoir prédire quand DoRA bat LoRA avant de lancer le run » est la barre de cette étape. De la prédiction, pas de l'expérience.
**Source primaire :** [Article : "DoRA: Weight-Decomposed Low-Rank Adaptation", Liu et al., arXiv:2402.09353](https://arxiv.org/abs/2402.09353)
**Prérequis :** [Leçon 18](0018-dora-magnitude-and-direction.md), [Leçon 17](0017-what-qlora-costs.md)

## Échauffement

1. ▢ Qu'est-ce que la renormalisation de DoRA empêche `BA` de faire ?

<details markdown="1"><summary>Vérifier</summary>

Changer la magnitude. Après renormalisation, `BA` n'affecte que la direction, et la magnitude vient du `m` entraîné séparément.

</details>

2. ▢ Pourquoi la norme par colonne ne peut-elle pas être mise en cache d'un pas à l'autre ?

<details markdown="1"><summary>Vérifier</summary>

C'est la norme de `W₀ + BA`, et `BA` change à chaque pas de l'optimizer.

</details>

3. ▢ Pourquoi une comparaison de qualité doit-elle utiliser plusieurs seeds ?

<details markdown="1"><summary>Vérifier</summary>

Parce que la variation d'une seed à l'autre dépasse fréquemment l'effet mesuré, donc une différence sur une seule seed ne peut pas être distinguée du bruit.

</details>

## À savoir

### Le schéma rapporté

Les gains de DoRA sur LoRA sont **les plus grands à bas rank et diminuent à mesure que le rank augmente.**

Le raisonnement découle directement du mécanisme. Aux rank 4 ou 8, la mise à jour de faible rang a très peu de capacité, et toute capacité dépensée à ajuster la magnitude est une capacité non dépensée sur la direction. DoRA confie la magnitude à un paramètre séparé, bon marché et dédié, libérant tout le budget de faible rang pour la direction. À rank 128, le budget n'est plus rare, donc en libérer un peu change moins de choses.

La règle de prédiction n'est donc pas « DoRA est meilleur » mais :

> **DoRA aide le plus exactement là où la capacité de LoRA est la plus serrée.**

### Quand s'attendre à un gain

| Situation | Attendre | Parce que |
|---|---|---|
| Rank très bas (4 à 16) | Gain significatif | La capacité est rare ; le découplage en libère un peu |
| Rank contraint à rester bas | Gain significatif | Même raison, et vous n'avez pas d'alternative |
| Rank moyen (32 à 64) | Gain plus faible | La capacité est moins rare |
| Rank élevé (128+) | Peu ou pas de gain | La capacité n'est pas la limite qui lie |
| Vous pourriez simplement augmenter le rank | Augmentez le rank | Moins cher en temps réel que le coût par pas de DoRA |
| Le temps par pas est votre contrainte | Passez DoRA | Vous payez des dizaines de pourcents pour un petit gain |

La cinquième ligne est celle qu'il faut intérioriser. Si le rank est une variable libre, **augmenter le rank est généralement un meilleur choix que passer à DoRA**, parce qu'un rank supplémentaire ne coûte presque aucune mémoire (leçon 7) et presque aucun temps, alors que DoRA coûte du vrai temps à chaque pas. DoRA gagne sa place quand le rank n'est *pas* libre, quand autre chose que la mémoire le retient vers le bas.

### Ce qui retient réellement le rank vers le bas

Il vaut la peine d'être concret, puisque toute la recommandation en dépend :

- **Surapprentissage sur un petit dataset.** Plus de rank signifie plus de mémorisation. Ici vous ne pouvez réellement pas augmenter le rank, et DoRA est une vraie option : vous tirez un meilleur parti d'un rank que vous maintenez délibérément petit.
- **Une contrainte de service sur la taille de l'adapter.** Rare, mais si vous distribuez des adapters ou en gardez beaucoup en mémoire à la fois, la taille peut lier.
- **Reproduire une configuration publiée.** Vous êtes cloué à leur rank.
- **Budget de temps d'entraînement total.** Notez que celui-ci joue *contre* DoRA plutôt que pour lui, parce que DoRA est plus lent par pas.

Si aucune de ces situations ne s'applique, le rank est libre, et l'action plus simple est disponible.

### Lire l'affirmation avec un œil critique

L'article DoRA rapporte des gains sur plusieurs tâches et familles de modèles, avec l'analyse magnitude-direction comme argument mécaniste. Cette analyse est réellement éclairante et la méthode est bien motivée.

Trois choses à garder à l'esprit :

**Les gains rapportés sont souvent petits en valeur absolue**, un point ou deux sur un benchmark. Comparez-les à votre bruit de seeds avant de les tenir pour réels sur votre tâche.

**La référence de comparaison compte.** DoRA au rank 8 contre LoRA au rank 8 est la comparaison de l'article et c'est la bonne pour isoler le mécanisme. DoRA au rank 8 contre LoRA au rank 32 est la comparaison à laquelle *vous* faites face quand vous décidez quoi lancer, et c'est une question différente avec peut-être une réponse différente.

**La réplication indépendante est plus mince que pour LoRA ou QLoRA.** LoRA a des années de preuves de praticiens sur d'innombrables tâches. DoRA en a moins. Ce n'est pas une critique de la méthode ; c'est une raison de mesurer sur votre propre tâche plutôt que d'importer une conclusion.

### La procédure de décision

1. Le rank est-il libre d'être augmenté ? → Augmentez-le. N'utilisez pas DoRA.
2. Le rank est-il maintenu bas, et par quoi ? → Si c'est par le risque de surapprentissage ou une contrainte dure, DoRA est un vrai candidat.
3. Le temps par pas est-il déjà la contrainte qui lie ? → N'utilisez pas DoRA.
4. Sinon : lancez les deux, avec le même ensemble de seeds, tout le reste identique, et comparez au bruit des seeds.

L'étape 4 n'est pas un échec de la procédure. Être capable de dire « l'effet attendu ici est petit et j'ai besoin de le mesurer » *est* la réponse de senior, et c'est une bien meilleure position que de croire l'article sans esprit critique ou de le rejeter.

## Pratique

1. ▢ Pourquoi les gains de DoRA diminuent-ils quand le rank augmente ?

<details markdown="1"><summary>Vérifier</summary>

Son bénéfice est de libérer la capacité de faible rang de l'obligation de représenter des changements de magnitude. Quand le rank est rare, cette capacité libérée compte proportionnellement beaucoup ; quand le rank est généreux, la capacité n'était pas le facteur limitant, donc en libérer un peu change peu de choses.

</details>

2. ▢ Vous êtes au rank 8 et pouvez augmenter le rank librement. DoRA ou plus de rank ?

<details markdown="1"><summary>Vérifier</summary>

Plus de rank. Cela ne coûte presque aucune mémoire et presque aucun temps, alors que DoRA coûte une pénalité par pas à chaque pas de chaque run futur.

Recourez à DoRA quand le rank est cloué par quelque chose, généralement un risque de surapprentissage sur un petit dataset, et pas quand c'est une variable libre.

</details>

3. ▢ 600 exemples d'entraînement, rank maintenu à 8 pour limiter la mémorisation. DoRA vaut-il la peine d'être essayé ?

<details markdown="1"><summary>Vérifier</summary>

Oui. C'est le cas auquel la méthode convient le mieux : le rank est délibérément bas pour une raison que vous ne pouvez pas lever, donc en tirer un meilleur parti est la seule amélioration disponible.

Mesurez-le face à LoRA au même rank avec plusieurs seeds, puisque l'effet attendu est petit.

</details>

4. ▢ Distinguez la comparaison de l'article de la vôtre.

<details markdown="1"><summary>Vérifier</summary>

L'article compare DoRA et LoRA à rank égal, ce qui isole correctement le mécanisme.

Votre décision se fait entre DoRA au rank que vous pouvez vous permettre et LoRA au rank que vous pouvez vous permettre, et comme LoRA est plus rapide par pas, vous pouvez peut-être vous offrir plus de rank avec lui. Mêmes chiffres, question différente.

</details>

5. ▢ Qu'est-ce qui prédit le plus fiablement un gain de DoRA ?

    - a) Un grand dataset d'entraînement avec de nombreux exemples variés
    - b) Un rank bas qui ne peut pas être augmenté pour d'autres raisons
    - c) Un base model quantifié en précision NF4 quatre bits
    - d) Un ensemble de target modules couvrant toutes les couches linéaires

<details markdown="1"><summary>Vérifier</summary>

**b)** Un rank bas qui ne peut pas être augmenté pour d'autres raisons.

La taille du dataset, la précision du base model et la couverture des target modules sont toutes orthogonales au mécanisme. La rareté de la capacité de faible rang est ce que DoRA soulage.

</details>

6. ▢ Votre gain mesuré de DoRA est de 0.6 point, avec une dispersion sur les seeds de 1.4 point. Que concluez-vous et que faites-vous ?

<details markdown="1"><summary>Vérifier</summary>

Que vous n'avez pas détecté d'effet. La différence est bien à l'intérieur du bruit.

Soit vous lancez assez de seeds pour résoudre une différence aussi petite, ce qui peut être beaucoup, soit vous acceptez que l'effet est trop petit pour compter ici et prenez la méthode la plus rapide. Décider que cela ne vaut pas la peine d'être résolu est un résultat légitime et souvent correct.

</details>

## Exercices en situation réelle

- [ ] Exécutez LoRA et DoRA au rank 8, trois seeds chacun, tout le reste fixé. Comparez la différence à la dispersion sur les seeds.
- [ ] Exécutez LoRA au rank 32 avec le même budget de temps réel que DoRA au rank 8. Notez lequel a produit le meilleur modèle par unité de temps.
- [ ] Demain : écrivez, avant de rien lancer, votre prédiction sur le fait que DoRA aidera ou non sur votre tâche réelle, et pourquoi. Gardez-la et vérifiez-la plus tard.

## Pour aller plus loin

- [Article : "DoRA: Weight-Decomposed Low-Rank Adaptation", Liu et al., arXiv:2402.09353](https://arxiv.org/abs/2402.09353)
- [Hyperparamètres de LoRA](../reference/lora-hyperparameters.md)
- [Leçon 20. Juger une nouvelle variante de PEFT](0020-judging-a-new-variant.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
