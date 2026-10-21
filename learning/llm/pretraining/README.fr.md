---
title: "Pré-entraînement des LLM"
description: "Entraîner un modèle à partir de zéro à grande échelle : données, tokenizer, entraînement distribué et budget de calcul défendable"
type: topic
---

# Pré-entraînement des LLM

Savoir planifier et mener un job de pré-entraînement à partir d'une initialisation aléatoire : construire le pipeline de données, entraîner le tokenizer, choisir un budget de tokens compute-optimal pour un nombre de paramètres donné, empêcher un run distribué de plusieurs jours de diverger ou de caler sur la panne d'un nœud, et défendre cet ensemble de choix face à quelqu'un qui aurait sinon simplement fait du fine-tuning d'un modèle de base existant.

**Dernière leçon :** [0024. Relire la configuration d'entraînement de quelqu'un d'autre](lessons/0024-reviewing-someone-elses-training-run-config.md)

## Objectif

- Construire un corpus de pré-entraînement dédupliqué et filtré sur la qualité à partir de sources brutes, et dire ce que retire chaque étape de filtrage et pourquoi.
- Entraîner un tokenizer et défendre une taille de vocabulaire au regard de son effet sur la longueur des séquences et sur la taille de la table d'embeddings.
- Étant donné un nombre de paramètres et un budget de calcul, calculer le nombre de tokens compute-optimal et le défendre face à une alternative sous-entraînée à la Kaplan.
- Expliquer ce que ZeRO/FSDP partitionnent, pourquoi le parallélisme de données seul manque de mémoire avant de manquer de calcul, et quand le parallélisme tensoriel ou de pipeline vaut son coût de communication.
- Lire la courbe de loss et les normes de gradient d'un run d'entraînement, et dire si un pic est récupérable ou impose de repartir d'un checkpoint antérieur.
- Concevoir un schéma de checkpointing pour un run de plusieurs jours qui survit à la panne d'un nœud sans perdre plus de quelques minutes de progression.
- Décider si une tâche donnée appelle un pré-entraînement, un pré-entraînement continu ou le fine-tuning d'un modèle de base existant, et défendre ce choix sur le coût.

## Contraintes

- Proche des frameworks, pas agnostique. Les techniques d'entraînement distribué (partitionnement ZeRO, parallélisme tensoriel et de pipeline) sont assez stables pour que les leçons nomment la vraie bibliothèque et la vraie API décrites, à la différence du pseudo-code neutre vis-à-vis des fournisseurs qu'utilise `llm/agents` pour une surface qui évolue plus vite.
- Aucune leçon n'entraîne un modèle de taille frontière. Les exercices restent petits (un modèle de la taille de GPT-2 sur une poignée de GPU, ou une configuration multi-nœuds simulée) et raisonnent à partir de là sur ce qui change à l'échelle décrite par les articles cités.
- Suppose `llm/transformers` : le mécanisme d'attention, la boucle d'entraînement, la loss d'entropie croisée, AdamW, la précision mixte et le gradient clipping sont des prérequis, pas des rappels.
- On suppose l'accès à plusieurs GPU (même deux, ou une simulation CPU multi-processus des opérations collectives) pour les exercices d'entraînement distribué.

## Hors périmètre

- L'architecture transformer elle-même, la loss d'entropie croisée, la passe arrière, AdamW, la précision mixte et le gradient clipping : voir [`llm/transformers`](../../llm/transformers/). Ce parcours reprend quand cette boucle doit tourner sur des centaines de GPU face à des milliers de milliards de tokens, pas avant.
- Adapter un modèle de base existant avec LoRA, QLoRA ou DoRA : voir [`llm/finetuning`](../../llm/finetuning/). Le pré-entraînement part de poids aléatoires, pas d'un checkpoint, et ce sont les deux manières de modifier les poids d'un modèle, traitées comme sœurs plutôt que l'une incluant l'autre.
- Le parallélisme et la quantification au moment du serving : voir [`llm/inference`](../../llm/inference/). Ce parcours couvre les versions du parallélisme propres à l'entraînement (synchronisation des gradients, partitionnement des activations et de l'optimizer), pas le serving.
- La méthodologie d'évaluation et la conception des données held-out : voir [`llm/evals`](../../llm/evals/). Reprise ici seulement comme la capacité dont un run de pré-entraînement a besoin, valider un checkpoint en cours de run, et citée plutôt que reformulée.
- Aligner un modèle pré-entraîné en assistant : voir [`llm/post-training`](../../llm/post-training/).
- La distillation comme signal d'entraînement, y compris la distribution d'un enseignant utilisée pendant le pré-entraînement : voir [`llm/distillation`](../../llm/distillation/). Ce parcours enseigne la loss et le choix des données ; mener le job de pré-entraînement reste ici.

## Le fil conducteur

Dix étapes, de l'absence de connaissances préalables au jugement de niveau senior. Pas une liste de leçons : une étape comprend plusieurs leçons, et les frontières sont souples.

