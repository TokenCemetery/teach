---
title: "22. Élève contre enseignant"
description: "Mesurer l'accord avec l'enseignant séparément de la qualité sur la tâche, une capacité à la fois"
type: lesson
---

# Leçon 22. Élève contre enseignant

**Lien avec la mission :** La mission vous demande de mesurer ce qu'un élève a perdu par rapport à son enseignant, et la première étape est de cesser de traiter « est d'accord avec l'enseignant » et « fait bien la tâche » comme un seul nombre.
**Source primaire :** [Article : "Does Knowledge Distillation Really Work?", Stanton et al., 2021](https://arxiv.org/abs/2106.05945), sections 3.2 et 4 à 5
**Prérequis :** [Leçon 17](0017-fidelity-and-generalization.md), [Leçon 18](0018-the-imitation-gap.md), [Fidélité](../GLOSSARY.md), [Accord top-1](../GLOSSARY.md), [Écart d'imitation](../GLOSSARY.md)

## Échauffement

1. ▢ La leçon 17 a dit qu'un élève qui généralise bien peut quand même être en désaccord avec son enseignant. Lequel des deux la leçon a-t-elle dit qu'il vous faut, et qu'est-ce qui le décide ?

<details markdown="1"><summary>Vérifier</summary>

Cela dépend de ce à quoi sert l'élève. Si vous avez besoin que le comportement de l'enseignant soit reproduit, comme dans un remplacement dont d'autres dépendent, la fidélité est le but. Si vous avez besoin d'un modèle qui fait bien la tâche, c'est la qualité sur la tâche, et un élève peut battre un enseignant défaillant en étant en désaccord avec lui. Aucun des deux ne tient lieu de l'autre.

</details>

2. ▢ La leçon 18 a donné l'écart d'imitation. Que copie le plus vite un élève, et que récompense une évaluation de préférence humaine ?

<details markdown="1"><summary>Vérifier</summary>

Il copie le style le plus vite : des réponses fluides, assurées, bien structurées. Une évaluation de préférence récompense la manière dont une réponse se lit, si bien qu'un élève peut bien y réussir tout en étant à la traîne sur la capacité. La capacité est plus lente à copier.

</details>

3. ▢ La leçon 21 a chiffré la passe de notation d'un enseignant. Quelle grandeur par token de cette passe vous faudrait-il aussi pour mesurer la fidélité, et quel coût supplémentaire son usage ajoute-t-il ?

<details markdown="1"><summary>Vérifier</summary>

La distribution de sortie de l'enseignant (ou son premier choix) à chaque position, que la passe de notation produit déjà. Mesurer la fidélité signifie exécuter aussi l'enseignant sur les prompts d'évaluation, un petit coût supplémentaire face à l'entraînement, parce que le jeu d'évaluation est bien plus petit que le jeu d'entraînement.

</details>

## À savoir

### Deux choses à mesurer

La [fidélité](../GLOSSARY.md) est la manière dont les prédictions d'un élève suivent de près celles de son enseignant sur les mêmes entrées. La qualité sur la tâche est la manière dont l'élève fait le travail, jugée par rapport à la bonne réponse. Stanton et al. définissent deux métriques de fidélité (section 3.2), et les deux se transposent à un modèle de langage position par position :

- **[Accord top-1](../GLOSSARY.md) :** la part des entrées sur lesquelles la réponse de plus haute probabilité de l'élève est la réponse de plus haute probabilité de l'enseignant.
- **KL prédictive moyenne :** la divergence KL moyenne de la distribution de l'enseignant vers celle de l'élève, sensible à chaque réponse, pas seulement à la première.

L'article définit les deux pour des classifieurs. Les appliquer à un LLM signifie noter les distributions du token suivant des deux modèles sur les mêmes préfixes de prompts held-out, ce qui est l'adaptation de ce parcours et non quelque chose que l'article a mené. Décidez d'emblée quel préfixe vous utilisez : le texte de l'enseignant, qui isole la prédiction, ou la génération propre de chaque modèle, qui mesure aussi comment les deux divergent une fois qu'ils ont choisi des mots différents.

### Pourquoi ils se dissocient

Stanton et al. donnent trois résultats qui expliquent pourquoi l'accord d'un élève et sa qualité sur la tâche peuvent évoluer indépendamment.

D'abord, l'accord est borné par la précision. Leur exemple (section 3.2) : deux modèles indépendants à 55 pour cent et 95 pour cent peuvent s'accorder sur au plus 60 pour cent des points. Un accord mesuré de 60 pour cent entre ces deux-là ne dit rien de la distillation. Ils ajoutent un contrôle pour exactement cette raison : mesurer aussi un élève distillé de la même façon à partir d'un enseignant indépendant, et comparer les deux accords. Si les deux élèves s'accordent à peu près autant avec l'enseignant, l'accord vient du fait que les deux généralisent bien, pas de la distillation.

Ensuite, un élève peut battre son enseignant en échouant à le copier. En auto-distillation sur CIFAR-100, où l'élève a l'architecture de l'enseignant, la précision de l'élève peut dépasser celle de l'enseignant, ce que l'article note n'être possible que parce que la distillation échoue : une copie parfaite ne pourrait pas faire mieux (sections 4.1 et 4.2). Dans cette expérience, augmenter la fidélité a baissé la précision de l'élève quand le jeu de distillation était petit.

Enfin, une fidélité plus haute n'achète pas toujours une précision plus haute même quand l'enseignant est bien meilleur. À la section 5, ils découpent CIFAR-100, distillent un élève sur la moitié d'entraînement propre de l'enseignant (s0) et un sur des données non vues (s1). L'élève sur données non vues s'accorde davantage avec l'enseignant, et pourtant l'élève sur les données de l'enseignant a la plus haute précision au test. Le résumé de l'article est que le gain de fidélité ne s'est pas traduit par la reproduction de la précision de l'enseignant.

Ils rapportent aussi qu'il est difficile d'atteindre une haute fidélité tout court. Sur MNIST avec LeNet-5, l'élève a atteint plus de 99 pour cent d'accord top-1 au test (section 4.1). Sur CIFAR-100 avec des élèves ResNet-56, le meilleur accord au test qu'ils rapportent est d'environ 86 pour cent, avec l'augmentation mixup (section 5).

Portée : ce sont surtout des expériences de classification d'images, avec des classifieurs de texte en annexe. Elles montrent que les deux grandeurs sont séparables. Ce ne sont pas des mesures d'un LLM, et aucun chiffre d'accord qui en vient n'est une cible pour le vôtre.

### Pourquoi une évaluation de préférence est le mauvais substitut

Gudibande et al. ont fait le fine-tuning de modèles LLaMA de 7B et 13B de paramètres sur des sorties de ChatGPT et comparé deux types d'évaluation. Des travailleurs de la foule ont jugé environ 70 pour cent des sorties des modèles d'imitation égales ou meilleures que celles de ChatGPT (leur figure 1). Sur des benchmarks ciblés, les modèles d'imitation ont comblé peu ou pas de l'écart entre le base model et ChatGPT pour les tâches que les données d'imitation ne couvraient pas beaucoup.

Leur tableau 1 le montre par capacité, avec Natural Questions comme tâche :

| Modèle | Données d'imitation | Score NQ |
|---|---|---|
| LLaMA 7B | aucune | 17 |
| LLaMA 7B | ShareGPT-Mix (large) | 10 |
| LLaMA 7B | NQ-Synthetic (ciblée) | 22 |
| LLaMA 13B | aucune | 20 |
| LLaMA 13B | ShareGPT-Mix (large) | 15 |
| LLaMA 13B | NQ-Synthetic (ciblée) | 27 |
| ChatGPT | non applicable | 31 |

Les données d'imitation larges ont baissé le score NQ des deux tailles, et les données ciblées l'ont relevé à moins de quatre points de l'enseignant pour 13B. L'explication de l'article pour l'écart d'évaluation est le style : les modèles d'imitation sont fluides et assurés, et un évaluateur sans expertise du domaine ni temps pour vérifier les faits manque les erreurs. Ils ont aussi constaté, dans leur tableau 2, que le style des sorties se rapprochait de celui de ChatGPT à mesure que des données d'imitation étaient ajoutées, ce qui est le même effet mesuré sur le texte de sortie.

La leçon pour la mesure n'est pas que les évaluations de préférence sont inutiles. C'est qu'un seul agrégat, qu'il s'agisse d'une évaluation ou d'une précision moyenne, cache les capacités qui ont évolué dans des directions opposées.

### Une capacité à la fois

La mesure est donc une grille. Choisissez les capacités qui vous importent, comme les réponses factuelles courtes, l'arithmétique, le code, le suivi d'instructions et les refus. Pour chacune, calculez deux colonnes : l'accord avec l'enseignant sur des prompts de ce genre, et la qualité sur la tâche par rapport à la bonne réponse sur les mêmes prompts. Un élève peut paraître haut sur la première et bas sur la seconde pour certaines lignes et l'inverse pour d'autres, et c'est le motif qui vous dit ce qui a été transféré et ce qui ne l'a pas été.

| Capacité | Accord avec l'enseignant | Qualité sur la tâche, élève | Qualité sur la tâche, enseignant | Lecture |
|---|---|---|---|---|
| Ligne hypothétique A | Haut | Proche de l'enseignant | Haute | Bien copiée |
| Ligne hypothétique B | Haut | Bien en dessous de l'enseignant | Haute | Style copié, capacité perdue |
| Ligne hypothétique C | Bas | Au-dessus de l'enseignant | Modérée | En désaccord, et l'enseignant était le plus faible |

Les lignes illustrent la façon de lire la grille, ce ne sont pas des données d'une source. La leçon 23 ajoute la colonne manquante, un modèle de même taille entraîné sans distillation, que cette grille ne peut pas juger seule.

## Pratique

1. ▢ Un enseignant obtient 90 pour cent de précision sur une tâche. Un modèle indépendant obtient 70 pour cent. Quel est l'accord top-1 le plus élevé que les deux puissent avoir, et qu'est-ce que cela implique pour la lecture du score d'accord d'un élève ?

<details markdown="1"><summary>Indice</summary>

Deux modèles ne peuvent s'accorder sur un point que s'ils ont tous deux raison ou tous deux tort. Déterminez le plus grand recouvrement que permettent les précisions, en suivant l'exemple 55 et 95 de l'article.

</details>

<details markdown="1"><summary>Vérifier</summary>

Au plus 80 pour cent, puisque l'écart de précision de 20 points les force à être en désaccord sur au moins 20 pour cent des points. Un élève dont la précision est de 70 pour cent ne peut donc pas montrer un accord supérieur à 80 pour cent avec cet enseignant, et un accord de 75 pour cent signifie autre chose que le même chiffre pour un élève à 88 pour cent. Comparez l'accord d'un élève à celui d'un élève indépendant du contrôle de l'article avant de tirer des conclusions.

</details>

2. ▢ Un élève a 94 pour cent d'accord top-1 avec son enseignant sur des prompts de chat généraux et 61 pour cent sur des prompts d'arithmétique à plusieurs étapes. La précision de l'enseignant en arithmétique est de 78 pour cent. Que mesurez-vous ensuite avant de dire quoi que ce soit de l'arithmétique de l'élève ?

<details markdown="1"><summary>Indice</summary>

Le nombre d'accord dit à quelle fréquence les deux coïncident, pas à quelle fréquence l'un ou l'autre a raison.

</details>

<details markdown="1"><summary>Vérifier</summary>

La précision de l'élève en arithmétique par rapport aux bonnes réponses, sur les mêmes prompts, plus la justesse par prompt de l'enseignant. Si la précision de l'élève est de 61 pour cent et celle de l'enseignant de 78 pour cent, l'écart est une perte de capacité. Si les deux sont en désaccord surtout là où l'enseignant a tort, l'élève peut très bien aller. Les 94 pour cent sur le chat disent seulement que le style s'est transféré, ce que prédit l'écart d'imitation.

</details>

3. ▢ Quel résultat montre le plus directement que la fidélité et la qualité sur la tâche peuvent se séparer ?

    - a) L'accord d'un élève avec son enseignant a baissé quand une forte augmentation a été appliquée à ses entrées.
    - b) Un élève entraîné sur davantage de données de distillation a atteint un accord au test plus élevé avec son enseignant.
    - c) Un élève ayant l'architecture de l'enseignant a atteint la précision de l'enseignant à une certaine taille de données.
    - d) Un élève distillé à partir de données non vues s'accordait davantage avec son enseignant mais était moins précis.

