---
title: "Glossaire"
description: "Termes de référence pour le RAG"
type: glossary
---

# Glossaire du RAG

Termes de référence pour un pipeline de récupération : en quoi il découpe les documents, et comment il décide ce qu'il transmet à l'étape de génération.

## Termes

**Récupération agentique** (agentic retrieval) :
Système qui décide, à chaque requête et à chaque étape, si la récupération est nécessaire, si ce qui est revenu suffit, et s'il faut récupérer à nouveau à partir de ce qui vient d'être déduit, au lieu de suivre un unique passage fixe de récupération puis de génération.
_À éviter_ : récupération multi-hop (un cas voisin mais plus étroit : le multi-hop couvre précisément le cas où une sous-question ultérieure dépend de la réponse à une sous-question antérieure, alors que la récupération agentique décide aussi s'il faut récupérer tout court)

**Chunk** :
Un morceau d'un document, produit en le découpant avant l'embedding et l'indexation, dimensionné pour que son embedding reste centré sur un seul sujet plutôt que d'être la moyenne de plusieurs.
_À éviter_ : segment, passage (à n'employer que pour citer une source qui utilise ce mot)

**Chunking** :
Processus qui consiste à découper un document en chunks, selon une taille fixe, selon la structure propre du document, ou en détectant où son sujet change.
_À éviter_ : découpage (trop générique ; à n'employer que dans une phrase qui décrit l'acte mécanique, pas comme nom du processus)

**Utilisation de la fenêtre de contexte** (context window utilization) :
Rapport entre le nombre de chunks effectivement cités dans une réponse générée et le nombre de chunks récupérés et placés dans le prompt. Une utilisation faible signifie que des tokens sont dépensés pour un contexte que le modèle n'a jamais utilisé ; une utilisation constamment élevée peut au contraire signaler que du contenu critique est tronqué hors de la fenêtre de contexte avant même de pouvoir être cité.
_À éviter_ : supposer qu'une utilisation plus élevée est toujours meilleure ; à haut niveau, c'est un signal de troncature, pas un simple gain d'efficacité

**Cascade d'erreurs** (error cascading) :
Une erreur à une étape précoce de l'ingestion (un titre mal identifié, des colonnes fusionnées dans le mauvais ordre) qui se propage à toutes les étapes suivantes, lesquelles travaillent sur la structure déjà corrompue qu'on leur a transmise, et corrompt tous les chunks d'une section entière au lieu de rester limitée à l'élément que l'erreur touchait directement.
_À éviter_ : une erreur d'analyse isolée (minimise l'effet ; nommer ce phénomène « cascade » sert justement à dire qu'une erreur précoce s'aggrave au lieu de rester locale)

**HyDE (Hypothetical Document Embeddings)** :
Fait de calculer l'embedding de la réponse hypothétique générée par un modèle de langage pour une requête, plutôt que celui de la requête elle-même, puis de chercher dans le corpus par similarité avec cet embedding. Tolère des détails factuellement faux dans le document hypothétique, puisque l'étape d'embedding de l'encodeur les filtre tout en préservant la vraie similarité thématique.
_À éviter_ : réécriture de requête (une autre correction côté requête : la réécriture reformule la requête elle-même, alors que HyDE calcule l'embedding d'une réponse générée au lieu de celui de la requête)

**Indexation incrémentale** (incremental indexing) :
Ajout de nouveaux vecteurs à un index déjà construit sans le reconstruire à partir de zéro. Bien prise en charge par HNSW, qui n'a pas d'étape d'entraînement ; moins bien par IVFFlat, dont les centroïdes de clusters sont fixés à la construction et jamais recalculés, si bien qu'un nouveau contenu qui diffère des données d'entraînement d'origine peut être mal regroupé.
_À éviter_ : réindexation (une reconstruction complète à partir de zéro, requise précisément quand le modèle d'embedding change, ce qui n'est pas la même opération que l'ajout incrémental de nouveaux vecteurs à un index inchangé)

**Ingestion** :
Transformation d'un document source brut (un PDF, une page HTML ou un fichier bureautique) en texte propre et structuré sur lequel le chunking opère réellement. Une véritable étape du pipeline, en amont du chunking, avec ses propres modes de défaillance, et non un détail de prétraitement qui échapperait à l'attention du pipeline.
_À éviter_ : traiter le chunking comme la première étape du pipeline (le chunking suppose que l'ingestion a déjà produit un texte propre ; c'est l'ingestion qui le produit réellement)

**Filtrage par métadonnées** (metadata filtering) :
Restriction de la récupération aux chunks qui satisfont un prédicat portant sur des attributs structurés (type de document, date, propriétaire, étiquette de permission) en plus de la similarité du plus proche voisin, plutôt que de chercher dans tout le corpus par la seule similarité.
_À éviter_ : filtrage par permissions (un cas particulier à enjeu plus élevé du filtrage par métadonnées, où une défaillance est un incident de sécurité et non une régression de qualité, et qui exige précisément un pré-filtrage)

**Récupération multi-hop** (multi-hop retrieval) :
Récupération en boucle où une requête ultérieure dépend d'un fait déduit d'une récupération antérieure, plutôt qu'un ensemble fixe de sous-questions décidées d'avance. Nécessaire quand une sous-question ne peut même pas être formulée avant que la réponse à une sous-question précédente soit connue, ce que la décomposition de requête seule ne peut pas gérer.
_À éviter_ : décomposition de requête (découpe des sous-questions déjà visibles dans le texte de la question d'origine ; la récupération multi-hop gère des sous-questions qui n'existent pas tant que la réponse d'un saut précédent ne les a pas produites)

**Post-filtrage** (post-filtering) :
Exécution d'abord d'une recherche ANN, puis rejet après coup des résultats qui échouent à un prédicat. Rapide, mais un prédicat sélectif peut écarter l'essentiel de ce que le balayage borné de candidats d'un index approximatif avait trouvé, ce qui fait chuter le recall ; pour un filtre de permissions en particulier, cela signifie aussi que du contenu non autorisé a brièvement existé dans le pipeline avant d'être écarté.
_À éviter_ : pré-filtrage (restreint l'ensemble des candidats avant l'exécution de la recherche ANN, ce qui préserve le recall sur l'ensemble filtré et ne laisse jamais le contenu interdit entrer dans le pipeline)

**Pré-filtrage** (pre-filtering) :
Restriction de l'ensemble des candidats aux seuls chunks qui satisfont un prédicat avant l'exécution de la recherche ANN, ce qui préserve le recall sur cet ensemble filtré quelle que soit la sélectivité du prédicat. Requis pour le contrôle d'accès en particulier, puisque le contenu non autorisé n'entre jamais dans le pipeline.
_À éviter_ : post-filtrage (cherche d'abord dans tout l'index et rejette ensuite ; le recall et, pour les filtres de permissions, la garantie de sécurité elle-même peuvent en pâtir)

**Décomposition de requête** (query decomposition) :
Découpage d'une question composée en sous-questions distinctes, avec une récupération indépendante pour chacune, plutôt que de calculer l'embedding de toute la question composée comme un seul vecteur qui se situe près d'aucun des passages qui répondraient bien à l'une de ses parties.
_À éviter_ : expansion multi-requête (une autre technique : l'expansion génère plusieurs reformulations complètes d'une même question, la décomposition découpe une question en sous-questions distinctes et plus étroites)

**Score sans référence** (reference-free scoring) :
Score de pertinence jugé par un LLM, calculé pour chaque chunk récupéré sans avoir besoin d'une réponse correcte connue, puis agrégé sur une fenêtre de temps sous forme de taux de réussite ou de pertinence moyenne. C'est ce que la surveillance en production utilise à la place de recall@k ou de MRR, qui exigent tous deux un jeu de requêtes étiqueté ou synthétique que la plupart du trafic réel n'a pas.
_À éviter_ : recall@k, MRR (des métriques hors ligne qui exigent des résultats connus comme corrects ; le score sans référence est précisément le substitut de production quand de telles étiquettes n'existent pas)

**Réindexation** (reindexing) :
Reconstruction d'un index vectoriel à partir de zéro, requise quand le modèle d'embedding lui-même change, puisque chaque vecteur existant a été produit dans l'espace vectoriel de l'ancien modèle et n'a aucune distance comparable avec les embeddings d'un nouveau modèle. Une opération différente de l'indexation incrémentale et de la maintenance périodique qu'exigent les suppressions et les mises à jour.
_À éviter_ : indexation incrémentale (ajout de nouveaux vecteurs à un index inchangé ; la réindexation désigne précisément la reconstruction de tout parce que le modèle qui produit les vecteurs a changé)
