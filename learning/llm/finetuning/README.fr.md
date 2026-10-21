---
title: "Fine-tuning avec adapters"
description: "Décider s'il faut faire du fine-tuning, le lancer, prouver qu'il a fonctionné, le livrer"
type: topic
---

# Apprentissage : le fine-tuning avec adapters (LoRA, QLoRA, DoRA)

Devenir la personne capable de prendre un base model et une tâche, de décider si le fine-tuning avec adapters est seulement la bonne réponse, de le lancer, de prouver qu'il a fonctionné avec une eval qui attraperait une régression, et de le livrer, et capable de plaider de façon convaincante pour le prompting ou la récupération quand ceux-ci feraient mieux le travail.

**Commencez ici :** [0001. Ce qu'est réellement un base model](lessons/0001-what-a-base-model-is.md)
**Dernière leçon :** [0027. Quand ne pas faire de fine-tuning](lessons/0027-when-not-to-fine-tune.md)

## Objectif

- Calculer le coût en mémoire du full fine-tuning face à celui de LoRA pour un modèle donné, et rendre compte de chaque octet.
- Choisir rank, alpha, target modules et learning rate pour une nouvelle tâche, et justifier chacun à partir de la tâche plutôt que des valeurs par défaut d'un billet de blog.
- Entraîner des adapters LoRA, QLoRA et DoRA sur la même tâche et expliquer les différences mesurées, pas celles qui sont annoncées.
- Construire une eval qui attrape une régression avant la livraison, au lieu de lire une courbe de loss en espérant que tout va bien.
- Servir un adapter à travers une pile d'inférence et mesurer ce qu'il a coûté en qualité et en latence.
- Diagnostiquer un run raté et nommer la cause : surapprentissage, oubli catastrophique, mauvais chat template, tokenizer incompatible, mauvais target modules.
- Lire un nouvel article sur PEFT et juger si le gain annoncé résisterait sur votre propre tâche.

## Contraintes

- Ne suppose aucune formation préalable en machine learning. La multiplication de matrices est la seule notion mathématique tenue pour acquise ; tout ce qui s'appuie dessus est enseigné là où c'est nécessaire.
- L'entraînement d'un adapter sur un base model de la classe 1B à 3B tient dans environ 16 Go de mémoire d'accélérateur ou de mémoire unifiée, ce qui met tout le parcours à portée d'un matériel ordinaire à un seul appareil.
- La prise en charge des backends est inégale, pas exclusive. CUDA reste la voie la plus complète et la mieux optimisée, et c'est là que les chiffres publiés se reproduisent le plus fiablement ; les autres backends fonctionnent avec une couverture de kernels variable et des pas plus lents. Chaque concept se transpose tel quel ; seules la vitesse et la disponibilité des kernels diffèrent.
- Les exercices ont une longue latence : un run d'entraînement prend de quelques minutes à plusieurs heures, donc les sessions se regroupent au lieu de tenir dans une soirée, avec de la lecture entre deux.
- Les outils évoluent plus vite que n'importe quel livre. Les API des bibliothèques se lisent dans la documentation de la version installée, jamais de mémoire.
- Rien dans le parcours n'exige d'infrastructure payante, même si louer un accélérateur plus gros accélérera certaines comparaisons.

## Hors périmètre

- Le full fine-tuning à grande échelle, le pré-entraînement et l'entraînement d'un modèle de zéro : voir [`llm/pretraining`](../../llm/pretraining/).
- RLHF, DPO et optimisation des préférences : voir [`llm/post-training`](../../llm/post-training/). Ce parcours possède la manière d'appliquer un changement à moins de paramètres ; celui-là possède l'objectif d'entraînement.
- La quantification comme sujet à part entière : voir [`llm/quantization`](../../llm/quantization/). L'étape 4 d'ici garde la tranche dont QLoRA a besoin et renvoie là-bas pour la théorie générale ; cette frontière a été fixée à l'écriture du parcours sur la quantification. La quantification au moment du service est couverte dans [`llm/inference`](../../llm/inference/).
- La distillation comme sujet à part entière : voir [`llm/distillation`](../../llm/distillation/). Ce parcours possède la manière d'appliquer un run d'entraînement à moins de paramètres ; celui-là possède l'objectif et les données de la distillation.
- Construire une infrastructure de service, au-delà du fait de faire tourner un adapter dans une pile existante : voir [`llm/inference`](../../llm/inference/).

## Le fil conducteur

Sept étapes, de zéro à senior. Une étape comprend plusieurs leçons et les frontières sont souples ; ce qui termine une étape, c'est la capacité acquise, pas le nombre de leçons.

| Étape | Leçons | Contenu | Terminée quand |
|---|---|---|---|
| 1. Les fondations | 0001 à 0004 | Ce que calcule une passe avant, où vivent les matrices de poids, tokenizers, chat templates, ce que l'entraînement change | Vous savez désigner quels tenseurs un adapter toucherait et pourquoi |
| 2. L'argument de la mémoire | 0005 à 0007 | Paramètres contre gradients contre état de l'optimizer, les deux moments d'AdamW, mémoire des activations, gradient checkpointing | Vous savez calculer, en octets, pourquoi le full fine-tuning échoue sur un appareil donné |
| 3. LoRA | 0008 à 0013 | `ΔW = BA`, rank, alpha et mise à l'échelle, initialisation, choix des target modules, l'exécuter, lire le run, fusionner | Vous entraînez un adapter et savez défendre chaque hyperparamètre |
| 4. Quantification et QLoRA | 0014 à 0017 | int8/int4, NF4, double quantification, rétropropagation à travers un base model quantifié gelé, ce qui se dégrade | Vous avez exécuté du vrai NF4 et savez dire ce que cela a coûté en qualité |
| 5. DoRA et le paysage des variantes | 0018 à 0020 | Décomposition magnitude/direction, pourquoi elle aide surtout à faible rank, comment évaluer l'affirmation d'une nouvelle variante | Vous savez prédire quand DoRA bat LoRA avant de lancer le run |
| 6. Données et évaluation | 0021 à 0024 | Construction du dataset, contamination, conception du jeu held-out, métriques de tâche contre loss, jeux de régression | Vous avez une eval qui a réellement attrapé une régression |
| 7. Exploiter et juger | 0025 à 0027 | Servir des adapters contre des modèles fusionnés, servir plusieurs adapters, coût et latence, quand *ne pas* faire de fine-tuning | On vous fait confiance pour décider si une tâche doit être fine-tunée tout court |

## Leçons

Suivez-les dans l'ordre.

| # | Leçon | Enseigne |
|---|---|---|
| [0001](lessons/0001-what-a-base-model-is.md) | Ce qu'est réellement un base model | Le modèle est une seule fonction du token suivant ; base n'est pas instruct |
| [0002](lessons/0002-where-the-weights-live.md) | Où vivent les poids | Nommer chaque projection à laquelle un adapter pourrait se rattacher |
| [0003](lessons/0003-tokenizers-and-chat-templates.md) | Tokenizers et chat templates | Entraînez sur le rendu que vous servirez |
| [0004](lessons/0004-what-training-changes.md) | Ce que l'entraînement change réellement | Les quatre opérations d'un pas d'entraînement |
| [0005](lessons/0005-counting-parameters-and-bytes.md) | Compter les paramètres et les octets | Transformer une configuration de modèle en gigaoctets |
| [0006](lessons/0006-gradients-and-optimizer-state.md) | Gradients et état de l'optimizer | Seize octets par paramètre entraînable, deux par paramètre gelé |
| [0007](lessons/0007-activations-and-checkpointing.md) | Activations, taille de batch et checkpointing | Pourquoi un run avec adapter manque quand même de mémoire |
| [0008](lessons/0008-the-low-rank-idea.md) | L'idée du faible rang | `ΔW = BA`, et compter un adapter |
| [0009](lessons/0009-rank-alpha-and-initialisation.md) | Rank, alpha et initialisation | Seul `α/r` compte, et pourquoi `B` démarre à zéro |
| [0010](lessons/0010-choosing-target-modules.md) | Choisir les target modules | « Attention seule » est une ablation de 2021, pas une valeur par défaut |
| [0011](lessons/0011-your-first-adapter.md) | Votre premier adapter | Un run qui prouve le pipeline avant de prouver quoi que ce soit d'autre |
| [0012](lessons/0012-reading-a-training-run.md) | Lire un run d'entraînement | Diagnostiquer d'après la forme de la courbe, et ce que la loss ne peut pas voir |
| [0013](lessons/0013-merging-and-shipping.md) | Fusionner, sauvegarder et livrer un adapter | La fusion est exacte ; un adapter est un diff qui a besoin de son base model |
| [0014](lessons/0014-quantisation-from-first-principles.md) | La quantification depuis les premiers principes | Des échelles par bloc, et pourquoi une seule valeur aberrante ruine un tenseur |
| [0015](lessons/0015-nf4-and-double-quantisation.md) | NF4 et double quantification | Les deux idées que QLoRA a réellement apportées |
| [0016](lessons/0016-training-through-a-quantized-base.md) | Entraîner à travers un base model quantifié | Comment les gradients traversent des poids gelés en 4 bits |
| [0017](lessons/0017-what-qlora-costs.md) | Ce que QLoRA coûte réellement | Séparer la dégradation du base model de celle de l'entraînement |
| [0018](lessons/0018-dora-magnitude-and-direction.md) | DoRA : magnitude et direction | La renormalisation découple les deux, et c'est cela, la méthode |
| [0019](lessons/0019-when-dora-wins.md) | Quand DoRA gagne, et quand non | Prédire le gain avant de lancer le run |
| [0020](lessons/0020-judging-a-new-variant.md) | Juger une nouvelle variante de PEFT | Six questions de triage, et la référence à battre |
| [0021](lessons/0021-building-the-dataset.md) | Construire le dataset | Les données l'emportent sur tous les hyperparamètres de cet espace de travail |
| [0022](lessons/0022-contamination-and-held-out-design.md) | Contamination et conception du jeu held-out | Découper selon la bonne clé, et dimensionner pour la question |
| [0023](lessons/0023-metrics-that-mean-something.md) | Des métriques qui veulent dire quelque chose | La loss sélectionne les checkpoints ; les métriques de tâche prennent les décisions |
| [0024](lessons/0024-the-regression-suite.md) | Le jeu de régression | Attraper les dégâts que tous les autres chiffres cachent |
| [0025](lessons/0025-serving-adapters.md) | Servir des adapters | Fusionner pour une tâche, router pour plusieurs |
| [0026](lessons/0026-cost-latency-and-throughput.md) | Coût, latence et débit | Prefill contre decode, et où va réellement l'argent |
| [0027](lessons/0027-when-not-to-fine-tune.md) | Quand ne pas faire de fine-tuning | Le fine-tuning est sixième sur la liste, et pourquoi cela compte |

## Référence

- [Glossaire](GLOSSARY.md) : termes de référence pour ce sujet
- [Ressources](RESOURCES.md) : sources et communautés fiables
- [Budget mémoire](reference/memory-budget.md) : le décompte des octets, et que tenter quand un run ne tient pas
- [Hyperparamètres de LoRA](reference/lora-hyperparameters.md) : rank, alpha, cibles, learning rate, variantes
- [Modes de défaillance](reference/failure-modes.md) : du symptôme à la cause, et les défaillances silencieuses

## Comment cela fonctionne

Chaque leçon est courte et autonome. Les corrigés sont repliés : rappelez-vous d'abord, puis ouvrez-les. Les exercices en situation réelle comptent plus que la lecture, et les espacer dans le temps est justement le but. Tout ce qui reste flou à la fin d'une leçon mérite d'être suivi jusqu'à sa source primaire avant de passer à la suite.
