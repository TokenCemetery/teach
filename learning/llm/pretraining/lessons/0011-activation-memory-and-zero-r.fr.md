---
title: "11. Mémoire des activations et ZeRO-R"
description: "Partitionner les états du modèle résout un problème de mémoire et en laisse un second debout : les activations"
type: lesson
---

# Leçon 11. Mémoire des activations et ZeRO-R

**Lien avec la mission :** « Expliquer ce que ZeRO/FSDP partitionnent, pourquoi le parallélisme de données seul manque de mémoire avant de manquer de calcul, et quand le parallélisme tensoriel ou de pipeline vaut son coût de communication » est le quatrième point sous Objectif. Les leçons 9 et 10 ont couvert les trois stages de ZeRO-DP, qui partitionnent les états du modèle ; cette leçon couvre le problème de mémoire distinct que ces trois stages ne touchent pas.
**Source primaire :** [Article : "ZeRO: Memory Optimizations Toward Training Trillion Parameter Models", Rajbhandari et al., 2019](https://arxiv.org/abs/1910.02054)
**Prérequis :** [Leçon 10](0010-zero-stage-3-and-fsdp-partitioning-parameters-too.md), [Activation checkpointing](../GLOSSARY.md)

## Échauffement

1. ▢ La documentation FSDP de PyTorch se décrit comme inspirée de quel stage ZeRO ?

<details markdown="1"><summary>Vérifier</summary>

ZeRO stage 3 (`P_os+g+p`), le stage qui partitionne les paramètres en plus de l'état d'optimizer et des gradients.

</details>

2. ▢ Pourquoi partitionner les paramètres (stage 3) ajoute-t-il de la communication que le partitionnement de l'état d'optimizer et des gradients (stages 1 et 2) n'ajoute pas ?

<details markdown="1"><summary>Vérifier</summary>

Parce que la passe avant et arrière de chaque appareil a besoin de chaque paramètre, pas seulement de la tranche qu'il possède, si bien que les tranches manquantes doivent être rassemblées depuis d'autres appareils à la demande, contrairement à l'état d'optimizer et aux gradients, dont seul l'appareil propriétaire a jamais besoin.

</details>

## À savoir

### Résoudre les états du modèle laisse un second problème debout

Les leçons 9 et 10 ont couvert **ZeRO-DP** : les trois stages qui partitionnent l'état d'optimizer, les gradients et les paramètres, les 16 octets par paramètre que la leçon 8 a comptés. Rajbhandari et al. sont explicites : ce n'est pas tout le tableau de la mémoire. Quand les états du modèle cessent de dominer, ce qu'ils appellent la **mémoire résiduelle**, c'est-à-dire les activations conservées de la passe avant pour calculer les gradients dans la passe arrière, les tampons temporaires et la mémoire perdue à cause de la fragmentation, devient le goulot d'étranglement suivant. L'exemple GPT-2 de la leçon 8 a montré que l'effet n'est pas petit : environ 60 Go de mémoire d'activations à une longueur de séquence de 1 024 et une taille de batch de 32, sur un modèle dont les seuls états du modèle ne représentaient que 24 Go. Les trois stages de ZeRO-DP ne font rien contre ces 60 Go ; ils ne s'occupent que des 24 Go. **ZeRO-R** est la réponse distincte de Rajbhandari et al. au versant résiduel.

### L'activation checkpointing aide, mais ne suffit pas seul

L'activation checkpointing, le terme du glossaire vers lequel cette leçon renvoie, jette la plupart des activations intermédiaires pendant la passe avant et les recalcule pendant la passe arrière au lieu de toutes les garder en mémoire en permanence, en échangeant du calcul supplémentaire contre moins de mémoire. Rajbhandari et al. notent que le checkpointing aide mais ne suffit pas seul pour les plus grands modèles : même l'ensemble réduit d'activations que conserve le checkpointing peut rester grand et, dans les configurations qui combinent parallélisme de données et parallélisme de modèle, cet ensemble réduit est souvent répliqué inutilement entre des rangs en parallélisme de modèle qui pourraient plutôt le partager.

### Ce que ZeRO-R ajoute par-dessus

ZeRO-R attaque la mémoire résiduelle sur trois fronts, chacun visant une partie différente de celle-ci :

- **Le partitionnement des activations.** Là où l'entraînement en parallélisme de modèle garderait autrement une copie redondante des mêmes activations sur chaque rang en parallélisme de modèle, ZeRO-R identifie et supprime cette réplication, en partitionnant les activations comme ZeRO-DP partitionne les états du modèle, et peut en plus **délester** (offload) les activations partitionnées vers la mémoire du CPU quand cet échange en vaut la peine.
- **Des tampons temporaires de taille adaptée.** Les grands tampons temporaires utilisés pendant l'entraînement reçoivent une taille choisie délibérément, qui équilibre l'usage de la mémoire et l'efficacité du calcul, au lieu d'être laissés grossir autant qu'une implémentation naïve le permettrait.
- **La défragmentation.** Des tenseurs aux durées de vie très différentes (certains vivent un pas d'entraînement entier, d'autres seulement un instant) créent au fil du temps une mémoire fragmentée, qui peut faire échouer une allocation mémoire même quand la mémoire libre totale serait par ailleurs suffisante. ZeRO-R gère la mémoire de façon proactive d'après la durée de vie attendue de chaque tenseur, pour empêcher cette fragmentation de s'accumuler.

Combinés, Rajbhandari et al. désignent ZeRO-DP et ZeRO-R ensemble simplement par **ZeRO** : une moitié supprime la redondance des états du modèle, l'autre contrôle tout le reste de ce que l'entraînement garde en mémoire.

## Pratique

1. ▢ Une équipe a déjà appliqué ZeRO stage 3 à un modèle, ramenant la mémoire de ses états du modèle bien dans le budget, mais le run manque encore de mémoire pendant la passe avant sur une longue longueur de séquence. Est-ce plus probablement un problème d'états du modèle ou de mémoire résiduelle, et qu'est-ce qui pourrait y remédier ?

<details markdown="1"><summary>Vérifier</summary>

Un problème de mémoire résiduelle, très probablement la mémoire des activations, qui est sensible à la longueur de séquence d'une façon que les états du modèle ne le sont pas. L'activation checkpointing, le partitionnement des activations ou le délestage des activations vers le CPU sont tous des techniques de mémoire résiduelle qui pourraient y remédier ; ajouter davantage de partitionnement ZeRO-DP n'y remédierait pas, puisque les états du modèle n'étaient pas le goulot d'étranglement ici.

</details>

2. ▢ Laquelle de ces affirmations décrit le mieux pourquoi l'activation checkpointing seule est jugée insuffisante pour les plus grands modèles ?

    - a) Le checkpointing est incompatible avec ZeRO-DP et ne peut pas être utilisé avec lui
    - b) Même l'ensemble réduit d'activations que conserve le checkpointing peut rester grand, et peut être répliqué inutilement entre des rangs en parallélisme de modèle sans optimisation supplémentaire
    - c) Le checkpointing augmente l'usage de la mémoire en échange de moins de calcul
    - d) Le checkpointing ne fonctionne que pour des modèles entraînés sans précision mixte

