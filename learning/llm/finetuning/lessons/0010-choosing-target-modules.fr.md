---
title: "10. Choisir les target modules"
description: "« Attention seule » est une ablation de 2021, pas une valeur par défaut"
type: lesson
---

# Leçon 10. Choisir les target modules

**Lien avec la mission :** Les target modules comptent plus que le rank, et la sagesse reçue à leur sujet est dépassée. C'est un endroit où vous pouvez être mesurablement meilleur que le praticien moyen.
**Source primaire :** [Doc : "LoRA Without Regret", Hugging Face TRL](https://huggingface.co/docs/trl/main/en/lora_without_regret)
**Prérequis :** [Leçon 2](0002-where-the-weights-live.md), [Leçon 9](0009-rank-alpha-and-initialisation.md)

## Échauffement

1. ▢ Que contrôle `α/r`, et que contrôle `r` seul ?

<details markdown="1"><summary>Vérifier</summary>

`α/r` fixe l'échelle de la contribution de l'adapter. `r` seul fixe sa capacité : la complexité de la mise à jour qu'il peut exprimer.

</details>

2. ▢ Quelle sous-couche contient la plupart des paramètres d'un bloc de transformer ?

<details markdown="1"><summary>Vérifier</summary>

Le MLP, environ 75 à 80 % du bloc, parce que la dimension intermédiaire fait plusieurs fois la taille cachée et que la grouped-query attention rétrécit deux des quatre projections d'attention.

</details>

3. ▢ Que garantit un `B` initialisé à zéro ?

<details markdown="1"><summary>Vérifier</summary>

Que le modèle adapté est identique au base model avant le premier pas de l'optimizer.

</details>

## À savoir

### Ce qu'a fait l'article original, et pourquoi ce n'est pas un conseil

L'article LoRA n'adaptait que les projections d'attention, dans ses expériences surtout `W_q` et `W_v`, et laissait le MLP tranquille. Ce choix s'est propagé dans des années de tutoriels, et c'est de là que vient `target_modules=["q_proj", "v_proj"]`.

Deux choses à comprendre à son sujet. C'était un constat raisonnable sous un budget mémoire et sur les tâches mesurées. Et ce n'est **pas** un résultat général sur l'endroit où l'adaptation devrait avoir lieu. Traiter une ablation de 2021 comme une valeur par défaut est l'erreur héritée la plus courante de ce domaine.

### Le cas du MLP

D'après la leçon 2 : le MLP contient environ quatre cinquièmes des paramètres de chaque bloc. Il existe un corpus substantiel de travaux d'interprétabilité qui traitent les couches MLP comme l'endroit où vit une grande partie des connaissances apprises et de la détection de features d'un modèle, tandis que l'attention achemine l'information entre les positions. Si votre tâche demande que le modèle *connaisse* ou *classe* quelque chose différemment, les paramètres qui l'encodent se trouvent de façon disproportionnée dans le MLP, et un adapter limité à l'attention ne peut pas les atteindre.

### La valeur par défaut actuelle

Les travaux récents convergent vers une recommandation brutale : **adapter toutes les couches linéaires**, et donner à l'adapter assez de rank. Le compte rendu de TRL sur le résultat « LoRA without regret » est explicite : appliquer LoRA à chaque couche linéaire, MLP compris, avec un rank suffisant, comble l'écart avec le full fine-tuning sur les charges de fine-tuning supervisé, alors que les configurations limitées à l'attention n'y parviennent pas.

```text
# The modern default: let the library find every linear layer.
config := {rank: 64, alpha: 128, target_modules: "all-linear"}

# The explicit equivalent, for a Llama-style architecture.
config := {
    rank: 64,
    alpha: 128,
    target_modules: [
        "q_proj", "k_proj", "v_proj", "o_proj",
        "gate_proj", "up_proj", "down_proj",
    ],
}
```

`"all-linear"` est le plus sûr des deux, parce qu'il ne peut pas devenir obsolète face à une architecture dont les noms de modules diffèrent de la liste que vous avez mémorisée. Son coût est que vous renoncez à un contrôle précis et devez vérifier ce qu'il a réellement retenu.

Pourquoi c'est abordable maintenant : d'après la leçon 7, les paramètres d'adapter représentent une part négligeable de la mémoire d'entraînement. Restreindre les target modules pour économiser de la mémoire était un vrai arbitrage en 2021 et est presque un non-arbitrage aujourd'hui. Ce que vous échangez réellement, c'est un risque de surapprentissage sur de petits datasets.

### La décision

| Situation | Cibles | Raisonnement |
|---|---|---|
| Valeur par défaut pour une vraie tâche | Toutes les couches linéaires | Meilleure qualité par unité d'effort ; correspond aux preuves actuelles |
| Petit dataset (< ~1k exemples) | Attention seule, rank bas | Limiter délibérément la capacité pour limiter la mémorisation |
| Style ou ton seulement | Attention seule, rank bas | Un petit changement de comportement demande une petite mise à jour |
| La tâche exige de nouvelles discriminations | Doit inclure le MLP | L'attention seule ne peut pas atteindre l'endroit où elles vivent |
| Reproduire un article | Exactement ce que l'article a utilisé | Sinon vous ne le reproduisez pas |

### Deux modules sur lesquels on vous interroge

**Embeddings et tête de sortie.** En général laissés tels quels. Les adapter coûte cher par rapport au bénéfice, et c'est le seul endroit où modifier les poids peut décaler le sens de chaque token. L'exception véritable est l'ajout de nouveaux tokens spéciaux, qui demande de toucher à la table d'embeddings et est une opération différente de son adaptation.

**Termes de biais.** `bias="none"` est le réglage standard. Entraîner aussi les biais ( `"all"` ou `"lora_only"`) est bon marché mais fait rarement la différence entre un run qui fonctionne et un run qui échoue, et complique la fusion.

### La vérification qui attrape la vraie erreur

Affichez ce qui a correspondu, à chaque fois :

```text
model := attach_adapter(base_model, config)
print(model.trainable_parameter_count())
print(first 8 parameter names containing "lora")
```

Un nom de target module qui ne correspondait à rien produit soit une erreur, soit, selon la version, un modèle sans adapter du tout, qui s'entraîne, journalise une loss et n'apprend rien. Un nombre de paramètres entraînables qui contredit votre arithmétique de la leçon 8 est l'avertissement le plus précoce possible.

## Pratique

1. ▢ Pourquoi l'article original ciblait-il l'attention seule, et pourquoi n'est-ce pas une valeur par défaut aujourd'hui ?

<details markdown="1"><summary>Vérifier</summary>

C'était une ablation sous un budget mémoire serré, sur les tâches que les auteurs ont mesurées, à une époque où limiter les paramètres entraînables comptait. Ce n'a jamais été l'affirmation que l'attention est l'endroit où l'adaptation doit se faire.

Aujourd'hui la mémoire de l'adapter est négligeable, et les preuves favorisent la couverture de toutes les couches linéaires avec un rank suffisant.

</details>

2. ▢ Votre tâche exige que le modèle distingue des concepts de domaine qu'il confond actuellement. Attention seule ou all-linear ?

<details markdown="1"><summary>Vérifier</summary>

All-linear. Faire de nouvelles discriminations, c'est changer la détection de features et les associations stockées, qui vivent de façon disproportionnée dans le MLP. L'attention achemine l'information ; ce n'est pas là que cette distinction est encodée.

</details>

3. ▢ Vous avez 400 exemples d'entraînement. Plaidez pour une restriction des target modules.

<details markdown="1"><summary>Vérifier</summary>

Avec 400 exemples, la capacité est le risque plutôt que la contrainte. Un adapter all-linear complet à rank généreux peut mémoriser l'ensemble tout entier : loss d'entraînement proche de zéro, loss held-out qui grimpe, et aucune généralisation.

Se limiter à l'attention à bas rank est une limite de capacité délibérée, qui joue le rôle de régularisation. La meilleure réponse, si elle est disponible, est davantage de données.

</details>

4. ▢ Quel changement est le plus susceptible d'améliorer la qualité sur une vraie tâche avec un dataset raisonnable ?

    - a) Augmenter le rank de l'adapter de 16 à 64
    - b) Étendre les cibles à toutes les couches linéaires
    - c) Ajouter du dropout LoRA à 0.05 au run
    - d) Entraîner un epoch complet de plus

