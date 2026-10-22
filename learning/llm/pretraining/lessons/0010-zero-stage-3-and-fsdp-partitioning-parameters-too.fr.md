---
title: "10. ZeRO stage 3 et FSDP : partitionner aussi les paramètres"
description: "Partitionner les paramètres eux-mêmes impose de les reconstruire à la demande, ce qui est le premier coût de cette approche"
type: lesson
---

# Leçon 10. ZeRO stage 3 et FSDP : partitionner aussi les paramètres

**Lien avec la mission :** « Expliquer ce que ZeRO/FSDP partitionnent, pourquoi le parallélisme de données seul manque de mémoire avant de manquer de calcul, et quand le parallélisme tensoriel ou de pipeline vaut son coût de communication » est le quatrième point sous Objectif. La leçon 9 a couvert les deux stages qui partitionnent gratuitement l'état de l'optimizer et les gradients ; cette leçon couvre le troisième, qui partitionne les paramètres eux-mêmes, et son API réelle.
**Source primaire :** [Documentation : "Fully Sharded Data Parallel", PyTorch](https://pytorch.org/docs/stable/fsdp.html)
**Prérequis :** [Leçon 9](0009-zero-stage-1-and-2-partitioning-optimizer-state-and-gradients.md)

## Échauffement

1. ▢ Quelle réduction de mémoire ZeRO stage 2 (`P_os+g`) donne-t-il, et à quel coût de communication par rapport au parallélisme de données ordinaire ?

<details markdown="1"><summary>Vérifier</summary>

Une réduction de mémoire de 8x, au même volume de communication que le parallélisme de données ordinaire : aucune donnée supplémentaire n'a à circuler, puisque l'état d'optimizer et les gradients ne sont jamais nécessaires qu'en local, à l'appareil chargé de la tranche correspondante.

</details>

2. ▢ Pourquoi l'état d'optimizer et les gradients peuvent-ils être partitionnés sans communication supplémentaire, d'une manière que le sujet de cette leçon ne permet pas ?

<details markdown="1"><summary>Vérifier</summary>

Parce que seul l'appareil chargé d'une tranche donnée des paramètres a jamais besoin de l'état d'optimizer ou du gradient de cette tranche. La passe avant et arrière de chaque appareil, en revanche, a besoin de chaque paramètre du modèle, pas seulement de ceux qu'il possède, ce dont la leçon 10 doit rendre compte.

</details>

## À savoir

### La dernière pièce : partitionner les paramètres

**`P_os+g+p`**, le troisième stage de ZeRO, partitionne les paramètres eux-mêmes en plus de l'état d'optimizer et des gradients que le stage 2 partitionne déjà : chaque appareil ne stocke au repos que `1/Nd` des paramètres, au lieu d'une copie complète. Rajbhandari et al. rapportent que la réduction de mémoire de ce stage croît linéairement avec le degré de parallélisme de données `Nd` : répartir sur 64 appareils donne une réduction de mémoire de 64x, et c'est ce qui fait fonctionner leur résultat phare : ils estiment qu'un modèle de mille milliards de paramètres sous Adam en précision mixte a besoin d'environ 16 téraoctets pour ses états du modèle, ce qui, divisé sur 1 024 GPU, revient à environ 16 Go par appareil, confortablement dans un GPU de 32 Go.

Cette réduction n'est pas gratuite comme l'étaient les stages 1 et 2. La passe avant et arrière de chaque appareil a toujours besoin de chaque paramètre, pas seulement des `1/Nd` qu'il stocke, si bien que les paramètres qu'un appareil ne détient pas doivent être reconstruits à partir des autres appareils au moment où ils sont nécessaires, puis écartés de nouveau une fois ce calcul terminé. Rajbhandari et al. rapportent que cela coûte une augmentation modeste de 50 % du volume de communication par rapport au parallélisme de données ordinaire, en échange d'une réduction de mémoire qui continue de croître à mesure qu'on ajoute des appareils, au lieu de plafonner à 8x comme le font les stages 1 et 2.

### Le mécanisme : rassembler à la demande, puis relâcher

Le schéma qu'utilise le stage 3 est : ne détenir au repos que sa propre tranche des paramètres ; juste avant qu'une couche n'ait besoin de tous ses paramètres pour un calcul avant ou arrière, faire un **all-gather** des morceaux manquants auprès des autres appareils pour reconstruire temporairement le tenseur complet des paramètres ; une fois le calcul de cette couche terminé, libérer la copie reconstruite et revenir à ne détenir que sa propre tranche. C'est la même opération collective all-gather que n'importe quelle autre, simplement déclenchée bien plus souvent, une fois par couche et par passe, plutôt qu'une fois par pas d'entraînement comme l'est la synchronisation des gradients du parallélisme de données ordinaire.

### FSDP : la même idée, sous forme d'API réelle

Le `FullyShardedDataParallel` de PyTorch, couramment abrégé en **FSDP**, implémente exactement ce schéma, et sa propre documentation le dit directement : elle se décrit comme « inspiré de ... ZeRO Stage 3 de DeepSpeed ». Envelopper un module dans FSDP partitionne ses paramètres entre les appareils en parallélisme de données, et pendant la passe avant et arrière, FSDP remplace les paramètres du module par des vues reconstruites rassemblées à la demande, le même schéma rassembler-puis-relâcher que cette leçon vient de décrire de façon abstraite. FSDP expose aussi des stratégies de partitionnement plus légères qui ne partitionnent que les gradients et l'état d'optimizer en laissant les paramètres non partitionnés, ce qui est le même compromis que fait le stage 2 plutôt que celui du stage 3 : moins de mémoire économisée, mais pas de trafic all-gather supplémentaire pour les paramètres à chaque passe avant et arrière.

## Pratique

1. ▢ D'après la mise à l'échelle rapportée de ZeRO stage 3, quelle réduction de mémoire une équipe doit-elle attendre en répartissant les paramètres, les gradients et l'état d'optimizer d'un modèle sur 32 appareils ?

<details markdown="1"><summary>Vérifier</summary>

Environ 32x, puisque Rajbhandari et al. rapportent que la réduction de mémoire du stage 3 croît linéairement avec le degré de parallélisme de données `Nd` (64 appareils donnent 64x dans leur propre exemple, donc 32 appareils donnent à peu près la moitié).

</details>

2. ▢ Pourquoi partitionner les paramètres eux-mêmes exige-t-il une communication supplémentaire que le partitionnement de l'état d'optimizer et des gradients n'exigeait pas ?

    - a) Les paramètres sont stockés dans une précision numérique différente, plus coûteuse à transmettre
    - b) La passe avant et arrière de chaque appareil a besoin de l'ensemble complet des paramètres, pas seulement de la tranche qu'il possède, si bien que les tranches manquantes doivent être rassemblées depuis d'autres appareils à la demande
    - c) Le partitionnement des paramètres exige un protocole réseau plus lent que le partitionnement des gradients
    - d) Il n'exige en réalité pas de communication supplémentaire ; le chiffre de 50 % de l'article correspond à une autre comparaison

