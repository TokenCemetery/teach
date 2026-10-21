---
title: "5. Les lois d'échelle : ce que Kaplan prédisait"
description: "Une loi de puissance empirique permet de prévoir la loss d'un run avant de le payer, et ce qu'elle prédisait sur la manière de dépenser un budget de calcul"
type: lesson
---

# Leçon 5. Les lois d'échelle : ce que Kaplan prédisait

**Lien avec la mission :** « Étant donné un nombre de paramètres et un budget de calcul, calculer le nombre de tokens compute-optimal et le défendre face à une alternative sous-entraînée à la Kaplan » est le troisième point sous Objectif. Cette leçon couvre ce que Kaplan et al. ont trouvé et recommandé ; la leçon 6 couvre la correction qui a changé la recommandation.
**Source primaire :** [Article : "Scaling Laws for Neural Language Models", Kaplan et al., 2020](https://arxiv.org/abs/2001.08361)
**Prérequis :** [Leçon 4](0004-sentencepiece-and-the-vocabulary-size-tradeoff.md)

## Échauffement

1. ▢ Nommez un axe sur lequel un vocabulaire de tokenizer plus grand est pire qu'un plus petit.

<details markdown="1"><summary>Vérifier</summary>

Un vocabulaire plus grand signifie une table d'embeddings et de projection de sortie plus grande (un pur nombre de paramètres), et il dilue le signal d'entraînement sur davantage de tokens distincts, si bien qu'un token précis est vu moins souvent par passe sur le même corpus.

</details>

## À savoir

### Ce qu'est réellement une loi d'échelle

Une **loi d'échelle**, dans ce contexte, est une relation empirique en loi de puissance : la loss held-out d'un modèle décroît régulièrement en fonction de la taille du modèle, de la taille du jeu de données ou du calcul d'entraînement, sur une plage assez large pour servir à la prévision. Kaplan et al. ont ajusté exactement cela, en constatant que la loss suit une loi de puissance avec chacune de ces trois quantités prise individuellement, sur des tendances couvrant plus de sept ordres de grandeur d'échelle. D'autres choix d'architecture, comme la manière de répartir un budget fixe de paramètres entre largeur et profondeur, se sont révélés compter comparativement peu dans une large plage une fois la taille du modèle elle-même prise en compte.

La valeur pratique d'une loi d'échelle est la prédiction : si la loss suit une courbe ajustée et régulière en fonction de la taille du modèle, de la taille du jeu de données et du calcul, une équipe peut prévoir approximativement les performances d'un run d'entraînement d'une taille et d'un budget donnés avant de dépenser le calcul pour le lancer, plutôt que de l'apprendre seulement après coup.

### Les modèles plus grands apprennent plus par token

L'un des résultats centraux de Kaplan et al. est que les modèles plus grands sont nettement plus efficaces en échantillons : pour atteindre une loss donnée, un modèle plus grand a besoin de voir moins de données qu'un modèle plus petit n'en aurait besoin pour atteindre cette même loss. Combiné à leurs relations ajustées entre la loss, le calcul et les deux choses que le calcul achète (un modèle plus grand, ou davantage de données pour l'entraîner), cela implique une réponse précise sur la manière de dépenser un budget de calcul fixe : un entraînement optimal en efficacité de calcul consiste à entraîner un très grand modèle sur une quantité comparativement modeste de données, et à s'arrêter bien avant de converger sur ces données, plutôt qu'à entraîner un modèle plus petit jusqu'à convergence sur davantage de données.

### À quoi ressemblait cette recommandation en pratique

Ce constat a façonné la manière dont une génération de grands modèles a réellement été entraînée : faire croître agressivement le nombre de paramètres, et garder le nombre de tokens comparativement fixe ou seulement modestement augmenté. GPT-3, par exemple, a entraîné un modèle de 175 milliards de paramètres sur 300 milliards de tokens. Cette leçon laisse ce chiffre là, sans autre commentaire ; la leçon 6 y revient directement une fois qu'on dispose d'une seconde loi d'échelle à laquelle le comparer.

