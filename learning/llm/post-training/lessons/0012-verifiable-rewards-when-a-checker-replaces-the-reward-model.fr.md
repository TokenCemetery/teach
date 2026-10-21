---
title: "12. Récompenses vérifiables : quand un vérificateur remplace le reward model"
description: "Un reward model entraîné est un pari sur ce qu'un humain préférerait ; un test unitaire ou une réponse qui correspond n'est pas un pari du tout"
type: lesson
---

# Leçon 12. Récompenses vérifiables : quand un vérificateur remplace le reward model

**Lien avec la mission :** « Expliquer l'avantage relatif au groupe dans GRPO et pourquoi une récompense vérifiable (un test unitaire, une réponse mathématique vérifiée) change ce que l'entraînement par RL peut viser » est la cinquième puce sous « Objectif », et cette leçon la conclut.
**Source primaire :** [Article : "DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models", Shao et al., 2024](https://arxiv.org/abs/2402.03300)
**Prérequis :** [Leçon 11](0011-grpo-group-relative-advantage-instead-of-a-value-function.md), [Récompense vérifiable](../GLOSSARY.md)

## Échauffement

1. ▢ Un groupe de 4 sorties échantillonnées pour la même question reçoit les récompenses `{2, 4, 6, 8}`. Quelles sorties reçoivent un avantage relatif au groupe positif, et lesquelles un avantage négatif ?

<details markdown="1"><summary>Vérifier</summary>

La moyenne est 5 ; les sorties qui ont scoré 6 et 8 sont au-dessus et reçoivent un avantage positif, celles qui ont scoré 2 et 4 sont en dessous et reçoivent un avantage négatif.

</details>

2. ▢ Pourquoi Shao et al. décrivent-ils la comparaison relative au groupe comme particulièrement adaptée aux reward models ?

<details markdown="1"><summary>Vérifier</summary>

Les reward models sont typiquement entraînés dès le départ sur des comparaisons entre des sorties à la même question, si bien que noter plusieurs sorties à une même question et les comparer entre elles demande au reward model de faire le même type de jugement relatif que celui qu'il a réellement été entraîné à faire.

</details>

## À savoir

### Ce dont GRPO a réellement besoin comme récompense

Rien dans l'avantage relatif au groupe de la leçon 11 n'exige que le score de chaque sortie échantillonnée vienne spécifiquement d'un reward model entraîné. Tout ce dont la formule de normalisation par groupe, `A_i = (r_i - mean(r)) / std(r)`, a besoin, c'est d'un nombre par sortie échantillonnée, `r_1` à `r_G`, qui reflète la qualité de chacune. Un reward model entraîné est une manière de produire ce nombre, celle qu'emploie l'entraînement GRPO de Shao et al. eux-mêmes. Ce n'est pas la seule.

### Ce qu'est une récompense vérifiable

Une **récompense vérifiable** est un signal de récompense produit par un vérificateur déterministe plutôt que par un modèle appris : un morceau de code généré passe-t-il un test unitaire fixe, la réponse numérique finale d'un problème de maths correspond-elle exactement à la réponse correcte connue, une preuve ou un programme généré satisfait-il une vérification formelle. Calculer une récompense vérifiable n'implique en rien de deviner ce qu'un humain aurait préféré ; c'est un fait direct et vérifiable sur la sortie, calculé de la même façon à chaque fois, sans aucun modèle de préférence entre la sortie et son score.

### Pourquoi cela change ce que l'entraînement par RL peut viser

Un reward model entraîné, aussi bien entraîné soit-il, ajuste toujours un jugement de préférence : la leçon 5 a couvert directement la façon dont une policy peut trouver des moyens de scorer bien contre lui sans produire réellement le comportement qu'il devait récompenser. Une récompense vérifiable n'a pas de mode d'échec analogue de cette forme : un test unitaire passe ou ne passe pas, et il n'y a aucun travers propre à un reward model qu'une policy pourrait apprendre à exploiter, parce qu'aucun modèle appris ne tient lieu de jugement. Cela ouvre l'entraînement par RL à des cibles auparavant difficiles à atteindre par la seule préférence humaine : on peut pousser une policy, groupe échantillonné après groupe échantillonné, vers des sorties plus souvent exactes, de façon vérifiable, sur des tâches comme les mathématiques et le code, plutôt que simplement plus souvent préférées par un juge (humain ou modèle) qui porte un jugement subjectif.

### Ce que cela ne change pas

Une récompense vérifiable n'est pas une amélioration gratuite par rapport à un reward model entraîné à tous égards ; elle ne s'applique que là où une vérification de la justesse existe réellement. Une bonne part du comportement que le post-training doit façonner (l'utilité, le ton, la sécurité, la qualité d'écriture ouverte) n'a aucun vérificateur déterministe qui pourrait remplacer un jugement de préférence humain ou de modèle ; il n'y a pas de test unitaire pour « cette réponse était d'une empathie appropriée ». Les récompenses vérifiables conviennent précisément aux tâches où la justesse est vérifiable dès le départ, ce qui explique que les maths et le code soient les domaines autour desquels cette combinaison est construite, et non un remplacement général de la modélisation de récompense fondée sur la préférence partout ailleurs.

## Pratique

1. ▢ Une équipe veut entraîner une policy à résoudre des problèmes d'algèbre en langage naturel avec GRPO. Au lieu d'entraîner un reward model sur des préférences humaines entre des solutions, que pourrait-elle utiliser à la place, et pourquoi cela éviterait-il le risque de reward hacking que décrivait la leçon 5 ?

<details markdown="1"><summary>Vérifier</summary>

Une récompense vérifiable : vérifier si la réponse numérique finale de la policy correspond exactement à la réponse correcte connue. Cela évite le reward hacking au sens du reward model parce qu'il n'y a pas de travers d'un modèle appris à exploiter ; la vérification est un fait direct et déterministe sur la sortie, et non un jugement entraîné qu'une policy pourrait apprendre à détourner.

</details>

2. ▢ Pourquoi une récompense vérifiable conviendrait-elle mal pour entraîner une policy à écrire des réponses de support client plus empathiques ?

    - a) Les récompenses vérifiables ne peuvent être calculées que pour des sorties numériques
    - b) Il n'existe aucun vérificateur déterministe pour « cette réponse était d'une empathie appropriée » ; la justesse de ce type n'est pas une propriété qu'un vérificateur peut tester
    - c) Les récompenses vérifiables exigent toujours un reward model séparé pour les interpréter
    - d) GRPO ne peut pas du tout être utilisé avec des récompenses vérifiables

