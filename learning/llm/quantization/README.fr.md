---
title: "Quantification"
description: "Quantifier un LLM et le défendre : formats de nombres, méthodes PTQ et QAT, ce qui tourne plus vite, et mesurer ce que cela a coûté"
type: topic
---

# Apprentissage : la quantification

Prendre un LLM entraîné et le rendre plus petit et plus rapide par la quantification, en sachant ce que chaque format de nombres et chaque méthode fait à ses poids, à ses activations et à son KV cache. Finir capable de choisir un schéma pour un modèle, un matériel et un niveau de qualité donnés, de mesurer honnêtement ce que cela a coûté, et de relire l'affirmation de quelqu'un selon laquelle un modèle quantifié « ne perd rien ».

**Dernière leçon :** [27. Quand la réponse habituelle est fausse](lessons/0027-when-the-usual-answer-is-wrong.md)

## Objectif

- Lire l'agencement de bits d'un format de nombres, dire quelle plage et quelle précision il apporte, et calculer l'empreinte mémoire d'un modèle dans ce format.
- Quantifier un tenseur à la main : choisir le scale, le zero-point, la plage d'écrêtage et la granularité, et prédire d'où viendra l'erreur.
- Expliquer pourquoi les LLM ont des features et des activations outlier, et quelle technique traite chacune.
- Expliquer ce que l'arrondi au plus proche, GPTQ et AWQ font chacun aux poids, et ce que le calibration set apporte et peut mal faire.
- Décider quand les activations et le KV cache peuvent être quantifiés en plus des poids, et avec quelle technique.
- Dire quand le quantization-aware training vaut son coût face à la quantification post-entraînement.
- Prédire si un schéma tournera réellement plus vite sur un matériel donné à une taille de batch donnée, plutôt que de supposer que moins de bits veut dire plus vite.
- Mesurer, au-delà de la perplexity, la qualité qu'a coûtée une quantification, face à une référence honnête.
- Lire un checkpoint quantifié, en safetensors avec sa config de quantification ou en GGUF, et dire ce qu'il contient.
- Choisir un schéma pour un modèle, un matériel et un niveau de qualité donnés, relire l'affirmation de quantification de quelqu'un d'autre en nommant ce qu'elle cache, et dire quand la réponse habituelle est la mauvaise.

## Contraintes

- Suppose l'aisance avec la lecture de Python et de NumPy, et de savoir ce qu'est une couche de transformer au niveau de « multiplications de matrices plus attention ». Aucune connaissance préalable de la quantification ni du fonctionnement interne de la virgule flottante.
- Neutre vis-à-vis du matériel autant que possible. Quand une affirmation relève du comportement documenté d'un seul fournisseur ou d'une seule bibliothèque, la leçon le nomme, parce que la prise en charge par les kernels change plus vite que la théorie.
- La pratique des étapes 1 à 3 tourne sur un portable avec NumPy. Les exercices suivants quantifient un petit modèle ouvert, ce pour quoi un notebook GPU gratuit suffit.

## Hors périmètre

- QLoRA, entraîner un adapter à travers un modèle de base en 4 bits : voir [`llm/finetuning`](../../llm/finetuning/), étape 4 (leçons 0014 à 0017). Ce parcours enseigne la théorie générale que ces leçons appliquent, et y renvoie au lieu de répéter QLoRA.
- Choisir un schéma pour un budget de latence de serving et l'exécuter dans vLLM ou llama.cpp : voir [`llm/inference`](../../llm/inference/), étape 3 (leçons 0007 à 0009) et sa fiche [Quantification au moment du serving](../../llm/inference/reference/quantization-at-serve-time.md). Ce parcours enseigne comment fonctionnent les méthodes et comment les juger ; la décision de serving reste là-bas.
- Construire une eval : voir [`llm/evals`](../../llm/evals/) et sa fiche [Go/No-Go](../../llm/evals/reference/go-no-go.md). Ce parcours utilise une eval pour mesurer la perte de quantification et n'enseigne pas à nouveau comment en construire une.
- L'élagage (pruning), la sparsité et la distillation, les autres manières de réduire un modèle. Ils se combinent avec la quantification mais sont des sujets distincts. La distillation a son propre parcours, [`llm/distillation`](../../llm/distillation/), qui la compare à la quantification dans son étape de jugement.
- Écrire des kernels de quantification. L'étape 7 enseigne ce qu'un kernel doit faire pour qu'un schéma tourne plus vite, pas comment en écrire un.

La frontière avec les deux voisins a été fixée à l'écriture de ce parcours : les leçons de fine-tuning et d'inférence restent telles qu'elles sont, chacune enseignant la tranche dont son cas d'usage a besoin, et renvoient ici pour les fondations.

## Le fil conducteur

Dix étapes, de ce qu'est un format de nombres jusqu'au jugement nécessaire pour relire la quantification de quelqu'un d'autre. Une étape comprend plusieurs leçons et les frontières sont souples ; ce qui termine une étape, c'est la capacité acquise, pas le nombre de leçons.

