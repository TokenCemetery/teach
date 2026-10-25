---
title: Stream Processing
description: "Calculer sur un flux avec Kafka Streams : topologies, état, fenêtres et jointures, et ce que coûte une topologie avant d'arriver en production"
type: topic
---

# Apprentissage : le traitement de flux

Savoir construire, tester et exécuter une application Kafka Streams qui donne la bonne réponse quand les enregistrements arrivent en retard, dans le désordre ou en double, et dire à partir de sa topologie quels topics internes, quel état et quel temps de reprise elle coûtera avant d'arriver en production.

**Dernière leçon :** [20. Modifier une topologie dont d'autres dépendent](lessons/0020-changing-a-topology-others-depend-on.md)

## Objectif

- Expliquer à partir de la dualité flux-table comment un topic, un changelog et une KTable sont liés, et prédire ce qu'une topologie émet pour une entrée donnée.
- Construire une topologie avec le DSL, lire la sortie de `describe()` et nommer chaque topic interne qu'elle crée, et pourquoi.
- Choisir un state store pour une opération avec état et dire comment son état est reconstruit quand l'instance qui le détient meurt.
- Choisir une fenêtre et une période de grâce pour une question temporelle, et dire quels enregistrements en retard elle écarte et quand elle émet un résultat.
- Choisir une jointure pour deux entrées, les rendre co-partitionnées ou dire pourquoi une GlobalKTable évite ce besoin, et prédire la sortie de la jointure.
- Dire ce que garantit `exactly_once_v2` et ce qu'il laisse de côté, et dimensionner les tâches, les threads, les instances et les répliques standby d'une application pour un temps de reprise donné.
- Tester une topologie avec `TopologyTestDriver`, et exploiter une application en cours d'exécution à partir de ses métriques, de ses états et de ses gestionnaires d'exceptions.
- Trancher entre Kafka Streams, un simple consommateur, Flink et ksqlDB pour une charge de travail, relire la topologie de quelqu'un d'autre, et modifier une topologie en cours d'exécution sans casser son état ni ses consommateurs en aval.

## Contraintes

- Suppose une pratique de Java et du log tel que l'enseigne [`data/kafka`](../../data/kafka/) : partitions, consumer groups, garanties de livraison, rétention et compaction. Ces leçons y renvoient au lieu d'en redériver quoi que ce soit.
- Kafka Streams est le seul moteur enseigné. Les exemples utilisent le DSL Java et la Processor API d'Apache Kafka 4.3.
- Les valeurs par défaut et les protocoles évoluent d'une version à l'autre. Quand une leçon en cite un, elle nomme la page de documentation ou le KIP d'où il vient, et le lecteur doit consulter cette page pour la valeur actuelle.

## Hors périmètre

- Le log lui-même : partitions, consumer groups, sémantiques de livraison, le coût des transactions, rétention et compaction, Kafka Connect et Schema Registry. Voir [`data/kafka`](../../data/kafka/), sur lequel ce parcours s'appuie.
- La défaillance partielle et la cohérence en tant que théorie : voir [`architecture/distributed-systems`](../../architecture/distributed-systems/). Ce parcours n'enseigne que ce que la reprise des state stores et le rebalancing changent pour une application Streams.
- Apache Flink, Spark Structured Streaming et ksqlDB en tant que sujets. L'étape 8 les compare à Kafka Streams en tant que candidats pour une charge de travail ; elle n'enseigne pas à les exploiter.
- Le langage Java : voir [`programming/java`](../../programming/java/).
- Le chargement d'un flux dans un entrepôt analytique : voir [`data/warehouses`](../../data/warehouses/).

## Le fil conducteur

Huit étapes, de la dualité flux-table jusqu'au jugement. Une étape comprend plusieurs leçons et les frontières sont souples ; ce qui termine une étape, c'est la capacité acquise, pas le nombre de leçons.

| Étape | Leçons | Contenu | Terminée quand |
|---|---|---|---|
| 1. Flux et tables | 0001 à 0002 | La dualité flux-table, les topics compactés comme tables, ce qu'exécute une application Streams et où | Vous savez dire si un topic se lit comme un flux ou comme une table, et ce qu'une application Streams ajoute à un consommateur |
| 2. Topologies | 0003 à 0004 | Le DSL, sources, processeurs et sinks, `describe()`, Serdes, opérations sans état, changements de clé et topics de repartitionnement | Vous savez lire une topologie et nommer chaque topic interne qu'elle crée |
| 3. État | 0005 à 0007 | State stores, topics de changelog, agrégations, mises à jour de KTable, le cache d'enregistrements, la Processor API et les punctuators | Vous savez choisir un store pour une étape avec état et dire comment son état survit à la mort d'une instance |
| 4. Temps et fenêtres | 0008 à 0010 | Temps de l'événement, temps de traitement et stream time, extracteurs de timestamp, fenêtres tumbling, hopping, sliding et de session, périodes de grâce, suppression | Vous savez choisir une fenêtre et une période de grâce pour une question et dire quels enregistrements elle écarte |
| 5. Jointures | 0011 à 0012 | Jointures flux-table et avec une GlobalKTable, co-partitionnement, jointures flux-flux fenêtrées, jointures table-table et par clé étrangère | Vous savez choisir une jointure pour deux entrées et prédire ce qu'elle émet |
| 6. Garanties et mise à l'échelle | 0013 à 0015 | `exactly_once_v2`, tâches, threads et instances, rebalancing, restauration de l'état, répliques standby et warmup, le protocole de rebalancing streams | Vous savez dire ce que couvre l'exactly-once et dimensionner une application pour un temps de reprise donné |
| 7. Tests et exploitation | 0016 à 0017 | `TopologyTestDriver`, métriques, états du client et des threads, gestionnaires d'exceptions, interactive queries, les outils d'exploitation | Vous savez tester une topologie sans broker et dire à partir de ses métriques si une application en cours d'exécution est en bonne santé |
| 8. Jugement | 0018 à 0020 | Streams face à un simple consommateur, à Flink et à ksqlDB, relire une topologie, modifier une topologie dont d'autres dépendent, trancher un désaccord à partir de la source | On vous fait confiance pour trancher et l'expliquer à quelqu'un d'autre |

## Leçons

Suivez-les dans l'ordre.

| # | Leçon | Enseigne |
|---|---|---|
| [0001](lessons/0001-streams-and-tables.md) | Flux et tables | Pourquoi un flux de changements et une table de valeurs courantes sont deux vues des mêmes données, et comment un topic peut contenir l'un ou l'autre |
| [0002](lessons/0002-a-streams-app-is-a-library.md) | Une application Streams est une bibliothèque | Ce qui s'exécute quand une application Kafka Streams démarre : des consommateurs, des producteurs et un état local dans votre propre processus, sans cluster à elle |
| [0003](lessons/0003-the-dsl-and-topologies.md) | Le DSL et les topologies | Comment les appels au DSL construisent une topologie de sources, de processeurs et de sinks, et comment la lire à partir de `describe()` |
| [0004](lessons/0004-stateless-operations-and-repartitioning.md) | Opérations sans état et repartitionnement | Quelles opérations transforment un enregistrement à la fois, et quel changement de clé fait écrire un topic de repartitionnement à l'étape avec état suivante |
| [0005](lessons/0005-state-stores-and-changelog-topics.md) | State stores et topics de changelog | Où une opération avec état garde son état, et comment un topic de changelog compacté permet à une autre instance de le reconstruire |
| [0006](lessons/0006-aggregations-ktables-and-the-record-cache.md) | Agrégations, KTables et cache d'enregistrements | Pourquoi une KTable émet un flux de mises à jour plutôt que des réponses définitives, et comment le cache d'enregistrements et l'intervalle de commit décident de leur nombre |
| [0007](lessons/0007-the-processor-api.md) | La Processor API | Quand descendre sous le DSL vers un processeur personnalisé avec son propre store et son punctuator, et ce dont vous êtes alors responsable |
| [0008](lessons/0008-event-time-processing-time-and-stream-time.md) | Temps de l'événement, temps de traitement et stream time | Quelle horloge suit une opération Streams, d'où vient le timestamp d'un enregistrement, et pourquoi le stream time ne fait qu'avancer |
| [0009](lessons/0009-windowed-aggregations.md) | Agrégations fenêtrées | Comment les fenêtres tumbling, hopping, sliding et de session regroupent les enregistrements par temps, et à quelle question répond chacune |
| [0010](lessons/0010-late-data-grace-periods-and-suppression.md) | Données en retard, périodes de grâce et suppression | Combien de temps une fenêtre accepte des enregistrements dans le désordre, ce que deviennent ceux qui arrivent après, et comment n'émettre qu'un résultat définitif |
| [0011](lessons/0011-stream-table-joins-and-co-partitioning.md) | Jointures flux-table et co-partitionnement | Comment un flux enrichit chaque enregistrement à partir d'une table, pourquoi les deux côtés doivent être co-partitionnés, et quand une GlobalKTable supprime ce besoin |
| [0012](lessons/0012-stream-stream-and-table-table-joins.md) | Jointures flux-flux et table-table | Comment une jointure fenêtrée apparie les événements de deux flux, et comment les jointures de tables, y compris par clé étrangère, maintiennent un résultat à jour |
| [0013](lessons/0013-exactly-once-in-kafka-streams.md) | L'exactly-once dans Kafka Streams | Ce que `exactly_once_v2` rend atomique à travers les lectures, l'état et les écritures, et quels effets de bord il ne peut pas couvrir |
| [0014](lessons/0014-tasks-threads-and-scaling-out.md) | Tâches, threads et mise à l'échelle horizontale | Comment les partitions deviennent des tâches, comment les tâches se répartissent sur les threads et les instances, et ce qui plafonne le parallélisme d'une application |
| [0015](lessons/0015-rebalancing-restoration-and-standby-replicas.md) | Rebalancing, restauration et répliques standby | Ce qui arrive à l'état quand une tâche se déplace, et comment les répliques standby et warmup raccourcissent le temps pendant lequel il est indisponible |
| [0016](lessons/0016-testing-with-topologytestdriver.md) | Tester avec TopologyTestDriver | Comment tester la sortie, l'état et le comportement temporel d'une topologie dans un test unitaire sans broker |
| [0017](lessons/0017-operating-and-monitoring-a-streams-app.md) | Exploiter et surveiller une application Streams | Les métriques, les états et les gestionnaires d'exceptions qui vous disent si une application en cours d'exécution est en bonne santé, et que faire quand elle ne l'est pas |
| [0018](lessons/0018-when-kafka-streams-is-the-wrong-tool.md) | Quand Kafka Streams n'est pas le bon outil | Quand un simple consommateur, Flink ou ksqlDB convient mieux qu'une application Streams à une charge de travail, et comment défendre ce choix |
| [0019](lessons/0019-reviewing-someone-elses-topology.md) | Relire la topologie de quelqu'un d'autre | Comment relire une topologie Streams et nommer ce que coûte chaque choix en topics internes, en état et en exactitude |
| [0020](lessons/0020-changing-a-topology-others-depend-on.md) | Modifier une topologie dont d'autres dépendent | Comment modifier la topologie d'une application en cours d'exécution sans corrompre son état ni casser les consommateurs en aval, et comment trancher une affirmation contestée à partir de la source |

## Référence

- [Glossaire](GLOSSARY.md) : termes de référence pour ce sujet
- [Ressources](RESOURCES.md) : sources fiables, chacune annotée avec ce qu'elle couvre
- [Opérations du DSL](reference/dsl-operations.md) : chaque opération du DSL par type d'entrée et de sortie, si elle garde un état, et si elle repartitionne
- [State stores](reference/state-stores.md) : types de stores, paramètres du changelog, le cache d'enregistrements, et comment l'état est restauré
- [Temps et fenêtres](reference/time-and-windows.md) : les trois horloges, les quatre types de fenêtres, les périodes de grâce et quand chacune émet
- [Jointures](reference/joins.md) : la matrice des jointures, avec le fenêtrage, le co-partitionnement et ce qu'émet chaque jointure
- [Configuration](reference/configuration.md) : les paramètres qui décident des garanties, de la latence, du parallélisme et de la reprise, avec leurs valeurs par défaut
- [Exploitation](reference/operations.md) : les métriques à surveiller, les états du client et des threads, les gestionnaires d'exceptions et les outils d'exploitation
- [Revue de topologie](reference/topology-review.md) : une liste de contrôle pour relire une topologie, le choix de l'outil, et les modifications de topologie sûres et dangereuses

## Comment cela fonctionne

Chaque leçon est courte et autonome. Les corrigés sont repliés : rappelez-vous d'abord, puis ouvrez-les. Les exercices en situation réelle comptent plus que la lecture, et les espacer dans le temps est justement le but. Tout ce qui reste flou à la fin d'une leçon mérite d'être suivi jusqu'à sa source primaire avant de passer à la suite.
