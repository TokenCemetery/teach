---
title: "Transformers"
description: "Construire l'attention à partir de zéro, pour que l'architecture cesse d'être une boîte noire derrière le script d'entraînement"
type: topic
---

# Apprentissage : les transformers

Savoir implémenter la passe avant d'un transformer et sa boucle d'entraînement à partir de tenseurs bruts, et savoir lire ou modifier du vrai code de modèle sans que l'architecture soit une boîte noire derrière lui.

**Dernière leçon :** [23. Relire une modification du code d'un modèle](lessons/0023-reviewing-a-change-to-model-code.md)

## Objectif

- Implémenter la scaled dot-product attention, la multi-head attention et un bloc transformer complet à partir de tenseurs bruts, en retrouvant la sortie d'une implémentation de référence.
- Écrire à partir de zéro la boucle d'entraînement qui entoure ce bloc et expliquer ce que fait chaque pièce (loss, passe arrière, pas d'optimiseur) aux poids.
- Lire le code d'un vrai modèle (une bibliothèque comme `transformers` ou `llama.cpp`) et indiquer où se trouve chaque pièce dérivée.
- Relire la modification que quelqu'un d'autre apporte au code d'un modèle et nommer précisément ce qu'elle casse ou ce qu'elle coûte (un bug de forme qui n'apparaît que deux couches plus loin, une accélération affirmée sans sortie correspondante, une affirmation d'architecture qui ne résiste pas à une relecture des équations réelles de l'article), au lieu de se fier à la description de la pull request.

## Contraintes

- Suppose l'aisance avec Python et les opérations de base sur les tenseurs PyTorch, et le produit matriciel comme seule mathématique tenue pour acquise ; aucune connaissance préalable en deep learning n'est requise.
- Implémentation en PyTorch, avec des opérations brutes sur les tenseurs plutôt que `nn.Transformer` ou d'autres modules d'attention préconstruits ; l'autograd et la prise en charge du GPU sont conservés, seule l'architecture elle-même est construite à la main.

## Hors périmètre

- Les variantes d'optimiseur et de planificateur au-delà de la boucle de base nécessaire pour voir le bloc s'entraîner, et l'entraînement distribué : voir [`llm/pretraining`](../../llm/pretraining/), qui prend le relais quand cette boucle doit s'exécuter sur de nombreux GPU.
- Le dispositif de faible rang et d'adapters construit au-dessus du bloc : voir [`llm/finetuning`](../../llm/finetuning/) pour cette frontière. Cet espace de travail dérive ce que celui-là nomme en passant (les tokenizers dans sa leçon 0003, l'idée de faible rang dans sa leçon 0008) au lieu de le répéter.

## Le fil conducteur

Douze étapes, d'une équation jusqu'à la lecture et à la génération à partir de vrai code de modèle à n'importe quelle échelle. Une étape comprend plusieurs leçons et les frontières sont souples ; ce qui termine une étape, c'est la capacité acquise, pas le nombre de leçons.

| Étape | Leçons | Contenu | Terminée quand |
|---|---|---|---|
| 1. L'attention | 0001 à 0003 | Scaled dot-product attention, multi-head attention, masquage causal | La multi-head attention est implémentée à partir de tenseurs bruts, en retrouvant une implémentation de référence |
| 2. Le bloc transformer | 0004 à 0006 | Encodage positionnel, layer norm et connexions résiduelles, bloc feed-forward | Un bloc transformer complet est implémenté à partir de tenseurs bruts |
| 3. Le modèle complet | 0007 à 0008 | Empilement des blocs, couches d'embedding et de sortie, weight tying | Une passe avant complète retrouve la sortie d'une implémentation de référence |
| 4. La boucle d'entraînement | 0009 à 0011 | Loss d'entropie croisée sur le vocabulaire, passe arrière, pas de l'optimiseur AdamW | Le modèle s'entraîne à partir de zéro et la loss diminue comme prévu |
| 5. Lire du vrai code de modèle | 0012 à 0013 | Associer chaque pièce dérivée à une vraie bibliothèque (`transformers` ou `llama.cpp`), tokenizers et adapters de faible rang nommés en passant | Vous savez indiquer où se trouve chaque pièce dérivée dans du vrai code de modèle |
| 6. Encodage positionnel et normalisation modernes | 0014 à 0015 | Embeddings de position rotatifs, RMSNorm | Vous savez dériver la propriété de position relative de RoPE et expliquer ce que RMSNorm retire de la layer norm |
| 7. Variantes modernes du feed-forward et de l'attention | 0016 à 0017 | SwiGLU et le feed-forward à porte, grouped-query et multi-query attention, KV caching | Vous savez dériver un bloc feed-forward à porte et expliquer pourquoi moins de têtes KV échangent de la qualité contre de la taille de cache |
| 8. Génération et échantillonnage | 0018 | Décodage glouton, température, échantillonnage top-k et top-p, exécution du modèle vers l'avant pour produire du texte | Vous savez générer du texte à partir du modèle construit à la main et expliquer pourquoi le décodage glouton dégénère |
| 9. Les aspects pratiques de la boucle d'entraînement | 0019 à 0020 | Initialisation de Xavier, warmup et décroissance du learning rate, écrêtage du gradient, précision mixte, accumulation de gradient | Vous savez expliquer contre quoi se protège chaque aspect pratique et les ajouter à une boucle d'entraînement fonctionnelle |
| 10. Architectures encodeur-décodeur et encodeur seul | 0021 | L'encodeur bidirectionnel de BERT, l'encodeur-décodeur de T5 avec cross-attention, situer le modèle decoder-only de cet espace de travail | Vous savez expliquer pourquoi chaque architecture utilise ou non un masque causal, et où se place la cross-attention |
| 11. Mixture-of-experts et FlashAttention | 0022 | Routage MoE à activation parcimonieuse, découpage en tuiles sensible aux entrées-sorties de FlashAttention | Vous savez expliquer comment le MoE découple les paramètres du calcul par token, et pourquoi FlashAttention est exacte et non approchée |
| 12. Le jugement | 0023 | Relire les modifications du code d'un modèle faites par quelqu'un d'autre, vérifier les formes et l'exactitude de la sortie, trancher les affirmations contestées à partir de la source primaire | On vous fait confiance pour relire les modifications de l'architecture d'un modèle et de sa boucle d'entraînement, et pour expliquer ce qu'une modification coûte ou risque au lieu d'en accepter la description |

