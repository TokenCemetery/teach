---
title: "5. Layer norm et connexions résiduelles"
description: "Pourquoi empiler de nombreux blocs transformer exige un chemin de gradient propre et des plages d'activation stables, et comment les connexions résiduelles et la layer norm en fournissent chacune un"
type: lesson
---

# Leçon 5. Layer norm et connexions résiduelles

**Lien avec la mission :** L'attention seule (étape 1) ne s'empile pas d'elle-même en un réseau profond et entraînable ; les connexions résiduelles et la layer normalization sont les deux pièces qui rendent l'empilement de nombreux blocs transformer (étape 3) praticable plutôt qu'instable.
**Source primaire :** [Article : "Layer Normalization", Ba, Kiros et Hinton, 2016](https://arxiv.org/abs/1607.06450)
**Prérequis :** [Leçon 4](0004-positional-encoding.md), [Scaled dot-product attention](../GLOSSARY.md)

## Échauffement

1. ▢ Pourquoi l'encodage positionnel est-il nécessaire, étant donné ce que l'équation de l'attention calcule à elle seule ?

<details markdown="1"><summary>Vérifier</summary>

L'attention traite son entrée comme un ensemble non ordonné : échanger deux positions réétiquette simplement la sortie sans changer aucune relation calculée. L'encodage positionnel injecte la position dans les embeddings de tokens eux-mêmes, ce qui est la seule façon de rendre les produits scalaires de l'attention sensibles à l'ordre.

</details>

2. ▢ Pourquoi mettre à 0 le score brut d'une position masquée ne l'exclut-il pas correctement de l'attention ?

<details markdown="1"><summary>Vérifier</summary>

`exp(0) = 1`, une valeur entièrement ordinaire qui reste en concurrence pour la masse de probabilité dans le dénominateur du softmax. Seul un grand nombre négatif fait tomber son exponentielle pratiquement à zéro, ce qui supprime réellement la contribution de cette position.

</details>

## À savoir

### Les connexions résiduelles donnent aux gradients un chemin direct

Une sous-couche de transformer (l'attention, ou le bloc feed-forward de la leçon suivante) est enveloppée dans une **connexion résiduelle** (residual connection) : la sortie du bloc est `x + Sublayer(x)`, et non `Sublayer(x)` seul. Cela compte dès que de nombreux blocs de ce genre sont empilés (le sujet de l'étape 3) : sans le terme `+ x`, un gradient qui remonte pendant l'entraînement doit traverser la transformation de chaque sous-couche à chaque couche, et dans une pile profonde ce chemin peut tendre vers zéro ou exploser, rendant le réseau difficile voire impossible à bien entraîner. Avec le terme résiduel, le gradient dispose d'une seconde voie, directe, à travers la connexion identité `+ x` à chaque couche, quoi que fasse la sous-couche elle-même, ce qui garde un signal d'entraînement exploitable jusqu'aux toutes premières couches d'une pile profonde.

### La layer normalization garde les activations de chaque couche dans une plage prévisible

La **layer normalization** normalise le vecteur d'activation propre à un seul token, en soustrayant sa moyenne et en divisant par son écart type, calculés sur les features de ce même vecteur, puis applique une échelle (`gamma`) et un décalage (`beta`) appris pour que le réseau puisse encore représenter une plage utile au lieu d'être coincé à une moyenne de 0 et une variance de 1. Elle diffère de la **batch normalization**, qui normalise au contraire sur la dimension du batch, en calculant ses statistiques à partir de nombreux exemples ensemble. Le calcul par exemple de la layer norm compte précisément pour les modèles de séquences : elle fonctionne de façon identique quelle que soit la taille du batch, y compris un batch d'un seul exemple, ce qui est exactement le cas pendant la génération autorégressive, où des statistiques de batch calculées sur une seule séquence générée seraient dénuées de sens ou instables.

L'effet pratique : la layer norm garde l'entrée de chaque sous-couche dans une plage numérique semblable et prévisible, de sorte qu'une sous-couche située au fond d'une pile de nombreux blocs ne reçoit pas des échelles d'activation très différentes de celles d'une sous-couche proche de l'entrée, ce qui stabilise l'entraînement comme le facteur d'échelle de la leçon 1 gardait les scores d'attention dans une plage où le gradient du softmax restait exploitable.

### Où se place la norme : post-norm contre pre-norm

L'article du transformer d'origine place la layer norm *après* l'addition résiduelle, `LayerNorm(x + Sublayer(x))`, ce qu'on appelle **post-norm**. Des travaux ultérieurs ont montré que placer la norme *avant* la sous-couche, à l'intérieur de la branche résiduelle, `x + Sublayer(LayerNorm(x))`, ce qu'on appelle **pre-norm**, s'entraîne de façon plus stable quand les modèles deviennent bien plus profonds. La raison : le pre-norm laisse le chemin résiduel lui-même parfaitement propre et non normalisé d'un bout à l'autre du réseau, une connexion identité sans obstacle de bout en bout, alors que le placement du post-norm fait que la somme résiduelle elle-même est normalisée à chaque couche, ce qui brouille cette autoroute propre du gradient. C'est pourquoi la plupart des grands modèles actuels utilisent le pre-norm, malgré le choix du post-norm dans l'article d'origine.

![Deux schémas côte à côte d'une branche résiduelle. À gauche, post-norm : x se divise en une ligne de contournement et une ligne qui traverse la sous-couche, les deux sont additionnées, et cette somme passe par la layer norm, si bien que le chemin résiduel lui-même est normalisé à chaque couche. À droite, pre-norm : x se divise en une ligne de contournement et une ligne qui passe par la layer norm avant la sous-couche, les deux sont additionnées, et la sortie est utilisée directement sans autre normalisation, si bien que le chemin résiduel qui descend de haut en bas reste entièrement propre et sans obstacle de bout en bout.](images/pre-norm-vs-post-norm.svg)

## Pratique

1. ▢ Pourquoi une connexion résiduelle aide-t-elle à entraîner une pile profonde de blocs transformer, du point de vue de ce qui arrive aux gradients pendant la rétropropagation ?

<details markdown="1"><summary>Vérifier</summary>

Sans connexion résiduelle, un gradient qui remonte doit traverser la transformation de chaque sous-couche à chaque couche empilée, ce qui peut le faire diminuer ou exploser sur de nombreuses couches. Le terme `+ x` de la connexion résiduelle donne au gradient une seconde voie directe à travers la connexion identité à chaque couche, ce qui garde un signal exploitable jusqu'aux toutes premières couches, quoi que la transformation de chaque sous-couche lui fasse.

</details>

2. ▢ Pourquoi le choix de la layer norm de normaliser sur la dimension des features, plutôt que sur la dimension du batch comme la batch norm, compte-t-il précisément pour un modèle de séquences qui fait de la génération autorégressive ?

<details markdown="1"><summary>Vérifier</summary>

La génération autorégressive s'exécute couramment avec un petit batch, souvent de taille 1. La batch normalization calcule ses statistiques sur la dimension du batch, ce qui n'a aucun sens ou est instable avec si peu d'exemples (ou un seul) pour calculer des statistiques. La layer norm calcule ses statistiques à partir des features d'un seul exemple, donc elle fonctionne de façon identique quelle que soit la taille du batch, grande ou petite.

</details>

3. ▢ Comparez le placement post-norm et le placement pre-norm, et expliquez pourquoi le pre-norm est généralement préféré pour les modèles très profonds.

<details markdown="1"><summary>Indice</summary>

Pensez au placement qui garde le chemin résiduel lui-même entièrement non normalisé de bout en bout.

</details>

<details markdown="1"><summary>Vérifier</summary>

Le post-norm applique la layer norm après l'ajout du résiduel, `LayerNorm(x + Sublayer(x))` ; le pre-norm l'applique avant la sous-couche, à l'intérieur de la branche résiduelle, `x + Sublayer(LayerNorm(x))`. Le pre-norm laisse le chemin résiduel lui-même parfaitement propre et non normalisé d'un bout à l'autre du réseau, une connexion identité sans obstacle de bout en bout, alors que le placement du post-norm normalise la somme résiduelle à chaque couche et perturbe ce chemin de gradient propre. C'est pourquoi le pre-norm s'entraîne de façon plus stable quand la profondeur augmente.

</details>

4. ▢ Un vecteur d'activation de longueur 4 vaut `[2, 4, 4, 6]`. Calculez sa moyenne et sa variance, puis la sortie normalisée de la layer norm (avant échelle et décalage).

<details markdown="1"><summary>Indice</summary>

La moyenne est la moyenne arithmétique ; la variance est la moyenne des carrés des écarts à la moyenne.

</details>

<details markdown="1"><summary>Vérifier</summary>

Moyenne : `(2+4+4+6)/4 = 4`. Écarts à la moyenne : `-2, 0, 0, 2`. Variance : `(4+0+0+4)/4 = 2`. Écart type : `sqrt(2) ≈ 1.414`. Normalisé : `[-2, 0, 0, 2] / 1.414 ≈ [-1.414, 0, 0, 1.414]`, avant l'application de l'échelle (`gamma`) et du décalage (`beta`) appris.

</details>

5. ▢ Quelle affirmation est vraie des connexions résiduelles et de la layer normalization dans un bloc transformer ?

    - a) Les connexions résiduelles rendent la layer normalization entièrement inutile
    - b) La layer norm normalise toujours sur la dimension du batch, comme la batch norm
    - c) Les connexions résiduelles donnent aux gradients un chemin direct à travers une pile profonde, et la layer norm garde les activations de chaque couche dans une plage stable et prévisible, indépendamment de la taille du batch
    - d) Le placement pre-norm ou post-norm n'a aucun effet sur la stabilité de l'entraînement, quelle que soit la profondeur

