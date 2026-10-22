---
title: "Inférence"
description: "Servir un modèle : le KV cache, le batching, la quantification au moment du serving, et un budget de latence que vous pouvez défendre"
type: topic
---

# Apprentissage : l'inférence

Savoir mettre en place un serveur d'inférence pour un vrai modèle, d'abord sur GPU puis sur CPU/edge, et défendre les chiffres de latence et de débit qu'il produit, au lieu de citer ce que donnent par hasard les valeurs par défaut du framework.

**Dernière leçon :** [25. Relire une configuration de serving](lessons/0025-reviewing-a-serving-configuration.md)

## Objectif

- Mettre en place une pile de serving (vLLM sur GPU, puis llama.cpp sur CPU/edge) pour un modèle donné et la faire répondre à des requêtes.
- Annoncer un budget de latence p99 pour une taille de batch et un modèle donnés, et défendre ce chiffre à partir des choix de KV cache, de batching et de quantification qui l'ont produit.
- Relire la configuration de serving de quelqu'un d'autre et nommer précisément ce qu'elle coûte (un paramètre mal réglé par rapport au goulot d'étranglement de la charge de travail annoncée, une topologie choisie sans goulot d'étranglement qui la justifie, un déploiement qui casse un appelant en cours de route), au lieu de dire que quelque chose cloche.

## Contraintes

- Suppose l'aisance avec un environnement Python de ML et une familiarité de base avec ce qu'est un modèle de langage ; aucune expérience préalable de l'infrastructure de serving n'est requise.
- Piles principales : vLLM (GPU) et llama.cpp (CPU/edge), traitées dans cet ordre. Les autres piles (TGI, TensorRT-LLM) ne sont mentionnées que là où un concept se transpose différemment.

## Hors périmètre

- Entraîner ou faire du fine-tuning sur un modèle ou un adapter : voir [`llm/finetuning`](../../llm/finetuning/) (leçons 0025, servir des adapters, et 0026, coût, latence et débit), vers lesquelles ce parcours renvoie au lieu de les reprendre.
- Juger la qualité des sorties ou construire une eval pour un modèle servi : voir [`llm/evals`](../../llm/evals/) pour cette frontière.
- Comment fonctionnent les méthodes de quantification et comment les juger, des formats numériques et de la correspondance affine à GPTQ, AWQ, SmoothQuant, QAT et à la mesure de la perte de qualité : voir [`llm/quantization`](../../llm/quantization/). L'étape 3 garde ici la décision de serving, choisir un schéma pour un budget de latence, et renvoie là-bas pour les fondations ; cette frontière a été fixée lors de l'écriture du parcours sur la quantification.
- Demander une sortie structurée du côté du prompt : voir [`llm/prompting`](../../llm/prompting/). Ce parcours possède le décodage contraint, le côté serving du même objectif.

## Le fil conducteur

Quatorze étapes, de la première requête à une configuration de serving défendue, à l'échelle d'une flotte, surveillée en production et relue. Une étape comprend plusieurs leçons et les frontières sont souples ; ce qui termine une étape, c'est la capacité acquise, pas le nombre de leçons.

