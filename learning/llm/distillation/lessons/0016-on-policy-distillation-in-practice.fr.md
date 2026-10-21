---
title: "16. La distillation on-policy en pratique"
description: "Ce que la distillation on-policy coûte par pas, ce qu'elle rapporte, et comment Qwen3 l'a utilisée pour ses petits modèles"
type: lesson
---

# Leçon 16. La distillation on-policy en pratique

**Lien avec la mission :** La mission vous demande de dire quand la distillation on-policy mérite son coût, ce qui veut dire compter ce que coûte un pas, quel signal il renvoie, et ce qu'une équipe de production a mesuré face à l'alternative.
**Source primaire :** [Article : "Qwen3 Technical Report", Qwen Team, 2025](https://arxiv.org/abs/2505.09388), section 4.5 et la discussion sur la distillation on-policy à la section 4.7
**Prérequis :** [Leçon 8](0008-sequence-level-distillation.md), [Leçon 14](0014-exposure-bias.md), [Leçon 15](0015-gkd-and-minillm.md), [Distillation off-policy](../GLOSSARY.md), [Distillation on-policy](../GLOSSARY.md)

## Échauffement

1. ▢ Que contrôle la fraction de données de l'élève lambda dans GKD, et quelles sont ses deux valeurs extrêmes ?

<details markdown="1"><summary>Vérifier</summary>

C'est la probabilité qu'un pas s'entraîne sur des séquences générées par l'élève plutôt que sur un jeu fixe. Lambda 0 est la distillation supervisée sur données fixes et lambda 1 est purement on-policy.

</details>

2. ▢ La première phase de distillation de Qwen3 s'entraîne sur des sorties que l'enseignant a générées. Quel terme de la leçon 8 nomme cela, et est-ce on-policy ?

<details markdown="1"><summary>Vérifier</summary>

La distillation au niveau de la séquence, dans les mots du rapport Qwen3 « response distillation ». C'est de l'off-policy : les séquences ont été fixées par l'enseignant, pas écrites par l'élève.

</details>

3. ▢ Le biais d'exposition est un décalage sur les préfixes que voit l'élève. Nommez le seul élément qu'un pas on-policy exige de l'enseignant et qu'un pas sur texte fixe n'exige pas.

<details markdown="1"><summary>Vérifier</summary>

Sa distribution sur les tokens à chaque position de la propre séquence de l'élève, ce qui veut dire que le modèle enseignant doit être exécuté sur la sortie de l'élève pendant l'entraînement. Du texte que l'enseignant a déjà écrit ne fournit pas cela.

</details>

## À savoir

### Ce que coûte un pas

Un pas off-policy avec du texte d'enseignant stocké coûte une passe avant et arrière de l'élève sur des séquences fixes. Un pas off-policy avec des logits d'enseignant stockés ajoute une lecture sur disque, et le coût de stockage relève de la leçon 7.

Un pas on-policy ajoute du travail, et il vaut la peine de le lister dans l'ordre :

| Étape | Travail | Notes |
|---|---|---|
| 1 | L'élève génère une séquence pour chaque prompt | Décodage séquentiel. Moins cher que si l'enseignant le faisait, parce que l'élève est plus petit (GKD, section 3.1) |
| 2 | L'enseignant exécute une passe avant sur la séquence terminée | Une passe parallèle, pas de la génération. Exige l'enseignant en mémoire ou joignable |
| 3 | L'élève exécute la passe avant et arrière et la divergence est calculée | Identique à un pas off-policy |

Les deux premières lignes n'ont pas d'équivalent off-policy avec du texte fixe. La propre note d'efficacité de l'article concerne plutôt SeqKD : dans l'expérience d'instruction tuning, GKD n'a pas exécuté SeqKD « due to its computational inefficiency for generating data from the teacher during training » (section 4.4). L'étape 1 ici utilise le petit modèle, qui est le côté le moins cher de ce compromis. Cette comparaison de coût est l'affirmation de l'article, et le tableau à trois lignes ci-dessus est ma comptabilité du travail.

### Signal dense contre récompense éparse

La distillation n'est pas la seule façon d'améliorer un petit modèle sur ses propres échantillons. L'apprentissage par renforcement s'entraîne aussi sur les propres séquences du modèle, mais il note chaque séquence entière avec une récompense scalaire. La section 3.2 de GKD écrit l'objectif combiné avec la récompense sous la forme `r(y)`, un seul nombre par séquence.

La distillation on-policy renvoie un score pour chaque token, tiré de la distribution de l'enseignant à cette position. C'est un signal plus dense par échantillon. Dense veut dire plus d'information par séquence générée. Cela ne veut pas dire que l'enseignant a raison, ce sur quoi la leçon 18 revient.

La conséquence pratique va dans un seul sens. Le RL peut améliorer un modèle sans qu'aucun modèle plus fort soit disponible, parce qu'il n'a besoin que d'une récompense. La distillation on-policy a besoin qu'un enseignant plus fort existe.

### Comment Qwen3 l'a utilisée

Le rapport Qwen3 décrit un pipeline de post-training en quatre étapes pour ses modèles phares, et une « strong-to-weak distillation » séparée pour les modèles légers : cinq modèles denses (0.6B, 1.7B, 4B, 8B et 14B) et un modèle mixture-of-experts (30B-A3B). La motivation était le coût : la distillation « eliminates the necessity of performing an exhaustive four-stage training process individually for every small-scale model » (section 4).

Les petits modèles sont distillés en deux phases (section 4.5) :

| Phase | Données | Signal d'entraînement |
|---|---|---|
| Off-policy | Sorties de l'enseignant générées en modes thinking et non-thinking | Distillation de réponses, pour donner la compétence de raisonnement de base et la capacité de changer de mode |
| On-policy | L'élève génère des réponses dans l'un ou l'autre mode | L'élève est affiné en alignant ses logits sur ceux de l'enseignant (Qwen3-32B ou Qwen3-235B-A22B) pour minimiser la divergence KL |

Lisez l'ordre. La phase off-policy vient d'abord, et le rapport dit qu'elle pose « a solid foundation » pour la phase on-policy. Cela concorde avec la remarque de GKD selon laquelle l'entraînement on-policy suppose un élève capable de déjà générer des séquences acceptables. C'est un calendrier en deux étapes, pas le mélange lambda par batch de GKD.

### La comparaison avec le RL

La section 4.7 compare la distillation on-policy au renforcement direct sur Qwen3-8B. Les deux partent du même checkpoint distillé off-policy, et la comparaison n'utilise que des requêtes de maths et de code. Le tableau 21 rapporte, avec le pass@64 entre parenthèses là où le rapport en donne un :

| Méthode | AIME'24 | AIME'25 | MATH500 | LiveCodeBench v5 | MMLU-Redux | GPQA-Diamond | Heures GPU |
|---|---|---|---|---|---|---|---|
| Distillation off-policy | 55.0 (90.0) | 42.8 (83.3) | 92.4 | 42.0 | 86.4 | 55.6 | non indiqué |
| plus apprentissage par renforcement | 67.6 (90.0) | 55.5 (83.3) | 94.8 | 52.9 | 86.9 | 61.3 | 17,920 |
| plus distillation on-policy | 74.4 (93.3) | 65.5 (86.7) | 97.0 | 60.3 | 88.3 | 63.3 | 1,800 |

Sur chaque benchmark du tableau, la distillation on-policy a obtenu un score supérieur au RL, et elle a utilisé environ un dixième des heures GPU : 17,920 divisé par 1,800 fait 9.96. Le rapport lit cela comme une performance nettement meilleure que le RL pour environ un dixième des heures GPU. Il note aussi que le pass@64 sur AIME a augmenté après la distillation et n'a pas changé après le RL, ce qu'il prend comme preuve que distiller à partir des logits de l'enseignant élargit l'espace d'exploration de l'élève.

### Dans quelle mesure se fier à ce tableau

C'est un rapport, une taille d'élève, des requêtes de maths et de code seulement, et les auteurs ont comparé leurs deux propres méthodes. Le rapport ne dit pas quel enseignant a été utilisé pour la comparaison sur le 8B. Je n'ai pas trouvé d'indication précisant si les chiffres d'heures GPU incluent l'exécution de l'enseignant, ne supposez donc pas qu'ils l'incluent. La recette de RL n'est pas décrite dans la comparaison, donc un run de RL mieux réglé pourrait combler une partie de l'écart. Le résultat est une preuve solide que la distillation était moins chère et meilleure dans le cadre de Qwen3, et non une preuve pour tous les cadres.

Notez aussi ce que la comparaison omet. Les enseignants eux-mêmes sont sortis du pipeline en quatre étapes, qui comprend du RL. L'économie est réelle, mais elle suppose que quelqu'un a déjà payé l'enseignant.

## Pratique

1. ▢ D'après le tableau 21, combien de points le RL et la distillation on-policy ont-ils chacun ajoutés sur LiveCodeBench v5 par rapport au checkpoint off-policy, et combien d'heures GPU par point chacun a-t-il utilisées ?

<details markdown="1"><summary>Vérifier</summary>

Le RL est passé de 42.0 à 52.9, soit +10.9 points, et 17,920 divisé par 10.9 fait environ 1,640 heures GPU par point. La distillation on-policy est passée à 60.3, soit +18.3 points, et 1,800 divisé par 18.3 fait environ 98 heures GPU par point. Le rapport est d'environ 17 contre 1 sur ce benchmark, plus grand que le 10 contre 1 du titre, parce que la distillation a aussi gagné plus de points. Les deux nombres valent pour une taille d'élève et un jeu de requêtes.

</details>

2. ▢ Quel coût est présent dans un pas de distillation on-policy et absent d'un pas off-policy sur du texte d'enseignant stocké ?

    - a) La rétropropagation à travers le modèle élève
    - b) Le calcul d'une loss à chaque position de token
    - c) L'exécution de l'enseignant sur la sortie de l'élève
    - d) La tokenisation des prompts avant le début de l'entraînement

