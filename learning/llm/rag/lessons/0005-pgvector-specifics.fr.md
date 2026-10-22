---
title: "5. Spécificités de pgvector"
description: "Mettre en place une recherche vectorielle dans Postgres, et faire correspondre les concepts d'index de la leçon 4 aux opérateurs et paramètres réels de pgvector"
type: lesson
---

# Leçon 5. Spécificités de pgvector

**Lien avec la mission :** C'est le point d'orgue de l'étape 3 : les concepts IVF et HNSW de la leçon 4 deviennent ici un vrai schéma, un vrai opérateur de distance et de vrais paramètres de réglage, sur la base vectorielle sur laquelle cet espace de travail s'aligne.
**Source primaire :** [Dépôt : pgvector, pgvector](https://github.com/pgvector/pgvector)
**Prérequis :** [Leçon 4](0004-ann-indexes.md), [Chunk](../GLOSSARY.md)

## Échauffement

1. ▢ Que contrôlent respectivement le paramètre `nprobe` d'IVF et le paramètre `ef_search` de HNSW ?

<details markdown="1"><summary>Vérifier</summary>

`nprobe` fixe combien de clusters d'IVF sont parcourus au moment de la requête ; `ef_search` fixe combien de candidats la recherche dans le graphe de HNSW suit à chaque étape. Tous deux arbitrent le recall contre la latence : des valeurs plus élevées cherchent davantage, ce qui améliore le recall au prix de la latence.

</details>

2. ▢ Pourquoi la similarité cosinus et le produit scalaire ne produisent-ils le même classement que lorsque les vecteurs d'embedding sont normalisés à une longueur unité ?

<details markdown="1"><summary>Vérifier</summary>

Le produit scalaire est la similarité cosinus multipliée par les normes des deux vecteurs. Quand les deux sont fixées à la longueur unité, ce facteur d'échelle est identique pour chaque paire, donc les classements coïncident ; quand les normes varient, le produit scalaire favorise les vecteurs plus grands.

</details>

## À savoir

### Une colonne vectorielle et un opérateur de distance

pgvector ajoute à Postgres un type de colonne `vector(N)`, dimensionné selon la dimensionnalité d'embedding retenue à la leçon 3 :

```sql
CREATE EXTENSION vector;
CREATE TABLE chunks (id bigserial PRIMARY KEY, content text, embedding vector(1536));
```

La similarité se calcule avec l'un de trois opérateurs : `<->` (distance euclidienne/L2), `<#>` (produit scalaire négatif) et `<=>` (distance cosinus). L'opérateur doit correspondre à la métrique pour laquelle le modèle d'embedding a été entraîné (leçon 2) : utiliser `<=>` avec un modèle entraîné pour le produit scalaire brut, ou l'inverse, est exactement le décalage dont la leçon 2 avertissait qu'il dégrade la qualité du classement, exprimé désormais comme un choix SQL concret plutôt qu'abstrait. Notez le signe de `<#>` : c'est un produit scalaire négatif précisément pour que, comme les deux autres opérateurs, plus petit signifie plus similaire, ce qui garde un `ORDER BY` croissant cohérent pour les trois.

### Un index doit être construit pour une fonction de distance précise

Créer un index implique de choisir une classe d'opérateurs qui correspond à la fonction de distance visée :

```sql
CREATE INDEX ON chunks USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);
```

`vector_cosine_ops`, `vector_l2_ops` et `vector_ip_ops` construisent chacune l'index pour un opérateur précis. Un index construit avec `vector_l2_ops` n'accélère pas une requête qui trie par `<=>` (distance cosinus) ; la classe d'opérateurs et l'opérateur de la requête doivent correspondre, faute de quoi l'index n'est pas utilisé et la requête retombe silencieusement sur un balayage séquentiel complet, ce qui annule tout l'intérêt de construire l'index.

### Les noms de paramètres de pgvector sont ceux de la leçon 4, sous d'autres noms

Les paramètres de construction de l'index HNSW, `m` (nombre maximal de connexions par nœud) et `ef_construction` (profondeur de recherche à la construction), sont exactement les réglages HNSW de la leçon 4, fixés à la création de l'index (`CREATE INDEX`). Son réglage de recall/latence au moment de la requête est un paramètre de session : `SET hnsw.ef_search = 100;`, l'`ef_search` de la leçon 4 sous un autre nom. Le paramètre de construction d'IVFFlat est `lists` (le nombre de clusters mentionné à la leçon 4), fixé de la même façon à la création de l'index, et son réglage au moment de la requête est `SET ivfflat.probes = 10;`, le `nprobe` de la leçon 4.

### IVFFlat a besoin de données avant d'être bien construit ; pas HNSW

L'étape de clustering d'IVFFlat a besoin d'un échantillon représentatif des vecteurs réels de la table pour bien placer ses centroïdes de clusters, ce qui signifie que construire un index IVFFlat sur une table vide ou à peine remplie produit de mauvais clusters qui ne reflètent pas la vraie distribution des vecteurs du corpus. Conséquence pratique : charger les données d'abord, puis construire l'index IVFFlat. Le graphe de HNSW se construit de façon incrémentale à mesure que les vecteurs sont insérés, sans dépendance équivalente à une table déjà remplie, ce qui explique en partie pourquoi HNSW est souvent préféré pour une table appelée à grossir avec le temps, en plus de l'avantage de recall/latence déjà décrit à la leçon 4.

## Pratique

1. ▢ Un modèle d'embedding a été entraîné pour que la similarité cosinus reflète la proximité sémantique. Quels opérateur et classe d'opérateurs pgvector la requête et son index doivent-ils utiliser tous les deux ?

<details markdown="1"><summary>Vérifier</summary>

L'opérateur `<=>` (distance cosinus) pour la requête, et `vector_cosine_ops` pour l'index. Utiliser un opérateur ou une classe d'opérateurs conçus pour une autre fonction de distance que celle pour laquelle le modèle a été entraîné réintroduit le problème de décalage de métrique de la leçon 2, désormais sous la forme d'un décalage SQL concret.

</details>

2. ▢ Une équipe construit un index HNSW avec `vector_l2_ops`, mais ses requêtes trient les résultats avec l'opérateur `<=>` (distance cosinus). Que se passe-t-il, et pourquoi est-ce un problème qui dépasse le simple « mauvais résultat » ?

<details markdown="1"><summary>Indice</summary>

Demandez-vous si l'index peut même être utilisé pour une requête dont l'opérateur ne correspond pas à la classe d'opérateurs avec laquelle il a été construit.

</details>

<details markdown="1"><summary>Vérifier</summary>

L'index construit pour `vector_l2_ops` n'accélère pas une requête qui utilise `<=>`, puisque l'index est construit pour une fonction de distance précise. La requête retombe sur un balayage séquentiel complet de la table, lent dès que le corpus a une taille réelle ; ce n'est pas seulement un risque de mauvais résultat, c'est la perte de tout le gain de performance que l'index devait apporter.

</details>

3. ▢ Une table a un index IVFFlat avec `lists = 1000`, mais le paramètre de requête `ivfflat.probes` est laissé à sa valeur par défaut de 1. Qu'est-ce que cela signifie pour le compromis recall/latence, en termes de `nprobe` de la leçon 4 ?

<details markdown="1"><summary>Vérifier</summary>

`ivfflat.probes = 1` équivaut à `nprobe = 1` : seul le cluster le plus proche parmi les 1 000 est parcouru. C'est l'extrémité la plus rapide et au recall le plus faible du compromis de la leçon 4 ; une requête proche d'une frontière de cluster peut rater de vrais plus proches voisins situés dans un cluster adjacent. Augmenter `probes` parcourt davantage de clusters, en échangeant de la latence de requête contre un meilleur recall.

</details>

4. ▢ Pourquoi l'ordre de construction compte-t-il pour un index IVFFlat (charger les données, puis construire) mais pas pour HNSW ?

<details markdown="1"><summary>Vérifier</summary>

L'étape de clustering d'IVFFlat a besoin d'un échantillon représentatif des vecteurs réels de la table pour bien placer ses centroïdes de clusters ; le construire sur une table vide ou peu remplie produit de mauvais clusters qui ne reflètent pas la vraie distribution des données. Le graphe de HNSW se construit de façon incrémentale à mesure que les vecteurs sont insérés, sans besoin équivalent que la table contienne déjà un échantillon représentatif.

</details>

5. ▢ Laquelle de ces affirmations est vraie à propos des classes d'opérateurs de pgvector (`vector_cosine_ops`, `vector_l2_ops`, `vector_ip_ops`) ?

    - a) N'importe quelle classe d'opérateurs fonctionne avec n'importe quel opérateur de requête, puisque pgvector convertit automatiquement entre fonctions de distance
    - b) La classe d'opérateurs d'un index doit correspondre à l'opérateur de distance de la requête, faute de quoi l'index ne sera pas utilisé pour cette requête
    - c) La classe d'opérateurs n'affecte que les index HNSW, pas IVFFlat
    - d) `vector_ip_ops` ne peut pas être utilisée avec des vecteurs d'embedding normalisés

