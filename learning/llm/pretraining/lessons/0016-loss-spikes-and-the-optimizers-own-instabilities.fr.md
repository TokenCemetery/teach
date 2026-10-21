---
title: "16. Pics de loss et instabilités propres à l'optimizer"
description: "Le même pic peut venir d'un mauvais batch ou de l'optimizer lui-même, et les distinguer demande une comparaison contrôlée"
type: lesson
---

# Leçon 16. Pics de loss et instabilités propres à l'optimizer

**Lien avec la mission :** « Étant donné une courbe de loss, savoir dire si un pic est récupérable ou impose un redémarrage depuis un checkpoint antérieur » est le point d'Objectif que sert cette étape. Cette leçon couvre ce dont un pic de loss peut réellement provenir, et la mitigation standard ; la leçon 17 couvre le schéma qui organise l'entraînement autour.
**Source primaire :** [Article : "Scaling Language Models: Methods, Analysis & Insights from Training Gopher", Rae et al., 2021](https://arxiv.org/abs/2112.11446)
**Prérequis :** [Leçon 15](0015-mixed-precision-at-scale-bfloat16-and-stochastic-rounding.md), [Pic de loss](../GLOSSARY.md)

## Échauffement

1. ▢ Pourquoi la plage d'exposant plus large du bf16 le rend-il plus indulgent pendant l'entraînement que le fp16, alors que le bf16 a moins de précision ?

<details markdown="1"><summary>Vérifier</summary>

Le bf16 garde les 8 bits d'exposant complets du fp32, ce qui lui donne la même plage dynamique que le fp32, si bien que les valeurs grandes ou petites qui apparaissent dans les gradients et les activations à grande échelle ont moins de chances de le faire déborder par le haut ou par le bas, même s'il représente les valeurs moins précisément dans cette plage que ne le fait le fp16.

</details>

2. ▢ Quelle limite Rae et al. ont-ils rapportée même après avoir utilisé l'arrondi stochastique pour les mises à jour de paramètres en bf16 ?

<details markdown="1"><summary>Vérifier</summary>

L'arrondi stochastique ne retrouve pas entièrement les performances de l'entraînement ordinaire en précision mixte ; c'est une mitigation, pas une solution complète.

</details>

## À savoir

### Un pic de loss n'annonce pas sa propre cause

Un **pic de loss**, une hausse soudaine et brutale de la loss d'entraînement en cours de run, peut venir de plusieurs endroits : un seul batch inhabituellement difficile ou malformé, un problème de précision numérique comme ceux que décrivait la leçon 15, ou quelque chose dans l'optimizer lui-même qui devient instable à l'échelle entraînée. Lire un pic sur une courbe de loss vous dit qu'il a eu lieu ; cela ne vous dit pas à soi seul laquelle de ces causes l'a produit, et la bonne réponse, un redémarrage, un changement d'hyperparamètre ou rien du tout, dépend de savoir laquelle.

### Un cas concret : Adafactor contre Adam à grande échelle

Rae et al. donnent un exemple détaillé de ce genre précis d'investigation. Adafactor est un optimizer qui utilise moins de mémoire qu'Adam, ce qui compte directement pour le budget mémoire que la leçon 8 a compté : une empreinte d'état d'optimizer plus petite pourrait permettre de faire tenir un modèle plus grand, ou de faire tenir le même modèle avec moins de partitionnement. À plus petite échelle, Rae et al. ont trouvé le pré-entraînement avec Adafactor stable et performant. À 7,1 milliards de paramètres, cela a cessé d'être vrai : ils ont observé, en entraînant avec Adafactor, des divergences de la loss qu'ils n'avaient pas vues à 1,4 milliard de paramètres, alors même que le run Adafactor utilisait un learning rate maximal plus bas (`6 × 10^-5`) que la baseline Adam stable à laquelle il était comparé (`1.2 × 10^-4`). Un learning rate plus bas est normalement la première chose à essayer contre l'instabilité ; ici, cela ne suffisait pas, ce qui a permis à Rae et al. de conclure que l'instabilité venait de l'optimizer lui-même à cette échelle, et pas simplement d'un learning rate réglé trop haut.

### La mitigation standard : le clipping par la norme globale du gradient

Quelle que soit la cause sous-jacente d'une instabilité, la mitigation la plus directe qu'utilisent Rae et al. est le **gradient clipping** par norme globale : calculer la norme (l'amplitude globale) du vecteur gradient complet sur tous les paramètres du modèle et, si cette norme dépasse un seuil choisi, remettre à l'échelle l'ensemble du gradient vers le bas de façon proportionnelle pour que sa norme soit exactement égale au seuil, avant que le pas de l'optimizer ne l'utilise. Cela borne l'ampleur de la mise à jour d'un seul pas, quelle que soit la cause d'un gradient anormalement grand. Rae et al. utilisent une valeur de clipping de 1 pour la plupart de leurs modèles, mais la ramènent à 0,25 spécifiquement pour leurs deux plus grands, le modèle de 7,1B et Gopher lui-même, pour une meilleure stabilité, un exemple direct et concret de resserrement de cette protection à mesure que l'échelle augmente plutôt que de la laisser fixe.

## Pratique

1. ▢ Une équipe observe un pic de loss en cours de run d'entraînement. Nommez deux causes sous-jacentes différentes décrites par cette leçon qui pourraient produire le même pic visible.

<details markdown="1"><summary>Vérifier</summary>

N'importe quelles deux parmi : un seul batch inhabituellement difficile ou malformé, un problème de précision numérique (comme un débordement ou un problème d'arrondi dans l'entraînement en bf16), ou une instabilité venant de l'optimizer lui-même qui devient instable à l'échelle entraînée.

</details>

2. ▢ Pourquoi baisser le learning rate n'a-t-il pas réussi à stabiliser le run Adafactor de 7,1B, et qu'ont conclu Rae et al. de cet échec ?

<details markdown="1"><summary>Indice</summary>

Le run Adafactor utilisait déjà un learning rate plus bas que la baseline Adam stable à laquelle il était comparé.

</details>

<details markdown="1"><summary>Vérifier</summary>

Le run Adafactor utilisait un learning rate maximal de `6 × 10^-5`, plus bas que les `1.2 × 10^-4` de la baseline Adam stable, et montrait quand même des instabilités. Puisqu'un learning rate plus bas ne réglait pas le problème, Rae et al. ont conclu que l'instabilité venait de l'optimizer lui-même à cette échelle, et pas simplement d'un learning rate trop haut.

</details>

3. ▢ Que fait réellement le clipping de la norme globale du gradient à un gradient dont la norme dépasse le seuil de clipping ?

    - a) Il écarte entièrement ce gradient et saute le pas d'optimizer pour ce batch
    - b) Il remet à l'échelle l'ensemble du vecteur gradient de façon proportionnelle pour que sa norme soit égale au seuil
    - c) Il arrondit les valeurs du gradient à un format de précision plus basse
    - d) Il abaisse définitivement le learning rate pour le reste de l'entraînement

