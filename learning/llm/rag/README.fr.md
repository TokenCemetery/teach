---
title: "RAG"
description: "Maîtriser la récupération : chunking, embeddings, recherche hybride, reranking, et mesurer si la bonne information a été récupérée"
type: topic
---

# Apprentissage : le RAG

Savoir concevoir un pipeline de récupération pour un vrai corpus et un vrai cas d'usage, et diagnostiquer pourquoi un système RAG existant renvoie le mauvais contexte au lieu de deviner une correction.

**Dernière leçon :** [20. Relire un pipeline de récupération](lessons/0020-reviewing-a-retrieval-pipeline.md)

## Objectif

- Concevoir un pipeline de récupération (chunking, embeddings, recherche hybride, reranking) pour un corpus et un cas d'usage donnés, et justifier chaque choix par rapport à eux.
- Face à un système RAG qui renvoie un contexte faux ou non pertinent, diagnostiquer quelle étape du pipeline est en cause au lieu de régler les paramètres au hasard.
- Ajuster les poids de la recherche hybride d'après une métrique de récupération mesurée plutôt qu'au feeling.
- Mener le contexte récupéré jusqu'à une réponse générée et rendre compte de ce que l'étape de génération elle-même peut encore rater.
- Relire la conception du pipeline de récupération de quelqu'un d'autre et nommer précisément ce qui ira de travers avant sa mise en production, et dire quand le RAG lui-même (et non une étape du pipeline) est la mauvaise réponse au problème posé.

## Contraintes

- Suppose des bases de Python et une familiarité avec ce qu'est un embedding ; aucune expérience préalable des systèmes de récupération n'est requise.
- Base vectorielle : pgvector, afin que les concepts se rattachent à ce que `data/postgres` couvre sur le coût d'un index vectoriel pour la base de données.

## Hors périmètre

- La technique de prompt engineering et la qualité de la génération en général : voir [`llm/prompting`](../../llm/prompting/). Abordées ici uniquement pour la façon dont le contexte récupéré parvient à l'étape de génération, sans être reprises comme un sujet à part.
- La façon dont la métrique de récupération elle-même est construite et défendue : voir [`llm/evals`](../../llm/evals/), auquel on renvoie sans le répéter.
- Ce qu'un index vectoriel coûte à la base de données en exploitation : voir [`data/postgres`](../../data/postgres/), auquel on renvoie sans le répéter.

## Le fil conducteur

Quatorze étapes, du premier chunk à un pipeline de production diagnostiqué, maîtrisé en coût et surveillé, avec le jugement pour conclure. Une étape comprend plusieurs leçons et les frontières sont souples ; ce qui termine une étape, c'est la capacité acquise, pas le nombre de leçons.

| Étape | Leçons | Contenu | Terminée quand |
|---|---|---|---|
| 1. Chunking | 0001 | Le premier choix du pipeline, dont hérite chaque étape suivante | Vous savez découper en chunks un corpus donné et justifier ce choix |
| 2. Embeddings | 0002 à 0003 | Modèles d'embedding, métriques de similarité, compromis de dimensionnalité | Vous savez choisir un modèle d'embedding et une métrique pour un corpus donné |
| 3. Recherche vectorielle et indexation | 0004 à 0005 | Index ANN (HNSW/IVF), spécificités de pgvector, compromis entre recall et latence | Vous savez mettre en place une recherche vectorielle sur pgvector pour le corpus découpé en chunks |
| 4. Recherche hybride | 0006 à 0007 | BM25 plus recherche vectorielle, reciprocal rank fusion, réglage du mélange | Vous savez ajuster les poids de la recherche hybride d'après une métrique de récupération mesurée |
| 5. Reranking | 0008 à 0009 | Rerankers cross-encoder, quand le reranking justifie son coût en latence | Vous savez ajouter une étape de reranking et la justifier par rapport à son coût |
| 6. Évaluation et diagnostic de la récupération | 0010 à 0011 | Recall@k, MRR, diagnostiquer quelle étape du pipeline est en cause | Face à un contexte récupéré faux, vous savez nommer l'étape en cause |
| 7. De la récupération à la génération | 0012 à 0013 | Construction du prompt sur le contexte récupéré, budget de la fenêtre de contexte, ce que la génération rate encore | Vous savez mener le contexte récupéré jusqu'à une réponse générée et nommer les modes de défaillance de l'étape de génération |
| 8. Transformation côté requête | 0014 | HyDE, réécriture de requête, expansion multi-requête, décomposition de requête | Face à un échec côté requête que la procédure de la leçon 11 ne détecte pas, vous savez choisir et justifier le bon remède |
| 9. Filtrage par métadonnées et récupération respectueuse des permissions | 0015 | Filtrage par métadonnées, pré-filtrage contre post-filtrage, pourquoi le contrôle d'accès exige précisément un pré-filtrage | Vous savez concevoir un chemin de récupération respectueux des permissions et expliquer pourquoi le post-filtrage n'y est pas sûr |
| 10. Le pipeline d'ingestion | 0016 | Analyse de PDF/HTML/documents bureautiques, extraction tenant compte de la mise en page contre extraction naïve, structure des tableaux, cascade d'erreurs | Vous savez expliquer pourquoi l'ingestion se situe en amont du chunking, et comment une mauvaise analyse échappe au diagnostic de la leçon 11 |
| 11. Fraîcheur | 0017 | Indexation incrémentale (HNSW contre IVFFlat), maintenance des suppressions et des mises à jour, réindexation lors d'un changement de modèle | Vous savez planifier les trois façons réellement différentes dont un corpus et son index deviennent périmés |
| 12. Récupération multi-hop et agentique | 0018 | Raisonnement et récupération entrelacés d'IRCoT, décision de récupération adaptative de Self-RAG | Vous savez concevoir une boucle de récupération pour une question que la décomposition seule ne peut pas résoudre |
| 13. Coût, latence et surveillance en production | 0019 | Budget de latence du pipeline entier, utilisation de la fenêtre de contexte, score sans référence, dérive des embeddings | Vous savez budgéter la latence du pipeline complet et surveiller la qualité de la récupération en production, sans vérité terrain |
| 14. Jugement | 0020 | Relire un pipeline, trancher quand le RAG est la bonne réponse face au long contexte, nommer ce qui va mal | On vous fait confiance pour relire la conception de récupération de quelqu'un d'autre et expliquer exactement pourquoi un choix échouera |