## Leçons

Suivez-les dans l'ordre.

| # | Leçon | Enseigne |
|---|---|---|
| [0001](lessons/0001-scaled-dot-product-attention.md) | Scaled dot-product attention | L'unique équation autour de laquelle le reste de l'architecture est construit |
| [0002](lessons/0002-multi-head-attention.md) | Multi-head attention | Pourquoi l'attention s'exécute dans plusieurs sous-espaces plus petits à la fois plutôt que dans un seul à pleine dimension |
| [0003](lessons/0003-causal-masking.md) | Masquage causal | Pourquoi une position de requête ne doit pas porter son attention sur les positions futures, et pourquoi le masque s'applique avant le softmax et non après |
| [0004](lessons/0004-positional-encoding.md) | Encodage positionnel | Pourquoi l'attention est aveugle à l'ordre à elle seule, et comment l'encodage sinusoïdal donne à chaque position une signature distinguable |
| [0005](lessons/0005-layer-norm-and-residuals.md) | Layer norm et connexions résiduelles | Pourquoi empiler de nombreux blocs transformer exige un chemin de gradient propre et des plages d'activation stables, et comment les connexions résiduelles et la layer norm en fournissent chacune un |
| [0006](lessons/0006-feed-forward-block.md) | Le bloc feed-forward position par position | Ce que la seconde sous-couche du bloc transformer apporte en plus de l'attention, et pourquoi elle ne mélange jamais l'information entre les positions |
| [0007](lessons/0007-stacking-blocks.md) | Empiler des blocs transformer | Pourquoi chaque bloc conserve la même forme, pourquoi la profondeur n'est pas du partage de poids, et pourquoi le dispositif résiduel de la leçon 5 compte le plus quand de nombreux blocs sont empilés |
| [0008](lessons/0008-embedding-output-and-weight-tying.md) | Couches d'embedding et de sortie, weight tying | Comment les tokens entrent dans l'espace vectoriel du transformer et en sortent, et pourquoi les deux couches qui s'en chargent peuvent partager une seule matrice |
| [0009](lessons/0009-cross-entropy-loss.md) | Loss d'entropie croisée sur le vocabulaire | Comment les logits deviennent un nombre entraînable, et pourquoi la loss est le logarithme négatif de la probabilité du token suivant réel |
| [0010](lessons/0010-backward-pass-and-autograd.md) | La passe arrière et autograd | Comment la règle de la chaîne, automatisée sur un graphe de calcul enregistré, transforme une loss scalaire en un gradient pour chaque poids |
| [0011](lessons/0011-adamw-optimizer.md) | Le pas de l'optimiseur AdamW | Ce que le momentum et la mise à l'échelle adaptative d'Adam apportent par rapport à la descente de gradient simple, et pourquoi AdamW découple le weight decay de la mise à jour par le gradient |
| [0012](lessons/0012-reading-real-model-code.md) | Lire du vrai code de modèle | Où se trouve chaque pièce dérivée dans une bibliothèque de modèles de production, et les petits écarts courants par rapport à l'article d'origine qu'il vaut mieux reconnaître que de s'y perdre |
| [0013](lessons/0013-tokenizers-and-low-rank-adapters.md) | Tokenizers et adapters de faible rang | Dériver le byte-pair encoding, et voir où un adapter de faible rang se rattache réellement à une matrice de poids que cet espace de travail a construite à partir de zéro |
| [0014](lessons/0014-rotary-position-embeddings.md) | Embeddings de position rotatifs | L'encodage sinusoïdal ajoute un vecteur fixe à l'embedding avant même que l'attention s'exécute ; RoPE fait au contraire tourner Q et K eux-mêmes, et ce seul changement est ce qui fait qu'un produit scalaire entre deux vecteurs tournés ne dépend que de leur distance relative |
| [0015](lessons/0015-rmsnorm.md) | RMSNorm | LayerNorm fait deux choses, recentrer et remettre à l'échelle, et RMSNorm existe parce que la moitié recentrage se révèle superflue, ce qui laisse une normalisation moins coûteuse que les modèles actuels placent dans la branche pre-norm déjà dérivée à la leçon 5 |
| [0016](lessons/0016-swiglu-and-the-gated-feed-forward.md) | SwiGLU et le bloc feed-forward à porte | Le bloc feed-forward de la leçon 6 étend, applique une non-linéarité et contracte ; une variante à porte calcule deux projections au lieu d'une et les multiplie, ce qui laisse le réseau apprendre quelle part de son propre calcul laisser passer |
| [0017](lessons/0017-grouped-query-attention-and-kv-caching.md) | Grouped-query attention et KV caching | La génération autorégressive fait recalculer à l'attention des clés et des valeurs qu'elle a déjà, et une fois que les mettre en cache devient la correction évidente, c'est la taille du cache lui-même qui justifie d'échanger un peu de qualité contre moins de têtes de clés et de valeurs |
| [0018](lessons/0018-generation-and-sampling.md) | Génération et échantillonnage | Le modèle que cet espace de travail a construit et entraîné n'a jamais produit le moindre texte, parce que l'entraînement et la génération lui posent deux questions différentes, et prendre toujours le token suivant le plus probable se révèle une moins bonne réponse à la seconde question qu'une dose bien choisie d'aléatoire |
| [0019](lessons/0019-initialization-warmup-and-gradient-clipping.md) | Initialisation, warmup et écrêtage du gradient | Un modèle aussi profond peut échouer avant même que l'entraînement commence si ses poids initiaux sont mal dimensionnés, et le pas AdamW dérivé à la leçon 11 a encore besoin de deux garde-fous, un départ lent et un plafond strict sur le gradient, pour survivre à un vrai entraînement |
| [0020](lessons/0020-mixed-precision-and-gradient-accumulation.md) | Précision mixte et accumulation de gradient | Les deux techniques existent pour faire tenir un run d'entraînement effectif plus gros dans un matériel plus petit que ce que le run semble exiger, l'une en réduisant l'empreinte de chaque nombre, l'autre en simulant un batch plus grand que ce que la mémoire pourrait jamais contenir d'un coup |
| [0021](lessons/0021-encoder-decoder-and-encoder-only-architectures.md) | Architectures encodeur-décodeur et encodeur seul | Cet espace de travail a construit un flux unique avec un masque causal parce qu'il n'avait jamais qu'une chose à faire, générer le token suivant, et les deux autres formes d'architecture existent parce que BERT et le modèle de traduction d'origine avaient besoin d'une garantie structurellement différente |
| [0022](lessons/0022-mixture-of-experts-and-flashattention.md) | Mixture-of-experts et FlashAttention | Le MoE accroît le nombre total de paramètres d'un modèle sans accroître ce que coûte le traitement d'un token donné, et FlashAttention calcule exactement la même équation que la leçon 1, plus vite, en réécrivant la façon dont elle touche la mémoire, pas ce qu'elle calcule |
| [0023](lessons/0023-reviewing-a-change-to-model-code.md) | Relire une modification du code d'un modèle | Relire la modification du code d'un modèle faite par quelqu'un d'autre et nommer ce qu'elle casse ou ce qu'elle coûte, au lieu de se fier à sa description |