<details markdown="1"><summary>Vérifier</summary>

**b)** est exactement le mécanisme : une remise à l'échelle proportionnelle pour ramener la norme au seuil, et non un rejet, un changement de précision ou un changement définitif de schéma. (a), (c) et (d) décrivent chacune une intervention différente et sans rapport.

</details>

4. ▢ Rae et al. utilisent une valeur de clipping de 1 pour la plupart des tailles de modèle mais la ramènent à 0,25 spécifiquement pour le modèle de 7,1B et Gopher (280B). Qu'illustre ce choix concret sur la manière dont se règlent les protections de stabilité ?

<details markdown="1"><summary>Vérifier</summary>

Qu'une protection comme le gradient clipping n'est pas nécessairement une constante fixe à toutes les échelles ; ici, elle a été resserrée spécifiquement pour les plus grands modèles, où le risque d'instabilité était le plus grand, plutôt que laissée à la même valeur que celle utilisée pour des runs plus petits et plus stables.

</details>

## Exercices en situation réelle

- [ ] Trouvez où le gradient clipping est exposé comme option de configuration dans un framework d'entraînement auquel vous avez accès, et notez sa valeur de clipping par défaut, si une est définie.
- [ ] Lisez le paragraphe de l'article Gopher (lié plus haut) qui décrit la comparaison Adafactor contre Adam, et écrivez une phrase qui indique quelle preuve, précisément, a écarté « le learning rate était simplement trop haut » comme explication.
- [ ] Demain : sans regarder la suite, écrivez une prédiction d'une phrase pour la leçon 17 : sachant que Rae et al. font monter le learning rate lentement tout au début de l'entraînement plutôt que de démarrer immédiatement à la valeur maximale, quel problème pourrait causer le fait de démarrer au learning rate maximal à partir d'un réseau fraîchement initialisé et non entraîné ?

## Pour aller plus loin

- [Article : "Scaling Language Models: Methods, Analysis & Insights from Training Gopher", Rae et al., 2021](https://arxiv.org/abs/2112.11446)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
