---
title: "7. Parallélisme de données et all-reduce des gradients"
description: "Répartir un batch entre des appareils qui détiennent chacun une copie complète du modèle, et ce qui garde chaque copie identique"
type: lesson
---

# Leçon 7. Parallélisme de données et all-reduce des gradients

**Lien avec la mission :** « Expliquer ce que ZeRO/FSDP partitionnent, pourquoi le parallélisme de données seul manque de mémoire avant de manquer de calcul, et quand le parallélisme tensoriel ou de pipeline vaut son coût de communication » est le quatrième point sous Objectif. Cette leçon couvre ce qu'est le parallélisme de données et comment il reste correct ; la leçon 8 couvre pourquoi il manque de mémoire.
**Source primaire :** [Article : "ZeRO: Memory Optimizations Toward Training Trillion Parameter Models", Rajbhandari et al., 2019](https://arxiv.org/abs/1910.02054)
**Prérequis :** [Leçon 6](0006-chinchilla-the-compute-optimal-correction.md)

## Échauffement

1. ▢ En utilisant `FLOPs(N, D) ≈ 6ND`, combien de tokens un budget de calcul de `6 × 10^21` FLOPs permet-il environ pour un modèle de 5 milliards de paramètres ?

<details markdown="1"><summary>Vérifier</summary>

200 milliards de tokens : `6 × 10^21 / (6 × 5 × 10^9) = 2 × 10^11`.

</details>

## À savoir

### Découper le batch, pas le modèle

Le **parallélisme de données** est la manière la plus simple de mettre plus d'un appareil au travail sur le même run d'entraînement : chaque appareil détient une copie complète et identique du modèle, et un seul grand batch est découpé en morceaux plus petits par appareil, un par appareil. Chaque appareil exécute sa propre passe avant et arrière sur son propre morceau, entièrement indépendamment des autres, en calculant son propre gradient local.

### Garder chaque copie identique

Si chaque appareil se contentait d'appliquer son propre gradient local à sa propre copie des poids, les copies divergeraient dès le premier pas, et « N appareils entraînant un modèle » deviendrait sans bruit « N appareils entraînant N modèles différents ». Le parallélisme de données l'évite par une étape de synchronisation avant l'exécution de l'optimizer : le gradient local de chaque appareil est moyenné avec celui de tous les autres, via une opération de communication collective appelée **all-reduce**, et chaque appareil reçoit en retour le même gradient moyenné. Comme chaque appareil applique alors le même gradient moyenné à une copie de départ identique des poids, toutes les copies restent identiques après le pas de l'optimizer, pas après pas, sans jamais avoir à comparer les poids eux-mêmes.

Une manière courante de l'implémenter efficacement est un **ring all-reduce** : les appareils sont disposés en anneau logique, et chacun n'échange jamais de données qu'avec ses deux voisins, selon une suite d'étapes qui garantit que chaque appareil finit avec la somme complète (puis la moyenne) sans jamais avoir besoin qu'un appareil collecte directement tout de la part de tous les autres. Cela garde le volume de communication par appareil à peu près constant quand on ajoute des appareils, au lieu de croître avec leur nombre, ce qui est précisément ce qui permet au parallélisme de données de passer raisonnablement bien à l'échelle.

### Ce que cela apporte, et ce que cela ne touche pas

Tout le bénéfice du parallélisme de données est le débit : avec `k` appareils, on peut traiter `k` fois plus de données par unité de temps réel, puisque chaque appareil fait un travail indépendant sur sa propre tranche du batch. Rien de tout cela ne change la quantité de mémoire dont un appareil donné a besoin. Chaque appareil détient toujours une copie complète des paramètres du modèle, de ses gradients et de son état d'optimizer, exactement comme s'il s'entraînait seul ; ajouter des appareils en parallélisme de données ajoute davantage de copies de la même empreinte mémoire, et non moins de mémoire par appareil. Le parallélisme de données est une manière de traiter plus vite davantage de l'entraînement d'un modèle de taille fixe ; à lui seul, il ne permet pas de faire tenir un modèle plus grand que ce qu'un seul appareil pourrait contenir. La leçon 8 rend cette limite concrète.

## Pratique

1. ▢ Quatre appareils entraînent un modèle en parallélisme de données. L'appareil 3 calcule un gradient local qui se trouve être anormalement grand par rapport aux gradients des trois autres appareils à ce pas, à cause de ce qui se trouvait dans sa tranche du batch. Qu'est-ce qui empêche la copie des poids de l'appareil 3 de s'écarter de celle des trois autres ?

<details markdown="1"><summary>Vérifier</summary>

L'étape d'all-reduce. Le gradient local de chaque appareil, y compris celui, anormalement grand, de l'appareil 3, est moyenné avec celui des quatre appareils avant qu'aucun appareil n'applique une mise à jour, si bien que chaque appareil applique le même gradient moyenné à une copie de départ identique des poids, ce qui garde les quatre copies identiques.

</details>

2. ▢ Laquelle de ces affirmations décrit le mieux ce que l'ajout d'appareils en parallélisme de données change à un run d'entraînement ?

    - a) Il réduit la quantité de mémoire dont chaque appareil a besoin pour contenir le modèle
    - b) Il permet de traiter une plus grande part du batch par unité de temps, sans changer la quantité de mémoire dont un appareil donné a besoin
    - c) Il supprime entièrement le besoin d'un pas d'optimizer
    - d) Il augmente automatiquement le nombre de paramètres du modèle

