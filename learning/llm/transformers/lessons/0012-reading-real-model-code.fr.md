---
title: "12. Lire du vrai code de modèle"
description: "Où se trouve chaque pièce dérivée dans une bibliothèque de modèles de production, et les petits écarts courants par rapport à l'article d'origine qu'il vaut mieux reconnaître que de s'y perdre"
type: lesson
---

# Leçon 12. Lire du vrai code de modèle

**Lien avec la mission :** L'étape 5 est la dernière ligne droite : tout ce qui a été dérivé à partir de tenseurs bruts aux étapes 1 à 4 existe dans du vrai code de production, sous d'autres noms et avec une poignée de petits écarts standard par rapport à l'article d'origine, et cette leçon montre comment passer de ce qui a été construit ici à ce qui tourne réellement en pratique.
**Source primaire :** [Dépôt : transformers, Hugging Face](https://github.com/huggingface/transformers)
**Prérequis :** [Leçon 11](0011-adamw-optimizer.md), [Scaled dot-product attention](../GLOSSARY.md)

## Échauffement

1. ▢ Qu'est-ce qui ne va pas quand on intègre le weight decay au gradient dans l'Adam d'origine, et que fait AdamW différemment ?

<details markdown="1"><summary>Vérifier</summary>

Intégré au gradient, le weight decay est divisé par le terme de mise à l'échelle adaptative avec tout le reste, si bien que son rétrécissement effectif varie selon le paramètre au lieu de s'appliquer uniformément. AdamW applique le weight decay directement aux poids, ajouté à la mise à jour séparément du terme fondé sur le gradient.

</details>

2. ▢ Les poids d'un bloc transformer sont-ils les mêmes que ceux d'un autre bloc de la pile ? Que cela coûte-t-il, et qu'est-ce que cela apporte ?

<details markdown="1"><summary>Vérifier</summary>

Non, chaque bloc a ses propres paramètres, appris indépendamment, ce qui coûte du nombre de paramètres à peu près linéairement avec la profondeur mais permet aux différents blocs de se spécialiser différemment au lieu d'être forcés de calculer une transformation identique à chaque profondeur.

</details>

## À savoir

### Les mêmes pièces, sous des noms différents

Un modèle de style GPT-2 dans la bibliothèque `transformers` de Hugging Face implémente tout ce que cet espace de travail a dérivé, simplement avec ses propres conventions de nommage. L'attention vit dans une classe comme `GPT2Attention`, qui calcule la même opération de scaled dot-product de la leçon 1, souvent via une seule couche linéaire fusionnée qui produit Q, K et V concaténés, puis séparés, un détail d'efficacité de produit matriciel par lots, et non une opération différente des projections séparées par tête de la leçon 2. Le masquage causal (leçon 3) apparaît sous la forme d'un buffer enregistré, précalculé, qui contient un masque triangulaire inférieur, appliqué aux scores d'attention avant le softmax exactement comme dérivé, au lieu d'être reconstruit de zéro à chaque appel de forward : comme le masque ne dépend que de la longueur de séquence, et non des valeurs d'entrée réelles, le calculer une fois et le réutiliser (ou en prendre une tranche) est un pur choix d'efficacité qui ne change rien au mécanisme lui-même. Les embeddings de tokens et de positions apparaissent sous forme de tables `wte` (word token embedding) et `wpe` (word position embedding) (leçons 4 et 8) ; les blocs empilés vivent dans une `ModuleList` parcourue par une boucle for dans la méthode forward du modèle, ce qui correspond directement à la leçon 7 ; et la projection de sortie est une couche linéaire, couramment nommée `lm_head`, liée aux poids de `wte` par une affectation explicite ou un appel à `tie_weights()`, exactement le weight tying de la leçon 8.

![Une correspondance en deux colonnes. À gauche, cinq pièces dérivées dans cet espace de travail : l'attention des leçons 1 et 2, le masque causal de la leçon 3, l'encodage positionnel de la leçon 4, les blocs empilés de la leçon 7, et l'embedding avec le weight tying de la leçon 8. À droite, le nom correspondant que chacune prend dans la bibliothèque transformers de Hugging Face : GPT2Attention avec une projection requête-clé-valeur fusionnée, un buffer triangulaire inférieur enregistré, une table de positions wpe apprise, une ModuleList de blocs parcourue dans une boucle for, et wte lié à lm_head. Une ligne relie chaque concept de gauche à son nom dans le vrai code à droite.](images/workspace-to-real-code-mapping.svg)

### Trois petits écarts standard par rapport à l'article d'origine

Presque tous les modèles de production modernes s'écartent de l'article d'origine des mêmes quelques petites façons, et les reconnaître comme des implémentations de concepts déjà couverts, et non comme quelque chose de nouveau, est le but de cette leçon. **Embedding de position** : beaucoup de modèles utilisent une table de positions apprise (l'alternative de la leçon 4 à l'encodage sinusoïdal) ou des embeddings rotatifs, plutôt que la formule sinusoïdale de l'article d'origine. **Fonction d'activation** : le bloc feed-forward (leçon 6) utilise couramment GELU au lieu du ReLU de l'article d'origine, la même forme d'extension puis de contraction, avec une non-linéarité différente. **Placement de la norme** : la plupart des modèles actuels utilisent le pre-norm (l'alternative de la leçon 5), qui place la layer norm avant chaque sous-couche à l'intérieur de la branche résiduelle, plutôt que le post-norm de l'article d'origine. Aucun de ces écarts ne change l'architecture sous-jacente que cet espace de travail a dérivée ; ce sont les variations standard que l'on trouve dans presque toutes les implémentations réelles.

### Le code d'entraînement vit en dehors de la classe du modèle

Les pièces de l'étape 4, l'appel à la loss d'entropie croisée, `loss.backward()` et le pas d'optimiseur, ne font pas du tout partie de la classe du modèle ; elles vivent dans le script d'entraînement ou dans un utilitaire d'entraînement (comme le `Trainer` de Hugging Face, ou une boucle personnalisée comme celle de nanoGPT). La classe du modèle définit la passe avant qui produit les logits ; tout ce qui consiste à transformer ces logits en un modèle entraîné vit un étage au-dessus, dans le code qui appelle le modèle à répétition et applique autour de lui le dispositif de l'étape 4.

### Une autre base de code, les mêmes objets mathématiques

llama.cpp, construit en C plutôt qu'en Python et PyTorch, exprime les mêmes opérations, l'attention, l'encodage positionnel (couramment rotatif), la normalisation (couramment RMSNorm, une variante simplifiée de la layer norm de la leçon 5) et un bloc feed-forward (couramment avec une activation SwiGLU), non pas sous forme de classes `nn.Module` avec une méthode `forward`, mais sous forme d'appels explicites qui construisent un graphe de calcul dans `ggml`, la bibliothèque de tenseurs qui se trouve en dessous. Le style des appels de construction de graphe et celui des classes avec méthode forward n'ont rien de commun à l'écran, mais ils calculent les mêmes objets mathématiques que cet espace de travail a dérivés à partir de tenseurs bruts ; la différence réside entièrement dans la façon dont le graphe de calcul est construit et exécuté, pas dans ce qu'il calcule.

## Pratique

1. ▢ Associez chacun de ces noms du vrai code à la leçon qui a dérivé le concept qu'il implémente : `wte`, `wpe`, un buffer de masque triangulaire inférieur enregistré, `lm_head` lié aux poids de `wte`, une `ModuleList` de blocs.

<details markdown="1"><summary>Vérifier</summary>

`wte` (word token embedding) : l'embedding d'entrée de la leçon 8. `wpe` (word position embedding) : l'encodage positionnel de la leçon 4 (ici, une table apprise plutôt que sinusoïdale). Le buffer de masque enregistré : le masquage causal de la leçon 3. `lm_head` lié à `wte` : le weight tying de la leçon 8. La `ModuleList` de blocs : l'empilement de la leçon 7.

</details>

2. ▢ Nommez les trois petits écarts courants par rapport à l'article d'origine que l'on trouve dans la plupart des implémentations réelles modernes, et dites à l'alternative de quelle leçon chacun correspond.

<details markdown="1"><summary>Vérifier</summary>

Des embeddings de position appris ou rotatifs au lieu de sinusoïdaux (l'alternative apprise de la leçon 4, ou une variante supplémentaire comme le rotatif). GELU au lieu de ReLU dans le bloc feed-forward (la non-linéarité de la leçon 6, remplacée par une autre fonction, avec la même forme d'extension puis de contraction). Un placement pre-norm au lieu de post-norm (l'alternative pre-norm de la leçon 5 au choix de l'article d'origine).

</details>

3. ▢ Pourquoi le masque causal apparaît-il dans le vrai code comme un buffer enregistré, précalculé, plutôt que d'être reconstruit à chaque appel de forward ?

<details markdown="1"><summary>Indice</summary>

Demandez-vous de quoi dépend réellement le masque.

</details>

<details markdown="1"><summary>Vérifier</summary>

Le masque ne dépend que de la longueur de séquence, jamais des valeurs d'entrée réelles, donc il peut être calculé une fois (couramment à la longueur de séquence maximale que le modèle prend en charge) et réutilisé ou découpé à chaque appel de forward, au lieu d'être reconstruit de zéro à chaque fois. C'est un pur choix d'efficacité ; le mécanisme de masquage lui-même, ajouté aux scores avant le softmax, est inchangé par rapport à la leçon 3.

</details>

4. ▢ En quoi l'approche de llama.cpp pour calculer l'attention et le bloc feed-forward diffère-t-elle mécaniquement de la passe avant d'un `nn.Module` de PyTorch, tout en calculant les mêmes opérations mathématiques sous-jacentes ?

<details markdown="1"><summary>Vérifier</summary>

llama.cpp construit un graphe de calcul explicite dans `ggml` par des appels de fonctions en C, au lieu de définir une classe avec une méthode `forward` que PyTorch trace automatiquement pendant l'exécution. Le style de construction du graphe paraît entièrement différent à l'écran, mais les opérations qu'il construit, l'attention, l'encodage positionnel, la normalisation, le bloc feed-forward, sont les mêmes objets mathématiques que cet espace de travail a dérivés à partir de tenseurs bruts.

</details>

5. ▢ Quelle affirmation est vraie de la lecture du code d'un vrai modèle après avoir dérivé l'architecture à partir de zéro ?

    - a) Les vrais modèles de production implémentent une architecture entièrement différente de celle que dérivent l'article d'origine et cet espace de travail
    - b) Les mêmes pièces apparaissent sous des noms différents, avec une poignée de petits écarts standard (schéma d'embedding de position, fonction d'activation, placement de la norme) qu'il vaut mieux reconnaître que traiter comme des nouveautés
    - c) Le code d'entraînement (loss, passe arrière, optimiseur) fait toujours partie de la définition de la classe du modèle
    - d) llama.cpp calcule des opérations mathématiques fondamentalement différentes de celles d'une implémentation PyTorch, puisqu'il est écrit en C

