---
title: "1. Le KV cache"
description: "Pourquoi la génération devient coûteuse, et ce que la mise en cache rachète"
type: lesson
---

# Leçon 1. Le KV cache

**Lien avec la mission :** Chaque chiffre de latence et de débit que cet espace de travail défend remonte à ce que le KV cache coûte en mémoire et à la qualité avec laquelle un serveur gère ce coût.
**Source primaire :** [Doc : "Optimizing inference", Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/llm_optims)
**Prérequis :** aucun

## À savoir

### Pourquoi le décodage a besoin d'un cache

Un transformer génère un token à la fois. Pour produire le token *N*, l'auto-attention a besoin des vecteurs de clés et de valeurs de chaque token de 1 à *N*, à chaque couche. Sans cache, chaque nouveau token oblige le modèle à recalculer les clés et les valeurs de *tout* le préfixe, alors que ces vecteurs ne changent plus une fois le token généré. C'est un travail quadratique dépensé à recalculer ce qui l'a déjà été.

Le **KV cache** stocke les vecteurs de clés et de valeurs de chaque token, par couche, dès qu'ils sont calculés pour la première fois. Générer le token *N+1* ne calcule alors qu'un seul nouvel ensemble de vecteurs K/V et réutilise le reste. C'est ce qui rend la génération autorégressive praticable : elle échange du recalcul contre de la mémoire.

### Ce que cette mémoire coûte réellement

Le cache n'est pas gratuit, et sa taille détermine combien de requêtes un serveur peut garder en mémoire en même temps. Par token et par couche, il contient un vecteur de clé et un vecteur de valeur, chacun de taille égale à la dimension cachée du modèle (`d_model`, la dimension du flux résiduel du modèle). En demi-précision (2 octets par valeur) :

```text
bytes per token = 2 (K and V) × num_layers × d_model × 2 bytes
```

Prenons Llama-2-7B comme cas concret : 32 couches, `d_model` = 4096.

```text
2 × 32 × 4096 × 2 bytes = 524,288 bytes ≈ 512 KB per token
```

