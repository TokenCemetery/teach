---
title: Postgres
description: "Exploiter Postgres : le WAL, le vacuum et le bloat, la réplication, et ce que coûte l'entretien d'un index"
type: topic
---

# Apprentissage : Postgres

Savoir exploiter une instance Postgres en fonctionnement, auto-hébergée ou managée, et diagnostiquer le bloat, le retard de réplication ou un basculement lent à se rétablir au lieu de deviner une correction, ainsi que concevoir dès le départ le stockage, la réplication et l'entretien des index d'un nouveau déploiement.

**Dernière leçon :** [18. Partitionnement et TOAST](lessons/0018-partitioning-and-toast.md)

## Objectif

- Face à une table gonflée ou à une réplique en retard, diagnostiquer la cause à partir des mécanismes du WAL, de l'autovacuum et de la réplication plutôt que par essais et erreurs.
- Concevoir le stockage, la topologie de réplication et la maintenance des index d'un nouveau déploiement, et défendre chaque choix.
- Expliquer ce dont un service managé (de type RDS) vous protège et ne vous protège pas, par rapport à l'exploitation de l'instance par vous-même.
- Rendre compte de ce que coûte à la base de données l'entretien d'un index vectoriel (pgvector), en lien avec le choix de pgvector comme stockage par `llm/rag`.

## Contraintes

- Suppose des bases en SQL (voir `programming/sql` pour le langage lui-même) ; aucune expérience préalable de l'administration de bases de données n'est requise.
- Couvre à la fois l'exploitation auto-hébergée et ce qui change avec un service managé.

## Hors périmètre

- Les requêtes, les plans de requête, la conception de schéma et la sémantique d'isolation : voir [`programming/sql`](../../programming/sql/), auquel on renvoie sans le répéter. Ce parcours prend en charge l'instance en fonctionnement, pas le langage.
- Les charges analytiques sur un entrepôt en colonnes, et quand il doit les reprendre à Postgres : voir [`data/warehouses`](../../data/warehouses/), dont l'étape de jugement tranche cette question.

## Le fil conducteur

Douze étapes, de la durabilité jusqu'à la maintenance au niveau des tables à grande échelle. Une étape comprend plusieurs leçons et les frontières sont souples ; ce qui termine une étape, c'est la capacité acquise, pas le nombre de leçons.

| Étape | Leçons | Contenu | Terminée quand |
|---|---|---|---|
| 1. Le write-ahead log | 0001 | Le mécanisme de durabilité sur lequel repose tout le reste de ce parcours | Vous savez expliquer comment le WAL rend un crash récupérable |
| 2. Vacuum et bloat | 0002 à 0003 | Fonctionnement interne de l'autovacuum, MVCC et tuples morts, diagnostic et réglage du bloat | Vous savez diagnostiquer une table gonflée à partir des mécanismes du vacuum et du WAL |
| 3. Réplication | 0004 à 0006 | Réplication en streaming, slots de réplication, basculement, diagnostic du retard | Vous savez diagnostiquer une réplique en retard et concevoir une topologie de réplication |
| 4. Les index et leur coût d'entretien | 0007 à 0008 | Coût de maintenance des B-tree/GiST/GIN, ce que coûte l'entretien d'un index pgvector | Vous savez concevoir un plan de maintenance des index et rendre compte du coût de pgvector |
| 5. Managé ou auto-hébergé | 0009 à 0010 | Ce dont un service managé de type RDS vous protège, et ce dont il ne vous protège pas | Vous savez expliquer la frontière du service managé et défendre un choix d'exploitation |
| 6. Sauvegarde et restauration à un instant donné | 0011 | Sauvegardes de base, archivage continu du WAL, `recovery_target_time`, et pourquoi une restauration non testée n'est pas une sauvegarde vérifiée | Vous savez concevoir et défendre une stratégie de sauvegarde qui reconstruit réellement une base de données fonctionnelle lorsqu'on la teste |
| 7. Configuration et réglage de la mémoire | 0012 | `shared_buffers`, `work_mem`, `maintenance_work_mem`, réglage des checkpoints | Vous savez dimensionner ces paramètres d'après la concurrence réelle plutôt que d'après un test isolé sur une seule requête |
| 8. Surveillance | 0013 | `pg_stat_activity`, wait events, `pg_stat_statements`, le journal du serveur | Vous savez choisir la bonne surface de surveillance (état en direct des backends, coût agrégé des requêtes ou événement journalisé) pour un symptôme donné |
| 9. Gestion des connexions | 0014 | `max_connections`, le coût d'un processus par connexion, les modes de pooling session/transaction/statement de PgBouncer | Vous savez choisir un mode de pooling qui correspond à ce dont l'application dépend réellement, plutôt que de prendre par défaut le plus efficace |
| 10. Réplication logique et mises à niveau de version majeure | 0015 à 0016 | Publications et souscriptions, la restriction de la réplication logique sur le DDL, les modes de transfert de `pg_upgrade`, la voie de mise à niveau par réplication logique avec peu d'interruption | Vous savez choisir et défendre une voie de mise à niveau (`pg_upgrade` sur place ou bascule par réplication logique) pour un budget d'interruption donné |
| 11. Rôles, privilèges et row-level security | 0017 | Les rôles face à la séparation utilisateur/groupe d'autres systèmes, les options INHERIT/SET de l'appartenance, les GRANT au niveau des tables, la row-level security et son contournement par défaut pour le propriétaire | Vous savez concevoir une organisation des rôles et des politiques RLS, et dire pourquoi activer RLS seul ne restreint pas le propriétaire de la table |
| 12. Partitionnement et TOAST | 0018 | Partitionnement par plage/liste/hachage, élagage des partitions, suppression en masse sans bloat, TOAST et ses quatre stratégies de stockage | Vous savez concevoir une disposition de partitions pour une gestion du cycle de vie sans bloat, et rendre compte de la stratégie de stockage d'une grande colonne |

