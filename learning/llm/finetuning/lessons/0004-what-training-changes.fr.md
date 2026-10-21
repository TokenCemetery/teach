---
title: "4. Ce que l'entraînement change réellement"
description: "Les quatre opérations d'un pas d'entraînement"
type: lesson
---

# Leçon 4. Ce que l'entraînement change réellement

**Lien avec la mission :** Chaque argument sur la mémoire, chaque hyperparamètre et chaque mode de défaillance de cet espace de travail découle de ce que fait un pas d'entraînement.
**Source primaire :** [Article : "Decoupled Weight Decay Regularization" (AdamW), Loshchilov & Hutter, arXiv:1711.05101](https://arxiv.org/abs/1711.05101)
**Prérequis :** [Leçon 1](0001-what-a-base-model-is.md), [Leçon 3](0003-tokenizers-and-chat-templates.md)

## Échauffement

1. ▢ Pourquoi l'entraînement et le service doivent-ils utiliser exactement le même chat template ?

<details markdown="1"><summary>Vérifier</summary>

Le gabarit définit la distribution de tokens sur laquelle les poids sont ajustés. Entraîner sur un rendu et servir un autre, c'est déployer un problème différent, et la loss ne le révélera pas.

</details>

2. ▢ Que fait une connexion résiduelle autour de chaque sous-couche ?

<details markdown="1"><summary>Vérifier</summary>

Elle rajoute la sortie de la sous-couche au flux courant au lieu de le remplacer, si bien que chaque bloc apporte un incrément plutôt qu'une réécriture.

</details>

3. ▢ Nommez les deux projections du MLP qui élargissent et rétrécissent la dimension cachée.

<details markdown="1"><summary>Vérifier</summary>

`up_proj` élargit jusqu'à la dimension intermédiaire, `down_proj` revient à la dimension cachée. `gate_proj` produit la porte appliquée entre les deux.

</details>

## À savoir

Un pas d'entraînement, c'est quatre opérations. Chaque coût mémoire de l'étape 2 est l'une de ces quatre opérations qui retient quelque chose en mémoire.

**1. Passe avant.** Faire passer un batch de séquences dans le modèle et calculer la loss. Pour rendre l'étape 3 possible, les résultats intermédiaires de chaque couche, les **activations**, doivent être conservés plutôt que jetés. C'est pourquoi l'entraînement demande bien plus de mémoire que l'inférence.

**2. Loss.** L'entropie croisée entre la distribution prédite et le token suivant réel, moyennée sur chaque position qui compte. Quelles positions comptent est votre choix, et c'est important :

- La **loss sur toute la séquence** note chaque token, y compris le prompt de l'utilisateur. Le modèle apprend à prédire les prompts autant que les réponses.
- La **loss sur la complétion seule** masque les tokens du prompt et ne note que la réponse de l'assistant.

Le masquage se fait en mettant le label à `-100` aux positions à ignorer, une convention que la fonction de loss lit comme « sauter ». Pour l'instruction tuning, la complétion seule est généralement ce que l'on veut : vous enseignez des réponses, pas au modèle à imaginer des questions d'utilisateurs.

**3. Passe arrière.** Remonter dans le graphe en appliquant la règle de dérivation en chaîne, ce qui produit pour chaque paramètre entraînable un **gradient** : la direction et l'amplitude dont ce paramètre devrait changer pour réduire la loss. Un gradient par paramètre entraînable, de la même forme que le paramètre lui-même. Retenez-le ; c'est la moitié de la leçon 6.

**4. Pas de l'optimizer.** Mettre à jour les paramètres à partir des gradients. La descente de gradient simple serait `w ← w − lr · g`. Personne ne l'utilise. **AdamW** maintient deux moyennes mobiles par paramètre :

| État | Suit | Effet |
|---|---|---|
| Premier moment | La moyenne des gradients récents | Momentum, lisse les directions bruitées |
| Second moment | La moyenne des gradients récents au carré | Mise à l'échelle du pas par paramètre |

Deux tenseurs supplémentaires, chacun de la taille des paramètres. C'est l'autre moitié de la leçon 6, et c'est la raison pour laquelle le full fine-tuning est si coûteux.

### Learning rate et schedule

Le learning rate met le pas à l'échelle. Trop élevé, la mise à jour dépasse la cible et détruit la structure préentraînée. C'est à cela que ressemble mécaniquement l'oubli catastrophique. Trop bas, rien ne bouge.

Deux raffinements standard :

- **Warm-up :** démarrer près de zéro et monter progressivement sur les quelques centaines de premiers pas, pour que les premiers gradients bruités ne ruinent pas les poids.
- **Décroissance :** réduire le taux au fil de l'entraînement, typiquement sur une courbe cosinus, pour que les derniers pas affinent au lieu de se débattre.

Le fine-tuning avec adapter tolère des learning rates supérieurs d'un à deux ordres de grandeur à ceux du full fine-tuning, couramment autour de `1e-4` à `2e-4` plutôt que `1e-5`. La leçon 9 explique pourquoi.

### Batch size, réelle et effective

Les gradients sont moyennés sur un batch. Des batchs plus gros donnent des gradients moins bruités mais coûtent proportionnellement plus de mémoire d'activations. La **gradient accumulation** achète la moyenne sans la mémoire : exécuter plusieurs petits batchs, sommer les gradients, ne faire le pas qu'une fois.

```text
effective batch size = per_device_batch_size × gradient_accumulation_steps × num_devices
```

Rapportez et raisonnez sur le chiffre effectif. Un run avec une batch size de 1 et 16 pas d'accumulation est un run à batch 16, et le comparer à un run à batch 1 comme s'ils étaient équivalents est une manière courante de tirer une fausse conclusion.

### Un epoch n'est pas une unité d'apprentissage

Un epoch est un passage sur le dataset. Sur un petit dataset d'instructions, deux ou trois epochs est une plage typique et au-delà on mémorise généralement. C'est le nombre de *pas* que voit l'optimizer, et les pas dépendent ensemble de la taille du dataset et de la batch size effective, donc « 3 epochs » veut dire quelque chose de complètement différent sur 500 exemples et sur 500 000.

## Pratique

1. ▢ Pourquoi l'entraînement demande-t-il beaucoup plus de mémoire que l'inférence, à batch size et longueur de séquence identiques ?

<details markdown="1"><summary>Vérifier</summary>

L'entraînement doit conserver les activations de la passe avant pour que la passe arrière puisse calculer les gradients, et il doit stocker les gradients et l'état de l'optimizer. L'inférence jette les résultats intermédiaires de chaque couche dès que la couche suivante les a consommés.

</details>

2. ▢ Vous faites un fine-tuning sur des paires question-réponse. La loss doit-elle être calculée sur toute la séquence ou seulement sur la réponse ? Donnez la conséquence du mauvais choix.

<details markdown="1"><summary>Vérifier</summary>

Seulement sur la réponse, dans la plupart des cas. Noter aussi le prompt dépense de la capacité à apprendre au modèle à générer des questions d'utilisateurs plausibles, ce qui n'est pas la tâche, et dilue le signal de gradient sur la partie qui vous importe.

L'exception, c'est quand les prompts sont très stylisés et que vous voulez que le modèle intériorise de façon générale le langage du domaine. Décidez délibérément ; ne laissez pas la valeur par défaut décider à votre place.

</details>

3. ▢ AdamW stocke combien de tenseurs supplémentaires par paramètre entraînable, et lesquels ?

<details markdown="1"><summary>Vérifier</summary>

Deux : une moyenne mobile des gradients (premier moment) et une moyenne mobile des gradients au carré (second moment). Chacun a la même forme que le paramètre.

Plus le gradient lui-même, qui est un troisième tenseur de même forme mais n'est pas de l'état d'optimizer. Garder ces trois éléments bien distincts est exactement ce que la leçon 6 vous demande.

</details>

4. ▢ Run A : batch size 8, accumulation 1. Run B : batch size 1, accumulation 8. Mêmes données, même seed, même learning rate. Les pas de l'optimizer sont-ils équivalents ?

<details markdown="1"><summary>Vérifier</summary>

Effectivement oui : les deux moyennent les gradients sur 8 exemples avant de faire le pas, donc la mise à jour est essentiellement la même, et B utilise bien moins de mémoire d'activations. De petites différences subsistent à cause de la façon dont le remplissage et la normalisation par batch interagissent.

La gradient accumulation est la manière standard d'obtenir un grand batch effectif avec une mémoire contrainte. Ce qui n'est *pas* équivalent, c'est de comparer B à un véritable run à batch 1, qui fait huit fois plus de pas sur des gradients plus bruités.

</details>

5. ▢ Un collègue règle le learning rate d'un run LoRA à `1e-5` « parce que c'est ce qu'utilise le full fine-tuning ». Qu'attendez-vous, et que dites-vous ?

<details markdown="1"><summary>Vérifier</summary>

Attendez-vous à du sous-apprentissage : la loss baisse lentement, le modèle change à peine, et le run ressemble à une preuve que la méthode ne fonctionne pas.

Les adapters partent d'une contribution nulle et contiennent une infime fraction des paramètres, donc il leur faut un taux bien plus grand pour bouger tout court, généralement `1e-4` à `2e-4`. Importer un learning rate de full fine-tuning est l'une des raisons les plus courantes pour lesquelles un premier run LoRA déçoit.

</details>

6. ▢ Pourquoi le warm-up est-il plus qu'une superstition ?

<details markdown="1"><summary>Vérifier</summary>

Au début de l'entraînement, l'estimation du second moment d'AdamW est construite à partir de très peu d'échantillons, donc sa mise à l'échelle par paramètre n'est pas fiable et peut produire des pas énormes. Monter progressivement le learning rate limite les dégâts que ces premiers pas peuvent causer aux poids préentraînés.

</details>

## Exercices en situation réelle

- [ ] Écrivez de mémoire les quatre opérations d'un pas d'entraînement, puis vérifiez-les avec cette leçon.
- [ ] Prenez n'importe quel script de fine-tuning publié et identifiez sa batch size effective, son learning rate, son warm-up et son schedule. Notez les quatre valeurs.
- [ ] Demain : trouvez une configuration d'entraînement où vous n'êtes pas d'accord avec l'une de ces quatre valeurs, et écrivez une phrase sur ce que vous changeriez et pourquoi.

## Pour aller plus loin

- [Article : "Decoupled Weight Decay Regularization" (AdamW), Loshchilov & Hutter, arXiv:1711.05101](https://arxiv.org/abs/1711.05101)
- [Article : "Adam: A Method for Stochastic Optimization", Kingma & Ba, arXiv:1412.6980](https://arxiv.org/abs/1412.6980)
- [Blog : "A Recipe for Training Neural Networks", Andrej Karpathy](https://karpathy.github.io/2019/04/25/recipe/)
- [Budget mémoire](../reference/memory-budget.md) : l'étape 2 transforme ces quatre étapes en octets

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
