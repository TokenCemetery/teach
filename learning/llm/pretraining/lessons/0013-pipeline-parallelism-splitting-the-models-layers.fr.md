---
title: "13. Parallélisme de pipeline : découper les couches du modèle"
description: "Affecter des couches consécutives à des appareils différents, et le temps d'inactivité que cela coûte au début et à la fin de chaque batch"
type: lesson
---

# Leçon 13. Parallélisme de pipeline : découper les couches du modèle

**Lien avec la mission :** « Expliquer ce que ZeRO/FSDP partitionnent, pourquoi le parallélisme de données seul manque de mémoire avant de manquer de calcul, et quand le parallélisme tensoriel ou de pipeline vaut son coût de communication » est le quatrième point sous Objectif. La leçon 12 a couvert le découpage du calcul propre à une couche entre des appareils ; cette leçon couvre plutôt le découpage des couches du modèle entre des appareils.
**Source primaire :** [Article : "Efficient Large-Scale Language Model Training on GPU Clusters Using Megatron-LM", Narayanan et al., 2021](https://arxiv.org/abs/2104.04473)
**Prérequis :** [Leçon 12](0012-tensor-parallelism-splitting-a-layers-matrices.md)

## Échauffement

1. ▢ Dans le découpage du MLP en parallélisme tensoriel, pourquoi découper la première matrice de poids selon ses colonnes, plutôt que selon ses lignes, évite-t-il d'avoir besoin d'une étape de synchronisation avant d'appliquer `GeLU` ?

<details markdown="1"><summary>Vérifier</summary>

Un découpage par colonnes divise la dimension de sortie, si bien que la tranche du résultat de chaque appareil est déjà complète et correcte ; un découpage par lignes diviserait la dimension sur laquelle on somme, laissant chaque appareil avec une simple somme partielle, et `GeLU` ne peut pas être appliquée correctement à une somme partielle puisqu'elle est non linéaire.

</details>

## À savoir

### Découper la profondeur du modèle, pas la largeur d'une seule couche

Le **parallélisme de pipeline** adopte une troisième approche, différente à la fois de ZeRO (étape 5) et du parallélisme tensoriel (leçon 12) : plutôt que de découper ce que calcule une couche donnée, il répartit les couches elles-mêmes du modèle entre des appareils. Pour un modèle construit à partir du même bloc transformer répété de nombreuses fois, c'est direct : chaque appareil, ou **étage de pipeline**, se voit affecter une suite contiguë et égale de couches du transformer, et la passe avant d'un exemple d'entraînement traverse les appareils en séquence, étage par étage, comme une chaîne de montage physique fait passer une pièce de poste en poste.

### Pourquoi un batch est découpé en micro-batches

Si un batch entier devait passer complètement par l'étage 1 avant que l'étage 2 puisse commencer à travailler dessus, tous les étages sauf un resteraient inactifs presque tout le temps ; il n'y aurait rien de pipeliné là-dedans. L'approche de Narayanan et al. découpe plutôt un batch en **micro-batches** plus petits et fait circuler leur exécution en pipeline : pendant que l'étage 1 travaille sur le micro-batch 2, l'étage 2 peut simultanément travailler sur la sortie du micro-batch 1, comme une vraie chaîne de montage a plusieurs pièces en cours à travers ses postes en même temps, au lieu de terminer complètement une pièce avant de commencer la suivante.

### La bulle de pipeline

Même avec des micro-batches échelonnés dans le pipeline, il y a un temps d'inactivité inévitable au début d'un batch, avant que chaque étage ait quoi que ce soit à traiter, et à la fin, après que le dernier micro-batch a quitté les étages précédents et que seuls les derniers étages ont encore du travail à finir. Narayanan et al. appellent ce temps d'inactivité la **bulle de pipeline**, et c'est un vrai coût : plus il y a d'étages de pipeline, plus ce temps d'inactivité s'accumule relativement au calcul utile, à moins d'utiliser assez de micro-batches par batch pour garder le pipeline plus rempli plus longtemps entre le remplissage et la vidange inévitables à chaque extrémité.

### Pourquoi le pipeline a besoin de vidanges périodiques

Une subtilité dont Narayanan et al. se préoccupent avec soin : un pipeline naïf, exécuté uniquement pour le débit et sans autre contrainte, peut laisser la passe arrière d'un micro-batch voir une version des poids différente, déjà mise à jour, de celle qu'a utilisée sa propre passe avant, si d'autres micro-batches plus avancés dans le pipeline ont terminé leur pas d'optimizer en premier. Cela casse le sens ordinaire, synchrone, d'un pas d'entraînement, où chaque exemple d'un batch est censé voir un seul jeu cohérent de poids entre sa propre passe avant et sa passe arrière. Pour conserver exactement cette garantie, Narayanan et al. introduisent des **vidanges de pipeline** (pipeline flushes) périodiques : des points où le pipeline est autorisé à se vider complètement et où le pas d'optimizer de chaque appareil a lieu en même temps, de façon synchronisée, avant que les micro-batches du batch suivant ne recommencent à remplir le pipeline. Cette vidange est aussi l'endroit où la bulle décrite plus haut se produit réellement ; c'est le prix payé pour conserver une sémantique d'optimizer synchrone plutôt que de laisser des versions de poids dériver d'un micro-batch à l'autre.

## Pratique

1. ▢ Un modèle de 8 couches de transformer est découpé en 4 étages de pipeline, de 2 couches chacun. Si un batch entier devait terminer entièrement l'étage 1 avant que l'étage 2 puisse commencer à travailler, que se passerait-il pour les étages 2 à 4 pendant que l'étage 1 travaille ?

<details markdown="1"><summary>Vérifier</summary>

Ils resteraient inactifs, puisqu'aucun d'eux n'aurait quoi que ce soit à calculer jusqu'à ce que l'étage 1 ait terminé le batch entier et transmis sa sortie. C'est exactement le problème que le découpage d'un batch en micro-batches est censé éviter.

</details>

2. ▢ Laquelle de ces affirmations décrit le mieux ce qu'est la bulle de pipeline ?

    - a) La mémoire supplémentaire utilisée pour stocker les activations aux frontières entre étages de pipeline
    - b) Le temps d'inactivité au début et à la fin d'un batch, pendant que le pipeline se remplit ou se vide, qui n'ajoute aucun calcul utile
    - c) Le délai de communication entre un all-reduce en parallélisme tensoriel et la multiplication matricielle suivante
    - d) Une pause délibérée insérée pour laisser les appareils refroidir entre les batches

