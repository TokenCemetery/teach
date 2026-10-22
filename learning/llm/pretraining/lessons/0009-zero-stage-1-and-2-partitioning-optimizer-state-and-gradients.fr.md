---
title: "9. ZeRO stage 1 et 2 : partitionner l'état de l'optimizer et les gradients"
description: "Supprimer gratuitement les copies redondantes du parallélisme de données, avant même que le coût de communication ait à croître"
type: lesson
---

# Leçon 9. ZeRO stage 1 et 2 : partitionner l'état de l'optimizer et les gradients

**Lien avec la mission :** « Expliquer ce que ZeRO/FSDP partitionnent, pourquoi le parallélisme de données seul manque de mémoire avant de manquer de calcul, et quand le parallélisme tensoriel ou de pipeline vaut son coût de communication » est le quatrième point sous Objectif. Cette leçon couvre les deux premiers des trois stages de ZeRO ; la leçon 10 couvre le troisième.
**Source primaire :** [Article : "ZeRO: Memory Optimizations Toward Training Trillion Parameter Models", Rajbhandari et al., 2019](https://arxiv.org/abs/1910.02054)
**Prérequis :** [Leçon 8](0008-why-data-parallelism-alone-runs-out-of-memory.md)

## Échauffement

1. ▢ Avec Adam en précision mixte, quels sont les cinq coûts mémoire par paramètre qui s'additionnent pour faire 16 octets par paramètre ?

<details markdown="1"><summary>Vérifier</summary>

Une copie fp16 des paramètres (2 octets), une copie fp16 des gradients (2 octets), et une copie fp32 chacune des paramètres, du moment et de la variance conservées par l'optimizer (4 octets chacune), soit 16 octets au total.

</details>

2. ▢ Le parallélisme de données ordinaire réduit-il l'un de ces 16 octets par appareil quand on ajoute des appareils ?

<details markdown="1"><summary>Vérifier</summary>

Non. Chaque appareil détient 16 octets complets et identiques par paramètre quel que soit le nombre d'autres appareils ; ajouter des appareils ajoute davantage de copies redondantes, et non une empreinte plus petite par appareil.

</details>

## À savoir

### La redondance que ZeRO supprime

La leçon 8 a établi que chaque appareil en parallélisme de données détient une copie complète et identique de l'état d'optimizer, des gradients et des paramètres. L'idée centrale de ZeRO est que cette redondance est inutile : sur `Nd` appareils en parallélisme de données, il suffit qu'une seule copie complète de cet état existe au total, découpée en `Nd` morceaux, un morceau par appareil, chaque appareil reconstruisant ou recevant le morceau qu'il ne détient pas uniquement au moment où il en a réellement besoin. Rajbhandari et al. appellent cela ZeRO-DP, et le définissent comme trois stages activables de façon cumulative, chacun partitionnant un morceau de plus des états du modèle que le précédent.

### Stage 1 : partitionner l'état de l'optimizer

**`P_os`** (partitionnement de l'état de l'optimizer) ne répartit que l'état de l'optimizer, la plus grande part des 16 octets par paramètre (la copie fp32 des paramètres, le moment et la variance : 12 des 16 octets), entre les `Nd` appareils, si bien que chaque appareil n'en détient que `1/Nd` au lieu de la totalité. Rajbhandari et al. rapportent que cela seul donne une réduction de mémoire de 4x, au **même volume de communication que le parallélisme de données ordinaire** : aucune donnée supplémentaire n'a à circuler entre appareils au-delà de ce que l'all-reduce des gradients exigeait déjà, parce que l'état de l'optimizer n'est jamais nécessaire qu'en local, au moment où chaque appareil applique sa propre tranche de la mise à jour.

### Stage 2 : partitionner aussi les gradients

**`P_os+g`** ajoute le partitionnement des gradients par-dessus le stage 1 : chaque appareil ne conserve que la tranche du gradient dont il a besoin pour mettre à jour sa propre tranche de l'état d'optimizer et des paramètres, au lieu de détenir le gradient complet de chaque paramètre du modèle. C'est une extension naturelle de la même idée, puisqu'un appareil qui ne possède que `1/Nd` de l'état d'optimizer n'a besoin que de `1/Nd` du gradient pour le mettre à jour. Rajbhandari et al. rapportent que cela atteint une réduction de mémoire de 8x, de nouveau au **même volume de communication que le parallélisme de données ordinaire** : les opérations reduce-scatter et all-gather en lesquelles cela restructure l'all-reduce déplacent la même quantité totale de données qu'un all-reduce standard, simplement adressées à l'appareil qui a réellement besoin de chaque tranche au lieu de diffuser le tout à tout le monde.

### Pourquoi ces deux stages sont presque un repas gratuit

Les deux stages suppriment une vraie redondance de mémoire sans ajouter de coût de communication au-delà de ce que le parallélisme de données payait déjà. C'est possible parce que l'état d'optimizer et les gradients ne sont jamais nécessaires qu'à l'appareil chargé de mettre à jour la tranche de paramètres correspondante ; rien d'autre dans la passe avant ou arrière n'a besoin de les lire. Le stage 3, qui partitionne les paramètres eux-mêmes, ne peut pas revendiquer la même chose, parce que la passe avant et arrière de chaque appareil a besoin de chaque paramètre, pas seulement de ceux qu'il possède. La leçon 10 couvre ce que cela coûte.

## Pratique

1. ▢ Un modèle de 7 milliards de paramètres est entraîné avec ZeRO stage 1 (`P_os`) sur 8 appareils en parallélisme de données. Combien d'octets par paramètre chaque appareil détient-il maintenant environ pour l'état d'optimizer, par rapport aux 12 octets par paramètre (paramètres fp32, moment, variance) qu'il détiendrait sans partitionnement ?

<details markdown="1"><summary>Indice</summary>

Le stage 1 répartit l'état de l'optimizer à parts égales entre les `Nd` appareils.

</details>

<details markdown="1"><summary>Vérifier</summary>

1,5 octet par paramètre (`12 / 8`), contre les 12 octets complets que chaque appareil détiendrait autrement. Les paramètres fp16 et les gradients fp16 (4 octets au total) ne sont pas affectés par le stage 1 seul.

</details>

2. ▢ Laquelle de ces affirmations décrit le mieux pourquoi les stages 1 et 2 de ZeRO n'augmentent pas le volume de communication au-delà du parallélisme de données ordinaire ?

    - a) Ils sautent entièrement l'étape de synchronisation des gradients
    - b) L'état d'optimizer et les gradients ne sont jamais nécessaires qu'en local, à l'appareil chargé de la tranche correspondante, si bien que restructurer qui détient quoi n'exige pas de déplacer davantage de données au total
    - c) Ils ne fonctionnent que sur de petits modèles, où le coût de communication n'a pas d'importance
    - d) Ils compressent les gradients avant de les envoyer, en échangeant de la précision contre de la bande passante

