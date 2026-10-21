---
title: "8. Pourquoi le parallélisme de données seul manque de mémoire"
description: "Compter exactement ce qu'un optimizer Adam en précision mixte détient par paramètre, et où cela se heurte à un mur"
type: lesson
---

# Leçon 8. Pourquoi le parallélisme de données seul manque de mémoire

**Lien avec la mission :** « Expliquer ce que ZeRO/FSDP partitionnent, pourquoi le parallélisme de données seul manque de mémoire avant de manquer de calcul, et quand le parallélisme tensoriel ou de pipeline vaut son coût de communication » est le quatrième point sous Objectif. La leçon 7 a couvert la manière dont le parallélisme de données garde identique la copie de chaque appareil ; cette leçon compte exactement ce que coûte « chaque appareil détient une copie complète », et où cela casse.
**Source primaire :** [Article : "ZeRO: Memory Optimizations Toward Training Trillion Parameter Models", Rajbhandari et al., 2019](https://arxiv.org/abs/1910.02054)
**Prérequis :** [Leçon 7](0007-data-parallelism-and-gradient-all-reduce.md)

## Échauffement

1. ▢ En parallélisme de données, quelle opération garde identique la copie du modèle de chaque appareil après chaque pas de l'optimizer ?

<details markdown="1"><summary>Vérifier</summary>

L'all-reduce : le gradient local de chaque appareil est moyenné avec celui de tous les appareils avant qu'aucun appareil n'applique une mise à jour, si bien que chaque appareil applique le même gradient moyenné à une copie de départ identique des poids.

</details>

2. ▢ Ajouter des appareils en parallélisme de données réduit-il la mémoire dont un appareil donné a besoin pour contenir le modèle ? Pourquoi ou pourquoi pas ?

<details markdown="1"><summary>Vérifier</summary>

Non. Chaque appareil détient toujours une copie complète des paramètres, des gradients et de l'état d'optimizer, exactement comme s'il s'entraînait seul ; davantage d'appareils signifie davantage de copies de cette même empreinte, et non une empreinte plus petite par appareil.

</details>

## À savoir

### Ce que contient réellement « une copie complète du modèle »

La leçon 7 a dit que chaque appareil en parallélisme de données détient une copie complète des paramètres, des gradients et de l'état d'optimizer, sans compter ce que cela coûte. L'entraînement en précision mixte, l'approche standard pour entraîner de grands modèles, rend le décompte concret. Avec Adam comme optimizer, Rajbhandari et al. comptent, par paramètre (`Ψ` désigne le nombre de paramètres) :

- une copie `fp16` des paramètres, utilisée pour les passes avant et arrière : 2 octets par paramètre
- une copie `fp16` des gradients : 2 octets par paramètre
- une copie `fp32` des paramètres, conservée par l'optimizer pour des mises à jour numériquement stables : 4 octets par paramètre
- une copie `fp32` du moment d'Adam : 4 octets par paramètre
- une copie `fp32` de la variance d'Adam : 4 octets par paramètre

Cela fait un total de 16 octets par paramètre, dont chaque appareil en parallélisme de données détient une copie complète, quel que soit le nombre d'autres appareils qui en détiennent aussi une copie identique.

### Où cela se heurte à un mur

Pour un modèle de 1,5 milliard de paramètres (la taille de GPT-2), 16 octets par paramètre font 24 Go rien que pour ces états du modèle, bien au-dessus des 3 Go qu'il faudrait pour contenir seulement les paramètres `fp16` seuls, et cela avant de compter les activations (les valeurs intermédiaires conservées de la passe avant pour calculer les gradients dans la passe arrière), que Rajbhandari et al. estiment séparément à environ 60 Go pour ce même modèle avec une longueur de séquence de 1 024 et une taille de batch de 32. Rajbhandari et al. énoncent directement la limite qui en résulte : « le parallélisme de données de base ne réduit pas la mémoire par appareil, et manque de mémoire pour les modèles de plus de 1,4 milliard de paramètres sur la génération actuelle de GPU avec 32 Go de mémoire. » Un GPU de 32 Go a manqué de place avant d'avoir manqué de quoi que ce soit d'autre, sur un modèle à peine plus grand que GPT-2, en utilisant chacun des nombreux appareils que le parallélisme de données peut ajouter.

### La forme de la solution

Chaque appareil du parallélisme de données ordinaire détient une copie identique et entièrement redondante des mêmes 16Ψ octets d'états du modèle. Cette redondance est exactement ce qu'une autre stratégie peut supprimer : au lieu que chaque appareil détienne tout, chacun pourrait ne détenir que sa propre tranche des états du modèle, en reconstruisant ou en communiquant ce qu'il ne détient pas, uniquement quand c'est réellement nécessaire à un calcul. C'est l'idée que l'étape 5 reprend directement, sous le nom de ZeRO.

## Pratique

1. ▢ En utilisant la décomposition à 16 octets par paramètre, de quelle quantité de mémoire les états du modèle seuls auraient-ils besoin pour un modèle de 7 milliards de paramètres entraîné en précision mixte avec Adam ?

<details markdown="1"><summary>Indice</summary>

Multipliez le nombre de paramètres par 16 octets, puis convertissez les octets en gigaoctets.

</details>

<details markdown="1"><summary>Vérifier</summary>

Environ 112 Go (`7 × 10^9 × 16` octets ≈ `1.12 × 10^11` octets ≈ 112 Go). Ce sont les états du modèle seuls, bien au-delà d'un seul GPU de 32 Go, voire de 80 Go, avant même de compter les activations.

</details>

2. ▢ Laquelle de ces affirmations explique le mieux pourquoi le parallélisme de données seul ne peut pas faire tenir un modèle arbitrairement grand, quel que soit le nombre d'appareils ajoutés ?

    - a) La bande passante de communication entre appareils finit par saturer
    - b) Chaque appareil détient une copie complète et redondante du même coût mémoire par paramètre, si bien qu'ajouter des appareils ajoute davantage de copies au lieu de réduire le besoin d'un appareil donné
    - c) L'opération d'all-reduce elle-même consomme une quantité de mémoire proportionnelle à la taille du modèle
    - d) Les modèles plus grands produisent toujours de plus grands gradients, qui débordent la représentation fp16

