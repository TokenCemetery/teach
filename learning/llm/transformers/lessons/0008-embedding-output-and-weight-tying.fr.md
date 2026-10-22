---
title: "8. Couches d'embedding et de sortie, weight tying"
description: "Comment les tokens entrent dans l'espace vectoriel du transformer et en sortent, et pourquoi les deux couches qui s'en chargent peuvent partager une seule matrice"
type: lesson
---

# Leçon 8. Couches d'embedding et de sortie, weight tying

**Lien avec la mission :** C'est la leçon de clôture de l'étape 3 : les blocs empilés (leçon 7) opèrent entièrement sur des vecteurs de dimension `d_model`, donc il faut bien que quelque chose convertisse les tokens discrets vers cet espace à l'entrée, puis vers des scores sur le vocabulaire à la sortie, ce qui boucle la chaîne des identifiants de tokens bruts jusqu'à une passe avant complète.
**Source primaire :** [Article : "Using the Output Embedding to Improve Language Models", Press et Wolf, 2017](https://arxiv.org/abs/1608.05859)
**Prérequis :** [Leçon 7](0007-stacking-blocks.md), [Scaled dot-product attention](../GLOSSARY.md)

## Échauffement

1. ▢ Pourquoi chaque bloc transformer doit-il conserver la même dimension d'entrée et de sortie (`d_model` en entrée, `d_model` en sortie) ?

<details markdown="1"><summary>Vérifier</summary>

Empiler signifie que la sortie d'un bloc alimente directement l'entrée du bloc suivant ; si un bloc changeait la dimension, chaque bloc suivant et le flux résiduel devraient être construits pour une autre taille, ce qui casserait l'empilement uniforme qui permet de répéter la même forme de bloc un nombre quelconque de fois.

</details>

2. ▢ Les poids d'un bloc d'une pile de transformer standard sont-ils les mêmes que ceux d'un autre bloc ? Que cela coûte-t-il, et qu'est-ce que cela apporte ?

<details markdown="1"><summary>Vérifier</summary>

Non, chaque bloc a ses propres paramètres, appris indépendamment. Cela coûte du nombre de paramètres, à peu près linéairement avec la profondeur, puisque rien n'est partagé, mais cela permet aux différents blocs de se spécialiser différemment à différentes profondeurs plutôt que de calculer tous la même transformation.

</details>

## À savoir

### L'embedding d'entrée : une recherche de l'identifiant du token vers un vecteur

Un tokenizer (nommé ici en passant ; c'est le domaine de `llm/finetuning` pour le dériver plus loin) produit une séquence d'identifiants de tokens entiers, chacun étant un indice dans un vocabulaire fixe. La **couche d'embedding d'entrée** est une matrice apprise de forme `vocab_size × d_model` : la ligne `i` est la représentation vectorielle dense du token `i`. Chercher l'embedding d'un token consiste simplement à lire sa ligne. C'est là que des tokens discrets et symboliques entrent dans l'espace vectoriel continu sur lequel opèrent réellement toutes les pièces suivantes, l'attention, le bloc feed-forward, l'encodage positionnel.

### La couche de sortie : reprojeter vers des scores sur le vocabulaire

Une fois que le dernier bloc empilé a produit sa sortie, toujours de dimension `d_model` par position, le modèle a besoin d'une étape de plus pour transformer ce vecteur en une prédiction sur le vocabulaire. La **couche de sortie** est une projection linéaire de forme `d_model × vocab_size`, qui produit un score brut, appelé **logit**, par token du vocabulaire à chaque position. Ces logits (transformés en distribution de probabilité par la loss d'entropie croisée de la leçon suivante) sont ce que « prédire le token suivant » signifie réellement sur le plan numérique : un vecteur de scores de la taille du vocabulaire, un par token possible.

### Les formes des deux couches sont transposées l'une de l'autre

La matrice d'embedding d'entrée est de forme `vocab_size × d_model` ; la projection de sortie est de forme `d_model × vocab_size`, exactement la forme transposée. Le **weight tying** exploite directement cela : au lieu d'apprendre une matrice de sortie entièrement séparée, le modèle réutilise la même matrice d'embedding, transposée, pour calculer les logits de sortie (`logits = h @ W_embedding^T`). Ce n'est pas une simple coïncidence exploitée par commodité ; les deux couches rattachent un token à essentiellement la même question sous-jacente, l'embedding d'entrée répond à « quel vecteur représente le token X », et la couche de sortie répond à « quelle est la probabilité du token X », et le tying les traite comme partageant une seule représentation plutôt qu'en apprenant deux représentations séparées et sans lien.

![Deux schémas côte à côte. À gauche, un identifiant de token cherche sa ligne dans la matrice d'embedding, de forme vocab_size par d_model, ce qui produit un vecteur d'embedding. À droite, un vecteur caché est projeté par la même matrice, transposée en d_model par vocab_size, ce qui produit un vecteur de logits, un score par token du vocabulaire. Une ligne en pointillés relie les deux matrices, étiquetée même matrice de poids, transposée, pour montrer que le weight tying réutilise une seule matrice apprise à la fois pour la recherche en entrée et pour la projection en sortie, au lieu d'en apprendre deux séparées.](images/weight-tying-embedding-output.svg)

### Ce que le tying économise réellement

Pour un vocabulaire de 50 000 tokens et `d_model = 768`, la seule table d'embedding contient `50,000 × 768 = 38,400,000` paramètres. Un modèle sans tying aurait besoin d'une seconde matrice de même taille pour la projection de sortie, 38,4 millions de paramètres de plus pour un rôle très proche. Le tying supprime cette seconde matrice entière, et pour des modèles dont le vocabulaire est grand par rapport à la taille cachée, cela représente une fraction substantielle du nombre total de paramètres du modèle, économisée pour essentiellement aucune perte, et souvent un gain mesurable, de qualité.

## Pratique

1. ▢ Quelle est la forme de la matrice de poids de la couche d'embedding d'entrée, et à quoi correspond structurellement la recherche de l'embedding d'un token précis ?

<details markdown="1"><summary>Vérifier</summary>

`vocab_size × d_model`. Chercher l'embedding d'un token consiste à lire la ligne de la matrice située à l'indice de ce token, une recherche directe plutôt qu'une transformation calculée.

</details>

2. ▢ Comment la forme de la couche de sortie se rapporte-t-elle à celle de la couche d'embedding d'entrée, et que rend possible ce rapport ?

<details markdown="1"><summary>Vérifier</summary>

La forme de la couche de sortie (`d_model × vocab_size`) est la transposée de celle de l'embedding d'entrée (`vocab_size × d_model`). Ce rapport est ce qui rend le weight tying possible : la même matrice, utilisée dans un sens comme table de recherche et dans l'autre sens (transposée) comme projection, peut jouer les deux rôles au lieu de nécessiter deux matrices apprises séparément.

</details>

3. ▢ Pour un vocabulaire de 50 000 tokens et `d_model = 768`, calculez le nombre de paramètres de la table d'embedding, et expliquez ce que le weight tying économise par rapport à un modèle sans tying.

<details markdown="1"><summary>Indice</summary>

Le nombre de paramètres de la table d'embedding est `vocab_size × d_model`. Une couche de sortie sans tying aurait besoin d'une matrice de même taille.

</details>

<details markdown="1"><summary>Vérifier</summary>

`50,000 × 768 = 38,400,000` paramètres pour la table d'embedding. Un modèle sans tying aurait besoin d'une seconde matrice, apprise séparément, de la même taille pour la projection de sortie ; le tying supprime cette seconde matrice entière et économise environ 38,4 millions de paramètres pour ce vocabulaire et cette taille cachée.

</details>

4. ▢ Au-delà de l'économie de paramètres, quelle est la raison de fond pour laquelle lier les matrices de poids d'entrée et de sortie a du sens, au lieu d'être un simple truc pratique ?

<details markdown="1"><summary>Vérifier</summary>

Les deux couches rattachent un token à fondamentalement la même représentation : l'embedding d'entrée répond à « quel vecteur représente ce token », et la couche de sortie répond à « quelle est la probabilité de ce token, étant donné la représentation courante ». Comme les deux questions portent sur la même relation entre token et vecteur, partager une seule représentation apprise entre elles est un biais inductif raisonnable, et pas seulement un moyen de réduire les paramètres.

</details>

5. ▢ Quelle affirmation est vraie des couches d'embedding d'entrée et de sortie ?

    - a) Elles doivent toujours être apprises comme deux matrices entièrement séparées, puisqu'elles servent des buts sans rapport
    - b) Leurs formes sont transposées l'une de l'autre, ce qui rend possible le weight tying, c'est-à-dire la réutilisation d'une seule matrice pour les deux
    - c) Le weight tying ne fait qu'économiser des paramètres et n'apporte aucun autre bénéfice
    - d) La forme de la couche de sortie dépend de `vocab_size` seul, sans rapport avec `d_model`