<details markdown="1"><summary>Indice</summary>

Demandez-vous ce qui est réellement réparti entre les appareils en parallélisme de données : le modèle, ou le batch ?

</details>

<details markdown="1"><summary>Vérifier</summary>

**b)** Le parallélisme de données découpe le batch, pas le modèle, si bien que le débit croît avec le nombre d'appareils alors que la mémoire par appareil ne diminue pas. (a) est exactement à l'envers, ce que la leçon 8 rend concret. (c) et (d) décrivent des changements que le parallélisme de données ne fait pas du tout.

</details>

3. ▢ Dans un ring all-reduce, pourquoi chaque appareil ne communique-t-il jamais qu'avec ses deux voisins dans l'anneau, plutôt que chaque appareil envoie son gradient directement à tous les autres ?

<details markdown="1"><summary>Vérifier</summary>

Pour que le volume de communication qu'un appareil donné doit gérer reste à peu près constant quand davantage d'appareils rejoignent l'anneau, au lieu de croître avec le nombre d'appareils, ce qui permet à cette approche de passer à l'échelle sur de nombreux appareils sans que la communication elle-même devienne le goulot d'étranglement.

</details>

## Exercices en situation réelle

- [ ] Trouvez la documentation d'une API d'entraînement en parallélisme de données à laquelle vous avez accès (le `DistributedDataParallel` de PyTorch en est une courante) et repérez où elle décrit l'étape de synchronisation des gradients. Notez comment elle nomme l'opération, et si la description correspond à « all-reduce » tel que cette leçon le décrit.
- [ ] Esquissez sur le papier quatre appareils disposés en anneau, et suivez à la main ce qu'un appareil donné envoie et reçoit dans un ring all-reduce sur quelques pas, avec un vecteur de gradient jouet de 4 nombres, réparti à raison d'un nombre par appareil.
- [ ] Demain : sans regarder la suite, écrivez une prédiction d'une phrase pour la leçon 8 : si chaque appareil en parallélisme de données doit détenir une copie complète des paramètres du modèle, de ses gradients et de son état d'optimizer, que se passe-t-il quand le modèle grossit alors que le nombre d'appareils reste fixe ?

## Pour aller plus loin

- [Article : "ZeRO: Memory Optimizations Toward Training Trillion Parameter Models", Rajbhandari et al., 2019](https://arxiv.org/abs/1910.02054)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
