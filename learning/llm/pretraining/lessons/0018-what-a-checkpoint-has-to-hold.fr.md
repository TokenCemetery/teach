---
title: "18. Ce qu'un checkpoint doit contenir"
description: "Un checkpoint qui ne sauvegarde que les poids ne peut pas reprendre un run à l'identique, et choisir la fréquence de sauvegarde est un compromis à part entière"
type: lesson
---

# Leçon 18. Ce qu'un checkpoint doit contenir

**Lien avec la mission :** « Concevoir un schéma de checkpointing qui borne la progression perdue après la panne d'un nœud » est la case « Terminée quand » de cette étape dans « Le fil conducteur ». Cette leçon couvre ce qu'un checkpoint doit contenir et à quelle fréquence en sauvegarder un ; la leçon 19 couvre ce qui se passe réellement quand un nœud tombe en panne en cours de run.
**Source primaire :** [Article : "OPT: Open Pre-trained Transformer Language Models", Zhang et al., 2022](https://arxiv.org/abs/2205.01068)
**Prérequis :** [Leçon 17](0017-warmup-decay-and-growing-the-batch-mid-run.md)

## Échauffement

1. ▢ D'après Rae et al., un modèle plus grand reçoit-il un learning rate maximal plus haut ou plus bas qu'un plus petit, toutes choses égales par ailleurs ?

<details markdown="1"><summary>Vérifier</summary>

Un learning rate maximal plus bas. Rae et al. indiquent directement qu'à mesure que la taille du modèle augmente, ils diminuent le learning rate maximal qu'utilise le schéma.

</details>

2. ▢ Que fait le clipping de la norme globale du gradient à un gradient dont la norme dépasse le seuil de clipping ?

<details markdown="1"><summary>Vérifier</summary>

Il remet à l'échelle l'ensemble du vecteur gradient de façon proportionnelle pour que sa norme soit égale au seuil, ce qui borne l'ampleur d'une seule mise à jour, au lieu d'écarter le gradient ou de changer le learning rate.

</details>

## À savoir

### Un checkpoint, c'est plus que les poids

Sauvegarder seulement les paramètres d'un modèle ne suffit pas pour reprendre l'entraînement exactement là où il s'était arrêté. Reprendre correctement un run d'entraînement exige au minimum : les **paramètres** du modèle ; l'**état de l'optimizer** (pour Adam, le moment et la variance que la leçon 8 a comptés, sans lesquels l'optimizer redémarre en pratique à froid) ; le **nombre de pas et la position dans le schéma de learning rate**, pour que le warmup et la décroissance (leçon 17) reprennent au bon point au lieu de recommencer ; et, pour une reproductibilité exacte, la **position du data loader et l'état du générateur de nombres aléatoires**, pour que le run ne retraite ni ne saute silencieusement des données autour du point de reprise. Un checkpoint auquel manque l'un de ces éléments n'échoue pas bruyamment ; il reprend dans un run qui a l'air de continuer, tout en s'entraînant discrètement un peu différemment de ce qu'aurait fait un run ininterrompu.

### Pourquoi la fréquence des checkpoints est un compromis à part entière

Quelle que soit la complétude du contenu d'un checkpoint, en sauvegarder un coûte du temps et du stockage : écrire l'état complet d'un grand modèle sur un stockage durable prend un vrai temps réel, pendant lequel le run d'entraînement est généralement en pause ou au moins ne progresse pas à plein régime, et chaque checkpoint occupe un vrai espace disque, surtout si on en garde plusieurs récents plutôt que seulement le dernier. Checkpointer plus souvent borne la quantité de progression qu'une panne peut détruire, puisque seul le travail effectué depuis le dernier checkpoint est jamais en danger. Checkpointer moins souvent dépense moins de temps et de stockage au total pour les checkpoints eux-mêmes, au prix de perdre plus de progression sur la même panne. Aucun extrême n'est bon en général : la bonne fréquence dépend de la fréquence à laquelle on s'attend réellement à des pannes, mise en balance avec le coût réel d'écriture de chaque checkpoint.

### À quelle fréquence les pannes surviennent réellement, dans un vrai run

Le récit de Zhang et al. sur l'entraînement d'OPT-175B rend concret, plutôt qu'hypothétique, le versant « à quelle fréquence s'attend-on à des pannes » de ce compromis. Sur environ deux mois d'entraînement, des pannes matérielles ont contribué à au moins 35 redémarrages manuels et au remplacement cyclique de plus de 100 hôtes, et les auteurs estiment à plus de 70 les redémarrages automatiques supplémentaires, sur un seul run d'entraînement. C'est bien plus d'un redémarrage tous les deux jours en moyenne, soutenu pendant toute la durée du run. Un schéma de checkpointing construit sur l'hypothèse que les pannes sont des événements rares et occasionnels aurait été largement erroné pour ce run ; un schéma qui suppose que les pannes sont une partie courante et attendue du processus, et qui checkpointe en conséquence, est ce dont un run à cette échelle a réellement besoin.

## Pratique

1. ▢ Une équipe reprend un run d'entraînement depuis un checkpoint qui a sauvegardé les paramètres du modèle mais pas l'état de l'optimizer. Qu'est-ce qui se passe mal, même si le run repris a par ailleurs l'air de continuer normalement ?

<details markdown="1"><summary>Vérifier</summary>

L'optimizer redémarre en pratique à froid : pour Adam, le moment et la variance accumulés avant le checkpoint sont perdus, si bien que les toutes premières mises à jour après la reprise se comportent différemment de ce qu'elles auraient fait si l'entraînement n'avait jamais été interrompu, même si les paramètres eux-mêmes sont corrects.

</details>

2. ▢ Pourquoi checkpointer plus souvent réduit-il la quantité de progression qu'une panne peut détruire, et que coûte l'obtention de ce bénéfice ?

<details markdown="1"><summary>Vérifier</summary>

Seul le travail effectué depuis le checkpoint le plus récent est en danger si une panne survient, donc un checkpoint plus récent borne la perte plus étroitement. Le coût est le temps passé à écrire chaque checkpoint (pendant lequel l'entraînement est généralement en pause) et le stockage que chacun occupe, qui s'accumulent tous deux plus vite plus on sauvegarde souvent.

</details>

3. ▢ Zhang et al. rapportent au moins 35 redémarrages manuels, plus de 100 hôtes remplacés et une estimation de plus de 70 redémarrages automatiques sur environ deux mois d'entraînement d'OPT-175B. Qu'est-ce que ce chiffre plaide pour un schéma de checkpointing destiné à un run d'échelle et de durée comparables ?

<details markdown="1"><summary>Vérifier</summary>

Que les pannes doivent être traitées comme courantes et fréquentes, et non comme des exceptions rares, quand on choisit la fréquence de checkpointing. Avec bien plus d'un redémarrage tous les deux jours soutenu sur tout le run, un schéma de checkpointing conçu pour des pannes occasionnelles laisserait beaucoup trop de progression exposée à un instant donné.

</details>

## Exercices en situation réelle

- [ ] Trouvez comment un framework d'entraînement auquel vous avez accès définit ce qui entre dans un checkpoint sauvegardé (paramètres, état de l'optimizer, nombre de pas, état du RNG), et vérifiez si l'un des quatre éléments que nomme cette leçon manque ou est facultatif dans sa configuration par défaut.
- [ ] Lisez la section « Hardware Failures » de l'article OPT (lié plus haut) et écrivez une phrase qui décrit la procédure opérationnelle suivie par les auteurs une fois une panne détectée, avant que la leçon 19 ne la couvre directement.
- [ ] Demain : pour un run hypothétique de votre choix (n'importe quelle durée et échelle), estimez une fréquence de checkpoint que vous choisiriez, et écrivez une phrase qui la justifie à la fois face au coût de checkpointer trop souvent et au risque de checkpointer trop rarement.

## Pour aller plus loin

- [Article : "OPT: Open Pre-trained Transformer Language Models", Zhang et al., 2022](https://arxiv.org/abs/2205.01068)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
