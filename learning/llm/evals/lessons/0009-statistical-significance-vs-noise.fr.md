---
title: "9. Significativité statistique et bruit"
description: "Pourquoi un écart de score doit se mesurer face au bruit qui pourrait le produire par hasard, et pourquoi la comparaison appariée l'emporte sur le traitement de deux scores comme indépendants"
type: lesson
---

# Leçon 9. Significativité statistique et bruit

**Lien avec la mission :** Le go/no-go de l'étape 5 ne vaut que ce que vaut le fait de savoir si un écart de score observé est réel ; cette leçon donne les outils pour y répondre, en s'appuyant directement sur le point de la leçon 8 : le chiffre d'une seule exécution porte son propre bruit.
**Source primaire :** [Doc : "Define success criteria and build evaluations", Claude Platform Docs](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests)
**Prérequis :** [Leçon 8](0008-reproducible-runs.md), [Contamination des données](../GLOSSARY.md)

## Échauffement

1. ▢ Pourquoi la même eval, exécutée deux fois à une température non nulle, peut-elle produire deux scores agrégés différents sans que rien soit anormal ?

<details markdown="1"><summary>Vérifier</summary>

L'échantillonnage à une température non nulle rend la génération stochastique, donc des complétions différentes, et donc des scores par exemple différents, sont attendus d'une exécution à l'autre. Le chiffre d'une seule exécution est un échantillon tiré d'une distribution, pas un fait fixe sur le modèle.

</details>

2. ▢ Que faut-il journaliser avec un score d'eval rapporté pour qu'une comparaison ultérieure ait un sens ?

<details markdown="1"><summary>Vérifier</summary>

Le seed aléatoire, la température de génération, les versions du modèle et du framework, la version du jeu d'eval et, quand plusieurs échantillons ont été exécutés, la dispersion entre eux, pas seulement leur moyenne.

</details>

## À savoir

### Un écart de score n'est pas automatiquement un vrai écart

Une nouvelle variante de modèle obtient 76 % contre 70 % pour une baseline sur le même jeu d'eval. Cet écart de six points ressemble à une amélioration, mais la leçon 8 a déjà établi que le score d'une seule exécution porte son propre bruit d'échantillonnage. La question à laquelle répond cette leçon : un écart de six points est-il plus grand que le bruit qui pourrait le produire par le seul hasard, ou est-ce exactement le genre de variation que deux exécutions du même modèle pourraient montrer entre elles ?

### La taille d'échantillon fixe le bruit à attendre

Pour un score de type réussite/échec sur *N* exemples, avec un vrai taux de réussite *p*, l'erreur standard de la proportion mesurée vaut approximativement `sqrt(p(1−p)/N)`. Un taux de réussite de 0,70 sur 100 exemples a une erreur standard d'environ `sqrt(0.70 × 0.30 / 100) ≈ 0.046`, soit à peu près 4,6 points de pourcentage ; un taux de réussite de 0,76 sur les mêmes 100 exemples a une erreur standard d'environ 4,3 points. Un écart de six points entre deux estimations portant chacune environ quatre à cinq points de bruit n'est pas manifestement plus grand que ce que le seul hasard pourrait produire ; davantage d'exemples réduiraient chaque erreur standard (elle décroît avec `sqrt(N)`), resserrant l'estimation et permettant de mieux distinguer une vraie différence du bruit.

### La comparaison appariée est l'outil plus précis

Traiter les deux scores comme des proportions indépendantes, comme l'a fait l'estimation ci-dessus, jette une information pourtant disponible : quand les mêmes exemples d'eval passent à la fois dans la baseline et dans la nouvelle variante, on sait non seulement combien chacune en a réussi, mais quels exemples précis chacune a réussis ou ratés. Une **comparaison appariée** regarde les exemples où les deux modèles divergent (l'un a réussi et l'autre non) plutôt que les deux taux de réussite bruts séparément. Cela élimine la difficulté propre à chaque exemple, qui touche les deux modèles de la même manière, une question que tous les modèles réussissent ou que tous ratent ne contribue en rien à savoir si un modèle est réellement meilleur que l'autre, et cela rend une vraie différence plus facile à détecter à partir de la même quantité de données qu'une comparaison de deux proportions indépendantes.

![Une grille deux par deux croisant le fait que la baseline ait réussi ou raté un exemple avec le fait que la variante l'ait réussi ou raté. Les deux réussissent et les deux ratent sont des cases d'accord, en gris : elles s'annulent. Baseline juste et variante fausse, et baseline fausse et variante juste, sont les cases de désaccord, dans la couleur d'accent : une comparaison appariée ne compte que celles-ci.](images/paired-comparison-grid.svg)

### Ce que « pas encore significatif » signifie pour un go/no-go

Un écart qui n'est pas nettement plus grand que le bruit n'est pas la preuve d'une absence de différence ; c'est la preuve qu'on n'a pas encore assez d'information pour trancher. La réponse honnête est soit d'exécuter plus d'exemples (ce qui réduit l'erreur standard), soit de lancer un vrai test de significativité apparié sur les désaccords, et non de traiter un score numériquement plus élevé comme la preuve d'une amélioration à lui seul.

## Pratique

