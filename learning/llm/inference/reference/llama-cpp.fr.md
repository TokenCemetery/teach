---
title: "llama.cpp"
description: "Le format de GGUF et ses noms de quantification, l'abstraction de backend de ggml, et ce qui change quand le serving quitte le GPU"
type: reference
---

# llama.cpp

La pile de serving CPU/edge. Conçu pour la consultation lors de la mise en place ou du raisonnement sur un déploiement llama.cpp.

## GGUF

Un seul fichier binaire qui regroupe les poids, le tokenizer et les métadonnées d'architecture, à la place des plusieurs fichiers séparés (`config.json`, tokenizer, poids) sous lesquels un checkpoint Hugging Face est livré. Ce regroupement compte surtout pour un déploiement edge : livrer un seul fichier à exécuter avec un petit binaire à peu de dépendances, sans écosystème Python ou Hugging Face installé pour réassembler les morceaux.

Parce que GGUF dispose les poids dans un format que l'OS peut lire directement, llama.cpp peut **projeter en mémoire** le fichier (`mmap`) au lieu de le lire avec empressement en RAM et de le désérialiser. Les pages ne sont lues sur le disque qu'à mesure que quelque chose les touche, et le cache de pages propre à l'OS gère ce qui reste résident. Cela compte surtout là où la RAM est la ressource la plus tendue, le matériel CPU et edge, moins sur un serveur GPU avec beaucoup de RAM système.

### Noms de quantification

GGUF porte la propre famille de quantification de llama.cpp, distincte de GPTQ et AWQ orientés GPU. Décodage d'un nom comme `Q4_K_M` :

| Partie | Signification |
|---|---|
| `Q4` | Largeur de bits : à peu près 4 bits par poids (aussi `Q5`, `Q8` et d'autres) |
| `K` | Un type **k-quant** : une largeur de bits par tenseur, avec des super-blocs de 256 poids dont les sous-blocs portent chacun leur propre échelle |
| `M` | La recette qui mélange les types selon les tenseurs, en donnant à certains tenseurs un type à plus de bits : `S` (small), `M` (medium), `L` (large). Voir [la fiche Measuring and Storing du parcours sur la quantification](../../quantization/reference/measuring-and-storing.md) |

## ggml : une base de code, de nombreux backends

llama.cpp repose sur **ggml**, une bibliothèque de tenseurs en C sans dépendances (aucune BLAS externe requise). Une passe avant est un graphe de calcul statique, construit une fois puis exécuté, plutôt que l'exécution eager opération par opération de PyTorch. Cette séparation entre « quoi calculer » et « qui l'exécute » est ce qui permet au même graphe de cibler plusieurs **backends**, CPU (AVX2/NEON), CUDA, Metal, Vulkan, à partir d'une seule base de code et sans runtime Python, sur du matériel allant du CPU ARM d'un téléphone au GPU Metal d'un Mac et à un Raspberry Pi. La conception de vLLM, en revanche, est spécifique à CUDA et ne peut pas fonctionner sans GPU NVIDIA.

## Les threads remplacent le batching GPU

| | Répartit | Borné par |
|---|---|---|
| Batching GPU (`--max-num-seqs`) | Le coût de bande passante mémoire entre des séquences concurrentes | La capacité du cache et le budget de latence |
| Threads CPU (`--threads`) | Les multiplications matricielles d'une seule séquence entre les cœurs | Le nombre de cœurs physiques du CPU |

Le multithreading accélère le calcul propre d'une séquence ; il n'a pas d'équivalent du « on paie déjà la lecture mémoire de toute façon » à amortir entre les requêtes d'inconnus comme le fait le batching GPU.

## Mettre en place le serveur

```text
llama-server -m model.Q4_K_M.gguf --threads 8
```

```bash
curl http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "model.Q4_K_M.gguf", "messages": [{"role": "user", "content": "Say hello"}]}'
```

La même forme de requête compatible OpenAI que [vLLM](vllm.md) ; ce qui change, c'est tout ce qui se trouve en dessous.

## Ce qui change hors GPU

| Mécanisme | Sur un GPU (vLLM) | À l'échelle CPU/edge (llama.cpp) |
|---|---|---|
| Concurrence | Le [continuous batching](batching.md) amortit la bande passante mémoire entre les requêtes de centaines d'inconnus concurrents | Une poignée d'emplacements parallèles (de un chiffre à quelques dizaines) ; une charge de travail edge typique, un appareil qui sert son propre utilisateur, a rarement des centaines de requêtes concurrentes à regrouper |
| Gestion du cache | [PagedAttention](vllm.md#pagedattention) gère un grand pool partagé en constante évolution | Un cache contigu par séquence plus simple suffit ; le problème que PagedAttention résout atteint rarement l'échelle où sa complexité se rentabilise |
| Moment de la quantification | Une option de serving (`--quantization`), choisie au lancement | Déjà verrouillée quand un niveau de quantification GGUF précis a été choisi ou produit ; la changer signifie utiliser un autre fichier, pas une option |

Les compromis eux-mêmes ([mémoire, vitesse et précision](quantization-at-serve-time.md)) sont inchangés ; seuls le moment où chaque décision est prise, et la concurrence à laquelle elle se rentabilise, diffèrent.

## Voir aussi

- [Leçon 13](../lessons/0013-gguf.md), [Leçon 14](../lessons/0014-llamacpp-architecture.md), [Leçon 15](../lessons/0015-what-changes-off-gpu.md)
- [vLLM](vllm.md), [Batching](batching.md), [Quantification au moment du serving](quantization-at-serve-time.md) : les mécanismes côté GPU auxquels cette fiche se compare
