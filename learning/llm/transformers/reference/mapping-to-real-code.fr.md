---
title: "Correspondance avec le vrai code"
description: "Où se trouve chaque pièce dérivée dans transformers ou llama.cpp, les trois écarts standard par rapport à l'article d'origine, le byte-pair encoding, et l'endroit où se rattache un adapter de faible rang"
type: reference
---

# Correspondance avec le vrai code

L'étape 5 condensée pour la consultation. La [leçon 12](../lessons/0012-reading-real-model-code.md) couvre la traduction des dérivations de cet espace de travail vers la nomenclature de `transformers` de Hugging Face et de llama.cpp ; la [leçon 13](../lessons/0013-tokenizers-and-low-rank-adapters.md) couvre la dérivation du byte-pair encoding et l'endroit où un adapter de faible rang se rattache à une matrice de poids. Cette fiche rassemble côte à côte la correspondance des noms, les écarts standard et les deux dérivations.

## Nomenclature dans `transformers` de Hugging Face

| Nom dans le vrai code | Dérivé dans | Ce que c'est |
|---|---|---|
| `GPT2Attention` (ou similaire) | Leçons 1-2 | La scaled dot-product attention, souvent via une seule couche linéaire QKV fusionnée, séparée ensuite, un détail d'efficacité de produit matriciel par lots, et non une opération différente |
| Un buffer de masque triangulaire inférieur enregistré | Leçon 3 | Le masquage causal, précalculé une fois puisque le masque ne dépend que de la longueur de séquence et non des valeurs d'entrée, et réutilisé ou découpé à chaque appel |
| `wte` (word token embedding) | Leçon 8 | La table d'embedding d'entrée |
| `wpe` (word position embedding) | Leçon 4 | L'encodage positionnel, ici couramment une table apprise plutôt que la formule sinusoïdale |
| Une `ModuleList` de blocs, parcourue dans une boucle for | Leçon 7 | Les blocs transformer empilés |
| `lm_head`, lié aux poids de `wte` | Leçon 8 | La projection de sortie, par weight tying |
| Le script d'entraînement ou `Trainer`, pas la classe du modèle | Leçons 9-11 | La loss d'entropie croisée, `.backward()`, le pas d'optimiseur ; la classe du modèle ne définit que la passe avant jusqu'aux logits |

## Trois écarts standard par rapport à l'article d'origine

| Pièce | Article d'origine | Courant dans les modèles de production | Toujours la même leçon sous-jacente |
|---|---|---|---|
| Embedding de position | Formule sinusoïdale | Une table apprise, ou des embeddings rotatifs | L'alternative apprise de la leçon 4, ou une variante supplémentaire |
| Fonction d'activation | ReLU | GELU (ou SwiGLU) | La forme d'extension puis de contraction de la leçon 6, avec une non-linéarité différente |
| Placement de la norme | Post-norm | Pre-norm | L'alternative pre-norm de la leçon 5 |

Aucun de ces écarts ne change l'architecture que cet espace de travail a dérivée ; ce sont des variations standard que l'on trouve dans presque toutes les implémentations réelles, et non une conception différente.

## Les mêmes mathématiques, une autre base de code : llama.cpp

llama.cpp (en C, via la bibliothèque de tenseurs `ggml`) construit un graphe de calcul explicite par des appels de fonctions plutôt que par des classes `nn.Module` avec une méthode `forward`. Il calcule les mêmes objets mathématiques : l'attention, l'encodage positionnel (couramment rotatif), la normalisation (couramment RMSNorm, une variante simplifiée de la layer norm) et un bloc feed-forward (couramment SwiGLU). La différence réside entièrement dans la façon dont le graphe de calcul est construit et exécuté, pas dans ce qu'il calcule.

## Dériver le tokenizer : le byte-pair encoding (BPE)

1. Représenter le texte d'entraînement comme une séquence d'octets ou de caractères bruts, chacun étant sa propre entrée du vocabulaire.
2. Compter chaque paire adjacente de symboles sur le corpus.
3. Fusionner la paire la plus fréquente en un nouveau symbole, ajouté au vocabulaire.
4. Répéter jusqu'à ce que le vocabulaire atteigne une taille cible choisie.

Exemple travaillé, corpus `"low low lower"` : la paire `l, o` est fréquente et fusionne en `lo` ; le tour suivant trouve `lo, w` et fusionne en `low`. Les mots fréquents se compressent vers un seul token ; les mots rares se replient sur des morceaux plus petits et plus fréquents.

`vocab_size` est le nombre de symboles de départ plus d'étapes de fusion pour lequel l'entraînement du tokenizer a été exécuté, fixé une fois cet entraînement terminé ; c'est exactement ce qui dimensionne la table d'embedding d'entrée et la couche de sortie de la leçon 8.

## Où se rattache un adapter de faible rang

Le mécanisme d'adapter de `llm/finetuning`, `ΔW = BA` où `A` projette vers le rang `r` et `B` reprojette vers le haut, se rattache à une matrice de poids concrète que cet espace de travail a dérivée, par exemple la projection de requête par tête de la leçon 2 :

```text
Q_i = X (W_Q^i + (alpha / r) B_i A_i)
```

| Matrice | Gelée ? | Reçoit des gradients pendant l'entraînement de l'adapter ? |
|---|---|---|
| `W_Q^i` | Oui, exactement comme pré-entraînée | Non |
| `A_i`, `B_i` | Non, nouvellement ajoutées, dimensionnées par le rang `r` | Oui |

Comme la mise à jour est additive et linéaire, exactement comme la projection d'origine, `W_Q^i + (alpha/r) B_i A_i` se réduit après l'entraînement à une seule matrice ordinaire. Rien dans la passe avant ne change pour servir le résultat fusionné, puisqu'il s'insère dans `Q_i = X W_Q^i` comme une matrice de projection ordinaire, sans aucun calcul ajouté à l'inférence.

## Avant de lire le code d'un vrai modèle ou d'y rattacher quelque chose

- [ ] Une couche linéaire QKV fusionnée qui est ensuite séparée est reconnue comme un détail d'efficacité, et non comme une opération différente des projections par tête.
- [ ] Le buffer de masque, s'il est précalculé, est compris comme ne dépendant que de la longueur de séquence, sans changer le mécanisme de masquage lui-même.
- [ ] Les choix d'embedding de position, d'activation et de placement de la norme sont confrontés aux trois écarts standard avant d'être traités comme une architecture différente.
- [ ] Le point de rattachement d'un adapter de faible rang est nommé comme une matrice de poids précise (quelle projection, dans quelle couche), et pas seulement « le modèle ».

## Sources

- [Dépôt : transformers, Hugging Face](https://github.com/huggingface/transformers)
- [Dépôt : nanoGPT, Karpathy](https://github.com/karpathy/nanoGPT)
- [Article : "Neural Machine Translation of Rare Words with Subword Units", Sennrich, Haddow et Birch, 2016](https://arxiv.org/abs/1508.07909)
- [Adapter](../../finetuning/GLOSSARY.md) : le terme canonique de `llm/finetuning` pour le schéma base gelée plus petits poids entraînables
- [Ressources](../RESOURCES.md)
