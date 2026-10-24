---
title: Kafka
description: "Maîtriser le log : partitions, consumer groups, garanties de livraison, et ce que coûte réellement « exactly once »"
type: topic
---

# Apprentissage : Kafka

Savoir concevoir la disposition des topics et des partitions pour une vraie charge de travail, et diagnostiquer un retard des consommateurs, des tempêtes de rebalancing ou une perte de messages inattendue au lieu de deviner une correction.

**Dernière leçon :** [16. Les métriques qui comptent pour exploiter un cluster](lessons/0016-the-metrics-that-matter-for-operating-a-cluster.md)

## Objectif

- Concevoir la disposition des topics, des partitions et des consumer groups pour une charge de travail donnée, et défendre le choix de garantie de livraison qui la sous-tend.
- Face à un consommateur en retard ou qui se rééquilibre sans cesse, diagnostiquer quel paramètre ou quel schéma d'utilisation est en cause.
- Dire ce que coûte réellement « exactly once » et quand l'at-least-once avec un traitement idempotent est le meilleur compromis.

## Contraintes

- Ne suppose aucune expérience préalable de Kafka ni des systèmes de messagerie.
- Apache Kafka est l'implémentation de référence ; les alternatives (Redpanda, services managés) ne sont pas couvertes.
- Aborde brièvement l'écosystème environnant (Schema Registry, bases de Kafka Connect), là où les garanties du log seules n'expliquent pas comment se construit un vrai pipeline.

## Hors périmètre

- Le modèle de défaillance derrière les garanties de livraison elles-mêmes : voir [`architecture/distributed-systems`](../../architecture/distributed-systems/), auquel on renvoie sans le redériver ici.
- ksqlDB et Kafka Streams en tant que sujets à part entière.

## Le fil conducteur

Dix étapes, du log jusqu'à l'exploitation du cluster en production. Une étape comprend plusieurs leçons et les frontières sont souples ; ce qui termine une étape, c'est la capacité acquise, pas le nombre de leçons.

| Étape | Leçons | Contenu | Terminée quand |
|---|---|---|---|
| 1. Les partitions et le log | 0001 | L'unité autour de laquelle tout le reste (ordre, parallélisme, consumer groups) est construit | Vous savez expliquer pourquoi une partition est l'unité d'ordre et de parallélisme |
| 2. Consumer groups et rebalancing | 0002 à 0003 | Coordination des groupes, rebalancing coopératif, retard des consommateurs | Vous savez diagnostiquer un consommateur en retard ou qui se rééquilibre sans cesse |
| 3. Garanties de livraison | 0004 à 0005 | Sémantiques at-most-once, at-least-once et exactly-once, producteurs idempotents, transactions | Vous savez défendre un choix de garantie de livraison et dire ce que coûte l'exactly-once |
| 4. Concevoir la disposition | 0006 à 0007 | Choix de la clé, compromis sur le nombre de partitions, garanties d'ordre | Vous savez concevoir la disposition des topics et des partitions pour une charge de travail donnée |
| 5. L'écosystème environnant | 0008 à 0009 | Schema Registry, bases de Kafka Connect | Vous savez expliquer comment ils s'articulent autour du log dans un vrai pipeline |
| 6. Rétention et réplication | 0010 à 0011 | `cleanup.policy`, compaction du log, facteur de réplication, ISR, `acks`, `min.insync.replicas`, unclean leader election | Vous savez défendre la durée de vie des données d'un topic et la durabilité que ses paramètres de réplication garantissent réellement |
| 7. Configuration des clients sous charge | 0012 | `batch.size`, `linger.ms`, `fetch.min.bytes`, `max.poll.interval.ms` | Vous savez associer un symptôme de débit, de latence ou de rebalancing intempestif au paramètre client précis qui le traite |
| 8. Coordination du cluster | 0013 | KRaft, le quorum de contrôleurs, `process.roles`, ce qui a remplacé ZooKeeper | Vous savez expliquer ce que fait le quorum de contrôleurs et pourquoi un basculement KRaft n'exige pas de recharger toutes les métadonnées |
| 9. Sécurité et multi-tenancy | 0014 à 0015 | TLS, SASL, `security.protocol`, ACL, refus par défaut, quotas | Vous savez nommer quel mécanisme (chiffrement, authentification, autorisation ou isolation des ressources) concerne réellement une question de sécurité donnée |
| 10. Exploiter le cluster | 0016 | `UnderReplicatedPartitions`, `UnderMinIsr`, marge disque, latence des requêtes, saturation des request handlers | Vous savez nommer à laquelle des trois familles de signaux appartient un symptôme opérationnel donné, et trier entre broker isolé et problème à l'échelle du cluster |

## Leçons

Suivez-les dans l'ordre.