## Référence

- [Glossaire](GLOSSARY.md) : termes de référence pour ce sujet
- [Ressources](RESOURCES.md) : sources fiables
- [Attention](reference/attention.md) : scaled dot-product attention, multi-head attention et masquage causal, avec les formes des tenseurs annotées à chaque étape
- [Le bloc transformer](reference/the-transformer-block.md) : encodage positionnel, layer norm et résiduels, bloc feed-forward, empilement et weight tying
- [La boucle d'entraînement](reference/the-training-loop.md) : loss d'entropie croisée, passe arrière et autograd, et pas de l'optimiseur AdamW, avec les exemples travaillés de règle de la chaîne et de descente de gradient
- [Correspondance avec le vrai code](reference/mapping-to-real-code.md) : la correspondance des noms entre transformers et llama.cpp, les trois écarts standard par rapport à l'article d'origine, le byte-pair encoding, et l'endroit où se rattache un adapter de faible rang

## Comment cela fonctionne

Chaque leçon est courte et autonome. Les corrigés sont repliés : rappelez-vous d'abord, puis ouvrez-les. Les exercices en situation réelle comptent plus que la lecture, et les espacer dans le temps est justement le but. Tout ce qui reste flou à la fin d'une leçon mérite d'être suivi jusqu'à sa source primaire avant de passer à la suite.
