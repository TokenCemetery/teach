---
title: "6. Gradients et état de l'optimizer"
description: "Seize octets par paramètre entraînable, deux par paramètre gelé"
type: lesson
---

# Leçon 6. Gradients et état de l'optimizer

**Lien avec la mission :** C'est l'argument en faveur des adapters. Une fois que vous savez dériver le chiffre de seize octets par paramètre, LoRA cesse d'être une astuce et devient la réponse évidente.
**Source primaire :** [Article : "ZeRO: Memory Optimizations Toward Training Trillion Parameter Models", Rajbhandari et al., arXiv:1910.02054](https://arxiv.org/abs/1910.02054)
**Prérequis :** [Leçon 4](0004-what-training-changes.md), [Leçon 5](0005-counting-parameters-and-bytes.md)

## Échauffement

1. ▢ Poids d'un modèle 7B en bf16 : combien de gigaoctets ?

<details markdown="1"><summary>Vérifier</summary>

Environ 14 Go. Deux octets par paramètre, donc les gigaoctets en bf16 valent à peu près le double des milliards de paramètres.

</details>

2. ▢ Quels deux tenseurs AdamW conserve-t-il par paramètre entraînable ?

<details markdown="1"><summary>Vérifier</summary>

Une moyenne mobile des gradients et une moyenne mobile des gradients au carré, les premier et second moments. Chacun a la forme du paramètre.

</details>

3. ▢ Pourquoi bf16 l'emporte-t-il sur fp16 pour l'entraînement ?

<details markdown="1"><summary>Vérifier</summary>

Sa plage d'exposant correspond à celle de fp32, donc les valeurs ne débordent pas vers l'infini. L'erreur d'arrondi est supportable ; les `NaN` ne le sont pas.

</details>

## À savoir

Tout ce que coûte un paramètre entraînable, par paramètre :

| Catégorie | Entraînement en fp32 | Précision mixte (calcul en bf16, maître en fp32) |
|---|---|---|
| Poids | 4 | 2 (bf16) + 4 (copie maître en fp32) |
| Gradients | 4 | 2 |
| Premier moment d'AdamW | 4 | 4 |
| Second moment d'AdamW | 4 | 4 |
| **Total** | **16 octets** | **16 octets** |

![Deux barres d'octets par paramètre entraînable, toutes deux longues de seize octets. En fp32, les seize octets se répartissent en quatre chacun pour les poids, les gradients et les deux moments. En précision mixte, les poids font deux octets de bf16 plus une copie maître de quatre octets, les gradients font deux octets, et les deux moments restent à quatre.](images/mixed-precision-same-total.svg)

La colonne de droite est ce qui surprend les gens. **La précision mixte ne réduit pas le total.**

Les deux barres atteignent la même marque, et c'est toute la découverte. Les deux morceaux accentués sont les tenseurs qui ont réellement été divisés par deux, soit quatre octets économisés à eux deux, et la copie maître placée à côté du premier remet aussitôt quatre octets. Tout ce qui se trouve à sa droite n'a jamais bougé. La précision mixte divise par deux les tenseurs de poids et de gradients, puis rajoute une copie maître en fp32 des poids, parce qu'accumuler de minuscules mises à jour dans une valeur bf16 les perd silencieusement. Les moments de l'optimizer restent en fp32 pour la même raison. Le gain de la précision mixte est le débit de calcul arithmétique, pas la mémoire.

Donc : **16 octets par paramètre entraînable**, avant la moindre activation.

### Ce que cela signifie

```text
1.5B trainable × 16 bytes = 24 GB
7B   trainable × 16 bytes = 112 GB
70B  trainable × 16 bytes = 1120 GB
```

Le full fine-tuning d'un modèle 7B demande 112 Go d'état d'optimizer et de poids à lui seul, puis les activations en plus. C'est le territoire du multi-GPU pour un modèle dont les poids pèsent 14 Go. L'écart entre « le modèle tient » et « l'entraînement du modèle tient » est un facteur huit, et il est entièrement dû aux gradients et à l'état de l'optimizer.

### L'échappatoire

Regardez de nouveau le tableau et notez par quoi les 16 octets sont multipliés : le nombre de paramètres **entraînables**, pas le nombre total de paramètres. Les paramètres gelés coûtent 2 octets chacun, pour leurs poids, et rien de plus. Pas de gradient. Pas de moments.

C'est tout l'argument en faveur des adapters :

```text
frozen parameter   = 2 bytes  (bf16 weights only)
trainable parameter = 16 bytes (weights + master + grad + 2 moments)
```

Gelez le base model, ajoutez quelques millions de paramètres entraînables, et le second terme disparaît presque. Calculé pour un base model 7B avec 4M paramètres d'adapter entraînables :

```text
frozen base    7B  × 2  = 14.0 GB
trainable      4M  × 16 = 0.064 GB
```

L'état d'optimizer de l'adapter fait 64 Mo. Il est devenu une erreur d'arrondi face aux poids du base model, et les poids du base model sont la seule partie que vous pouvez attaquer séparément, avec la quantification, à l'étape 4.

### Mesures partielles, et pourquoi elles ne suffisent pas

Avant l'existence des adapters, on réduisait ce coût par d'autres moyens. Ils sont tous toujours disponibles et tous toujours bornés :

| Technique | Ce qu'elle économise | Ce qu'elle coûte |
|---|---|---|
| Optimizer 8 bits | Moments à 1 octet au lieu de 4 : 16 → 10 octets | Léger risque sur la qualité ; toujours linéaire en nombre de paramètres entraînables |
| SGD avec momentum | Un moment au lieu de deux : 16 → 12 octets | Convergence nettement moins bonne pour les transformers |
| Sharding de l'optimizer (ZeRO) | Répartit l'état sur N appareils | Demande N appareils et une interconnexion rapide |
| Offload vers le CPU | Sort l'état de l'accélérateur | Limité par la bande passante ; pas bien plus lents |

Chacune de ces techniques met la constante à l'échelle. Aucune ne change le fait que le coût est proportionnel au nombre de paramètres entraînables. Les adapters s'attaquent au multiplicateur, ce qui explique qu'ils gagnent de plusieurs ordres de grandeur plutôt que de simples facteurs.

### Pourquoi on ne peut pas simplement abandonner les moments

Une question raisonnable : si les deux moments d'AdamW représentent les deux tiers du coût, pourquoi ne pas utiliser du SGD simple ? Parce que l'entraînement des transformers dépend de la mise à l'échelle du pas par paramètre d'Adam. Les amplitudes de gradient varient énormément d'un paramètre à l'autre dans un transformer, et un learning rate global unique les sert mal. Le second moment est ce qui permet à chaque paramètre de faire un pas de taille appropriée. C'est empirique, constant, et ce n'est pas un problème de réglage qu'on peut faire disparaître d'un souhait.

## Pratique

1. ▢ Dérivez la mémoire nécessaire au full fine-tuning d'un modèle 3B avec AdamW en précision mixte, activations exclues.

<details markdown="1"><summary>Vérifier</summary>

16 octets par paramètre entraînable × 3e9 = 48 Go.

Détail : 6 Go de poids en bf16 + 12 Go de maître en fp32 + 6 Go de gradients en bf16 + 12 Go de premier moment + 12 Go de second moment = 48 Go.

</details>

2. ▢ Pourquoi la précision mixte ne réduit-elle pas la mémoire totale d'entraînement ?

<details markdown="1"><summary>Vérifier</summary>

Elle divise par deux les poids et les gradients mais ajoute une copie maître des poids en fp32, et laisse les deux moments de l'optimizer en fp32. Les économies et l'ajout s'annulent, et l'on retombe sur 16 octets.

La copie maître n'est pas optionnelle : ajouter à répétition une très petite mise à jour à une valeur bf16 s'arrondit à aucun changement du tout, donc la mise à jour est perdue.

</details>

3. ▢ Un base model 7B est gelé en bf16 et vous entraînez un adapter de 20M paramètres. Total, activations exclues ?

<details markdown="1"><summary>Vérifier</summary>

14 Go pour le base model gelé (7e9 × 2) plus 0.32 Go pour l'adapter (2e7 × 16), soit environ 14.3 Go.

Face aux 112 Go du full fine-tuning : une réduction de 7.8×, et presque tout ce qui reste est le base model gelé. L'étape 4 s'attaque à ce reste.

</details>

4. ▢ Quel changement réduit le plus la mémoire de l'optimizer pour un modèle donné ?

    - a) Passer l'optimizer d'AdamW à SGD
    - b) Passer la précision de calcul en bf16
    - c) Geler le base model et entraîner un adapter
    - d) Passer au masquage de la loss sur la complétion seule