<details markdown="1"><summary>Vérifier</summary>

**b)** Étendre les cibles à toutes les couches linéaires.

Cela met à portée de l'adaptation environ quatre fois plus de paramètres, MLP compris. Augmenter le rank ajoute de la capacité dans les couches que vous atteignez déjà. Le dropout régularise plutôt qu'il n'améliore l'ajustement. Un epoch de plus risque le surapprentissage sans ajouter de capacité.

</details>

5. ▢ Vous réglez `target_modules=["c_attn"]` et le run s'entraîne avec une loss qui bouge à peine. Que vérifiez-vous en premier ?

<details markdown="1"><summary>Vérifier</summary>

Si `c_attn` existe dans ce modèle. C'est la projection d'attention fusionnée des architectures de style GPT-2 et elle n'existe pas dans celles de style Llama, qui utilisent des `q_proj`, `k_proj`, `v_proj` séparées.

Affichez les noms de modules, puis `print_trainable_parameters()`. Un nombre de paramètres entraînables proche de zéro est la réponse.

</details>

6. ▢ Pourquoi `"all-linear"` est-il plus sûr qu'une liste de modules explicite ?

<details markdown="1"><summary>Vérifier</summary>

Il se résout par rapport au modèle chargé plutôt que par rapport à votre mémoire, donc il ne peut pas rater silencieusement des couches sur une architecture dont la nomenclature diffère.

Son coût est une perte de précision, donc vérifiez ce qu'il a retenu et notez qu'il peut inclure des couches que vous préféreriez laisser de côté.

</details>

## Exercices en situation réelle

- [ ] Construisez un adapter limité à l'attention et un adapter all-linear au même rank sur le même modèle. Notez les deux nombres de paramètres entraînables et leur rapport.
- [ ] Vérifiez quels modules `"all-linear"` a retenus en affichant les noms de paramètres de l'adapter. Notez tout ce qui est inattendu.
- [ ] Demain : trouvez trois configurations de fine-tuning publiées en ligne et notez lesquelles ciblent l'attention seule. Jugez si l'auteur l'a choisi ou hérité.

## Pour aller plus loin

- [Doc : "LoRA Without Regret", Hugging Face TRL](https://huggingface.co/docs/trl/main/en/lora_without_regret)
- [Blog : "Practical Tips for Finetuning LLMs Using LoRA", Sebastian Raschka](https://magazine.sebastianraschka.com/p/practical-tips-for-finetuning-llms) : les ablations sur les target modules
- [Hyperparamètres de LoRA](../reference/lora-hyperparameters.md)
- [Leçon 11. Votre premier adapter](0011-your-first-adapter.md)

---

Ça ne passe pas ? Relisez la source primaire en haut de page, car cette leçon la condense et c'est dans la condensation que la compréhension s'échappe. Consultez le [glossaire](../GLOSSARY.md) pour tout terme qui vous a paru glissant.

Si c'est la leçon elle-même qui n'est pas claire plutôt que la matière, c'est un défaut : [ouvrez une issue](https://github.com/TokenCemetery/teach/issues).
