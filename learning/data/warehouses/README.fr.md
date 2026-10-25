---
title: Warehouses
description: "Maîtriser l'entrepôt analytique : stockage et exécution en colonnes, stockage séparé du calcul, et pourquoi les conseils de performance d'un stockage en lignes cessent de s'appliquer"
type: topic
---

# Apprentissage : les entrepôts analytiques

Savoir concevoir une table, un modèle et un chemin de chargement sur BigQuery, Snowflake ou Redshift qui répondent aux questions analytiques qu'on leur pose pour un coût que vous pouvez prévoir, et expliquer à partir de la disposition du stockage pourquoi un conseil juste sur un stockage en lignes y devient faux.

**Dernière leçon :** [20. Modifier un modèle que d'autres interrogent](lessons/0020-changing-a-model-others-query.md)

## Objectif

- Expliquer à partir de la disposition du stockage pourquoi une requête est bon marché sur un stockage en lignes et coûteuse sur un entrepôt en colonnes, ou l'inverse, et prédire ce qu'une modification de la requête change aux octets qu'elle parcourt.
- Dire ce que BigQuery, Snowflake et Redshift séparent chacun entre stockage et calcul, et dimensionner ou isoler le calcul pour une charge de travail donnée.
- Choisir le partitionnement, le clustering ou les sort keys et une distribution pour une table à partir de son profil de requêtes, et montrer le parcours que ce choix économise.
- Concevoir un modèle dimensionnel à un grain donné, y compris la façon dont une dimension qui change conserve son historique.
- Concevoir un chemin de chargement, par lots ou en micro-batch, qui peut être relancé sans dupliquer ni perdre de lignes.
- Estimer ce que coûte une requête ou une charge de travail en tarification à la demande et en tarification à la capacité, et réduire ce coût sans changer la réponse.
- Trancher entre un entrepôt, Postgres et un lakehouse pour une charge de travail, relire le schéma et la facture d'entrepôt de quelqu'un d'autre, et modifier un modèle que d'autres interrogent sans rien casser pour eux.

## Contraintes

- Suppose une pratique du SQL et aucune expérience préalable des entrepôts. Le langage, les plans de requête et la conception de schémas transactionnels sont enseignés dans [`programming/sql`](../../programming/sql/), et ces leçons les supposent acquis.
- BigQuery, Snowflake et Redshift sont les trois plateformes comparées tout au long du parcours. Chaque leçon enseigne d'abord le mécanisme, puis nomme la façon dont chaque plateforme l'expose, afin que le contenu survive à un changement de fournisseur.
- Les valeurs par défaut, les limites et les prix des plateformes évoluent d'une version à l'autre. Quand une leçon en cite un, elle nomme la page de documentation d'où il vient, et le lecteur doit consulter cette page pour la valeur actuelle.

## Hors périmètre

- Le langage SQL, les plans de requête, la conception de schémas et l'isolation sur un stockage en lignes : voir [`programming/sql`](../../programming/sql/), sur lequel ce parcours s'appuie au lieu de le répéter.
- L'exploitation d'une instance Postgres : voir [`data/postgres`](../../data/postgres/). L'étape 8 compare Postgres en tant que candidat pour une charge de travail analytique ; elle n'enseigne pas à l'exploiter.
- Les plateformes de streaming en tant que sujet. L'étape 6 charge depuis un flux ; le fonctionnement du log lui-même est traité dans [`data/kafka`](../../data/kafka/).
- Les frameworks d'orchestration et de transformation (Airflow, dbt) en tant que sujets. Ils apparaissent là où une leçon de chargement ou de modélisation en a besoin, et leur configuration n'est pas enseignée.
- Les outils de BI, les couches sémantiques et la conception de tableaux de bord.
- Spark, Trino et les autres moteurs en tant que sujets. L'étape 8 situe face à l'entrepôt le lakehouse qu'ils interrogent ; elle n'enseigne pas à les exploiter.

## Le fil conducteur

Huit étapes, de la disposition du stockage jusqu'au jugement. Une étape comprend plusieurs leçons et les frontières sont souples ; ce qui termine une étape, c'est la capacité acquise, pas le nombre de leçons.

| Étape | Leçons | Contenu | Terminée quand |
|---|---|---|---|
| 1. Stockage en lignes et en colonnes | 0001 à 0002 | Profils d'accès OLTP et OLAP, stockage en lignes face au stockage en colonnes, row groups, column chunks et leurs statistiques | Vous savez prédire quelle disposition lit le moins d'octets pour une requête donnée, et pourquoi |
| 2. Exécution en colonnes | 0003 à 0004 | Encodage par dictionnaire, run-length et delta, compression, exécution vectorisée, matérialisation tardive | Vous savez dire pourquoi un stockage en colonnes compresse et exécute comme il le fait, et ce que `SELECT *` y coûte |
| 3. Stockage et calcul | 0005 à 0006 | Comment BigQuery, Snowflake et Redshift séparent le stockage du calcul, slots, virtual warehouses, types de nœuds, concurrence et isolation des charges de travail | Vous savez dimensionner et isoler le calcul pour une charge de travail donnée sur n'importe laquelle des trois |
| 4. Conception physique | 0007 à 0010 | Partitionnement et élagage, clustering et sort keys, zone maps, distribution et stratégie de jointure, les conseils du stockage en lignes qui cessent de s'appliquer | Vous savez choisir la disposition physique d'une table à partir de son profil de requêtes et montrer le parcours qu'elle économise |
| 5. Modélisation dimensionnelle | 0011 à 0013 | Faits, dimensions et grain, schémas en étoile face aux tables larges et imbriquées, slowly changing dimensions | Vous savez concevoir un modèle à un grain donné qui conserve l'historique dont une question a besoin |
| 6. Chargement | 0014 à 0015 | ELT face à ETL, chargement par lots et taille des fichiers, ingestion en micro-batch et en streaming, merges idempotents | Vous savez concevoir un chemin de chargement qui peut être relancé sans dupliquer ni perdre de lignes |
| 7. Coût | 0016 à 0017 | Tarification à la demande et à la capacité sur chaque plateforme, lire le coût d'une requête, caches, vues matérialisées et les contrôles qui plafonnent une facture | Vous savez estimer le coût d'une charge de travail et le réduire sans changer la réponse |
| 8. Jugement | 0018 à 0020 | Entrepôt face à Postgres face à un lakehouse, relire un schéma et sa facture, modifier un modèle que d'autres interrogent, trancher un désaccord à partir de la documentation de la plateforme | On vous fait confiance pour trancher et l'expliquer à quelqu'un d'autre |

## Leçons

Suivez-les dans l'ordre.

| # | Leçon | Enseigne |
|---|---|---|
| [0001](lessons/0001-row-stores-and-column-stores.md) | Stockage en lignes et stockage en colonnes | Pourquoi une requête analytique lit sur un stockage en colonnes une fraction des octets qu'elle lit sur un stockage en lignes, et pourquoi la recherche d'une seule ligne va dans l'autre sens |
| [0002](lessons/0002-inside-a-columnar-file.md) | À l'intérieur d'un fichier en colonnes | Comment les row groups, les column chunks et les statistiques par chunk permettent à un lecteur de sauter des données qu'il ne décompresse jamais |
| [0003](lessons/0003-encoding-and-compression.md) | Encodage et compression | Pourquoi une colonne d'un seul type se compresse bien mieux qu'une ligne, et quel encodage convient à quelle forme de données |
| [0004](lessons/0004-vectorized-execution-and-late-materialization.md) | Exécution vectorisée et matérialisation tardive | Comment un moteur en colonnes traite un lot de valeurs par appel et n'assemble des lignes que pour les valeurs qui survivent |
| [0005](lessons/0005-separating-storage-from-compute.md) | Séparer le stockage du calcul | Ce que BigQuery, Snowflake et Redshift tiennent chacun à part entre l'endroit où vivent les données et ce qui les lit, et ce que cela apporte et coûte |
| [0006](lessons/0006-compute-sizing-concurrency-and-isolation.md) | Dimensionnement du calcul, concurrence et isolation des charges de travail | Comment dimensionner le calcul pour une charge de travail et empêcher les requêtes d'une équipe de faire la queue derrière celles d'une autre |
| [0007](lessons/0007-partitioning-and-pruning.md) | Partitionnement et élagage | Comment une table partitionnée permet à un filtre de sauter des partitions entières, et les filtres qui parcourent tout sans prévenir |
| [0008](lessons/0008-clustering-and-sort-keys.md) | Clustering et sort keys | Comment ordonner les données dans le stockage resserre le minimum et le maximum de chaque bloc pour qu'un filtre en saute davantage |
| [0009](lessons/0009-joins-and-data-distribution.md) | Jointures et distribution des données | Comment un entrepôt distribué déplace des lignes pour les joindre, et comment un choix de distribution décide s'il doit le faire |
| [0010](lessons/0010-the-row-store-advice-that-stops-applying.md) | Les conseils du stockage en lignes qui cessent de s'appliquer | Quelles habitudes d'indexation et de normalisation d'un stockage en lignes sont fausses sur un entrepôt en colonnes, et lesquelles tiennent toujours |
| [0011](lessons/0011-facts-dimensions-and-the-grain.md) | Faits, dimensions et grain | Comment déclarer ce que signifie une ligne d'une table de faits avant de choisir la moindre colonne |
| [0012](lessons/0012-star-schemas-wide-tables-and-nesting.md) | Schémas en étoile, tables larges et imbrication | Quand garder les dimensions dans leurs propres tables, quand les aplatir en une seule table large, et quand les imbriquer |
| [0013](lessons/0013-slowly-changing-dimensions.md) | Slowly changing dimensions | Comment une dimension garde ou abandonne son historique quand un attribut change, et ce que chaque choix fait aux anciens rapports |
| [0014](lessons/0014-elt-and-batch-loading.md) | ELT et chargement par lots | Pourquoi les entrepôts chargent d'abord les données brutes et les transforment sur place, et comment le nombre et la taille des fichiers décident de la vitesse de chargement |
| [0015](lessons/0015-micro-batch-streaming-and-idempotent-merges.md) | Micro-batch, streaming et merges idempotents | Comment déposer des données en continu et faire qu'une relance de n'importe quel chargement laisse la table exactement comme l'aurait laissée une seule exécution |
| [0016](lessons/0016-how-a-warehouse-bills.md) | Comment un entrepôt facture | Ce que chaque plateforme facture en tarification à la demande et à la capacité, et quelle charge de travail chaque modèle avantage |
| [0017](lessons/0017-reading-and-cutting-a-querys-cost.md) | Lire et réduire le coût d'une requête | Comment savoir ce que coûtera une requête avant de l'exécuter, et les modifications qui réduisent ce coût sans changer sa réponse |
| [0018](lessons/0018-warehouse-postgres-or-lakehouse.md) | Entrepôt, Postgres ou lakehouse | Comment décider où placer une charge de travail analytique, et quand la réponse habituelle, un entrepôt, est la mauvaise |
| [0019](lessons/0019-reviewing-a-warehouse-schema-and-its-bill.md) | Relire un schéma d'entrepôt et sa facture | Comment relire la conception d'entrepôt de quelqu'un d'autre et nommer ce que coûte chaque choix, en octets et en argent |
| [0020](lessons/0020-changing-a-model-others-query.md) | Modifier un modèle que d'autres interrogent | Comment modifier une table dont dépendent des tableaux de bord et des pipelines sans les casser, et comment trancher une affirmation contestée à partir de la documentation |

## Référence

- [Glossaire](GLOSSARY.md) : termes de référence pour ce sujet
- [Ressources](RESOURCES.md) : sources fiables, chacune annotée avec ce qu'elle couvre
- [Stockage et exécution en colonnes](reference/columnar-storage-and-execution.md) : disposition en lignes face à la disposition en colonnes, les encodages, et ce qu'un moteur en colonnes saute
- [Comparaison des plateformes](reference/platforms-compared.md) : comment BigQuery, Snowflake et Redshift nomment et facturent les mêmes idées de stockage et de calcul
- [Conception physique](reference/physical-design.md) : partitionnement, clustering, sort keys et distribution sur chaque plateforme, et les habitudes du stockage en lignes à abandonner
- [Modélisation dimensionnelle](reference/dimensional-modelling.md) : les quatre étapes de conception, les formes de schéma et les types de slowly changing dimensions
- [Chargement](reference/loading.md) : méthodes de chargement par plateforme, taille des fichiers, et les schémas qui permettent de relancer un chargement sans risque
- [Modèle de coût](reference/cost-model.md) : ce que facture chaque modèle de tarification, comment lire le coût d'une requête, et les contrôles qui plafonnent une facture
- [Revue de schéma et de facture](reference/schema-and-bill-review.md) : une liste de contrôle pour relire la conception d'un entrepôt et sa facture, et la décision de placement

## Comment cela fonctionne

Chaque leçon est courte et autonome. Les corrigés sont repliés : rappelez-vous d'abord, puis ouvrez-les. Les exercices en situation réelle comptent plus que la lecture, et les espacer dans le temps est justement le but. Tout ce qui reste flou à la fin d'une leçon mérite d'être suivi jusqu'à sa source primaire avant de passer à la suite.