## Pratique

1. ▢ Que signifie précisément que la loss « suit une loi de puissance » avec la taille du modèle, au sens où l'emploient Kaplan et al. ?

    - a) La loss diminue exactement de la même quantité fixe pour chaque augmentation fixe de la taille du modèle
    - b) La loss décroît régulièrement en suivant une courbe ajustée, valable sur une large plage de tailles de modèle, ce qui rend la prévision possible
    - c) La loss devient nulle dès que le modèle est assez grand
    - d) La loss ne dépend que de la taille du modèle et pas du tout de la quantité de données d'entraînement

<details markdown="1"><summary>Vérifier</summary>

**b)** Un ajustement en loi de puissance assez régulier, et validé sur assez d'ordres de grandeur, pour permettre la prévision. (a) décrit une relation linéaire, pas une loi de puissance. (c) n'est affirmé nulle part dans l'article. (d) contredit le résultat distinct de l'article, une loi d'échelle avec la taille du jeu de données.

</details>

2. ▢ D'après Kaplan et al., lequel atteint une loss cible fixée avec moins de données d'entraînement : un modèle plus grand ou un plus petit ?

<details markdown="1"><summary>Vérifier</summary>

Un modèle plus grand. Les modèles plus grands sont plus efficaces en échantillons, c'est-à-dire qu'ils ont besoin de moins de données pour atteindre la même loss qu'un modèle plus petit n'atteindrait qu'avec davantage de données.

</details>

3. ▢ Étant donné un budget de calcul fixe et les résultats de Kaplan et al., quelle allocation leur analyse recommande-t-elle : un très grand modèle entraîné sur comparativement peu de données et arrêté bien avant la convergence, ou un modèle plus petit entraîné jusqu'à convergence sur autant de données que le budget le permet ?

<details markdown="1"><summary>Indice</summary>

Cela découle directement de la combinaison de « les modèles plus grands sont plus efficaces en échantillons » avec un budget de calcul fixe : le calcul dépensé sur les données n'est pas dépensé sur la taille du modèle, et l'article a constaté que l'un de ces deux usages du calcul rapportait plus que l'autre.

</details>

<details markdown="1"><summary>Vérifier</summary>

Le très grand modèle entraîné sur comparativement peu de données, arrêté avant la convergence. C'est la recommandation énoncée par Kaplan et al. eux-mêmes pour un entraînement optimal en efficacité de calcul sous un budget fixe.

</details>

## Exercices en situation réelle

- [ ] Trouvez le nombre de paramètres et le nombre de tokens d'entraînement déclaré pour deux ou trois modèles connus sortis dans l'année ou les deux ans qui ont suivi l'article de Kaplan (de 2020 à 2022 environ). Notez si leur nombre de tokens est resté à peu près fixe pendant que le nombre de paramètres croissait, ce à quoi ressemblerait le fait de suivre la recommandation de cette leçon.
- [ ] Relisez encore une fois le résumé de l'article de Kaplan (lié plus haut) et énoncez, en une phrase, ce que signifie « s'arrêter nettement avant la convergence » pour un run d'entraînement : qu'achèterait réellement la poursuite de l'entraînement, que cette recommandation juge ne pas valoir son calcul ?
- [ ] Demain : sans regarder la leçon 6, écrivez une prédiction d'une phrase : sachant que la construction du jeu de données (étape 1 de ce parcours) est coûteuse et lente à faire passer à l'échelle, alors que le simple nombre de paramètres est comparativement facile à faire croître en ajoutant des accélérateurs, quelle pression pratique a pu pousser les vrais runs d'entraînement vers la recommandation de Kaplan encore plus fort que ne le justifiaient les seules courbes de loss ?

## Pour aller plus loin

- [Article : "Scaling Laws for Neural Language Models", Kaplan et al., 2020](https://arxiv.org/abs/2001.08361)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
