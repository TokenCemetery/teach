---
title: "3. Croissance, prefill, decode et précision"
description: "Comment le cache croît pendant le prefill et le decode, et ce que rachète une précision plus basse"
type: lesson
---

# Leçon 3. Croissance, prefill, decode et précision

**Lien avec la mission :** Un budget de latence dépend du moment où la mémoire du cache est réclamée au cours d'une requête, et pas seulement de sa taille finale, ainsi que des autres leviers dont un serveur dispose sur cette taille en dehors de la taille de batch et de la longueur de contexte.
**Source primaire :** [Doc : vLLM Documentation, vLLM Project](https://docs.vllm.ai/en/latest/)
**Prérequis :** [Leçon 2](0002-capacity-and-batch-size.md), [KV cache](../GLOSSARY.md)

## Échauffement

1. ▢ Écrivez la formule de l'empreinte totale du KV cache d'un batch, en fonction des octets par token, de la longueur de contexte et de la taille de batch.

<details markdown="1"><summary>Vérifier</summary>

`total cache bytes = bytes per token × context length × batch size`.

</details>

2. ▢ Pourquoi un modèle qui utilise la grouped-query attention a-t-il un KV cache plus petit que le même modèle en attention multi-têtes complète ?

<details markdown="1"><summary>Vérifier</summary>

Le cache contient une paire clé/valeur par tête KV, et non par tête de requête, et la GQA utilise moins de têtes KV que de têtes de requête. Le cache évolue avec `num_kv_heads`, que la MHA complète fixe égal à `num_heads`.

</details>

## À savoir

### Le cache ne croît pas à un rythme régulier

Une requête comporte deux phases, qui réclament la mémoire du cache de façons très différentes.

Le **prefill** traite tout le prompt en une seule passe avant : les vecteurs de clés et de valeurs de chaque token du prompt sont calculés et mis en cache ensemble, en une seule étape. Le cache passe de vide à `bytes per token × prompt length` avant même que le modèle n'ait généré un seul token de sortie. Cette phase est limitée par le calcul : c'est une seule grande multiplication matricielle parallèle sur tout le prompt.

Le **decode** génère ensuite un token de sortie à la fois. Chaque étape calcule et met en cache les clés et les valeurs d'un seul token de plus, si bien que le cache croît de `bytes per token` par étape, un mince filet en comparaison. Cette phase est limitée par la bande passante mémoire : chaque étape doit relire tout le cache pour calculer l'attention dessus, pour le travail nouveau d'un seul token.

Un long prompt réclame donc l'essentiel de l'empreinte de cache finale d'une requête immédiatement, au prefill, tandis que le decode ajoute le reste progressivement. Un plan de capacité qui ne regarde que la « longueur de contexte finale » demande en réalité « quelle taille cela atteindra-t-il après le prefill plus le nombre d'étapes de decode que j'attends », et les deux phases contribuent selon des calendriers très différents.

![Un graphique de la taille du cache au fil du temps : le cache fait un bond presque vertical pendant l'unique étape de prefill, puis monte en un escalier lent et régulier pendant le decode, chaque token de sortie ajoutant la taille d'un token de cache. Un prompt de 2048 tokens réclame environ 640 MB au prefill, tandis que 128 étapes de decode n'ajoutent qu'environ 40 MB de plus, soit 6 % du total.](images/prefill-decode-cache-growth.svg)

### Un levier indépendant des poids du modèle : la précision du cache

La formule de la leçon 2 portait `bytes_per_value` comme un terme à part, distinct de `num_layers`, `num_kv_heads` et `head_dim`. Ce terme n'a pas à correspondre à la précision dans laquelle le modèle calcule. Une pile de serving peut stocker le KV cache lui-même dans une précision plus basse, couramment fp8, pendant que le modèle calcule toujours en bf16 ou en fp16. Passer `bytes_per_value` de 2 octets à 1 divise l'empreinte du cache par deux d'emblée, sans rien changer à `num_kv_heads`, sans rien changer à la longueur de contexte, et sans réentraînement : c'est un choix au moment du serving, indépendant de la précision à laquelle les poids ont été quantifiés.

Cela se cumule avec tout ce qui précède de la leçon 2. Reprenons les chiffres de Llama-2-70B (80 couches, 8 têtes KV, `head_dim` = 128) : en fp16, le coût par token était de 320 KB. En fp8, il est de `2 × 80 × 8 × 128 × 1 byte = 163,840 bytes ≈ 160 KB`, exactement la moitié, parce que seul `bytes_per_value` a changé.

## Pratique

1. ▢ Une requête a un prompt de 2048 tokens. Avec le chiffre fp16 de Llama-2-70B de 320 KB par token, quelle quantité de cache le prefill réclame-t-il à lui seul, avant qu'aucun token de sortie ne soit généré ?

<details markdown="1"><summary>Vérifier</summary>

`320 KB × 2048 ≈ 640 MB`, réclamés en l'unique étape de prefill.

</details>

2. ▢ Cette même requête génère ensuite 128 tokens de sortie par le decode. Quelle quantité de cache supplémentaire le decode ajoute-t-il, et quelle fraction du cache final total de la requête cela représente-t-il ?

<details markdown="1"><summary>Indice</summary>

Le decode ajoute `bytes per token × number of decode steps`. Comparez cela au chiffre du prefill de la question 1.

</details>

<details markdown="1"><summary>Vérifier</summary>

`320 KB × 128 ≈ 40 MB` ajoutés par le decode. Le cache total est de `640 MB + 40 MB = 680 MB`, donc le decode n'en représente qu'environ 6 % ; le prefill a réclamé les 94 % restants en une seule étape.

</details>

3. ▢ Avec le chiffre de cache fp8 de Llama-2-70B de 160 KB par token, calculez l'empreinte totale du cache pour un batch de 64 séquences avec un contexte de 4096 tokens.

<details markdown="1"><summary>Indice</summary>

`total cache bytes = bytes per token × context length × batch size`, la même formule que dans l'échauffement.

</details>

<details markdown="1"><summary>Vérifier</summary>

`160 KB × 4096 × 64 = 41,943,040 KB ≈ 40 GB`.

</details>

4. ▢ La version fp16 de ce même batch (question 3, mais à 320 KB par token) coûterait combien de cache, et que montre la comparaison sur le fait d'empiler un changement de précision sur un changement de partage de têtes ?

<details markdown="1"><summary>Vérifier</summary>

`320 KB × 4096 × 64 ≈ 80 GB`, exactement le double. Le cache fp8 divise l'empreinte par deux en plus de ce que la GQA avait déjà rachetée par rapport à la MHA complète : les deux leviers sont indépendants et se multiplient au lieu de se substituer l'un à l'autre.

</details>

## Exercices en situation réelle

- [ ] Trouvez l'option de votre pile de serving pour le type de données du KV cache (vLLM : `--kv-cache-dtype`) et lisez quelles précisions elle prend en charge et ce qu'elle signale sur la précision.
- [ ] Pour une forme de requête que vous attendez réellement (longueur de prompt, longueur de sortie attendue), calculez quelle part de son cache final le prefill réclame par rapport au decode, avec le chiffre réel par token d'un modèle.
- [ ] Demain : lisez un paragraphe de la documentation de vLLM sur le chunked prefill et notez en une phrase pourquoi découper le prefill en morceaux change le calendrier de réclamation de mémoire décrit dans cette leçon.

## Pour aller plus loin

- [Doc : vLLM Documentation, vLLM Project](https://docs.vllm.ai/en/latest/)
- [Billet : "Transformer Inference Arithmetic", Kipply](https://kipp.ly/transformer-inference-arithmetic/)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
