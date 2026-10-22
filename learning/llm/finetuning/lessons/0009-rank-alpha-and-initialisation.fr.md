---
title: "9. Rank, alpha et initialisation"
description: "Seul `α/r` compte, et pourquoi `B` démarre à zéro"
type: lesson
---

# Leçon 9. Rank, alpha et initialisation

**Lien avec la mission :** La mission vous demande de justifier chaque hyperparamètre à partir de la tâche. Ces trois-là sont ceux où la plupart des gens répètent du folklore.
**Source primaire :** [Doc : LoRA, Hugging Face PEFT](https://huggingface.co/docs/peft/main/en/developer_guides/lora)
**Prérequis :** [Leçon 8](0008-the-low-rank-idea.md)

## Échauffement

1. ▢ Écrivez l'équation de la passe avant de LoRA.

<details markdown="1"><summary>Vérifier</summary>

`h = W₀x + (α/r) · BAx`, avec `W₀` gelé et seuls `A` et `B` entraînables.

</details>

2. ▢ Nombre de paramètres d'adapter pour une couche ciblée ?

<details markdown="1"><summary>Vérifier</summary>

`r × (d_in + d_out)`. Dominé par la plus grande dimension.

</details>

3. ▢ Pourquoi un adapter fusionné ne coûte-t-il rien à l'inférence ?

<details markdown="1"><summary>Vérifier</summary>

La mise à jour est additive et linéaire, donc elle se refond dans le poids de base et laisse derrière elle une matrice ordinaire.

</details>

## À savoir

### Initialisation, et pourquoi elle n'est pas arbitraire

`A` est initialisée aléatoirement, de façon gaussienne ou Kaiming-uniforme. `B` est initialisée à **exactement zéro**.

Donc `BA = 0` au pas zéro, donc `ΔW = 0`, donc **le modèle adapté est, bit pour bit, le base model avant la première mise à jour.** C'est une propriété délibérée et importante :

- L'entraînement part d'un modèle dont on sait qu'il est bon, plutôt que d'un modèle perturbé.
- Il n'y a pas de choc initial sur le comportement préentraîné, donc pas de dégâts précoces à réparer.
- Toute dégradation que vous observez est quelque chose que l'entraînement a fait, pas quelque chose que l'initialisation a fait.

![B dessinée comme une grille de zéros, A comme une grille de valeurs variées, et leur produit comme une grille de zéros, avec les deux initialisations rejetées nommées en dessous.](images/zero-whatever-a-holds.svg)

Les entrées de `A` sont visibles et aucune n'a d'importance : chacune est multipliée par un zéro en entrant dans le produit.

L'asymétrie est nécessaire. Si les deux étaient à zéro, le gradient des deux serait nul et rien n'apprendrait jamais : le produit a besoin qu'un facteur soit non nul pour porter le signal. Si les deux étaient aléatoires, `ΔW` démarrerait comme du bruit structuré injecté dans chaque couche ciblée.

C'est aussi pourquoi LoRA tolère des learning rates bien plus élevés que le full fine-tuning. Vous ne poussez pas doucement des poids qui encodent déjà tout ce que le modèle sait ; vous faites croître un terme à partir de zéro.

### Alpha et le facteur d'échelle

`α` (`lora_alpha`) est un scalaire fixe. La mise à jour est mise à l'échelle par `α/r`.

Diviser par `r` avait pour but de rendre l'amplitude effective de la mise à jour à peu près indépendante du rank, pour que changer de rank ne vous oblige pas à re-régler le learning rate. **Ce qui compte, c'est le rapport `α/r`, pas l'un ou l'autre nombre seul.**

| `r` | `α` | `α/r` | Effet |
|---|---|---|---|
| 8 | 16 | 2.0 | Référence courante |
| 16 | 32 | 2.0 | Plus de capacité, même échelle de mise à jour |
| 16 | 16 | 1.0 | Plus de capacité, mise à jour plus faible |
| 64 | 16 | 0.25 | Beaucoup plus de capacité, fortement amortie |

Cette dernière ligne est un piège qui mérite d'être nommé : augmenter le rank en laissant `α` fixe *réduit* l'échelle de la mise à jour. Les gens augmentent le rank en espérant plus de puissance d'expression, oublient `α`, et concluent qu'un rank plus élevé nuit. Ce n'est pas le cas ; ils ont discrètement baissé l'adapter d'un facteur 8.

Le point de départ conventionnel est `α = 2r`. Considérez-le comme une convention avec une justification, pas comme une découverte.

**rsLoRA** ([arXiv:2312.03732](https://arxiv.org/abs/2312.03732)) soutient que le diviseur `α/r` amortit trop à rank élevé et propose `α/√r` à la place, ce qui garde l'apprentissage stable quand le rank grandit. Si vous prévoyez de travailler à un rank de 64 ou plus, c'est le réglage à connaître :

```python
LoraConfig(r=64, lora_alpha=16, use_rslora=True, ...)
```

### Choisir le rank

Le rank, c'est la **capacité**. Il borne la complexité de la mise à jour que l'adapter peut exprimer.

| Rank | Raisonnable pour |
|---|---|
| 4 à 8 | Style, ton, format de sortie ; petits datasets |
| 16 à 32 | Une vraie tâche avec quelques milliers d'exemples |
| 64 à 128 | Tâches plus difficiles, datasets plus grands, comportement qui repose sur le raisonnement |
| 256+ | Approche la capacité du full fine-tuning sur de grands datasets de SFT |

Deux diagnostics qui valent mieux que deviner :

**Sous-apprentissage.** La loss d'entraînement plafonne au-dessus de là où vous en avez besoin et davantage d'epochs n'aident pas. Pas assez de capacité : augmentez le rank, ou ajoutez des target modules (généralement le meilleur choix, d'après la leçon 10).

**Surapprentissage.** La loss d'entraînement continue de baisser pendant que la loss held-out monte. Trop de capacité pour les données, ou trop d'epochs. Baissez le rank, ajoutez du dropout, obtenez plus de données, ou arrêtez plus tôt.

Notez l'asymétrie avec la leçon sur la mémoire : le rank coûte très peu de mémoire (leçon 7), donc le coût d'un rank supplémentaire est un risque de surapprentissage et un peu de calcul, pas de tenir en mémoire. Cela inverse le réflexe que beaucoup de gens ont gardé de l'époque où la mémoire était la contrainte qui lie.

### Dropout

`lora_dropout` applique du dropout à l'entrée de l'adapter. Les valeurs typiques vont de 0.0 à 0.1. Utilisez-le quand la loss held-out monte et que vous ne pouvez pas obtenir davantage de données. Sur de grands datasets, il est souvent inutile et ne fait que ralentir la convergence.

### La configuration

```text
config := {
    rank: 16,
    alpha: 32,               # α/r = 2
    dropout: 0.05,
    adapt_bias: false,
    target_modules: [...],   # Lesson 10
}

model := attach_adapter(model, config)
print(model.trainable_parameter_count())
```

Cette dernière ligne n'est pas optionnelle. C'est la vérification que vos target modules ont correspondu à quelque chose, et elle doit concorder avec l'arithmétique que vous avez faite à la leçon 8. Lisez les noms de paramètres dans la documentation de la version installée plutôt que de mémoire, car cette surface change d'une version à l'autre.

## Pratique

1. ▢ Pourquoi `B` est-elle initialisée à zéro et `A` aléatoirement, plutôt que les deux à zéro ou les deux aléatoirement ?

<details markdown="1"><summary>Vérifier</summary>

Une `B` nulle fait que `ΔW = 0` au départ, donc l'entraînement commence exactement depuis le base model, sans perturbation à rattraper. Une `A` aléatoire garde non nul le gradient du produit, donc l'apprentissage peut démarrer.

Les deux à zéro : les gradients s'annulent, rien n'apprend. Les deux aléatoires : le modèle démarre comme base plus bruit dans chaque couche ciblée.

</details>

2. ▢ Vous faites passer le rank de 8 à 64 et laissez `α` à 16. La loss bouge à peine. Diagnostiquez.

<details markdown="1"><summary>Vérifier</summary>

L'échelle `α/r` est passée de 2.0 à 0.25. L'adapter a huit fois plus de capacité et huit fois moins d'influence, donc l'effet net est une mise à jour amortie, pas plus forte.

Montez `α` à 128 pour préserver le rapport, ou réglez `use_rslora=True` pour que le diviseur devienne `√r`.

</details>

3. ▢ La loss d'entraînement s'aplatit à un niveau trop élevé pour être utile, et un quatrième epoch n'aide pas. De quoi s'agit-il, et quelles sont vos deux options ?

<details markdown="1"><summary>Vérifier</summary>

Du sous-apprentissage : l'adapter n'a pas la capacité d'exprimer la mise à jour requise.

Augmentez le rank, ou étendez les target modules pour couvrir davantage du modèle. Ajouter des target modules est généralement le meilleur premier geste, parce que le MLP contient la plupart des paramètres et que la capacité manquante s'y trouve souvent. Davantage d'epochs ne peuvent pas corriger un plafond de capacité.

</details>

4. ▢ Quel couple donne l'échelle de mise à jour la plus forte ?

    - a) `r = 8` avec `alpha = 8`
    - b) `r = 8` avec `alpha = 32`
    - c) `r = 32` avec `alpha = 32`
    - d) `r = 64` avec `alpha = 64`

