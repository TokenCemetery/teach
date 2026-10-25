---
title: Systèmes distribués
description: "Raisonner sur la défaillance partielle : ce qu'un réseau peut vous faire, quelle cohérence vous achetez réellement, et pourquoi le consensus coûte cher"
type: topic
---

# Apprentissage : les systèmes distribués

Savoir choisir et défendre un modèle de cohérence pour un système que vous concevez, et raisonner sur un incident de production causé par une défaillance partielle au lieu de traiter le réseau comme fiable.

**Dernière leçon :** [19. Vérifier une affirmation](lessons/0019-verifying-a-claim.md)

## Objectif

- Face à la conception d'un système, choisir un modèle de cohérence et défendre ce compromis face aux alternatives.
- Face à un incident causé par une défaillance partielle (une partition réseau, un nœud lent pris pour un nœud mort), nommer le mécanisme responsable.
- Expliquer ce qu'apporte un protocole de consensus et pourquoi il coûte ce qu'il coûte, sans avoir besoin de prouver sa correction à partir des premiers principes.

## Contraintes

- Suppose une expérience professionnelle de construction d'un service en réseau ; aucune étude formelle préalable des systèmes distribués n'est requise.
- Accent pratique et opérationnel : le coût et les compromis comptent davantage qu'une preuve formelle de la correction d'un protocole.

## Hors périmètre

- La concurrence au sein d'un seul processus (goroutines, threads, `Send`/`Sync`) : prise en charge par les parcours de langages. Ce parcours commence là où la frontière du processus est franchie.
- L'exécution de charges de travail sur un orchestrateur de cluster : prise en charge par [`infrastructure/kubernetes`](../../infrastructure/kubernetes/), qui enseigne ce que etcd et la réconciliation signifient en pratique et renvoie ici pour la théorie.
- Le traitement de flux au-dessus d'un log : pris en charge par [`data/stream-processing`](../../data/stream-processing/), qui enseigne ce que la reprise des state stores et le rebalancing changent pour une application Kafka Streams et renvoie ici pour la théorie.

## Le fil conducteur

Douze étapes, de la défaillance partielle à un incident diagnostiqué, puis aux mécanismes qu'utilisent réellement les systèmes de production pour y survivre, et à la façon de vérifier que tout cela tient vraiment. Une étape comprend plusieurs leçons et les frontières sont souples ; ce qui termine une étape, c'est la capacité acquise, pas le nombre de leçons.

| Étape | Leçons | Contenu | Terminée quand |
|---|---|---|---|
| 1. Défaillance partielle | 0001 | Le problème unique auquel répond chaque sujet ultérieur de ce parcours | Vous savez expliquer pourquoi un réseau ne peut pas être traité comme fiable |
| 2. Temps et ordre | 0002 à 0003 | Horloges, ordonnancement, pourquoi un timeout est le seul signal de défaillance disponible | Vous savez expliquer pourquoi un timeout ne peut pas distinguer un nœud lent d'un nœud mort |
| 3. Modèles de cohérence | 0004 à 0006 | CAP, linéarisabilité, cohérence séquentielle et cohérence à terme | Vous savez choisir et défendre un modèle de cohérence pour une conception donnée |
| 4. Consensus | 0007 à 0009 | Raft, élection du leader, ce qu'apporte le consensus et pourquoi il coûte ce qu'il coûte | Vous savez expliquer ce qu'apporte et ce que coûte un protocole de consensus sans prouver sa correction |
| 5. Diagnostiquer des incidents | 0010 | Appliquer les mécanismes ci-dessus à un vrai incident de production | Face à un incident causé par une défaillance partielle, vous savez nommer le mécanisme responsable |
| 6. Réplication et quorums | 0011 | Réplication avec leader contre sans leader, quorums de lecture et d'écriture, la condition `R + W > N` | Vous savez expliquer comment un quorum garantit qu'une lecture voit la dernière écriture, et choisir R et W pour une charge de travail donnée |
| 7. Partitionnement et sharding | 0012 | Hachage cohérent, nœuds virtuels, réplication des clés chaudes, routage des requêtes | Vous savez expliquer pourquoi le hachage cohérent borne le coût d'un redimensionnement, et ce qu'il manque encore à un anneau nu pour gérer les défaillances et les clés chaudes |
| 8. Résolution des conflits en cohérence à terme | 0013 | Last-write-wins et ce qu'il perd, vecteurs de versions, CRDT | Vous savez distinguer détecter un conflit et le résoudre, et expliquer comment un CRDT fusionne sans perte |
| 9. Transactions entre services | 0014 à 0015 | Le commit à deux phases et son mode de défaillance bloquant, les sagas et la compensation, le transactional outbox, les consommateurs idempotents | Vous savez expliquer pourquoi le 2PC bloque, ce qu'une saga sacrifie pour l'éviter, et comment le pattern outbox évite le problème de la double écriture |
| 10. La boîte à outils de résilience | 0016 à 0017 | Budgets de timeout, nouveaux essais avec backoff et jitter, tempêtes de nouveaux essais, circuit breakers, délestage de charge, backpressure | Vous savez expliquer quoi faire après le déclenchement d'un timeout, et associer une dépendance défaillante, un serveur surchargé ou une file qui se remplit au bon mécanisme |
| 11. Observabilité de la défaillance partielle | 0018 | Spans, traces, propagation à travers une frontière réseau, types de span | Vous savez expliquer comment une trace relie les spans d'une requête à travers les services, et pourquoi la propagation doit se faire explicitement à chaque saut |
| 12. Vérifier une affirmation | 0019 | Les tests en boîte opaque vérifiés par modèle de Jepsen, l'injection de fautes en production du chaos engineering, la reproductibilité de la simulation déterministe | Vous savez expliquer quel compromis fait chaque technique de vérification, et ce qu'un résultat de test donné prouve ou ne prouve pas |