<details markdown="1"><summary>Vérifier</summary>

**b)** est le mécanisme réel : contrairement à l'état d'optimizer et aux gradients, dont seul l'appareil propriétaire a besoin, les paramètres sont nécessaires à chaque appareil pour le calcul avant et arrière de chaque couche, si bien qu'un all-gather doit reconstruire les tranches qu'un appareil ne détient pas. (a), (c) et (d) ne décrivent pas la vraie raison.

</details>

3. ▢ Une équipe choisit la stratégie `SHARD_GRAD_OP` de PyTorch FSDP au lieu de `FULL_SHARD`. À quel stage ZeRO cela correspond-il, et quel compromis cela fait-il par rapport à `FULL_SHARD` ?

<details markdown="1"><summary>Indice</summary>

`SHARD_GRAD_OP` laisse les paramètres non partitionnés et exposés sous leur forme complète, en ne partitionnant que les gradients et l'état d'optimizer.

</details>

<details markdown="1"><summary>Vérifier</summary>

Cela correspond au stage 2 de ZeRO. Elle économise moins de mémoire que `FULL_SHARD` (stage 3), puisque les paramètres ne sont pas partitionnés, mais elle évite aussi le trafic all-gather supplémentaire dont le stage 3 a besoin pour reconstruire les paramètres à la demande à chaque passe avant et arrière.

</details>

## Exercices en situation réelle

- [ ] Lisez la documentation FSDP de PyTorch (liée plus haut) et trouvez la description de ce qui arrive aux paramètres d'un module enveloppé pendant la passe avant. Écrivez une phrase qui la relie au schéma « rassembler, puis relâcher » que décrit cette leçon.
- [ ] En utilisant l'exemple de mille milliards de paramètres sur 1 024 GPU de cette leçon (environ 16 To d'états du modèle, 16 Go par appareil), refaites le même calcul pour un modèle de 100 milliards de paramètres réparti sur 64 appareils, et vérifiez s'il tient confortablement dans un GPU de 80 Go.
- [ ] Demain : trouvez un exemple de configuration (dans la documentation de FSDP ou de DeepSpeed) qui fixe explicitement une stratégie de partitionnement, et identifiez à quel stage ZeRO correspond cette configuration précise, en vous appuyant sur les descriptions de cette leçon et de la leçon 9 de ce que chaque stage partitionne.

## Pour aller plus loin

- [Article : "ZeRO: Memory Optimizations Toward Training Trillion Parameter Models", Rajbhandari et al., 2019](https://arxiv.org/abs/1910.02054)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
