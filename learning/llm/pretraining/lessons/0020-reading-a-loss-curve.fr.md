---
title: "20. Lire une courbe de loss"
description: "La seule courbe de loss d'entraînement sous-estime les problèmes ; deux autres signaux repèrent ce qu'elle rate, et le repèrent plus tôt"
type: lesson
---

# Leçon 20. Lire une courbe de loss

**Lien avec la mission :** « Savoir lire un tableau de bord d'entraînement et dire si le run est sur la bonne voie » est la case « Terminée quand » de cette étape dans « Le fil conducteur ». Cette leçon couvre ce qu'il faut réellement surveiller sur un tableau de bord en direct ; la leçon 21 couvre l'évaluation de checkpoints sauvegardés sur des données held-out.
**Source primaire :** [Article : "Scaling Language Models: Methods, Analysis & Insights from Training Gopher", Rae et al., 2021](https://arxiv.org/abs/2112.11446)
**Prérequis :** [Leçon 19](0019-surviving-a-node-failure.md)

## Échauffement

1. ▢ Qu'ont remarqué Zhang et al. qui était corrélé à la divergence de la loss pendant l'entraînement d'OPT-175B, en dehors de la courbe de loss elle-même ?

<details markdown="1"><summary>Vérifier</summary>

Leur loss scalar dynamique (une partie de la configuration en précision mixte) tombant à zéro, et la norme des activations de la dernière couche qui faisait un pic.

</details>

2. ▢ Pourquoi se remettre d'une divergence de la loss plaide-t-il pour garder plus que le seul checkpoint le plus récent ?

<details markdown="1"><summary>Vérifier</summary>

Parce que le meilleur point de redémarrage était choisi d'après la santé du loss scalar et la tendance de la norme des activations, ce qui n'était pas toujours le checkpoint le plus récent ; ne garder que le plus récent supprimerait la possibilité de revenir plus loin en arrière.

</details>

## À savoir

### La courbe de loss d'entraînement, et ce que « sain » signifie pour elle

La chose la plus élémentaire qu'un tableau de bord d'entraînement montre est la loss d'entraînement elle-même, tracée en fonction du pas d'entraînement ou du nombre de tokens. Les lois d'échelle de l'étape 3 donnent une vraie attente pour sa forme : la loss doit décroître régulièrement, en suivant à peu près une courbe de type loi de puissance à mesure que le calcul et les tokens s'accumulent, ni en ligne droite ni par une suite de sauts sans rapport. Une courbe qui suit cette forme générale se comporte comme prévu ; une courbe qui se aplatit bien plus tôt que ne le prédirait la trajectoire de la loi d'échelle, ou qui montre une hausse soudaine et brutale (un pic de loss, leçon 16), est une courbe de loss d'entraînement qui signale quelque chose qui mérite investigation, avant de présumer que le run est simplement sur la bonne voie.

### Deux signaux qui repèrent le problème avant que la courbe de loss ne le montre clairement

Surveiller la seule loss d'entraînement ne suffit pas, parce que le temps qu'un pic soit visible dans la loss elle-même, le problème sous-jacent a peut-être déjà couvé depuis un moment. Le récit d'OPT-175B de Zhang et al. donne deux autres signaux qui ont averti plus tôt du même problème que la courbe de loss a fini par montrer : leur **loss scalar dynamique**, une partie de la configuration en précision mixte, qui tombe vers zéro, et la **norme des activations de la dernière couche** qui fait un pic vers le haut. Les deux sont des symptômes d'un run d'entraînement qui se dirige vers l'instabilité, visibles avant, ou en même temps que, la divergence nette de la loss elle-même, et c'est exactement pourquoi Zhang et al. les ont utilisés, et pas seulement la courbe de loss, pour juger si un point donné de l'entraînement était sûr pour redémarrer.

### La norme du gradient, surveillée dans le temps

La leçon 16 a couvert le clipping de la norme du gradient comme protection par pas, qui borne l'ampleur d'une mise à jour donnée. La même norme du gradient, surveillée comme une courbe sur le cours de l'entraînement plutôt que seulement comparée au seuil de clipping à chaque pas, est elle-même un signal utile : une norme de gradient qui monte avec le temps, ou qui fait des pics répétés même après clipping, peut être un signe précoce du même genre d'instabilité qu'un pic de loss montrerait plus tard de façon plus dramatique, et donner une chance d'intervenir, par exemple en baissant le learning rate, avant qu'une divergence complète n'impose un redémarrage.

### Surveiller, en continu

Aucun de ces signaux n'aide si personne, ou aucun automate, ne les regarde réellement. L'étape 8 a établi que les pannes et les instabilités sont une partie courante et fréquente d'un grand run d'entraînement, et non un événement rare ; un tableau de bord montrant la loss, la norme du gradient et un signal de stabilité numérique comme un loss scalar n'est utile que s'il est consulté assez souvent, ou s'il alerte assez automatiquement, pour attraper un problème naissant avant qu'il ne coûte bien plus de progression qu'une détection plus précoce.

## Pratique

1. ▢ La courbe de loss d'entraînement d'une équipe décroît, mais nettement plus lentement que ne le prédiraient les relations de loi d'échelle de l'étape 3 pour la taille de leur modèle et leur nombre de tokens à ce stade. Est-ce nécessairement le signe d'un problème, ou cela pourrait-il être compatible avec un run sain ?

<details markdown="1"><summary>Indice</summary>

Les lois d'échelle sont des ajustements empiriques avec une vraie variance, et non une garantie exacte pour chaque run individuel.

</details>

<details markdown="1"><summary>Vérifier</summary>

Cela mérite investigation plutôt que de présumer que tout va bien, mais ce n'est pas automatiquement la preuve d'un problème ; les lois d'échelle sont des tendances ajustées avec de la variance, et non une garantie exacte par run. Un écart significatif et durable par rapport à la trajectoire attendue est une raison légitime de vérifier d'autres signaux (la norme du gradient, un loss scalar si on utilise la précision mixte, ou le pipeline de données lui-même) plutôt que de présumer que la courbe seule tranche la question dans un sens ou dans l'autre.

</details>

2. ▢ Pourquoi un loss scalar qui tombe vers zéro, ou une norme d'activation qui fait un pic, pourraient-ils avertir plus tôt de l'instabilité que la courbe de loss d'entraînement elle-même ?

<details markdown="1"><summary>Vérifier</summary>

Ce sont des symptômes du problème numérique sous-jacent en train de se développer, qui peuvent apparaître avant qu'il ne devienne assez grand pour perturber visiblement la courbe de loss. Le temps qu'un pic soit clairement visible dans la loss elle-même, le problème a peut-être déjà couvé pendant un certain temps.

</details>

3. ▢ Laquelle de ces affirmations décrit le mieux pourquoi un tableau de bord qui suit la loss, la norme du gradient et un signal de stabilité comme un loss scalar n'est utile en pratique que s'il est surveillé fréquemment ?

    - a) Ces métriques n'ont de sens qu'une fois par run d'entraînement, tout à la fin
    - b) Les pannes et les instabilités sont des événements fréquents et courants à grande échelle (étape 8), si bien qu'un problème attrapé tard coûte bien plus de progression perdue que le même problème attrapé tôt
    - c) Les métriques elles-mêmes changent de sens si on les consulte trop souvent
    - d) Une surveillance fréquente n'est utile que pour de très petits modèles