<details markdown="1"><summary>Vérifier</summary>

d). C'est le résultat s1 contre s0 de la section 5 : fidélité plus haute avec précision au test plus basse. b) montre la fidélité qui monte avec les données, ce qui est attendu et ne sépare pas les deux. c) est une affirmation sur la seule précision. a) est un résultat sur la baisse de l'accord sous augmentation, qui rapporte un changement de fidélité sans comparaison de qualité sur la tâche.

</details>

4. ▢ Une fiche de modèle dit qu'un modèle distillé de 3B « est jugé presque aussi bon que le 70B par des évaluateurs humains ». En vous appuyant sur Gudibande et al., listez deux questions de suivi que vous poseriez avant d'accepter que l'élève a gardé les capacités du 70B.

<details markdown="1"><summary>Vérifier</summary>

Quels prompts les évaluateurs ont vus, et si l'un d'eux pouvait vérifier les faits ou le code, puisque le style peut gagner une évaluation que la capacité ne gagnerait pas. Et ce que l'élève obtient sur des benchmarks ciblés par capacité par rapport à l'enseignant et au modèle de base non distillé, y compris sur des tâches que les données de distillation couvraient à peine. Une évaluation qui s'accorde avec les benchmarks est une preuve. Une évaluation seule n'en est pas une.

