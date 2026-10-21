---
title: "17. Ce que QLoRA coûte réellement"
description: "Séparer la dégradation du base model de celle de l'entraînement"
type: lesson
---

# Leçon 17. Ce que QLoRA coûte réellement

**Lien avec la mission :** La mission dit « expliquer les différences mesurées, pas celles qui sont annoncées ». Cette leçon est la mesure.
**Source primaire :** [Article : "QLoRA: Efficient Finetuning of Quantized LLMs", Dettmers et al., arXiv:2305.14314](https://arxiv.org/abs/2305.14314)
**Prérequis :** [Leçon 16](0016-training-through-a-quantized-base.md)

## Échauffement

1. ▢ Pourquoi un base model gelé en 4 bits peut-il quand même laisser passer des gradients ?

<details markdown="1"><summary>Vérifier</summary>

C'est une constante du graphe. Propager le gradient exige de le lire en haute précision, pas de le dériver, et aucun gradient n'est stocké pour lui.

</details>

2. ▢ Quel composant de QLoRA est réellement propre à CUDA ?

<details markdown="1"><summary>Vérifier</summary>

Les paged optimizers, qui dépendent de la mémoire unifiée de NVIDIA. Et ils comptent le moins pour l'entraînement d'adapters, où l'état de l'optimizer est petit.

</details>

3. ▢ Où fusionnez-vous un adapter entraîné face à un base model en 4 bits ?

<details markdown="1"><summary>Vérifier</summary>

Dans le base model en pleine précision, puis quantifiez ensuite si nécessaire.

</details>

## À savoir

### L'affirmation de l'article, énoncée précisément

Le résultat phare de QLoRA est que le fine-tuning avec adapter en NF4 4 bits peut égaler les performances d'un fine-tuning en 16 bits sur les tâches mesurées. C'est un résultat solide et il est authentique.

C'est aussi une affirmation sur **une configuration précise, sur des benchmarks précis**. Ce qu'elle n'établit pas :

- Que NF4 est gratuit sur *votre* tâche. Les benchmarks de suivi d'instructions ne sont pas votre distribution de production.
- Que la quantification est gratuite à toutes les échelles. L'erreur de quantification est une perturbation relative fixe, et les petits modèles ont moins de redondance pour l'absorber, donc la dégradation est en général plus visible sur les petits modèles que sur les grands.
- Que toutes les implémentations 4 bits sont équivalentes. Le type de quantification, la taille de bloc, l'activation ou non de la double quantification, le compute dtype et la qualité des kernels varient tous.

Lire l'affirmation d'un article comme « la quantification est gratuite », c'est exactement le mode de défaillance visé par la formule de la mission : *mesuré, pas annoncé*.

### Séparer les deux coûts

Il y a deux questions de qualité distinctes et les confondre rend les résultats ininterprétables.

**Coût 1. Le base model quantifié est un moins bon modèle, avant tout entraînement.** Une pure propriété de la représentation.

**Coût 2. Entraîner face à un base model quantifié donne un moins bon adapter.** Une propriété du processus d'entraînement, par-dessus le coût 1.

Mesurez-les séparément :

| Configuration | Isole |
|---|---|
| Base model en bf16, sans adapter | Le point de référence |
| Base model en 4 bits, sans adapter | Le coût 1, les dégâts de quantification seuls |
| Base model en bf16 + adapter | Le plafond d'entraînement |
| Base model en 4 bits + adapter | Les coûts 1 et 2 combinés |
| Adapter entraîné en 4 bits fusionné dans un base model en bf16 | Si le coût 1 survit dans l'artefact |

![La précision du base model contre l'adapter, sous forme de grille deux par deux contenant le point de référence, le plafond d'entraînement, le coût 1 seul et les deux coûts ensemble, avec une cinquième boîte sous la grille pour un adapter entraîné en 4 bits et fusionné dans un base model en bf16.](images/the-one-that-is-not-a-cell.svg)

Quatre des cinq configurations sont des cases d'une même grille. La cinquième n'en est pas une, parce qu'elle utilise pour l'entraînement un base model différent de celui du déploiement, et une configuration sans case où se loger est facile à oublier d'exécuter.

Cette dernière ligne est la plus intéressante et elle est régulièrement sautée. Vous avez entraîné face à un base model dégradé, mais vous pouvez *déployer* face à celui en pleine précision. Savoir si l'adapter a appris à compenser l'erreur de quantification, et se trouve donc mal assorti quand l'erreur disparaît, est une question empirique qui a une vraie réponse pour votre tâche. Mesurez-la plutôt que de supposer dans un sens ou dans l'autre.

### Comment mesurer honnêtement

**Gardez tout le reste fixe.** Mêmes données, même découpage, même seed, mêmes rank, alpha, learning rate, schedule et pas. Une seule variable : la précision du base model. Une comparaison où deux choses changent n'est pas une comparaison.

**Utilisez une métrique de tâche, pas la loss.** La loss n'est pas comparable d'une configuration à l'autre comme vous le voudriez, et ce n'est pas ce qui vous importe. La leçon 23 traite du choix de la métrique.

**Rapportez une dispersion, pas un point.** Exécutez chaque configuration avec trois seeds. Si votre variation d'une seed à l'autre est de 2 points et que votre effet de quantification est de 1 point, vous n'avez rien mesuré, et cela arrive constamment. Une comparaison à seed unique de deux configurations est une anecdote.

**Mesurez aussi la vitesse et la mémoire.** Ce sont les raisons pour lesquelles vous envisagez la quantification, donc elles ont leur place dans le même tableau que la qualité.

### Un tableau de résultats qui vaut la peine d'être produit

| Configuration | Métrique de tâche | Mémoire de pointe | Sec/pas |
|---|---|---|---|
| Base model en bf16 + adapter | | | |
| Base model en NF4 + adapter | | | |
| NF4 sans double quantification | | | |
| int4 plutôt que NF4 | | | |
| NF4, fusionné dans bf16 pour l'eval | | | |

Remplir ce tableau une fois, sur une tâche qui vous importe, vaut plus que n'importe quelle quantité de lecture sur la quantification. La dernière ligne en particulier vous apprendra quelque chose qu'on ne trouve pas dans une documentation.

### À quoi s'attendre, pour pouvoir être surpris

Des attentes approximatives tirées de la littérature et de la pratique courante, comme un a priori à mettre à jour plutôt qu'un résultat :

- **Mémoire :** environ 4× de réduction sur les poids de base. Fiable, c'est de l'arithmétique.
- **Vitesse :** plus lent par pas, souvent nettement. La déquantification est un vrai travail.
- **Qualité :** petite dégradation, fréquemment dans le bruit des seeds sur les gros modèles, plus visible sur les petits et sur les tâches à faibles marges.
- **NF4 contre int4 :** NF4 meilleur à stockage identique.
- **Double quantification :** économie de mémoire avec un effet négligeable sur la qualité.

Si vos mesures divergent nettement de ces attentes, cela mérite une enquête plutôt qu'un rejet. La cause la plus courante est un chemin de kernel non optimisé sur votre backend, ou une comparaison où plus d'une chose a changé.

### Quand recourir à QLoRA

**Utilisez-le quand la mémoire est la contrainte qui lie**, c'est-à-dire quand un base model en bf16 plus les activations ne tient pas et que l'alternative est de ne pas entraîner du tout, ou d'entraîner un plus petit modèle. Un grand modèle en 4 bits bat généralement un petit modèle en bf16.

**Ne l'utilisez pas quand la mémoire n'est pas la contrainte.** Si bf16 tient, quantifier vous coûte de la vitesse et un peu de qualité pour rien. Le réflexe de tutoriel de toujours charger en 4 bits est un coût sans bénéfice quand vous aviez de toute façon la mémoire.

## Pratique

1. ▢ Énoncez l'affirmation phare de QLoRA, puis énoncez ce qu'elle n'établit pas.

<details markdown="1"><summary>Vérifier</summary>

Affirmation : le fine-tuning avec adapter en NF4 4 bits peut égaler les performances d'un fine-tuning en 16 bits sur les benchmarks mesurés.

N'établit pas : que cela tient sur votre tâche et votre distribution, que cela tient également à petite échelle de modèle, ou que toute implémentation 4 bits équivaut à celle de l'article.

</details>

2. ▢ Nommez les deux coûts de qualité distincts et comment vous les isolez.

<details markdown="1"><summary>Vérifier</summary>

Coût 1 : le base model quantifié est un moins bon modèle avant l'entraînement, donc mesurez le base model sans adapter, quantifié contre non quantifié.

Coût 2 : entraîner face à un base model quantifié donne un moins bon adapter, donc comparez des adapters entraînés sur des base models quantifiés contre en pleine précision, tout le reste étant fixé.

</details>

3. ▢ Vous mesurez 71.2 pour bf16 et 70.8 pour NF4. La quantification vous coûte-t-elle 0.4 point ?

<details markdown="1"><summary>Vérifier</summary>

On ne sait pas. Sans dispersion sur les seeds, vous ne pouvez pas distinguer 0.4 du bruit, et la variation d'une seed à l'autre sur un run de fine-tuning le dépasse fréquemment.

Exécutez trois seeds par configuration et comparez les distributions. Une différence de cette taille sur une seule seed n'est pas un résultat.

</details>

4. ▢ Quelle comparaison est le plus souvent sautée, et que vous apprend-elle ?

<details markdown="1"><summary>Vérifier</summary>

Évaluer un adapter entraîné en 4 bits fusionné dans le base model en pleine précision.

Elle vous dit si le coût de la quantification doit survivre dans votre artefact déployé. Vous avez entraîné à peu de frais, mais rien ne vous oblige à servir à peu de frais. Elle révèle aussi si l'adapter s'est adapté à l'erreur de quantification elle-même.

</details>

5. ▢ Votre run en bf16 tient confortablement en mémoire. Devez-vous quand même passer en 4 bits ?

<details markdown="1"><summary>Vérifier</summary>

Non. Vous paieriez des pas plus lents et un petit risque sur la qualité pour économiser une mémoire dont vous n'étiez pas à court.

La quantification est une réponse à une contrainte mémoire qui lie. L'appliquer par réflexe, parce que le tutoriel le faisait, est un coût sans bénéfice correspondant.

</details>

6. ▢ NF4 dégrade nettement votre tâche sur un modèle 1B mais l'article ne rapportait aucune dégradation. Contredisez-vous l'article ?

<details markdown="1"><summary>Vérifier</summary>

Non. L'erreur de quantification est une perturbation relative fixe et les petits modèles ont moins de redondance pour l'absorber, donc la dégradation est en général plus visible à petite échelle. Votre tâche et votre métrique diffèrent aussi des benchmarks mesurés.

Les deux résultats peuvent être justes. C'est précisément pourquoi la mission demande des différences mesurées plutôt qu'annoncées.

</details>

## Exercices en situation réelle

- [ ] Remplissez le tableau de comparaison à cinq lignes sur une tâche qui vous importe. Trois seeds par ligne.
- [ ] Mesurez la mémoire de pointe et les secondes par pas pour chaque ligne, à côté du chiffre de qualité.
- [ ] Évaluez l'adapter entraîné en 4 bits fusionné dans le base model en bf16. Notez s'il a battu, égalé ou perdu face à la version servie en 4 bits.
- [ ] Demain : écrivez un paragraphe qui dit ce que la quantification a coûté à *vous*, chiffres à l'appui, et en quoi cela diffère de ce que vous attendiez.

## Pour aller plus loin

- [Article : "QLoRA: Efficient Finetuning of Quantized LLMs", Dettmers et al., arXiv:2305.14314](https://arxiv.org/abs/2305.14314) : lisez la section sur les limites
- [r/LocalLLaMA](https://www.reddit.com/r/LocalLLaMA/) : le plus grand réservoir de mesures de praticiens sur du matériel grand public, et un bon endroit pour confronter vos chiffres
- [Leçon 23. Des métriques qui veulent dire quelque chose](0023-metrics-that-mean-something.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
