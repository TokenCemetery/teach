---
title: "21. Évaluation held-out périodique"
description: "La loss d'entraînement dit que le modèle s'ajuste à ses propres données d'entraînement ; seul un contrôle held-out dit quelque chose du reste"
type: lesson
---

# Leçon 21. Évaluation held-out périodique

**Lien avec la mission :** « Savoir lire un tableau de bord d'entraînement et dire si le run est sur la bonne voie » est la case « Terminée quand » de cette étape dans « Le fil conducteur ». La leçon 20 a couvert la surveillance des signaux internes du run d'entraînement ; cette leçon couvre le contrôle de checkpoints sauvegardés sur quelque chose que la loss d'entraînement ne peut pas vous dire, et confie cette mesure à l'endroit où elle est enseignée en entier.
**Source primaire :** [Article : "Scaling Language Models: Methods, Analysis & Insights from Training Gopher", Rae et al., 2021](https://arxiv.org/abs/2112.11446)
**Prérequis :** [Leçon 20](0020-reading-a-loss-curve.md), [Données held-out](../../evals/GLOSSARY.md)

## Échauffement

1. ▢ Pourquoi un loss scalar qui tombe vers zéro, ou une norme d'activation qui fait un pic, pourraient-ils avertir plus tôt de l'instabilité que la courbe de loss d'entraînement elle-même ?

<details markdown="1"><summary>Vérifier</summary>

Ce sont des symptômes du problème numérique sous-jacent en train de se développer, qui peuvent apparaître avant qu'il ne devienne assez grand pour perturber visiblement la courbe de loss ; le temps qu'un pic soit clairement visible dans la loss elle-même, le problème a peut-être déjà couvé pendant un certain temps.

</details>

2. ▢ Pourquoi un tableau de bord qui suit la loss, la norme du gradient et un signal de stabilité n'est-il utile en pratique que s'il est surveillé fréquemment ?

<details markdown="1"><summary>Vérifier</summary>

Parce que les pannes et les instabilités sont des événements fréquents et courants à grande échelle (étape 8), si bien qu'un problème attrapé tard coûte bien plus de progression perdue que le même problème attrapé tôt.

</details>

## À savoir

### Ce que la loss d'entraînement ne peut pas vous dire

La loss d'entraînement mesure à quel point un modèle s'ajuste aux batches précis sur lesquels il est actuellement entraîné. Une loss d'entraînement qui décroît régulièrement est nécessaire pour un run sain, mais ce n'est pas la même chose que le modèle qui est bon à tout ce qu'une personne extérieure à la boucle d'entraînement lui demandera réellement de faire, et cela ne dit rien du tout sur le fait de savoir si cette amélioration tiendrait sur du texte que le modèle n'a jamais vu à l'entraînement. Une courbe de loss d'entraînement qui a l'air parfaitement saine peut quand même reposer sur un modèle qui sur-apprend discrètement des particularités propres à son propre mélange d'entraînement.

### À quoi ressemblait l'évaluation périodique de Gopher lui-même

Rae et al. n'ont pas attendu la fin de l'entraînement pour vérifier cela. Ils rapportent des courbes d'évaluation calculées périodiquement pendant l'entraînement, sur quatre benchmarks de modélisation du langage (Wikitext103, LAMBADA, Curation Corpus et C4) qu'ils ont explicitement retirés au préalable de l'ensemble d'entraînement, précisément pour qu'un bon score sur eux ne puisse pas s'expliquer par le fait que le modèle ait simplement vu ce texte exact pendant l'entraînement. Contrôler un benchmark de ce genre périodiquement, plutôt qu'une seule fois tout à la fin, est ce qui permet réellement à une équipe d'attraper un problème, un bug dans le pipeline de données, une régression due à un changement de configuration, une divergence inattendue des capacités, pendant que le run est encore en cours et qu'on peut encore y faire quelque chose, plutôt que de le découvrir seulement après que le budget de calcul complet a déjà été dépensé.

### Pourquoi « retiré de l'ensemble d'entraînement » fait un vrai travail

L'expression qu'emploient Rae et al., des benchmarks « explicitement retirés de l'ensemble d'entraînement », est la même idée autour de laquelle a été construite la leçon 1 du contenu sur le pipeline de données de ce parcours, appliquée à l'évaluation plutôt qu'à l'entraînement : un score ne signifie quelque chose sur la généralisation que si le modèle n'a pas pu réussir en ayant mémorisé le texte exact testé. C'est précisément ce que signifient les **données held-out**, et c'est un sujet assez vaste, avec ses propres voies de contamination, méthodes de détection et techniques de conception, pour qu'un parcours entier soit construit autour.

### Où cela passe la main

`llm/evals` possède en entier la méthodologie d'évaluation : comment construire un jeu held-out qui résiste à la contamination, ce qui rend une métrique digne de confiance, et comment transformer un nombre en décision défendable. La seule revendication de ce parcours sur cette matière est celle faite dans cette leçon : un run de pré-entraînement a besoin de contrôles périodiques sur des données held-out, sur des checkpoints sauvegardés, et pas seulement à la fin. Pour tout ce qui va au-delà, la [fiche Données held-out et contamination](../../evals/reference/held-out-data-and-contamination.md) de `llm/evals` est celle à lire ensuite, et non une reformulation ici.

## Pratique

1. ▢ La loss d'entraînement d'un modèle a décru régulièrement pendant tout le run. Cela vous dit-il, à soi seul, si le modèle réussit bien des tâches qu'il n'a pas été directement entraîné à ajuster ?

<details markdown="1"><summary>Vérifier</summary>

Non. La loss d'entraînement mesure l'ajustement aux propres batches d'entraînement du modèle ; une loss d'entraînement qui décroît régulièrement est nécessaire pour un run sain mais ne dit rien à soi seule sur les performances sur des données ou des tâches sur lesquelles le modèle n'a pas été entraîné, ce à quoi sert une évaluation held-out.

</details>

2. ▢ Pourquoi Rae et al. ont-ils explicitement retiré Wikitext103, LAMBADA, Curation Corpus et C4 de l'ensemble d'entraînement de Gopher avant de les utiliser comme benchmarks d'évaluation périodique ?

<details markdown="1"><summary>Vérifier</summary>

Pour qu'un bon score sur ces benchmarks ne puisse pas s'expliquer par le fait que le modèle ait simplement vu et mémorisé ce texte exact pendant l'entraînement. Un benchmark sur lequel le modèle a été entraîné ne peut pas distinguer une vraie capacité de la mémorisation, ce qui fait d'un benchmark held-out une preuve significative d'une manière dont un benchmark contaminé ne l'est pas.

</details>

3. ▢ Qu'apporte réellement à une équipe le fait d'évaluer périodiquement pendant l'entraînement plutôt qu'une seule fois à la fin, vu le coût d'un run d'entraînement complet ?

    - a) Aucun avantage sur une seule évaluation à la fin ; c'est le résultat final qui compte
    - b) Cela permet d'attraper, et éventuellement de traiter, un bug, une régression ou une divergence des capacités pendant que le run est encore en cours, plutôt que de le découvrir seulement après que le budget de calcul complet est déjà dépensé
    - c) Cela remplace entièrement le besoin de données held-out
    - d) Cela ne compte que pour de très courts runs d'entraînement

