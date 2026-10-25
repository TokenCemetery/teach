---
title: Parcours d'apprentissage
description: Chaque sujet de ce dépôt, regroupé par domaine
type: index
---

# Parcours d'apprentissage

Regroupés par domaine, un répertoire par sujet. Chaque sujet est un parcours autonome piloté par le skill `teach` : une mission, un ensemble ordonné de leçons, et le matériel de référence que ces leçons ont produit.

## Sujets

| Domaine | Sujet | Mission | Leçons |
|---|---|---|---|
| programming | [Bash](programming/bash/) | Écrire du shell qui survit à la production : quoting, code de sortie, modes de défaillance, et savoir quand s'arrêter pour passer à un vrai langage | 17 |
| programming | [C#](programming/csharp/) | Maîtriser un service C# : le système de types, l'async, et ce que fait le CLR de ce que vous avez écrit | 45 |
| programming | [Go](programming/golang/) | Maîtriser Go au sein d'une équipe : concevoir, livrer et exploiter un service de production | 41 |
| programming | [Java](programming/java/) | Maîtriser un service Java : le modéliser en Java moderne, puis exploiter ce qu'en fait la JVM | 52 |
| programming | [Kotlin](programming/kotlin/) | Maîtriser Kotlin sur la JVM : null safety, coroutines, et les cas où l'habitude Java produit du Kotlin qui compile mais se lit mal | 44 |
| programming | [Python](programming/python/) | Maîtriser Python en production : le livrer typé, testé, empaqueté et profilé | 44 |
| programming | [Rust](programming/rust/) | Maîtriser Rust : concevoir avec l'ownership au lieu de lutter contre le borrow checker, puis livrer la crate | 67 |
| programming | [SQL](programming/sql/) | Maîtriser la base de données : écrire la requête, lire le plan, concevoir le schéma, survivre à la concurrence | 53 |
| programming | [TypeScript](programming/typescript/) | Maîtriser une base de code TypeScript : faire rejeter par le compilateur les états qui ne devraient pas exister | 49 |
| llm | [Fine-tuning avec adapters](llm/finetuning/) | Décider s'il faut faire du fine-tuning, le lancer, prouver qu'il a fonctionné, le livrer | 27 |
| llm | [Pré-entraînement](llm/pretraining/) | Entraîner un modèle à partir de zéro à grande échelle : données, tokenizer, entraînement distribué et budget de calcul défendable | 24 |
| llm | [Post-training](llm/post-training/) | Aligner un modèle de base : SFT, modélisation de récompense, RLHF, DPO et GRPO, et savoir lequel choisir | 20 |
| llm | [Inférence](llm/inference/) | Servir un modèle : le KV cache, le batching, la quantification au moment du serving, et un budget de latence que vous pouvez défendre | 24 |
| llm | [Evals](llm/evals/) | Prouver qu'une modification de modèle a aidé : construire l'eval, garder honnêtement les données held-out et défendre le chiffre face à la contamination | 18 |
| llm | [RAG](llm/rag/) | Maîtriser la récupération : chunking, embeddings, recherche hybride, reranking, et mesurer si la bonne information a été récupérée | 19 |
| llm | [Transformers](llm/transformers/) | Construire l'attention à partir de zéro, pour que l'architecture cesse d'être une boîte noire derrière le script d'entraînement | 22 |
| llm | [Agents](llm/agents/) | Construire la boucle soi-même : outils, contexte, mémoire, et savoir quand un agent est la mauvaise réponse | 37 |
| llm | [Quantification](llm/quantization/) | Quantifier un LLM et le défendre : formats de nombres, méthodes PTQ et QAT, ce qui tourne plus vite, et mesurer ce que cela a coûté | 27 |
| llm | [Prompting](llm/prompting/) | Écrire, versionner et livrer les prompts d'une fonctionnalité LLM, prouver qu'une modification de prompt a aidé, et relire le prompt de production de quelqu'un d'autre | 24 |
| llm | [Distillation](llm/distillation/) | Distiller un grand modèle en un plus petit et le défendre : soft targets, loss sur les logits et au niveau de la séquence, données synthétiques, entraînement on-policy, et ce que l'élève a perdu | 27 |
| data | [Postgres](data/postgres/) | Exploiter Postgres : le WAL, le vacuum et le bloat, la réplication, et ce que coûte l'entretien d'un index | 18 |
| data | [Kafka](data/kafka/) | Maîtriser le log : partitions, consumer groups, garanties de livraison, et ce que coûte réellement « exactly once » | 16 |
| data | [Redis](data/redis/) | Utiliser Redis pour ce qu'il est : le modèle mémoire, l'éviction, la persistance, et les usages qui le détournent sans bruit | 17 |
| data | [Warehouses](data/warehouses/) | Maîtriser l'entrepôt analytique : stockage et exécution en colonnes, stockage séparé du calcul, et pourquoi les conseils de performance d'un stockage en lignes cessent de s'appliquer | 20 |
| data | [Stream Processing](data/stream-processing/) | Calculer sur un flux avec Kafka Streams : topologies, état, fenêtres et jointures, et ce que coûte une topologie avant d'arriver en production | 20 |
| architecture | [Systèmes distribués](architecture/distributed-systems/) | Raisonner sur la défaillance partielle : ce qu'un réseau peut vous faire, quelle cohérence vous achetez réellement, et pourquoi le consensus coûte cher | 19 |
| architecture | [Conception d'API](architecture/api-design/) | Concevoir une interface dont d'autres dépendent : le contrat, ses erreurs, et comment il évolue sans les casser | 19 |
| infrastructure | [Conteneurs](infrastructure/containers/) | Empaqueter un service sous forme d'image de conteneur et la maîtriser : primitives du noyau, Dockerfiles, exécution, sécurisation et débogage d'un conteneur | 24 |
| infrastructure | [Kubernetes](infrastructure/kubernetes/) | Faire tourner des services sur un cluster Kubernetes et les maîtriser : la boucle de réconciliation, les workloads, le réseau, la configuration, la fiabilité, la sécurité, le packaging et le débogage | 28 |
| infrastructure | [CI/CD](infrastructure/ci-cd/) | Construire, tester et livrer chaque modification via un pipeline, et le maîtriser : workflows, feedback rapide, artefacts, secrets, déploiements, rollback et sécurité de la chaîne d'approvisionnement | 30 |

## Commencer un sujet

```bash
cp -r templates/learning-workspace learning/<domain>/<topic-slug>
```

Lancez ensuite le skill `teach` et nommez le sujet. Il lit le parcours, remplit la mission en vous interrogeant, et écrit la première leçon.

Un domaine est un regroupement, pas un parcours : il contient des répertoires de sujets et rien d'autre. Créez-en un nouveau quand un deuxième sujet le partagerait.

## Organisation

```text
learning/
├── <domain>/              # programming, llm, …
│   └── <topic>/           # one track per topic
├── .nav.yml               # sidebar order/titles for the published site
└── README.md              # this index
```

Chaque parcours :

```text
learning/<domain>/<topic>/
├── README.md              # mission, success criteria, lesson index
├── GLOSSARY.md            # canonical terms for this topic
├── RESOURCES.md           # trusted sources, known gaps
├── NOTES.md               # preferences and working notes
├── lessons/               # NNNN-slug.md, one tight win each
├── reference/             # cheat sheets, built for lookup
└── learning-records/      # NNNN-slug.md, what was demonstrably learned
```

Les leçons sont numérotées à partir de `0001` dans chaque parcours. Les parcours peuvent se lier entre eux, mais un lien est un pointeur plutôt qu'une inclusion : il n'importe pas le matériel d'un autre sujet dans cette mission. Préférez lier un terme du glossaire ou une fiche de référence plutôt qu'une leçon, car ceux-ci sont écrits pour la consultation et conviennent à n'importe quel lecteur.

Le skill `teach` définit le format de chaque fichier ici. Lisez [sa spécification](https://github.com/TokenCemetery/teach/blob/main/.agents/skills/teach/SKILL.md) avant d'en rédiger un à la main.

## Licence

Tout le contenu de ce site est sous licence [CC BY 4.0](https://github.com/TokenCemetery/teach/blob/main/LICENSE-CONTENT). Copiez-le, traduisez-le, enseignez à partir de lui, construisez dessus, à des fins commerciales ou non. Indiquez simplement d'où il vient.