## Leçons

Suivez-les dans l'ordre.

| # | Leçon | Enseigne |
|---|---|---|
| [0001](lessons/0001-partial-failure.md) | Défaillance partielle | Le problème unique auquel répond chaque sujet ultérieur de ce parcours |
| [0002](lessons/0002-clocks-and-ordering.md) | Horloges et ordonnancement | Pourquoi on ne peut pas se fier aux horodatages d'horloge murale de machines différentes pour ordonner des événements, et comment une horloge logique les ordonne sans avoir besoin d'un temps synchronisé |
| [0003](lessons/0003-timeouts-as-failure-detectors.md) | Les timeouts comme détecteurs de défaillance | Pourquoi tout détecteur de défaillance pratique repose sur un timeout, et le vocabulaire formel du compromis entre précision et rapidité qui en découle |
| [0004](lessons/0004-the-cap-theorem-precisely.md) | Le théorème CAP, précisément | Ce que CAP prouve réellement, pourquoi la tolérance aux partitions n'a jamais été optionnelle, et les contresens précis qui font de « en choisir deux » une mauvaise façon de l'énoncer |
| [0005](lessons/0005-linearizability.md) | Linéarisabilité | Ce que garantit réellement la linéarisabilité, pourquoi c'est le modèle de cohérence courant le plus fort, et ce qu'il coûte de la fournir pendant une partition |
| [0006](lessons/0006-sequential-and-eventual-consistency.md) | Cohérence séquentielle et cohérence à terme | Deux modèles plus faibles que la linéarisabilité, ce que chacun garantit encore, et comment choisir parmi les trois pour une conception donnée |
| [0007](lessons/0007-what-consensus-is-for.md) | À quoi sert le consensus | Le problème de la machine à états répliquée que résolvent les protocoles de consensus, et pourquoi c'est le mécanisme sous-jacent à la coordination d'un système linéarisable |
| [0008](lessons/0008-raft-leader-election-and-log-replication.md) | Raft, élection du leader et réplication du journal | Comment Raft élit un leader unique et réplique un journal par son intermédiaire, les deux mécanismes qui rendent concret le problème de la machine à états répliquée |
| [0009](lessons/0009-what-consensus-costs.md) | Ce que coûte le consensus | Pourquoi chaque écriture paie un aller-retour vers une majorité, pourquoi une partition minoritaire perd la disponibilité plutôt que la cohérence, et comment mettre ce coût en balance avec ce qu'apporte le consensus |
| [0010](lessons/0010-diagnosing-a-production-incident.md) | Diagnostiquer un incident de production | Appliquer la défaillance partielle, la détection de défaillance, les modèles de cohérence et le consensus pour nommer le mécanisme derrière un vrai incident, au lieu de raisonner sur « le réseau » ou « la cohérence » dans l'abstrait |
| [0011](lessons/0011-replication-and-quorums.md) | Réplication et quorums | Un protocole de consensus n'est pas la seule façon de répliquer des données, et la condition de quorum derrière son alternative moins coûteuse est une unique garantie de recouvrement, pas une vague notion d'accord majoritaire |
| [0012](lessons/0012-partitioning-and-sharding.md) | Partitionnement et sharding | Le hachage cohérent existe parce que le partitionnement naïf par hachage modulo N redistribue presque tout dès qu'un nœud arrive ou part, et même le hachage cohérent a besoin de nœuds virtuels avant de cesser de déverser toute la charge d'un nœud défaillant sur un seul voisin malchanceux |
| [0013](lessons/0013-conflict-resolution-under-eventual-consistency.md) | Résolution des conflits en cohérence à terme | Détecter que deux écritures étaient concurrentes et décider quoi en faire sont deux problèmes différents, et last-write-wins ne résout ni l'un ni l'autre : il choisit simplement un survivant et jette le perdant |
| [0014](lessons/0014-two-phase-commit-and-sagas.md) | Commit à deux phases et sagas | Le commit à deux phases ressemble au consensus (un coordinateur, un vote, un commit), mais il résout un problème différent et le paie plus cher, en bloquant indéfiniment si le coordinateur meurt en plein vote, ce qui est précisément pourquoi les systèmes de production se tournent plutôt vers les sagas |
| [0015](lessons/0015-the-transactional-outbox-and-idempotent-consumers.md) | Le transactional outbox et les consommateurs idempotents | Mettre à jour une base de données et publier un événement ne peuvent pas se faire atomiquement sans transaction distribuée, alors le pattern outbox contourne entièrement le problème en écrivant l'événement comme une ligne ordinaire dans la même transaction locale, et le paie avec un message susceptible d'être envoyé deux fois |
| [0016](lessons/0016-timeouts-retries-and-backoff.md) | Timeouts, nouveaux essais et backoff | La leçon 3 a établi qu'un timeout est le seul signal de défaillance disponible, mais en déclencher un et réessayer immédiatement est exactement ce qui transforme la mauvaise journée d'un service en cours de rétablissement en curée, le problème précis que le backoff et le jitter existent pour empêcher |
| [0017](lessons/0017-circuit-breakers-load-shedding-and-backpressure.md) | Circuit breakers, délestage de charge et backpressure | Un nouvel essai avec backoff et jitter suppose encore que l'appel défaillant vaut la peine d'être tenté, et le circuit breaker, le délestage de charge et la backpressure sont les trois réponses pour le moment où ce n'est plus le cas, visant respectivement une dépendance défaillante, un serveur surchargé et une file débordée |
| [0018](lessons/0018-distributed-tracing-and-correlation.md) | Traçage distribué et corrélation | Chaque mécanisme vu jusqu'ici dans ce parcours vous dit ce que fait un système en cas de défaillance, mais aucun ne vous dit quel saut d'une requête précise a réellement échoué, la seule chose à laquelle une trace est conçue pour répondre |
| [0019](lessons/0019-verifying-a-claim.md) | Vérifier une affirmation | Jepsen, le chaos engineering et la simulation déterministe cherchent tous à trouver un vrai bug avant un client, mais ils font des compromis opposés entre réalisme et reproductibilité pour y parvenir, et savoir lequel fait quoi est ce qui vous dit ce qu'un test donné a réellement prouvé |

