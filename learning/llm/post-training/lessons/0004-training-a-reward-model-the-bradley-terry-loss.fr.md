---
title: "4. Entraîner un reward model : la loss de Bradley-Terry"
description: "Un reward model ne voit jamais de score absolu à l'entraînement, seulement laquelle de deux complétions un humain a préférée"
type: lesson
---

# Leçon 4. Entraîner un reward model : la loss de Bradley-Terry

**Lien avec la mission :** « Entraîner un reward model sur des paires de préférence avec la loss de Bradley-Terry, et identifier une complétion victime de reward hacking issue d'une policy entraînée contre lui » est la deuxième puce sous « Objectif ». Cette leçon couvre l'entraînement du reward model ; la leçon 5 couvre ce qui peut mal tourner quand une policy est optimisée contre lui.
**Source primaire :** [Article : "Training language models to follow instructions with human feedback", Ouyang et al., 2022](https://arxiv.org/abs/2203.02155)
**Prérequis :** [Leçon 3](0003-loss-masking-on-non-assistant-tokens.md)

## Échauffement

1. ▢ Que fait réellement, mécaniquement, le masquage de la loss sur les tokens hors assistant pendant l'entraînement SFT ?

<details markdown="1"><summary>Vérifier</summary>

Il donne à la position de chaque token de prompt ou hors assistant un label que la fonction de loss doit ignorer, si bien que seules les positions de l'assistant (la réponse) contribuent à un gradient, même si les tokens du prompt restent présents en entrée, ce sur quoi le modèle conditionne sa réponse.

</details>

2. ▢ Qu'est-ce qui casse dans l'entraînement SFT si ce masquage est omis ?

<details markdown="1"><summary>Vérifier</summary>

Du signal de gradient est dépensé, ou dilué, à apprendre à prédire les tokens du prompt lui-même, ce qui n'est pas la compétence que le SFT doit enseigner, au lieu d'être concentré entièrement sur les tokens de la réponse que le modèle devrait réellement apprendre à produire.

</details>

## À savoir

### Collecter des données de préférence

Un reward model a besoin de données qui disent laquelle de deux sorties du modèle est la meilleure, pas ce qu'aurait dû être la meilleure sortie mot pour mot. Ouyang et al. les collectent en présentant aux annotateurs plusieurs sorties (entre 4 et 9) pour un même prompt et en leur demandant de classer tout l'ensemble, au lieu de toujours comparer deux sorties à la fois. Un classement de `K` sorties produit toutes les comparaisons par paires de ce classement, soit `K` parmi 2, si bien qu'une seule tâche de classement donne d'un coup de nombreuses paires d'entraînement.

### D'où vient le reward model

Un reward model n'est pas entraîné à partir de rien. Ouyang et al. décrivent un départ depuis le modèle SFT lui-même, dont la couche finale de désembedding (unembedding), celle qui transforme un état caché en probabilités du token suivant, est retirée et remplacée par une couche qui produit un seul scalaire. Le reward model réutilise tout ce que le modèle SFT a déjà appris sur le langage et sur le comportement visé, réaffecté à produire un nombre, un score, pour un prompt et une complétion donnés, au lieu d'une distribution sur le token suivant.

### La loss de Bradley-Terry

Étant donné une complétion préférée `y_w` (« gagnante ») et une complétion rejetée `y_l` (« perdante ») pour le même prompt `x`, et les sorties scalaires `r(x, y_w)` et `r(x, y_l)` du reward model pour chacune, Ouyang et al. entraînent le reward model avec cette loss :

```text
loss(θ) = -E[log(σ(r_θ(x, y_w) - r_θ(x, y_l)))]
```

où `σ` est la fonction sigmoïde logistique. C'est la **loss de Bradley-Terry** : elle traite la probabilité qu'un humain préfère `y_w` à `y_l` comme la sigmoïde de la différence entre leurs deux scores, et entraîne le reward model à faire correspondre cette probabilité prédite à ce que l'annotateur a réellement choisi. Faire baisser cette loss revient à faire monter `r(x, y_w) - r(x, y_l)` : le modèle est entraîné à donner à la complétion préférée un score plus élevé qu'à la rejetée, d'une marge proportionnelle à la confiance avec laquelle la sigmoïde doit la favoriser.

### Pourquoi l'échelle absolue de la récompense n'a pas de sens en soi

Remarquez que la loss ne dépend que de la *différence* entre les deux scores, jamais de l'un d'eux seul. Ajouter la même constante à chaque récompense que le modèle produit laisserait chaque différence, et donc toute la loss, complètement inchangée. Cela signifie que rien dans l'entraînement n'impose aux scores du reward model une échelle absolue particulière ; seul l'ordre relatif (et la taille des écarts) entre complétions préférées et rejetées est jamais contraint. Ouyang et al. le traitent directement : comme la loss est invariante à un décalage, ils normalisent le reward model avec un biais pour que les démonstrations des annotateurs obtiennent un score moyen de 0, avant de l'utiliser en apprentissage par renforcement, ce qui donne à l'échelle par ailleurs arbitraire un ancrage fixe pour la mesurer.

### Pourquoi les comparaisons d'un même classement restent groupées

Traiter chacune des `K` parmi 2 comparaisons d'une même tâche de classement comme un exemple d'entraînement indépendant, mélangé séparément, pose un problème précis : comme le même petit ensemble de complétions réapparaît dans beaucoup de ces comparaisons, un seul passage sur des données construites ainsi tend à faire du surapprentissage, chaque complétion étant en pratique réutilisée dans `K - 1` comparaisons corrélées. La solution d'Ouyang et al. est de traiter toutes les comparaisons d'une même tâche de classement comme un seul élément de batch à l'entraînement, au lieu de les mélanger indépendamment dans le jeu de données plus large, ce qui, ont-ils constaté, améliorait la précision et la loss de validation par rapport à un traitement de chaque comparaison par paire comme totalement indépendante.

## Pratique

1. ▢ Un reward model produit `r(x, y_w) = 2.0` et `r(x, y_l) = 1.0` pour une paire, et `r(x, y_w) = 12.0` et `r(x, y_l) = 11.0` pour une seconde paire, issue d'un autre prompt. La loss de Bradley-Terry traite-t-elle ces deux paires différemment ?

<details markdown="1"><summary>Indice</summary>

La loss est une fonction de `r(x, y_w) - r(x, y_l)`, pas de l'une ou l'autre valeur seule.

</details>

<details markdown="1"><summary>Vérifier</summary>

Non. Les deux paires ont la même différence, `1.0`, et la loss ne dépend que de cette différence, pas des scores absolus. C'est exactement pourquoi l'échelle absolue du reward model n'a pas de sens sans ancrage extérieur.

</details>

2. ▢ D'où viennent réellement les poids initiaux d'un reward model, d'après Ouyang et al. ?

<details markdown="1"><summary>Vérifier</summary>

Du modèle SFT, dont la couche finale de désembedding est retirée et remplacée par une couche qui produit un seul scalaire, et non d'un modèle neuf initialisé aléatoirement.

</details>

3. ▢ Un annotateur classe 4 complétions (`K = 4`) pour un seul prompt. Combien de comparaisons par paires cette seule tâche de classement produit-elle pour l'entraînement ?

<details markdown="1"><summary>Vérifier</summary>

6 (`4` parmi `2`, soit `(4 × 3) / 2 = 6`).

</details>

4. ▢ Pourquoi Ouyang et al. gardent-ils toutes les comparaisons d'une même tâche de classement ensemble comme un seul élément de batch, au lieu de mélanger chaque comparaison par paire indépendamment dans le jeu d'entraînement ?

    - a) Cela fait entraîner le reward model plus vite sans effet sur la précision
    - b) Les mélanger indépendamment provoque du surapprentissage, puisque le même petit ensemble de complétions est réutilisé dans de nombreuses comparaisons corrélées au sein d'une même tâche de classement
    - c) La loss de Bradley-Terry ne peut pas être calculée si les comparaisons ne sont pas groupées ainsi
    - d) C'est nécessaire pour que les scores du reward model tombent dans une plage numérique fixe