| Étape | Leçons | Contenu | Terminée quand |
|---|---|---|---|
| 1. Le KV cache | 0001 à 0003 | Pourquoi la génération autorégressive est coûteuse, ce que le cache échange contre de la mémoire, comment sa taille croît avec le contexte et le batch | Vous savez calculer l'empreinte mémoire du KV cache d'un modèle pour une longueur de contexte et une taille de batch données |
| 2. Le batching | 0004 à 0006 | Batching statique et continu, ordonnancement des requêtes, le compromis débit/latence | Vous savez défendre une configuration de batching pour une charge de travail donnée |
| 3. La quantification au moment du serving | 0007 à 0009 | int8/int4/AWQ/GPTQ à l'inférence, précision contre vitesse contre mémoire | Vous savez choisir un schéma de quantification au moment du serving et défendre le compromis |
| 4. vLLM en pratique | 0010 à 0012 | Mettre en place vLLM, PagedAttention, les paramètres de réglage qui comptent | Une pile vLLM tourne et répond à de vraies requêtes |
| 5. llama.cpp sur CPU/edge | 0013 à 0015 | GGUF, l'architecture de llama.cpp, ce qui change hors GPU | Une pile llama.cpp tourne sur CPU et répond à de vraies requêtes |
| 6. Le budget de latence | 0016 à 0017 | Méthodologie de mesure du p99, relier le chiffre aux choix de cache, de batching et de quantification | Vous savez annoncer et défendre de bout en bout un budget de latence p99 |
| 7. Le décodage spéculatif | 0018 | Décodage spéculatif avec draft model, n-gram, Medusa et EAGLE | Vous savez expliquer pourquoi la vérification parallèle est presque gratuite et choisir une variante de décodage spéculatif pour une charge de travail |
| 8. L'échantillonnage et le décodage contraint au moment du serving | 0019 | Paramètres d'échantillonnage par requête dans un batch partagé, décodage contraint indexé par automate à états finis | Vous savez expliquer pourquoi la garantie du décodage contraint est structurelle et pourquoi son coût par token reste faible |
| 9. Le prefix caching | 0020 | Prefix caching automatique comme partage de blocs entre requêtes, charges de travail de longs documents et multi-tours, sa limite au seul prefill | Vous savez expliquer quand le prefix caching aide une charge de travail et pourquoi il n'accélère jamais le decode |
| 10. Le parallélisme multi-GPU et multi-nœud | 0021 | Le mécanisme réel du parallélisme tensoriel au-delà de l'unique option de la leçon 12, le parallélisme de pipeline, et une procédure de décision pour savoir lequel (ou les deux) un déploiement exige | Vous savez expliquer ce que coûtent respectivement une étape de recombinaison du parallélisme tensoriel et une bulle de pipeline, et choisir la bonne répartition pour une interconnexion et un nombre de nœuds donnés |
| 11. Le serving à l'échelle d'une flotte | 0022 | Routage des requêtes informé par la localité du cache, autoscaling piloté par la profondeur de file, et pourquoi le temps de chargement du modèle lors d'un cold start borne la vitesse à laquelle une nouvelle réplique aide réellement | Vous savez expliquer comment le routage, l'autoscaling et la latence de cold start se raisonnent comme un seul pipeline plutôt que de se régler séparément |
| 12. L'observabilité et le coût en production | 0023 | Métriques exportées en continu, SLI/SLO/budgets d'erreur qui transforment une métrique en cible, et coût par million de tokens dérivé du débit mesuré | Vous savez défendre une configuration de production en citant son p99, le SLO et le budget d'erreur auxquels elle est tenue, et son coût par million de tokens |
| 13. Le contexte long au moment du serving | 0024 | RoPE scaling contre attention à fenêtre glissante et attention sinks, et ce que chacun fait réellement à la formule de croissance du cache de la leçon 2 | Vous savez expliquer si une technique de contexte long étend la longueur utilisable, plafonne la taille du cache à une constante, ou corrige le mode de défaillance d'un cache plafonné |
| 14. Le jugement | 0025 | Relire la configuration de quelqu'un d'autre pour y trouver des paramètres inadaptés, déployer sans risque en tenant compte de ce dont les autres dépendent, et dire quand le décodage spéculatif n'est pas un gain gratuit | On vous fait confiance pour relire une configuration de serving et nommer ce que coûte chaque choix, pas seulement dire que quelque chose cloche |

## Leçons

Suivez-les dans l'ordre.

