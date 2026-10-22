---
title: "Quantification au moment du serving"
description: "Quantification des poids int8/int4/GPTQ/AWQ, pourquoi la mémoire, la vitesse et la précision n'évoluent pas ensemble, et un cadre de décision pour choisir un schéma"
type: reference
---

# Quantification au moment du serving

La quantification des poids comme levier de serving, indépendante de la précision du [KV cache](kv-cache.md). Conçu pour la consultation lors du choix ou de la défense d'un schéma.

## Schémas

| Schéma | Largeur de bits | Mécanisme | Précision à cette largeur |
|---|---|---|---|
| int8 | 8 | Arrondi au plus proche (round-to-nearest) | Généralement correcte en version naïve |
| int4, naïf | 4 | Arrondi au plus proche (round-to-nearest) | Se dégrade brutalement : seulement 16 valeurs représentables par poids, contre 256 pour int8 |
| GPTQ | 3-4 | Quantifie une colonne à la fois ; après chaque colonne, ajuste les poids restants, pas encore quantifiés, de cette couche pour compenser, en utilisant l'information de sensibilité de second ordre | Corrige l'erreur après coup, colonne par colonne |
| AWQ | 3-4 | Une passe de calibration trouve les canaux de poids qui voient les plus grandes magnitudes d'activation ; met ces canaux à l'échelle pour les protéger avant de quantifier quoi que ce soit | Protège avant coup les poids probablement sensibles |

GPTQ et AWQ visent le même résultat, un modèle précis avec des poids 4 bits, avec un calendrier opposé : GPTQ compense l'erreur déjà introduite ; AWQ la prévient dans les canaux que la calibration signale comme sensibles.

## La mémoire est l'axe prévisible ; la vitesse et la précision ne le sont pas

```text
memory ≈ fp16 footprint / (16 / bit_width)      # int8 halves it, int4 quarters it
```

**Exemple détaillé**, un modèle fp16 de 14 GB : int8 fait environ 7 GB, int4 environ 3.5 GB. Ce rapport tient quel que soit le schéma (naïf, GPTQ, AWQ) qui a produit les poids quantifiés, et quelle que soit la largeur de bits au-delà de cela.

La vitesse ne suit **pas** le rapport de mémoire :

- Un poids quantifié doit souvent être **déquantifié** vers une précision plus haute juste avant l'exécution de la multiplication matricielle, puisque le matériel de multiplication attend cette précision. Si cette étape de déquantification coûte du temps, l'accélération en temps réel reste en deçà du rapport de mémoire, à moins que le kernel de la pile de serving opère directement sur le format quantifié.
- Le decode (limité par la bande passante mémoire) est l'endroit où une empreinte de poids plus petite paie : moins à lire, moins de temps passé à le lire. Le prefill (limité par le calcul) passe son temps dans la multiplication matricielle elle-même, pas à lire des poids de façon répétée, si bien que la même quantification rapporte bien moins d'accélération au prefill, parfois presque aucune.

La précision demande un chiffre mesuré, et non une impression tirée d'exemples de sorties : la **perplexité** (la façon dont le modèle prédit un texte held-out ; plus elle est haute, pire c'est) par rapport au modèle non quantifié, ou un écart de score sur un benchmark propre à la tâche. Une sortie fluide n'est pas la preuve que la précision a tenu.

| Étape | Mémoire | Vitesse | Précision |
|---|---|---|---|
| fp16 vers int8 | Divisée par deux | Suit assez bien la mémoire | Coût faible, généralement tolérable |
| int8 vers int4 | De nouveau divisée par deux | Dépend du surcoût de déquantification et de la prise en charge par les kernels | Croît de façon disproportionnée par rapport à l'étape int8, ce qui explique l'existence de GPTQ/AWQ |

Aucun des trois axes n'évolue au même pas que les autres, c'est pourquoi un choix défendable a besoin d'un chiffre pour chacun.

<a id="picking-a-scheme-name-the-binding-constraint-first"></a>

## Choisir un schéma : nommer d'abord la contrainte qui lie

La quantification est un correctif pour une contrainte que fp16 ne satisfait pas, pas une étape par défaut. Si fp16 tient déjà dans le budget de mémoire et respecte le budget de latence, quantifier n'achète rien de nécessaire pour un coût réel en précision.

| Contrainte qui lie | Que faire |
|---|---|
| Mémoire : les poids plus la [capacité de KV cache](kv-cache.md#capacity-budget) requise ne tiennent pas | Quantifier juste assez pour tenir : int8 d'abord (coût de précision le plus faible), int4 avec GPTQ ou AWQ seulement si int8 seul ne laisse toujours pas de place |
| Latence : le modèle tient, mais le decode manque le budget | int8 ou int4 peuvent aider, puisque le decode est limité par la bande passante mémoire, mais il faut mesurer l'accélération réelle plutôt que la supposer à partir de la largeur de bits |
| Précision : un plafond de score de benchmark ou de perplexité ne peut pas être franchi | N'exclut pas la quantification, mais exclut de choisir un schéma sur la seule mémoire ou la seule vitesse : mesurer GPTQ contre AWQ pour ce modèle précis, puisqu'ils tiennent différemment d'un modèle à l'autre |

**Exemple détaillé** : les poids fp16 d'un modèle prennent 70 GB sur un GPU de 80 GB, ce qui laisse 10 GB pour le cache et le surcoût, trop peu pour une concurrence significative. C'est une contrainte de mémoire. Quantifier en int8 ramène les poids à ~35 GB, ce qui libère ~45 GB pour le cache, et relève sensiblement le [plafond de capacité](kv-cache.md#capacity-budget). Si int8 seul satisfait déjà les cibles de capacité et de latence, descendre encore à int4 achète de la mémoire dont personne n'a besoin pour un coût réel et mesuré en précision : quantifier au-delà de la contrainte qui lie est la même erreur que quantifier alors que fp16 tenait déjà.

<a id="defending-the-choice-means-citing-three-numbers"></a>

## Défendre le choix, c'est citer trois chiffres

1. **Le chiffre de mémoire** qui a rendu la quantification nécessaire, ou celui qui montre qu'elle ne l'était pas.
2. **Le chiffre de précision** mesuré pour le schéma choisi à la largeur de bits choisie : un écart de perplexité ou une variation de score de benchmark par rapport au modèle non quantifié.
3. **Le chiffre de vitesse** réellement mesuré pour la phase que couvre le budget (le decode, dans la plupart des cas limités par la latence), puisque le gain en temps réel ne suit pas automatiquement le rapport de mémoire.

Un choix défendu par un seul d'entre eux (« int4 avec AWQ donne les meilleures économies de mémoire ») n'est pas défendu : il laisse sans examen les deux autres axes, et la question de savoir si cette largeur de bits était même nécessaire.

## Voir aussi

- [Leçon 7](../lessons/0007-quantization-schemes.md), [Leçon 8](../lessons/0008-accuracy-speed-memory-tradeoffs.md), [Leçon 9](../lessons/0009-picking-a-quantization-scheme.md)
- [KV cache](kv-cache.md) : le plafond de capacité par rapport auquel se mesure une décision de quantification contrainte par la mémoire