<details markdown="1"><summary>Vérifier</summary>

**b)** est la raison qu'Ouyang et al. donnent directement : les complétions corrélées et réutilisées dans les comparaisons d'une tâche de classement font qu'un seul passage fait du surapprentissage si elles sont mélangées indépendamment. (a), (c) et (d) ne décrivent ni le vrai problème ni sa solution.

</details>

## Exercices en situation réelle

- [ ] Trouvez un jeu de données de préférence public (beaucoup sont publiés pour entraîner des reward models) et vérifiez combien de complétions sont classées par prompt, et si le format publié reflète déjà des comparaisons par paires ou un classement complet.
- [ ] Calculez à la main le terme sigmoïde de la loss de Bradley-Terry pour une différence de récompense de `0` (aucun signal de préférence) et pour une grande différence positive, et décrivez en une phrase le comportement de la loss à chaque extrême.
- [ ] Demain : sans regarder la suite, écrivez une prédiction d'une phrase pour la leçon 5 : si un reward model n'est jamais entraîné qu'à classer les complétions que des humains lui ont réellement montrées, qu'est-ce qui pourrait mal tourner quand une policy est libre de générer n'importe quelle complétion, à la recherche de ce qui score le plus haut ?

## Pour aller plus loin

- [Article : "Training language models to follow instructions with human feedback", Ouyang et al., 2022](https://arxiv.org/abs/2203.02155)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
