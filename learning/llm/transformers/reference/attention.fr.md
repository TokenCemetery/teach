---
title: "Attention"
description: "Scaled dot-product attention, multi-head attention et masquage causal, avec les formes des tenseurs annotées à chaque étape"
type: reference
---

# Attention : scaled dot-product, multi-head et masquage causal

L'étape 1 condensée pour la consultation. La [leçon 1](../lessons/0001-scaled-dot-product-attention.md) couvre l'équation centrale ; la [leçon 2](../lessons/0002-multi-head-attention.md) couvre son exécution dans des sous-espaces parallèles ; la [leçon 3](../lessons/0003-causal-masking.md) couvre sa restriction au passé. Cette fiche rassemble côte à côte les équations et les formes.

## Scaled dot-product attention

```text
Attention(Q, K, V) = softmax(QK^T / sqrt(d_k)) V
```

| Étape | Forme en entrée | Forme en sortie | Remarque |
|---|---|---|---|
| `Q`, `K`, `V` donnés | n/a | `[n, d_k]`, `[m, d_k]`, `[m, d_v]` | `n` requêtes, `m` paires clé/valeur ; `d_k` est la dimension des clés et des requêtes |
| `QK^T` | `[n, d_k] × [d_k, m]` | `[n, m]` | un score de similarité par paire requête-clé |
| `/ sqrt(d_k)` | `[n, m]` | `[n, m]` | compense la croissance de la variance avec `d_k`, garde le gradient du softmax exploitable |
| `softmax(...)` (par ligne) | `[n, m]` | `[n, m]` | chaque ligne est désormais une distribution de probabilité de somme 1 |
| `× V` | `[n, m] × [m, d_v]` | `[n, d_v]` | un vecteur de sortie par requête, un mélange pondéré des valeurs |

La self-attention est le cas où `Q`, `K`, `V` viennent tous de la même séquence (`n = m`), chaque position portant son attention sur toutes les positions, elle-même comprise.

**Pourquoi la mise à l'échelle.** La variance du produit scalaire croît avec `d_k`, ce qui pousse le softmax vers des sorties presque one-hot où son gradient est quasiment plat et où l'entraînement cale. `/ sqrt(d_k)` compense cette croissance quelle que soit la taille de `d_k`.

## Multi-head attention

```text
Q_i = X W_Q^i,   K_i = X W_K^i,   V_i = X W_V^i          (per head i, i = 1..h)
head_i = Attention(Q_i, K_i, V_i)
MultiHead(Q, K, V) = Concat(head_1, ..., head_h) W_O
```

| Étape | Forme en entrée | Forme en sortie | Remarque |
|---|---|---|---|
| Entrée `X` | n/a | `[n, d_model]` | |
| Projection par tête (`W_Q^i`, `W_K^i`, `W_V^i`) | `[n, d_model] × [d_model, d_k]` | `[n, d_k]` par tête, `d_k = d_model / h` | les projections de chaque tête sont apprises indépendamment |
| `head_i = Attention(Q_i, K_i, V_i)` | `[n, d_k]` chacun | `[n, d_k]` | l'équation exacte ci-dessus, exécutée une fois par tête |
| `Concat(head_1, ..., head_h)` | `h × [n, d_k]` | `[n, d_model]` | place les têtes côte à côte, pas encore d'interaction entre têtes |
| `× W_O` | `[n, d_model] × [d_model, d_model]` | `[n, d_model]` | la seule étape qui permet à l'information de têtes différentes de se combiner |

**La formule de mise à l'échelle utilise le `d_k` par tête, pas `d_model`.** Les produits scalaires de chaque tête sont sommés sur sa propre dimension, plus petite, c'est donc la variance que la mise à l'échelle doit compenser, quelle que soit la taille du modèle complet.

**`W_O` n'est pas facultative.** La concaténation seule place les sorties côte à côte sans interaction ; `W_O` est le seul endroit où l'information de têtes différentes peut se combiner en une seule représentation.

## Masquage causal

Ajouté aux scores bruts, avant le softmax :

```text
scores = QK^T / sqrt(d_k)
scores[i, j] += -inf   for every j > i     (a fixed lower-triangular pattern)
Attention(Q, K, V) = softmax(scores) V
```

| Choix | Pourquoi |
|---|---|
| Masquer avant le softmax, pas après | Mettre un poids à zéro après l'exécution du softmax laisse les poids restants avec une somme inférieure à 1, ce qui n'est pas une distribution valide. Masquer le score laisse la renormalisation se faire automatiquement dans le même softmax |
| Un grand nombre négatif, pas `0` | `exp(0) = 1`, une valeur ordinaire et non négligeable qui reste en concurrence pour la masse de probabilité. Seul un nombre négatif assez grand fait tomber `exp(...)` pratiquement à zéro |
| Le même masque pour chaque tête et chaque exemple d'un batch | La restriction (la position de requête `i` peut porter son attention sur les positions de clé `0..i`) est une propriété de la tâche, pas d'une tête en particulier |

À l'inférence, un modèle génère le token `N` à partir des seuls tokens `1..N-1` ; laisser la position `i` porter son attention sur une position ultérieure `j` pendant l'entraînement permet au modèle d'utiliser une réponse qu'il n'aura jamais au moment de la génération. La loss d'entraînement paraît bonne dans ce cas, mais le modèle n'apprend rien de transférable.

## Avant de faire confiance à une implémentation de l'attention

- [ ] Le diviseur de mise à l'échelle est le `d_k` par tête (`d_model / h`), pas le `d_model` complet.
- [ ] `W_O` est appliquée après la concaténation des têtes, et non omise.
- [ ] Le masque causal est ajouté aux scores bruts avant le softmax, et non appliqué aux poids après.
- [ ] La valeur du masque est un grand nombre négatif (ou `-inf`), pas `0`.
- [ ] La forme de sortie est `[n, d_model]` quel que soit le nombre de têtes, puisque les têtes ne changent que la dimension intermédiaire par tête.

## Sources

- [Article : "Attention Is All You Need", Vaswani et al., 2017](https://arxiv.org/abs/1706.03762)
- [Billet : "The Annotated Transformer", Harvard NLP](http://nlp.seas.harvard.edu/annotated-transformer/)
- [Billet : "The Illustrated Transformer", Jay Alammar](https://jalammar.github.io/illustrated-transformer/)
- [Ressources](../RESOURCES.md)