<details markdown="1"><summary>Vérifier</summary>

**b)** est la vraie limite : les récompenses vérifiables conviennent aux tâches où la justesse est vérifiable dès le départ, et le ton empathique n'a pas de telle vérification déterministe. (a) est trop étroit ; la justesse d'un code est un exemple non numérique qui se vérifie pourtant. (c) contredit tout l'intérêt d'une récompense vérifiable, qui n'a besoin d'aucun reward model. (d) est faux ; la mécanique de normalisation par groupe de GRPO fonctionne avec n'importe quel score par sortie, vérifiable ou produit par un modèle.

</details>

3. ▢ Utiliser une récompense vérifiable change-t-il quoi que ce soit à la façon dont l'avantage relatif au groupe de la leçon 11 est calculé ?

<details markdown="1"><summary>Vérifier</summary>

Non. La même normalisation, qui soustrait la moyenne du groupe et divise par son écart-type, s'applique que le score sous-jacent par sortie, `r_i`, vienne d'un reward model entraîné ou d'un vérificateur déterministe. Seule change la provenance de ce score, pas ce que GRPO en fait.

</details>

## Exercices en situation réelle

- [ ] Trouvez un montage publié d'entraînement RL pour le raisonnement (un article, un rapport technique ou un script d'entraînement ouvert) et identifiez exactement ce que vérifie sa récompense vérifiable : une réponse en correspondance exacte, une suite de tests unitaires, un vérificateur de preuves formelles, ou autre chose.
- [ ] Choisissez une tâche que vous jugez plausible pour des récompenses vérifiables (une tâche de code, un jeu de problèmes de maths) et une tâche que vous jugez peu plausible (une tâche d'écriture ouverte ou de conversation), et écrivez une phrase pour chacune expliquant ce qu'un vérificateur déterministe pourrait ou ne pourrait pas tester.
- [ ] Demain : sans regarder la suite, écrivez une prédiction d'une phrase pour l'étape 7 : si les récompenses vérifiables permettent à l'entraînement par RL de pousser une policy à être plus souvent exactement correcte, quel type de nouveau comportement du modèle attendriez-vous de voir émerger d'un entraînement intensif sur des problèmes de maths et de code de cette façon, au-delà du simple fait d'obtenir plus de bonnes réponses ?

## Pour aller plus loin

- [Article : "DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models", Shao et al., 2024](https://arxiv.org/abs/2402.03300)
- [Ressources](../RESOURCES.md)

---

L'étape 6 a couvert le mécanisme (l'avantage relatif au groupe) et la récompense qui s'y associe particulièrement bien (les vérifications vérifiables). L'étape 7 couvre ce qui se passe quand cette combinaison est portée à l'échelle comme principale façon d'entraîner un modèle : les modèles de raisonnement, et ce que produit réellement un entraînement à grande échelle sur des récompenses vérifiables.

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
