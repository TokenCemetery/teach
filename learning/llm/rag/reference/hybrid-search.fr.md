---
title: "Recherche hybride"
description: "Le score de statistiques de termes de BM25, pourquoi il compte encore à côté de la recherche vectorielle, et la reciprocal rank fusion comme moyen de les combiner indépendant de l'échelle"
type: reference
---

# Recherche hybride

Combiner des classements lexicaux et vectoriels. Conçu pour la consultation lors de la mise en place ou du réglage d'un mélange hybride.

## BM25 note le recouvrement des termes, pas le sens

Une fonction de classement purement lexicale, sans embedding, sans aucune notion de sens. Trois ingrédients :

| Ingrédient | Ce qu'il fait |
|---|---|
| Fréquence inverse de document (IDF) | Pondère un terme de la requête selon sa rareté dans le corpus ; un mot courant comme « le » ne contribue presque à rien |
| Fréquence du terme, avec saturation | Plus d'occurrences d'un terme augmentent le score, mais avec des rendements décroissants, donc la seule répétition (bourrage de mots-clés) ne peut pas dominer |
| Normalisation de la longueur | Neutralise l'avantage brut de fréquence des termes qu'un document tire du simple fait d'être plus long |

## BM25 et la recherche vectorielle ont des angles morts opposés

| Forme de requête | BM25 | Recherche vectorielle |
|---|---|---|
| Identifiant exact (« code d'erreur E502 ») | Trouve : la chaîne littérale apparaît | Peut rater : le modèle d'embedding a été entraîné pour la similarité sémantique, pas pour la correspondance exacte d'identifiants |
| Formulation synonyme, sans mots en commun (« tuyau cassé » / « conduit qui fuit ») | Score proche de zéro : aucun recouvrement de termes | Trouve : les deux expressions veulent dire la même chose |

Chaque approche détecte ce que l'autre manque, ce qui est toute la base pour les combiner.

## Reciprocal rank fusion (RRF) : utiliser le rang, pas le score

Le score de BM25 est non borné et dépend du corpus ; la similarité cosinus est bornée à [-1, 1]. Les moyenner directement revient à inventer une normalisation fragile et propre au corpus. **RRF** contourne le problème d'échelle en n'utilisant que la position dans le classement de chaque document au sein de chaque classement :

```text
RRF(d) = sum over rankings r of 1 / (k + rank_r(d))
```

`k` amortit l'influence des tout premiers rangs (une valeur par défaut courante est `k = 60` ; un `k` plus petit fait compter davantage les différences de rang près du sommet, un `k` plus grand les atténue). La position dans le classement est une monnaie commune à toute méthode de classement, donc aucune normalisation n'est nécessaire entre BM25 et la recherche vectorielle.

**Exemple détaillé**, `k = 1`, BM25 classe A 1er / B 4e / C 2e, la recherche vectorielle classe A 4e / B 1er / C 2e :

```text
RRF(A) = 1/(1+1) + 1/(1+4) = 0.500 + 0.200 = 0.700
RRF(B) = 1/(1+4) + 1/(1+1) = 0.200 + 0.500 = 0.700
RRF(C) = 1/(1+2) + 1/(1+2) = 0.333 + 0.333 = 0.667
```

A et B sont à égalité en tête, chacun excellant avec une méthode et se comportant mal avec l'autre ; C, simplement médiocre avec les deux, perd face aux deux. RRF récompense un document auquel une seule méthode croit fortement, pas seulement un document sur lequel les deux méthodes s'accordent mollement.

## Régler le mélange

RRF s'étend avec un poids par classement, `sum of w_r / (k + rank_r(d))`, ce qui permet à la recherche vectorielle de compter plus ou moins que BM25. Le bon poids et le bon `k` ne se devinent pas : mesurez la qualité de la récupération (recall@k, MRR) sur un jeu de requêtes étiqueté ou synthétique représentatif du trafic réel du corpus, à plusieurs pondérations candidates, et livrez le mélange qui récupère réellement les bons documents le plus souvent pour ce corpus, et non une répartition 50/50 par défaut.

## Voir aussi

- [Leçon 6](../lessons/0006-bm25-and-lexical-search.md), [Leçon 7](../lessons/0007-reciprocal-rank-fusion.md)
- [Recherche vectorielle et indexation](vector-search-and-indexing.md) : la moitié vectorielle de la fusion
