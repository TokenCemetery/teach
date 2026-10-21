---
title: "16. Entraîner à travers un base model quantifié"
description: "Comment les gradients traversent des poids gelés en 4 bits"
type: lesson
---

# Leçon 16. Entraîner à travers un base model quantifié

**Lien avec la mission :** QLoRA en pratique. C'est aussi la seule leçon où le matériel dont vous disposez change réellement ce qui est à votre portée.
**Source primaire :** [Doc : bitsandbytes quantization, Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/quantization/bitsandbytes)
**Prérequis :** [Leçon 15](0015-nf4-and-double-quantisation.md), [Leçon 11](0011-your-first-adapter.md)

## Échauffement

1. ▢ Qu'est-ce que NF4 place aux quantiles d'une loi normale, et pourquoi ?

<details markdown="1"><summary>Vérifier</summary>

Ses 16 niveaux représentables, pour que chacun couvre la même masse de probabilité plutôt que la même plage, ce qui correspond à l'endroit où les poids normalement distribués se regroupent réellement.

</details>

2. ▢ Que compresse la double quantification ?

<details markdown="1"><summary>Vérifier</summary>

Les échelles de bloc du premier niveau, pas les poids. Environ 0.37 bit par paramètre.

</details>

3. ▢ Pour un base model en 4 bits avec un adapter, quel terme de mémoire domine ?

<details markdown="1"><summary>Vérifier</summary>

Les activations. Le base model est tombé à quelques gigaoctets et l'état de l'adapter n'en représente qu'une fraction, donc c'est la batch size et la longueur de séquence qui décident maintenant si le run tient.

</details>

## À savoir

### Comment un gradient atteint l'adapter à travers un base model quantifié gelé

Le paradoxe apparent : les poids de base sont des entiers de 4 bits, et l'on ne peut pas prendre de façon sensée un gradient par rapport à un entier de 4 bits. Alors comment l'entraînement fonctionne-t-il ?

Il fonctionne parce que **les poids de base ne sont pas entraînés.** Suivez une couche adaptée :

```text
forward:   h = W₀_dequant(x) + (α/r) · B A x
```

`W₀` est déquantifié en bf16 pour la multiplication de matrices et la copie déquantifiée est jetée. La passe arrière a besoin du gradient de la loss par rapport à `A` et `B`, et pour le calculer elle a besoin des *activations* qui traversent la couche, en bf16, et du gradient qui arrive d'en haut, aussi en bf16.

Les poids gelés ne participent à la passe arrière qu'en **laissant passer le gradient** vers les couches antérieures. Cela exige de multiplier par `W₀`, donc de le déquantifier de nouveau plutôt que de le dériver. Aucun gradient n'est jamais stocké pour un poids de base, parce qu'aucun n'est demandé.

