---
title: Redis
description: "Utiliser Redis pour ce qu'il est : le modèle mémoire, l'éviction, la persistance, et les usages qui le détournent sans bruit"
type: topic
---

# Apprentissage : Redis

Savoir repérer où un système existant détourne Redis sans bruit, par exemple un cache traité comme un stockage ou un verrou qui n'en est pas un, et concevoir à la place un usage correct dès le départ.

**Dernière leçon :** [17. ACL et protected mode](lessons/0017-acls-and-protected-mode.md)

## Objectif

- Face à l'usage de Redis par un système existant, déterminer s'il traite un cache comme un stockage durable, implémente un verrou de façon incorrecte ou laisse grandir un keyspace sans limite, et dire ce qui casse à cause de cela.
- Concevoir dès le départ un usage correct de Redis (keyspace borné, politique d'éviction adaptée, vrai verrou distribué) pour un nouveau cas d'usage.
- Comparer les garanties de persistance de Redis (RDB/AOF) à la durabilité adossée au WAL de Postgres, et dire quand recourir à Redis plutôt qu'à une base de données est le bon choix ou un anti-pattern.
- Raisonner sur Redis Cluster/Sentinel au niveau des compromis qu'introduit le clustering, sans avoir besoin d'en exploiter un.

## Contraintes

- Ne suppose aucune expérience préalable de Redis.

## Hors périmètre

- L'exploitation d'une instance Postgres en production : voir [`data/postgres`](../../data/postgres/), auquel on renvoie pour la comparaison sans le répéter.

## Le fil conducteur

Dix étapes, de l'éviction jusqu'au contrôle d'accès. Une étape comprend plusieurs leçons et les frontières sont souples ; ce qui termine une étape, c'est la capacité acquise, pas le nombre de leçons.

| Étape | Leçons | Contenu | Terminée quand |
|---|---|---|---|
| 1. Mémoire et éviction | 0001 | Pourquoi Redis évince des clés, et l'anti-pattern qui découle de l'oubli de ce fait | Vous savez expliquer l'effet d'une politique d'éviction sur une charge de travail donnée |
| 2. Persistance | 0002 à 0003 | RDB et AOF, et comment leur durabilité se compare au WAL de Postgres | Vous savez dire quand recourir à Redis plutôt qu'à une base de données est le bon choix ou un anti-pattern |
| 3. Verrous distribués | 0004 à 0005 | Erreurs de verrouillage naïves, Redlock, la critique de Kleppmann | Vous savez concevoir, ou rejeter à bon escient, un verrou distribué fondé sur Redis |
| 4. Anti-patterns cache contre stockage | 0006 à 0007 | Cache-aside, un cache traité comme un stockage durable, un keyspace non borné | Face à un système existant, vous savez identifier le mauvais usage et dire ce qui casse |
| 5. Clustering | 0008 | Redis Cluster et Sentinel, les compromis qu'introduit le clustering | Vous savez raisonner sur les compromis du clustering sans avoir besoin d'en exploiter un |
| 6. Types de données et leur modèle de coût | 0009 à 0010 | Strings, hashes, lists, sets, sorted sets, bitmaps, HyperLogLog, et comment choisir entre eux | Vous savez choisir une structure de données pour un cas d'usage donné et expliquer ce qu'elle coûte |
| 7. Messagerie et expiration | 0011 à 0012 | Pub/Sub contre streams, consumer groups comparés à ceux de Kafka, expiration des clés paresseuse contre active | Vous savez choisir le bon mécanisme de messagerie pour un cas d'usage et expliquer comment une clé quitte réellement Redis |
| 8. Transactions et scripts | 0013 à 0014 | `MULTI`/`EXEC`, verrouillage optimiste avec `WATCH`, scripts Lua, Redis Functions | Vous savez construire une séquence vérifier-puis-agir réellement sûre, et expliquer ce qui rend atomique la libération d'un verrou |
| 9. Performance et exploitation | 0015 à 0016 | Coût des allers-retours, pipelining, pool de connexions, `INFO`/`SLOWLOG`/latency monitor/`MEMORY USAGE`, `SCAN` contre `KEYS` | Vous savez réduire le coût réseau d'un client bavard et diagnostiquer le comportement réel d'une instance sans la geler |
| 10. Contrôle d'accès | 0017 | Protected mode, ACL, catégories de commandes, l'utilisateur par défaut | Vous savez restreindre ce que peuvent faire respectivement une connexion non authentifiée et un utilisateur authentifié |

## Leçons

Suivez-les dans l'ordre.

| # | Leçon | Enseigne |
|---|---|---|
| [0001](lessons/0001-memory-and-eviction.md) | Mémoire et éviction | Pourquoi Redis évince des clés, et l'anti-pattern qui découle de l'oubli de ce fait |
| [0002](lessons/0002-rdb-snapshotting.md) | Snapshots RDB | Ce que capture réellement un snapshot RDB, et la fenêtre de perte de données que son intervalle de sauvegarde laisse ouverte |
| [0003](lessons/0003-aof-and-wal-comparison.md) | AOF et la comparaison avec le WAL | Comment la politique de fsync d'AOF fixe sa fenêtre de perte de données, et pourquoi même le réglage courant le plus strict de Redis sacrifie davantage de durabilité à la vitesse que Postgres par défaut |
| [0004](lessons/0004-naive-locking-mistakes.md) | Erreurs de verrouillage naïves | Pourquoi SET NX PX seul n'est pas un verrou distribué, et les deux modes de défaillance qui le cassent en conditions réelles |
| [0005](lessons/0005-redlock-and-kleppmanns-critique.md) | Redlock et la critique de Kleppmann | Ce que Redlock corrige réellement par rapport au verrou naïf, ce que la critique de Kleppmann montre qu'il ne corrige toujours pas, et comment décider si un verrou Redis est seulement le bon outil |
| [0006](lessons/0006-cache-aside-and-the-store-anti-pattern.md) | Cache-aside et l'anti-pattern du stockage | À quoi ressemble un usage correct du cache-aside, et la façon précise dont un cache devient sans bruit le système de référence quand ce schéma est ignoré |
| [0007](lessons/0007-unbounded-keyspace-and-spotting-misuse.md) | L'anti-pattern du keyspace non borné et le repérage des mauvais usages | Comment un keyspace grandit sans limite quand personne ne lui fixe de TTL ni de politique d'éviction, et une liste de contrôle pour repérer cela et l'anti-pattern du stockage dans un système existant |
| [0008](lessons/0008-cluster-and-sentinel.md) | Redis Cluster et Sentinel | Les compromis qu'introduisent respectivement le sharding de Redis Cluster et le basculement automatique de Sentinel, analysés sans avoir besoin d'exploiter l'un ou l'autre |
| [0009](lessons/0009-strings-hashes-and-lists.md) | Strings, hashes et lists | Les trois structures de données fondamentales que Redis stocke réellement, et ce que chacune coûte en lecture, en écriture et en croissance |
| [0010](lessons/0010-sets-sorted-sets-and-probabilistic-structures.md) | Sets, sorted sets et structures probabilistes | Choisir une structure de données pour un cas d'usage, de l'appartenance exacte jusqu'à un comptage approximatif qui ne coûte presque rien à conserver |
| [0011](lessons/0011-streams-and-pubsub-as-messaging.md) | Streams et Pub/Sub comme surface de messagerie | Deux façons dont Redis fait circuler des messages entre clients, et pourquoi une seule d'entre elles est sûre pour bâtir une file |
| [0012](lessons/0012-key-expiration-lazy-vs-active.md) | Expiration des clés : paresseuse contre active | Pourquoi le TTL d'une clé qui atteint zéro ne la retire pas à lui seul de la mémoire, et les deux mécanismes qui finissent par le faire |
| [0013](lessons/0013-multi-exec-and-optimistic-locking-with-watch.md) | MULTI/EXEC et verrouillage optimiste avec WATCH | Mettre plusieurs commandes en file pour qu'elles s'exécutent sans interruption, et détecter qu'une valeur a changé dans votre dos avant d'agir dessus |
| [0014](lessons/0014-lua-scripting-and-redis-functions.md) | Scripts Lua et Redis Functions | Le mécanisme qui rend réellement sûre la libération d'un verrou, en exécutant une vérification et une action en une seule étape atomique |
| [0015](lessons/0015-pipelining-round-trip-cost-and-connection-pooling.md) | Pipelining, coût des allers-retours et pool de connexions | Pourquoi N commandes séquentielles coûtent N allers-retours réseau alors que chacune s'exécute en quelques microsecondes, et les deux corrections distinctes |
| [0016](lessons/0016-operational-visibility.md) | Visibilité opérationnelle | Les outils qui montrent ce que fait réellement une instance Redis, et la commande qui a provoqué plus de pannes que presque n'importe quelle autre |
| [0017](lessons/0017-acls-and-protected-mode.md) | ACL et protected mode | Comment Redis empêche une instance non authentifiée d'être joignable tout court, et délimite ce qu'un client authentifié a réellement le droit de faire |

## Référence

- [Glossaire](GLOSSARY.md) : termes de référence pour ce sujet
- [Ressources](RESOURCES.md) : sources fiables
- [Persistance](reference/persistence.md) : ce que promettent respectivement RDB et AOF, la fenêtre de perte exacte que laisse chaque politique de fsync, et ce que dit la documentation de Redis elle-même sur l'égalisation de la durabilité d'une base de données
- [Verrous distribués](reference/distributed-locks.md) : le verrou naïf et ses deux failles, l'algorithme de Redlock avec l'arithmétique de validité, et la seule question qui décide si l'un ou l'autre est le bon outil
- [Anti-patterns cache contre stockage](reference/cache-vs-store-anti-patterns.md) : le cache-aside bien fait, les deux façons dont un cache cesse d'en être un, et les paramètres d'éviction qui décident de la défaillance que vous obtenez
- [Clustering](reference/clustering.md) : ce que les slots de Cluster vous retirent, les paramètres qui décident si un cluster dégradé continue de servir ou s'arrête, et pourquoi le quorum de Sentinel ne contrôle pas le basculement

## Comment cela fonctionne

Chaque leçon est courte et autonome. Les corrigés sont repliés : rappelez-vous d'abord, puis ouvrez-les. Les exercices en situation réelle comptent plus que la lecture, et les espacer dans le temps est justement le but. Tout ce qui reste flou à la fin d'une leçon mérite d'être suivi jusqu'à sa source primaire avant de passer à la suite.
