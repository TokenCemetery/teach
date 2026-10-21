---
title: "5. Ordonnancement des requêtes"
description: "Comment un ordonnanceur de continuous batching choisit la requête suivante, et pourquoi un gros prefill peut bloquer tous les autres"
type: lesson
---

# Leçon 5. Ordonnancement des requêtes

**Lien avec la mission :** Le continuous batching, vu à la leçon 4, n'aide que si l'ordonnanceur qui y admet des requêtes ne crée pas lui-même un nouveau problème de latence ; c'est dans cette leçon que se trouve ce compromis.
**Source primaire :** [Doc : vLLM Documentation, vLLM Project](https://docs.vllm.ai/en/latest/)
**Prérequis :** [Leçon 4](0004-static-vs-continuous-batching.md), [KV cache](../GLOSSARY.md)

## Échauffement

1. ▢ Dans le continuous batching, que se passe-t-il à l'instant où une séquence du batch termine sa génération ?

<details markdown="1"><summary>Vérifier</summary>

Sa place est libérée immédiatement, et une nouvelle requête en attente y est admise à l'étape suivante, au lieu que la place reste inactive jusqu'à ce qu'un groupe fixe de requêtes termine tout entier.

</details>

2. ▢ Pourquoi le prefill est-il limité par le calcul alors que le decode est limité par la bande passante mémoire ?

<details markdown="1"><summary>Vérifier</summary>

Le prefill traite un prompt entier en une seule grande passe avant parallèle, il y a donc assez de travail par octet lu pour occuper le calcul du GPU. Le decode ne calcule qu'un seul nouveau token par étape, si bien que le trafic mémoire de chaque étape (lecture du cache et des poids) domine la faible quantité de nouveau calcul.

</details>

## À savoir

### Quelle requête en attente passe ensuite

Un ordonnanceur qui détient une file de requêtes en attente a besoin d'une politique pour décider laquelle admettre dans une place qui vient de se libérer. La valeur par défaut simple, et celle que vLLM utilise sans autre configuration, est le **premier arrivé, premier servi (FCFS)** : les requêtes sont admises dans l'ordre d'arrivée. Ce n'est pas la seule politique possible (un ordonnanceur pourrait donner la priorité selon la longueur attendue, ou selon un budget de latence annoncé), mais le FCFS est la bonne valeur par défaut à connaître d'abord : il est simple, il est équitable en ce sens qu'aucune requête n'attend derrière une requête arrivée plus tard, et toute politique plus élaborée est une variante du même mécanisme d'admission dans une place libérée que décrivait la leçon 4.

### Une étape de batch est atomique, et cela crée un nouveau problème

Toutes les séquences qui partagent une étape de batch avancent ensemble : la latence de toute l'étape est fixée par le travail le plus coûteux qu'elle contient. Admettre une nouvelle requête signifie que son travail de prefill doit avoir lieu quelque part, et l'endroit le plus direct est l'étape de batch suivante, à côté des étapes de decode dont les séquences déjà en cours ont besoin.

C'est acceptable quand le prompt de la nouvelle requête est court. Ça ne l'est pas quand il est long : un prefill de 6 000 tokens intégré à une étape domine désormais la latence de cette étape, et chaque autre séquence du batch, des séquences qui n'avaient besoin que d'une petite étape de decode rapide, attend qu'il se termine avant d'obtenir son token suivant. Une seule grosse admission bloque la progression de tous les autres. C'est un problème de **head-of-line blocking** : la file va bien, mais ce qui tourne maintenant, non.

### Le chunked prefill borne les dégâts

Le **chunked prefill** découpe le prefill d'un gros prompt en morceaux plus petits et entrelace chaque morceau avec les étapes de decode en cours du batch, au lieu d'exécuter tout le prefill en une seule étape. Chaque étape de batch n'admet alors qu'une quantité bornée de nouveau travail de prefill, ce qui tient dans le budget de latence de l'étape, au lieu de tout ce que le prompt d'une requête nouvellement admise contient. Le compromis est que le prefill de la nouvelle requête prend maintenant plusieurs étapes au lieu d'une, mais aucune autre séquence du batch n'est bloquée à l'attendre.

![En haut : sans découpage, tout le prefill d'un gros prompt est intégré à une seule étape, ce qui fait exploser sa latence bien au-delà des étapes de decode régulières de 20 ms pendant que toutes les autres séquences attendent. En bas : le chunked prefill découpe le prefill du même prompt en petits morceaux entrelacés avec le decode, ce qui garde chaque étape proche de 20 ms au prix d'un prefill de la nouvelle requête qui prend plus d'étapes pour se terminer.](images/chunked-prefill.svg)

## Pratique

1. ▢ Un continuous batch exécute des étapes régulières de decode seul d'environ 20 ms chacune. Un prompt de 6 000 tokens est admis et son prefill complet est intégré à l'étape suivante, sans découpage. Qu'arrive-t-il à la latence de cette étape, et qui en subit l'effet ?

<details markdown="1"><summary>Vérifier</summary>

Cette étape doit maintenant terminer le calcul de prefill des 6 000 tokens du prompt, en plus du travail de decode de chaque autre séquence du batch, parce que tout le batch avance ensemble en une seule étape. La latence de l'étape explose bien au-delà de 20 ms, et chaque autre séquence du batch, y compris celles qui n'avaient besoin que d'une étape de decode rapide, attend que cette étape se termine avant d'obtenir son token suivant.

</details>

2. ▢ Comment le chunked prefill évite-t-il le blocage décrit à la question 1 ?

<details markdown="1"><summary>Indice</summary>

Pensez à ce qui change par étape, pas à ce qui change dans la quantité totale de travail de prefill nécessaire.

</details>

<details markdown="1"><summary>Vérifier</summary>

Au lieu d'exécuter tout le prompt de la nouvelle requête en une seule étape, l'ordonnanceur découpe son prefill en morceaux plus petits et entrelace chaque morceau avec les étapes de decode habituelles du batch, en n'admettant qu'une quantité bornée de nouveau travail de prefill par étape. La latence d'une étape quelconque reste bornée ; le prefill de la nouvelle requête prend simplement plus d'étapes au total pour se terminer.

</details>

3. ▢ Laquelle de ces affirmations est vraie à propos du chunked prefill ?

    - a) Il supprime entièrement le prefill, en traitant chaque token comme une étape de decode
    - b) Il borne la latence ajoutée à une étape en découpant un gros prefill en morceaux
    - c) C'est une technique propre aux piles de serving CPU comme llama.cpp
    - d) Il réduit la quantité de KV cache dont un long prompt a besoin une fois entièrement traité