<details markdown="1"><summary>Vérifier</summary>

**b)** est le raisonnement réel : étant donné la fréquence des pannes et des instabilités à grande échelle, la valeur d'un tableau de bord est directement liée à la rapidité avec laquelle un problème naissant est remarqué. (a), (c) et (d) ne reflètent rien de ce qu'ont établi cette leçon ou l'étape 8.

</details>

## Exercices en situation réelle

- [ ] Trouvez le tableau de bord d'un framework d'entraînement ou d'un outil de suivi d'expériences (Weights & Biases, TensorBoard ou similaire) et identifiez lesquels des signaux de cette leçon (loss, norme du gradient, un indicateur de stabilité numérique) il affiche par défaut, et lesquels devraient être ajoutés explicitement.
- [ ] Lisez le paragraphe de l'article OPT (lié plus haut) qui relie la divergence de la loss au loss scalar et à la norme des activations, et écrivez une phrase sur le signal que vous vérifieriez en premier si vous voyiez un pic de loss sur un tableau de bord où les trois sont disponibles.
- [ ] Demain : sans regarder la suite, écrivez une prédiction d'une phrase pour la leçon 21 : si la loss d'entraînement seule ne dit pas dans quelle mesure un modèle réussit les tâches pour lesquelles les gens l'utiliseront réellement, que faudrait-il mesurer différemment pour le vérifier pendant l'entraînement, et pas seulement après qu'il est terminé ?

## Pour aller plus loin

- [Article : "Scaling Language Models: Methods, Analysis & Insights from Training Gopher", Rae et al., 2021](https://arxiv.org/abs/2112.11446)
- [Article : "OPT: Open Pre-trained Transformer Language Models", Zhang et al., 2022](https://arxiv.org/abs/2205.01068)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
