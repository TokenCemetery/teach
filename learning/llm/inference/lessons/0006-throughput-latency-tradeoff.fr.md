---
title: "6. Le compromis débit/latence"
description: "Comment la taille de batch échange le débit contre la latence par token, et comment défendre une configuration de batching face à un budget de latence annoncé"
type: lesson
---

# Leçon 6. Le compromis débit/latence

**Lien avec la mission :** C'est la synthèse de l'étape 2 : défendre une configuration de batching pour une charge de travail annoncée, c'est chiffrer le compromis débit/latence décrit aux leçons 4 et 5, face à un budget de latence et au plafond de capacité calculé à la leçon 2.
**Source primaire :** [Doc : vLLM Documentation, vLLM Project](https://docs.vllm.ai/en/latest/)
**Prérequis :** [Leçon 5](0005-request-scheduling.md), [Leçon 2](0002-capacity-and-batch-size.md), [KV cache](../GLOSSARY.md)

## Échauffement

1. ▢ Pourquoi regrouper les étapes de decode de plus de séquences augmente-t-il le débit sans augmentation proportionnelle du trafic mémoire ?

<details markdown="1"><summary>Vérifier</summary>

Le trafic mémoire d'une étape de decode, qui lit les poids et les KV caches présents, ne change presque pas selon qu'elle calcule le token suivant d'une séquence ou de plusieurs. Le batching répartit ce même trafic sur davantage de calcul utile.

</details>

2. ▢ Qu'est-ce que le plafond de capacité de la leçon 2, en une phrase ?

<details markdown="1"><summary>Vérifier</summary>

`(total memory − weights − overhead) / (bytes per token × context length)` : le nombre maximal de séquences concurrentes que permet le budget de KV cache, indépendamment de tout ce qui concerne la latence.

</details>

## À savoir

### Des batchs plus grands font deux choses à la fois, et elles tirent en sens opposés

Ajouter une séquence de plus à un batch augmente le débit : davantage de tokens sont produits par seconde, en agrégeant toutes les séquences de l'étape. Mais chaque séquence d'une étape de batch avance ensemble (leçon 5), donc empiler le travail de decode de plus de séquences dans une étape allonge aussi cette étape elle-même. Le délai entre les tokens successifs d'une séquence, sa latence inter-token, croît avec le batch qu'elle partage dans une étape. Le débit et la latence par token évoluent ensemble, et non l'un contre l'autre de façon indépendante : pousser l'un vers le haut pousse aussi l'autre vers le haut.

### La courbe a deux régimes

Aux petites tailles de batch, le decode est limité par la bande passante mémoire (leçon 4) : les mêmes lectures de poids et de cache dominent déjà le coût de l'étape, donc ajouter une séquence de plus est presque gratuit. Le débit croît à peu près linéairement avec la taille de batch tandis que la latence de l'étape bouge à peine. Au-delà d'une certaine taille de batch, il y a assez de travail empilé pour que le calcul brut du GPU, et non sa bande passante mémoire, devienne le goulot d'étranglement : la latence de l'étape commence à grimper sensiblement à chaque séquence ajoutée, et chaque séquence supplémentaire achète moins de débit additionnel que la précédente. Cette inflexion est la même distinction entre limité par la bande passante mémoire et limité par le calcul que la leçon 3 a tracée entre le prefill et le decode, qui se produit ici à l'intérieur du decode lui-même quand le batch grandit.

![Latence par token en fonction de la taille de batch : 15 ms à 8, 25 ms à 32, 45 ms à 64, 90 ms à 128. La courbe reste plate tant que le decode est limité par la bande passante mémoire, puis grimpe fortement quand le calcul devient le goulot d'étranglement. Un budget de latence de 30 ms, marqué par une ligne en pointillés, est franchi entre une taille de batch de 32 et de 64.](images/throughput-latency-tradeoff.svg)

### Défendre une configuration, c'est choisir un point sur cette courbe, pas le plus grand nombre disponible

Une charge de travail annoncée donne deux contraintes indépendantes, et la configuration qui mérite d'être défendue est la plus grande taille de batch qui satisfait les deux :

- **Un budget de latence** : un plafond annoncé de latence inter-token (par exemple, aucun token de sortie ne doit mettre plus d'un certain nombre de millisecondes à arriver).
- **Le plafond de capacité** : le maximum dérivé de la mémoire de la leçon 2, qui ne dit rien de la latence et tout de la question de savoir si le cache tient tout court.

Une taille de batch inférieure aux deux contraintes laisse sur la table du débit que le budget aurait pu s'offrir. Une taille de batch supérieure au budget de latence échange une violation de latence contre un débit que personne n'a demandé. Le chiffre défendu est le plus petit de ce que permet le budget et de ce que permet la capacité, et le raisonnement qui le fait choisir est la réponse à « pourquoi ce chiffre et pas un autre », ce qui est exactement ce que défendre une configuration veut dire.

## Pratique

1. ▢ Une pile de serving a été mesurée à quatre tailles de batch : 8 (15 ms/token), 32 (25 ms/token), 64 (45 ms/token), 128 (90 ms/token). Le budget de latence annoncé est de 30 ms/token. Laquelle de ces tailles de batch est la plus grande à satisfaire le budget ?

<details markdown="1"><summary>Vérifier</summary>

32, à 25 ms/token. 64 et 128 dépassent toutes deux le budget de 30 ms ; 32 est la plus grande des quatre qui reste en dessous.

</details>

2. ▢ Suite de la question 1 : le plafond de capacité de KV cache pour cette charge de travail, calculé comme à la leçon 2, vaut 100 séquences concurrentes. Quelle taille de batch faut-il réellement défendre, et quelle contrainte est celle qui lie ?

<details markdown="1"><summary>Indice</summary>

Le chiffre défendu est le plus petit de ce que chaque contrainte permet séparément.

</details>

<details markdown="1"><summary>Vérifier</summary>

Une taille de batch de 32. Le budget de latence est celui qui lie ici, puisque 32 est très inférieur au plafond de capacité de 100 séquences ; le cache a encore beaucoup de place, mais le budget de latence n'en a plus.

</details>

3. ▢ Supposons plutôt que le plafond de capacité soit tombé à 20 séquences, tout le reste de la question 1 étant inchangé. Quelle taille de batch faut-il maintenant défendre, et pourquoi ?

<details markdown="1"><summary>Vérifier</summary>

Une taille de batch de 20. C'est maintenant le plafond de capacité qui lie plutôt que le budget de latence : 32 satisferait le budget de 30 ms/token, mais le cache ne peut pas contenir autant de séquences concurrentes, donc la contrainte mémoire plafonne le nombre plus bas que la seule latence ne l'aurait fait.

</details>

4. ▢ Une équipe choisit une taille de batch de 8 pour la charge de travail de la question 1, bien en dessous à la fois du choix de 32 dicté par le budget de latence et du plafond de capacité de 100 séquences. Quel est le coût de ce choix ?

<details markdown="1"><summary>Vérifier</summary>

Du débit laissé sur la table. À 8, la latence de l'étape (15 ms/token) est bien sous le budget de 30 ms, ce qui signifie que le budget pourrait s'offrir un batch plus grand, et le cache a bien plus de place que ce qu'utilisent 8 séquences. Rien n'est violé, mais le serveur sert moins de requêtes concurrentes qu'il ne pourrait en défendre.

</details>

## Exercices en situation réelle

- [ ] Trouvez l'option de votre pile de serving pour la taille de batch maximale (vLLM : `--max-num-seqs`) et lisez ce que sa documentation dit sur son réglage face à une cible de latence.
- [ ] Si vous avez accès à un serveur en fonctionnement ou à ses benchmarks, tracez (ou trouvez) son débit et sa latence par token à quelques tailles de batch, et repérez à peu près où commence le régime limité par le calcul.
- [ ] Demain : choisissez un budget de latence que vous voudriez réellement défendre pour une charge de travail qui vous importe, et écrivez, en une phrase, pourquoi ce chiffre et pas un plus strict ou plus souple.

## Pour aller plus loin

- [Doc : vLLM Documentation, vLLM Project](https://docs.vllm.ai/en/latest/)
- [Billet : "How continuous batching enables 23x throughput in LLM inference while reducing p50 latency", Anyscale](https://www.anyscale.com/blog/continuous-batching-llm-inference)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
