---
title: "4. Batching statique et continu"
description: "Pourquoi regrouper des requêtes améliore le débit, et pourquoi le continuous batching bat le batching statique"
type: lesson
---

# Leçon 4. Batching statique et continu

**Lien avec la mission :** Le batching est le levier qui transforme la capacité de KV cache d'un serveur, ce que les leçons 1 à 3 ont appris à calculer, en débit réellement servi ; la qualité du batching d'un serveur décide quelle part de cette capacité va à du travail utile.
**Source primaire :** [Billet : "How continuous batching enables 23x throughput in LLM inference while reducing p50 latency", Anyscale](https://www.anyscale.com/blog/continuous-batching-llm-inference)
**Prérequis :** [Leçon 3](0003-growth-prefill-decode-precision.md), [KV cache](../GLOSSARY.md)

## Échauffement

1. ▢ Pourquoi le decode est-il limité par la bande passante mémoire plutôt que par le calcul ?

<details markdown="1"><summary>Vérifier</summary>

Chaque étape de decode relit tout le KV cache pour calculer l'attention dessus, afin de calculer un seul nouveau token. La quantité de nouveau calcul par étape est faible par rapport au trafic mémoire nécessaire pour lire le cache et les poids.

</details>

2. ▢ La leçon 3 a distingué le prefill du decode. Laquelle des deux traite un prompt entier en une seule passe avant ?

<details markdown="1"><summary>Vérifier</summary>

Le prefill. Le decode, lui, génère un token de sortie, et fait croître le cache de la taille d'un token, à chaque étape.

</details>

## À savoir

### Pourquoi regrouper les étapes de decode aide tout court

Le trafic mémoire d'une étape de decode, qui lit les poids du modèle et le KV cache de chaque séquence présente, ne change presque pas selon qu'elle calcule le token suivant d'une séquence ou ceux de plusieurs séquences à la fois. Regrouper en batch les étapes de decode de plusieurs séquences répartit ce même trafic mémoire sur davantage de calcul utile, ce qui est exactement le remède dont une étape limitée par la bande passante mémoire a besoin : plus de travail effectué par octet lu.

### Le batching statique gaspille ce gain à cause des durées de fin inégales

La façon évidente de faire du batching est de regrouper un ensemble fixe de requêtes, d'exécuter des étapes de decode jusqu'à ce que chacune ait terminé, puis de démarrer le groupe suivant. C'est le **batching statique**, et il a un défaut sérieux : le groupe ne peut pas se terminer avant sa séquence la plus longue. Chaque séquence qui termine tôt occupe quand même une place du batch, sans rien apporter, jusqu'à ce que tout le groupe soit terminé.

Prenons quatre requêtes regroupées, qui ont besoin respectivement de 10, 20, 30 et 100 tokens de sortie. Le batch tourne pendant 100 étapes, parce que c'est ce dont la séquence la plus longue a besoin. Sur ces 100 étapes, le batch consomme `4 × 100 = 400` slot-steps de travail GPU, mais seulement `10 + 20 + 30 + 100 = 160` de ces slot-steps ont servi à quelque chose. Les 240 autres ont été dépensés sur des séquences déjà terminées, inactives jusqu'à la frontière du batch. Cela fait 60 % de gaspillage, et cela empire à mesure que l'écart entre les longueurs des requêtes grandit, ce qui est le cas normal : les vraies requêtes varient énormément dans ce qu'elles génèrent.

### Le continuous batching supprime la frontière du batch

Le **continuous batching** (aussi appelé ordonnancement au niveau de l'itération) ordonnance au niveau d'une seule étape de decode plutôt que d'un groupe fixe. Dès qu'une séquence se termine, sa place est libérée et une nouvelle requête en attente est admise dans le batch dès l'étape suivante, au lieu d'attendre que toutes les autres séquences de son ancien groupe terminent aussi. La composition du batch change en continu ; c'est sa taille, et non la durée de vie d'une requête quelconque, qui reste à peu près constante.

Dans l'exemple des quatre requêtes, la séquence qui n'a besoin que de 10 tokens libère sa place à l'étape 10. Un ordonnanceur statique laisse cette place inactive pendant 90 étapes de plus. Un ordonnanceur continu y admet immédiatement une nouvelle requête, de sorte que le GPU continue de faire du travail utile dans cette place au lieu de traîner un poids mort jusqu'à une frontière arbitraire. C'est le mécanisme derrière les gains de débit que rapporte la source primaire de cette leçon : non pas un calcul par étape plus rapide, mais bien moins de chaque étape gaspillée sur des séquences qui n'avaient plus rien à faire.

![Deux places de batch sur 100 étapes de decode : la place A a besoin de 10 étapes, la place D de 100. Avec le batching statique, la place A termine à l'étape 10 et reste inactive pendant 90 étapes jusqu'à ce que tout le batch termine ensemble. Avec le continuous batching, une nouvelle requête est admise dans la place A dès qu'elle se libère, à l'étape 10, de sorte que la place continue de faire du travail utile.](images/static-vs-continuous-batching.svg)

## Pratique

1. ▢ Un batch statique contient deux requêtes qui ont besoin de 15 et 60 tokens de sortie. Combien de slot-steps au total le batch consomme-t-il, combien sont utiles, et quelle fraction est gaspillée ?

<details markdown="1"><summary>Indice</summary>

Le total des slot-steps est `batch size × steps until the longest sequence finishes`. Les slot-steps utiles sont la somme de la longueur réelle de chaque requête.

</details>

<details markdown="1"><summary>Vérifier</summary>

Total : `2 × 60 = 120` slot-steps. Utiles : `15 + 60 = 75`. Gaspillés : `120 − 75 = 45`, soit `45 / 120 = 37.5%`.

</details>

2. ▢ Dans un ordonnanceur de continuous batching, que se passe-t-il à l'étape exacte où une séquence du batch termine sa génération ?

<details markdown="1"><summary>Vérifier</summary>

Sa place est libérée immédiatement, et une nouvelle requête en attente est admise dans cette place à l'étape suivante, au lieu que la place reste inactive jusqu'à ce que toutes les autres séquences d'un groupe fixe terminent aussi.

</details>

3. ▢ Laquelle de ces affirmations est vraie à propos du continuous batching par rapport au batching statique ?

    - a) Il réduit le coût de calcul par étape de l'attention elle-même
    - b) Il supprime l'exigence de KV cache des séquences terminées avant de les évincer
    - c) Il garde le batch plein en admettant de nouvelles requêtes à mesure que des places se libèrent, au lieu d'attendre qu'un groupe fixe ait entièrement terminé
    - d) Il ne s'applique qu'aux piles de serving CPU comme llama.cpp