<details markdown="1"><summary>Vérifier</summary>

**b)** La classe d'opérateurs et l'opérateur de la requête doivent correspondre, faute de quoi la requête retombe sur un balayage séquentiel au lieu d'utiliser l'index. (a) est fausse : il n'y a pas de conversion automatique entre fonctions de distance. (c) est fausse : les deux types d'index exigent de faire correspondre une classe d'opérateurs à la fonction de distance. (d) est fausse : les vecteurs normalisés sont exactement le cas où le produit scalaire et la distance cosinus coïncident, comme l'a vu la leçon 2.

</details>

## Exercices en situation réelle

- [ ] Créez une petite table pgvector avec une colonne `vector(N)` dimensionnée selon un modèle d'embedding que vous utilisez, et construisez un index avec la classe d'opérateurs qui correspond à la métrique de similarité d'entraînement de ce modèle.
- [ ] Exécutez `EXPLAIN` sur une requête de similarité contre votre table et confirmez que l'index est réellement utilisé, et non remplacé par un balayage séquentiel.
- [ ] Demain : essayez deux valeurs différentes de `ivfflat.probes` ou de `hnsw.ef_search` sur la même requête et comparez à la fois les résultats renvoyés et la latence de la requête.

## Pour aller plus loin

- [Dépôt : pgvector, pgvector](https://github.com/pgvector/pgvector)
- [Article : "Efficient and Robust Approximate Nearest Neighbor Search Using Hierarchical Navigable Small World Graphs", Malkov and Yashunin, 2018](https://arxiv.org/abs/1603.09320)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
