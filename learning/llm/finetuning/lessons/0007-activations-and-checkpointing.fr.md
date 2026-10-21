---
title: "7. Activations, taille de batch et checkpointing"
description: "Pourquoi un run avec adapter manque quand même de mémoire"
type: lesson
---

# Leçon 7. Activations, taille de batch et checkpointing

**Lien avec la mission :** Les adapters suppriment le coût de l'optimizer mais pas celui des activations, ce qui explique qu'un run LoRA puisse quand même manquer de mémoire. C'est la partie qui surprend les gens.
**Source primaire :** [Article : "Training Deep Nets with Sublinear Memory Cost", Chen et al., arXiv:1604.06174](https://arxiv.org/abs/1604.06174)
**Prérequis :** [Leçon 6](0006-gradients-and-optimizer-state.md)

## Échauffement

1. ▢ Octets par paramètre entraînable sous AdamW, en précision mixte ?

<details markdown="1"><summary>Vérifier</summary>

Seize octets : deux pour les poids en bf16, quatre pour la copie maître en fp32, deux pour le gradient en bf16, et quatre chacun pour les deux moments.

</details>

2. ▢ Octets par paramètre gelé ?

<details markdown="1"><summary>Vérifier</summary>

Deux, en bf16, pour la seule valeur du poids. Pas de gradient, pas de moments, pas de copie maître.

</details>

3. ▢ Pourquoi ne peut-on pas simplement abandonner les moments d'AdamW pour les transformers ?

<details markdown="1"><summary>Vérifier</summary>

Les amplitudes de gradient varient énormément d'un paramètre à l'autre dans un transformer, et le second moment fournit la mise à l'échelle du pas par paramètre qu'un learning rate global unique ne peut pas fournir.

</details>

## À savoir

Les gradients et l'état de l'optimizer évoluent avec le **nombre de paramètres**. Les activations évoluent avec la **batch size et la longueur de séquence**, et sont presque indépendantes du nombre de paramètres entraînables. Geler le base model n'aide ici en rien.

### Pourquoi les activations existent

La passe arrière a besoin de l'entrée de chaque couche pour calculer le gradient de cette couche. La passe avant conserve donc ses résultats intermédiaires au lieu de les jeter. Chaque tenseur conservé vaut environ :

```text
batch_size × sequence_length × hidden_size × bytes_per_element
```

par tenseur, et un bloc de transformer en contient une douzaine environ : après chaque normalisation, chaque projection, la sortie de l'attention, l'intermédiaire du MLP à sa dimension plus large, et ainsi de suite. Multipliez par le nombre de couches.

Un chiffre de travail approximatif pour un bloc de transformer en bf16, en comptant les tenseurs notables :

```text
activations ≈ n_layers × batch × seq_len × hidden × ~20 bytes
```

Considérez la constante comme un point de départ à mesurer, pas comme une loi, parce qu'elle varie avec l'implémentation de l'attention, la fonction d'activation, et la fusion éventuelle d'opérations par le framework. Ce qui compte, c'est la *forme* de la formule.

### Les conséquences de la forme

**Linéaire en batch size.** Doublez le batch, doublez la mémoire des activations. C'est le réglage auquel on pense en premier, et la gradient accumulation (leçon 4) retrouve la batch size effective sans coût en mémoire.

**Linéaire en longueur de séquence** pour les activations stockées, et quadratique pour la matrice des scores d'attention, sauf si vous utilisez un kernel d'attention économe en mémoire. Les implémentations modernes comme FlashAttention évitent de matérialiser la matrice complète `seq_len × seq_len`, ce qui supprime le terme quadratique. Si vous subissez encore une explosion quadratique sur les longues séquences, le correctif est l'implémentation de l'attention, pas la batch size.

Calculé pour un modèle de 24 couches de taille cachée 2048, batch 4, longueur de séquence 2048 :

```text
24 × 4 × 2048 × 2048 × 20 bytes ≈ 8.0 GB
```

Huit gigaoctets d'activations, contre environ 2.2 Go de poids gelés en bf16 et quelques dizaines de mégaoctets d'état d'adapter. **Les activations sont maintenant le coût dominant.** C'est le profil mémoire d'un run typique avec adapter, et c'est l'inverse du profil du full fine-tuning vu à la leçon 6.

### Gradient checkpointing

L'échange qui règle le problème : ne pas stocker la plupart des activations. En stocker quelques-unes, et recalculer le reste pendant la passe arrière.

On garde l'entrée de chaque bloc (un *checkpoint*), on jette tout ce qu'il y a à l'intérieur, et quand la passe arrière atteint ce bloc, on relance sa passe avant pour régénérer ce qui est nécessaire. Le stockage passe d'à peu près linéaire en profondeur à à peu près la racine carrée de celle-ci, au prix d'environ une passe avant supplémentaire, couramment de 20 à 40 % de ralentissement par pas.

![Deux courbes en fonction de la profondeur. Sans checkpointing, les activations stockées montent en ligne droite avec le nombre de couches. Avec le checkpointing, elles suivent la racine carrée et s'aplatissent presque aussitôt. À 24 couches, les deux sont séparées d'un facteur cinq environ.](images/linear-against-square-root.svg)

La forme de cet échange explique qu'il soit presque une valeur par défaut. Une droite et une racine carrée sont à peine distinctes à deux ou trois couches, donc sur un modèle jouet la technique semble inutile ; l'écart est d'un facteur cinq environ aux 24 couches de l'exemple calculé et continue de se creuser, et le prix reste une passe avant supplémentaire, quelle que soit la profondeur du modèle.

```python
model.gradient_checkpointing_enable()
model.config.use_cache = False  # incompatible with checkpointing during training
```

Cette seconde ligne compte. Le KV cache existe pour accélérer la *génération* autorégressive et n'a aucun rôle à l'entraînement ; le laisser activé avec le checkpointing produit des avertissements dans le meilleur cas et de la mémoire gaspillée dans le pire.

**Le gradient checkpointing est presque une valeur par défaut pour le fine-tuning avec adapter.** Il rachète le plus gros coût unique du profil ci-dessus, et le ralentissement en vaut presque toujours la peine.

### Remplissage et packing

Chaque séquence d'un batch est complétée par du remplissage jusqu'à la taille de la plus longue du batch, et le remplissage consomme de la mémoire d'activations sans rien apporter. Deux remèdes :

- **Regroupement par longueur.** Regrouper dans un même batch des séquences de tailles voisines, pour qu'il faille moins de remplissage.
- **Packing.** Concaténer des exemples courts en séquences de pleine longueur, ce qui élimine presque entièrement le remplissage.

Le packing est un vrai gain d'efficacité sur les datasets d'exemples courts, et il a une exigence de correction : les exemples empaquetés ensemble ne doivent pas porter leur attention au-delà de leurs frontières. Les implémentations gèrent cela avec des réinitialisations de position et une attention qui tient compte des frontières. Si vous activez le packing, vérifiez que votre masquage de la loss y survit : une séquence empaquetée doit garder ses labels `-100` intacts, sinon la loss sur la complétion seule devient discrètement une loss sur toute la séquence.

### L'ordre dans lequel essayer les choses

Quand un run ne tient pas, dans l'ordre de ce à quoi vous renoncez :

1. Activer le gradient checkpointing, qui ne coûte que du temps
2. Réduire la batch size par appareil et augmenter la gradient accumulation, ce qui coûte un peu de temps et ne change rien statistiquement
3. Réduire la longueur de séquence, ce qui change la tâche, donc examinez d'abord votre distribution des longueurs en tokens
4. Quantifier le base model, ce qui relève de l'étape 4 et coûte un peu de qualité
5. Réduire le rank de l'adapter, ce qui coûte de la capacité et économise le moins de toutes les options ici

Ce dernier point mérite qu'on s'y attarde. Le rank est le réglage auquel on pense en premier et c'est presque le *moins* efficace, parce que les paramètres de l'adapter ne sont qu'une infime fraction du total. Diviser par deux le rank d'un adapter de 4M paramètres économise 32 Mo.

## Pratique

1. ▢ Lesquels de ces éléments évoluent avec le nombre de paramètres entraînables, et lesquels avec le batch et la longueur de séquence : gradients, activations, moments de l'optimizer, poids gelés ?

<details markdown="1"><summary>Vérifier</summary>

Nombre de paramètres entraînables : gradients, moments de l'optimizer. Taille du modèle seulement : poids gelés. Batch et longueur de séquence : activations.

Que les activations relèvent d'un tout autre axe est le sujet de cette leçon, et la raison pour laquelle les adapters ne les résolvent pas.

</details>

2. ▢ Estimez la mémoire des activations pour un modèle de 32 couches, taille cachée 4096, batch 2, longueur de séquence 4096, bf16.

<details markdown="1"><summary>Vérifier</summary>

32 × 2 × 4096 × 4096 × 20 ≈ 21 Go.

Énorme par rapport à un base model 7B gelé de 14 Go. Avec le gradient checkpointing, cela baisse d'environ un ordre de grandeur, ce qui rend le run possible sur un seul appareil.

</details>

3. ▢ Votre run LoRA manque de mémoire. Un collègue suggère de faire passer le rank de 64 à 8. Évaluez.

<details markdown="1"><summary>Vérifier</summary>

Cela n'aidera guère. Passer du rank 64 au rank 8 sur un modèle 7B économise de l'ordre d'une centaine de mégaoctets d'état d'adapter et de gradients, face à des activations qui se mesurent en gigaoctets.

Activez d'abord le gradient checkpointing et réduisez la batch size par appareil. Le rank est une décision de capacité, et la dépenser sur une mémoire dont vous n'étiez pas à court est un mauvais échange.

</details>

4. ▢ Pourquoi `use_cache` doit-il être désactivé quand le gradient checkpointing est activé ?

<details markdown="1"><summary>Vérifier</summary>

Le KV cache stocke les keys et values passées pour éviter de les recalculer pendant la génération autorégressive. L'entraînement fait une seule passe avant sur une séquence complète, donc le cache n'apporte aucun bénéfice, et il entre en conflit avec la stratégie de recalcul du checkpointing tout en consommant de la mémoire.

</details>

5. ▢ Qu'échange le gradient checkpointing, dans les deux sens ?

<details markdown="1"><summary>Vérifier</summary>

Il échange du calcul contre de la mémoire : le stockage des activations passe d'à peu près linéaire en profondeur à à peu près sa racine carrée, en échange d'environ une passe avant supplémentaire par pas, typiquement 20 à 40 % de ralentissement.

</details>

6. ▢ Vous activez le packing et votre modèle se met à produire des réponses à des questions que personne n'a posées. Qu'est-ce qui a mal tourné ?

<details markdown="1"><summary>Vérifier</summary>

Très probablement le masque de la loss n'a pas survécu au packing, donc les tokens du prompt sont maintenant entraînés, ou bien les exemples portent leur attention au-delà de leurs frontières et apprennent qu'un texte sans rapport suit une réponse.

Vérifiez que les labels `-100` sont préservés à travers l'étape de packing et que l'implémentation tient compte des frontières. Le packing est une optimisation d'efficacité avec une précondition de correction.

</details>

## Exercices en situation réelle

- [ ] Exécutez un pas d'entraînement à batch 1, puis batch 2, puis batch 4, en notant la mémoire de pointe à chaque fois. Confirmez que la relation est linéaire.
- [ ] Activez le gradient checkpointing et recommencez. Notez à la fois la mémoire économisée et les secondes par pas perdues, et décidez si vous accepteriez cet échange.
- [ ] Demain : mesurez la distribution des longueurs en tokens d'un vrai dataset avec le vrai tokenizer. Trouvez le 95e percentile. C'est lui, et non le maximum, qui est votre longueur de séquence.

## Pour aller plus loin

- [Article : "Training Deep Nets with Sublinear Memory Cost", Chen et al., arXiv:1604.06174](https://arxiv.org/abs/1604.06174)
- [Article : "FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness", Dao et al., arXiv:2205.14135](https://arxiv.org/abs/2205.14135)
- [Doc : Methods and tools for efficient training on a single GPU, Hugging Face](https://huggingface.co/docs/transformers/main/en/perf_train_gpu_one)
- [Budget mémoire](../reference/memory-budget.md) : désormais assez complet pour être utilisé

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
