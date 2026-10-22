---
title: "Recherche vectorielle et indexation"
description: "Le compromis recall/latence d'IVF et de HNSW, et les opérateurs, paramètres d'index et spécificités d'ordre de construction de pgvector"
type: reference
---

# Recherche vectorielle et indexation

La recherche de plus proches voisins approximatifs et son implémentation dans pgvector. Conçu pour la consultation lors de la mise en place ou du réglage d'un index.

## Pourquoi la recherche exacte ne passe pas à l'échelle

La recherche exacte de plus proches voisins compare une requête à chaque vecteur : linéaire en la taille du corpus, trop lente à des millions de chunks. Un index de **plus proches voisins approximatifs (ANN)** accepte une petite part d'inexactitude contrôlable en échange de temps de recherche qui ne croissent pas linéairement.

## IVF et HNSW

| Index | Mécanisme | Réglage au moment de la recherche | Coût de construction |
|---|---|---|---|
| IVF (inverted file) | Partitionne les vecteurs en clusters (k-means) à l'avance ; ne cherche que dans les `nprobe` clusters les plus proches | `nprobe` : faible = rapide, peut rater des voisins près d'une frontière de cluster ; élevé = approche la recherche exacte | A besoin d'un échantillon représentatif du corpus pour bien placer les centroïdes |
| HNSW (hierarchical navigable small world) | Graphe multicouche ; couches clairsemées au sommet pour les grands sauts, couche dense en bas pour la recherche locale précise, descendu goulûment | `ef_search` : combien de candidats sont suivis à chaque étape ; faible = rapide mais peut se contenter d'un nœud localement bon ; élevé = plus de recall | Plus de mémoire (arêtes du graphe) et une construction d'index plus lente qu'IVF |

Les deux réglages placent un point sur une **courbe recall/latence** pour un corpus donné ; aucun n'a de réglage universellement correct. HNSW atteint généralement un meilleur point de cette courbe qu'IVF (un recall plus élevé à la même latence), au prix de la mémoire et du temps de construction. Le bon point dépend du budget de latence de la charge de travail et de la perte de recall qu'une étape ultérieure (le reranking) peut absorber, mesurée plutôt que supposée.

## pgvector : colonne, opérateur, index

```sql
CREATE EXTENSION vector;
CREATE TABLE chunks (id bigserial PRIMARY KEY, content text, embedding vector(1536));
```

| Opérateur | Distance | Classe d'opérateurs (pour l'indexation) |
|---|---|---|
| `<->` | Euclidienne/L2 | `vector_l2_ops` |
| `<#>` | Produit scalaire négatif | `vector_ip_ops` |
| `<=>` | Cosinus | `vector_cosine_ops` |

`<#>` est un produit scalaire *négatif* précisément pour que, comme les deux autres, plus petit signifie plus similaire, ce qui garde un `ORDER BY` croissant cohérent pour les trois. L'opérateur doit correspondre à [la métrique pour laquelle le modèle d'embedding a été entraîné](chunking-and-embeddings.md#similarity-metrics-must-match-training) : utiliser `<=>` avec un modèle entraîné pour le produit scalaire (ou l'inverse) est ce même décalage de métrique, devenu un choix SQL concret.

```sql
CREATE INDEX ON chunks USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);
```

**Un index est construit pour une fonction de distance précise.** Une requête qui trie par un opérateur ne correspondant pas à la classe d'opérateurs de l'index n'utilise pas du tout cet index : elle retombe silencieusement sur un balayage séquentiel complet, ce qui perd tout le gain de performance que l'index devait apporter. Il n'y a pas de conversion automatique entre fonctions de distance.

## Les paramètres de pgvector sont ceux de la leçon 4, renommés

| Concept | HNSW | IVFFlat |
|---|---|---|
| Paramètre(s) de construction | `m` (nombre maximal de connexions par nœud), `ef_construction` (profondeur de recherche à la construction), fixés à `CREATE INDEX` | `lists` (nombre de clusters), fixé à `CREATE INDEX` |
| Réglage de recall/latence au moment de la requête | `SET hnsw.ef_search = 100;` | `SET ivfflat.probes = 10;` (c'est `nprobe`) |

## L'ordre de construction compte pour IVFFlat, pas pour HNSW

L'étape de clustering d'IVFFlat a besoin d'un échantillon représentatif des vecteurs réels de la table pour bien placer les centroïdes : le construire sur une table vide ou clairsemée produit de mauvais clusters. Chargez d'abord les données, puis construisez l'index IVFFlat. Le graphe de HNSW se construit de façon incrémentale à mesure que les vecteurs sont insérés, sans dépendance équivalente, ce qui explique en partie pourquoi HNSW est souvent préféré pour une table appelée à grossir avec le temps.

## Voir aussi

- [Leçon 4](../lessons/0004-ann-indexes.md), [Leçon 5](../lessons/0005-pgvector-specifics.md)
- [Chunking et embeddings](chunking-and-embeddings.md) : les vecteurs et la métrique de similarité auxquels l'index de cette fiche doit correspondre
