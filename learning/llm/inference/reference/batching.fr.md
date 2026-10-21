---
title: "Batching"
description: "Batching statique contre continu, ordonnancement des requêtes, et le compromis débit/latence qu'une configuration doit défendre"
type: reference
---

# Batching

Comment un serveur transforme la capacité de [KV cache](kv-cache.md) en débit servi. Conçu pour la consultation lors du réglage ou de la défense d'une configuration de batching.

<a id="static-batching-wastes-capacity-on-uneven-finish-times"></a>

## Le batching statique gaspille de la capacité à cause des durées de fin inégales

Le trafic mémoire d'une étape de decode (lecture des poids et du cache de chaque séquence présente) ne change presque pas selon qu'elle calcule le token suivant d'une séquence ou de plusieurs à la fois, donc regrouper les étapes de decode est du débit presque gratuit. Le **batching statique** regroupe un ensemble fixe de requêtes et exécute des étapes de decode jusqu'à ce que la plus longue termine ; chaque séquence qui termine tôt occupe quand même une place, sans rien faire, jusqu'à la fin de tout le groupe.

```text
total slot-steps  = batch size × steps until the longest sequence finishes
useful slot-steps = sum of each request's actual length
wasted fraction   = (total − useful) / total
```

**Exemple détaillé**, quatre requêtes qui ont besoin de 10, 20, 30 et 100 tokens de sortie :

```text
total:  4 × 100 = 400 slot-steps
useful: 10 + 20 + 30 + 100 = 160 slot-steps
wasted: (400 − 160) / 400 = 60%
```

Le gaspillage croît avec l'écart entre les longueurs des requêtes, ce qui est le cas normal.

## Le continuous batching supprime la frontière du batch

Le **continuous batching** (ordonnancement au niveau de l'itération) ordonnance au niveau d'une seule étape de decode plutôt que d'un groupe fixe : dès qu'une séquence termine, sa place est libérée et une requête en attente est admise dès l'étape suivante. C'est la taille de batch, et non la durée de vie d'une requête quelconque, qui reste à peu près constante. Le gain n'est pas un calcul par étape plus rapide ; ce sont moins de slot-steps dépensés sur des séquences qui n'avaient plus rien à faire.

<a id="admission-order-and-head-of-line-blocking"></a>

## Ordre d'admission et head-of-line blocking

La politique d'admission par défaut est le **premier arrivé, premier servi (FCFS)** : simple, et équitable en ce sens qu'aucune requête n'attend derrière une requête arrivée plus tard. Mais toutes les séquences qui partagent une étape de batch avancent ensemble, donc admettre le travail de prefill d'une nouvelle requête dans l'étape suivante est acceptable quand le prompt est court et dommageable quand il est long : un gros prefill intégré à une étape domine la latence de cette étape, et chaque autre séquence, même celles qui n'avaient besoin que d'une étape de decode rapide, l'attend. C'est le **head-of-line blocking** : la file va bien, mais ce qui tourne maintenant, non. Le FCFS seul ne cause ni ne corrige cela ; il décide seulement de qui est admis, pas de la part de leur prefill qui atterrit dans une seule étape.

Le **chunked prefill** découpe le prefill d'un gros prompt en morceaux entrelacés avec les étapes de decode en cours du batch, de sorte que chaque étape n'admet qu'une quantité bornée de nouveau travail de prefill. Le prefill de la nouvelle requête prend plus d'étapes pour se terminer ; aucune autre séquence du batch n'est bloquée à l'attendre. La taille finale du cache d'un prompt entièrement traité est inchangée, seule change la façon dont le travail pour y arriver est réparti dans le temps.

<a id="the-throughputlatency-trade-off"></a>

## Le compromis débit/latence

Ajouter une séquence de plus à un batch augmente le débit (davantage de tokens produits par seconde, agrégés sur le batch) et augmente la latence par token (chaque séquence d'une étape avance ensemble, donc une étape plus grosse prend plus de temps). Les deux évoluent ensemble, et non l'un contre l'autre de façon indépendante.

| Régime | Goulot d'étranglement | Effet de l'ajout d'une séquence de plus |
|---|---|---|
| Petit batch | Limité par la bande passante mémoire, comme le decode simple | Le débit croît à peu près linéairement ; la latence bouge à peine |
| Grand batch | Limité par le calcul | La latence grimpe sensiblement ; chaque séquence ajoutée achète moins de débit que la précédente |

**Exemple détaillé**, une pile mesurée à quatre tailles de batch :

| Taille de batch | Latence par token |
|---|---|
| 8 | 15 ms |
| 32 | 25 ms |
| 64 | 45 ms |
| 128 | 90 ms |

<a id="defending-a-configuration"></a>

## Défendre une configuration

La taille de batch défendue est la plus grande qui satisfait les deux contraintes indépendantes, celle des deux qui lie le plus :

- **Un budget de latence** : un plafond annoncé de latence inter-token.
- **Le plafond de capacité** : [le maximum du KV cache dérivé de la mémoire](kv-cache.md#capacity-budget), qui ne dit rien de la latence.

```text
defended batch size = min(largest batch size within the latency budget,
                          capacity ceiling)
```

**Exemple détaillé**, budget de 30 ms/token, avec le tableau ci-dessus :

```text
largest batch within budget: 32 (25 ms/token); 64 and 128 exceed 30 ms

capacity ceiling 100 -> defended size 32, latency budget binds
capacity ceiling 20  -> defended size 20, capacity binds instead
```

Une taille de batch choisie bien en dessous des deux contraintes (disons 8 alors que 32 respecterait encore le budget) n'est pas fausse, mais elle laisse sur la table du débit que le budget aurait pu s'offrir.

## Voir aussi

- [Leçon 4](../lessons/0004-static-vs-continuous-batching.md), [Leçon 5](../lessons/0005-request-scheduling.md), [Leçon 6](../lessons/0006-throughput-latency-tradeoff.md)
- [KV cache](kv-cache.md) : le plafond de capacité dont dépend la formule de configuration défendue de cette fiche
