---
title: "17. Warmup, décroissance et croissance du batch en cours de run"
description: "Démarrer lentement, décroître selon un schéma, et laisser la taille du batch elle-même changer en cours d'entraînement"
type: lesson
---

# Leçon 17. Warmup, décroissance et croissance du batch en cours de run

**Lien avec la mission :** « Étant donné une courbe de loss, savoir dire si un pic est récupérable ou impose un redémarrage depuis un checkpoint antérieur » est le point d'Objectif que sert cette étape. La leçon 16 a couvert les pics et le clipping qui s'en protège ; cette leçon couvre le schéma qui organise le run autour de cette protection.
**Source primaire :** [Article : "Scaling Language Models: Methods, Analysis & Insights from Training Gopher", Rae et al., 2021](https://arxiv.org/abs/2112.11446)
**Prérequis :** [Leçon 16](0016-loss-spikes-and-the-optimizers-own-instabilities.md)

## Échauffement

1. ▢ Que fait le clipping de la norme globale du gradient à un gradient dont la norme dépasse le seuil de clipping, et pourquoi Rae et al. ont-ils réduit le seuil spécifiquement pour leurs deux plus grands modèles ?

<details markdown="1"><summary>Vérifier</summary>

Il remet à l'échelle l'ensemble du gradient de façon proportionnelle pour que sa norme soit égale au seuil, ce qui borne l'ampleur d'une seule mise à jour. Rae et al. ont réduit le seuil de 1 à 0,25 spécifiquement pour le modèle de 7,1B et Gopher (280B), pour une meilleure stabilité à cette échelle.

</details>

2. ▢ Pourquoi baisser le learning rate n'a-t-il pas réussi à stabiliser le run Adafactor de 7,1B de Rae et al., et qu'est-ce que cet échec indiquait ?

<details markdown="1"><summary>Vérifier</summary>

Le run Adafactor utilisait déjà un learning rate plus bas que la baseline Adam stable et montrait quand même des instabilités, ce qui indiquait que l'instabilité venait de l'optimizer lui-même à cette échelle, et pas simplement d'un learning rate trop haut.

</details>

## À savoir

### Démarrer lentement exprès

Rae et al. ne commencent pas l'entraînement au learning rate maximal qu'utilise leur schéma. Ils font plutôt monter progressivement le learning rate de `10^-7` jusqu'à la valeur maximale, pendant les 1 500 premiers pas, avant de le laisser suivre le reste du schéma. Les toutes premières mises à jour d'un réseau fraîchement initialisé sont les moins informées de tout le run : les poids n'ont vu aucune donnée, si bien qu'une mise à jour calculée à partir d'eux est plus susceptible d'être une correction démesurée et inutile qu'une mise à jour ultérieure, calculée une fois que le réseau s'ajuste déjà raisonnablement aux données. Démarrer le learning rate près de zéro et le faire monter donne à ces mises à jour les plus précoces et les moins fiables un effet plus faible sur les poids, au lieu de les laisser secouer le modèle aussi fort qu'une mise à jour pleinement échauffée.

### Décroître ensuite

Une fois le warmup terminé, Rae et al. font décroître le learning rate d'un facteur 10 sur le reste de l'entraînement, selon un schéma en cosinus : une courbe lisse qui part du learning rate maximal et décroît vers la valeur finale en suivant la forme d'un quart d'onde de cosinus, plutôt que de chuter par paliers brusques. C'est une décision distincte du warmup, visant un autre moment de l'entraînement : alors que le warmup protège le tout début du run, la décroissance consiste à faire des pas plus petits et plus prudents à mesure que l'entraînement avance et que le paysage de la loss près d'une bonne solution appelle en général des ajustements plus fins que les grands pas utiles au début.

### Modèles plus grands, learning rates crêtes plus bas

Rae et al. énoncent cette relation sans détour : à mesure que la taille du modèle augmente, ils diminuent le learning rate maximal vers lequel le schéma monte et à partir duquel il décroît. Un learning rate parfaitement raisonnable pour un petit modèle n'est pas automatiquement sûr pour un modèle bien plus grand ; choisir un learning rate maximal par modèle, plutôt que de réutiliser une seule valeur fixe pour toutes les tailles entraînées, fait partie de ce qui garde les runs plus grands dans la plage que le clipping de la leçon 16 et le warmup de cette leçon sont censés protéger.

### La taille du batch elle-même peut changer en cours de run

En plus du schéma de learning rate, Rae et al. décrivent un levier supplémentaire : augmenter la taille du batch pendant l'entraînement lui-même. La taille de batch de Gopher est passée de trois millions à six millions de tokens par batch au cours de son run d'entraînement, et n'est pas restée fixe du premier pas au dernier. Un batch plus grand donne une estimation du gradient moins bruitée et plus fiable à chaque pas et une meilleure utilisation du matériel, mais démarrer tout un run immédiatement à la plus grande taille de batch n'est pas forcément nécessaire pour obtenir ces bénéfices tout du long ; y entrer progressivement en cours de route est une décision de schéma à part entière, au même titre que le warmup et la décroissance du learning rate, plutôt que quelque chose qu'il faut fixer pour tout le run dès le départ.

## Pratique

1. ▢ Pourquoi démarrer l'entraînement immédiatement au learning rate maximal, sans warmup, pourrait-il être plus risqué que de monter progressivement, étant donné ce à quoi ressemblent les premières mises à jour d'un réseau fraîchement initialisé ?

<details markdown="1"><summary>Vérifier</summary>

Les mises à jour les plus précoces du réseau, calculées avant qu'il ait vu la moindre donnée, sont les moins informées de tout le run et plus susceptibles d'être des corrections démesurées et inutiles. Un learning rate à pleine force appliqué à une telle mise à jour pourrait secouer fortement les poids dans une mauvaise direction ; le warmup limite l'effet que ces mises à jour les plus précoces et les moins fiables peuvent avoir.

</details>

2. ▢ Quelle est la différence pratique entre ce dont le warmup protège et ce que vise la décroissance en cosinus ?

<details markdown="1"><summary>Vérifier</summary>

Le warmup protège le tout début de l'entraînement, quand les mises à jour du réseau sont les moins informées. La décroissance en cosinus concerne l'entraînement plus tardif, en faisant progressivement des pas plus petits, puisque le paysage de la loss près d'une bonne solution appelle en général des ajustements plus fins que les pas plus grands utiles plus tôt. Ils traitent des moments différents du même run, et non deux fois le même problème.

</details>

3. ▢ D'après Rae et al., un modèle plus grand reçoit-il un learning rate maximal plus haut ou plus bas qu'un plus petit, toutes choses égales par ailleurs ?

<details markdown="1"><summary>Vérifier</summary>

Un learning rate maximal plus bas. Rae et al. indiquent directement qu'à mesure que la taille du modèle augmente, ils diminuent le learning rate maximal qu'utilise le schéma.

</details>

4. ▢ La taille de batch de Gopher est passée de trois millions à six millions de tokens par batch au cours de l'entraînement, au lieu de démarrer à six millions dès le premier pas. Nommez une raison plausible d'entrer progressivement dans la plus grande taille de batch plutôt que d'y démarrer immédiatement.

<details markdown="1"><summary>Vérifier</summary>

Tout récit raisonnable est acceptable, par exemple : plus tôt dans l'entraînement, quand les mises à jour sont déjà moins stables (selon le raisonnement du warmup), ajouter par-dessus un très grand batch n'est peut-être pas nécessaire pour obtenir une estimation utile du gradient, et faire croître la taille du batch plus tard tire parti des bénéfices du plus grand batch (un gradient moins bruité, une meilleure utilisation du matériel) une fois que l'entraînement a déjà atteint une région plus stable.

</details>

## Exercices en situation réelle

- [ ] Trouvez la documentation d'un framework d'entraînement sur ses options de scheduler de learning rate, et identifiez s'il expose une phase de warmup, une phase de décroissance en cosinus ou les deux, et comment chacune est configurée.
- [ ] Esquissez sur le papier une courbe approximative du learning rate en fonction du pas d'entraînement combinant le warmup (une courte montée depuis près de zéro) suivi d'une décroissance en cosinus (une courbe lisse jusqu'à une valeur finale bien plus petite), en indiquant approximativement où se situerait le warmup de 1 500 pas décrit par Rae et al. par rapport à un run de, disons, 300 000 pas au total.
- [ ] Demain : pour une taille de modèle de votre choix (petite, moyenne ou grande, selon vos propres termes), décidez qualitativement si vous vous attendriez à ce que son learning rate maximal soit plus proche de celui de Gopher ou de celui d'un modèle bien plus petit, et écrivez une phrase sur la raison, d'après la relation avec la taille du modèle de cette leçon.

## Pour aller plus loin

- [Article : "Scaling Language Models: Methods, Analysis & Insights from Training Gopher", Rae et al., 2021](https://arxiv.org/abs/2112.11446)
- [Ressources](../RESOURCES.md)

---

L'étape 7 a couvert le numérique et le schéma qui gardent stable un run d'entraînement unique. L'étape 8 aborde ce qui se passe sur les nombreux jours qu'un tel run prend réellement : comment la progression survit à une sauvegarde, à une reprise et à l'interruption par une panne en cours de route.

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