1. ▢ Un modèle de baseline réussit 70 exemples d'eval sur 100 ; une nouvelle variante en réussit 76 sur 100. Calculez l'erreur standard approximative de chaque proportion, et dites si l'écart de six points paraît nettement plus grand que le bruit combiné.

<details markdown="1"><summary>Indice</summary>

Utilisez `sqrt(p(1−p)/N)` pour chaque proportion séparément, avec N = 100.

</details>

<details markdown="1"><summary>Vérifier</summary>

Baseline : `sqrt(0.70 × 0.30 / 100) ≈ 0.046`, environ 4,6 points. Nouvelle variante : `sqrt(0.76 × 0.24 / 100) ≈ 0.043`, environ 4,3 points. Chaque estimation porte individuellement environ quatre à cinq points de bruit, donc un écart de six points n'est pas nettement plus grand que ce que ce bruit combiné pourrait produire par hasard ; il est évocateur, pas concluant, sur 100 exemples seulement.

</details>

2. ▢ Pourquoi un jeu d'eval plus grand (plus d'exemples) permet-il de mieux distinguer une vraie différence de score du bruit ?

<details markdown="1"><summary>Vérifier</summary>

L'erreur standard d'une proportion décroît avec `sqrt(N)`, donc un N plus grand réduit le bruit de chaque estimation. Un écart qui paraissait ambigu face au bruit de 100 exemples peut devenir nettement plus grand que le bruit une fois mesuré face à, disons, 1 000 exemples, sans que la vraie différence sous-jacente ait changé.

</details>

3. ▢ Les mêmes 100 exemples d'eval passent à la fois dans une baseline et dans une nouvelle variante. Pourquoi regarder quels exemples précis chaque modèle a réussis ou ratés (une comparaison appariée) est-il plus puissant que de simplement comparer les deux taux de réussite bruts, 70 % et 76 %, comme des chiffres indépendants ?

<details markdown="1"><summary>Vérifier</summary>

Comparer les taux de réussite bruts traite chaque score comme s'il provenait d'un échantillon sans lien, en écartant le fait que les mêmes exemples ont servi pour les deux. Une comparaison appariée regarde au contraire où les deux modèles divergent, ce qui élimine la difficulté propre à chaque exemple qui touche les deux de la même manière (une question que tous les modèles réussissent ou que tous ratent ne dit rien sur le meilleur modèle), et rend une vraie différence détectable avec moins de données qu'une comparaison de proportions indépendantes n'en demande.

</details>

4. ▢ Une équipe observe un écart de score entre deux variantes de modèle qui s'avère ne pas être nettement plus grand que le bruit estimé. Quelle est la conclusion honnête, et quelles sont deux façons d'obtenir une réponse plus nette ?

<details markdown="1"><summary>Vérifier</summary>

La conclusion honnête est qu'il n'y a pas encore assez d'information pour dire si la différence est réelle, et non qu'il n'y a pas de différence. Deux façons de clarifier : exécuter l'eval sur plus d'exemples, ce qui réduit l'erreur standard de chaque estimation, ou lancer un vrai test de significativité apparié sur les exemples précis où les deux variantes divergent, plutôt que de comparer les deux taux de réussite bruts comme des chiffres indépendants.

</details>

5. ▢ Laquelle de ces affirmations est vraie du jugement sur le caractère réel d'un écart de score d'eval ?

    - a) Tout écart positif entre deux scores compte comme preuve d'amélioration, quelle que soit la taille d'échantillon
    - b) Un écart doit être jugé face au bruit que la taille d'échantillon pourrait produire par hasard, et une comparaison appariée exploite les données plus efficacement que le traitement des scores comme indépendants
    - c) La significativité statistique ne compte que pour les métriques propres à la tâche, pas pour les scores de LLM-as-judge
    - d) Un jeu d'eval plus grand ne peut jamais changer le fait qu'un écart donné paraisse significatif ou non

<details markdown="1"><summary>Vérifier</summary>

**b)** Le raisonnement bruit contre taille d'échantillon et l'avantage de la comparaison appariée sont exactement ce que couvre cette leçon. (a) est faux : un écart plus petit que le bruit estimé n'est pas une preuve solide, quel que soit son signe. (c) est faux : le même raisonnement statistique s'applique à tout score agrégé, quelle que soit la façon dont il a été noté. (d) est faux : l'erreur standard décroît avec `sqrt(N)`, donc un jeu d'eval plus grand peut transformer un écart ambigu en un écart net.

</details>

## Exercices en situation réelle

- [ ] Pour un écart de score que vous avez observé entre deux variantes de modèle, estimez l'erreur standard de chaque proportion avec la formule de cette leçon, et vérifiez si l'écart est nettement plus grand que le bruit combiné.
- [ ] Si vous avez les résultats par exemple des deux variantes sur le même jeu d'eval, regardez les exemples où elles divergent et comptez-les, comme première étape vers une comparaison appariée.
- [ ] Demain : décidez, pour une eval qui vous importe, si sa taille d'échantillon actuelle est assez grande pour détecter l'ampleur d'amélioration qui compterait vraiment pour une décision go/no-go.

## Pour aller plus loin

- [Doc : "Define success criteria and build evaluations", Claude Platform Docs](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