| # | Leçon | Enseigne |
|---|---|---|
| [0001](lessons/0001-partitions-and-the-log.md) | Les partitions et le log | L'unité autour de laquelle tout le reste de ce parcours (ordre, parallélisme, consumer groups) est construit |
| [0002](lessons/0002-consumer-group-coordination.md) | Coordination des consumer groups | Comment un group coordinator et un group leader répartissent les partitions entre les consommateurs, et comment les offsets suivent la progression de chaque groupe |
| [0003](lessons/0003-cooperative-rebalancing-and-lag.md) | Rebalancing coopératif et diagnostic du retard des consommateurs | Pourquoi le protocole de rebalancing d'origine provoque une tempête de rebalancing, comment le rebalancing coopératif la circonscrit, et un ordre de diagnostic pour le retard des consommateurs |
| [0004](lessons/0004-delivery-semantics.md) | At-most-once, at-least-once et exactly-once | Où chaque garantie de livraison se gagne ou se perd réellement sur les segments production, broker et consommation du chemin |
| [0005](lessons/0005-idempotent-producers-and-transactions.md) | Producteurs idempotents et transactions | Pourquoi l'idempotence est presque gratuite alors que les transactions portent le vrai coût de l'exactly-once |
| [0006](lessons/0006-partition-key-choice.md) | Choix de la clé de partition et garanties d'ordre | Choisir une clé de partition, c'est choisir à la fois l'ordre que vous obtenez et le parallélisme auquel vous renoncez, dans une seule et même décision |
| [0007](lessons/0007-partition-count-and-topic-layout.md) | Compromis sur le nombre de partitions et conception de la disposition d'un topic | Pourquoi davantage de partitions n'est pas gratuit, et ce qu'une disposition de topic pleinement défendue doit nommer de chaque étape précédente |
| [0008](lessons/0008-schema-registry.md) | Schema Registry | Comment détecter une modification de schéma incompatible au moment de la production remplace une casse silencieuse en aval, au moment de la consommation |
| [0009](lessons/0009-kafka-connect-basics.md) | Bases de Kafka Connect | Comment les tâches et les modes de worker de Connect apportent parallélisme et tolérance aux pannes, et pourquoi Connect n'accorde aucune garantie que l'API producteur ou consommateur sous-jacente ne fournissait pas déjà |
| [0010](lessons/0010-retention-and-log-compaction.md) | Rétention et compaction du log | Combien de temps un message survit réellement dans un topic, et l'autre politique de nettoyage qui conserve l'historique d'une clé plutôt que son âge |
| [0011](lessons/0011-replication-isr-acks-and-unclean-leader-election.md) | Réplication, ISR, acks et unclean leader election | Ce qu'attend réellement acks=all, le plancher qui l'empêche de signifier silencieusement moins que ce qu'il annonce, et le compromis lorsque toutes les répliques in-sync ont disparu |
| [0012](lessons/0012-producer-and-consumer-configuration-under-load.md) | Configuration du producteur et du consommateur sous charge | Les réglages côté client qui échangent de la latence contre du débit, et celui qui peut déclencher un rebalancing pour un consommateur qui n'a jamais été réellement mort |
| [0013](lessons/0013-kraft-and-what-replaced-zookeeper.md) | KRaft, et ce qui a remplacé ZooKeeper | Comment le cluster s'accorde sur ses propres métadonnées maintenant que le service de coordination externe a disparu, et pourquoi le rechargement complet de l'état lors d'un basculement était le problème qui valait la peine d'être résolu |
| [0014](lessons/0014-tls-and-sasl-authenticating-to-a-cluster.md) | TLS et SASL : s'authentifier auprès d'un cluster | Chiffrer le canal et authentifier le client sont deux tâches distinctes que security.protocol combine en un seul paramètre, et les confondre est l'origine de la plupart des malentendus |
| [0015](lessons/0015-acls-and-quotas-authorization-and-multi-tenancy.md) | ACL et quotas : autorisation et multi-tenancy | Un principal authentifié n'est encore autorisé à rien tant qu'une ACL ne le dit pas, et un principal autorisé à agir n'est toujours pas empêché d'affamer tous les autres tenants en capacité du cluster |
| [0016](lessons/0016-the-metrics-that-matter-for-operating-a-cluster.md) | Les métriques qui comptent pour exploiter un cluster | Les partitions sous-répliquées, la marge disque et la latence des requêtes sont les trois signaux à surveiller, et chacun pointe vers un type de problème différent |

## Référence

- [Glossaire](GLOSSARY.md) : termes de référence pour ce sujet
- [Ressources](RESOURCES.md) : sources fiables
- [Consumer groups et rebalancing](reference/consumer-groups-and-rebalancing.md) : les deux protocoles de rebalancing, les deux timeouts de vivacité indépendants, et un ordre de diagnostic pour le retard des consommateurs avec la configuration qui gouverne chaque étape
- [Garanties de livraison](reference/delivery-guarantees.md) : quelle configuration décide de chaque segment du chemin, pourquoi l'idempotence peut être désactivée en silence, et ce qu'attend réellement un consommateur read_committed
- [Conception des topics et des partitions](reference/topic-and-partition-design.md) : comment un enregistrement atteint réellement une partition, quel ordre cela garantit ou non, et les deux sens dans lesquels le nombre de partitions coûte cher à modifier
- [Écosystème](reference/ecosystem.md) : les sept types de compatibilité avec, pour chacun, qui doit mettre à jour en premier, et ce que Kafka Connect ajoute autour du log, y compris la garantie désactivée par défaut

## Comment cela fonctionne

Chaque leçon est courte et autonome. Les corrigés sont repliés : rappelez-vous d'abord, puis ouvrez-les. Les exercices en situation réelle comptent plus que la lecture, et les espacer dans le temps est justement le but. Tout ce qui reste flou à la fin d'une leçon mérite d'être suivi jusqu'à sa source primaire avant de passer à la suite.