<details markdown="1"><summary>Vérifier</summary>

**c)** L'enseignant doit évaluer des séquences qui n'existaient pas avant que l'élève les génère. (b), (a) et (d) ont aussi lieu dans les pas off-policy.

</details>

3. ▢ Le pass@1 s'est amélioré après le RL comme après la distillation on-policy. Qu'a montré le pass@64 sur AIME pour chacun, et que conclut le rapport ?

<details markdown="1"><summary>Indice</summary>

Regardez les nombres entre parenthèses dans les colonnes AIME pour la ligne RL.

</details>

<details markdown="1"><summary>Vérifier</summary>

Pour le RL, le pass@64 est resté à 90.0 sur AIME'24 et à 83.3 sur AIME'25, inchangé par rapport au checkpoint de départ. Après la distillation on-policy, il est monté à 93.3 et 86.7. Le rapport conclut que distiller à partir des logits de l'enseignant a élargi l'espace d'exploration de l'élève alors que le RL ne l'a pas fait. C'est l'interprétation des auteurs d'une seule comparaison.

</details>

4. ▢ Vous avez un élève de 8B, un enseignant plus fort avec le même tokenizer, une tâche de maths avec une réponse vérifiable, et un budget GPU limité. Le tableau de Qwen3 tranche-t-il entre RL et distillation on-policy ?