<details markdown="1"><summary>Vérifier</summary>

**b)** Le rapport de formes transposées est exactement ce qu'exploite le tying. (a) est faux : c'est précisément ce que le tying évite d'avoir à faire. (c) est faux : on soutient aussi que le tying aide la qualité, puisque les deux couches se rapportent à la même représentation sous-jacente des tokens. (d) est faux : la forme de la couche de sortie est `d_model × vocab_size`, elle dépend des deux.

</details>

## Exercices en situation réelle

- [ ] Implémentez d'abord la recherche d'embedding d'entrée et la projection de sortie comme deux matrices séparées, puis modifiez votre implémentation pour les lier et vérifiez que la forme des logits de sortie est inchangée.
- [ ] Pour un modèle que vous connaissez, cherchez sa taille de vocabulaire et son `d_model`, et calculez combien de paramètres le weight tying économiserait par rapport à une version sans tying.
- [ ] Demain : vérifiez si une vraie implémentation de modèle à laquelle vous avez accès (dans la bibliothèque `transformers` ou ailleurs) lie ses poids d'embedding et de sortie, et trouvez où cela est configuré dans le code.

## Pour aller plus loin

- [Article : "Using the Output Embedding to Improve Language Models", Press et Wolf, 2017](https://arxiv.org/abs/1608.05859)
- [Article : "Attention Is All You Need", Vaswani et al., 2017](https://arxiv.org/abs/1706.03762)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