![Une couche adaptée dessinée deux fois avec les mêmes quatre boîtes. En passe avant, l'entrée atteint à la fois le base model en 4 bits et l'adapter en bf16, qui se rejoignent à la sortie ; en passe arrière, le gradient parcourt les mêmes arêtes en sens inverse, mais seul l'adapter a un gradient stocké.](images/a-constant-in-the-graph.svg)

Les deux panneaux contiennent les mêmes boîtes aux mêmes endroits, et les arêtes de la passe arrière sont celles de la passe avant inversées. Le base model apparaît dans les deux, y travaille dans les deux, et ne conserve rien d'aucun.

Il n'y a donc rien d'exotique ici. Le base model quantifié est une constante du graphe de calcul. Il doit être lu en haute précision, mais n'a jamais besoin d'être mis à jour, et la mise à jour est la partie coûteuse.

Le coût est le calcul : la déquantification a lieu à chaque passe avant et de nouveau dans la passe arrière, à chaque pas. QLoRA échange de la vitesse contre de la mémoire, et il est nettement plus lent par pas qu'un base model en bf16.

### Préparer le modèle

```text
quant_config := {
    load_in_4bit: true,
    quant_type: "nf4",
    use_double_quant: true,
    compute_dtype: "bfloat16",
}

model := load_model("<base model>", quantization: quant_config)
model := prepare_for_quantized_training(model, gradient_checkpointing: true)

adapter_config := {rank: 32, alpha: 64, target_modules: "all-linear"}
model := attach_adapter(model, adapter_config)
print(model.trainable_parameter_count())
```

`prepare_model_for_kbit_training` fait plusieurs petites choses nécessaires : il convertit les normalisations de couche et la tête de sortie vers une précision stable, active le gradient checkpointing et l'exigence de gradients sur les entrées, et s'assure que rien de ce qui doit rester en plus haute précision n'a été quantifié. Le sauter produit des runs instables ou qui échouent avec des erreurs de gradient, et la cause n'est pas évidente d'après le message.

### Tout le reste est inchangé

Rank, alpha, target modules, learning rate, schedule, découpage held-out, sondes de génération, les quatre vérifications de la leçon 11 : tout est identique. **QLoRA, c'est LoRA avec un base model moins cher.** Ce n'est pas une méthode différente avec son propre folklore d'hyperparamètres, et la traiter comme telle est une source courante de confusion.

Le seul ajustement qui mérite d'être mentionné : comme le base model est plus bruité, certains praticiens utilisent un peu plus de rank qu'avec un base model en bf16, dans l'idée que l'adapter doit compenser l'erreur de quantification en plus d'apprendre la tâche. Considérez cela comme une hypothèse à tester sur votre tâche, pas comme une règle.

### Backends : ce qui est réellement vrai

Cela demande de l'attention, parce que la version largement répétée est périmée.

`bitsandbytes` a commencé comme CUDA seul, et pendant plusieurs années « QLoRA a besoin d'un GPU NVIDIA » était simplement exact. La bibliothèque est depuis passée à une architecture multi-backend, avec un aiguillage vers **CUDA (qui couvre aussi AMD ROCm), CPU, Intel XPU, Intel Gaudi et Apple MPS**, à côté de solutions de repli en pur PyTorch. Les opérations 4 bits, quantifier, déquantifier et le produit matrice-vecteur en 4 bits, ont des implémentations de backend au-delà de CUDA, aiguillées quand la taille de bloc est de celles que le kernel compilé prend en charge, et se rabattant sur des chemins génériques plus lents sinon.

Ce qui en découle pour vous :

- **CUDA reste la voie la plus complète et la mieux optimisée.** Si vous l'avez, utilisez-la, et attendez-vous à ce que les chiffres publiés soient reproductibles.
- **Les autres backends sont viables et s'améliorent, avec des réserves.** La couverture varie selon l'opération, la taille de bloc et la version de la bibliothèque. Attendez-vous à des pas plus lents, et à devoir vérifier si une configuration précise tombe sur un kernel optimisé ou sur un repli.
- **Les paged optimizers sont la pièce réellement propre à CUDA.** Ils s'appuient sur la mémoire unifiée de NVIDIA pour déverser l'état de l'optimizer vers la mémoire de l'hôte pendant des pics transitoires, en évitant un plantage par manque de mémoire à un pic. C'est une fonctionnalité matérielle, pas un algorithme portable. Elle compte aussi le moins dans l'entraînement d'adapters, où l'état de l'optimizer est minuscule ; son but d'origine était l'état à l'échelle du full fine-tuning.
- **Vérifiez face à votre version installée plutôt que face à n'importe quel document.** Ce domaine a changé à plusieurs reprises et changera encore. `bitsandbytes` n'est pas non plus la seule voie vers le 4 bits ; d'autres backends de quantification existent, avec une couverture matérielle différente.

Les concepts des leçons 14 et 15, à savoir les échelles par bloc, les niveaux aux quantiles normaux, la quantification des constantes et la précision de stockage contre la précision de calcul, relèvent de l'arithmétique et sont identiques sur tous les backends. Seules la disponibilité des kernels et la vitesse diffèrent.

### À quoi s'attendre du run

| Face à un base model en bf16 | Effet |
|---|---|
| Mémoire fixe | Environ 4× plus basse pour le base model |
| Temps par pas | Plus lent, déquantification à chaque passe avant et arrière |
| Forme de la courbe de loss | Très semblable ; peut se situer légèrement plus haut |
| Qualité finale | Légèrement plus basse, selon la tâche, donc mesurez-la (leçon 17) |

Et la règle de fusion de la leçon 13 tient toujours, plus importante que jamais : **fusionnez dans le base model en pleine précision, pas dans le base model quantifié.** Entraînez face au 4 bits, puis chargez le base model en bf16, appliquez l'adapter, fusionnez là. Fusionner dans des poids quantifiés ajoute une perte de requantification que vous n'avez aucune raison d'accepter.

## Pratique

1. ▢ Comment les gradients peuvent-ils circuler quand les poids de base sont des entiers de 4 bits ?

<details markdown="1"><summary>Vérifier</summary>

Aucun gradient n'est jamais pris par rapport à un poids de base : ce sont des constantes gelées. Les gradients sont pris par rapport à `A` et `B`, qui sont en haute précision.

Les poids gelés sont nécessaires pour *propager* le gradient vers les couches antérieures, ce qui exige de les déquantifier pour la multiplication, pas de les dériver.

</details>

2. ▢ Que fait `prepare_model_for_kbit_training`, et que se passe-t-il si vous le sautez ?

<details markdown="1"><summary>Vérifier</summary>

Il convertit les modules qui ont besoin de stabilité, comme les normalisations de couche et la tête de sortie, vers une précision plus haute, active le gradient checkpointing et les gradients sur les entrées, et s'assure que rien de ce qui doit rester en haute précision n'a été quantifié.

Le sauter donne typiquement un run instable ou une erreur disant que les gradients ne sont pas requis, avec un message qui ne pointe pas la cause.

</details>

3. ▢ Quelle est la partie de QLoRA propre à CUDA, et quelle importance a-t-elle pour l'entraînement d'adapters ?

<details markdown="1"><summary>Vérifier</summary>

Les paged optimizers, qui utilisent la mémoire unifiée de NVIDIA pour déverser l'état de l'optimizer vers la mémoire de l'hôte pendant les pics.

Elle importe peu pour l'entraînement d'adapters, où l'état de l'optimizer se compte en mégaoctets. Elle a été conçue pour un état à l'échelle du full fine-tuning, où un pic transitoire met réellement fin au run.

</details>

4. ▢ Un tutoriel de 2023 affirme que le NF4 en 4 bits exige un GPU NVIDIA. Est-ce toujours correct ?

<details markdown="1"><summary>Vérifier</summary>

Pas de façon absolue. `bitsandbytes` aiguille maintenant les opérations 4 bits vers CUDA/ROCm, CPU, Intel XPU, Intel Gaudi et Apple MPS, avec des replis PyTorch là où un kernel compilé n'est pas disponible.

CUDA reste la voie la plus complète et la plus rapide, et la couverture des autres backends varie selon l'opération, la taille de bloc et la version. L'énoncé correct est donc « CUDA est la voie la mieux prise en charge », pas « CUDA est la seule voie », et vous vérifiez face à votre version installée plutôt que face à n'importe quel tutoriel.

</details>

5. ▢ Quel hyperparamètre devez-vous repenser en passant de LoRA à QLoRA ?

    - a) Le learning rate, qu'il faut baisser nettement
    - b) La valeur d'alpha, qu'il faut augmenter pour compenser
    - c) Aucun, la précision du base model est un sujet distinct
    - d) La batch size, qu'il faut augmenter pour rester stable