<details markdown="1"><summary>Vérifier</summary>

**b)** est la vraie limite que cette leçon retrace, directement à partir de l'empreinte mémoire redondante par appareil. (a) est une vraie préoccupation de l'entraînement distribué mais c'est un coût en temps de communication, pas le mur de capacité mémoire dont parle cette leçon. (c) et (d) ne sont pas le mécanisme que les auteurs de ZeRO identifient.

</details>

3. ▢ Rajbhandari et al. indiquent que le parallélisme de données de base manque de mémoire pour les modèles de plus de 1,4 milliard de paramètres sur des GPU de 32 Go de mémoire. D'après la décomposition à 16 octets par paramètre, de combien de mémoire les seuls états d'un modèle de 1,4 milliard de paramètres auraient-ils besoin environ, et comment cela se compare-t-il au chiffre de 32 Go une fois les activations ajoutées ?

<details markdown="1"><summary>Vérifier</summary>

Environ 22,4 Go pour les états du modèle seuls (`1.4 × 10^9 × 16` octets ≈ `2.24 × 10^10` octets). Cela laisse déjà moins de 10 Go d'un GPU de 32 Go pour les activations, que l'exemple GPT-2 de la leçon situait à environ 60 Go pour une longueur de séquence et une taille de batch modestes, bien au-delà de ce qui reste.

</details>

## Exercices en situation réelle

- [ ] Prenez le nombre de paramètres d'un modèle ouvert publié et, avec la formule à 16 octets par paramètre, estimez son besoin en mémoire pour les états du modèle sous Adam en précision mixte. Comparez cette estimation aux tailles de mémoire de GPU couramment utilisées pour l'entraînement (24, 40 et 80 Go sont des chiffres typiques auxquels comparer).
- [ ] Lisez le paragraphe de l'article ZeRO (lié plus haut) qui décrit la mémoire résiduelle (activations, tampons temporaires, fragmentation de la mémoire) et écrivez une phrase qui la distingue de la mémoire des états du modèle que cette leçon a comptée.
- [ ] Demain : sans regarder la suite, écrivez une prédiction d'une phrase pour l'étape 5 : si le problème est que chaque appareil détient une copie complète et redondante des mêmes 16Ψ octets, que devrait faire à la place une solution qui supprime la redondance, et que devrait-elle communiquer pour compenser le fait de ne plus tout détenir localement ?

## Pour aller plus loin

- [Article : "ZeRO: Memory Optimizations Toward Training Trillion Parameter Models", Rajbhandari et al., 2019](https://arxiv.org/abs/1910.02054)
- [Ressources](../RESOURCES.md)

---

L'étape 4 a établi que c'est la redondance du parallélisme de données, et non son calcul, qui s'épuise en premier. L'étape 5 la reprend directement : ce que ZeRO et FSDP partitionnent réellement pour la supprimer.

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
