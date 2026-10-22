---
title: "Le bloc transformer"
description: "Encodage positionnel, layer norm et connexions résiduelles, bloc feed-forward, et empilement des blocs en un modèle complet avec embedding, sortie et weight tying"
type: reference
---

# Le bloc transformer : d'un seul bloc au modèle complet

Les étapes 2 et 3 condensées pour la consultation. La [leçon 4](../lessons/0004-positional-encoding.md) couvre l'injection de la position dans les embeddings ; la [leçon 5](../lessons/0005-layer-norm-and-residuals.md) couvre les résiduels et la layer norm ; la [leçon 6](../lessons/0006-feed-forward-block.md) couvre la sous-couche feed-forward ; la [leçon 7](../lessons/0007-stacking-blocks.md) couvre l'empilement des blocs en profondeur ; la [leçon 8](../lessons/0008-embedding-output-and-weight-tying.md) couvre l'entrée dans l'espace vectoriel du modèle et la sortie de cet espace. Cette fiche rassemble côte à côte les formules, les formes et les choix.

## Encodage positionnel

L'attention n'a aucune notion d'ordre par elle-même ; échanger deux positions réétiquette simplement la sortie. La position doit être inscrite dans les embeddings eux-mêmes, avant même que l'attention s'exécute.

```text
PE(pos, 2i)   = sin(pos / 10000^(2i / d_model))
PE(pos, 2i+1) = cos(pos / 10000^(2i / d_model))
```

| Schéma | Se généralise à des longueurs de séquence inconnues | Implémentation |
|---|---|---|
| Sinusoïdal (formule fixe) | Oui, la formule s'évalue à n'importe quelle position | Aucun paramètre à apprendre |
| Embedding de position appris | Non, n'a de lignes que pour les positions vues à l'entraînement | Une table de recherche, entraînée comme n'importe quel autre paramètre |

## Connexions résiduelles et layer norm

```text
post-norm: LayerNorm(x + Sublayer(x))
pre-norm:  x + Sublayer(LayerNorm(x))
```

| Pièce | Résout | Indépendante de |
|---|---|---|
| Résiduel (`+ x`) | La diminution ou l'explosion du gradient à travers une pile profonde, en lui donnant un chemin identité direct à chaque couche | La transformation propre de la sous-couche |
| Layer norm | La dérive de l'échelle des activations d'une couche à l'autre, en normalisant le vecteur de features propre à chaque token (moyenne et variance sur les features, puis échelle et décalage appris) | La taille du batch, contrairement à la batch norm, qui a besoin des statistiques de nombreux exemples |

**Pre-norm plutôt que post-norm.** Le pre-norm garde le chemin résiduel lui-même entièrement non normalisé de bout en bout, une connexion identité sans obstacle ; le post-norm normalise la somme résiduelle à chaque couche, ce qui perturbe ce chemin. Le pre-norm est ce qu'utilisent la plupart des grands modèles actuels, malgré le choix du post-norm dans l'article d'origine.

## Le bloc feed-forward

```text
FFN(x) = max(0, x W1 + b1) W2 + b2
```

| Étape | Forme en entrée | Forme en sortie | Remarque |
|---|---|---|---|
| `x W1 + b1`, non-linéarité | `[n, d_model] × [d_model, d_ff]` | `[n, d_ff]` | `d_ff` couramment 4x `d_model` (512 vers 2048 dans l'article d'origine) ; ReLU à l'origine, GELU/SwiGLU dans les architectures ultérieures |
| `... W2 + b2` | `[n, d_ff] × [d_ff, d_model]` | `[n, d_model]` | reprojette vers le bas pour que le résultat s'ajoute au flux résiduel |

Appliqué de façon identique, avec les mêmes poids, à chaque position séparément, aucune position ne voit jamais le vecteur d'une autre ici. C'est le complément exact de l'attention : l'attention mélange entre les positions mais est linéaire en les valeurs une fois ses poids calculés ; le bloc feed-forward est l'endroit où la représentation propre d'une seule position reçoit un remodelage réellement non linéaire.

## Empiler des blocs

| Propriété | Ce que cela signifie | Pourquoi c'est important |
|---|---|---|
| Conserve la forme | Chaque bloc prend `d_model` en entrée et produit `d_model` en sortie | La sortie du bloc N devient l'entrée du bloc N+1 sans adaptateur ; la même forme de bloc s'empile un nombre quelconque de fois |
| Sans partage de poids | Chaque bloc a ses propres paramètres, appris indépendamment | Coûte des paramètres à peu près linéairement avec la profondeur ; permet à des blocs différents de se spécialiser à des profondeurs différentes |
| Flux résiduel | Un seul vecteur courant traverse chaque bloc, chacun y ajoutant sa propre contribution | C'est exactement ce que le dispositif résiduel et de layer norm de la leçon 5 protège quand la profondeur atteint des dizaines de blocs |

## Embedding, sortie et weight tying

| Couche | Forme | Rôle |
|---|---|---|
| Embedding d'entrée | `vocab_size × d_model` | La ligne `i` est le vecteur appris du token `i` ; la chercher est une recherche, pas une transformation calculée |
| Projection de sortie | `d_model × vocab_size` | Produit un logit par token du vocabulaire et par position |

Les deux formes sont transposées l'une de l'autre. Le **weight tying** réutilise la matrice d'embedding, transposée, comme projection de sortie (`logits = h @ W_embedding^T`) au lieu d'apprendre une seconde matrice, au motif que les deux couches rattachent un token à la même représentation sous-jacente.

Exemple travaillé : vocabulaire de 50 000, `d_model = 768`. Table d'embedding : `50,000 × 768 = 38,400,000` paramètres. Une couche de sortie sans tying a besoin d'une seconde matrice de cette taille ; le tying la supprime, ce qui économise ici environ 38,4 millions de paramètres sans perte de qualité, et souvent avec un gain mesurable.

## Avant de faire confiance à une implémentation du modèle complet

- [ ] L'encodage positionnel est ajouté aux embeddings de tokens avant le premier bloc, et non injecté d'une autre façon dans l'attention.
- [ ] Chaque sous-couche est enveloppée dans une connexion résiduelle, et le placement de la layer norm (pre- ou post-) est un choix délibéré, et non ce qu'un tutoriel a utilisé par hasard.
- [ ] Les deux couches du bloc feed-forward étendent puis contractent (`d_model` vers `d_ff` vers `d_model`), et ses poids ne sont jamais partagés entre positions.
- [ ] Chaque bloc de la pile prend et renvoie `d_model`, et a ses propres poids appris indépendamment.
- [ ] Si le weight tying est utilisé, la projection de sortie est la matrice d'embedding transposée, et non une seconde matrice apprise.

## Sources

- [Article : "Attention Is All You Need", Vaswani et al., 2017](https://arxiv.org/abs/1706.03762)
- [Article : "Layer Normalization", Ba, Kiros et Hinton, 2016](https://arxiv.org/abs/1607.06450)
- [Article : "On Layer Normalization in the Transformer Architecture", Xiong et al., 2020](https://arxiv.org/abs/2002.04745)
- [Article : "Using the Output Embedding to Improve Language Models", Press et Wolf, 2017](https://arxiv.org/abs/1608.05859)
- [Ressources](../RESOURCES.md)