<details markdown="1"><summary>Vérifier</summary>

**b)** est le mécanisme réel : aucun appareil n'a besoin de la tranche d'état d'optimizer ou de gradient d'un autre appareil pendant la passe avant ou arrière, seulement à sa propre étape de mise à jour. (a) est faux ; la synchronisation a toujours lieu, simplement remodelée en reduce-scatter et all-gather. (c) et (d) décrivent des mécanismes que ces deux stages n'utilisent pas.

</details>

3. ▢ Une équipe veut la plus grande réduction de mémoire que ZeRO peut offrir sans aucune augmentation du volume de communication par rapport au parallélisme de données ordinaire. Quel stage doit-elle utiliser, et quelle réduction de mémoire donne-t-il ?

<details markdown="1"><summary>Vérifier</summary>

Le stage 2 (`P_os+g`), qui donne une réduction de mémoire de 8x au même volume de communication que le parallélisme de données ordinaire. Le stage 3 va plus loin sur la mémoire mais c'est celui pour lequel Rajbhandari et al. rapportent une augmentation du volume de communication.

</details>

## Exercices en situation réelle

- [ ] Trouvez la documentation de la configuration ZeRO ou FSDP d'un framework d'entraînement (les stratégies de partitionnement de PyTorch FSDP, ou les réglages de stage ZeRO de DeepSpeed) et identifiez quelle option de configuration correspond au stage 1 et laquelle au stage 2.
- [ ] En utilisant la décomposition à 16 octets par paramètre, calculez la mémoire par appareil pour les états du modèle d'un modèle de 13 milliards de paramètres sous le stage 2, sur 8 appareils, et comparez-la au même modèle sans aucun partitionnement ZeRO.
- [ ] Demain : sans regarder la suite, écrivez une prédiction d'une phrase pour la leçon 10 : si la passe avant et arrière de chaque appareil a besoin de chaque paramètre, pas seulement de ceux qu'il possède, que devrait faire différemment un appareil qui partitionne les paramètres eux-mêmes par rapport à ce que font les stages 1 et 2 ?

## Pour aller plus loin

- [Article : "ZeRO: Memory Optimizations Toward Training Trillion Parameter Models", Rajbhandari et al., 2019](https://arxiv.org/abs/1910.02054)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
