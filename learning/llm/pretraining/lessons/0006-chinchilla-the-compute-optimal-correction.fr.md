---
title: "6. Chinchilla : la correction compute-optimal"
description: "Pourquoi la taille du modèle et le nombre de tokens doivent croître ensemble, et comment transformer un budget de calcul en nombre de tokens"
type: lesson
---

# Leçon 6. Chinchilla : la correction compute-optimal

**Lien avec la mission :** « Étant donné un nombre de paramètres et un budget de calcul, calculer le nombre de tokens compute-optimal et le défendre face à une alternative sous-entraînée à la Kaplan » est le troisième point sous Objectif. La leçon 5 a couvert la recommandation de Kaplan et al. ; cette leçon couvre l'étude plus large qui l'a renversée, et l'arithmétique pour l'appliquer.
**Source primaire :** [Article : "Training Compute-Optimal Large Language Models", Hoffmann et al., 2022](https://arxiv.org/abs/2203.15556)
**Prérequis :** [Leçon 5](0005-scaling-laws-what-kaplan-predicted.md)

## Échauffement

1. ▢ D'après Kaplan et al., pour un budget de calcul fixe, un entraînement optimal en efficacité de calcul signifie-t-il entraîner le plus grand modèle abordable sur comparativement peu de données, ou un modèle plus petit sur autant de données que le budget le permet ?

<details markdown="1"><summary>Vérifier</summary>

Le plus grand modèle abordable, entraîné sur comparativement peu de données et arrêté avant la convergence. Le fait que les modèles plus grands soient plus efficaces en échantillons est ce qui en fait l'allocation recommandée d'un budget fixe.

</details>

2. ▢ GPT-3 a entraîné un modèle de 175 milliards de paramètres sur 300 milliards de tokens. Cela fait approximativement combien de tokens par paramètre ?

<details markdown="1"><summary>Vérifier</summary>

Environ 1,7 token par paramètre (300 milliards divisés par 175 milliards).

</details>

## À savoir

### Un balayage bien plus large, une réponse différente

Hoffmann et al. ont mené le même genre d'étude de lois d'échelle que Kaplan et al., mais bien plus grande et plus soigneusement contrôlée : plus de 400 modèles, de 70 millions à plus de 16 milliards de paramètres, entraînés sur entre 5 milliards et 500 milliards de tokens. En ajustant une loi d'échelle sur ce balayage, ils sont arrivés à une conclusion pratique différente : pour un entraînement compute-optimal, la taille du modèle et le nombre de tokens d'entraînement doivent croître **à parts égales**. Doubler le budget de calcul signifie doubler à la fois la taille du modèle et le nombre de tokens, et non, comme l'impliquait la recommandation de Kaplan et al., dépenser presque tout le calcul supplémentaire sur un modèle plus grand.

### L'approximation qui rend cette arithmétique possible

Les deux articles utilisent la même approximation grossière du coût en calcul d'un run d'entraînement : `FLOPs(N, D) ≈ 6ND`, où `N` est le nombre de paramètres et `D` le nombre de tokens d'entraînement. Hoffmann et al. ont vérifié directement cette approximation contre un décompte de FLOPs plus exact pour une plage de tailles de modèle, et ont trouvé l'écart assez petit pour ne pas affecter leurs conclusions. Cela signifie qu'un budget de calcul `C`, un nombre de paramètres `N` et un nombre de tokens `D` ne sont pas trois choix indépendants : en fixer deux détermine le troisième, via `D ≈ C / (6N)`.

### Chinchilla, et les chiffres derrière le titre

Hoffmann et al. ont entraîné un modèle, Chinchilla, de 70 milliards de paramètres sur 1 400 milliards de tokens, avec le même calcul d'entraînement que celui qu'avait utilisé Gopher (un modèle de 280 milliards de paramètres). Cela fait environ 20 tokens pour chaque paramètre (1 400 milliards divisés par 70 milliards). Leurs propres projections d'allocation optimale pour d'autres budgets de calcul tombent dans une plage similaire sans retomber chaque fois sur exactement le même nombre : un modèle compute-optimal de 175 milliards de paramètres devrait vouloir plus de 4 200 milliards de tokens (environ 24 par paramètre), et un de 280 milliards de paramètres environ 6 800 milliards de tokens (environ 24 par paramètre) à un budget plus grand. Le bon enseignement à retenir est « environ 20 à 25 tokens par paramètre à l'allocation compute-optimal sur la plage que cet article a vérifiée », et non une constante universelle unique.

À côté de cela, les 175 milliards de paramètres de GPT-3 sur 300 milliards de tokens, environ 1,7 token par paramètre d'après l'échauffement de cette leçon, sont très en dessous de cette plage. Cet écart est exactement ce que le résumé de l'article Chinchilla veut dire en qualifiant les grands modèles de langage contemporains de « significativement sous-entraînés » : le même calcul d'entraînement aurait pu aller vers un modèle plus petit entraîné jusqu'à une loss plus basse, ou vers le modèle de même taille entraîné sur plusieurs fois plus de données, et l'un comme l'autre auraient mieux utilisé le calcul que ce qui a été réellement dépensé.

### Le résultat qui a fait tenir la correction

Entraîné au budget de calcul de Gopher mais avec un quart de son nombre de paramètres et quatre fois son nombre de tokens, Chinchilla a surpassé de façon uniforme et significative Gopher (280B), GPT-3 (175B), Jurassic-1 (178B) et Megatron-Turing NLG (530B), dont plusieurs font plusieurs fois sa taille, sur un large éventail d'évaluations en aval, y compris un 67,5 % sur MMLU alors à l'état de l'art, soit plus de 7 points au-dessus de Gopher. Faire le quart de la taille de Gopher a aussi rendu Chinchilla nettement moins cher à exécuter à l'inférence, un bénéfice distinct, au moment du déploiement, qu'apporte l'entraînement compute-optimal en plus de l'argument sur l'entraînement que développe cette leçon.

## Pratique

1. ▢ Une équipe entraîne un modèle de 13 milliards de paramètres et veut se placer dans la plage d'environ 20 à 25 tokens par paramètre de Chinchilla. Combien de tokens d'entraînement cela implique-t-il environ ?

<details markdown="1"><summary>Vérifier</summary>

Environ 260 à 325 milliards de tokens (13 milliards fois 20 à 25). L'une ou l'autre extrémité de cette plage est une réponse défendable ; un nombre bien en dehors, comme le ratio de 1,7 par paramètre de GPT-3, ne l'est pas.

</details>

2. ▢ Une équipe dispose d'un budget de calcul de `1.2 × 10^22` FLOPs et prévoit d'entraîner un modèle de 10 milliards de paramètres. En utilisant `FLOPs(N, D) ≈ 6ND`, combien de tokens ce budget permet-il environ ?

<details markdown="1"><summary>Indice</summary>

Résolvez `D ≈ C / (6N)` avec `C = 1.2 × 10^22` et `N = 10^10`.

</details>

<details markdown="1"><summary>Vérifier</summary>

Environ 200 milliards de tokens : `1.2 × 10^22 / (6 × 10^10) = 2 × 10^11`, soit 200 milliards, environ 20 tokens par paramètre et en plein dans la plage que donne cette leçon.

</details>

3. ▢ Laquelle de ces affirmations caractérise le mieux la différence pratique entre la recommandation de Kaplan et al. et la correction de Hoffmann et al., pour un budget de calcul fixe ?

    - a) Kaplan recommande de dépenser l'essentiel du budget sur un modèle plus grand avec comparativement peu de données ; Hoffmann recommande de faire croître à parts égales la taille du modèle et le nombre de tokens
    - b) Les deux articles aboutissent à des recommandations identiques, formulées seulement différemment
    - c) Kaplan dit que la taille du modèle n'a aucun rapport avec la loss ; Hoffmann dit que seule la taille du modèle compte
    - d) Hoffmann soutient qu'un modèle plus grand est toujours moins bon qu'un plus petit à calcul égal

