---
title: "Ressources"
description: "Sources fiables pour le RAG"
type: resources
---

# Ressources sur le RAG

## Connaissances

- [Billet : "Chunking Strategies for LLM Applications", Pinecone](https://www.pinecone.io/learn/chunking-strategies/)
  Panorama pratique des approches de chunking (taille fixe, récursif, sémantique, tenant compte de la structure du document) et des compromis que chacune fait entre contexte et précision. À utiliser pour : choisir et justifier une stratégie de chunking pour un corpus donné.
- [Dépôt : pgvector, pgvector](https://github.com/pgvector/pgvector)
  Dépôt officiel de la base vectorielle sur laquelle cet espace de travail s'aligne : types d'index (IVFFlat, HNSW), fonctions de distance, opérateurs qui font d'une table Postgres un index vectoriel, et ses propres consignes de maintenance (réindexer avant de lancer le vacuum après des suppressions, dépendance d'IVFFlat à ses données d'entraînement). À utiliser pour : exploiter et configurer pgvector lui-même, et voir comment chaque type d'index gère différemment les ajouts et les suppressions incrémentaux.
- [Article : "Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks", Reimers and Gurevych, 2019](https://arxiv.org/abs/1908.10084)
  L'article derrière l'approche d'embedding bi-encoder qu'utilise presque tout pipeline de récupération : pourquoi un espace d'embedding partagé permet de calculer la similarité par une distance au lieu d'exécuter le modèle sur chaque paire. À utiliser pour : comprendre ce qu'un modèle d'embedding optimise réellement.
- [Article : "Passage Re-ranking with BERT", Nogueira and Cho, 2019](https://arxiv.org/abs/1901.04085)
  Introduit le reranking par cross-encoder : noter une paire requête-passage conjointement plutôt que par distance entre embeddings, au prix d'une exécution du modèle par candidat. À utiliser pour : comprendre pourquoi une étape de reranking existe et ce qu'elle apporte par rapport à la seule similarité des embeddings.
- [Doc : "Reciprocal rank fusion (RRF)", Elasticsearch](https://www.elastic.co/guide/en/elasticsearch/reference/current/rrf.html)
  Explique la méthode standard pour combiner un classement de recherche par mots-clés et un classement de recherche vectorielle en un seul classement hybride, avec la formule et son unique paramètre de réglage. À utiliser pour : voir comment la recherche hybride combine réellement ses deux classements.
- [Doc : "Reranking", Cohere](https://docs.cohere.com/docs/reranking)
  Documentation orientée praticiens d'un reranker cross-encoder hébergé : comment l'appeler, ce qu'il coûte en latence et où il se place dans un pipeline de récupération. À utiliser pour : disposer d'une étape de reranking concrète et exécutable sur laquelle raisonner, en parallèle de l'article de Nogueira et Cho ci-dessus.
- [Billet : "Evaluation Measures for Search and Recommender Systems", Pinecone](https://www.pinecone.io/learn/offline-evaluation/)
  Passe en revue les métriques de récupération standard (Recall@k, MRR, nDCG) et la façon de calculer chacune sur un jeu de requêtes étiqueté ou synthétique. À utiliser pour : mesurer si la bonne information a été récupérée, avant de confier ce chiffre à `llm/evals` pour apprendre à le défendre.
- [Article : "Matryoshka Representation Learning", Kusupati et al., 2022](https://arxiv.org/abs/2205.13147)
  Introduit des embeddings entraînés de sorte qu'un préfixe tronqué du vecteur complet reste à lui seul un embedding significatif et utilisable, ce qui permet d'arbitrer la dimensionnalité contre le stockage et la latence après l'entraînement, et pas seulement en choisissant d'emblée un modèle plus petit. À utiliser pour : comprendre quand on peut tronquer un vecteur d'embedding sans risque, et quand on ne le peut pas.
- [Article : "Efficient and Robust Approximate Nearest Neighbor Search Using Hierarchical Navigable Small World Graphs", Malkov and Yashunin, 2018](https://arxiv.org/abs/1603.09320)
  L'article derrière HNSW, l'index de plus proches voisins approximatif à base de graphe qu'utilisent pgvector et la plupart des bases vectorielles : sa structure multicouche et le compromis entre recall et latence que contrôle son paramètre de profondeur de recherche. À utiliser pour : comprendre ce que fait réellement un index ANN à la place d'une recherche exacte, et pourquoi son réglage échange du recall contre de la vitesse.
- [Article : "The Probabilistic Relevance Framework: BM25 and Beyond", Robertson and Zaragoza, 2009](https://www.staff.city.ac.uk/~sbrp622/papers/foundations_bm25_review.pdf)
  La référence de fond sur BM25, la fonction de classement lexical derrière la fréquence des termes, la fréquence inverse de document et la normalisation de la longueur, avec le raisonnement derrière chacun de ses paramètres. À utiliser pour : comprendre ce que la recherche lexicale note réellement, en complément de la similarité sémantique de la recherche vectorielle.
- [Article : "Lost in the Middle: How Language Models Use Long Contexts", Liu et al., 2023](https://arxiv.org/abs/2307.03172)
  Montre que les modèles exploitent bien plus fiablement l'information placée au début ou à la fin d'un long contexte que celle enfouie au milieu, même quand tout se trouve techniquement dans la fenêtre de contexte. À utiliser pour : comprendre pourquoi l'emplacement des chunks dans un prompt assemblé compte autant que le fait qu'un chunk ait été récupéré, et pourquoi une récupération qui place les chunks pertinents en haut du contexte fait mieux que renvoyer un corpus entier où les parties pertinentes sombrent au milieu.
- [Article : "RAGAS: Automated Evaluation of Retrieval Augmented Generation", Es et al., 2023](https://arxiv.org/abs/2309.15217)
  Définit la fidélité (le fait qu'une affirmation générée soit réellement étayée par le contexte récupéré) comme une métrique distincte de la qualité de la récupération, et la façon de la vérifier sans avoir besoin d'une nouvelle vérité terrain étiquetée par des humains pour chaque réponse générée. À utiliser pour : évaluer si l'étape de génération est restée ancrée dans ce qui a été récupéré, une fois la récupération elle-même confirmée correcte.

- [Article : "Precise Zero-Shot Dense Retrieval without Relevance Labels" (HyDE), Gao et al., 2022](https://arxiv.org/abs/2212.10496)
  Introduit le calcul de l'embedding d'une réponse hypothétique générée au lieu de celui de la requête elle-même, ce qui laisse le goulot d'étranglement dense de l'encodeur filtrer les erreurs factuelles du document hypothétique tout en gardant son véritable signal de pertinence. À utiliser pour : le mécanisme précis qui explique pourquoi un document inventé, parfois faux, améliore quand même la récupération.
- [Article : "Policy-aware Vector Search: A Vision for Fine Grained Access Control in Vector Databases", Yalamarthi and Pappachan, 2026](https://arxiv.org/abs/2606.19803)
  Formalise le contrôle d'accès fin comme un problème d'application des règles dans les bases vectorielles, ainsi que la tension inhérente entre application correcte, recall ANN et latence des requêtes. À utiliser pour : comprendre pourquoi le contrôle d'accès exige précisément un pré-filtrage plutôt que le post-filtrage, plus rapide mais risqué pour le recall et la sécurité.
- [Article : "Docling Technical Report", Auer et al., 2024](https://arxiv.org/abs/2408.09869)
  Introduit un pipeline d'analyse de la mise en page (DocLayNet) et de reconnaissance de la structure des tableaux (TableFormer) pour la conversion de PDF, comme alternative à l'extraction de texte naïve qui aplatit la mise en page et la structure des tableaux. À utiliser pour : savoir ce qu'un pipeline d'ingestion tenant compte de la mise en page détecte et reconstruit réellement, alors qu'un simple extracteur de texte le jette.
- [Article : "Interleaving Retrieval with Chain-of-Thought Reasoning for Knowledge-Intensive Multi-Step Questions" (IRCoT), Trivedi et al., 2022](https://arxiv.org/abs/2212.10509)
  Énonce précisément pourquoi la récupération en un seul passage échoue sur les questions à plusieurs étapes (ce qu'il faut récupérer dépend de ce qui a déjà été déduit) et entrelace une étape de raisonnement avec une étape de récupération pour y remédier. À utiliser pour : le mécanisme derrière une boucle de récupération où une requête ultérieure dépend de la réponse d'un saut précédent.
- [Article : "Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection", Asai et al., 2023](https://arxiv.org/abs/2310.11511)
  Entraîne un modèle à décider si la récupération est nécessaire tout court et à critiquer les passages récupérés, au lieu de récupérer à chaque fois un nombre fixe de passages sans discernement. À utiliser pour : l'autre axe de la récupération agentique, décider s'il faut récupérer tout court, distinct du nombre de sauts qu'exige une question à plusieurs étapes.
- [Guide : "RAG Observability: How Coralogix Helps You Trace Retrieval-to-Generation Quality", Coralogix, 2026](https://coralogix.com/guides/rag-observability/)
  Explique pourquoi la surveillance d'infrastructure ordinaire (latence, débit, taux d'erreur) reste au vert malgré des défaillances silencieuses de la récupération et de la fenêtre de contexte, et quels signaux (sans référence, utilisation de la fenêtre de contexte, dérive des embeddings) les détectent à la place. À utiliser pour : savoir quoi surveiller concrètement une fois le pipeline en production, au-delà des métriques hors ligne que couvre la leçon 10.

## Lacunes

- Aucune source encore sur le chunking sémantique pour les corpus structurés ou riches en code (par opposition à la prose), où les heuristiques de taille fixe et de frontières de paragraphes donnent toutes deux de mauvais résultats ; à combler une fois que la conception des leçons atteindra le choix de la stratégie de chunking.