<details markdown="1"><summary>Vérifier</summary>

**b)** est le bénéfice pratique direct : attraper un problème tôt, alors qu'il reste du budget de calcul pour y répondre, plutôt que de s'en apercevoir seulement une fois le run terminé. (a) ignore tout cela. (c) inverse la relation ; l'évaluation périodique doit toujours être held-out pour signifier quoi que ce soit. (d) est à l'envers, puisqu'un run plus long et plus coûteux a davantage à perdre d'un problème attrapé tard.

</details>

## Exercices en situation réelle

- [ ] Trouvez comment un framework d'entraînement ou une configuration de suivi d'expériences auquel vous avez accès planifie l'évaluation périodique pendant l'entraînement (un intervalle d'évaluation mesuré en pas ou en tokens est courant), et notez quels benchmarks ou métriques il évalue par défaut.
- [ ] Lisez la [fiche Données held-out et contamination](../../evals/reference/held-out-data-and-contamination.md) de `llm/evals` et identifiez laquelle de ses deux voies de contamination (l'absorption par le pré-entraînement, ou le sur-apprentissage itératif) est celle contre laquelle se prémunit la formulation « explicitement retirés de l'ensemble d'entraînement » de Gopher.
- [ ] Demain : pour un run de pré-entraînement hypothétique de votre choix, décidez d'un intervalle d'évaluation (à quelle fréquence, en tokens ou en pas, vous contrôleriez les performances held-out) et nommez un benchmark ou un jeu held-out sur lequel vous le contrôleriez, et pourquoi.

## Pour aller plus loin

- [Article : "Scaling Language Models: Methods, Analysis & Insights from Training Gopher", Rae et al., 2021](https://arxiv.org/abs/2112.11446)
- [`llm/evals` : Données held-out et contamination](../../evals/reference/held-out-data-and-contamination.md)
- [Ressources](../RESOURCES.md)

---

L'étape 9 a couvert la surveillance d'un run pendant qu'il se déroule, à la fois ses propres éléments internes et ses checkpoints face à quelque chose d'extérieur. L'étape 10 clôt le fil conducteur : décider s'il faut lancer l'un de ces runs et défendre ce choix face à quelqu'un d'autre.

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