<details markdown="1"><summary>Vérifier</summary>

**b)** Il borne la latence ajoutée à une étape en découpant un gros prefill en morceaux entrelacés avec le decode. (a) est fausse : le prompt a toujours besoin d'un traitement de prefill complet, simplement réparti sur plus d'étapes. (c) est fausse : c'est une technique d'ordonnancement du continuous batching sur GPU. (d) est fausse : la taille finale du cache d'un prompt entièrement traité est inchangée ; le découpage ne change que la façon dont le travail pour y arriver est réparti dans le temps.

</details>

4. ▢ Une admission FCFS seule (sans découpage) aurait-elle évité le blocage de la question 1 ?

<details markdown="1"><summary>Vérifier</summary>

Non. Le FCFS décide seulement quelle requête en attente est admise ensuite ; il ne dit rien de la quantité de prefill de cette requête qui atterrit dans une seule étape une fois admise. Le blocage vient de l'intégration d'un gros prefill entier dans une seule étape de batch atomique, ce que règle le découpage, et non l'ordre d'admission.

</details>

## Exercices en situation réelle

- [ ] Trouvez l'option ou le paramètre de configuration de votre pile de serving pour le chunked prefill (vLLM : activé par défaut dans les versions récentes ; consultez sa documentation pour le réglage de la taille de morceau) et lisez quelle est la taille de morceau par défaut.
- [ ] Estimez, pour une charge de travail dont vous avez des données de longueur de requête, à quelle fréquence environ un prompt serait assez long pour bloquer sensiblement une étape de batch sans découpage.
- [ ] Demain : lisez un paragraphe sur la façon dont un ordonnanceur arbitre entre admettre le morceau de prefill d'une nouvelle requête et poursuivre celui d'une requête en cours, quand les deux se disputent le budget de la même étape.

## Pour aller plus loin

- [Doc : vLLM Documentation, vLLM Project](https://docs.vllm.ai/en/latest/)
- [Billet : "How continuous batching enables 23x throughput in LLM inference while reducing p50 latency", Anyscale](https://www.anyscale.com/blog/continuous-batching-llm-inference)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