</details>

5. ▢ La leçon 19 a couvert la capacité. Un élève reproduit la réponse top-1 de son enseignant sur 97 pour cent des prompts faciles et 52 pour cent des difficiles. Nommez une lecture qui correspond à l'écart de capacité et une qui n'en a pas besoin.

<details markdown="1"><summary>Vérifier</summary>

Correspond : l'élève n'a pas la capacité de modéliser le comportement de l'enseignant sur des entrées difficiles, donc l'écart se concentre là où l'enseignant fait le plus de travail. N'en a pas besoin : les prompts difficiles sont peu nombreux dans les données de distillation, donc l'élève y a vu peu de signal, et plus de données sur eux aideraient. Les deux prédisent des correctifs différents, testez donc en ajoutant des données de prompts difficiles à une copie du run et en mesurant à nouveau.

</details>

## Exercices en situation réelle

- [ ] Choisissez deux petits modèles ouverts qui partagent un tokenizer. Sur 50 prompts, enregistrez le premier choix du token suivant de chaque modèle à une position choisie par prompt et comptez à quelle fréquence ils coïncident.
- [ ] Ouvrez l'article de Gudibande et al. et trouvez le tableau 1. Écrivez une phrase sur ce que disent les lignes à large couverture quant à la lecture d'un score moyen.
- [ ] Demain : sans notes, dessinez la grille des capacités de cette leçon pour un projet à vous, avec les deux colonnes, et nommez la capacité où vous attendez que l'accord et la qualité diffèrent le plus.

## Pour aller plus loin

- [Dimensionner et mesurer](../reference/sizing-and-measuring.md)
- [Article : "Does Knowledge Distillation Really Work?", Stanton et al., 2021](https://arxiv.org/abs/2106.05945), sections 3.2 et 5
- [Article : "The False Promise of Imitating Proprietary LLMs", Gudibande et al., 2023](https://arxiv.org/abs/2305.15717), sections 4.2 et 4.4
- [Evals](../../evals/) : le parcours pour construire le côté qualité sur la tâche de cette grille
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