## Leçons

Suivez-les dans l'ordre.

| # | Leçon | Enseigne |
|---|---|---|
| [0001](lessons/0001-chunking.md) | Chunking | Le premier choix du pipeline, dont hérite chaque étape suivante |
| [0002](lessons/0002-embedding-models-and-similarity.md) | Modèles d'embedding et similarité | Ce que fait un modèle d'embedding bi-encoder, et pourquoi la métrique de similarité doit correspondre à la façon dont il a été entraîné |
| [0003](lessons/0003-embedding-dimensionality.md) | Compromis de dimensionnalité des embeddings | Pourquoi un vecteur d'embedding plus grand n'est pas gratuit, et quand on peut sans risque le tronquer au lieu de choisir un modèle plus petit |
| [0004](lessons/0004-ann-indexes.md) | Index ANN : HNSW et IVF | Pourquoi la recherche vectorielle sacrifie l'exactitude à la vitesse, et comment IVF et HNSW exposent chacun ce compromis sous forme d'un réglage ajustable |
| [0005](lessons/0005-pgvector-specifics.md) | Spécificités de pgvector | Mettre en place une recherche vectorielle dans Postgres, et faire correspondre les concepts d'index de la leçon 4 aux opérateurs et paramètres réels de pgvector |
| [0006](lessons/0006-bm25-and-lexical-search.md) | BM25 et recherche lexicale | Ce que BM25 note réellement, et pourquoi la correspondance exacte des termes détecte encore ce que les embeddings sémantiques manquent |
| [0007](lessons/0007-reciprocal-rank-fusion.md) | Reciprocal Rank Fusion | Comment combiner un classement lexical et un classement vectoriel sans comparer des scores incomparables, et comment régler le mélange d'après une métrique mesurée |
| [0008](lessons/0008-cross-encoder-rerankers.md) | Rerankers cross-encoder | Ce qu'un cross-encoder note et qu'un bi-encoder ne peut pas noter, et pourquoi le reranking est une seconde étape et non un remplacement de la récupération |
| [0009](lessons/0009-when-reranking-earns-its-cost.md) | Quand le reranking justifie son coût | Un cadre de décision pour savoir si une étape de reranking vaut sa latence supplémentaire pour une charge de travail donnée |
| [0010](lessons/0010-recall-at-k-and-mrr.md) | Recall@k et MRR | Les deux métriques de récupération standard, ce que chacune vous apprend que l'autre ne dit pas, et comment choisir k pour la charge de travail |
| [0011](lessons/0011-diagnosing-the-pipeline.md) | Diagnostiquer le pipeline | Une procédure étape par étape pour trouver quelle partie d'un pipeline de récupération est réellement responsable d'un contexte récupéré faux |
| [0012](lessons/0012-prompt-construction-and-context-budget.md) | Construction du prompt et budget de la fenêtre de contexte | Pourquoi les chunks récupérés se disputent un budget de fenêtre de contexte partagé, et pourquoi l'emplacement d'un chunk dans le prompt compte autant que le fait qu'il ait été récupéré |
| [0013](lessons/0013-what-generation-still-gets-wrong.md) | Ce que la génération peut encore rater | Les modes de défaillance qui subsistent même avec un contexte récupéré correct et bien placé, et en quoi ils diffèrent d'un échec de récupération |
| [0014](lessons/0014-query-side-transformation.md) | Transformation côté requête | La procédure de diagnostic de la leçon 11 vérifie le chunking, l'embedding, l'index, la pondération hybride et le reranking, mais jamais la requête elle-même, et une requête trop courte, trop composée ou formulée sans rapport avec le corpus demande son propre remède, pas une énième correction d'étape du pipeline |
| [0015](lessons/0015-metadata-filtering-and-access-control.md) | Filtrage par métadonnées et récupération respectueuse des permissions | Un filtre de contrôle d'accès qui échoue ne plante pas et n'a pas l'air faux : il produit une réponse parfaitement bien formée, construite à partir d'un document que l'utilisateur n'aurait jamais dû voir, et c'est exactement pourquoi le post-filtrage est le mauvais choix pour ce seul type de filtre |
| [0016](lessons/0016-the-ingestion-pipeline.md) | Le pipeline d'ingestion | Le chunking n'a jamais été vraiment la première étape du pipeline, il supposait simplement qu'un texte d'entrée propre existait déjà, et une mauvaise analyse en amont du chunking corrompt tout ce qui suit tout en ressemblant, pour chaque diagnostic ultérieur, à une défaillance complètement différente |
| [0017](lessons/0017-freshness.md) | Fraîcheur | Un corpus qui ne cesse de changer demande trois réponses réellement différentes, pas une seule, car ajouter un document, en supprimer un et changer de modèle d'embedding remettent chacun en cause une hypothèse différente sur laquelle l'index a été construit |
| [0018](lessons/0018-multi-hop-and-agentic-retrieval.md) | Récupération multi-hop et agentique | La décomposition découpe une question composée en sous-questions que l'on voit déjà dans le texte d'origine, mais certaines questions ne révèlent leur seconde moitié qu'une fois la réponse à la première revenue, ce qui demande une vraie boucle, pas un découpage initial plus malin |
| [0019](lessons/0019-cost-latency-and-production-monitoring.md) | Coût, latence et surveillance en production | Un pipeline peut paraître parfaitement sain sur tous les signaux d'infrastructure ordinaires tout en servant discrètement une réponse assurée, bâtie sur un document qui n'a en réalité jamais atteint le modèle, et c'est précisément cet écart que la surveillance propre à la récupération sert à combler |
| [0020](lessons/0020-reviewing-a-retrieval-pipeline.md) | Relire un pipeline de récupération | Relire la conception du pipeline de récupération de quelqu'un d'autre et nommer précisément ce qui ira de travers avant sa mise en production, et dire quand le RAG lui-même (et non une étape du pipeline) est la mauvaise réponse au problème posé |

