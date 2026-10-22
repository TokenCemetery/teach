---
title: "24. Relire la configuration d'entraînement de quelqu'un d'autre"
description: "Passer le plan au crible de chaque étape que ce parcours a couverte, dans l'ordre, et trancher une affirmation contestée à partir de la source plutôt que d'un article de blog"
type: lesson
---

# Leçon 24. Relire la configuration d'entraînement de quelqu'un d'autre

**Lien avec la mission :** Cette leçon clôt le fil conducteur. Chaque étape antérieure a produit une chose à vérifier dans le plan de quelqu'un d'autre ; cette leçon est la liste de contrôle, plus la discipline qui consiste à trancher une affirmation technique contestée à partir d'une source primaire plutôt que de faire confiance à la source secondaire la plus commode.
**Source primaire :** [Article : "Training Compute-Optimal Large Language Models", Hoffmann et al., 2022](https://arxiv.org/abs/2203.15556)
**Prérequis :** toutes les leçons précédentes de ce parcours, puisque celle-ci est la synthèse.

## Échauffement

1. ▢ Nommez les quatre catégories d'affirmations en lesquelles la leçon 23 dit qu'un plan de pré-entraînement défendable devrait être découpé.

<details markdown="1"><summary>Vérifier</summary>

Le ratio tokens par paramètre, le pipeline de données, le plan de parallélisme adapté à l'interconnexion du matériel, et le plan de stabilité et de surveillance.

</details>

2. ▢ D'après la leçon 22, nommez une raison légitime de pré-entraîner à partir de zéro plutôt que d'adapter un modèle existant.

<details markdown="1"><summary>Vérifier</summary>

N'importe laquelle : la langue ou le domaine cible est si éloigné de la couverture de tout modèle de base disponible que l'adaptation ne peut pas combler l'écart, une exigence de licence ou de provenance écarte tous les modèles de base disponibles, ou un changement d'architecture délibéré dans lequel un checkpoint existant ne peut pas être adapté.

</details>

## À savoir

### La liste de contrôle de relecture : les étapes dans l'ordre

Quand on relit un plan de pré-entraînement proposé ou existant, on le passe au crible des étapes de ce parcours dans l'ordre, en posant à chacune la même question : ce choix est-il énoncé et justifié, ou simplement présumé ?

**Étapes 1 et 2, données et tokenizer.** Le sourcing et le mélange du corpus sont-ils une décision explicite et défendue (leçon 1), avec une déduplication et un filtrage de qualité réellement appliqués et décrits (leçon 2), plutôt que « tout ce qu'on a pu scraper » ? La taille de vocabulaire du tokenizer est-elle un choix énoncé, mis en balance avec la longueur des séquences et le coût de la table d'embeddings (leçon 4), plutôt qu'une valeur par défaut reprise d'un projet sans rapport ?

**Étape 3, le ratio.** Calculez directement le ratio tokens par paramètre du plan et comparez-le à la plage d'environ 20 à 25 que la leçon 6 a fondée sur les propres résultats de Chinchilla. Un plan bien en dehors de cette plage, dans un sens ou dans l'autre, n'est pas automatiquement faux, mais c'est une affirmation qui a besoin de sa propre raison énoncée, le même test qu'appliquait la leçon 23.

**Étapes 4 à 6, parallélisme.** La stratégie de partitionnement (stage ZeRO, ou équivalent) correspond-elle à la mémoire réelle dont le modèle a besoin, d'après le décompte par paramètre de la leçon 8 ? Un éventuel découpage en parallélisme tensoriel reste-t-il dans l'interconnexion rapide d'un seul nœud, et le parallélisme de pipeline porte-t-il la charge de la traversée des nœuds, d'après le raisonnement de la leçon 14, plutôt que l'inverse ?

**Étapes 7 à 9, l'exécuter.** Le plan énonce-t-il un choix de précision et, si l'on utilise des paramètres bf16, indique-t-il si l'on emploie l'arrondi stochastique ou une copie maître fp32 (leçon 15) ? Énonce-t-il une valeur de gradient clipping, et cette valeur se resserre-t-elle pour les plus grands modèles que le plan entraîne, comme l'a fait celle de Gopher (leçon 16) ? Énonce-t-il une fréquence de checkpoint défendable face au taux de panne que la preuve de l'étape 8 a montré normal, et non exceptionnel, à cette échelle (leçon 18) ? Inclut-il une évaluation held-out périodique, et pas seulement la loss d'entraînement, pour attraper tôt les problèmes (leçon 21) ?

**Étape 10, la décision elle-même.** Le plan explique-t-il pourquoi un pré-entraînement continu ou le fine-tuning d'un modèle existant n'aurait pas servi l'objectif énoncé (leçon 22), avant de défendre le budget à partir de zéro selon ses propres termes (leçon 23) ?

Un plan qui répond à tout cela par un choix énoncé et défendable est un plan qui a fait le travail que décrit ce parcours. Un plan qui répond à plusieurs de ces questions par le silence ne l'a pas fait, quelle que soit l'allure de son estimation de coût final.

### Trancher une affirmation contestée à partir de la source, pas d'un article de blog

Une confusion précise et courante mérite d'être parcourue directement, parce qu'elle montre la discipline dont parle réellement cette leçon. On prétend parfois en ligne que « le bf16 exige du loss scaling, comme le fp16 ». C'est énoncé avec assurance dans assez de sources secondaires pour que cela paraisse réglé. Mais la leçon 15 a retracé pourquoi le bf16 garde les 8 bits d'exposant complets du fp32, ce qui lui donne la même plage dynamique que le fp32 ; le loss scaling (multiplier les valeurs vers le haut avant de les stocker dans un format à plage étroite, puis les redescendre avant la mise à jour, pour éviter l'underflow) est précisément une mitigation de la plage d'exposant plus étroite de 5 bits du fp16, le problème exact que la plage plus large du bf16 a été conçue pour éviter en premier lieu. Le récit de Rae et al. sur l'entraînement de Gopher ne décrit pas du tout de loss scaling pour leurs activations bf16 ; la préoccupation numérique qu'ils décrivent et traitent pour le bf16 est l'arrondi stochastique pour les mises à jour de paramètres, un problème différent (de précision, non de plage) avec une solution différente. Une source secondaire qui répète « le bf16 a aussi besoin de loss scaling » confond deux problèmes différents de deux formats différents ; revenir à ce qu'une source primaire décrit réellement comme besoin de chaque format, plutôt que de faire confiance à une reformulation assurée, est ce qui attrape cette confusion. C'est l'habitude qui vaut la peine d'être emportée de ce parcours : quand deux récits divergent, ou qu'un récit affirme quelque chose de suspectement proche de ce qu'une leçon antérieure a retracé sans y correspondre tout à fait, c'est la source primaire qui tranche, et non le récit lu en premier ou celui qui avait l'air le plus sûr de lui.

## Pratique

1. ▢ Un plan d'entraînement propose un modèle de 50 milliards de paramètres entraîné sur 400 milliards de tokens, avec ZeRO stage 2 sur 16 appareils répartis en 2 nœuds de 8, et un parallélisme tensoriel de taille 16 (couvrant les deux nœuds). Nommez deux éléments de ce plan qui méritent d'être contestés, à l'aide de la liste de contrôle de cette leçon.

<details markdown="1"><summary>Vérifier</summary>

Le ratio (`400 / 50 = 8` tokens par paramètre) est bien en dessous de la plage compute-optimal d'environ 20 à 25, et il vaut la peine de demander si c'est un choix délibéré et justifié. La taille de parallélisme tensoriel de 16, couvrant les deux nœuds au lieu de rester dans un seul nœud de 8 GPU, contredit le raisonnement de la leçon 14 selon lequel l'all-reduce fréquent du parallélisme tensoriel relève de l'interconnexion rapide d'un seul nœud, le découpage entre nœuds étant porté plutôt par le parallélisme de pipeline (et non par le parallélisme tensoriel).

</details>

2. ▢ Un collègue affirme « le bf16 exige du loss scaling, comme le fp16, puisque ce sont deux formats de 16 bits ». En utilisant l'exemple détaillé de cette leçon, quelle est la vraie réponse, et qu'est-ce qui est précisément confondu ?

<details markdown="1"><summary>Vérifier</summary>

Le bf16 n'a pas besoin de loss scaling comme le fp16. Le loss scaling traite la plage d'exposant étroite de 5 bits du fp16 qui cause de l'underflow ; le bf16 garde la plage d'exposant complète de 8 bits du fp32, ce qui est précisément le problème que le loss scaling existe pour contourner, si bien que le bf16 n'a pas ce problème en premier lieu. L'affirmation du collègue confond les largeurs de bits des deux formats (16 bits au total tous deux) avec leur vraie différence de plage d'exposant, qui est ce qui détermine si le loss scaling est nécessaire.

</details>

3. ▢ Un plan n'énonce qu'un seul chiffre de coût de calcul total, sans décomposition du ratio, du pipeline de données, du plan de parallélisme ou du plan de stabilité. D'après les leçons 23 et celle-ci, ce plan est-il relisible tel qu'énoncé ?

<details markdown="1"><summary>Vérifier</summary>

Pas vraiment : un seul nombre regroupé n'invite que « cela peut-il être moins cher » et cache quelles affirmations sous-jacentes sont bien étayées et lesquelles sont des hypothèses non examinées. Une vraie relecture a besoin que le plan soit découpé dans les catégories que parcourt la liste de contrôle de cette leçon, pour que chacune puisse être vérifiée selon ses propres termes.

</details>

## Exercices en situation réelle

- [ ] Trouvez une vraie configuration de pré-entraînement publiée (un rapport technique, le fichier de configuration d'un script d'entraînement ou une model card) et passez-la à la liste de contrôle de cette leçon, étape par étape, en notant quels éléments sont énoncés explicitement et lesquels sont laissés sous silence.
- [ ] Trouvez une affirmation sur le pré-entraînement des LLM énoncée avec assurance dans un article de blog ou une réponse de forum, et confrontez-la à la vraie source primaire dont elle devrait remonter (un article que ce parcours cite, ou un autre que vous localisez). Notez si elle tient, si c'est une simplification, ou si c'est une vraie confusion comme l'exemple bf16 de cette leçon.
- [ ] Demain : écrivez une courte relecture, de trois à cinq phrases, d'un plan de pré-entraînement réel ou hypothétique, en nommant au moins un choix précis que vous contesteriez et ce que vous demanderiez à la personne qui le défend de justifier.

## Pour aller plus loin

- [Article : "Training Compute-Optimal Large Language Models", Hoffmann et al., 2022](https://arxiv.org/abs/2203.15556)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