| # | Leçon | Enseigne |
|---|---|---|
| [0001](lessons/0001-the-kv-cache.md) | Le KV cache | Pourquoi la génération devient coûteuse, et ce que la mise en cache rachète |
| [0002](lessons/0002-capacity-and-batch-size.md) | Capacité et taille de batch | Comment le partage de têtes (GQA/MQA) et la taille de batch changent l'empreinte réelle du cache |
| [0003](lessons/0003-growth-prefill-decode-precision.md) | Croissance, prefill, decode et précision | Comment le cache croît pendant le prefill et le decode, et ce que rachète une précision plus basse |
| [0004](lessons/0004-static-vs-continuous-batching.md) | Batching statique et continu | Pourquoi regrouper des requêtes améliore le débit, et pourquoi le continuous batching bat le batching statique |
| [0005](lessons/0005-request-scheduling.md) | Ordonnancement des requêtes | Comment un ordonnanceur de continuous batching choisit la requête suivante, et pourquoi un gros prefill peut bloquer tous les autres |
| [0006](lessons/0006-throughput-latency-tradeoff.md) | Le compromis débit/latence | Comment la taille de batch échange le débit contre la latence par token, et comment défendre une configuration de batching face à un budget de latence annoncé |
| [0007](lessons/0007-quantization-schemes.md) | Schémas de quantification au moment du serving | Ce que int8, int4, GPTQ et AWQ font réellement aux poids d'un modèle, et pourquoi la version naïve de la quantification à bas nombre de bits a besoin d'un correctif |
| [0008](lessons/0008-accuracy-speed-memory-tradeoffs.md) | Compromis entre précision, vitesse et mémoire | Pourquoi la mémoire, la vitesse et la précision n'évoluent pas ensemble quand un modèle est quantifié, et comment chacune se mesure réellement |
| [0009](lessons/0009-picking-a-quantization-scheme.md) | Choisir et défendre un schéma de quantification | Un cadre de décision pour choisir un schéma de quantification au moment du serving, et les trois chiffres qui le défendent |
| [0010](lessons/0010-standing-up-vllm.md) | Mettre en place vLLM | Installer vLLM, lancer son serveur, et trouver les options qui portent les concepts déjà enseignés |
| [0011](lessons/0011-pagedattention.md) | PagedAttention | Le mécanisme de table de blocs derrière vLLM, son compromis sur la taille de bloc, et comment il permet à des séquences de partager le cache d'un préfixe commun |
| [0012](lessons/0012-vllm-tuning-knobs.md) | Les paramètres de réglage de vLLM qui comptent | Deux options de plus, gpu-memory-utilization et tensor-parallel-size, plus une procédure de décision pour savoir quel paramètre un symptôme désigne réellement |
| [0013](lessons/0013-gguf.md) | GGUF | Ce que regroupe le format de modèle en un seul fichier de llama.cpp, ses noms de quantification, et pourquoi il peut être projeté en mémoire (memory-mapped) au lieu d'être chargé |
| [0014](lessons/0014-llamacpp-architecture.md) | L'architecture de llama.cpp | La bibliothèque de tenseurs ggml sous llama.cpp, son abstraction de backend, et en quoi le multithreading CPU diffère du batching GPU |
| [0015](lessons/0015-what-changes-off-gpu.md) | Ce qui change hors GPU | Mettre en place le serveur de llama.cpp, et comment le batching, la gestion du cache et la quantification se présentent chacun différemment à l'échelle CPU/edge |
| [0016](lessons/0016-p99-latency-methodology.md) | Méthodologie de mesure de la latence p99 | Pourquoi le p99 vaut mieux qu'une moyenne, pourquoi le TTFT et la latence inter-token exigent des chiffres séparés, et ce qui rend une mesure du p99 digne de confiance |
| [0017](lessons/0017-defending-a-latency-budget-end-to-end.md) | Défendre un budget de latence de bout en bout | Un ordre de diagnostic pour un budget p99 manqué, et les trois éléments que doit citer une configuration finale défendue |
| [0018](lessons/0018-speculative-decoding.md) | Décodage spéculatif | Vérifier plusieurs tokens candidats en une seule passe avant parallèle coûte à peu près ce que coûte normalement la génération d'un seul token, puisque le décodage est limité par le déplacement des poids et non par l'arithmétique, ce qui est le seul fait sur lequel repose chaque variante du décodage spéculatif |
| [0019](lessons/0019-sampling-and-constrained-decoding-at-serve-time.md) | Échantillonnage et décodage contraint au moment du serving | Un continuous batch fait déjà passer de nombreuses requêtes dans une seule passe avant partagée, et donner à chacune ses propres réglages d'échantillonnage, ou forcer l'une d'elles à ne produire que du JSON valide, doivent tous deux se faire ligne par ligne à l'intérieur de cette même passe partagée sans ralentir les autres |
| [0020](lessons/0020-prefix-caching.md) | Prefix caching | La leçon 11 laissait les échantillons parallèles d'une même requête partager les blocs en cache d'un seul prompt ; le prefix caching est le même partage appliqué à des requêtes par ailleurs sans lien, et il accélère exactement la phase que le prefill redondant gaspille, jamais la phase qui génère la réponse |
| [0021](lessons/0021-tensor-and-pipeline-parallelism.md) | Parallélisme tensoriel et de pipeline | La leçon 12 a nommé tensor-parallel-size comme une option qui répartit un modèle sur plusieurs GPU ; cette leçon ouvre ce que fait réellement cette répartition à l'intérieur d'une couche, présente le parallélisme de pipeline comme une autre façon de découper le même problème, et donne une procédure de décision pour savoir lequel (ou les deux) une charge de travail exige réellement |
| [0022](lessons/0022-fleet-level-serving.md) | Serving à l'échelle d'une flotte | L'ordonnanceur de la leçon 5 choisit la requête suivante dans la file d'un seul serveur ; une flotte ajoute une décision en amont, quel serveur reçoit la requête, une décision sur le moment d'ajouter des serveurs, et un coût de cold start qui rend un serveur fraîchement ajouté inutile pendant des dizaines de secondes |
| [0023](lessons/0023-production-observability-and-cost.md) | Observabilité et coût en production | La leçon 17 a défendu un chiffre p99 mesuré pour une configuration ; cette leçon couvre ce qu'il faut exporter en continu pour détecter une régression automatiquement, le SLO et le budget d'erreur qui font de « assez bon » une cible plutôt qu'une impression, et le chiffre du coût par million de tokens qu'il faut défendre en plus du p99, pas à sa place |
| [0024](lessons/0024-long-context-at-serve-time.md) | Contexte long au moment du serving | La formule de capacité de la leçon 2 facture la mémoire linéairement avec la longueur du contexte ; le RoPE scaling étend la longueur possible d'un contexte sans changer du tout cette facture, tandis que l'attention à fenêtre glissante et les attention sinks changent la formule elle-même en plafonnant la longueur du contexte à une constante |
| [0025](lessons/0025-reviewing-a-serving-configuration.md) | Relire une configuration de serving | Relire la configuration de serving de quelqu'un d'autre et nommer précisément ce qu'elle coûte (un paramètre mal réglé par rapport au goulot d'étranglement de la charge de travail annoncée, une topologie choisie sans goulot d'étranglement qui la justifie, un déploiement qui casse un appelant en cours de route), au lieu de dire que quelque chose cloche |

