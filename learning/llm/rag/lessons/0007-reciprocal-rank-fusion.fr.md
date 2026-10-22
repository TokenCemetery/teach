---
title: "7. Reciprocal Rank Fusion"
description: "Comment combiner un classement lexical et un classement vectoriel sans comparer des scores incomparables, et comment régler le mélange d'après une métrique mesurée"
type: lesson
---

# Leçon 7. Reciprocal Rank Fusion

**Lien avec la mission :** C'est le point d'orgue de l'étape 4 : BM25 et la recherche vectorielle (leçons 4 à 6) produisent chacun un classement, et cette leçon explique comment ces deux classements deviennent un seul résultat hybride, réglé d'après un chiffre mesuré plutôt qu'un mélange deviné.
**Source primaire :** [Doc : "Reciprocal rank fusion (RRF)", Elasticsearch](https://www.elastic.co/guide/en/elasticsearch/reference/current/rrf.html)
**Prérequis :** [Leçon 6](0006-bm25-and-lexical-search.md), [Chunk](../GLOSSARY.md)

## Échauffement

1. ▢ Donnez un exemple de requête où BM25 réussirait et où la recherche vectorielle pourrait échouer, et un exemple où c'est l'inverse.

<details markdown="1"><summary>Vérifier</summary>

Un identifiant exact comme « code d'erreur E502 » favorise BM25, puisque le modèle d'embedding de la recherche vectorielle n'a pas été entraîné à faire correspondre précisément des codes précis. Une formulation synonyme sans mots en commun, comme « tuyau cassé » face à « conduit qui fuit », favorise la recherche vectorielle, puisque BM25 donne zéro aux documents qui n'ont aucun terme en commun avec la requête.

</details>

2. ▢ Pourquoi utiliser le mauvais opérateur de distance sur un index pgvector fait-il retomber la requête sur un balayage séquentiel ?

<details markdown="1"><summary>Vérifier</summary>

Un index est construit pour une fonction de distance précise (une classe d'opérateurs) ; une requête qui utilise un autre opérateur ne correspond pas à ce pour quoi l'index a été construit, donc l'index ne peut pas être utilisé et la requête balaie directement la table.

</details>

## À savoir

### Le problème : deux classements sur des échelles incomparables

BM25 produit un score non borné qui dépend du corpus ; la similarité cosinus produit un score borné entre -1 et 1. Les moyenner directement, même après une certaine normalisation, oblige à décider comment rendre comparables deux échelles fondamentalement différentes, et cette décision est fragile : elle dépend du corpus, de la requête et du schéma de normalisation choisi, sans moyen rigoureux de savoir qu'elle est équitable.

### RRF : utiliser la position dans le classement, pas le score lui-même

**Reciprocal rank fusion (RRF)** contourne entièrement le problème d'échelle en ignorant les scores sous-jacents et en n'utilisant que la **position dans le classement** de chaque document au sein de chaque classement. Pour un document *d* qui apparaît au rang `rank_r(d)` dans le classement *r*, son score RRF additionne un terme de rang réciproque sur chaque classement où il apparaît :

```text
RRF(d) = sum over rankings r of 1 / (k + rank_r(d))
```

`k` est une constante qui amortit l'influence des tout premiers rangs ; une valeur par défaut courante, issue de l'article d'origine, est `k = 60`. Comme seule compte la position dans le classement, pas l'amplitude du score, RRF combine un classement BM25 et un classement de recherche vectorielle sans avoir besoin de normaliser l'un ou l'autre : la position dans le classement est déjà une monnaie commune, qui s'auto-normalise quelle que soit la méthode de classement.

### Un exemple détaillé

Avec un `k = 1` simplifié pour garder un calcul net (les systèmes de production retiennent plus couramment `k = 60`, qui amortit les différences entre les premiers rangs plus fortement que `k = 1`) : pour une requête, BM25 classe le document A 1er, le document B 4e, le document C 2e ; la recherche vectorielle classe A 4e, B 1er, C 2e.

```text
RRF(A) = 1/(1+1) + 1/(1+4) = 0.500 + 0.200 = 0.700
RRF(B) = 1/(1+4) + 1/(1+1) = 0.200 + 0.500 = 0.700
RRF(C) = 1/(1+2) + 1/(1+2) = 0.333 + 0.333 = 0.667
```

A et B sont à égalité en tête, chacun excellant avec une méthode et se comportant mal avec l'autre ; C, simplement médiocre avec les deux, perd face aux deux. RRF récompense un document auquel une seule méthode croit fortement, pas seulement un document sur lequel les deux méthodes s'accordent mollement.

![Deux listes classées côte à côte, le rang BM25 et le rang de la recherche vectorielle, chacune énumérant quatre positions. Le document A est 1er avec BM25 mais 4e avec la recherche vectorielle ; le document B est 4e avec BM25 mais 1er avec la recherche vectorielle ; le document C est 2e dans les deux. Des lignes relient chaque document, depuis ses deux positions, à un classement RRF fusionné à droite, où A et B sont à égalité à la première place, chacun ayant excellé avec une méthode, tandis que C, seulement modéré, arrive derrière eux alors qu'il n'est jamais mal classé dans aucune des deux listes.](images/rrf-worked-example.svg)

### Régler le mélange d'après une métrique mesurée

RRF peut être étendu avec un poids par classement, `sum of w_r / (k + rank_r(d))`, ce qui permet à la recherche vectorielle de compter plus ou moins que BM25 dans la fusion finale. Le bon poids, et le bon `k`, ne se devinent pas : ils se mesurent, comme la leçon 3 a mesuré la qualité des embeddings à des dimensionnalités candidates au lieu d'en supposer une. Avec les métriques de récupération de l'étape 6 (recall@k, MRR) sur un jeu de requêtes étiqueté ou synthétique représentatif du trafic réel du corpus, différentes pondérations peuvent être comparées directement, et le mélange qui récupère réellement les bons documents plus souvent pour ce corpus, et non une répartition 50/50 par défaut, est celui qui mérite d'être livré.

## Pratique

1. ▢ Pour une requête, BM25 classe le document X 2e et le document Y 1er ; la recherche vectorielle classe X 1er et Y 3e. Avec `k = 1`, calculez le score RRF de chaque document et dites lequel est mieux classé.

<details markdown="1"><summary>Indice</summary>

`RRF(d) = 1/(k + rank_in_bm25) + 1/(k + rank_in_vector)`.

</details>

<details markdown="1"><summary>Vérifier</summary>

`RRF(X) = 1/(1+2) + 1/(1+1) = 0.333 + 0.500 = 0.833`. `RRF(Y) = 1/(1+1) + 1/(1+3) = 0.500 + 0.250 = 0.750`. X est mieux classé, puisque c'est un résultat fort (1re place) avec la recherche vectorielle et seulement moyennement bon avec BM25, ce qui lui permet de devancer Y, fort avec BM25 mais plus faible avec la recherche vectorielle.

</details>

2. ▢ Pourquoi RRF utilise-t-il la position dans le classement de chaque document plutôt que directement son score BM25 brut ou son score de similarité cosinus ?

<details markdown="1"><summary>Vérifier</summary>

Les scores BM25 et de similarité cosinus vivent sur des échelles incomparables (l'une non bornée et dépendante du corpus, l'autre bornée entre -1 et 1), et il n'existe aucun moyen rigoureux, indépendant du corpus, de les normaliser l'une par rapport à l'autre. La position dans le classement est déjà une monnaie commune à toute méthode de classement, donc l'utiliser contourne entièrement le problème de normalisation.

</details>

3. ▢ Qu'est-ce qu'un petit `k` (comme 1) change à la formule RRF par rapport à un grand `k` (comme 60), quant à l'importance de la position exacte d'un document dans le classement ?

<details markdown="1"><summary>Vérifier</summary>

Un petit `k` rend le terme de rang réciproque beaucoup plus sensible aux petites différences de rang près du haut d'une liste (l'écart entre le rang 1 et le rang 2 est proportionnellement plus grand), alors qu'un grand `k` atténue cette sensibilité, ce qui rend la différence entre, disons, le rang 1 et le rang 5 comparativement plus petite. Des valeurs de `k` plus grandes produisent une fusion plus douce, moins sensible à la position dans le classement.

</details>

4. ▢ Comment une équipe doit-elle décider si elle pondère la recherche vectorielle plus fortement que BM25 dans son mélange hybride, plutôt que de retenir par défaut une répartition égale ?

<details markdown="1"><summary>Vérifier</summary>

Mesurer la qualité de la récupération (recall@k ou MRR, les métriques de l'étape 6) sur un jeu de requêtes étiqueté ou synthétique représentatif du type de requêtes réel du corpus, à plusieurs pondérations candidates, et choisir celle qui récupère réellement les bons documents le plus souvent pour ce corpus, plutôt que de supposer qu'une répartition égale ou toute autre valeur par défaut est correcte sans vérifier.

</details>

5. ▢ Laquelle de ces affirmations est vraie à propos de la reciprocal rank fusion ?

    - a) Elle exige de normaliser les scores BM25 et de similarité cosinus sur la même échelle avant de les combiner
    - b) Elle combine les classements en n'utilisant que la position dans le classement, ce qui évite de comparer des échelles de score incomparables
    - c) Un document classé 1er dans un classement et dernier dans un autre sera toujours mieux classé qu'un document classé moyennement dans les deux
    - d) La constante `k` n'a aucun effet sur le classement fusionné, seulement sur l'amplitude du score numérique