| Étape | Leçons | Contenu | Terminée quand |
| --- | --- | --- | --- |
| 1. Pipeline de données | 0001 à 0002 | Sourcing, déduplication, filtrage de qualité | Vous savez construire un corpus filtré et dédupliqué à partir de sources brutes et défendre ce que chaque étape a retiré |
| 2. Entraînement du tokenizer | 0003 à 0004 | BPE et SentencePiece depuis zéro, compromis sur la taille du vocabulaire | Vous savez entraîner un tokenizer et défendre le choix d'une taille de vocabulaire |
| 3. Lois d'échelle | 0005 à 0006 | Kaplan contre Chinchilla, le ratio tokens par paramètre compute-optimal | Étant donné un budget de calcul, vous savez en déduire un nombre de tokens compute-optimal et le défendre |
| 4. Parallélisme de données | 0007 à 0008 | All-reduce des gradients, pourquoi il cesse de passer à l'échelle seul | Vous savez dire pourquoi le parallélisme de données seul manque de mémoire avant de manquer de calcul |
| 5. Partitionner la mémoire | 0009 à 0011 | ZeRO stages 1 à 3, FSDP, partitionnement des activations et de l'optimizer | Vous savez dire ce que chaque stage ZeRO partitionne et ce qu'il coûte en communication |
| 6. Parallélisme de modèle | 0012 à 0014 | Parallélisme tensoriel et de pipeline pour l'entraînement | Vous savez décider quand le parallélisme tensoriel ou de pipeline justifie son coût de communication face au seul partitionnement |
| 7. Numérique et stabilité à grande échelle | 0015 à 0017 | Précision mixte à grande échelle, pics de loss, normes de gradient, schémas de warmup et de décroissance | Étant donné une courbe de loss, vous savez dire si un pic est récupérable ou impose un redémarrage depuis un checkpoint antérieur |
| 8. Checkpointing et tolérance aux pannes | 0018 à 0019 | Sauvegarder et reprendre un run de plusieurs jours, survivre à la panne d'un nœud | Vous savez concevoir un schéma de checkpointing qui borne la progression perdue après la panne d'un nœud |
| 9. Surveiller un run d'entraînement | 0020 à 0021 | Courbes de loss, checkpoints d'évaluation périodiques, lien avec `llm/evals` | Vous savez lire un tableau de bord d'entraînement et dire si le run est sur la bonne voie |
| 10. Le jugement | 0022 à 0024 | Pré-entraîner, poursuivre le pré-entraînement ou faire du fine-tuning, défendre un budget de calcul, relire la configuration d'entraînement de quelqu'un d'autre | On vous fait confiance pour trancher et l'expliquer à quelqu'un d'autre |

## Leçons

Suivez-les dans l'ordre.