<details markdown="1"><summary>Vérifier</summary>

**b)** C'est exactement la traduction qu'enseigne cette leçon. (a) est faux : l'architecture sous-jacente est la même, simplement nommée et configurée différemment. (c) est faux : le code d'entraînement vit dans un script ou un utilitaire d'entraînement distinct, pas dans la classe du modèle elle-même. (d) est faux : les opérations sont mathématiquement identiques ; seule diffère la façon dont le graphe de calcul est construit et exprimé.

</details>

## Exercices en situation réelle

- [ ] Ouvrez l'implémentation d'un modèle de style GPT-2 dans la bibliothèque `transformers` et trouvez sa classe d'attention, son masque causal et ses noms `wte`/`wpe`/`lm_head`, en associant chacun à la leçon qui l'a dérivé.
- [ ] Vérifiez si ce même modèle utilise le pre-norm ou le post-norm, et GELU ou ReLU, et notez lequel est lequel par rapport à la liste d'écarts courants de cette leçon.
- [ ] Demain : trouvez le script d'entraînement (ou l'usage de `Trainer`) d'un modèle auquel vous avez accès, et repérez son calcul de la loss, son appel à `.backward()` et son pas d'optimiseur.

## Pour aller plus loin

- [Dépôt : transformers, Hugging Face](https://github.com/huggingface/transformers)
- [Dépôt : nanoGPT, Karpathy](https://github.com/karpathy/nanoGPT)
- [Ressources](../RESOURCES.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