<details markdown="1"><summary>Vérifier</summary>

**b)** `r = 8` avec `alpha = 32`, ce qui donne `α/r = 4`.

Tous les autres valent `α/r = 1`. La capacité diffère entre eux, mais pas l'échelle de mise à jour, ce qui est exactement la distinction que la conception autour de `α/r` devait faire.

</details>

5. ▢ Pourquoi LoRA peut-il utiliser un learning rate de dix à cent fois supérieur à celui du full fine-tuning ?

<details markdown="1"><summary>Vérifier</summary>

Les paramètres entraînables partent d'une contribution nulle et ne sont pas eux-mêmes le lieu de stockage des connaissances préentraînées. Il n'y a pas de structure accumulée à endommager, et le terme doit croître à partir de rien, donc il lui faut un pas bien plus grand pour bouger de façon significative en un nombre raisonnable de pas.

</details>

6. ▢ Quand n'augmenteriez-vous *pas* le rank alors que l'adapter sous-apprend ?

<details markdown="1"><summary>Vérifier</summary>

Quand le dataset est petit. Une capacité supplémentaire sur peu d'exemples achète de la mémorisation, pas de la généralisation : la loss d'entraînement baisse, la loss held-out monte.

La bonne réponse dans ce cas est davantage de données ou de meilleures données, ou une tâche plus étroite, pas un adapter plus gros.

</details>

## Exercices en situation réelle

- [ ] Construisez trois configurations, `(8, 16)`, `(16, 32)` et `(64, 16)`, et notez le `α/r` de chacune et ce que vous prédisez qu'il se passera. Gardez les prédictions.
- [ ] Affichez `print_trainable_parameters()` pour chacune et réconciliez avec votre arithmétique de la leçon 8.
- [ ] Demain : trouvez une configuration de fine-tuning publiée dans la nature, calculez son `α/r`, et décidez si l'auteur l'a choisi ou hérité.

## Pour aller plus loin

- [Doc : LoRA, Hugging Face PEFT](https://huggingface.co/docs/peft/main/en/developer_guides/lora)
- [Article : "A Rank Stabilization Scaling Factor for Fine-Tuning with LoRA", Kalajdzievski, arXiv:2312.03732](https://arxiv.org/abs/2312.03732)
- [Blog : "Practical Tips for Finetuning LLMs Using LoRA", Sebastian Raschka](https://magazine.sebastianraschka.com/p/practical-tips-for-finetuning-llms)
- [Hyperparamètres de LoRA](../reference/lora-hyperparameters.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