## Leçons

Suivez-les dans l'ordre.

| # | Leçon | Enseigne |
|---|---|---|
| [0001](lessons/0001-the-write-ahead-log.md) | Le write-ahead log | Le mécanisme de durabilité sur lequel repose tout le reste de ce parcours |
| [0002](lessons/0002-mvcc-and-dead-tuples.md) | MVCC et tuples morts | Pourquoi un UPDATE ou un DELETE ne supprime jamais rien immédiatement, et pourquoi cela laisse des tuples morts que le vacuum doit nettoyer |
| [0003](lessons/0003-bloat-diagnosis-and-autovacuum-tuning.md) | Diagnostic du bloat et réglage de l'autovacuum | Comment mesurer le bloat, pourquoi l'autovacuum prend du retard, et l'ordre de diagnostic qui trouve la vraie cause au lieu de deviner |
| [0004](lessons/0004-streaming-replication-and-slots.md) | Réplication en streaming et slots de réplication | Comment un standby se connecte réellement et rattrape son retard, et ce qu'un slot de réplication garantit que le streaming seul ne garantit pas |
| [0005](lessons/0005-failover-mechanics.md) | Mécanique du basculement | Ce qui se passe quand un standby est promu, pourquoi un ancien primaire ne peut pas simplement revenir, et le compromis sur la perte de données que borne la réplication synchrone |
| [0006](lessons/0006-diagnosing-replication-lag.md) | Diagnostiquer le retard de réplication | Pourquoi le retard de réception et le retard d'application sont des mesures différentes, et l'ordre de diagnostic qui trouve lequel se produit réellement |
| [0007](lessons/0007-index-maintenance-cost.md) | Coût de maintenance des B-Tree, GiST et GIN | Pourquoi chaque index rend les écritures plus coûteuses, et comment B-tree, GiST et GIN paient chacun ce coût différemment |
| [0008](lessons/0008-what-a-pgvector-index-costs.md) | Ce que coûte l'entretien d'un index pgvector | Le coût en disque, en temps de construction et en mémoire permanente qu'un index vectoriel ajoute au-delà des vecteurs bruts qu'il indexe |
| [0009](lessons/0009-what-managed-shields-you-from.md) | Ce dont un service managé vous protège | Ce que l'automatisation de type RDS supprime réellement, et pourquoi tout ce que couvrent les leçons précédentes doit encore être compris en dessous |
| [0010](lessons/0010-defending-an-operating-choice.md) | Défendre un choix d'exploitation | Une conception de déploiement détaillée qui cite une décision et un coût précis de chaque étape, plutôt que de supposer une réponse par défaut |
| [0011](lessons/0011-backup-and-point-in-time-recovery.md) | Sauvegarde et restauration à un instant donné | Une sauvegarde de base et une archive continue du WAL permettent ensemble de reconstruire n'importe quel moment depuis la sauvegarde, et pas seulement le moment où elle a été prise, et une restauration non testée n'est pas une sauvegarde vérifiée |
| [0012](lessons/0012-configuration-and-memory-tuning.md) | Configuration et réglage de la mémoire | shared_buffers, work_mem et maintenance_work_mem répondent chacun à une question de mémoire différente, et celui qui est le plus souvent mal réglé est celui qui se multiplie discrètement par le nombre d'opérations qui tournent réellement en même temps |
| [0013](lessons/0013-monitoring-activity-statements-and-the-log.md) | Surveillance : activité, requêtes et journal | Une vue en direct de ce que fait chaque backend en ce moment, une vue agrégée de ce qui coûte réellement le plus au serveur dans la durée, et un journal qui nomme exactement ce qui bloque une requête coincée, sont trois questions différentes |
| [0014](lessons/0014-connection-management-and-pgbouncer.md) | Gestion des connexions et PgBouncer | Chaque connexion Postgres est un processus complet du système d'exploitation, c'est pourquoi un pooler est généralement nécessaire, et les trois modes de pooling de PgBouncer échangent chacun différemment la correction au niveau de la session contre l'efficacité de la réutilisation |
| [0015](lessons/0015-logical-replication-publications-and-subscriptions.md) | Réplication logique, publications et souscriptions | La réplication en streaming expédie le WAL brut pour construire une copie identique de tout le cluster ; la réplication logique décode ces mêmes modifications en événements au niveau des lignes qu'un abonné peut appliquer de façon sélective, d'une version majeure à l'autre, au prix de ne jamais répliquer le DDL d'elle-même |
| [0016](lessons/0016-major-version-upgrades-and-pg-upgrade.md) | Mises à niveau de version majeure et pg_upgrade | Les modes de transfert les plus rapides de pg_upgrade achètent leur vitesse en renonçant à la possibilité de simplement revenir en arrière, et la réplication logique offre un compromis réellement différent, une interruption quasi nulle, au prix d'une gestion manuelle du DDL tout au long de la migration |
| [0017](lessons/0017-roles-privileges-and-row-level-security.md) | Rôles, privilèges et row-level security | Les GRANT au niveau des tables et la row-level security sont deux couches d'autorisation distinctes, et activer RLS ne restreint pas le propriétaire de la table à moins de le lui demander explicitement |
| [0018](lessons/0018-partitioning-and-toast.md) | Partitionnement et TOAST | Le partitionnement transforme un parcours complet de la table en un parcours des seules partitions pertinentes et rend la suppression en masse sans bloat, tandis que TOAST est la raison pour laquelle une seule ligne peut contenir une valeur bien plus grande qu'une page de 8 ko |