| Étape | Leçons | Contenu | Terminée quand |
|---|---|---|---|
| 1. Formats de nombres | 0001 à 0003 | Ce que la quantification apporte, fp32, fp16, bf16, fp8, int8, int4 et formats à échelle par bloc | Vous savez lire l'agencement de bits d'un format et dimensionner un modèle dans ce format |
| 2. La correspondance de quantification | 0004 à 0006 | Quantifier et déquantifier, scale et zero-point, choix de la plage d'écrêtage, par tenseur, par canal et par groupe | Vous savez quantifier un tenseur à la main et prédire son erreur |
| 3. Outliers | 0007 à 0008 | Features outlier et activations massives dans les LLM, et les familles de parades | Vous savez dire pourquoi un LLM en int8 naïf casse et quelle parade s'applique |
| 4. Quantification des poids post-entraînement | 0009 à 0012 | Arrondi au plus proche, GPTQ, AWQ, le calibration set | Vous savez quantifier les poids d'un modèle en 4 bits et expliquer ce que chaque méthode a changé |
| 5. Activations et KV cache | 0013 à 0016 | Weight-only contre poids-et-activations, SmoothQuant, rotations, quantification du KV cache | Vous savez décider quoi quantifier au-delà des poids et avec quelle technique |
| 6. Quantization-aware training | 0017 à 0018 | Fake quantization, estimateur straight-through, QAT pour les LLM | Vous savez dire quand le QAT vaut son coût face au PTQ |
| 7. Matériel et kernels | 0019 à 0020 | Limité par la mémoire contre limité par le calcul, ce qu'un kernel doit prendre en charge, quel matériel exécute quel format | Vous savez prédire si un schéma tourne plus vite sur un matériel et une taille de batch donnés |
| 8. Mesurer la perte de qualité | 0021 à 0022 | La perplexity et ses limites, flips, suites de tâches, une comparaison honnête | Vous savez mesurer ce qu'a coûté une quantification et défendre le chiffre |
| 9. Formats de fichier | 0023 à 0024 | Safetensors avec configs de quantification, types de quantification GGUF et matrice d'importance | Vous savez lire un checkpoint quantifié et dire ce qu'il contient |
| 10. Le jugement | 0025 à 0027 | Choisir un schéma, relire une affirmation, livrer un modèle quantifié dont d'autres dépendent, quand la réponse habituelle est fausse | On vous fait confiance pour trancher sur une quantification et l'expliquer à quelqu'un d'autre |

## Leçons

Suivez-les dans l'ordre.