Avec un contexte de 4096 tokens, cela donne `512 KB × 4096 ≈ 2 GB`, pour une *seule* séquence. Gardez 16 séquences de ce type en même temps et le cache à lui seul demande environ 32 GB, soit plus que les 14 GB que prennent les poids du modèle en fp16. C'est l'arithmétique qui explique pourquoi « ajouter simplement du KV cache » est le mauvais réflexe, et pourquoi les piles de serving se préoccupent autant de la mémoire du cache au lieu de la traiter comme un détail (voir [Transformer Inference Arithmetic](https://kipp.ly/transformer-inference-arithmetic/) de Kipply pour la dérivation complète, y compris la façon dont cela évolue avec les schémas de partage de têtes d'attention comme GQA/MQA).

### Où la mise en cache naïve gaspille de la mémoire

Une implémentation naïve réserve un bloc de mémoire contigu par séquence, dimensionné pour la longueur maximale de séquence qu'elle pourrait jamais atteindre. Deux modes de défaillance en découlent :

- **Fragmentation interne** : une séquence qui finit courte détient quand même de la mémoire réservée pour une longueur maximale qu'elle n'a jamais utilisée.
- **Fragmentation externe** : des séquences de longueurs réelles différentes laissent entre leurs blocs réservés des trous dans lesquels le cache d'aucune autre séquence ne peut tenir.

L'article de PagedAttention a mesuré des systèmes naïfs dont seulement 20 à 40 % de la mémoire de KV cache allouée contenait réellement des données utiles. Sa solution s'inspire directement de la mémoire virtuelle des systèmes d'exploitation : découper le cache en blocs de taille fixe, les stocker de façon non contiguë, et tenir pour chaque séquence une table de blocs qui fait correspondre les positions logiques aux blocs physiques. C'est l'idée autour de laquelle vLLM est construit, et c'est pourquoi le framework compte autant que l'arithmétique : le même cache, bien alloué, sert beaucoup plus de requêtes concurrentes.

![En haut : des blocs contigus naïfs, dimensionnés à la longueur maximale, gaspillent de la mémoire par fragmentation interne (réservée mais inutilisée) et par fragmentation externe (un trou entre les blocs). En bas : les blocs non contigus de taille fixe de PagedAttention s'entrelacent librement, de sorte qu'une séquence ne détient que le nombre de blocs qu'elle a réellement utilisés.](images/paged-attention-fragmentation.svg)

## Pratique

1. ▢ En une phrase, que permet le KV cache à un serveur de ne pas faire à chaque token généré après le premier ?

<details markdown="1"><summary>Vérifier</summary>

Recalculer les vecteurs de clés et de valeurs de chaque token précédent de la séquence, à chaque couche. Seuls les K/V du nouveau token doivent être calculés ; le reste est lu dans le cache.

</details>

2. ▢ Un modèle a 40 couches et `d_model` = 5120, servi en fp16. Estimez la taille du KV cache pour une séquence avec un contexte de 2048 tokens.

<details markdown="1"><summary>Indice</summary>

Utilisez `2 × num_layers × d_model × 2 bytes`, puis multipliez par le nombre de tokens.

</details>

<details markdown="1"><summary>Vérifier</summary>

Par token : `2 × 40 × 5120 × 2 = 819,200 bytes ≈ 800 KB`.
À 2048 tokens : `800 KB × 2048 ≈ 1.6 GB` pour une séquence.

</details>

3. ▢ Deux séquences détiennent des blocs de KV cache naïfs, contigus et dimensionnés à la longueur maximale. L'une se termine bien avant la longueur maximale qu'elle avait réservée. Qu'advient-il de la mémoire qu'elle a réservée sans l'utiliser, et que cela coûte-t-il au serveur ?

<details markdown="1"><summary>Vérifier</summary>

Elle reste réservée et inutilisable par toute autre séquence jusqu'à ce que le cache de cette séquence soit libéré : c'est la fragmentation interne. Le coût est un nombre réduit de séquences concurrentes que le serveur peut réellement servir, puisque de la mémoire qui paraît « allouée » ne fait aucun travail utile.

</details>

4. ▢ Laquelle de ces affirmations est vraie à propos de la solution de PagedAttention ?

    - a) Elle réduit la taille totale du KV cache pour un modèle et une longueur de contexte donnés
    - b) Elle supprime le KV cache et recalcule l'attention à la demande à la place
    - c) Elle réduit la mémoire gaspillée en stockant le cache dans des blocs non contigus de taille fixe
    - d) Elle n'aide que les piles de serving CPU comme llama.cpp

<details markdown="1"><summary>Vérifier</summary>

**c)** Elle réduit la mémoire gaspillée en stockant le cache dans des blocs non contigus de taille fixe, adressés par une table de blocs propre à chaque séquence, la même idée que la pagination de la mémoire virtuelle d'un OS.

(a) est fausse : le coût par token est inchangé ; seul le gaspillage qui l'entoure diminue. (b) est fausse : le cache est toujours là, simplement mieux alloué. (d) est fausse : PagedAttention est une technique de serving GPU (vLLM) ; cet espace de travail traite llama.cpp séparément.

</details>

## Exercices en situation réelle

- [ ] Choisissez un modèle que vous prévoyez de servir. Calculez sa taille de KV cache par token avec la formule ci-dessus, à partir de son `num_layers` et de sa taille cachée publiés.
- [ ] Calculez la taille totale des poids de ce même modèle dans la précision où vous le serviriez, et comparez-la à la taille du KV cache à sa longueur de contexte maximale.
- [ ] Demain : trouvez la documentation d'une pile de serving (vLLM ou llama.cpp) et repérez l'option qui contrôle la quantité de mémoire qu'elle réserve au KV cache.

## Pour aller plus loin

- [Billet : "Transformer Inference Arithmetic", Kipply](https://kipp.ly/transformer-inference-arithmetic/)
- [Article : "Efficient Memory Management for Large Language Model Serving with PagedAttention", Kwon et al., SOSP 2023](https://arxiv.org/abs/2309.06180)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