<details markdown="1"><summary>Vérifier</summary>

**c)** Chaque pièce résout un problème distinct : les connexions résiduelles traitent la circulation du gradient à travers la profondeur, la layer norm traite l'échelle des activations indépendamment de la taille du batch. (a) est faux : elles résolvent des problèmes différents et apparaissent ensemble dans un bloc standard. (b) est faux : c'est précisément ce qui distingue la layer norm de la batch norm. (d) est faux : l'avantage du pre-norm sur le post-norm apparaît précisément quand les modèles deviennent plus profonds.

</details>

## Exercices en situation réelle

- [ ] Implémentez la layer normalization à partir d'opérations brutes sur les tenseurs (moyenne, variance, normalisation, échelle et décalage appris) pour un petit vecteur d'activation, et vérifiez qu'elle correspond à un calcul à la main comme l'exemple travaillé de cette leçon.
- [ ] Enveloppez votre implémentation de l'attention des leçons 1 à 3 dans une connexion résiduelle et une layer norm, en choisissant le placement pre-norm ou post-norm, et notez lequel vous avez choisi et pourquoi.
- [ ] Demain : lisez le résumé et l'introduction de l'article « Layer Normalization », et notez quel problème de la batch normalization pour les modèles de séquences il a été écrit à l'origine pour résoudre.

## Pour aller plus loin

- [Article : "Layer Normalization", Ba, Kiros et Hinton, 2016](https://arxiv.org/abs/1607.06450)
- [Article : "On Layer Normalization in the Transformer Architecture", Xiong et al., 2020](https://arxiv.org/abs/2002.04745)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