| # | Leçon | Enseigne |
|---|---|---|
| [0001](lessons/0001-what-quantization-buys.md) | Ce que la quantification apporte | Moins de bits par paramètre réduisent la mémoire et les octets lus par token, ce qui explique l'essentiel du gain de vitesse |
| [0002](lessons/0002-floating-point-formats.md) | Les formats à virgule flottante | Comment les bits de signe, d'exposant et de mantisse répartissent plage et précision en fp32, fp16 et bf16 |
| [0003](lessons/0003-low-bit-formats.md) | Les formats à faible nombre de bits | Ce que fp8, int8, int4 et les formats à échelle par bloc comme MXFP4 peuvent et ne peuvent pas représenter |
| [0004](lessons/0004-quantize-and-dequantize.md) | Quantifier et déquantifier | La correspondance affine entre valeurs réelles et entiers : scale, zero-point, arrondi et écrêtage |
| [0005](lessons/0005-choosing-the-range.md) | Choisir la plage | Pourquoi écrêter la plage échange un peu d'erreur d'écrêtage contre beaucoup moins d'erreur d'arrondi |
| [0006](lessons/0006-granularity.md) | La granularité | Scales par tenseur, par canal et par groupe, et ce que chacun coûte en bits stockés |
| [0007](lessons/0007-why-llms-have-outliers.md) | Pourquoi les LLM ont des outliers | Les dimensions de features outlier et les activations massives, où elles apparaissent et pourquoi une seule valeur ruine le scale d'un tenseur |
| [0008](lessons/0008-handling-outliers.md) | Traiter les outliers | Les quatre familles de parades : les garder en haute précision, réduire le groupe, les migrer ou les faire pivoter |
| [0009](lessons/0009-round-to-nearest.md) | Arrondi au plus proche | Quantifier les poids un par un sans données, pourquoi cela tient en 8 bits et décroche en 4 bits ou moins |
| [0010](lessons/0010-gptq.md) | GPTQ | Quantifier les poids d'une couche en séquence et dépenser chaque erreur d'arrondi sur les poids pas encore quantifiés |
| [0011](lessons/0011-awq.md) | AWQ | Protéger les poids qui rencontrent de grandes activations en mettant leurs canaux à l'échelle avant l'arrondi |
| [0012](lessons/0012-the-calibration-set.md) | Le calibration set | Quelles données de calibration une méthode lit, combien il lui en faut, et comment un jeu inadapté se manifeste |
| [0013](lessons/0013-weights-activations-or-both.md) | Poids, activations ou les deux | Ce que les schémas weight-only et poids-et-activations économisent chacun, et pourquoi les activations sont plus difficiles |
| [0014](lessons/0014-smoothquant.md) | SmoothQuant | Déplacer la difficulté de quantification des activations vers les poids avec un scale par canal |
| [0015](lessons/0015-rotations.md) | Les rotations | Multiplier par une matrice orthogonale pour répartir les outliers sur les canaux afin que des activations en 4 bits survivent |
| [0016](lessons/0016-kv-cache-quantization.md) | Quantification du KV cache | Pourquoi les clés et les valeurs se quantifient selon des axes différents, et ce que cela apporte à contexte long |
| [0017](lessons/0017-fake-quantization-and-the-ste.md) | Fake quantization et STE | Comment l'entraînement voit la quantification : un arrondi simulé dans la passe avant, un gradient straight-through dans la passe arrière |
| [0018](lessons/0018-qat-for-llms.md) | Le QAT pour les LLM | Ce que le quantization-aware training coûte sur un LLM, ce qu'il récupère, et quand le PTQ suffit |
| [0019](lessons/0019-what-actually-runs-faster.md) | Ce qui tourne vraiment plus vite | Pourquoi la quantification weight-only accélère le décodage à petit batch et peut ralentir le prefill à grand batch |
| [0020](lessons/0020-hardware-and-kernel-support.md) | Matériel et prise en charge par les kernels | Quels formats un GPU calcule nativement, lesquels il ne fait que stocker, et ce que coûte un kernel manquant |
| [0021](lessons/0021-perplexity-and-its-limits.md) | La perplexity et ses limites | Ce que mesure la perplexity, pourquoi un petit changement peut cacher de grands flips de réponses, et quoi mesurer à la place |
| [0022](lessons/0022-an-honest-quantization-eval.md) | Une eval de quantification honnête | Comparer un modèle quantifié à sa référence sur le même harness et les mêmes tâches, et rapporter ce qu'il a perdu et où |
| [0023](lessons/0023-quantized-checkpoints.md) | Checkpoints quantifiés | Ce que stocke un checkpoint safetensors quantifié, et comment sa config de quantification indique à un chargeur comment le lire |
| [0024](lessons/0024-gguf-quant-types.md) | Types de quantification GGUF | Ce que signifie un nom de type GGUF comme Q4_K_M, et ce que change la matrice d'importance |
| [0025](lessons/0025-choosing-a-scheme.md) | Choisir un schéma | Choisir un format et une méthode d'après le modèle, le matériel, la forme du batch et le niveau de qualité exigé |
| [0026](lessons/0026-reviewing-a-quantization-claim.md) | Relire une affirmation de quantification | Relire « 4 bits sans perte de qualité » en nommant ce que la mesure a caché, et déployer un modèle quantifié dont d'autres dépendent |
| [0027](lessons/0027-when-the-usual-answer-is-wrong.md) | Quand la réponse habituelle est fausse | Reconnaître quand des poids en 4 bits ou une recette standard est le mauvais choix, et trancher le différend à partir de la source primaire |

## Référence

- [Glossaire](GLOSSARY.md) : termes de référence pour ce sujet
- [Ressources](RESOURCES.md) : sources fiables, chacune annotée avec ce qu'elle couvre
- [Formats de nombres](reference/number-formats.md) : agencements de bits, plage et précision de chaque format, et arithmétique de la mémoire, issus de l'étape 1
- [La correspondance de quantification](reference/quantization-mapping.md) : les formules de quantification et de déquantification, choix de la plage, granularité et parades aux outliers, issus des étapes 2 et 3
- [Méthodes PTQ pour les poids](reference/weight-ptq-methods.md) : arrondi au plus proche, GPTQ et AWQ côte à côte, et ce que fait le calibration set, issus de l'étape 4
- [Activations et KV cache](reference/activations-and-kv-cache.md) : weight-only contre poids-et-activations, SmoothQuant, rotations et quantification du KV cache, issus de l'étape 5
- [QAT et matériel](reference/qat-and-hardware.md) : comment fonctionne le QAT et quand il rapporte, et ce qui fait tourner un schéma plus vite, issus des étapes 6 et 7
- [Mesurer et stocker](reference/measuring-and-storing.md) : une eval de quantification honnête, et comment lire un checkpoint quantifié ou un type GGUF, issus des étapes 8 et 9
- [Liste de contrôle de relecture d'une quantification](reference/quantization-review-checklist.md) : choisir un schéma et les questions à poser à l'affirmation de quantification de quelqu'un d'autre, issues de l'étape 10

## Comment cela fonctionne

Chaque leçon est courte et autonome. Les corrigés sont repliés : rappelez-vous d'abord, puis ouvrez-les. Les exercices en situation réelle comptent plus que la lecture, et les espacer dans le temps est justement le but. Tout ce qui reste flou à la fin d'une leçon mérite d'être suivi jusqu'à sa source primaire avant de passer à la suite.