<details markdown="1"><summary>Vérifier</summary>

**c)** Geler le base model et entraîner un adapter.

(a) retire un moment sur deux, ce qui économise un quart. (b) n'économise rien au total, comme vu plus haut. (d) change les positions qui contribuent à la loss, pas le nombre de paramètres qui ont un état. Seul (c) s'attaque au nombre de paramètres entraînables, qui est le multiplicateur de tout.

</details>

5. ▢ Quelqu'un propose un optimizer 8 bits pour pouvoir faire le full fine-tuning d'un modèle 70B sur un seul accélérateur de 80 Go. Faites l'arithmétique et répondez.

<details markdown="1"><summary>Vérifier</summary>

Des moments en 8 bits donnent 2 + 4 + 2 + 1 + 1 = 10 octets par paramètre. 70e9 × 10 = 700 Go. Toujours près de neuf fois un appareil de 80 Go, avant les activations.

La technique est réelle et utile ; le plan est faux d'un ordre de grandeur. C'est la valeur de faire l'arithmétique avant l'expérience.

</details>

6. ▢ En une phrase : pourquoi les paramètres gelés coûtent-ils tellement moins que les paramètres entraînables ?

<details markdown="1"><summary>Vérifier</summary>

Un paramètre gelé n'a besoin que de sa propre valeur stockée pour la passe avant, alors qu'un paramètre entraînable demande en plus un gradient, deux moments d'optimizer et une copie maître en haute précision : huit fois plus.

</details>

## Exercices en situation réelle

- [ ] Reconstruisez de mémoire, sur papier, le tableau des 16 octets. Puis calculez la mémoire totale d'entraînement pour trois tailles de modèle qui vous importent vraiment.
- [ ] Chargez un petit modèle, exécutez un pas d'entraînement avec AdamW sur tous les paramètres, et notez la mémoire de pointe. Comparez à votre prédiction.
- [ ] Demain : recommencez avec le base model gelé et seul un petit adapter entraînable. Le rapport que vous mesurez est l'argument de l'étape 3.

## Pour aller plus loin

- [Article : "ZeRO: Memory Optimizations Toward Training Trillion Parameter Models", Rajbhandari et al., arXiv:1910.02054](https://arxiv.org/abs/1910.02054) : le décompte canonique de ces catégories
- [Article : "8-bit Optimizers via Block-wise Quantization", Dettmers et al., arXiv:2110.02861](https://arxiv.org/abs/2110.02861)
- [Budget mémoire](../reference/memory-budget.md)
- [Leçon 8. L'idée du faible rang](0008-the-low-rank-idea.md) : la réponse à cette leçon

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