## Référence

- [Glossaire](GLOSSARY.md) : termes de référence pour ce sujet
- [Ressources](RESOURCES.md) : sources fiables
- [KV cache](reference/kv-cache.md) : coût par token, partage de têtes, croissance au fil d'une requête et planification de capacité
- [Batching](reference/batching.md) : batching statique et continu, ordonnancement des requêtes et compromis débit/latence
- [Quantification au moment du serving](reference/quantization-at-serve-time.md) : int8/int4/GPTQ/AWQ, pourquoi la mémoire, la vitesse et la précision n'évoluent pas ensemble, et un cadre de décision pour choisir un schéma
- [vLLM](reference/vllm.md) : mettre en place vLLM, PagedAttention et les paramètres de réglage qui comptent
- [llama.cpp](reference/llama-cpp.md) : GGUF, l'architecture de llama.cpp et ce qui change hors GPU
- [Budget de latence](reference/latency-budget.md) : méthodologie de mesure du p99, et relier un budget manqué aux choix de cache, de batching et de quantification

## Comment cela fonctionne

Chaque leçon est courte et autonome. Les corrigés sont repliés : rappelez-vous d'abord, puis ouvrez-les. Les exercices en situation réelle comptent plus que la lecture, et les espacer dans le temps est justement le but. Tout ce qui reste flou à la fin d'une leçon mérite d'être suivi jusqu'à sa source primaire avant de passer à la suite.
