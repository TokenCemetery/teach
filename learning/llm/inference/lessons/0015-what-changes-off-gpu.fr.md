---
title: "15. Ce qui change hors GPU"
description: "Mettre en place le serveur de llama.cpp, et comment le batching, la gestion du cache et la quantification se présentent chacun différemment à l'échelle CPU/edge"
type: lesson
---

# Leçon 15. Ce qui change hors GPU

**Lien avec la mission :** C'est la synthèse de l'étape 5 et la seconde moitié des critères de réussite de la mission : une pile llama.cpp qui tourne sur CPU et répond à de vraies requêtes, avec chaque concept des étapes 1 à 4 réexaminé pour voir ce qui s'applique encore à cette échelle.
**Source primaire :** [Dépôt : llama.cpp, ggml-org](https://github.com/ggml-org/llama.cpp)
**Prérequis :** [Leçon 14](0014-llamacpp-architecture.md), [KV cache](../GLOSSARY.md)

## Échauffement

1. ▢ Que contrôle `--threads` dans llama.cpp, et en quoi est-ce différent de `--max-num-seqs` de vLLM ?

<details markdown="1"><summary>Vérifier</summary>

`--threads` répartit les multiplications matricielles d'une seule séquence entre les cœurs physiques du CPU. `--max-num-seqs` plafonne plutôt le nombre de séquences concurrentes qui partagent une étape de batch GPU, en amortissant entre elles le trafic mémoire. L'une accélère le calcul d'une séquence ; l'autre répartit le coût de bande passante mémoire entre de nombreuses séquences.

</details>

2. ▢ Décodez le nom de quantification `Q4_K_M` en ses trois parties.

<details markdown="1"><summary>Vérifier</summary>

`Q4` : à peu près 4 bits par poids. `K` : une méthode k-quant qui mélange la précision au sein d'un tenseur. `M` : le préréglage medium parmi les configurations de taille/qualité de cette méthode.

</details>

## À savoir

### Mettre en place le serveur

Le serveur propre à llama.cpp, `llama-server`, charge un fichier GGUF et expose un point d'accès HTTP compatible OpenAI, la même forme de requête que la leçon 10 a utilisée contre vLLM :

```text
llama-server -m model.Q4_K_M.gguf --threads 8
```

```bash
curl http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "model.Q4_K_M.gguf", "messages": [{"role": "user", "content": "Say hello"}]}'
```

La forme de la requête et de la réponse est familière. Ce qui change, c'est tout ce qui se trouve en dessous.

![Une comparaison en trois lignes. Batching : sur un GPU, le continuous batching amortit la bande passante mémoire entre des centaines de requêtes concurrentes ; à l'échelle CPU/edge, avec seulement de un chiffre à quelques dizaines de requêtes concurrentes, ce sont des threads qui répartissent le calcul d'une séquence entre les cœurs qui le remplacent. Gestion du cache : sur un GPU, PagedAttention gère un grand pool partagé en constante évolution ; à l'échelle CPU/edge, un simple cache contigu par séquence suffit. Moment de la quantification : sur un GPU avec vLLM, le schéma est une option de serving choisie au lancement ; sur llama.cpp, la décision était déjà verrouillée quand un niveau de quantification GGUF précis a été choisi, avant même que le serveur ne démarre.](images/gpu-vs-cpu-edge-mechanisms.svg)

### Le batching compte moins à cette échelle

Le continuous batching de vLLM (leçons 4 et 5) existe pour amortir le coût de bande passante mémoire d'un GPU entre les requêtes de centaines d'inconnus concurrents. Un CPU n'a pas d'équivalent des milliers de cœurs parallèles sur lesquels répartir ce coût ; le serveur de llama.cpp prend bien en charge une poignée d'emplacements de requêtes parallèles, mais à une échelle de un chiffre à quelques dizaines, pas de centaines. Ce n'est pas une fonctionnalité manquante : la charge de travail typique d'un déploiement edge, un appareil qui sert son propre utilisateur, a rarement des centaines de requêtes concurrentes à regrouper au départ. Le batching intensif résout un problème que le serving CPU/edge n'a généralement pas.

### Le cache n'a pas non plus besoin de pagination à cette échelle

PagedAttention (leçon 11) existe pour permettre à de nombreuses séquences de partager la mémoire efficacement et d'éviter la fragmentation sur un grand pool de requêtes concurrentes en constante évolution. À l'échelle CPU/edge, avec peu de séquences concurrentes et sans grand pool partagé à fragmenter, une allocation de cache par séquence plus simple et contiguë est courante et suffisante. Le problème que PagedAttention résout ne disparaît pas en principe, il atteint simplement rarement l'échelle où sa complexité se rentabilise.

### La décision de quantification a déjà eu lieu

Sur vLLM, `--quantization` est une option de serving : le schéma est choisi au démarrage du serveur, à partir d'un checkpoint déjà quantifié ou d'un checkpoint à quantifier au chargement. Sur llama.cpp, cette décision a été prise plus tôt, quand un fichier GGUF a été choisi (ou produit) à un niveau de quantification précis, comme `Q4_K_M`. Il n'y a pas d'option de serving pour le changer ; changer de quantification signifie télécharger ou produire un autre fichier GGUF. Le compromis des leçons 7 à 9, mémoire contre précision contre vitesse, s'applique toujours, il est simplement réglé avant même que le serveur ne démarre, et non configuré au démarrage.

## Pratique

1. ▢ Trois requêtes arrivent en même temps sur une instance `llama-server`, toutes de la part des utilisateurs d'un seul appareil edge. Prédisez, avant de vérifier : qu'arrive-t-il au débit de chaque requête, et pourquoi cela diffère-t-il de ce que fait le continuous batching sur un GPU ?

<details markdown="1"><summary>Vérifier</summary>

Le débit de chaque requête baisse à peu près en proportion du nombre de threads qu'elle doit désormais partager, puisque le nombre fixe de cœurs du CPU est réparti entre les requêtes concurrentes au lieu que chacune dispose de tout le nombre de threads pour elle seule. Cela diffère du continuous batching GPU, qui amortit un coût de bande passante mémoire déjà nécessaire entre des séquences concurrentes, pour un faible coût supplémentaire par séquence ; répartir le calcul CPU entre des requêtes n'a pas d'équivalent de coût « déjà payé de toute façon » à amortir.

</details>

2. ▢ Pourquoi le batching intensif à la manière de vLLM compte-t-il moins pour un déploiement CPU/edge typique que pour un serveur GPU ?

<details markdown="1"><summary>Vérifier</summary>

Le continuous batching justifie sa complexité quand les requêtes de nombreux inconnus concurrents se partagent le coût de bande passante mémoire d'un GPU. Un déploiement edge typique, un appareil qui sert son propre utilisateur, a rarement autant de requêtes concurrentes à regrouper au départ, donc le problème que le mécanisme résout n'est généralement pas présent à cette échelle.

</details>

3. ▢ Où la décision de quantification a-t-elle été prise pour un déploiement llama.cpp, par rapport à l'endroit où elle est prise pour un déploiement vLLM ?

<details markdown="1"><summary>Vérifier</summary>

Pour llama.cpp, elle a été prise quand un fichier GGUF précis (à un niveau de quantification précis, comme `Q4_K_M`) a été choisi ou produit, avant même que le serveur ne démarre ; la changer signifie utiliser un autre fichier. Pour vLLM, c'est une option de serving, `--quantization`, choisie au lancement du serveur. Le compromis lui-même est celui qu'ont enseigné les leçons 7 à 9 ; seul le moment où la décision est verrouillée diffère.

</details>

4. ▢ Laquelle de ces affirmations est vraie sur la raison pour laquelle une gestion de la mémoire à la manière de PagedAttention est moins souvent nécessaire à l'échelle CPU/edge ?

    - a) Le matériel CPU rend la pagination techniquement impossible
    - b) La charge de travail typique a assez peu de séquences concurrentes pour qu'un cache contigu par séquence plus simple suffise
    - c) Le format GGUF de llama.cpp est incompatible avec toute forme de mémoire paginée
    - d) Les KV caches n'existent pas du tout dans le serving CPU