<details markdown="1"><summary>Vérifier</summary>

**b)** Utiliser la position dans le classement plutôt que les scores bruts est exactement ce qui évite le problème de normalisation. (a) est fausse : c'est l'approche de fusion par scores bruts que RRF évite précisément. (c) est fausse : l'exemple détaillé a montré qu'un document constamment moyen peut quand même perdre face à deux documents qui excellent chacun avec une méthode, mais le résultat dépend des valeurs de rang réelles, pas d'une règle universelle voulant que l'extrême batte le moyen. (d) est fausse : `k` change l'importance des différences de position dans le classement, ce qui peut changer l'ordre du classement fusionné, pas seulement son échelle.

</details>

## Exercices en situation réelle

- [ ] Pour une requête de votre corpus, relevez le rang BM25 et le rang de la recherche vectorielle d'une poignée de documents candidats, et calculez leurs scores RRF à la main avec `k = 60`.
- [ ] Si vous disposez d'un jeu de requêtes étiqueté ou synthétique, comparez le recall@k d'un classement BM25 seul, d'un classement vectoriel seul et d'un classement fusionné par RRF sur les mêmes requêtes.
- [ ] Demain : essayez deux valeurs différentes du poids de la recherche vectorielle dans une formule RRF pondérée, et voyez si l'une ou l'autre améliore mesurablement le recall@k par rapport à une répartition égale.

## Pour aller plus loin

- [Doc : "Reciprocal rank fusion (RRF)", Elasticsearch](https://www.elastic.co/guide/en/elasticsearch/reference/current/rrf.html)
- [Article : "The Probabilistic Relevance Framework: BM25 and Beyond", Robertson and Zaragoza, 2009](https://www.staff.city.ac.uk/~sbrp622/papers/foundations_bm25_review.pdf)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