<details markdown="1"><summary>Vérifier</summary>

**c)** Il garde le batch plein en continu. (a) est fausse : l'arithmétique par étape est inchangée ; le gain, ce sont moins de slot-steps gaspillés. (b) est fausse et à l'envers : le cache d'une séquence terminée est libéré dans le cadre de son éviction, dans les deux styles d'ordonnancement. (d) est fausse : le continuous batching est une technique d'ordonnancement du serving GPU, surtout associée à vLLM et aux moteurs similaires.

</details>

4. ▢ Un batch statique de 8 requêtes a besoin d'exactement 50 tokens de sortie chacune. Le continuous batching améliorerait-il le débit par rapport au batching statique pour ce batch précis, et pourquoi ou pourquoi pas ?

<details markdown="1"><summary>Vérifier</summary>

À peine, voire pas du tout. Le gain du continuous batching vient du remplissage des places libérées par les requêtes qui terminent tôt pendant que d'autres continuent. Quand chaque requête du groupe a besoin d'exactement le même nombre de tokens, il n'y a aucune requête qui termine tôt et aucune place inactive à remplir, donc le batching statique ne gaspille déjà rien ici.

</details>

## Exercices en situation réelle

- [ ] Trouvez l'option ou le paramètre de configuration que la pile de serving de votre choix utilise pour activer le continuous batching (vLLM l'active par défaut ; regardez comment sa documentation nomme le mécanisme sous-jacent).
- [ ] Examinez un échantillon de trafic réel ou un journal de requêtes auquel vous avez accès (ou un jeu de données public de longueurs de requêtes LLM) et estimez l'écart entre la longueur de sortie la plus courte et la plus longue. Estimez la fraction de gaspillage du batching statique que cet écart causerait.
- [ ] Demain : lisez un paragraphe sur la façon dont un ordonnanceur de continuous batching décide quelle requête en attente admettre ensuite, et notez si c'est un simple ordre d'arrivée ou autre chose.

## Pour aller plus loin

- [Billet : "How continuous batching enables 23x throughput in LLM inference while reducing p50 latency", Anyscale](https://www.anyscale.com/blog/continuous-batching-llm-inference)
- [Doc : vLLM Documentation, vLLM Project](https://docs.vllm.ai/en/latest/)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