## Référence

- [Glossaire](GLOSSARY.md) : termes de référence pour ce sujet
- [Ressources](RESOURCES.md) : sources fiables
- [Vacuum et bloat](reference/vacuum-and-bloat.md) : ce qui déclenche l'autovacuum et avec quels chiffres, ce qui retient l'espace qu'il peut récupérer, et les vues à consulter dans quel ordre
- [Réplication](reference/replication.md) : ce qu'un slot garantit et ce qu'il risque, les cinq niveaux synchrones et quand trois d'entre eux ne font rien, et les deux retards avec les colonnes qui les distinguent
- [Maintenance des index](reference/index-maintenance.md) : ce que chaque type d'index facture par écriture et ce qui le dégrade, et les paramètres et la falaise mémoire qu'un index pgvector apporte avec lui
- [Managé ou auto-hébergé](reference/managed-vs-self-hosted.md) : ce qu'un service managé automatise et ce qu'il ne fait que déplacer, les trois formes de haute disponibilité qui ne sont pas interchangeables, et les décisions qu'une conception défendue doit nommer

## Comment cela fonctionne

Chaque leçon est courte et autonome. Les corrigés sont repliés : rappelez-vous d'abord, puis ouvrez-les. Les exercices en situation réelle comptent plus que la lecture, et les espacer dans le temps est justement le but. Tout ce qui reste flou à la fin d'une leçon mérite d'être suivi jusqu'à sa source primaire avant de passer à la suite.