<details markdown="1"><summary>Vérifier</summary>

**a)** est la différence réelle que parcourent cette leçon et la leçon 5. (b) efface un désaccord réel et lourd de conséquences pratiques entre les deux articles. (c) et (d) ne décrivent les affirmations d'aucun des deux articles.

</details>

4. ▢ GPT-3 a entraîné 175 milliards de paramètres sur 300 milliards de tokens, soit environ 1,7 token par paramètre. D'après la plage compute-optimal de Chinchilla, d'environ 20 à 25 tokens par paramètre, GPT-3 était-il plus proche d'un sur-entraînement ou d'un sous-entraînement sur les données, relativement à sa taille ?

<details markdown="1"><summary>Vérifier</summary>

Sous-entraîné. Son ratio est plus de dix fois inférieur à la plage que les résultats de Chinchilla impliquent être compute-optimal, ce qui signifie que le même calcul d'entraînement aurait plausiblement pu aller vers un modèle plus petit entraîné jusqu'à une loss plus basse, ou vers le même modèle de 175 milliards de paramètres entraîné sur nettement plus de données.

</details>

## Exercices en situation réelle

- [ ] Trouvez le nombre de paramètres et le nombre de tokens d'entraînement publiés pour un modèle ouvert sorti après 2022 (Llama, Mistral ou similaires publient les deux). Calculez son ratio tokens par paramètre et comparez-le à la plage d'environ 20 à 25 de cette leçon.
- [ ] En utilisant `FLOPs(N, D) ≈ 6ND`, estimez le calcul d'entraînement (en FLOPs) qu'a utilisé le vrai run d'entraînement de GPT-3 (175 milliards de paramètres, 300 milliards de tokens), et estimez séparément le calcul qu'aurait demandé un run compute-optimal de 175 milliards de paramètres à 4 200 milliards de tokens. Comparez les deux nombres.
- [ ] Demain : choisissez un budget de calcul hypothétique de votre choix (n'importe quel ordre de grandeur), et établissez sur le papier à la fois une allocation à la Kaplan (privilégier un modèle bien plus grand, garder les tokens comparativement fixes) et une allocation à la Chinchilla (faire croître les deux ensemble) pour ce même budget. Notez côte à côte les deux paires `(N, D)` obtenues.

## Pour aller plus loin

- [Article : "Training Compute-Optimal Large Language Models", Hoffmann et al., 2022](https://arxiv.org/abs/2203.15556)
- [Ressources](../RESOURCES.md)

---

Les étapes 1 et 2 ont décidé sur quoi le modèle s'entraîne et comment il est tokenisé ; cette étape a décidé quelle quantité en utiliser pour une taille donnée. L'étape 4 aborde la manière dont un run d'entraînement amène réellement autant de calcul sur plusieurs appareils à la fois.

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