## Référence

- [Glossaire](GLOSSARY.md) : termes de référence pour ce sujet
- [Ressources](RESOURCES.md) : sources fiables
- [Chunking et embeddings](reference/chunking-and-embeddings.md) : stratégies de chunking, modèles d'embedding, métriques de similarité, compromis de dimensionnalité
- [Recherche vectorielle et indexation](reference/vector-search-and-indexing.md) : index ANN (HNSW/IVF), spécificités de pgvector, compromis entre recall et latence
- [Recherche hybride](reference/hybrid-search.md) : BM25 plus recherche vectorielle, reciprocal rank fusion, réglage du mélange
- [Reranking](reference/reranking.md) : rerankers cross-encoder, et quand le reranking justifie son coût en latence
- [Évaluation de la récupération](reference/retrieval-evaluation.md) : Recall@k, MRR, et diagnostic de l'étape du pipeline en cause
- [Génération à partir de la récupération](reference/generation-from-retrieval.md) : construction du prompt sur le contexte récupéré, budget de la fenêtre de contexte, modes de défaillance de l'étape de génération

## Comment cela fonctionne

Chaque leçon est courte et autonome. Les corrigés sont repliés : rappelez-vous d'abord, puis ouvrez-les. Les exercices en situation réelle comptent plus que la lecture, et les espacer dans le temps est justement le but. Tout ce qui reste flou à la fin d'une leçon mérite d'être suivi jusqu'à sa source primaire avant de passer à la suite.