<details markdown="1"><summary>Vérifier</summary>

**c)** Aucun. La précision du base model est un sujet distinct.

QLoRA, c'est LoRA avec un base model moins cher. Certains praticiens essaient un peu plus de rank pour absorber le bruit de quantification, mais c'est une hypothèse à tester, pas un changement requis.

</details>

6. ▢ Vous avez entraîné face à un base model en 4 bits et voulez un seul modèle déployable. Donnez les étapes dans l'ordre.

<details markdown="1"><summary>Vérifier</summary>

Chargez le base model en bf16 (pas en 4 bits), appliquez l'adapter entraîné, fusionnez, sauvegardez avec le tokenizer, et quantifiez le modèle fusionné ensuite seulement si vous avez besoin d'un artefact quantifié pour le service.

Fusionner dans le base model en 4 bits exige de déquantifier, d'ajouter puis de requantifier, et perd de la qualité pour rien.

</details>

## Exercices en situation réelle

- [ ] Chargez un base model en bf16 et en NF4. Notez la mémoire de chacun et calculez le rapport.
- [ ] Exécutez le même court travail d'entraînement face aux deux base models. Notez les secondes par pas et la courbe de loss, et relevez lequel est plus lent et de combien.
- [ ] Vérifiez quel backend votre installation de `bitsandbytes` utilise réellement, et si votre taille de bloc tombe sur un kernel optimisé ou sur un repli.
- [ ] Demain : fusionnez l'adapter entraîné en 4 bits dans le base model en bf16 et vérifiez en décodage glouton face à vos sondes.

## Pour aller plus loin

- [Doc : bitsandbytes quantization, Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/quantization/bitsandbytes)
- [Code : bitsandbytes, bitsandbytes-foundation](https://github.com/bitsandbytes-foundation/bitsandbytes) : le répertoire des backends fait autorité sur la couverture
- [Article : "QLoRA: Efficient Finetuning of Quantized LLMs", Dettmers et al., arXiv:2305.14314](https://arxiv.org/abs/2305.14314)
- [Leçon 17. Ce que QLoRA coûte réellement](0017-what-qlora-costs.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