<details markdown="1"><summary>Vérifier</summary>

**b)** est exactement ainsi que Narayanan et al. la nomment. (a) décrit un vrai coût du pipeline mais pas la bulle en particulier. (c) décrit une préoccupation du parallélisme tensoriel, pas du parallélisme de pipeline. (d) n'est pas une vraie raison du temps d'inactivité.

</details>

3. ▢ Pourquoi les vidanges périodiques du pipeline comptent-elles pour la correction, et pas seulement pour le débit ?

<details markdown="1"><summary>Indice</summary>

Demandez-vous ce qui pourrait mal tourner pour la passe arrière d'un micro-batch précis si d'autres micro-batches plus avancés dans le pipeline avaient déjà déclenché un pas d'optimizer.

</details>

<details markdown="1"><summary>Vérifier</summary>

Sans vidange, la passe arrière d'un micro-batch pourrait voir une version des poids différente, déjà mise à jour, de celle qu'a utilisée sa propre passe avant, si d'autres micro-batches ont terminé leur pas d'optimizer en premier. Cela casse la sémantique d'optimizer synchrone, où chaque exemple d'un batch est censé voir un seul jeu cohérent de poids entre sa propre passe avant et sa passe arrière. Une vidange laisse le pipeline se vider et le pas d'optimizer de chaque appareil avoir lieu en même temps, ce qui préserve cette garantie au prix de la bulle.

</details>

4. ▢ Une équipe augmente le nombre de micro-batches par batch sans changer le nombre d'étages de pipeline. Quel effet cela aurait-il sur la fraction de temps perdue à cause de la bulle de pipeline ?

<details markdown="1"><summary>Vérifier</summary>

Cela réduirait la fraction de temps perdue à cause de la bulle, puisque le coût fixe de remplissage et de vidange est amorti sur davantage de calcul utile de micro-batches entre les deux. La bulle elle-même ne disparaît pas, mais elle devient une part plus petite du temps total passé par batch.

</details>

## Exercices en situation réelle

- [ ] Dessinez sur le papier quatre étages de pipeline et quatre micro-batches, et esquissez une chronologie montrant quel étage travaille sur quel micro-batch à chaque pas de temps, y compris les cases inactives au début et à la fin qui représentent la bulle.
- [ ] Lisez la section de l'article Megatron-LM (liée plus haut) qui décrit les vidanges de pipeline, et écrivez une phrase avec vos propres mots qui distingue ce que garantit une vidange de ce que garantit le seul découpage en micro-batches.
- [ ] Demain : sans regarder la suite, écrivez une prédiction d'une phrase pour la leçon 14 : sachant que le parallélisme tensoriel a besoin d'un all-reduce pour chaque couche alors que le parallélisme de pipeline n'a besoin que de transmettre des activations entre une poignée de frontières d'étages, lequel vous attendriez-vous à voir mieux tolérer une connexion réseau plus lente et de plus longue distance entre appareils ?

## Pour aller plus loin

- [Article : "Efficient Large-Scale Language Model Training on GPU Clusters Using Megatron-LM", Narayanan et al., 2021](https://arxiv.org/abs/2104.04473)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