| # | Leçon | Enseigne |
|---|---|---|
| [0001](lessons/0001-sourcing-and-mixing-a-pretraining-corpus.md) | Sourcer et mélanger un corpus de pré-entraînement | Ce qui entre dans un corpus de pré-entraînement, et pourquoi le mélange des sources compte plus que le nombre total d'octets |
| [0002](lessons/0002-deduplication-and-quality-filtering.md) | Déduplication et filtrage de qualité | Pourquoi les textes quasi dupliqués et les documents de faible qualité sont retirés avant l'entraînement, et ce que coûte le fait de sauter cette étape |
| [0003](lessons/0003-byte-pair-encoding-from-scratch.md) | Le byte-pair encoding depuis zéro | L'algorithme qui transforme les mots rares et inconnus en séquences d'unités de sous-mots apprises, déroulé à la main |
| [0004](lessons/0004-sentencepiece-and-the-vocabulary-size-tradeoff.md) | SentencePiece et le compromis sur la taille du vocabulaire | Tokeniser du texte brut sans pré-tokenizer, et ce que coûte réellement un vocabulaire plus grand ou plus petit |
| [0005](lessons/0005-scaling-laws-what-kaplan-predicted.md) | Les lois d'échelle : ce que Kaplan prédisait | Une loi de puissance empirique permet de prévoir la loss d'un run avant de le payer, et ce qu'elle prédisait sur la manière de dépenser un budget de calcul |
| [0006](lessons/0006-chinchilla-the-compute-optimal-correction.md) | Chinchilla : la correction compute-optimal | Pourquoi la taille du modèle et le nombre de tokens doivent croître ensemble, et comment transformer un budget de calcul en nombre de tokens |
| [0007](lessons/0007-data-parallelism-and-gradient-all-reduce.md) | Parallélisme de données et all-reduce des gradients | Répartir un batch entre des appareils qui détiennent chacun une copie complète du modèle, et ce qui garde chaque copie identique |
| [0008](lessons/0008-why-data-parallelism-alone-runs-out-of-memory.md) | Pourquoi le parallélisme de données seul manque de mémoire | Compter exactement ce qu'un optimizer Adam en précision mixte détient par paramètre, et où cela se heurte à un mur |
| [0009](lessons/0009-zero-stage-1-and-2-partitioning-optimizer-state-and-gradients.md) | ZeRO stage 1 et 2 : partitionner l'état de l'optimizer et les gradients | Supprimer gratuitement les copies redondantes du parallélisme de données, avant même que le coût de communication ait à croître |
| [0010](lessons/0010-zero-stage-3-and-fsdp-partitioning-parameters-too.md) | ZeRO stage 3 et FSDP : partitionner aussi les paramètres | Partitionner les paramètres eux-mêmes impose de les reconstruire à la demande, ce qui est le premier coût de cette approche |
| [0011](lessons/0011-activation-memory-and-zero-r.md) | Mémoire des activations et ZeRO-R | Partitionner les états du modèle résout un problème de mémoire et en laisse un second debout : les activations |
| [0012](lessons/0012-tensor-parallelism-splitting-a-layers-matrices.md) | Parallélisme tensoriel : découper les matrices d'une couche | Choisir l'axe selon lequel découper une matrice de poids pour qu'un bloc transformer entier n'ait besoin que d'un seul all-reduce |
| [0013](lessons/0013-pipeline-parallelism-splitting-the-models-layers.md) | Parallélisme de pipeline : découper les couches du modèle | Affecter des couches consécutives à des appareils différents, et le temps d'inactivité que cela coûte au début et à la fin de chaque batch |
| [0014](lessons/0014-combining-all-three-when-tensor-and-pipeline-parallelism-earn-their-cost.md) | Combiner les trois : quand les parallélismes tensoriel et de pipeline justifient leur coût | Faire correspondre chaque stratégie de parallélisme à l'interconnexion qu'elle tolère, et quand le partitionnement seul ne suffit pas |
| [0015](lessons/0015-mixed-precision-at-scale-bfloat16-and-stochastic-rounding.md) | Précision mixte à grande échelle : bfloat16 et arrondi stochastique | Un format numérique avec la plage du fp32 mais moins de précision, et ce que coûte la mise à jour directe des paramètres dans ce format |
| [0016](lessons/0016-loss-spikes-and-the-optimizers-own-instabilities.md) | Pics de loss et instabilités propres à l'optimizer | Le même pic peut venir d'un mauvais batch ou de l'optimizer lui-même, et les distinguer demande une comparaison contrôlée |
| [0017](lessons/0017-warmup-decay-and-growing-the-batch-mid-run.md) | Warmup, décroissance et croissance du batch en cours de run | Démarrer lentement, décroître selon un schéma, et laisser la taille du batch elle-même changer en cours d'entraînement |
| [0018](lessons/0018-what-a-checkpoint-has-to-hold.md) | Ce qu'un checkpoint doit contenir | Un checkpoint qui ne sauvegarde que les poids ne peut pas reprendre un run à l'identique, et choisir la fréquence de sauvegarde est un compromis à part entière |
| [0019](lessons/0019-surviving-a-node-failure.md) | Survivre à la panne d'un nœud | Mettre en pause, diagnostiquer, isoler ce qui est cassé et reprendre depuis le dernier checkpoint, quel qu'en soit le coût |
| [0020](lessons/0020-reading-a-loss-curve.md) | Lire une courbe de loss | La seule courbe de loss d'entraînement sous-estime les problèmes ; deux autres signaux repèrent ce qu'elle rate, et le repèrent plus tôt |
| [0021](lessons/0021-periodic-held-out-evaluation.md) | Évaluation held-out périodique | La loss d'entraînement dit que le modèle s'ajuste à ses propres données d'entraînement ; seul un contrôle held-out dit quelque chose du reste |
| [0022](lessons/0022-pretraining-is-usually-the-wrong-default.md) | Le pré-entraînement est souvent le mauvais choix par défaut | Une seconde phase de pré-entraînement sur un modèle existant obtient l'essentiel du bénéfice sans repayer le coût complet |
| [0023](lessons/0023-defending-a-compute-budget.md) | Défendre un budget de calcul | Un plan de pré-entraînement est un pari composé de nombreuses décisions distinctes, et le défendre revient à défendre chacune selon ses propres termes |
| [0024](lessons/0024-reviewing-someone-elses-training-run-config.md) | Relire la configuration d'entraînement de quelqu'un d'autre | Passer le plan au crible de chaque étape que ce parcours a couverte, dans l'ordre, et trancher une affirmation contestée à partir de la source plutôt que d'un article de blog |

## Référence

- [Glossaire](GLOSSARY.md) : termes de référence pour ce sujet
- [Ressources](RESOURCES.md) : sources fiables

## Comment cela fonctionne

Chaque leçon est courte et autonome. Les corrigés sont repliés : rappelez-vous d'abord, puis ouvrez-les. Les exercices en situation réelle comptent plus que la lecture, et les espacer dans le temps est justement le but. Tout ce qui reste flou à la fin d'une leçon mérite d'être suivi jusqu'à sa source primaire avant de passer à la suite.
