---
title: "vLLM"
description: "Mettre en place vLLM, les options qui portent les concepts des étapes 1 à 3, la table de blocs de PagedAttention, et une procédure de décision du symptôme au paramètre"
type: reference
---

# vLLM

La pile de serving GPU. Conçu pour la consultation lors de la mise en place ou du réglage d'un serveur.

## Mettre en place un serveur

```bash
pip install vllm
vllm serve meta-llama/Llama-2-7b-hf
```

Démarre un serveur HTTP compatible OpenAI sur le port 8000. Une requête ressemble à n'importe quel appel de chat completion OpenAI :

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "meta-llama/Llama-2-7b-hf", "messages": [{"role": "user", "content": "Say hello"}]}'
```

Le champ `"model"` de la requête doit correspondre au modèle avec lequel le serveur a été démarré.

## Les options qui portent l'arithmétique des étapes 1 à 3

| Option | Porte |
|---|---|
| `--max-num-seqs` | Le plafond de taille de batch [défendu face à un budget de latence](batching.md#defending-a-configuration) |
| `--kv-cache-dtype` | La [précision du cache](kv-cache.md#cache-precision-is-a-lever-independent-of-the-models-own-weights), par exemple `fp8`, indépendante de la précision des poids du modèle |
| `--quantization` | Le schéma (`gptq`, `awq`, ...) [choisi et défendu](quantization-at-serve-time.md) pour un checkpoint déjà quantifié |

Le continuous batching et le chunked prefill sont activés par défaut ; il n'y a pas d'option pour désactiver le mécanisme de base, seulement pour le régler (comme la taille de morceau). Omettre `--quantization` sert le checkpoint dans la précision où il a été enregistré, le plus souvent fp16 ou bf16 ; rien n'est quantifié au chargement.

<a id="pagedattention"></a>

## PagedAttention

Le cache de chaque séquence est découpé en **blocs** de taille fixe (16 tokens par défaut) ; une **table de blocs** propre à chaque séquence fait correspondre les positions logiques de tokens à des emplacements physiques de blocs, la même idée qu'une table de pages d'OS.

**La taille de bloc est un compromis :**

| Taille de bloc | Espace gaspillé dans le dernier bloc, partiellement rempli | Comptabilité de la table de blocs |
|---|---|---|
| Plus grande | Plus | Moins |
| Plus petite | Moins | Plus |

**Exemple détaillé** : une séquence de 40 tokens avec une taille de bloc de 16 tokens utilise `ceil(40/16) = 3` blocs ; le troisième contient 8 tokens et gaspille les 8 autres emplacements.

**Partage de blocs** : les tables de blocs de deux séquences peuvent pointer vers le même bloc physique quand le contenu est identique, le plus souvent un préfixe de prompt partagé. L'échantillonnage parallèle et la beam search en sont les cas les plus clairs : la table de chaque échantillon pointe vers les mêmes blocs de prompt jusqu'à ce que le propre token généré d'un échantillon diverge, moment où un **copy-on-write** ne donne qu'à cet échantillon une copie privée du bloc modifié.

**Exemple détaillé**, 10 échantillons parallèles du même prompt de 200 tokens, blocs de 16 tokens : une copie demande `ceil(200/16) = 13` blocs. Sans partage : `13 × 10 = 130` blocs. Avec partage : 13 blocs, jusqu'à ce qu'un échantillon commence à diverger.

## Deux paramètres de réglage de plus

| Option | Ce qu'elle contrôle | Compromis |
|---|---|---|
| `--gpu-memory-utilization` | Fraction de la mémoire d'un GPU que vLLM peut utiliser pour les poids, le cache et son propre surcoût (par défaut ~0.9) | La relever vers 1.0 augmente le plafond de capacité du cache mais laisse moins de marge pour tout ce qui partage le GPU |
| `--tensor-parallel-size` | Répartit les poids et le calcul d'un modèle entre plusieurs GPU | Étale le modèle au lieu de le réduire (aucun coût de précision, contrairement à la quantification) ; combinable avec la quantification quand aucune des deux ne suffit seule |

`--gpu-memory-utilization` change le sens de « mémoire totale » dans [la formule du plafond de capacité](kv-cache.md#capacity-budget) : sur un GPU de 80 GB à la valeur par défaut de ~0.9, seuls ~72 GB, et non 80 GB, sont ce que la formule doit utiliser.

## Du symptôme au paramètre

| Symptôme | À vérifier |
|---|---|
| Ne démarre pas, ou signale trop peu de mémoire pour le cache | `--gpu-memory-utilization` d'abord ; si cela ne tient toujours pas à 100 %, c'est [le cas contraint par la mémoire](quantization-at-serve-time.md#picking-a-scheme-name-the-binding-constraint-first) : quantifier, ajouter `--tensor-parallel-size`, ou les deux |
| Decode plus lent que le budget de latence | `--max-num-seqs` par rapport à [la taille de batch défendue](batching.md#the-throughputlatency-trade-off), puis si quantifier les poids ou `--kv-cache-dtype` est justifié par des chiffres mesurés |
| Une requête bloque les tokens de toutes les autres séquences | [Head-of-line blocking](batching.md#admission-order-and-head-of-line-blocking) : vérifier la taille de morceau du chunked prefill, pas la taille de batch |
| La mémoire semble gaspillée sur des échantillons parallèles du même prompt | Le partage de blocs ci-dessus : vérifier qu'il a bien lieu avant de toucher à la taille de batch ou à l'utilisation de la mémoire |

## Voir aussi

- [Leçon 10](../lessons/0010-standing-up-vllm.md), [Leçon 11](../lessons/0011-pagedattention.md), [Leçon 12](../lessons/0012-vllm-tuning-knobs.md)
- [KV cache](kv-cache.md), [Batching](batching.md), [Quantification au moment du serving](quantization-at-serve-time.md) : les concepts que portent ces options
