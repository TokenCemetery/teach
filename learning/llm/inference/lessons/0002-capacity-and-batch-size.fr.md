---
title: "2. Capacité et taille de batch"
description: "Comment le partage de têtes (GQA/MQA) et la taille de batch changent l'empreinte réelle du cache"
type: lesson
---

# Leçon 2. Capacité et taille de batch

**Lien avec la mission :** Un budget de latence se défend en termes du nombre de requêtes concurrentes qu'un serveur peut garder, et ce nombre découle directement du calcul de cache que cette leçon prolonge.
**Source primaire :** [Billet : "Transformer Inference Arithmetic", Kipply](https://kipp.ly/transformer-inference-arithmetic/)
**Prérequis :** [Leçon 1](0001-the-kv-cache.md), [KV cache](../GLOSSARY.md)

## Échauffement

1. ▢ En une phrase, que permet le KV cache à un serveur de ne pas faire à chaque token généré après le premier ?

<details markdown="1"><summary>Vérifier</summary>

Recalculer les vecteurs de clés et de valeurs de chaque token précédent de la séquence, à chaque couche.

</details>

2. ▢ Qu'est-ce qui n'allait pas dans une allocation de cache naïve, contiguë et dimensionnée à la longueur maximale, et qu'a changé PagedAttention ?

<details markdown="1"><summary>Vérifier</summary>

Elle réservait de la mémoire pour la longueur maximale qu'une séquence pouvait atteindre, la gaspillant en fragmentation interne et externe. PagedAttention alloue plutôt le cache en blocs non contigus de taille fixe, adressés par une table propre à chaque séquence.

</details>

## À savoir

### La plupart des modèles ne mettent pas en cache une clé et une valeur par tête

La formule de la leçon 1, `2 × num_layers × d_model × 2 bytes` par token, suppose que chaque tête d'attention garde ses propres vecteurs de clés et de valeurs. C'est l'**attention multi-têtes (MHA)**. La plupart des modèles servis aujourd'hui utilisent la **grouped-query attention (GQA)** ou son cas extrême, la **multi-query attention (MQA)** : de nombreuses têtes de requête partagent un nombre beaucoup plus petit de têtes clé/valeur. Le cache ne contient jamais qu'une paire K/V par *tête KV*, et non par tête de requête, si bien que la formule devient :

```text
bytes per token = 2 (K and V) × num_layers × num_kv_heads × head_dim × bytes_per_value
```

où `head_dim = d_model / num_heads`, et où c'est `num_kv_heads` qui compte désormais, pas le nombre total de têtes. Quand `num_kv_heads = num_heads`, cela se réduit exactement à la formule de la leçon 1 (la MHA est le cas particulier de la GQA). Quand `num_kv_heads` est beaucoup plus petit, le cache rétrécit de ce même rapport, gratuitement, sans rien changer à la longueur de contexte ni à la taille de batch.

![Trois lignes : la MHA a 8 têtes de requête, chacune associée à sa propre tête KV ; la GQA a des groupes de têtes de requête qui partagent l'une de 2 têtes KV (un quart du cache) ; la MQA a les 8 têtes de requête qui partagent une seule tête KV (un huitième du cache). Le nombre de têtes de requête n'apparaît jamais dans la formule du cache ; seul le nombre de têtes KV y figure.](images/mha-gqa-mqa-head-sharing.svg)

Llama-2-70B est un cas concret : 80 couches, 64 têtes de requête, mais seulement 8 têtes KV, `head_dim` = 128. En fp16 :

```text
per token = 2 × 80 × 8 × 128 × 2 bytes = 327,680 bytes ≈ 320 KB
```

S'il avait utilisé la MHA complète (64 têtes KV au lieu de 8), les mêmes couches et le même `head_dim` donnent `2 × 80 × 64 × 128 × 2 = 2,621,440 bytes ≈ 2.5 MB` par token, huit fois plus, exactement le rapport entre `num_heads` et `num_kv_heads`. La GQA est autant une décision de coût de serving qu'une décision de modélisation.

### Faire passer le coût par token à l'empreinte totale d'un batch

Un serveur garde rarement une seule séquence. L'empreinte totale du cache à un instant donné est le coût par token, multiplié par la longueur qu'a atteinte chaque séquence, multiplié par le nombre de séquences présentes ensemble :

```text
total cache bytes = bytes per token × context length × batch size
```

Pour Llama-2-70B avec un contexte de 4096 tokens, une séquence coûte `320 KB × 4096 ≈ 1.25 GB`. Trente-deux séquences concurrentes à cette même longueur coûtent `1.25 GB × 32 = 40 GB`, avant même que les poids du modèle ne prennent la moindre place.

### En faire un budget de capacité

C'est le nombre dont une décision de serving a réellement besoin : étant donné un pool de mémoire, combien de séquences concurrentes tiennent ? Soustrayez les poids et le surcoût du framework de la mémoire totale disponible, puis divisez ce qui reste par le coût de cache par séquence à la longueur de contexte que vous prévoyez de prendre en charge :

```text
max concurrent sequences = (total memory − weights − overhead) / (bytes per token × context length)
```

Prenons un pool de 320 GB (quatre GPU de 80 GB, en parallélisme tensoriel) qui sert Llama-2-70B, avec des poids et un surcoût du framework mesurés à 160 GB. Il reste 160 GB pour le cache. Avec le chiffre ci-dessus de 4096 tokens et 1.25 GB par séquence : `160 GB / 1.25 GB ≈ 128` séquences concurrentes. C'est ce plafond, et non le débit brut du modèle, contre lequel un ordonnanceur de batching négocie le plus souvent, et c'est là que la leçon 4 prend le relais.

## Pratique

1. ▢ Un modèle utilise la GQA avec `num_kv_heads` égal au quart de `num_heads`. Par rapport au même modèle en MHA complète, de combien son KV cache par token est-il plus petit ?

<details markdown="1"><summary>Vérifier</summary>

D'un quart de la taille. Le cache contient une paire K/V par tête KV, et non par tête de requête, donc le coût par token évolue avec `num_kv_heads` seul ; tout le reste de la formule est inchangé.

</details>

2. ▢ Un modèle a 48 couches, 40 têtes de requête, 8 têtes KV, `head_dim` = 128, servi en fp16. Calculez la taille de son KV cache par token.

<details markdown="1"><summary>Indice</summary>

Utilisez `2 × num_layers × num_kv_heads × head_dim × bytes_per_value`. Le nombre de têtes de requête n'apparaît pas du tout dans la formule.

</details>

<details markdown="1"><summary>Vérifier</summary>

`2 × 48 × 8 × 128 × 2 = 196,608 bytes ≈ 192 KB` par token.

</details>

3. ▢ Avec le modèle à 192 KB par token de la question 2, calculez l'empreinte totale du cache pour un batch de 16 séquences avec un contexte de 2048 tokens.

<details markdown="1"><summary>Indice</summary>

`total cache bytes = bytes per token × context length × batch size`.

</details>

<details markdown="1"><summary>Vérifier</summary>

Par séquence : `192 KB × 2048 ≈ 384 MB`. Pour 16 séquences : `384 MB × 16 = 6,144 MB ≈ 6 GB`.

</details>

4. ▢ Un serveur a 96 GB de mémoire. Les poids et le surcoût du framework en prennent 40 GB. Le cache de chaque séquence coûte 384 MB à la longueur de contexte que ce serveur prend en charge. Quel est le nombre maximal de séquences concurrentes que permet le budget de cache ?

<details markdown="1"><summary>Vérifier</summary>

`(96 GB − 40 GB) / 384 MB = 56 GB / 384 MB ≈ 149` séquences. En pratique, un serveur réserve une marge de sécurité supplémentaire sous ce plafond, mais l'arithmétique est cette division.

</details>

## Exercices en situation réelle

- [ ] Cherchez le champ `num_key_value_heads` (ou équivalent) dans le fichier de configuration d'un modèle que vous prévoyez de servir, à côté de `num_attention_heads`. Calculez le rapport entre les deux et ce qu'il rachète en taille de cache.
- [ ] Avec la taille de cache par token de ce modèle, calculez combien de séquences concurrentes pourrait contenir un pool de mémoire auquel vous avez accès (ou la mémoire d'un GPU publié) à une longueur de contexte qui vous importe.
- [ ] Demain : trouvez l'option que la pile de serving de votre choix (vLLM ou llama.cpp) utilise pour plafonner la mémoire totale du KV cache, et lisez ce qui se passe quand une requête la dépasserait.

## Pour aller plus loin

- [Billet : "Transformer Inference Arithmetic", Kipply](https://kipp.ly/transformer-inference-arithmetic/)
- [Article : "Efficient Memory Management for Large Language Model Serving with PagedAttention", Kwon et al., SOSP 2023](https://arxiv.org/abs/2309.06180)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