<details markdown="1"><summary>Vérifier</summary>

**b)** est le raisonnement même de l'article. (a) est faux ; ZeRO-R est décrit comme complémentaire du checkpointing, pas comme un remplaçant qui entre en conflit avec lui. (c) inverse le vrai compromis, qui est moins de mémoire contre plus de recalcul. (d) n'est pas une contrainte que l'article décrit.

</details>

3. ▢ Nommez les trois choses que ZeRO-R optimise, et associez chacune au problème de mémoire résiduelle qu'elle vise : des activations répliquées inutilement entre rangs en parallélisme de modèle, une allocation mémoire qui échoue malgré assez de mémoire libre au total, et des tampons temporaires laissés grossir plus que nécessaire.

<details markdown="1"><summary>Vérifier</summary>

Le partitionnement des activations (et le délestage) traite les activations répliquées entre rangs en parallélisme de modèle. La défragmentation, fondée sur la durée de vie attendue de chaque tenseur, traite les échecs d'allocation dus à une mémoire fragmentée. Les tampons temporaires de taille adaptée traitent les tampons qui grossissent plus que ne le demanderait un équilibre entre mémoire et efficacité du calcul.

</details>

## Exercices en situation réelle

- [ ] Trouvez où l'activation checkpointing (parfois appelé gradient checkpointing) est exposé comme option dans un framework d'entraînement auquel vous avez accès, et notez ce qu'il coûte en calcul supplémentaire, si la documentation l'indique.
- [ ] En utilisant l'exemple de mémoire d'activations de GPT-2 de la leçon 8 (environ 60 Go à une longueur de séquence de 1 024, une taille de batch de 32), prédisez qualitativement ce qui arrive à ce chiffre si la longueur de séquence double, et vérifiez votre prédiction contre toute formule ou explication que la documentation du framework donne sur la manière dont la mémoire des activations évolue.
- [ ] Demain : pour un modèle et une configuration matérielle auxquels vous avez accès (ou une configuration hypothétique), décidez quelle technique de mémoire résiduelle (checkpointing, partitionnement des activations, délestage vers le CPU ou une combinaison) vous essaieriez en premier, et écrivez une phrase sur la raison, compte tenu de ce que chacune sacrifie.

## Pour aller plus loin

- [Article : "ZeRO: Memory Optimizations Toward Training Trillion Parameter Models", Rajbhandari et al., 2019](https://arxiv.org/abs/1910.02054)
- [Ressources](../RESOURCES.md)

---

L'étape 5 a couvert la manière dont la mémoire d'un run d'entraînement est partitionnée entre des appareils qui font tous le même genre de travail. L'étape 6 couvre un autre genre de découpage : répartir le modèle lui-même entre des appareils qui font chacun une partie différente du calcul.

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