## Référence

- [Glossaire](GLOSSARY.md) : termes de référence pour ce sujet
- [Ressources](RESOURCES.md) : sources fiables
- [Temps et ordre](reference/time-and-order.md) : ce que la relation happens-before peut et ne peut pas trancher, ce qu'une horloge de Lamport refuse de vous dire, et le vocabulaire des détecteurs de défaillance dont un timeout n'est qu'une instance
- [Modèles de cohérence](reference/consistency-models.md) : CAP énoncé tel qu'il a été prouvé, les modèles côte à côte avec ce que chacun garantit, et lesquels peuvent encore répondre pendant une partition
- [Consensus](reference/consensus.md) : le problème de la machine à états répliquée, les cinq propriétés de sûreté de Raft et les règles qui les produisent, et ce que coûte une majorité en écriture et en lecture
- [Diagnostiquer des incidents](reference/diagnosing-incidents.md) : quatre questions dans l'ordre, le vocabulaire des anomalies nommées pour décrire un symptôme avec précision, et une table symptôme vers mécanisme indexée sur les fiches ci-dessus

## Comment cela fonctionne

Chaque leçon est courte et autonome. Les corrigés sont repliés : rappelez-vous d'abord, puis ouvrez-les. Les exercices en situation réelle comptent plus que la lecture, et les espacer dans le temps est justement le but. Tout ce qui reste flou à la fin d'une leçon mérite d'être suivi jusqu'à sa source primaire avant de passer à la suite.