<details markdown="1"><summary>Vérifier</summary>

Il oriente vers la distillation sans trancher. Il soutient que, avec un enseignant fort déjà disponible et l'élève d'abord échauffé par distillation off-policy, la distillation on-policy a été moins chère et meilleure dans les runs de Qwen3. Il ne couvre ni votre tâche, ni votre enseignant, ni le fait que les chiffres d'heures GPU incluent ou non l'enseignant. S'il n'existe aucun enseignant plus fort, la distillation n'est pas disponible du tout et le RL est la voie, ce qui est la façon dont les enseignants de Qwen3 ont été construits.

</details>

5. ▢ Pourquoi Qwen3 exécute-t-il la phase off-policy avant la phase on-policy, et qu'est-ce qui, dans GKD, soutient cet ordre ?

<details markdown="1"><summary>Vérifier</summary>

La phase off-policy donne à l'élève la capacité de raisonnement de base et le changement de mode, ce qui, dit le rapport, pose une fondation pour l'entraînement on-policy. GKD fait la même hypothèse : il lui faut un élève capable de déjà générer des séquences de qualité suffisante pour que le retour de l'enseignant ait un sens, et ses élèves partaient de checkpoints affinés de façon supervisée.

</details>

## Exercices en situation réelle

- [ ] Ouvrez la section 4.7 du rapport Qwen3 et trouvez le tableau 21. Copiez dans une note les trois cellules d'heures GPU et d'AIME'24 et calculez les points par heure de chaque méthode à partir d'elles.
- [ ] Écrivez en trois lignes le coût par pas de votre propre run prévu : qui génère, qui évalue, qui met à jour. Marquez ensuite quel modèle est assez grand pour avoir besoin de son propre GPU.
- [ ] Demain : sans notes, écrivez les deux phases de Qwen3, ce sur quoi chacune s'entraîne, et deux raisons de ne pas généraliser le chiffre de 1/10.

## Pour aller plus loin

- [Distillation on-policy](../reference/on-policy-distillation.md)
- [Article : "Qwen3 Technical Report", Qwen Team, 2025](https://arxiv.org/abs/2505.09388)
- [Post-training](../../post-training/)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