<details markdown="1"><summary>Vérifier</summary>

**b)** Avec peu de séquences concurrentes et sans grand pool partagé à fragmenter, un schéma d'allocation plus simple suffit généralement ; le problème que PagedAttention résout atteint rarement l'échelle où sa complexité se rentabilise. (a) est fausse : rien dans le matériel CPU n'exclut la pagination, c'est un compromis de conception, pas une limitation. (c) est fausse : GGUF décrit le fichier du modèle, pas la disposition du cache du runtime. (d) est fausse : le decode a toujours besoin d'un KV cache sur CPU, pour la même raison qu'a établie la leçon 1 ; il est simplement le plus souvent géré plus simplement.

</details>

## Exercices en situation réelle

- [ ] Compilez ou installez llama.cpp, téléchargez un petit modèle GGUF, et exécutez `llama-server` avec un nombre de threads adapté au nombre de cœurs de votre CPU.
- [ ] Envoyez la requête curl de cette leçon à votre serveur en fonctionnement, et confirmez que vous obtenez une vraie complétion en retour.
- [ ] Demain : envoyez deux ou trois requêtes en même temps à votre serveur en fonctionnement et observez, de façon informelle, si chacune paraît plus lente que lorsqu'elle est la seule requête en cours.

## Pour aller plus loin

- [Dépôt : llama.cpp, ggml-org](https://github.com/ggml-org/llama.cpp)
- [Doc : vLLM Documentation, vLLM Project](https://docs.vllm.ai/en/latest/)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
